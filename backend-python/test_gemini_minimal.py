"""
Task 6 — Minimal Gemini connectivity test.
Tests a simple prompt BEFORE trying the full floor-plan schema.
NEVER prints API keys or secrets.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google import genai
from google.genai import types
from app.core.config import settings

print("=" * 60)
print("TASK 6A — MINIMAL GEMINI REQUEST (no schema)")
print("=" * 60)

api_key_present = bool(settings.GEMINI_API_KEY)
print(f"API key present: {api_key_present}")
if not api_key_present:
    print("ABORT: No API key")
    sys.exit(1)

sdk_version = getattr(genai, "__version__", "unknown")
print(f"SDK version: {sdk_version}")

# Use the same timeout as the fixed provider: 60000 ms
client = genai.Client(
    api_key=settings.GEMINI_API_KEY,
    http_options={"timeout": 60000},
)

model = "gemini-3.8-flash"
print(f"Model: {model}")
print(f"Timeout: 60000 ms (60s)")
print()

# ---- Test A: Simple text prompt, no schema ----
print("--- Test A: Simple text prompt ---")
t0 = time.time()
try:
    resp = client.models.generate_content(
        model=model,
        contents="Reply with only the word OK",
        config=types.GenerateContentConfig(
            temperature=0.0,
        ),
    )
    elapsed = time.time() - t0
    
    candidates = getattr(resp, "candidates", None)
    candidate_count = len(candidates) if candidates else 0
    finish_reason = None
    if candidates:
        finish_reason = getattr(candidates[0], "finish_reason", None)
    
    text = resp.text if resp.text else "(empty)"
    print(f"  Status: SUCCESS")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Candidates: {candidate_count}")
    print(f"  Finish reason: {finish_reason}")
    print(f"  Response text: {text[:100]}")
    test_a_ok = True
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")
    test_a_ok = False

print()

# ---- Test B: Structured JSON with a tiny schema ----
print("--- Test B: Structured JSON (tiny schema) ---")
tiny_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "number": {"type": "integer"}
    },
    "required": ["status", "number"]
}

t0 = time.time()
try:
    resp2 = client.models.generate_content(
        model=model,
        contents="Return a JSON object with status set to 'ok' and number set to 42.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=tiny_schema,
            temperature=0.0,
        ),
    )
    elapsed = time.time() - t0
    
    candidates = getattr(resp2, "candidates", None)
    candidate_count = len(candidates) if candidates else 0
    finish_reason = None
    if candidates:
        finish_reason = getattr(candidates[0], "finish_reason", None)
    
    text = resp2.text if resp2.text else "(empty)"
    print(f"  Status: SUCCESS")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Candidates: {candidate_count}")
    print(f"  Finish reason: {finish_reason}")
    print(f"  Response text: {text[:200]}")
    test_b_ok = True
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")
    test_b_ok = False

print()
print("=" * 60)
print(f"Test A (simple text): {'PASS' if test_a_ok else 'FAIL'}")
print(f"Test B (structured JSON): {'PASS' if test_b_ok else 'FAIL'}")
print("=" * 60)

if test_a_ok and test_b_ok:
    print("NETWORK AND GEMINI: WORKING")
    print("Proceed to full floor-plan test.")
elif test_a_ok and not test_b_ok:
    print("NETWORK OK but SCHEMA FAILURE")
    print("The floor-plan schema may have issues.")
elif not test_a_ok:
    print("NETWORK OR AUTH FAILURE")
    print("Cannot reach Gemini at all.")
