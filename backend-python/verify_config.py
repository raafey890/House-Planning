import os
from dotenv import dotenv_values
from app.core.config import settings

env_dict = dotenv_values('.env')
file_key = env_dict.get('GEMINI_API_KEY')
sys_env_key = os.environ.get('GEMINI_API_KEY')
settings_key = getattr(settings, 'GEMINI_API_KEY', None)

is_placeholder = (settings_key == 'your_gemini_api_key' or file_key == 'your_gemini_api_key' or settings_key == '' or settings_key is None)
env_override = bool(sys_env_key and sys_env_key != file_key)

print(f"GEMINI KEY PRESENT: {'yes' if file_key or sys_env_key else 'no'}")
print(f"PLACEHOLDER VALUE: {'yes' if is_placeholder else 'no'}")
print(f"SETTINGS RECEIVES KEY: {'yes' if settings_key else 'no'}")
print(f"ENV OVERRIDE: {'yes' if env_override else 'no'}")
print(f"READY FOR GENERATION: {'yes' if settings_key and not is_placeholder else 'no'}")
