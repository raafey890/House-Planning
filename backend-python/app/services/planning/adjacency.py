"""
Architectural Adjacency Rules and CP-SAT Formulation.
Encodes required, preferred, and cluster adjacency constraints for the solver.
"""
from typing import Dict, Any, List

def add_touch_constraint(model, r1, r2, overlap_min=2.5):
    """
    Creates a boolean variable representing if r1 and r2 share a contiguous edge segment >= overlap_min.
    """
    MAX_DIM = 200
    
    # Horizontal touch: r1 right of r2 (r1.x == r2.x_end) OR r2 right of r1 (r2.x == r1.x_end)
    r1_right_r2 = model.NewBoolVar(f"r1_r_r2_{r1['id']}_{r2['id']}")
    model.Add(r1['x'] == r2['x_end']).OnlyEnforceIf(r1_right_r2)
    model.Add(r1['x'] != r2['x_end']).OnlyEnforceIf(r1_right_r2.Not())

    r2_right_r1 = model.NewBoolVar(f"r2_r_r1_{r1['id']}_{r2['id']}")
    model.Add(r2['x'] == r1['x_end']).OnlyEnforceIf(r2_right_r1)
    model.Add(r2['x'] != r1['x_end']).OnlyEnforceIf(r2_right_r1.Not())

    h_touch = model.NewBoolVar(f"ht_{r1['id']}_{r2['id']}")
    model.AddBoolOr([r1_right_r2, r2_right_r1]).OnlyEnforceIf(h_touch)
    model.AddBoolAnd([r1_right_r2.Not(), r2_right_r1.Not()]).OnlyEnforceIf(h_touch.Not())

    # Y overlap
    y_min_end = model.NewIntVar(0, MAX_DIM, f"yme_{r1['id']}_{r2['id']}")
    model.AddMinEquality(y_min_end, [r1['y_end'], r2['y_end']])

    y_max_start = model.NewIntVar(0, MAX_DIM, f"yms_{r1['id']}_{r2['id']}")
    model.AddMaxEquality(y_max_start, [r1['y'], r2['y']])

    y_overlap = model.NewIntVar(-MAX_DIM, MAX_DIM, f"yo_{r1['id']}_{r2['id']}")
    model.Add(y_overlap == y_min_end - y_max_start)

    h_overlap_valid = model.NewBoolVar(f"hov_{r1['id']}_{r2['id']}")
    model.Add(y_overlap >= int(overlap_min)).OnlyEnforceIf(h_overlap_valid)
    model.Add(y_overlap < int(overlap_min)).OnlyEnforceIf(h_overlap_valid.Not())

    h_adj = model.NewBoolVar(f"hadj_{r1['id']}_{r2['id']}")
    model.AddBoolAnd([h_touch, h_overlap_valid]).OnlyEnforceIf(h_adj)
    model.AddBoolOr([h_touch.Not(), h_overlap_valid.Not()]).OnlyEnforceIf(h_adj.Not())

    # Vertical touch: r1 below r2 (r1.y == r2.y_end) OR r2 below r1 (r2.y == r1.y_end)
    r1_below_r2 = model.NewBoolVar(f"r1_b_r2_{r1['id']}_{r2['id']}")
    model.Add(r1['y'] == r2['y_end']).OnlyEnforceIf(r1_below_r2)
    model.Add(r1['y'] != r2['y_end']).OnlyEnforceIf(r1_below_r2.Not())

    r2_below_r1 = model.NewBoolVar(f"r2_b_r1_{r1['id']}_{r2['id']}")
    model.Add(r2['y'] == r1['y_end']).OnlyEnforceIf(r2_below_r1)
    model.Add(r2['y'] != r1['y_end']).OnlyEnforceIf(r2_below_r1.Not())

    v_touch = model.NewBoolVar(f"vt_{r1['id']}_{r2['id']}")
    model.AddBoolOr([r1_below_r2, r2_below_r1]).OnlyEnforceIf(v_touch)
    model.AddBoolAnd([r1_below_r2.Not(), r2_below_r1.Not()]).OnlyEnforceIf(v_touch.Not())

    # X overlap
    x_min_end = model.NewIntVar(0, MAX_DIM, f"xme_{r1['id']}_{r2['id']}")
    model.AddMinEquality(x_min_end, [r1['x_end'], r2['x_end']])

    x_max_start = model.NewIntVar(0, MAX_DIM, f"xms_{r1['id']}_{r2['id']}")
    model.AddMaxEquality(x_max_start, [r1['x'], r2['x']])

    x_overlap = model.NewIntVar(-MAX_DIM, MAX_DIM, f"xo_{r1['id']}_{r2['id']}")
    model.Add(x_overlap == x_min_end - x_max_start)

    v_overlap_valid = model.NewBoolVar(f"vov_{r1['id']}_{r2['id']}")
    model.Add(x_overlap >= int(overlap_min)).OnlyEnforceIf(v_overlap_valid)
    model.Add(x_overlap < int(overlap_min)).OnlyEnforceIf(v_overlap_valid.Not())

    v_adj = model.NewBoolVar(f"vadj_{r1['id']}_{r2['id']}")
    model.AddBoolAnd([v_touch, v_overlap_valid]).OnlyEnforceIf(v_adj)
    model.AddBoolOr([v_touch.Not(), v_overlap_valid.Not()]).OnlyEnforceIf(v_adj.Not())

    # Overall adjacency
    adj = model.NewBoolVar(f"adj_{r1['id']}_{r2['id']}")
    model.AddBoolOr([h_adj, v_adj]).OnlyEnforceIf(adj)
    model.AddBoolAnd([h_adj.Not(), v_adj.Not()]).OnlyEnforceIf(adj.Not())

    return adj

HUBS = {"living_room", "dining_room", "corridor", "foyer", "hallway"}

def apply_architectural_rules(model, rooms_by_floor: Dict[int, List[Dict[str, Any]]], objective_terms: List[Any]):
    """
    Applies architectural adjacency preferences, contiguity guarantees, and clustering.
    """
    for lvl, rooms in rooms_by_floor.items():
        n = len(rooms)
        if n <= 1:
            continue

        adj_matrix = {}
        for i in range(n):
            for j in range(i + 1, n):
                r1 = rooms[i]
                r2 = rooms[j]
                adj_var = add_touch_constraint(model, r1, r2, overlap_min=2.5)
                adj_matrix[(i, j)] = adj_var
                adj_matrix[(j, i)] = adj_var

        # ── 1. CONTIGUITY: Every room must touch at least one other room ──
        for i in range(n):
            touching_neighbors = [adj_matrix[(i, j)] for j in range(n) if j != i]
            model.AddBoolOr(touching_neighbors)

        # ── 2. CIRCULATION REACHABILITY: Habitable rooms must touch a circulation hub ──
        hub_indices = [j for j in range(n) if rooms[j]["type"] in HUBS]
        if hub_indices:
            for i in range(n):
                rtype = rooms[i]["type"]
                if rtype in HUBS or rtype in ["parking", "garage", "terrace", "balcony"]:
                    continue

                if rtype == "staircase":
                    # Staircase MUST touch at least one hub
                    touching_hubs = [adj_matrix[(i, j)] for j in hub_indices if j != i]
                    if touching_hubs:
                        model.AddBoolOr(touching_hubs)

                elif "bedroom" in rtype or rtype == "study_room":
                    # Bedrooms & study must touch at least one hub
                    touching_hubs = [adj_matrix[(i, j)] for j in hub_indices if j != i]
                    if touching_hubs:
                        model.AddBoolOr(touching_hubs)

                elif "bath" in rtype or "toilet" in rtype:
                    # Bathrooms can touch a hub OR a bedroom (for attached bath)
                    targets = [j for j in range(n) if j != i and (rooms[j]["type"] in HUBS or "bedroom" in rooms[j]["type"])]
                    if targets:
                        model.AddBoolOr([adj_matrix[(i, j)] for j in targets])

                elif rtype == "utility_room":
                    # Utility can touch kitchen or a hub
                    targets = [j for j in range(n) if j != i and (rooms[j]["type"] in HUBS or rooms[j]["type"] == "kitchen")]
                    if targets:
                        model.AddBoolOr([adj_matrix[(i, j)] for j in targets])

        # ── 3. ARCHITECTURAL PREFERENCES (SCORING) ──
        for i in range(n):
            for j in range(i + 1, n):
                r1 = rooms[i]
                r2 = rooms[j]
                t1, t2 = r1["type"], r2["type"]
                adj_var = adj_matrix[(i, j)]

                # Kitchen <-> Dining (Strong bonus)
                if (t1 == "kitchen" and t2 == "dining_room") or (t1 == "dining_room" and t2 == "kitchen"):
                    objective_terms.append(-adj_var * 300)

                # Living <-> Dining (Strong bonus)
                elif (t1 == "living_room" and t2 == "dining_room") or (t1 == "dining_room" and t2 == "living_room"):
                    objective_terms.append(-adj_var * 250)

                # Master Bedroom <-> Bath (Strong bonus)
                elif (t1 == "master_bedroom" and "bath" in t2) or (t2 == "master_bedroom" and "bath" in t1):
                    objective_terms.append(-adj_var * 350)

                # Staircase <-> Hub
                elif (t1 == "staircase" and t2 in HUBS) or (t2 == "staircase" and t1 in HUBS):
                    objective_terms.append(-adj_var * 200)

                # Avoid Kitchen <-> Bathroom
                elif (t1 == "kitchen" and "bath" in t2) or (t2 == "kitchen" and "bath" in t1):
                    objective_terms.append(adj_var * 250)
