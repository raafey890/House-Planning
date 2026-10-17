import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from app.services.planning.area_program import build_area_program
from app.services.planning.adjacency import apply_architectural_rules
from ortools.sat.python import cp_model

context_50x80 = {
    "plot_width": 50,
    "plot_length": 80,
    "facing": "south",
    "floors": 2,
    "number_of_floors": 2,
    "design_style": "modern",
    "setbacks": {"front": 4, "rear": 4, "left": 3, "right": 3},
    "parking_spaces": 1
}

requirements = [{
    "bedrooms": 3,
    "bathrooms": 3,
    "kitchens": 1,
    "living_rooms": 1,
    "dining_rooms": 1,
    "parking_spaces": 1,
    "balconies": 1,
    "pooja_room": True,
    "study_room": True,
}]

prog = build_area_program(context_50x80, requirements)
plot_w = prog["plot_width"]
plot_l = prog["plot_length"]
build_w = prog["buildable_width"]
build_l = prog["buildable_length"]
target_fp = prog["target_footprint"]
target_w = int(target_fp["target_width"])
target_l = min(int(target_fp["target_length"]), build_l - 18)  # Leave 18 ft for front + rear yards
print(f"Target footprint: {target_w} x {target_l} ({target_w * target_l} sq ft)")

model = cp_model.CpModel()
objective_terms = []

rooms_vars_by_floor = {}
x_intervals = {}
y_intervals = {}

for lvl, room_list in prog["floors_program"].items():
    rooms_vars_by_floor[lvl] = []
    x_intervals[lvl] = []
    y_intervals[lvl] = []
    for idx, r in enumerate(room_list):
        rtype = r["type"]
        specs = r["specs"]
        rid = f"r_{lvl}_{idx}_{rtype}"
        min_w = specs["min_w"]
        max_w = min(specs["max_w"], build_w)
        min_h = specs["min_h"]
        max_h = min(specs["max_h"], build_l)
        pref_w = min(specs["pref_w"], max_w)
        pref_h = min(specs["pref_h"], max_h)

        x = model.NewIntVar(0, build_w - min_w, f"x_{rid}")
        w = model.NewIntVar(min_w, max_w, f"w_{rid}")
        xe = model.NewIntVar(min_w, build_w, f"xe_{rid}")
        model.Add(xe == x + w)
        x_int = model.NewIntervalVar(x, w, xe, f"xi_{rid}")

        y = model.NewIntVar(0, build_l - min_h, f"y_{rid}")
        h = model.NewIntVar(min_h, max_h, f"h_{rid}")
        ye = model.NewIntVar(min_h, build_l, f"ye_{rid}")
        model.Add(ye == y + h)
        y_int = model.NewIntervalVar(y, h, ye, f"yi_{rid}")

        area = model.NewIntVar(min_w * min_h, build_w * build_l, f"area_{rid}")
        model.AddMultiplicationEquality(area, [w, h])
        model.Add(area >= specs["min_area"])

        # Aspect ratio constraint <= 2.2
        model.Add(w * 10 <= h * 22)
        model.Add(h * 10 <= w * 22)

        rooms_vars_by_floor[lvl].append({
            "id": rid, "type": rtype, "floor": lvl,
            "x": x, "y": y, "w": w, "h": h,
            "x_end": xe, "y_end": ye, "area": area,
            "specs": specs
        })
        x_intervals[lvl].append(x_int)
        y_intervals[lvl].append(y_int)

        # Deviation from preferred dimensions
        wd = model.NewIntVar(-build_w, build_w, f"wd_{rid}")
        model.Add(wd == w - pref_w)
        wda = model.NewIntVar(0, build_w, f"wda_{rid}")
        model.AddAbsEquality(wda, wd)

        hd = model.NewIntVar(-build_l, build_l, f"hd_{rid}")
        model.Add(hd == h - pref_h)
        hda = model.NewIntVar(0, build_l, f"hda_{rid}")
        model.AddAbsEquality(hda, hd)

        objective_terms.append(wda * 6)
        objective_terms.append(hda * 6)
        # Reward area up to preferred
        objective_terms.append(-area * 2)

# Non-overlap & envelope per floor
for lvl in x_intervals:
    model.AddNoOverlap2D(x_intervals[lvl], y_intervals[lvl])
    
    indoor_x = [rv["x"] for rv in rooms_vars_by_floor[lvl]]
    indoor_xe = [rv["x_end"] for rv in rooms_vars_by_floor[lvl]]
    indoor_y = [rv["y"] for rv in rooms_vars_by_floor[lvl]]
    indoor_ye = [rv["y_end"] for rv in rooms_vars_by_floor[lvl]]

    env_min_x = model.NewIntVar(0, build_w, f"emx_{lvl}")
    env_max_x = model.NewIntVar(0, build_w, f"eMx_{lvl}")
    env_min_y = model.NewIntVar(0, build_l, f"emy_{lvl}")
    env_max_y = model.NewIntVar(0, build_l, f"eMy_{lvl}")

    model.AddMinEquality(env_min_x, indoor_x)
    model.AddMaxEquality(env_max_x, indoor_xe)
    model.AddMinEquality(env_min_y, indoor_y)
    model.AddMaxEquality(env_max_y, indoor_ye)

    env_w = model.NewIntVar(0, build_w, f"ew_{lvl}")
    env_h = model.NewIntVar(0, build_l, f"eh_{lvl}")
    model.Add(env_w == env_max_x - env_min_x)
    model.Add(env_h == env_max_y - env_min_y)

    if lvl == 0:
        # TARGET DEVIATION PENALTY (not minimization!)
        w_tgt_dev = model.NewIntVar(-build_w, build_w, f"wtd_{lvl}")
        model.Add(w_tgt_dev == env_w - target_w)
        w_tgt_abs = model.NewIntVar(0, build_w, f"wta_{lvl}")
        model.AddAbsEquality(w_tgt_abs, w_tgt_dev)

        h_tgt_dev = model.NewIntVar(-build_l, build_l, f"htd_{lvl}")
        model.Add(h_tgt_dev == env_h - target_l)
        h_tgt_abs = model.NewIntVar(0, build_l, f"hta_{lvl}")
        model.AddAbsEquality(h_tgt_abs, h_tgt_dev)

        objective_terms.append(w_tgt_abs * 12)
        objective_terms.append(h_tgt_abs * 12)

        # Severe penalty if footprint is crushed < 80% of target
        under_w = model.NewIntVar(0, build_w, f"uw_{lvl}")
        model.Add(under_w >= int(target_w * 0.85) - env_w)
        model.Add(under_w >= 0)
        under_h = model.NewIntVar(0, build_l, f"uh_{lvl}")
        model.Add(under_h >= int(target_l * 0.85) - env_h)
        model.Add(under_h >= 0)
        objective_terms.append(under_w * 25)
        objective_terms.append(under_h * 25)

        # Position house: South facing means front is near y = build_l
        # Leave 10-14 ft for front garden/driveway (y_end ~ build_l - 2 to build_l - 12)
        # Leave 8-12 ft for rear yard (y_start ~ 8 to 14)
        rear_open = model.NewIntVar(0, build_l, "rear_open")
        model.Add(rear_open == env_min_y)
        # Ideal rear open space around 8-12 ft
        rear_dev = model.NewIntVar(-build_l, build_l, "rdev")
        model.Add(rear_dev == rear_open - 10)
        rear_dev_abs = model.NewIntVar(0, build_l, "rdeva")
        model.AddAbsEquality(rear_dev_abs, rear_dev)
        objective_terms.append(rear_dev_abs * 8)

# Staircase alignment
stair_vars = []
for lvl, rvars in rooms_vars_by_floor.items():
    for rv in rvars:
        if rv["type"] == "staircase":
            stair_vars.append(rv)
if len(stair_vars) >= 2:
    for i in range(len(stair_vars) - 1):
        s1, s2 = stair_vars[i], stair_vars[i+1]
        model.Add(s1["x"] == s2["x"])
        model.Add(s1["y"] == s2["y"])
        model.Add(s1["w"] == s2["w"])
        model.Add(s1["h"] == s2["h"])

# Adjacency
apply_architectural_rules(model, rooms_vars_by_floor, objective_terms)

# Orientation for South facing
for lvl, rvars in rooms_vars_by_floor.items():
    for rv in rvars:
        rtype = rv["type"]
        if rtype in ["parking", "garage"]:
            # Place parking along front edge (near build_l) and towards right side
            objective_terms.append((build_l - rv["y_end"]) * 20)
            objective_terms.append((build_w - rv["x_end"]) * 10)
        elif rtype in ["foyer", "living_room"] and lvl == 0:
            objective_terms.append((build_l - rv["y_end"]) * 12)

model.Minimize(sum(objective_terms))

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 4.0
solver.parameters.num_workers = 4
solver.parameters.random_seed = 42

t0 = time.time()
status = solver.Solve(model)
t1 = time.time()

print(f"Status: {solver.StatusName(status)} in {t1 - t0:.2f}s")
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    for lvl in sorted(rooms_vars_by_floor.keys()):
        rvars = rooms_vars_by_floor[lvl]
        min_x = min(solver.Value(r["x"]) for r in rvars)
        max_x = max(solver.Value(r["x_end"]) for r in rvars)
        min_y = min(solver.Value(r["y"]) for r in rvars)
        max_y = max(solver.Value(r["y_end"]) for r in rvars)
        w_env = max_x - min_x
        l_env = max_y - min_y
        tot_area = sum(solver.Value(r["area"]) for r in rvars)
        print(f"\nFloor {lvl} Envelope: x=[{min_x}, {max_x}] (w={w_env}), y=[{min_y}, {max_y}] (l={l_env}), Envelope Area={w_env * l_env}, Total Room Area={tot_area}, Util={tot_area/(w_env*l_env)*100:.1f}%")
        for r in rvars:
            vx, vy = solver.Value(r["x"]), solver.Value(r["y"])
            vw, vh = solver.Value(r["w"]), solver.Value(r["h"])
            print(f"  {r['type']:18s} x={vx:4.1f} y={vy:4.1f} w={vw:4.1f} h={vh:4.1f} area={vw*vh:5.1f}")
