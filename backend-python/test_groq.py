"""
Groq integration tests — isolated and full pipeline.
NEVER prints API keys, JWTs, or secrets.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groq import Groq
from app.core.config import settings

print("=" * 60)
print("STEP 9 — MINIMAL GROQ CONNECTIVITY TEST")
print("=" * 60)

api_key_present = bool(settings.GROQ_API_KEY)
print(f"GROQ_API_KEY present: {api_key_present}")
print(f"GROQ_MODEL: {settings.GROQ_MODEL}")

if not api_key_present:
    print("ABORT: No GROQ_API_KEY")
    sys.exit(1)

client = Groq(api_key=settings.GROQ_API_KEY, timeout=30.0)

# ---- Test A: Simple JSON ----
print("\n--- Test A: Minimal JSON request ---")
t0 = time.time()
try:
    resp = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": "Return only raw JSON, no markdown."},
            {"role": "user", "content": 'Return a JSON object: {"status": "ok"}'},
        ],
        temperature=0.0,
        max_tokens=64,
        response_format={"type": "json_object"},
    )
    elapsed = time.time() - t0
    choice = resp.choices[0]
    text = choice.message.content
    parsed = json.loads(text)
    print(f"  Status: SUCCESS ({elapsed:.2f}s)")
    print(f"  Model: {resp.model}")
    print(f"  Finish reason: {choice.finish_reason}")
    print(f"  Parsed JSON: {parsed}")
    test_a_ok = True
except Exception as e:
    elapsed = time.time() - t0
    print(f"  Status: FAILED ({elapsed:.2f}s)")
    print(f"  Error: {type(e).__name__}: {e}")
    test_a_ok = False

print()
print("=" * 60)
print(f"Minimal test: {'PASS' if test_a_ok else 'FAIL'}")
print("=" * 60)

if not test_a_ok:
    print("ABORT: Groq connectivity failed")
    sys.exit(1)

# ---- STEP 10: Full floor plan via provider ----
print()
print("=" * 60)
print("STEP 10 — FULL FLOOR-PLAN GENERATION (GroqProvider)")
print("=" * 60)

from app.services.ai.groq_provider import GroqProvider
from app.validators.geometry_validator import GeometryValidator, GeometryValidationError

context = {
    "plot_width": 30,
    "plot_length": 40,
    "facing": "East",
    "floors": 2,
    "bedrooms": 3,
    "bathrooms": 2,
    "kitchens": 1,
    "living_rooms": 1,
    "balconies": 1,
    "design_style": "Modern",
    "interior_style": "Minimal",
    "custom_notes": "None",
}

print(f"Context: 30x40 East, 2 floors, Modern")
print()

t0 = time.time()
try:
    provider = GroqProvider()
    layout = provider.generate_layout(context)
    elapsed = time.time() - t0

    print(f"Pydantic validation: PASS")
    print(f"  schema_version: {layout.schema_version}")
    print(f"  units: {layout.units}")
    print(f"  plot: {layout.plot.width}x{layout.plot.length} {layout.plot.facing}")
    print(f"  floors: {len(layout.floors)}")
    for floor in layout.floors:
        print(f"    Floor {floor.level} '{floor.name}': {len(floor.rooms)} rooms")
        for room in floor.rooms:
            print(f"      - {room.label} ({room.type}): {room.width}x{room.length} at ({room.x},{room.y})")
    total_rooms = sum(len(f.rooms) for f in layout.floors)
    print(f"  Total rooms: {total_rooms}")

    # Geometry validation
    print()
    try:
        GeometryValidator.validate_layout(layout)
        print("Geometry validation: PASS")
        geo_ok = True
    except GeometryValidationError as gve:
        print(f"Geometry validation: FAIL — {gve}")
        geo_ok = False

    print()
    print("=" * 60)
    print(f"RESULT: {'SUCCESS' if geo_ok else 'PARTIAL (geo fail)'}")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Pydantic: PASS")
    print(f"  Geometry: {'PASS' if geo_ok else 'FAIL'}")
    print(f"  Ready for SVG: {'YES' if geo_ok else 'NEEDS RETRY'}")
    print("=" * 60)

except Exception as e:
    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print("RESULT: FAILED")
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")
    print("=" * 60)
