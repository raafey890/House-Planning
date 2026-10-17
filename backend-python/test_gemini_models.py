from google import genai
from app.core.config import settings

def main():
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        models = client.models.list(config={'page_size': 100})
        
        available = []
        for m in models:
            if m.name.startswith("models/gemini"):
                available.append(m.name)
        
        # Sort and deduplicate if necessary, but list_models returns unique
        print("AVAILABLE GENERATION MODELS:")
        for i, m in enumerate(available, 1):
            print(f"{i}. {m}")
            
        rec = "gemini-1.5-flash"
        reason = "Generous free tier limits (15 RPM vs Pro's 2 RPM), native JSON structured output support, fast execution, and highly capable for complex JSON generation tasks like House Planning."
        
        for m in available:
            if "2.0-flash" in m:
                rec = "gemini-2.0-flash"
                reason = "Latest flash model with native JSON schema support, extremely fast, highly capable reasoning, and generous free-tier quotas suitable for development."
                break
                
        print(f"RECOMMENDED DEVELOPMENT MODEL: {rec}")
        print(f"REASON: {reason}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    main()
