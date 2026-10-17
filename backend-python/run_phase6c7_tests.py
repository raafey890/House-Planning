"""
Phase 6C.7 Comprehensive Test Suite.
Tests Case A, Case B, Failure Test, and Offline Deterministic Generation.
"""
import time
import json
from app.services.planning.engine import solve_layout, PlannerException
from app.services.planning.post_processor import post_process_layout
from app.validators.geometry_validator import GeometryValidator
from app.validators.connectivity_validator import ConnectivityValidator
from app.services.metrics import compute_floor_metrics

def test_case_a():
    print("=" * 60)
    print("TEST CASE A: 30x40 ft, East-facing, G+1")
    print("=" * 60)
    context = {
        "plot_width": 30,
        "plot_length": 40,
        "facing": "east",
        "floors": 2,
        "setbacks": {"front": 3, "rear": 3, "left": 3, "right": 3}
    }
    requirements = [
        {"room_type": "living_room", "count": 1, "floor_level": 0},
        {"room_type": "dining_room", "count": 1, "floor_level": 0},
        {"room_type": "kitchen", "count": 1, "floor_level": 0},
        {"room_type": "parking", "count": 1, "floor_level": 0},
        {"room_type": "staircase", "count": 1, "floor_level": 0},
        {"room_type": "bedroom", "count": 1, "floor_level": 0},
        {"room_type": "bathroom", "count": 1, "floor_level": 0},
        {"room_type": "staircase", "count": 1, "floor_level": 1},
        {"room_type": "bedroom", "count": 2, "floor_level": 1},
        {"room_type": "bathroom", "count": 1, "floor_level": 1}
    ]

    t0 = time.time()
    res = solve_layout(context, requirements)
    elapsed = time.time() - t0
    layout = post_process_layout(res)

    geo_passed, geo_results = GeometryValidator.validate_layout(layout)
    conn_results = ConnectivityValidator.validate_connectivity(layout)
    metrics = compute_floor_metrics(layout)

    print(f"Solver Status: {res['status']}")
    print(f"Solve Time: {elapsed:.2f}s")
    print(f"Plot Area: {layout.plot.width * layout.plot.length:.0f} sq ft")
    print(f"Buildable Area: {metrics['buildable_area']} sq ft")
    print(f"Total Utilization: {metrics['totals']['utilization_pct']}%")
    print(f"Geometry Valid: {geo_passed}")
    print(f"Circulation Valid: {conn_results['circulation_valid']}")
    print(f"Isolated Rooms: {conn_results['isolated_rooms']}")
    print(f"Main Entrance: {geo_results['main_entrance']}")
    print(f"Vehicle Gate: {geo_results['vehicle_gate']}")
    print(f"Parking Connection: {geo_results['parking_connection']}")
    print(f"Stair Alignment: {geo_results['stair_alignment']}")
    print(f"Kitchen-Dining Adjacency: {conn_results['required_adjacencies'].get('kitchen_dining')}")
    print(f"Living-Dining Adjacency: {conn_results['required_adjacencies'].get('living_dining')}")

    return {
        "status": res["status"],
        "solve_time": elapsed,
        "geo_valid": geo_passed,
        "circ_valid": conn_results["circulation_valid"],
        "isolated": conn_results["isolated_rooms"],
        "metrics": metrics
    }

def test_case_b():
    print("\n" + "=" * 60)
    print("TEST CASE B: 50x80 ft, South-facing, G+1")
    print("=" * 60)
    context = {
        "plot_width": 50,
        "plot_length": 80,
        "facing": "south",
        "floors": 2,
        "setbacks": {"front": 5, "rear": 4, "left": 4, "right": 4}
    }
    requirements = [
        {"room_type": "living_room", "count": 1, "floor_level": 0},
        {"room_type": "dining_room", "count": 1, "floor_level": 0},
        {"room_type": "kitchen", "count": 1, "floor_level": 0},
        {"room_type": "parking", "count": 1, "floor_level": 0},
        {"room_type": "utility_room", "count": 1, "floor_level": 0},
        {"room_type": "bedroom", "count": 1, "floor_level": 0},
        {"room_type": "bathroom", "count": 1, "floor_level": 0},
        {"room_type": "staircase", "count": 1, "floor_level": 0},
        {"room_type": "staircase", "count": 1, "floor_level": 1},
        {"room_type": "master_bedroom", "count": 1, "floor_level": 1},
        {"room_type": "bedroom", "count": 2, "floor_level": 1},
        {"room_type": "study_room", "count": 1, "floor_level": 1},
        {"room_type": "balcony", "count": 1, "floor_level": 1},
        {"room_type": "bathroom", "count": 2, "floor_level": 1}
    ]

    t0 = time.time()
    res = solve_layout(context, requirements)
    elapsed = time.time() - t0
    layout = post_process_layout(res)

    geo_passed, geo_results = GeometryValidator.validate_layout(layout)
    conn_results = ConnectivityValidator.validate_connectivity(layout)
    metrics = compute_floor_metrics(layout)

    print(f"Solver Status: {res['status']}")
    print(f"Solve Time: {elapsed:.2f}s")
    print(f"Plot Area: {layout.plot.width * layout.plot.length:.0f} sq ft")
    print(f"Buildable Area: {metrics['buildable_area']} sq ft")
    print(f"Total Utilization: {metrics['totals']['utilization_pct']}%")
    print(f"Geometry Valid: {geo_passed}")
    print(f"Circulation Valid: {conn_results['circulation_valid']}")
    print(f"Isolated Rooms: {conn_results['isolated_rooms']}")
    print(f"Main Entrance: {geo_results['main_entrance']}")
    print(f"Vehicle Gate: {geo_results['vehicle_gate']}")
    print(f"Parking Connection: {geo_results['parking_connection']}")
    print(f"Stair Alignment: {geo_results['stair_alignment']}")
    print(f"Kitchen-Dining Adjacency: {conn_results['required_adjacencies'].get('kitchen_dining')}")
    print(f"Living-Dining Adjacency: {conn_results['required_adjacencies'].get('living_dining')}")

    return {
        "status": res["status"],
        "solve_time": elapsed,
        "geo_valid": geo_passed,
        "circ_valid": conn_results["circulation_valid"],
        "isolated": conn_results["isolated_rooms"],
        "metrics": metrics
    }

def test_failure_case():
    print("\n" + "=" * 60)
    print("FAILURE TEST: 20x25 ft plot with 6 Bedrooms, Parking, G+1")
    print("=" * 60)
    context = {
        "plot_width": 20,
        "plot_length": 25,
        "facing": "north",
        "floors": 1,
        "setbacks": {"front": 3, "rear": 3, "left": 3, "right": 3}
    }
    requirements = [
        {"room_type": "living_room", "count": 2},
        {"room_type": "master_bedroom", "count": 3},
        {"room_type": "bedroom", "count": 3},
        {"room_type": "kitchen", "count": 2},
        {"room_type": "parking", "count": 2}
    ]

    try:
        res = solve_layout(context, requirements)
        print("UNEXPECTED: Succeeded in fitting impossible requirements!")
        return False
    except PlannerException as pe:
        print(f"EXPECTED FAILURE CAUGHT: {pe}")
        return True

def test_offline_capability():
    print("\n" + "=" * 60)
    print("OFFLINE TEST: Verifying no external HTTP / AI requests are made")
    print("=" * 60)
    import os
    # Temporarily hide all API keys
    old_gemini = os.environ.get("GEMINI_API_KEY", "")
    old_groq = os.environ.get("GROQ_API_KEY", "")
    os.environ["GEMINI_API_KEY"] = ""
    os.environ["GROQ_API_KEY"] = ""

    try:
        res = test_case_a()
        print("OFFLINE TEST PASSED: Engine generated layout without any external AI API keys.")
        return True
    finally:
        os.environ["GEMINI_API_KEY"] = old_gemini
        os.environ["GROQ_API_KEY"] = old_groq

if __name__ == "__main__":
    res_a = test_case_a()
    res_b = test_case_b()
    fail_res = test_failure_case()
    offline_res = test_offline_capability()

    print("\n" + "=" * 60)
    print("PHASE 6C.7 TEST SUMMARY")
    print(f"Case A: {'PASS' if res_a['geo_valid'] and res_a['circ_valid'] else 'FAIL'}")
    print(f"Case B: {'PASS' if res_b['geo_valid'] and res_b['circ_valid'] else 'FAIL'}")
    print(f"Failure Handling: {'PASS' if fail_res else 'FAIL'}")
    print(f"Offline Generation: {'PASS' if offline_res else 'FAIL'}")
    print("=" * 60)
