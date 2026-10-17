import asyncio
from supabase import create_client
from app.core.config import settings
from app.api.routes.floor_plans import generate_floor_plan, GenerateRequest
from app.services.floorplan_service import FloorplanService
from app.validators.geometry_validator import GeometryValidator

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_PUBLISHABLE_KEY)

async def test_generation():
    print("Setting up test project (50x80, South, G+1, Modern)...")
    
    # Let's get a random user from existing projects
    proj_res = supabase.table("projects").select("user_id").limit(1).execute()
    user_id = proj_res.data[0]["user_id"]
    
    # Create project
    proj_payload = {
        "user_id": user_id,
        "name": "Phase 6C.5 Test",
        "plot_width": 50.0,
        "plot_length": 80.0,
        "facing": "South",
        "floors": 2,
        "design_style": "Modern"
    }
    proj_res = supabase.table("projects").insert(proj_payload).execute()
    project_id = proj_res.data[0]["id"]
    
    # Add requirements
    reqs = [
        {"project_id": project_id, "room_type": "living_room", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "kitchen", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "dining_room", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "bedroom", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "bathroom", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "parking", "count": 1, "floor_level": 0},
        {"project_id": project_id, "room_type": "master_bedroom", "count": 1, "floor_level": 1},
        {"project_id": project_id, "room_type": "bedroom", "count": 2, "floor_level": 1},
        {"project_id": project_id, "room_type": "bathroom", "count": 2, "floor_level": 1},
        {"project_id": project_id, "room_type": "balcony", "count": 1, "floor_level": 1}
    ]
    supabase.table("project_requirements").insert(reqs).execute()

    print(f"Project created: {project_id}")
    print("Calling generate endpoint...")
    
    req = GenerateRequest(optimization_priority="balanced")
    
    try:
        res = await generate_floor_plan(project_id, req, user_id, supabase)
        if isinstance(res, dict): # Error JSON response
            print("ERROR RESPONSE:", res)
        else:
            print(f"\n--- SUCCESS! ({res.status}) ---")
            print("Validation:", res.validation)
            if res.metrics:
                print("\nMetrics:")
                print(f"  Buildable Area: {res.metrics.get('buildable_area')}")
                print(f"  Utilization:    {res.metrics.get('totals', {}).get('utilization_pct')}%")
                print(f"  Room Area:      {res.metrics.get('totals', {}).get('room_area')}")
                print(f"  Unclassified:   {res.metrics.get('totals', {}).get('unclassified_area')}")
            else:
                print("No metrics returned.")
                
            print("\nVerification Checks:")
            passed = True
            v = res.validation
            checks = ['main_entrance', 'pedestrian_gate', 'vehicle_gate', 'parking_connection', 'stair_alignment', 'stair_present', 'foyer']
            for c in checks:
                ok = v.get(c)
                print(f"  {c}: {'PASS' if ok else 'FAIL'}")
                if not ok: passed = False
            
            print(f"\nFinal Result: {'PASS' if passed else 'FAIL'}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation())
