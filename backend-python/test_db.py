import os
import json
from supabase import create_client

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

res = supabase.table("projects").select("id, user_id, name, created_at").order("created_at", desc=True).limit(5).execute()
print(json.dumps(res.data, indent=2))
