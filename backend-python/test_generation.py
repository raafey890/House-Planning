"""
Controlled end-to-end generation test.
Authenticates via Supabase, picks a project, calls /generate, and reports diagnostics.
NEVER prints secrets, JWTs, or user data beyond safe summaries.
"""
import os
import sys
import json
import requests

# Add parent so we can import settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.core.config import settings

BACKEND = "http://127.0.0.1:8001"

# ---- Step 1: Sign in to Supabase to get a JWT ----
print("=" * 60)
print("STEP 1: Supabase authentication")
print("=" * 60)

# Read test credentials from environment (do NOT hardcode)
email = os.environ.get("TEST_USER_EMAIL")
password = os.environ.get("TEST_USER_PASSWORD")

if not email or not password:
    print("ERROR: Set TEST_USER_EMAIL and TEST_USER_PASSWORD env vars")
    print("Example: $env:TEST_USER_EMAIL='your@email.com'; $env:TEST_USER_PASSWORD='yourpass'")
    sys.exit(1)

auth_url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
auth_resp = requests.post(
    auth_url,
    headers={
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Content-Type": "application/json",
    },
    json={"email": email, "password": password},
    timeout=15,
)

if auth_resp.status_code != 200:
    print(f"AUTH FAILED: HTTP {auth_resp.status_code}")
    # Only print the error_description field — never dump the full body
    try:
        err_body = auth_resp.json()
        print(f"  error: {err_body.get('error', 'unknown')}")
        print(f"  description: {err_body.get('error_description', 'no description')}")
    except Exception:
        print("  (could not parse error response)")
    sys.exit(1)

auth_data = auth_resp.json()
access_token = auth_data.get("access_token", "")
user_id = auth_data.get("user", {}).get("id", "unknown")
print(f"AUTH OK  |  user_id={user_id}  token_present={bool(access_token)}")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# ---- Step 2: Find a project ----
print()
print("=" * 60)
print("STEP 2: Fetch user projects")
print("=" * 60)

# Use Supabase REST to list projects
proj_url = f"{settings.SUPABASE_URL}/rest/v1/projects?select=id,name&limit=1"
proj_resp = requests.get(
    proj_url,
    headers={
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    },
    timeout=15,
)

if proj_resp.status_code != 200 or not proj_resp.json():
    print(f"PROJECT FETCH FAILED: HTTP {proj_resp.status_code}")
    print("  (no projects found or Supabase REST error)")
    sys.exit(1)

projects = proj_resp.json()
project_id = projects[0]["id"]
project_name = projects[0].get("name", "unnamed")
print(f"PROJECT FOUND  |  id={project_id}  name={project_name}")

# ---- Step 3: Call floor-plan generation ----
print()
print("=" * 60)
print("STEP 3: Call POST /generate")
print("=" * 60)

gen_url = f"{BACKEND}/api/v1/projects/{project_id}/floor-plans/generate"
print(f"URL: {gen_url}")

try:
    gen_resp = requests.post(
        gen_url,
        headers=headers,
        json={"optimization_priority": "balanced"},
        timeout=200,  # generous overall timeout for retries
    )
except requests.exceptions.Timeout:
    print("REQUEST TIMED OUT (200s)")
    sys.exit(1)
except Exception as e:
    print(f"REQUEST EXCEPTION: {type(e).__name__}: {e}")
    sys.exit(1)

# ---- Step 4: Report ----
print()
print("=" * 60)
print("GENERATION TEST RESULTS")
print("=" * 60)

print(f"HTTP STATUS: {gen_resp.status_code}")

try:
    body = gen_resp.json()
except Exception:
    body = {"raw": gen_resp.text[:500]}

if gen_resp.status_code == 200:
    print("RESULT: SUCCESS")
    print(f"  generation_id: {body.get('generation_id')}")
    print(f"  status: {body.get('status')}")
    print(f"  floor_plan_id: {body.get('floor_plan_id')}")
    layout = body.get("layout_data", {})
    floors = layout.get("floors", [])
    total_rooms = sum(len(f.get("rooms", [])) for f in floors)
    print(f"  floors: {len(floors)}")
    print(f"  total_rooms: {total_rooms}")
    print(f"  validation: {body.get('validation')}")
    print(f"  schema_version: {layout.get('schema_version')}")
    print(f"  units: {layout.get('units')}")
    print()
    print("REACHES SVG RENDERER: YES (frontend can consume this)")
else:
    detail = body.get("detail", str(body)[:500])
    print(f"RESULT: FAILED")
    print(f"  detail: {detail}")
    print()
    print("REACHES SVG RENDERER: NO")

print()
print("=" * 60)
print("DONE")
print("=" * 60)
