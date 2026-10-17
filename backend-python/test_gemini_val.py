import os
from app.core.config import settings

key = getattr(settings, 'GEMINI_API_KEY', None)
if key == 'your_gemini_api_key':
    print("Value is exactly 'your_gemini_api_key'")
elif key == '':
    print("Value is empty string")
elif key is None:
    print("Value is None")
else:
    print("Value is something else")
