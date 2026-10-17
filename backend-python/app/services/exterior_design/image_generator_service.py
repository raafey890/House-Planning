"""
Personalized Photorealistic Exterior Image Generator Service — Phase 6F.2.
Constructs geometry-grounded, architecturally coherent prompts tailored to
exact plot frontage, floor levels, selected exterior design style, view angle,
day/night lighting, and user-customized paint/material finishes.

Provides an honest provider abstraction layer:
- Attempts Google Gemini Imagen / Image Generation (`gemini-2.5-flash-image`) if configured and within quota.
- Surfaces honest diagnostic errors (e.g. 429 RESOURCE_EXHAUSTED / limit: 0) without simulating success.
- Serves verified static artifacts from `frontend/public/images/exteriors/generated/` when available.
"""

import os
import re
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.exterior_design import (
    ExteriorVisualizationRequest,
    ExteriorVisualizationResponse
)
from app.services.exterior_design.catalog import get_exterior_design_by_id

logger = logging.getLogger("exterior.image_generator")

# Directory for saved personalized exterior renderings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
GENERATED_EXTERIORS_DIR = os.path.join(BASE_DIR, "frontend", "public", "images", "exteriors", "generated")
os.makedirs(GENERATED_EXTERIORS_DIR, exist_ok=True)


def build_exterior_geometry_prompt(req: ExteriorVisualizationRequest) -> str:
    """
    Constructs an architectural prompt embedding the house's validated plot frontage,
    floor levels, aspect ratio, selected exterior style, and user-selected colors and materials.
    """
    design = get_exterior_design_by_id(req.design_id)
    design_name = design.name if design else "Contemporary Indian Residence"
    design_style = design.style if design else "Modern"
    category = design.category if design else "modern_contemporary"

    frontage = req.plot_width or 30.0
    depth = req.plot_length or 40.0
    floors = req.floors or 1
    floor_str = f"G+{floors - 1} ({floors} level{'s' if floors > 1 else ''})"

    # Colors
    c = req.colors or {}
    primary_color = c.get("primary_wall", design.primary_paint_color.get("hex", "#F4F4F0") if design else "#F4F4F0")
    accent_color = c.get("accent_wall", design.secondary_paint_color.get("hex", "#2B313B") if design else "#2B313B")
    boundary_color = c.get("boundary_wall", accent_color)
    door_color = c.get("door", "#8B5A2B")

    # Materials
    m = req.materials or {}
    finish = m.get("finish_type", "smooth_acrylic_emulsion").replace("_", " ")
    cladding = m.get("cladding_type", "wooden_slats").replace("_", " ")
    railing = m.get("railing_material", "toughened_glass").replace("_", " ")

    # View Angle Description
    view_desc = "Straight-on frontal elevation orthographic view"
    if req.view_angle == "front_left":
        view_desc = "Front-left three-quarter (3/4) architectural perspective showing front facade and left depth wall"
    elif req.view_angle == "front_right":
        view_desc = "Front-right three-quarter (3/4) architectural perspective showing front facade and right depth wall"

    # Lighting Description
    lighting_desc = "Bright clear daylight, warm sunlight casting crisp architectural shadows under cantilevers and balconies"
    if req.lighting_mode == "night":
        lighting_desc = (
            "Dusk/twilight blue hour architectural photography, deep indigo sky, warm 2700K interior illumination glowing "
            "through glazed floor-to-ceiling windows, dramatic upward and downward architectural LED wall grazers on columns "
            "and accent cladding, glowing boundary pillar lanterns, ambient entrance portico wash"
        )

    # Architectural composition
    balcony_clause = f"Cantilevered master balcony with {railing} on upper level, " if floors > 1 else ""
    boundary_clause = f"Front compound boundary wall finished in {boundary_color} with a motorized sliding driveway gate."

    prompt = (
        f"A photorealistic architectural photograph of a luxury residential building exterior in {design_style} style ({design_name}). "
        f"House physical footprint: {frontage:.1f} ft wide frontage by {depth:.1f} ft depth, building height: {floor_str}. "
        f"Perspective: {view_desc}. "
        f"Lighting and atmosphere: {lighting_desc}. "
        f"Color palette: Primary wall body in {primary_color} ({finish}), cantilevered accent feature wall in {accent_color} with {cladding} cladding. "
        f"Main entrance portal with grand teak pivot door ({door_color}) and concrete canopy. "
        f"{balcony_clause}"
        f"{boundary_clause} "
        f"Paved granite driveway, neat manicured landscaping, professional architectural magazine photography, 8k resolution, perfectly straight verticals."
    )
    return prompt


def generate_personalized_exterior_image(req: ExteriorVisualizationRequest) -> ExteriorVisualizationResponse:
    """
    Executes the personalized exterior image generation workflow.
    Checks available provider (Gemini Imagen API) and reports status honestly.
    """
    prompt = build_exterior_geometry_prompt(req)
    w = req.plot_width or 30.0
    l = req.plot_length or 40.0
    floors = req.floors or 1

    dimensions_meta = {
        "plot_width_ft": w,
        "plot_length_ft": l,
        "floors": floors,
        "facing": req.plot_facing or "North",
        "aspect_ratio": round(w / l, 2)
    }

    design = get_exterior_design_by_id(req.design_id)
    design_name = design.name if design else "Exterior Elevation"

    # File caching convention
    safe_proj = re.sub(r'[^a-zA-Z0-9_-]', '_', req.project_id)
    safe_design = re.sub(r'[^a-zA-Z0-9_-]', '_', req.design_id)
    angle = req.view_angle or "front"
    mode = req.lighting_mode or "daylight"
    output_filename = f"proj_{safe_proj}_{safe_design}_{angle}_{mode}.jpg"
    output_path = os.path.join(GENERATED_EXTERIORS_DIR, output_filename)
    public_url = f"/images/exteriors/generated/{output_filename}"

    colors_used = req.colors or {}
    materials_used = req.materials or {}

    # 1. Check if a pre-generated verified artifact exists for this project/design/angle/lighting
    if not req.force_regenerate and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        return ExteriorVisualizationResponse(
            status="success",
            preview_mode="ai_generated",
            svg_content=None,
            image_url=public_url,
            view_angle=angle,
            lighting_mode=mode,
            project_id=req.project_id,
            design_id=req.design_id,
            design_name=design_name,
            provider="Saved Personalized Exterior Artifact",
            dimensions=dimensions_meta,
            colors_used=colors_used,
            materials_used=materials_used,
            prompt_used=prompt,
            metadata={
                "cached": True,
                "file_size_bytes": os.path.getsize(output_path),
                "generated_at": datetime.fromtimestamp(os.path.getmtime(output_path)).isoformat()
            }
        )

    # 2. Check Gemini API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return ExteriorVisualizationResponse(
            status="provider_error",
            preview_mode="ai_generated",
            svg_content=None,
            image_url=None,
            view_angle=angle,
            lighting_mode=mode,
            project_id=req.project_id,
            design_id=req.design_id,
            design_name=design_name,
            provider="Google Gemini Image Generation",
            dimensions=dimensions_meta,
            colors_used=colors_used,
            materials_used=materials_used,
            prompt_used=prompt,
            error_detail="GEMINI_API_KEY is not configured in backend-python/.env.",
            metadata={"error_code": "API_KEY_MISSING"}
        )

    # 3. Attempt Google Gemini Image Generation via google.genai
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt
        )

        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if image_bytes:
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            return ExteriorVisualizationResponse(
                status="success",
                preview_mode="ai_generated",
                svg_content=None,
                image_url=public_url,
                view_angle=angle,
                lighting_mode=mode,
                project_id=req.project_id,
                design_id=req.design_id,
                design_name=design_name,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                colors_used=colors_used,
                materials_used=materials_used,
                prompt_used=prompt,
                metadata={
                    "cached": False,
                    "file_size_bytes": len(image_bytes),
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
        else:
            return ExteriorVisualizationResponse(
                status="provider_error",
                preview_mode="ai_generated",
                svg_content=None,
                image_url=None,
                view_angle=angle,
                lighting_mode=mode,
                project_id=req.project_id,
                design_id=req.design_id,
                design_name=design_name,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                colors_used=colors_used,
                materials_used=materials_used,
                prompt_used=prompt,
                error_detail="Provider did not return inline image data.",
                metadata={"error_code": "NO_IMAGE_DATA"}
            )

    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Gemini exterior image generation provider error: {err_msg}")

        # Check for Quota exhaustion
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "limit: 0" in err_msg:
            quota_detail = (
                "Google Gemini API reported 429 RESOURCE_EXHAUSTED: Free tier image generation quota limit is 0 "
                "for this project. A paid Gemini API key with billing enabled is required for real-time external image generation. "
                "The personalized plan-aware vector elevation preview remains fully functional."
            )
            return ExteriorVisualizationResponse(
                status="provider_error",
                preview_mode="ai_generated",
                svg_content=None,
                image_url=None,
                view_angle=angle,
                lighting_mode=mode,
                project_id=req.project_id,
                design_id=req.design_id,
                design_name=design_name,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                colors_used=colors_used,
                materials_used=materials_used,
                prompt_used=prompt,
                error_detail=quota_detail,
                metadata={
                    "error_code": "RESOURCE_EXHAUSTED_429",
                    "raw_error": err_msg[:250]
                }
            )

        return ExteriorVisualizationResponse(
            status="provider_error",
            preview_mode="ai_generated",
            svg_content=None,
            image_url=None,
            view_angle=angle,
            lighting_mode=mode,
            project_id=req.project_id,
            design_id=req.design_id,
            design_name=design_name,
            provider="Google Gemini (gemini-2.5-flash-image)",
            dimensions=dimensions_meta,
            colors_used=colors_used,
            materials_used=materials_used,
            prompt_used=prompt,
            error_detail=f"Image generation failed: {err_msg[:200]}",
            metadata={"error_code": "PROVIDER_EXCEPTION", "raw_error": err_msg[:250]}
        )
