import asyncio
from supabase import create_client

sb = create_client('https://cptjtxjqsyuwrwstcehu.supabase.co', 'sb_publishable_qSgTcS8fj2Sy_xoYN9F-Bg_NB6OudPg')
res = sb.table('ai_generations').select('*').order('created_at', desc=True).limit(1).execute()
print(res.data)
