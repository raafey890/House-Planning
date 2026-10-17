from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import floor_plans, cost_estimation, interior_designs, exterior_designs

app = FastAPI(title="AI House Planner - Geometry & Planning Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(floor_plans.router)
app.include_router(cost_estimation.router)
app.include_router(interior_designs.catalog_router)
app.include_router(interior_designs.project_interior_router)
app.include_router(exterior_designs.catalog_router)
app.include_router(exterior_designs.project_exterior_router)

from app.core.security import get_current_user

@app.get("/api/v1/auth/me")
def verify_auth(user_id: str = Depends(get_current_user)):
    return {
        "authenticated": True,
        "user_id": user_id
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "House Planner Geometry API", "version": "1.0.0"}
