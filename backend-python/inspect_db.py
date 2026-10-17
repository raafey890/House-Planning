import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from supabase import create_client

def main():
    sb = create_client(settings.SUPABASE_URL, settings.SUPABASE_PUBLISHABLE_KEY)
    
    # Query projects
    res = sb.table("projects").select("id, name, plot_width, plot_length, facing, floors, created_at").execute()
    print("Projects count:", len(res.data))
    for p in res.data:
        print(f"Project ID: {p['id']}, Name: {p.get('name')}, Size: {p.get('plot_width')}x{p.get('plot_length')}, Facing: {p.get('facing')}, Floors: {p.get('floors')}")
        
        # Check floor plans for this project
        fps = sb.table("floor_plans").select("id, version_name, created_at, generation_engine").eq("project_id", p["id"]).order("created_at", desc=True).execute()
        print(f"  Floor plans ({len(fps.data)}):")
        for fp in fps.data:
            print(f"    FP ID: {fp['id']}, Version: {fp.get('version_name')}, Created: {fp.get('created_at')}, Engine: {fp.get('generation_engine')}")

if __name__ == "__main__":
    main()
