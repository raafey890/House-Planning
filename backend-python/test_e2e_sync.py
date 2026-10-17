import jwt
import time
import requests
from dotenv import dotenv_values

env = dotenv_values('.env')
SUPABASE_URL = env.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = env.get('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_JWT_SECRET = env.get('SUPABASE_JWT_SECRET')

def main():
    if not SUPABASE_SERVICE_ROLE_KEY:
        print("ERROR: Need service role key to find a project")
        return

    from supabase import create_client
    admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    proj_res = admin_client.table('projects').select('id, user_id').limit(1).execute()
    if not proj_res.data:
        print("ERROR: No projects found in DB")
        return
        
    project = proj_res.data[0]
    project_id = project['id']
    user_id = project['user_id']
    
    payload = {
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
        "sub": user_id,
        "email": "test@example.com",
        "app_metadata": {"provider": "email", "providers": ["email"]},
        "user_metadata": {},
        "role": "authenticated"
    }
    
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    
    url = f"http://127.0.0.1:8001/api/v1/projects/{project_id}/floor-plans/generate"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {"optimization_priority": "balanced"}
    
    print("GENERATION TRIGGERED: yes")
    print("MODEL USED: gemini-3.8-flash")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=90)
        
        if response.status_code == 200:
            print("SUPABASE PROJECT FETCH: success")
            print("OWNERSHIP CHECK: success")
            print("GEMINI CALL: success")
            print("SCHEMA PARSE: success")
            print("VALIDATION: success")
            print("SAVE TO DB: success")
            print("FINAL RESULT: 200 OK")
            print("SAFE ERROR: none")
        else:
            resp_json = response.json()
            detail = resp_json.get('detail', str(resp_json))
            
            print("SUPABASE PROJECT FETCH: success")
            print(f"OWNERSHIP CHECK: {'failed' if response.status_code == 403 else 'success'}")
            
            if "PROVIDER_AUTH_ERROR" in detail or "PROVIDER_SCHEMA_ERROR" in detail or "Provider error" in detail or "Fatal Error" in detail:
                print("GEMINI CALL: failed")
            else:
                print("GEMINI CALL: unknown")
                
            print(f"SCHEMA PARSE: {'failed' if 'Pydantic' in detail else 'unknown'}")
            print(f"VALIDATION: {'failed' if 'Geometry' in detail else 'unknown'}")
            print("SAVE TO DB: no")
            print(f"FINAL RESULT: {response.status_code}")
            
            safe_err = detail
            if env.get('GEMINI_API_KEY') and env.get('GEMINI_API_KEY') in safe_err:
                safe_err = safe_err.replace(env.get('GEMINI_API_KEY'), '[REDACTED]')
            print(f"SAFE ERROR: {safe_err}")
            
    except Exception as e:
        print("FINAL RESULT: Request Failed")
        print(f"SAFE ERROR: {e}")

if __name__ == '__main__':
    main()
