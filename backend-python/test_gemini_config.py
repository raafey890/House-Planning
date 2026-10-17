import os
from app.core.config import settings

key = getattr(settings, 'GEMINI_API_KEY', None)
print("GEMINI_KEY_PRESENT:", bool(key))
print("IS_DUMMY_KEY:", key == 'your_gemini_api_key' or key == '')
print("ENV_FILE_USED:", settings.Config.env_file)
