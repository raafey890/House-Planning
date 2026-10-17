from supabase import create_client, Client
from app.core.config import settings
from fastapi import HTTPException, status
from typing import Dict, Any

async def verify_ownership(project_id: str, supabase: Client, user_id: str = None) -> bool:
    """
    Queries Supabase to verify project ownership.
    If user_id is provided, explicitly verifies project.user_id == user_id.
    """
    try:
        query = supabase.table("projects").select("id, user_id").eq("id", project_id)
        if user_id:
            query = query.eq("user_id", user_id)
        response = query.execute()
        
        # If project doesn't exist or user doesn't own it, response.data will be empty
        if not response.data:
            return False
            
        return True
        
    except Exception as e:
        # Don't swallow unexpected API errors as a mere "False" auth rejection.
        # Check if it's an API configuration error
        err_msg = str(e)
        if "API key" in err_msg or "Configuration" in err_msg or "auth" in err_msg.lower():
            print(f"Infrastructure Error verifying ownership: {e}")
            raise HTTPException(status_code=500, detail="Database infrastructure failure")
        print(f"Unexpected error verifying ownership: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while verifying access")

async def get_planning_context(project_id: str, supabase: Client) -> Dict[str, Any]:
    """
    Fetches project and project_requirements from Supabase using the user's authenticated client.
    """
    project_res = supabase.table("projects").select("*").eq("id", project_id).execute()
    req_res = supabase.table("project_requirements").select("*").eq("project_id", project_id).execute()
    
    if not project_res.data:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project = project_res.data[0]
    requirements = req_res.data[0] if req_res.data else {}
    
    # Compute setbacks (defaults if not provided)
    front_setback = project.get("front_setback", 4)  # feet
    rear_setback = project.get("rear_setback", 4)
    left_setback = project.get("left_setback", 3)
    right_setback = project.get("right_setback", 3)

    # Buildable footprint inside setbacks
    buildable_width = max(0, project.get("plot_width", 0) - left_setback - right_setback)
    buildable_length = max(0, project.get("plot_length", 0) - front_setback - rear_setback)

    context = {
        "project_id": project_id,
        "plot_width": project.get("plot_width", 0),
        "plot_length": project.get("plot_length", 0),
        "facing": project.get("facing", "Unknown"),
        "floors": project.get("floors", 1),
        "budget": project.get("budget", 0),
        "design_style": project.get("design_style", "Modern"),
        "interior_style": project.get("interior_style", "Minimal"),
        "bedrooms": requirements.get("bedrooms", 0),
        "bathrooms": requirements.get("bathrooms", 0),
        "kitchens": requirements.get("kitchens", 0),
        "living_rooms": requirements.get("living_rooms", 0),
        "balconies": requirements.get("balconies", 0),
        "custom_notes": requirements.get("custom_notes", ""),
        "setbacks": {
            "front": front_setback,
            "rear": rear_setback,
            "left": left_setback,
            "right": right_setback,
        },
        "buildable_boundary": {
            "width": buildable_width,
            "length": buildable_length,
        },
    }
    
    return context

