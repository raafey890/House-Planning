from google import genai
from app.core.config import settings
import re

def main():
    model_name = "gemini-3.1-pro-preview"
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=model_name,
            contents="Reply with exactly: GEMINI_OK",
        )
        reply_text = response.text.strip()
        
        print("RESULT: SUCCESS")
        print("HTTP STATUS: 200 OK")
        print(f"RESPONSE RECEIVED: {reply_text}")
        print("QUOTA ERROR: no")
        print("RETRY INFORMATION: none")
        
    except Exception as e:
        err_msg = str(e)
        print("RESULT: FAILED")
        print("RESPONSE RECEIVED: no")
        
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            print("HTTP STATUS: 429 RESOURCE_EXHAUSTED")
            print("QUOTA ERROR: yes")
            
            retry_info = "unknown"
            match = re.search(r"Please retry in (.*?)\.", err_msg)
            if match:
                retry_info = match.group(1)
            else:
                match2 = re.search(r"'retryDelay': '(.*?)'", err_msg)
                if match2:
                    retry_info = match2.group(1)
                else:
                    retry_info = "yes (present in headers)"
            print(f"RETRY INFORMATION: {retry_info}")
        else:
            print(f"HTTP STATUS: {type(e).__name__}")
            print("QUOTA ERROR: no")
            print("RETRY INFORMATION: none")

if __name__ == '__main__':
    main()
