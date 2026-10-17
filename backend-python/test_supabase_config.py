from dotenv import dotenv_values
from app.core.config import settings

env_dict = dotenv_values('.env')
print(f"URL IN ENV: {'yes' if env_dict.get('SUPABASE_URL') else 'no'}")
print(f"KEY IN ENV: {'yes' if env_dict.get('SUPABASE_PUBLISHABLE_KEY') else 'no'}")

url_settings = getattr(settings, 'SUPABASE_URL', None)
key_settings = getattr(settings, 'SUPABASE_PUBLISHABLE_KEY', None)

print(f"URL IN SETTINGS: {'yes' if url_settings else 'no'}")
print(f"KEY IN SETTINGS: {'yes' if key_settings else 'no'}")
