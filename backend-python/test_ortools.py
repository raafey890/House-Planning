import sys
from ortools.sat.python import cp_model

def test_solver():
    model = cp_model.CpModel()
    
    W, L = 30, 40
    
    rooms = [
        {"name": "living", "min_area": 150, "min_side": 10},
        {"name": "kitchen", "min_area": 80, "min_side": 8},
        {"name": "bed1", "min_area": 120, "min_side": 10},
        {"name": "bath1", "min_area": 40, "min_side": 5}
    ]
    
    x_intervals = []
    y_intervals = []
    
    vars_dict = {}
    
    for i, r in enumerate(rooms):
        name = r["name"]
        min_s = r["min_side"]
        max_s = min(W, L)
        
        # Dimensions
        x = model.NewIntVar(0, W - min_s, f"x_{name}")
        w = model.NewIntVar(min_s, max_s, f"w_{name}")
        x_end = model.NewIntVar(min_s, W, f"x_end_{name}")
        
        y = model.NewIntVar(0, L - min_s, f"y_{name}")
        h = model.NewIntVar(min_s, max_s, f"h_{name}")
        y_end = model.NewIntVar(min_s, L, f"y_end_{name}")
        
        model.Add(x_end == x + w)
        model.Add(y_end == y + h)
        
        # Area approximation: w * h >= min_area
        # CP-SAT allows multiplication of two variables
        area = model.NewIntVar(0, W*L, f"area_{name}")
        model.AddMultiplicationEquality(area, [w, h])
        model.Add(area >= r["min_area"])
        
        # Intervals
        x_int = model.NewIntervalVar(x, w, x_end, f"x_int_{name}")
        y_int = model.NewIntervalVar(y, h, y_end, f"y_int_{name}")
        
        x_intervals.append(x_int)
        y_intervals.append(y_int)
        
        vars_dict[name] = {"x": x, "y": y, "w": w, "h": h}
        
    model.AddNoOverlap2D(x_intervals, y_intervals)
    
    # Try to pack them tightly towards (0,0) as an objective
    objective = []
    for v in vars_dict.values():
        objective.append(v["x"] + v["y"])
        
    model.Minimize(sum(objective))
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("Success!")
        for name, v in vars_dict.items():
            vx, vy, vw, vh = solver.Value(v["x"]), solver.Value(v["y"]), solver.Value(v["w"]), solver.Value(v["h"])
            print(f"{name}: x={vx}, y={vy}, w={vw}, h={vh}, area={vw*vh}")
    else:
        print("Failed to find a solution.")

if __name__ == "__main__":
    test_solver()
