import asyncio
from supabase import create_client
async def main():
    try:
        sb = create_client('https://cptjtxjqsyuwrwstcehu.supabase.co', 'your_supabase_service_role_key')
        res = sb.table('projects').select('id').limit(1).execute()
        print(res)
    except Exception as e:
        print(f"Exception: {type(e).__name__} - {e}")
asyncio.run(main())
