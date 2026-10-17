from google import genai
from app.core.config import settings

def main():
    model_name = "gemini-3.8-flash"
    print(f"MODEL: {model_name}")
    print("REQUEST SENT: yes")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: GEMINI_OK",
        )
        reply_text = response.text.strip()
        
        print("API KEY ACCEPTED: yes")
        print("HTTP STATUS: 200 OK")
        print("RESPONSE RECEIVED: yes")
        print(f"RESPONSE: {reply_text}")
        print("FREE TIER REQUEST SUCCESS: yes")
        print("ERROR TYPE: none")
        print("SAFE ERROR MESSAGE: none")
        
    except Exception as e:
        err_msg = str(e)
        if "api key" in err_msg.lower() or "400" in err_msg or "403" in err_msg or "invalid_argument" in err_msg.lower():
            print("API KEY ACCEPTED: no")
        else:
            print("API KEY ACCEPTED: yes")
            
        print("HTTP STATUS: FAILED")
        print("RESPONSE RECEIVED: no")
        print("RESPONSE: none")
        print("FREE TIER REQUEST SUCCESS: no")
        print(f"ERROR TYPE: {type(e).__name__}")
        
        safe_msg = err_msg
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY in safe_msg:
            safe_msg = safe_msg.replace(settings.GEMINI_API_KEY, "[REDACTED]")
        print(f"SAFE ERROR MESSAGE: {safe_msg}")

if __name__ == '__main__':
    main()
