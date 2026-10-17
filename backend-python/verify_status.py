import os
from dotenv import dotenv_values
from app.core.config import settings

env_path = getattr(settings.Config, 'env_file', '.env')

env_dict = dotenv_values(env_path) if os.path.exists(env_path) else {}
file_key = env_dict.get('GEMINI_API_KEY')
sys_env_key = os.environ.get('GEMINI_API_KEY')
settings_key = getattr(settings, 'GEMINI_API_KEY', None)

saved_file_key_present = bool(file_key)
saved_file_placeholder = (file_key == 'your_gemini_api_key')
settings_key_present = bool(settings_key and settings_key != 'your_gemini_api_key')
file_matches_settings = (file_key == settings_key)
system_env_override = bool(sys_env_key and sys_env_key != file_key)
ready = saved_file_key_present and not saved_file_placeholder and settings_key_present and file_matches_settings

print(f"SAVED FILE KEY PRESENT: {'yes' if saved_file_key_present else 'no'}")
print(f"SAVED FILE PLACEHOLDER: {'yes' if saved_file_placeholder else 'no'}")
print(f"SETTINGS KEY PRESENT: {'yes' if settings_key_present else 'no'}")
print(f"FILE MATCHES SETTINGS: {'yes' if file_matches_settings else 'no'}")
print(f"ENV FILE PATH: {env_path}")
print(f"SYSTEM ENV OVERRIDE: {'yes' if system_env_override else 'no'}")
print(f"READY FOR GEMINI TEST: {'yes' if ready else 'no'}")
