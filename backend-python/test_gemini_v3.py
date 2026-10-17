from google import genai
from app.core.config import settings

def main():
    model_name = "gemini-3.1-pro-preview"
    
    print(f"MODEL: {model_name}")
    print("GEMINI REQUEST SENT: yes")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: GEMINI_OK",
        )
        
        reply_text = response.text.strip()
        print("API KEY ACCEPTED: yes")
        print("RESPONSE RECEIVED: yes")
        print(f"RESPONSE MATCHES GEMINI_OK: {'yes' if 'GEMINI_OK' in reply_text else 'no'}")
        print("HTTP/API RESULT: SUCCESS")
        
    except Exception as e:
        print("API KEY ACCEPTED: unknown")
        print("RESPONSE RECEIVED: no")
        print("RESPONSE MATCHES GEMINI_OK: no")
        print("HTTP/API RESULT: FAILED")
        print(f"ERROR: {e}")

if __name__ == '__main__':
    main()
