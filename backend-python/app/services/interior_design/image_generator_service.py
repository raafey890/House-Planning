"""
Personalized Photorealistic Interior Image Generator Service — Phase 6E.1B.
Constructs geometry-grounded, architecturally coherent prompts tailored to
exact room dimensions, door/window openings, aspect ratio, and user-customized finishes.

Provides an honest provider abstraction layer:
- Attempts Google Gemini Imagen / Image Generation if configured and within quota.
- Surfaces honest diagnostic errors (e.g. 429 RESOURCE_EXHAUSTED / limit: 0) without simulating success.
- Serves verified static artifacts from `frontend/public/images/interiors/generated/` when available.
"""

import os
import re
import json
import logging
import math
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models.interior_design import (
    RoomImageGenerationRequest,
    RoomImageGenerationResponse
)
from app.services.interior_design.catalog import get_interior_design_by_id

logger = logging.getLogger("interior.image_generator")

# Directory for saved personalized interior renderings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
GENERATED_IMAGES_DIR = os.path.join(BASE_DIR, "frontend", "public", "images", "interiors", "generated")
os.makedirs(GENERATED_IMAGES_DIR, exist_ok=True)


def build_geometry_grounded_prompt(req: RoomImageGenerationRequest) -> str:
    """
    Constructs an architectural prompt embedding the room's validated geometry,
    aspect ratio, fenestration (doors/windows), circulation clearances,
    and user-selected interior finishes.
    """
    design = get_interior_design_by_id(req.design_id)
    design_name = design.name if design else "Contemporary Interior"
    design_style = design.style if design else "Modern"
    palette = design.description if design else "Neutral palette"

    # Dimensions & aspect ratio
    w = req.room_width
    l = req.room_length
    area = req.room_area or (w * l)
    aspect_ratio = round(w / l, 2)
    spatial_feel = "elongated rectangular" if aspect_ratio < 0.75 or aspect_ratio > 1.33 else "well-proportioned square-like"

    # Room type specifics
    norm_type = req.room_type.lower().replace(" ", "_")
    custom = req.customizations or {}
    flooring = custom.get("flooring_choice", design.flooring_default if design else "vitrified tiles")
    wall_finish = custom.get("wall_finish_choice", design.wall_finish_default if design else "acrylic emulsion")
    ceiling = custom.get("ceiling_option_id", design.ceiling_concept if design else "gypsum false ceiling")
    lighting_points = custom.get("lighting_points_count", 6)

    # Fenestration text
    openings_desc = []
    if req.doors:
        openings_desc.append(f"{len(req.doors)} entry door opening(s)")
    else:
        openings_desc.append("1 standard entry door opening with clear swing clearance")

    if req.windows:
        openings_desc.append(f"{len(req.windows)} exterior glazed window(s)")
    else:
        openings_desc.append("wide natural daylight exterior window")

    openings_str = " and ".join(openings_desc)

    # Room category specific guidelines
    category_context = ""
    if "bed" in norm_type or "guest" in norm_type:
        bed_size = "king-size platform bed" if w >= 11.0 else "queen-size platform bed"
        category_context = (
            f"Centered {bed_size} against primary feature wall, dual floating nightstands with min 2.5 ft side clearance, "
            f"integrated wardrobe run along side wall, warm 2700K ambient cove lighting."
        )
    elif "kit" in norm_type:
        counter_type = "L-shaped continuous modular counter" if w >= 9.0 else "parallel galley counter run"
        category_context = (
            f"Ergonomic {counter_type} with quartz countertop, built-in induction hob and chimney, double bowl sink, "
            f"upper display cabinets with under-cabinet 4000K task lighting, clear central work aisle."
        )
    elif "liv" in norm_type or "hall" in norm_type:
        category_context = (
            f"Spacious seating arrangement with fabric sectional sofa, floating TV console along feature media wall, "
            f"coffee table, acoustic wall panelling, perimeter gypsum drop ceiling with magnetic track spots."
        )
    elif "din" in norm_type:
        chair_count = 6 if area >= 100 else 4
        category_context = (
            f"Centered solid wood {chair_count}-seater dining table, upholstered dining chairs with 3 ft pull-out clearance, "
            f"modern linear chandelier pendant directly above table, side crockery storage unit."
        )
    elif "bath" in norm_type or "toilet" in norm_type:
        category_context = (
            f"Frameless glass wet-shower partition, anti-skid porcelain floor tiles, modern wall-hung WC, "
            f"floating vanity counter with integrated ceramic basin and backlit mirror."
        )
    else:
        category_context = f"Custom architectural interior tailored to {req.room_name}."

    prompt = (
        f"A photorealistic architectural interior photograph of a {req.room_name} ({req.room_type.replace('_', ' ')}). "
        f"Room physical dimensions: {w:.1f} ft width by {l:.1f} ft length ({area:.0f} sq ft floor area), {spatial_feel} layout. "
        f"Design style: {design_name} ({design_style}). "
        f"Fenestration and access: {openings_str}. "
        f"Flooring material: {flooring}. "
        f"Wall treatment: {wall_finish}. "
        f"Ceiling: {ceiling} with {lighting_points} recessed warm LED spotlight points. "
        f"Layout and furnishings: {category_context} "
        f"Professional interior design photography, 8k resolution, authentic materials, natural daylight, warm atmospheric illumination."
    )
    return prompt


def generate_personalized_room_image(req: RoomImageGenerationRequest) -> RoomImageGenerationResponse:
    """
    Executes the personalized image generation workflow.
    Checks available provider (Gemini Imagen API) and reports status honestly.
    """
    prompt = build_geometry_grounded_prompt(req)
    w = req.room_width
    l = req.room_length
    area = req.room_area or (w * l)
    aspect_ratio = round(w / l, 2)

    dimensions_meta = {
        "width_ft": w,
        "length_ft": l,
        "area_sqft": area,
        "aspect_ratio": aspect_ratio
    }

    # Clean filename for this project and room
    safe_proj = re.sub(r'[^a-zA-Z0-9_-]', '_', req.project_id)
    safe_room = re.sub(r'[^a-zA-Z0-9_-]', '_', req.room_id)
    output_filename = f"proj_{safe_proj}_{safe_room}.jpg"
    output_path = os.path.join(GENERATED_IMAGES_DIR, output_filename)
    public_url = f"/images/interiors/generated/{output_filename}"

    # 1. Check if a pre-generated verified artifact exists for this project/room (unless force_regenerate)
    if not req.force_regenerate and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
        return RoomImageGenerationResponse(
            status="success",
            image_url=public_url,
            prompt_used=prompt,
            room_id=req.room_id,
            design_id=req.design_id,
            provider="Saved Personalized Room Artifact",
            dimensions=dimensions_meta,
            generation_metadata={
                "cached": True,
                "file_size_bytes": os.path.getsize(output_path),
                "generated_at": datetime.fromtimestamp(os.path.getmtime(output_path)).isoformat()
            }
        )

    # 2. Attempt Google Gemini Image Generation via google.genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return RoomImageGenerationResponse(
            status="provider_error",
            image_url=None,
            prompt_used=prompt,
            room_id=req.room_id,
            design_id=req.design_id,
            provider="Google Gemini Image Generation",
            dimensions=dimensions_meta,
            error_detail="GEMINI_API_KEY is not configured in backend-python/.env.",
            generation_metadata={"error_code": "API_KEY_MISSING"}
        )

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Call gemini image generation model
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt
        )

        # Extract image if returned
        image_bytes = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    break

        if image_bytes:
            with open(output_path, "wb") as f:
                f.write(image_bytes)

            return RoomImageGenerationResponse(
                status="success",
                image_url=public_url,
                prompt_used=prompt,
                room_id=req.room_id,
                design_id=req.design_id,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                generation_metadata={
                    "cached": False,
                    "file_size_bytes": len(image_bytes),
                    "generated_at": datetime.utcnow().isoformat()
                }
            )
        else:
            return RoomImageGenerationResponse(
                status="provider_error",
                image_url=None,
                prompt_used=prompt,
                room_id=req.room_id,
                design_id=req.design_id,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                error_detail="Provider did not return inline image data.",
                generation_metadata={"error_code": "NO_IMAGE_DATA"}
            )

    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Gemini image generation provider error: {err_msg}")
        
        # Check for Quota exhaustion
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "limit: 0" in err_msg:
            quota_detail = (
                "Google Gemini API reported 429 RESOURCE_EXHAUSTED: Free tier image generation quota limit is 0 "
                "for this project. A paid Gemini API key with billing enabled is required for real-time external image generation. "
                "The reference design photograph and plan-aware 2D room blueprint remain fully functional."
            )
            return RoomImageGenerationResponse(
                status="provider_error",
                image_url=None,
                prompt_used=prompt,
                room_id=req.room_id,
                design_id=req.design_id,
                provider="Google Gemini (gemini-2.5-flash-image)",
                dimensions=dimensions_meta,
                error_detail=quota_detail,
                generation_metadata={
                    "error_code": "RESOURCE_EXHAUSTED_429",
                    "raw_error": err_msg[:250]
                }
            )

        return RoomImageGenerationResponse(
            status="provider_error",
            image_url=None,
            prompt_used=prompt,
            room_id=req.room_id,
            design_id=req.design_id,
            provider="Google Gemini (gemini-2.5-flash-image)",
            dimensions=dimensions_meta,
            error_detail=f"Image generation failed: {err_msg[:200]}",
            generation_metadata={"error_code": "PROVIDER_EXCEPTION", "raw_error": err_msg[:250]}
        )
