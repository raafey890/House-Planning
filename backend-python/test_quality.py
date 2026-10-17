"""
Test script for the new Phase 6C.1 Floor Plan Quality improvements.
Uses the exact retry logic from floor_plans.py.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai.provider_factory import generate_with_fallback
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

print(f"Context: {context['plot_width']}x{context['plot_length']} {context['facing']}, {context['floors']} floors")

max_attempts = 3
feedback = None
layout_data = None
valid = False
provider_used = "unknown"
errors = []
t0 = time.time()

for attempt in range(max_attempts):
    print(f"\n--- ATTEMPT {attempt + 1}/{max_attempts} ---")
    if feedback:
        print(f"Feedback passed: {feedback}")
        
    try:
        layout_data, provider_used = generate_with_fallback(context, feedback)
        
        # Calculate utilization before validation for reporting
        b_width = layout_data.plot.buildable_boundary.width
        b_length = layout_data.plot.buildable_boundary.length
        buildable_area = b_width * b_length
        print(f"  Buildable Area: {buildable_area} sq ft")
        
        for floor in layout_data.floors:
            floor_area = sum(r.width * r.length for r in floor.rooms)
            print(f"  Floor {floor.level} Used Area: {floor_area} sq ft ({(floor_area/buildable_area)*100:.1f}%)")
            
        print(f"  Total rooms: {sum(len(f.rooms) for f in layout_data.floors)}")

        # Validate quality
        GeometryValidator.validate_layout(layout_data)
        
        valid = True
        print("  Validation: PASS")
        break
        
    except GeometryValidationError as gve:
        feedback = str(gve)
        errors.append(feedback)
        print(f"  Validation: FAIL -> {feedback}")
    except Exception as e:
        feedback = f"System Error: {e}"
        errors.append(feedback)
        print(f"  Validation: FAIL -> {feedback}")

elapsed = time.time() - t0

print("\n" + "="*60)
print(f"FINAL RESULT: {'SUCCESS' if valid else 'FAILED'}")
print(f"Elapsed: {elapsed:.2f}s")
if valid:
    total_rooms = sum(len(f.rooms) for f in layout_data.floors)
    print(f"Total Rooms: {total_rooms}")
    has_stair = any(r.type == "stairs" or r.type == "staircase" for f in layout_data.floors for r in f.rooms)
    print(f"Stairs Present: {has_stair}")
else:
    print("Errors:")
    for i, e in enumerate(errors):
        print(f"  {i+1}. {e}")
print("="*60)
