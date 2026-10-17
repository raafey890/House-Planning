import pytest
import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.core.security import get_current_user, jwks_client
from app.api.routes import floor_plans

app = FastAPI()

@app.get("/test/auth")
def test_auth(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}

app.include_router(floor_plans.router)

client = TestClient(app)

def test_missing_auth_header():
    response = client.get("/test/auth")
    assert response.status_code in (401, 403) 

def test_malformed_bearer():
    response = client.get("/test/auth", headers={"Authorization": "InvalidToken"})
    assert response.status_code in (401, 403) 

@patch("app.core.security.jwt.get_unverified_header")
def test_invalid_jwt(mock_get_header):
    mock_get_header.side_effect = jwt.InvalidTokenError("Not a valid JWT")
    response = client.get("/test/auth", headers={"Authorization": "Bearer fake_token"})
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]

@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_expired_jwt(mock_get_key, mock_header, mock_decode):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_key.key = "fake_key"
    mock_get_key.return_value = mock_key
    mock_decode.side_effect = jwt.ExpiredSignatureError()
    
    response = client.get("/test/auth", headers={"Authorization": "Bearer expired_token"})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_wrong_algorithm(mock_get_key, mock_header, mock_decode):
    mock_header.return_value = {"alg": "RS256", "kid": "123"} 
    mock_key = MagicMock()
    mock_key.key = "fake_key"
    mock_get_key.return_value = mock_key
    mock_decode.side_effect = jwt.InvalidAlgorithmError("Invalid algorithm")
    
    response = client.get("/test/auth", headers={"Authorization": "Bearer bad_alg_token"})
    assert response.status_code == 401

@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_missing_sub(mock_get_key, mock_header, mock_decode):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_key.key = "fake_key"
    mock_get_key.return_value = mock_key
    mock_decode.return_value = {"aud": "authenticated"} 
    
    response = client.get("/test/auth", headers={"Authorization": "Bearer no_sub_token"})
    assert response.status_code == 401
    assert "missing sub" in response.json()["detail"].lower()

@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_valid_es256_token(mock_get_key, mock_header, mock_decode):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_key.key = "fake_key"
    mock_get_key.return_value = mock_key
    mock_decode.return_value = {"sub": "user-123"}
    
    response = client.get("/test/auth", headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    assert response.json()["user_id"] == "user-123"

@patch("app.api.routes.floor_plans.get_user_supabase_client")
@patch("app.api.routes.floor_plans.FloorplanService.create_generation_job")
@patch("app.api.routes.floor_plans.project_service.get_planning_context")
@patch("app.api.routes.floor_plans.project_service.verify_ownership")
@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_own_project_authorization(mock_get_key, mock_header, mock_decode, mock_verify, mock_context, mock_job, mock_client):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_get_key.return_value = mock_key
    mock_decode.return_value = {"sub": "owner-user"}
    
    # We must patch get_user_supabase_client inside floor_plans router
    app.dependency_overrides[floor_plans.get_user_supabase_client] = lambda: MagicMock()
    
    mock_verify.return_value = True
    
    mock_context.return_value = {}
    mock_job.side_effect = Exception("Stop execution after auth")
    
    response = client.post("/api/v1/projects/proj-123/floor-plans/generate", 
                           headers={"Authorization": "Bearer token"},
                           json={"optimization_priority": "balanced"})
    # 500 means it passed 401 and 403 and reached our Stop exception
    assert response.status_code == 500
    
    # Remove override
    app.dependency_overrides.clear()

@patch("app.api.routes.floor_plans.project_service.verify_ownership")
@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_unauthorized_project_access(mock_get_key, mock_header, mock_decode, mock_verify):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_get_key.return_value = mock_key
    mock_decode.return_value = {"sub": "hacker-user"}
    
    app.dependency_overrides[floor_plans.get_user_supabase_client] = lambda: MagicMock()
    
    mock_verify.return_value = False
    
    response = client.post("/api/v1/projects/proj-123/floor-plans/generate", 
                           headers={"Authorization": "Bearer token"},
                           json={"optimization_priority": "balanced"})
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]
    app.dependency_overrides.clear()

@patch("app.api.routes.floor_plans.project_service.verify_ownership")
@patch("app.core.security.jwt.decode")
@patch("app.core.security.jwt.get_unverified_header")
@patch.object(jwks_client, "get_signing_key_from_jwt")
def test_infrastructure_error_not_403(mock_get_key, mock_header, mock_decode, mock_verify):
    mock_header.return_value = {"alg": "ES256", "kid": "123"}
    mock_key = MagicMock()
    mock_get_key.return_value = mock_key
    mock_decode.return_value = {"sub": "owner-user"}
    
    app.dependency_overrides[floor_plans.get_user_supabase_client] = lambda: MagicMock()
    
    mock_verify.side_effect = HTTPException(status_code=500, detail="Database infrastructure failure")
    
    response = client.post("/api/v1/projects/proj-123/floor-plans/generate", 
                           headers={"Authorization": "Bearer token"},
                           json={"optimization_priority": "balanced"})
    assert response.status_code == 500
    assert "infrastructure" in response.json()["detail"].lower()
    app.dependency_overrides.clear()
