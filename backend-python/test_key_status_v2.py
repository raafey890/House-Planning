from app.core.config import settings

key = settings.GEMINI_API_KEY
if key == 'your_gemini_api_key':
    print("GEMINI_API_KEY present: yes")
    print("Placeholder value: yes")
elif key == '':
    print("GEMINI_API_KEY present: no")
    print("Placeholder value: n/a")
elif key is not None and len(key) > 5:
    print("GEMINI_API_KEY present: yes")
    print("Placeholder value: no")
else:
    print("GEMINI_API_KEY present: yes")
    print("Placeholder value: unknown state")
