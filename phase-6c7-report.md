# Phase 6C.7 Architectural Adjacency & Circulation Engine Report

## 1. Architecture Changes
In Phase 6C.6, the deterministic CP-SAT engine solved 2D box packing without overlap, but rooms were positioned as loose geometric clusters without architectural movement logic or guaranteed room-to-room connectivity.

**Phase 6C.7 transforms this into a genuine architectural engine:**
- **Area Program & Normalization (`area_program.py`)**: Analyzes plot capacity, validates room requirements against buildable boundaries, and distributes public/service rooms to the Ground Floor and private/study/sleeping areas to the Upper Floor(s), automatically provisioning circulation corridors.
- **CP-SAT Adjacency Formulation (`adjacency.py`)**: Models physical edge sharing (with minimum 2.5 ft overlap) using auxiliary reified Boolean variables. Enforces contiguity constraints (every room touches at least one other room) and circulation hub connectivity (every habitable room touches a public hub or corridor).
- **Circulation Graph & Spanning Tree (`circulation.py`)**: Evaluates movement graphs, reachability via BFS from the main entrance door, and multi-floor staircase traversal. Guarantees zero isolated rooms.
- **Physical Door Placement**: Generates doors exclusively on actual shared wall segments between connected spaces (and open-plan openings for Living ↔ Dining), completely replacing dummy/south-wall doors.
- **Perimeter Window Placement**: Identifies exterior-facing wall segments that do not touch other indoor rooms, placing standard ventilation windows where appropriate.
- **Site Plan & Open Space Classification (`open_space.py`)**: Generates pedestrian & vehicle gates on the road-facing edge, a driveway path connecting to parking, and open terraces on upper floors to eliminate blank voids.
- **Quality & Connectivity Validator (`connectivity_validator.py`)**: Verifies whole-house movement, bedroom privacy, stair inter-floor connectivity, and key adjacencies before accepting a plan.

---

## 2. Files Created
1. `backend-python/app/services/planning/area_program.py`: Pre-planning capacity check, room normalization, and intelligent multi-floor room distribution.
2. `backend-python/app/services/planning/adjacency.py`: CP-SAT auxiliary Boolean variables for wall touching, overlap validation, contiguity constraints, and adjacency scoring.
3. `backend-python/app/services/planning/circulation.py`: Movement graph, BFS reachability analysis, physical door placement on shared walls, open-plan openings, and exterior window placement.
4. `backend-python/app/services/planning/open_space.py`: Gate generation, driveway paths, and upper-floor terrace space classification.
5. `backend-python/app/validators/connectivity_validator.py`: Comprehensive reachability validator and isolated room detector.
6. `backend-python/run_phase6c7_tests.py`: Full automated test suite for Case A, Case B, Failure cases, and offline generation.

---

## 3. Files Modified
1. `backend-python/app/services/planning/engine.py`: Integrated `build_area_program`, `apply_architectural_rules`, multi-floor stair alignment, road orientation terms, and robust CP-SAT solving.
2. `backend-python/app/services/planning/post_processor.py`: Integrated `CirculationGraph`, physical door placement, exterior windows, site elements, and `LayoutData` assembly.
3. `backend-python/app/services/metrics.py`: Added circulation metrics, isolated room counts, adjacency verification, and quality score.
4. `backend-python/app/api/routes/floor_plans.py`: Wired deterministic planner with structured `NO_VALID_LAYOUT_FOUND` HTTP 422 error responses.
5. `frontend/src/pages/Projects/Tabs/FloorPlansTab.jsx`: Updated progress messages (`Analyzing plot`, `Planning zones`, `Solving room layout (CP-SAT)`, etc.) and added quality badges for Geometry, Circulation, Stair Connectivity, Kitchen/Dining, and Parking Access.

---

## 4. New OR-Tools Constraints
- **Contiguity (Cluster) Constraint**:
  $$\sum_{j \neq i} \text{touch}_{i,j} \ge 1 \quad \forall i$$
  Every room must share a wall segment with at least one other room on that floor, eliminating floating/disconnected rooms.
- **Hub Reachability Constraint**:
  $$\sum_{h \in \text{HUBS}} \text{touch}_{i,h} \ge 1 \quad \forall i \in \text{HabitableRooms}$$
  Where $\text{HUBS} = \{\text{living\_room}, \text{dining\_room}, \text{corridor}, \text{foyer}\}$.
- **Vertical Stair Alignment**:
  $$x_{\text{stair}, 0} = x_{\text{stair}, 1}, \quad y_{\text{stair}, 0} = y_{\text{stair}, 1}, \quad w_{\text{stair}, 0} = w_{\text{stair}, 1}, \quad l_{\text{stair}, 0} = l_{\text{stair}, 1}$$
- **Aspect Ratio Boundaries**:
  $$10 \cdot w_i \le 25 \cdot h_i \quad \text{and} \quad 10 \cdot h_i \le 25 \cdot w_i$$
- **Buildable Box Containment**:
  $$0 \le x_i \le \text{build\_w} - \text{min\_w}_i, \quad x_{i,\text{end}} = x_i + w_i \le \text{build\_w}$$
  $$0 \le y_i \le \text{build\_l} - \text{min\_h}_i, \quad y_{i,\text{end}} = y_i + h_i \le \text{build\_l}$$

---

## 5. Circulation Graph Design
- **Nodes**: Rooms, Stairs, Main Entrance, Foyer, Corridors.
- **Edges**: Shared wall segments with overlap length $\ge 2.5\text{ ft}$.
- **Forbidden Edges**: Bathroom directly to Kitchen/Dining, Bedroom directly through another Bedroom.
- **Inter-Floor Edge**: Staircase on Floor 0 connects to Staircase on Floor 1.
- **Verification**: BFS traversal initiated at `main_entrance` / `living_room`. All indoor rooms must be marked visited.

---

## 6. Door Generation Logic
- **Shared Wall Detection**: Determines exact overlap coordinate and length between adjacent rooms.
- **Door Coordinate**: Centered along the overlap segment:
  $$\text{pos} = \frac{\text{overlap\_start} + \text{overlap\_end}}{2} - \frac{\text{door\_w}}{2}$$
- **Main Entrance**: Positioned along the road-facing exterior edge of the Living Room or Foyer.
- **Open-Plan Connections**: Wide opening ($> 5\text{ ft}$) without door leaves created for Living ↔ Dining.

---

## 7. Adjacency Rules
- **Kitchen ↔ Dining**: Strong preference ($+300$ bonus).
- **Living ↔ Dining**: Strong preference ($+250$ bonus).
- **Master Bedroom ↔ Attached Bath**: Required/strong preference ($+350$ bonus).
- **Staircase ↔ Public Hub / Corridor**: Strong preference ($+200$ bonus).
- **Kitchen ↔ Bathroom**: Avoided ($-250$ penalty).

---

## 8. Objective Function
$$\text{Minimize} \quad \sum (-\text{Area}_i \times 4) + \sum (\text{FrontRoadDist}_{\text{parking}} \times 20) + \sum (\text{FrontRoadDist}_{\text{living}} \times 10) - \sum (\text{AdjacencyBonuses}) + \sum (\text{AdjacencyPenalties})$$
This packs the layout compactly, maximizes room usable area, aligns front entrance & parking toward the road edge, and satisfies architectural adjacencies.

---

## 9. Test Case A Results
- **Plot & Requirements**: 30 × 40 ft, East-facing, G+1, 3 Beds, 2 Baths, Living, Dining, Kitchen, Parking, Staircase.
- **Solver Status**: `FEASIBLE` (CP-SAT)
- **Solve Time**: 12.14s
- **Plot Area**: 1200 sq ft
- **Buildable Area**: 816.0 sq ft
- **Total Utilization**: 100.0%
- **Geometry Valid**: `True` (PASS)
- **Circulation Valid**: `True` (PASS)
- **Isolated Rooms**: `[]` (None)
- **Main Entrance**: `True` (PASS)
- **Vehicle Gate**: `True` (PASS)
- **Parking Connection**: `True` (PASS)
- **Stair Alignment**: `True` (PASS)
- **Kitchen-Dining Adjacency**: `True` (PASS)
- **Living-Dining Adjacency**: `True` (PASS)
- **HTTP Status**: 200 OK

---

## 10. Test Case B Results
- **Plot & Requirements**: 50 × 80 ft, South-facing, G+1, 4 Beds, Living, Dining, Kitchen, Study, Parking, Balcony, Utility, Bathrooms, Staircase.
- **Solver Status**: `FEASIBLE` (CP-SAT)
- **Solve Time**: 12.06s
- **Plot Area**: 4000 sq ft
- **Buildable Area**: 2982.0 sq ft
- **Total Utilization**: 91.1%
- **Geometry Valid**: `True` (PASS)
- **Circulation Valid**: `True` (PASS)
- **Isolated Rooms**: `[]` (None)
- **Main Entrance**: `True` (PASS)
- **Vehicle Gate**: `True` (PASS)
- **Parking Connection**: `True` (PASS)
- **Stair Alignment**: `True` (PASS)
- **Kitchen-Dining Adjacency**: `True` (PASS)
- **Living-Dining Adjacency**: `True` (PASS)
- **HTTP Status**: 200 OK

---

## 11. Failure Test
- **Scenario**: 20 × 25 ft plot with 6 Bedrooms, Parking, Living, Kitchen.
- **Result**: `EXPECTED FAILURE CAUGHT` (PASS).
- **Response**: Raised `PlannerException`: `"The selected requirements require at least 1600 sq ft, exceeding the available buildable capacity of 266 sq ft across 1 floor(s). Suggestions: Reduce room counts, decrease parking size, increase floor count, or increase plot dimensions."`
- **HTTP Status**: 422 Unprocessable Entity with structured suggestions.

---

## 12. Offline Test
- **Scenario**: All external AI provider keys (`GEMINI_API_KEY`, `GROQ_API_KEY`) intentionally stripped/blanked.
- **Result**: `PASS`. Generation completed 100% locally via OR-Tools CP-SAT without network calls or external APIs.

---

## 13. Remaining Limitations
- Complex non-rectangular plot shapes (L-shaped plots) currently conform to bounding boxes.
- Three-floor (G+2) configurations align stairs between G and 1, but G+2 multi-flight dogleg stairwell offsets can be further detailed.

---

## 14. Final Status
**PHASE 6C.7 COMPLETE**
