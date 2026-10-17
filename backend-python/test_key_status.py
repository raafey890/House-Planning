from app.core.config import settings

key = settings.GEMINI_API_KEY
if key == 'your_gemini_api_key':
    print("KEY IS STILL DUMMY")
elif key == '':
    print("KEY IS EMPTY")
elif len(key) > 10:
    print("KEY IS PRESENT AND HAS LENGTH", len(key))
else:
    print("KEY IS SOMETHING ELSE")
