"""Test structured JSON without response_schema (JSON mime type only)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.genai import types
from app.core.config import settings

client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options={"timeout": 60000},
)

print("=" * 60)
print("TEST: response_mime_type=application/json WITHOUT response_schema")
print("=" * 60)

# Test 1: JSON mime type only (no schema constraint)
print("\n--- Test 1: JSON mime, no schema ---")
t0 = time.time()
try:
    resp = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Return ONLY a valid JSON object: {\"status\": \"ok\", \"number\": 42}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0,
        ),
    )
    elapsed = time.time() - t0
    print(f"  Status: SUCCESS  ({elapsed:.2f}s)")
    print(f"  Response: {resp.text[:200]}")
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED  ({elapsed:.2f}s)")
    print(f"  Error: {type(e).__name__}: {e}")

# Test 2: Plain text with JSON instructions, then parse
print("\n--- Test 2: Plain text prompt, parse JSON manually ---")
t0 = time.time()
try:
    resp2 = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="You are a JSON generator. Return ONLY a raw JSON object with no markdown formatting. The object must have: {\"status\": \"ok\", \"number\": 42}",
        config=types.GenerateContentConfig(
            temperature=0.0,
        ),
    )
    elapsed = time.time() - t0
    import json
    parsed = json.loads(resp2.text.strip())
    print(f"  Status: SUCCESS  ({elapsed:.2f}s)")
    print(f"  Parsed JSON: {parsed}")
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED  ({elapsed:.2f}s)")
    print(f"  Error: {type(e).__name__}: {e}")
    if hasattr(resp2, 'text'):
        print(f"  Raw text: {resp2.text[:200]}")

# Test 3: JSON mime with schema (the mode that keeps failing)
print("\n--- Test 3: JSON mime + schema (structured output mode) ---")
schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "number": {"type": "integer"}
    },
    "required": ["status", "number"]
}
t0 = time.time()
try:
    resp3 = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Return JSON with status=ok and number=42",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.0,
        ),
    )
    elapsed = time.time() - t0
    print(f"  Status: SUCCESS  ({elapsed:.2f}s)")
    print(f"  Response: {resp3.text[:200]}")
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED  ({elapsed:.2f}s)")
    print(f"  Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
