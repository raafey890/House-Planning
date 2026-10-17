"""Quick test of available Groq models for JSON generation."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY, timeout=30.0)

models_to_test = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "allam-2-7b",
]

for model in models_to_test:
    print(f"\n--- Testing: {model} ---")
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return only raw JSON, no markdown."},
                {"role": "user", "content": 'Return a JSON object with exactly: {"status": "ok", "number": 42}'},
            ],
            temperature=0.0,
            max_tokens=128,
            response_format={"type": "json_object"},
        )
        text = r.choices[0].message.content
        parsed = json.loads(text)
        print(f"  OK! model={r.model} finish={r.choices[0].finish_reason}")
        print(f"  JSON: {parsed}")
    except Exception as e:
        print(f"  FAIL: {type(e).__name__}: {str(e)[:200]}")
