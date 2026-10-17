"""
Task 6 — Full floor-plan generation test via the provider directly.
Bypasses HTTP/auth to isolate the Gemini provider behavior.
NEVER prints secrets.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.gemini_provider import GeminiProvider

# Simulated project context (the same shape the endpoint would send)
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

print("=" * 60)
print("FLOOR-PLAN GENERATION TEST (direct provider call)")
print("=" * 60)
print(f"Context: {json.dumps({k: v for k, v in context.items() if k != 'custom_notes'}, indent=2)}")
print()

t0 = time.time()
try:
    provider = GeminiProvider()
    layout = provider.generate_layout(context)
    elapsed = time.time() - t0

    print()
    print("=" * 60)
    print("RESULT: SUCCESS")
    print("=" * 60)
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Schema version: {layout.schema_version}")
    print(f"  Units: {layout.units}")
    print(f"  Plot: {layout.plot.width}x{layout.plot.length} {layout.plot.facing}")
    print(f"  Floors: {len(layout.floors)}")
    for floor in layout.floors:
        print(f"    Floor {floor.level} '{floor.name}': {len(floor.rooms)} rooms, {len(floor.walls)} walls, {len(floor.doors)} doors")
        for room in floor.rooms:
            print(f"      - {room.label} ({room.type}): {room.width}x{room.length} at ({room.x},{room.y})")
    total_rooms = sum(len(f.rooms) for f in layout.floors)
    print(f"  Total rooms: {total_rooms}")
    print(f"  Metrics: {layout.metrics}")
    print()
    print("READY FOR SVG RENDERER: YES")

except Exception as e:
    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print("RESULT: FAILED")
    print("=" * 60)
    print(f"  Elapsed: {elapsed:.2f}s")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error: {e}")
    print()
    print("READY FOR SVG RENDERER: NO")
