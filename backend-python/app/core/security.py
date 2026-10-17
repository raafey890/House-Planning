import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

# Supabase JWKS configuration
# URL format: <SUPABASE_URL>/auth/v1/.well-known/jwks.json
# We cache keys to prevent fetching on every request
jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the Supabase JWT token using JWKS (ES256) and extracts the user_id.
    """
    token = credentials.credentials
    try:
        # Extract unverified header to get the 'kid' (Key ID) without validating signature yet
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "ES256")

        if alg == "HS256" and getattr(settings, "SUPABASE_JWT_SECRET", None):
            payload = jwt.decode(
                token,
                key=settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False, "verify_iss": False, "verify_exp": True}
            )
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials (missing sub)")
            return user_id

        # Get the corresponding public key from JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        expected_issuer = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1"
        
        # Verify the signature, algorithm, exp, and issuer
        payload = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=[alg],
            issuer=expected_issuer,
            options={
                "verify_aud": False,  # Audiences can vary based on setup (usually 'authenticated')
                "verify_iss": True,
                "verify_exp": True,
                "verify_signature": True
            }
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials (missing sub)",
            )
        return user_id
        
    except jwt.PyJWKClientError as e:
        print(f"Auth Error: JWKS client error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error fetching signing keys",
        )
    except jwt.ExpiredSignatureError:
        print("Auth Error: Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidSignatureError:
        print("Auth Error: Signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
    except jwt.InvalidIssuerError:
        print("Auth Error: Invalid issuer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer",
        )
    except jwt.InvalidTokenError as e:
        print(f"Auth Error: Invalid token - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except Exception as e:
        print(f"Auth Error: Unexpected error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

from supabase import create_client, Client, ClientOptions

def get_user_supabase_client(credentials: HTTPAuthorizationCredentials = Depends(security), user_id: str = Depends(get_current_user)) -> Client:
    """
    Constructs a Supabase client for database operations.
    Prefers SUPABASE_SERVICE_ROLE_KEY when available to avoid PostgREST PGRST301 token decoding errors,
    relying on get_current_user for cryptographic caller authentication and endpoint-level user authorization.
    Falls back to user bearer token with SUPABASE_PUBLISHABLE_KEY.
    """
    if not settings.SUPABASE_URL:
        print("Configuration Error: Missing SUPABASE_URL")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client credentials are not configured"
        )
    
    service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
    if service_key:
        return create_client(settings.SUPABASE_URL, service_key)

    token = credentials.credentials
    pub_key = getattr(settings, 'SUPABASE_PUBLISHABLE_KEY', None)
    if not pub_key:
        print("Configuration Error: Missing SUPABASE_PUBLISHABLE_KEY")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client credentials are not configured"
        )
    
    options = ClientOptions(headers={'Authorization': f'Bearer {token}'})
    return create_client(settings.SUPABASE_URL, pub_key, options=options)
