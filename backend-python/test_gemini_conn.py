import sys
from google import genai
from app.core.config import settings

def main():
    model_name = "gemini-2.5-pro"
    
    print("GEMINI REQUEST SENT: yes")
    print(f"MODEL: {model_name}")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: GEMINI_OK",
        )
        
        reply_text = response.text.strip()
        print("HTTP/API RESULT: SUCCESS")
        print("RESPONSE RECEIVED: yes")
        print(f"RESPONSE MATCHES GEMINI_OK: {'yes' if 'GEMINI_OK' in reply_text else 'no'}")
        print("API KEY ACCEPTED: yes")
        
    except Exception as e:
        err_msg = str(e)
        print("HTTP/API RESULT: FAILED")
        print("RESPONSE RECEIVED: no")
        print("RESPONSE MATCHES GEMINI_OK: no")
        
        if "api key" in err_msg.lower() or "400" in err_msg or "403" in err_msg or "invalid_argument" in err_msg.lower():
            print("API KEY ACCEPTED: no")
        else:
            print("API KEY ACCEPTED: unknown")
            
        print(f"ERROR TYPE: {type(e).__name__}")
        
        safe_msg = err_msg
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY in safe_msg:
            safe_msg = safe_msg.replace(settings.GEMINI_API_KEY, "[REDACTED]")
        print(f"SAFE ERROR MESSAGE: {safe_msg}")

if __name__ == '__main__':
    main()
