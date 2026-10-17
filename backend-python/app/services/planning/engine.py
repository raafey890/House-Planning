"""
Deterministic Floor Planning Engine using Google OR-Tools CP-SAT.
Orchestrates area program, CP-SAT target-footprint formulation, architectural adjacencies,
multi-candidate generation, and architectural quality scoring.
"""
import time
import logging
from typing import Dict, Any, List, Optional
from ortools.sat.python import cp_model
from app.services.planning.area_program import build_area_program, AreaProgramError
from app.services.planning.adjacency import apply_architectural_rules
from app.services.planning.room_catalog import get_room_specs

logger = logging.getLogger("planning.engine")

class PlannerException(Exception):
    pass

def solve_candidate(
    program: Dict[str, Any],
    seed: int = 42,
    weight_variant: str = "balanced",
    timeout_sec: float = 3.0
) -> Optional[Dict[str, Any]]:
    """
    Formulates and solves a single CP-SAT candidate layout using target-footprint optimization.
    """
    plot_w = program["plot_width"]
    plot_l = program["plot_length"]
    facing = program["facing"]
    setbacks = program["setbacks"]
    build_w = program["buildable_width"]
    build_l = program["buildable_length"]
    floors_program = program["floors_program"]
    target_fp = program.get("target_footprint", {})

    target_w = int(round(target_fp.get("target_width", build_w * 0.75)))
    target_l = int(round(target_fp.get("target_length", build_l * 0.75)))

    # Offsets for global coordinates
    build_x_start = int(setbacks.get("left", 3))
    build_y_start = int(setbacks.get("front", 4))

    model = cp_model.CpModel()
    objective_terms = []

    rooms_vars_by_floor: Dict[int, List[Dict[str, Any]]] = {}
    x_intervals_by_floor: Dict[int, List[Any]] = {}
    y_intervals_by_floor: Dict[int, List[Any]] = {}

    for lvl, room_list in floors_program.items():
        rooms_vars_by_floor[lvl] = []
        x_intervals_by_floor[lvl] = []
        y_intervals_by_floor[lvl] = []

        for idx, r in enumerate(room_list):
            rtype = r["type"]
            specs = r["specs"]
            room_id = f"r_{lvl}_{idx}_{rtype}"

            min_w = specs["min_w"]
            max_w = min(specs.get("max_w", 20), build_w)
            min_h = specs["min_h"]
            max_h = min(specs.get("max_h", 22), build_l)
            pref_w = min(specs.get("pref_w", min_w), max_w)
            pref_h = min(specs.get("pref_h", min_h), max_h)

            if min_w > max_w:
                min_w = max_w
            if min_h > max_h:
                min_h = max_h

            x = model.NewIntVar(0, build_w - min_w, f"x_{room_id}")
            w = model.NewIntVar(min_w, max_w, f"w_{room_id}")
            x_end = model.NewIntVar(min_w, build_w, f"xe_{room_id}")
            model.Add(x_end == x + w)
            x_int = model.NewIntervalVar(x, w, x_end, f"xint_{room_id}")

            y = model.NewIntVar(0, build_l - min_h, f"y_{room_id}")
            h = model.NewIntVar(min_h, max_h, f"h_{room_id}")
            y_end = model.NewIntVar(min_h, build_l, f"ye_{room_id}")
            model.Add(y_end == y + h)
            y_int = model.NewIntervalVar(y, h, y_end, f"yint_{room_id}")

            # Room Area
            area = model.NewIntVar(min_w * min_h, build_w * build_l, f"area_{room_id}")
            model.AddMultiplicationEquality(area, [w, h])
            model.Add(area >= specs["min_area"])

            # Architectural aspect ratio: width/height within 2.2:1
            model.Add(w * 10 <= h * 22)
            model.Add(h * 10 <= w * 22)

            room_var = {
                "id": room_id,
                "type": rtype,
                "floor": lvl,
                "x": x, "y": y,
                "w": w, "h": h,
                "x_end": x_end, "y_end": y_end,
                "area": area,
                "specs": specs
            }
            rooms_vars_by_floor[lvl].append(room_var)
            x_intervals_by_floor[lvl].append(x_int)
            y_intervals_by_floor[lvl].append(y_int)

            # Penalize deviation from preferred dimensions
            w_diff = model.NewIntVar(-build_w, build_w, f"wdiff_{room_id}")
            model.Add(w_diff == w - pref_w)
            w_diff_abs = model.NewIntVar(0, build_w, f"wdiff_abs_{room_id}")
            model.AddAbsEquality(w_diff_abs, w_diff)

            h_diff = model.NewIntVar(-build_l, build_l, f"hdiff_{room_id}")
            model.Add(h_diff == h - pref_h)
            h_diff_abs = model.NewIntVar(0, build_l, f"hdiff_abs_{room_id}")
            model.AddAbsEquality(h_diff_abs, h_diff)

            dim_penalty_weight = 5 if weight_variant == "generous_living" and rtype in ["living_room", "dining_room"] else 7
            objective_terms.append(w_diff_abs * dim_penalty_weight)
            objective_terms.append(h_diff_abs * dim_penalty_weight)

            # Reward room area expansion up to preferred
            area_reward = 3 if weight_variant == "generous_living" and rtype in ["living_room", "dining_room"] else 2
            objective_terms.append(-area * area_reward)

    # 3. NoOverlap2D & Building Footprint Target per floor
    for lvl in x_intervals_by_floor:
        model.AddNoOverlap2D(x_intervals_by_floor[lvl], y_intervals_by_floor[lvl])

        all_x = [rv["x"] for rv in rooms_vars_by_floor[lvl]]
        all_xe = [rv["x_end"] for rv in rooms_vars_by_floor[lvl]]
        all_y = [rv["y"] for rv in rooms_vars_by_floor[lvl]]
        all_ye = [rv["y_end"] for rv in rooms_vars_by_floor[lvl]]

        env_min_x = model.NewIntVar(0, build_w, f"env_min_x_{lvl}")
        env_max_x = model.NewIntVar(0, build_w, f"env_max_x_{lvl}")
        env_min_y = model.NewIntVar(0, build_l, f"env_min_y_{lvl}")
        env_max_y = model.NewIntVar(0, build_l, f"env_max_y_{lvl}")

        model.AddMinEquality(env_min_x, all_x)
        model.AddMaxEquality(env_max_x, all_xe)
        model.AddMinEquality(env_min_y, all_y)
        model.AddMaxEquality(env_max_y, all_ye)

        env_w = model.NewIntVar(0, build_w, f"env_w_{lvl}")
        env_h = model.NewIntVar(0, build_l, f"env_h_{lvl}")
        model.Add(env_w == env_max_x - env_min_x)
        model.Add(env_h == env_max_y - env_min_y)

        # ── TARGET FOOTPRINT DEVIATION (Removes aggressive envelope minimization!) ──
        if lvl == 0:
            w_tgt_dev = model.NewIntVar(-build_w, build_w, f"w_tgt_dev_{lvl}")
            model.Add(w_tgt_dev == env_w - target_w)
            w_tgt_abs = model.NewIntVar(0, build_w, f"w_tgt_abs_{lvl}")
            model.AddAbsEquality(w_tgt_abs, w_tgt_dev)

            h_tgt_dev = model.NewIntVar(-build_l, build_l, f"h_tgt_dev_{lvl}")
            model.Add(h_tgt_dev == env_h - target_l)
            h_tgt_abs = model.NewIntVar(0, build_l, f"h_tgt_abs_{lvl}")
            model.AddAbsEquality(h_tgt_abs, h_tgt_dev)

            objective_terms.append(w_tgt_abs * 12)
            objective_terms.append(h_tgt_abs * 12)

            # Asymmetric penalty against undersized footprints (< 80% of target)
            under_w = model.NewIntVar(0, build_w, f"under_w_{lvl}")
            model.Add(under_w >= int(target_w * 0.82) - env_w)
            model.Add(under_w >= 0)
            under_h = model.NewIntVar(0, build_l, f"under_h_{lvl}")
            model.Add(under_h >= int(target_l * 0.82) - env_h)
            model.Add(under_h >= 0)
            objective_terms.append(under_w * 25)
            objective_terms.append(under_h * 25)

            # Balanced rear open space (leaves intentional 10-16 ft for private rear garden on South plots)
            if facing == "south" and build_l >= 40:
                rear_open = model.NewIntVar(0, build_l, "rear_open_s")
                model.Add(rear_open == env_min_y)
                ideal_rear = max(8, min(14, int(build_l * 0.18)))
                r_dev = model.NewIntVar(-build_l, build_l, "r_dev_s")
                model.Add(r_dev == rear_open - ideal_rear)
                r_dev_abs = model.NewIntVar(0, build_l, "r_dev_abs_s")
                model.AddAbsEquality(r_dev_abs, r_dev)
                objective_terms.append(r_dev_abs * 8)

        elif lvl > 0:
            # Upper floors: penalize envelope exceeding target footprint
            w_excess = model.NewIntVar(0, build_w, f"w_exc_{lvl}")
            model.Add(w_excess >= env_w - target_w)
            model.Add(w_excess >= 0)
            h_excess = model.NewIntVar(0, build_l, f"h_exc_{lvl}")
            model.Add(h_excess >= env_h - target_l)
            model.Add(h_excess >= 0)
            objective_terms.append(w_excess * 10)
            objective_terms.append(h_excess * 10)

    # 4. Multi-floor Staircase Alignment Constraint
    stair_vars = []
    for lvl, rvars in rooms_vars_by_floor.items():
        for rv in rvars:
            if rv["type"] == "staircase":
                stair_vars.append(rv)

    if len(stair_vars) >= 2:
        for i in range(len(stair_vars) - 1):
            s1 = stair_vars[i]
            s2 = stair_vars[i + 1]
            model.Add(s1["x"] == s2["x"])
            model.Add(s1["y"] == s2["y"])
            model.Add(s1["w"] == s2["w"])
            model.Add(s1["h"] == s2["h"])

    # 5. Architectural Adjacency & Contiguity Rules
    apply_architectural_rules(model, rooms_vars_by_floor, objective_terms)

    # 6. Orientation Preferences (Front Road vs Rear)
    for lvl, rvars in rooms_vars_by_floor.items():
        for rv in rvars:
            rtype = rv["type"]
            if rtype in ["parking", "garage"]:
                if facing == "south":
                    objective_terms.append((build_l - rv["y_end"]) * 22)
                    objective_terms.append((build_w - rv["x_end"]) * 10)
                elif facing == "north":
                    objective_terms.append(rv["y"] * 22)
                    objective_terms.append((build_w - rv["x_end"]) * 10)
                elif facing == "east":
                    objective_terms.append((build_w - rv["x_end"]) * 22)
                elif facing == "west":
                    objective_terms.append(rv["x"] * 22)

            elif rtype in ["foyer", "living_room"] and lvl == 0:
                if facing == "south":
                    objective_terms.append((build_l - rv["y_end"]) * 14)
                elif facing == "north":
                    objective_terms.append(rv["y"] * 14)
                elif facing == "east":
                    objective_terms.append((build_w - rv["x_end"]) * 14)
                elif facing == "west":
                    objective_terms.append(rv["x"] * 14)

    model.Minimize(sum(objective_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_sec
    solver.parameters.num_workers = 4
    solver.parameters.random_seed = seed

    t_solve_start = time.time()
    status = solver.Solve(model)
    solve_duration = time.time() - t_solve_start

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    # Extract Coordinates
    solved_floors: Dict[int, List[Dict[str, Any]]] = {}
    for lvl, rvars in rooms_vars_by_floor.items():
        solved_floors[lvl] = []
        for rv in rvars:
            vx = solver.Value(rv["x"]) + build_x_start
            vy = solver.Value(rv["y"]) + build_y_start
            vw = solver.Value(rv["w"])
            vh = solver.Value(rv["h"])
            varea = vw * vh

            solved_floors[lvl].append({
                "id": rv["id"],
                "type": rv["type"],
                "floor_level": lvl,
                "x": float(vx),
                "y": float(vy),
                "width": float(vw),
                "length": float(vh),
                "area": float(varea),
                "space_category": rv["specs"].get("privacy", "private")
            })

    return {
        "status": "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE",
        "solve_time": round(solve_duration, 2),
        "objective_value": solver.ObjectiveValue(),
        "seed": seed,
        "variant": weight_variant,
        "floors": solved_floors,
        "plot": {
            "width": float(plot_w),
            "length": float(plot_l),
            "facing": facing,
            "setbacks": setbacks,
            "buildable": {
                "x": float(build_x_start),
                "y": float(build_y_start),
                "w": float(build_w),
                "l": float(build_l)
            }
        },
        "target_footprint": target_fp
    }

def solve_layout(context: Dict[str, Any], requirements: List[Dict[str, Any]], use_gemini: bool = True) -> Dict[str, Any]:
    """
    Hybrid floor-planning engine.

    When use_gemini=True (default), tries the Gemini architectural planner first.
    On success, returns the Gemini-planned + deterministically-validated layout.
    On any Gemini failure, falls back to the multi-candidate deterministic solver.

    Returns a dict compatible with the post_processor pipeline.
    """
    t_start = time.time()

    # ── 0. Try Gemini hybrid planner first ─────────────────────────────────
    if use_gemini:
        try:
            from app.core.config import settings
            if settings.GEMINI_API_KEY:
                from app.services.planning.gemini_planner import plan_with_gemini, GeminiPlannerError
                logger.info("=== Attempting Gemini hybrid planner ===")

                layout_data = plan_with_gemini(context, requirements)

                # Gemini returned a LayoutData; wrap it in the engine result format
                # so the caller (floor_plans.py) can process it uniformly
                gemini_result = {
                    "status": "GEMINI_HYBRID",
                    "layout_data": layout_data,
                    "planner_source": "gemini_hybrid",
                    "solve_time": round(time.time() - t_start, 2),
                    "total_time": round(time.time() - t_start, 2),
                }
                logger.info("Gemini hybrid planner succeeded in %.2fs", gemini_result["solve_time"])
                return gemini_result
            else:
                logger.info("GEMINI_API_KEY not set — skipping Gemini planner")
        except Exception as e:
            logger.warning("Gemini hybrid planner failed, falling back to deterministic: %s: %s",
                           type(e).__name__, e)

    # ── 1. Deterministic fallback ──────────────────────────────────────────
    logger.info("=== Using deterministic OR-Tools planner ===")

    # 1. Run Area Program and compute target footprint
    try:
        program = build_area_program(context, requirements)
    except AreaProgramError as ape:
        raise PlannerException(str(ape))

    # Candidate variants to explore
    CANDIDATES = [
        {"seed": 42,  "variant": "balanced"},
        {"seed": 101, "variant": "generous_living"},
        {"seed": 202, "variant": "balanced"},
        {"seed": 303, "variant": "balanced"},
        {"seed": 404, "variant": "generous_living"},
    ]

    from app.services.planning.post_processor import post_process_layout
    from app.validators.geometry_validator import GeometryValidator
    from app.services.planning.quality_scorer import compute_architectural_quality_score

    best_candidate_res = None
    best_score = -1.0
    valid_candidates_count = 0

    for cand_cfg in CANDIDATES:
        try:
            cand_res = solve_candidate(
                program=program,
                seed=cand_cfg["seed"],
                weight_variant=cand_cfg["variant"],
                timeout_sec=2.5
            )
            if not cand_res:
                continue

            # Evaluate candidate with post_processor and validators
            temp_layout = post_process_layout(cand_res)
            passed, _val_res = GeometryValidator.validate_layout(temp_layout)

            q_eval = compute_architectural_quality_score(temp_layout, program.get("target_footprint"))
            cand_score = q_eval["total_score"]

            if passed:
                valid_candidates_count += 1
                cand_score += 10.0  # Bonus for passing all hard validators

            if cand_score > best_score:
                best_score = cand_score
                cand_res["quality_score"] = q_eval
                cand_res["geometry_valid"] = passed
                best_candidate_res = cand_res

        except Exception as e:
            logger.debug(f"Candidate {cand_cfg['seed']} failed: {e}")
            continue

    if not best_candidate_res:
        raise PlannerException(
            "The selected requirements cannot be arranged within this plot using current architectural constraints. "
            "Suggestions: Reduce room counts, decrease parking requirements, or expand plot dimensions."
        )

    best_candidate_res["total_time"] = round(time.time() - t_start, 2)
    best_candidate_res["candidates_evaluated"] = len(CANDIDATES)
    best_candidate_res["valid_candidates"] = valid_candidates_count
    best_candidate_res["planner_source"] = "deterministic_fallback"

    return best_candidate_res
