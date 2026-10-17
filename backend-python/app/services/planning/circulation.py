"""
Circulation graph, reachability validation, and opening (door/window) generator.
Ensures that all rooms form a functional architectural movement network.
"""
from typing import Dict, Any, List, Tuple, Set, Optional
from collections import deque
from app.models.layout import Room, Door, Window, Stair, Point2D, Wall

# Invalid direct connections according to architectural best practices
FORBIDDEN_CONNECTIONS = {
    ("bathroom", "kitchen"),
    ("kitchen", "bathroom"),
    ("toilet", "kitchen"),
    ("kitchen", "toilet"),
    ("bathroom", "dining_room"),
    ("dining_room", "bathroom"),
    ("toilet", "dining_room"),
    ("dining_room", "toilet"),
    ("main_entrance", "bathroom"),
    ("main_entrance", "toilet"),
    ("main_entrance", "utility_room"),
    ("parking", "bedroom"),
    ("bedroom", "parking"),
    ("bedroom", "kitchen"),
    ("kitchen", "bedroom"),
}

def find_shared_wall_segment(r1: Dict[str, Any], r2: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Checks if room r1 and r2 share a contiguous wall segment.
    Returns the overlap details (orientation: 'H' or 'V', coordinate, start, end, length) or None.
    """
    x1, y1, w1, l1 = r1["x"], r1["y"], r1["width"], r1["length"]
    x2, y2, w2, l2 = r2["x"], r2["y"], r2["width"], r2["length"]

    x1_end, y1_end = x1 + w1, y1 + l1
    x2_end, y2_end = x2 + w2, y2 + l2

    TOLERANCE = 0.5  # ft

    # Horizontal wall touch (r1 is North of r2, or r2 is North of r1)
    # They share a horizontal line: y1_end == y2 or y2_end == y1
    if abs(y1_end - y2) <= TOLERANCE or abs(y2_end - y1) <= TOLERANCE:
        shared_y = y1_end if abs(y1_end - y2) <= TOLERANCE else y2_end
        overlap_start = max(x1, x2)
        overlap_end = min(x1_end, x2_end)
        overlap_len = overlap_end - overlap_start
        if overlap_len >= 2.5:  # Sufficient for door
            return {
                "orientation": "H",
                "coord": shared_y,
                "start": overlap_start,
                "end": overlap_end,
                "length": overlap_len
            }

    # Vertical wall touch (r1 is West of r2, or r2 is West of r1)
    # They share a vertical line: x1_end == x2 or x2_end == x1
    if abs(x1_end - x2) <= TOLERANCE or abs(x2_end - x1) <= TOLERANCE:
        shared_x = x1_end if abs(x1_end - x2) <= TOLERANCE else x2_end
        overlap_start = max(y1, y2)
        overlap_end = min(y1_end, y2_end)
        overlap_len = overlap_end - overlap_start
        if overlap_len >= 2.5:
            return {
                "orientation": "V",
                "coord": shared_x,
                "start": overlap_start,
                "end": overlap_end,
                "length": overlap_len
            }

    return None

class CirculationGraph:
    def __init__(self, floors_rooms: Dict[int, List[Dict[str, Any]]], facing: str = "south"):
        self.floors_rooms = floors_rooms
        self.facing = facing.lower()
        self.adjacencies = []  # list of (r1, r2, shared_seg)
        self.graph = {}  # room_id -> list of neighbor room_ids
        self._build_physical_connections()

    def _build_physical_connections(self):
        for lvl, rooms in self.floors_rooms.items():
            for r in rooms:
                self.graph.setdefault(r["id"], [])

            n = len(rooms)
            for i in range(n):
                r1 = rooms[i]
                for j in range(i + 1, n):
                    r2 = rooms[j]
                    seg = find_shared_wall_segment(r1, r2)
                    if seg:
                        t1, t2 = r1["type"], r2["type"]
                        # Check forbidden connections
                        if (t1, t2) in FORBIDDEN_CONNECTIONS or (t2, t1) in FORBIDDEN_CONNECTIONS:
                            continue
                        # If both are normal bedrooms, do not connect directly (privacy)
                        if "bedroom" in t1 and "bedroom" in t2:
                            continue

                        self.adjacencies.append((r1, r2, seg))
                        self.graph[r1["id"]].append(r2["id"])
                        self.graph[r2["id"]].append(r1["id"])

        # Multi-floor link via staircase
        stairs = []
        for lvl, rooms in self.floors_rooms.items():
            for r in rooms:
                if r["type"] in ["staircase", "stairs"]:
                    stairs.append((lvl, r))
        
        if len(stairs) >= 2:
            stairs.sort(key=lambda s: s[0])
            for i in range(len(stairs) - 1):
                s1_id = stairs[i][1]["id"]
                s2_id = stairs[i + 1][1]["id"]
                self.graph[s1_id].append(s2_id)
                self.graph[s2_id].append(s1_id)

    def validate_circulation(self) -> Dict[str, Any]:
        """
        Validates reachability of all rooms starting from the main living room / entrance on ground floor.
        """
        ground_rooms = self.floors_rooms.get(0, [])
        # Find entry room: living_room or foyer
        entry_room = None
        for r in ground_rooms:
            if r["type"] == "foyer":
                entry_room = r
                break
        if not entry_room:
            for r in ground_rooms:
                if r["type"] == "living_room":
                    entry_room = r
                    break

        if not entry_room:
            # Fallback to first room on ground
            entry_room = ground_rooms[0] if ground_rooms else None

        if not entry_room:
            return {"valid": False, "isolated_rooms": ["no_rooms_found"], "visited_count": 0}

        # BFS from entry_room
        visited: Set[str] = set()
        queue = deque([entry_room["id"]])
        visited.add(entry_room["id"])

        while queue:
            curr_id = queue.popleft()
            for neighbor_id in self.graph.get(curr_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)

        # Collect all non-outdoor rooms that should be reachable
        all_rooms = {}
        for lvl, rooms in self.floors_rooms.items():
            for r in rooms:
                # Parking and open terrace may be accessed externally or through specific doors
                all_rooms[r["id"]] = r

        isolated = []
        for r_id, r in all_rooms.items():
            if r["type"] in ["parking", "garage", "terrace", "balcony", "garden"]:
                continue
            if r_id not in visited:
                isolated.append(r["type"])

        # Check key adjacencies
        has_k_d = self.check_adjacency("kitchen", "dining_room")
        has_l_d = self.check_adjacency("living_room", "dining_room")
        has_stair_hub = (
            self.check_adjacency("staircase", "corridor") or self.check_adjacency("staircase", "living_room") or
            self.check_adjacency("stairs", "corridor") or self.check_adjacency("stairs", "living_room")
        )

        return {
            "valid": len(isolated) == 0,
            "isolated_rooms": isolated,
            "visited_count": len(visited),
            "total_rooms": len(all_rooms),
            "kitchen_dining": has_k_d,
            "living_dining": has_l_d,
            "stair_hub": has_stair_hub,
        }

    def check_adjacency(self, type1: str, type2: str) -> bool:
        for r1, r2, _ in self.adjacencies:
            if (r1["type"] == type1 and r2["type"] == type2) or (r1["type"] == type2 and r2["type"] == type1):
                return True
        return False

    def generate_doors_and_openings(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Creates doors on shared walls along the spanning tree of the circulation graph.
        Returns (doors_list, openings_list).
        """
        doors = []
        openings = []
        connected_pairs: Set[Tuple[str, str]] = set()

        # Prioritize natural architectural movement paths:
        # Foyer <-> Living, Living <-> Dining (often an open archway/opening), Dining <-> Kitchen,
        # Hub <-> Bedrooms, Hub <-> Common Bath, Master Bed <-> Attached Bath, Hub <-> Stairs
        for r1, r2, seg in self.adjacencies:
            t1, t2 = r1["type"], r2["type"]
            pair_key = tuple(sorted([r1["id"], r2["id"]]))
            if pair_key in connected_pairs:
                continue

            # Living <-> Dining can be an open-plan opening
            if (t1 == "living_room" and t2 == "dining_room") or (t1 == "dining_room" and t2 == "living_room"):
                openings.append({
                    "id": f"open_{r1['id']}_{r2['id']}",
                    "type": "open_plan",
                    "orientation": seg["orientation"],
                    "position": {
                        "x": (seg["start"] + seg["end"]) / 2 if seg["orientation"] == "H" else seg["coord"],
                        "y": seg["coord"] if seg["orientation"] == "H" else (seg["start"] + seg["end"]) / 2
                    },
                    "width": min(seg["length"] - 1.0, 6.0),
                    "room_ids": [r1["id"], r2["id"]]
                })
                connected_pairs.add(pair_key)
                continue

            # Standard door on shared wall
            door_w = 3.0
            if "bathroom" in t1 or "bathroom" in t2 or "toilet" in t1 or "toilet" in t2:
                door_w = 2.5

            door_pos_center = (seg["start"] + seg["end"]) / 2
            if seg["orientation"] == "H":
                pos = Point2D(x=round(door_pos_center - door_w / 2, 1), y=round(seg["coord"], 1))
            else:
                pos = Point2D(x=round(seg["coord"], 1), y=round(door_pos_center - door_w / 2, 1))

            doors.append(Door(
                id=f"d_{r1['id']}_{r2['id']}",
                type="interior",
                position=pos,
                width=door_w,
                room_ids=[r1["id"], r2["id"]],
                floor_level=r1.get("floor_level", 0)
            ))
            connected_pairs.add(pair_key)

        return doors, openings

    def generate_exterior_windows(self, build_box: Dict[str, float]) -> List[Window]:
        """
        Generates windows on perimeter walls that face open setbacks / exterior.
        """
        windows = []
        for lvl, rooms in self.floors_rooms.items():
            for r in rooms:
                rtype = r["type"]
                if rtype in ["staircase", "stairs", "corridor", "parking", "garage", "terrace"]:
                    continue

                rx, ry, rw, rl = r["x"], r["y"], r["width"], r["length"]
                rx_end, ry_end = rx + rw, ry + rl

                # Check which edges touch the exterior buildable box
                # North edge (y == build_box['y_start'])
                # South edge (y_end == build_box['y_end'])
                # West edge (x == build_box['x_start'])
                # East edge (x_end == build_box['x_end'])
                exterior_edges = []
                if abs(ry - build_box["y_start"]) <= 1.0:
                    exterior_edges.append(("N", (rx + rx_end) / 2, ry))
                if abs(ry_end - build_box["y_end"]) <= 1.0:
                    exterior_edges.append(("S", (rx + rx_end) / 2, ry_end))
                if abs(rx - build_box["x_start"]) <= 1.0:
                    exterior_edges.append(("W", rx, (ry + ry_end) / 2))
                if abs(rx_end - build_box["x_end"]) <= 1.0:
                    exterior_edges.append(("E", rx_end, (ry + ry_end) / 2))

                win_w = 4.0 if rtype in ["living_room", "bedroom", "master_bedroom"] else 3.0
                if "bath" in rtype or "toilet" in rtype:
                    win_w = 2.0

                for orient, wx, wy in exterior_edges[:1]:  # 1 window per exterior room
                    windows.append(Window(
                        id=f"win_{r['id']}_{orient}",
                        type="standard",
                        position=Point2D(x=round(wx - win_w / 2, 1), y=round(wy, 1)),
                        width=win_w,
                        room_id=r["id"]
                    ))

        return windows
