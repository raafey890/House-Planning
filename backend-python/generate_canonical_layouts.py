import sys
import os
import json
import hashlib
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.engine import solve_layout
from app.services.planning.post_processor import post_process_layout
from app.models.layout import LayoutData

CANONICAL_DIR = os.path.join(os.path.dirname(__file__), "canonical_layouts")
os.makedirs(CANONICAL_DIR, exist_ok=True)

def generate_and_save_canonical(name, filename, run_id, ctx, reqs):
    print(f"Generating Canonical Layout: {name} ({run_id})...")
    res = solve_layout(ctx, reqs, use_gemini=False)
    layout = post_process_layout(res)

    # Attach canonical metadata
    layout.metadata["canonical_run_id"] = run_id
    layout.metadata["canonical_name"] = name
    layout.metadata["canonical_generated_at"] = datetime.now().isoformat()

    file_path = os.path.join(CANONICAL_DIR, filename)
    json_str = layout.model_dump_json(indent=2)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json_str)

    # Compute SHA-256 hash
    sha256 = hashlib.sha256(json_str.encode('utf-8')).hexdigest()

    print(f"  Saved to: {file_path}")
    print(f"  Run ID  : {run_id}")
    print(f"  SHA-256 : {sha256}")
    return file_path, run_id, sha256

if __name__ == "__main__":
    # Case 1: 30x40 East G+1
    ctx_30 = {
        "plot_width": 30, "plot_length": 40, "facing": "east", "floors": 2,
        "design_style": "modern", "setbacks": {"front": 4, "rear": 3, "left": 3, "right": 3},
        "parking_spaces": 0
    }
    reqs_30 = [{
        "bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0
    }]
    path_30, id_30, hash_30 = generate_and_save_canonical(
        "30x40 East-facing G+1",
        "canonical_30x40_east_g1.json",
        "CANONICAL-30X40-EAST-G1-20261016",
        ctx_30,
        reqs_30
    )

    # Case 2: 50x80 South G+1
    ctx_50 = {
        "plot_width": 50, "plot_length": 80, "facing": "south", "floors": 2,
        "design_style": "modern", "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3},
        "parking_spaces": 0
    }
    reqs_50 = [{
        "bedrooms": 3, "bathrooms": 2, "kitchens": 1, "living_rooms": 1, "parking_spaces": 0
    }]
    path_50, id_50, hash_50 = generate_and_save_canonical(
        "50x80 South-facing G+1",
        "canonical_50x80_south_g1.json",
        "CANONICAL-50X80-SOUTH-G1-20261016",
        ctx_50,
        reqs_50
    )

    print("\nSummary of Canonical Layouts:")
    print(f"1. 30x40 East G+1  : ID={id_30}, Hash={hash_30[:16]}... ({os.path.basename(path_30)})")
    print(f"2. 50x80 South G+1 : ID={id_50}, Hash={hash_50[:16]}... ({os.path.basename(path_50)})")
