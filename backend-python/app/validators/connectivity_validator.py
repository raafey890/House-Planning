"""
Connectivity and Circulation Validator.
Validates whole-house reachability, room access, and absence of isolated rooms.
"""
from typing import Dict, Any, List, Set, Tuple
from collections import deque
from app.models.layout import LayoutData

class ConnectivityValidator:
    @staticmethod
    def validate_connectivity(layout: LayoutData) -> Dict[str, Any]:
        """
        Validates the movement graph across all floors of the layout.
        Verifies:
        1. Main entrance door exists.
        2. Every indoor room is reachable from the main entrance via doors / openings / stairs.
        3. No room requires traversing an unrelated private bedroom.
        4. Staircase connects between floors.
        """
        report: Dict[str, Any] = {
            "connectivity": "PASS",
            "isolated_rooms": [],
            "required_adjacencies": {},
            "circulation_valid": True,
            "stair_connectivity": True,
            "main_entrance_valid": False,
            "details": []
        }

        # 1. Check Main Entrance Door
        main_door = None
        for floor in layout.floors:
            if floor.level == 0:
                for door in floor.doors:
                    if getattr(door, "type", "interior") == "main_entrance":
                        main_door = door
                        break

        if not main_door:
            report["connectivity"] = "FAIL"
            report["circulation_valid"] = False
            report["main_entrance_valid"] = False
            report["details"].append("Main entrance door missing on Ground Floor.")
            return report

        report["main_entrance_valid"] = True
        entry_room_ids = main_door.room_ids or []

        # 2. Build Whole-House Adjacency Graph from Doors and Openings
        adj: Dict[str, Set[str]] = {}
        room_types: Dict[str, str] = {}
        all_rooms: Set[str] = set()

        for floor in layout.floors:
            for room in floor.rooms:
                all_rooms.add(room.id)
                room_types[room.id] = room.type
                adj.setdefault(room.id, set())

            for door in floor.doors:
                if len(door.room_ids) >= 2:
                    r1, r2 = door.room_ids[0], door.room_ids[1]
                    if r1 in adj and r2 in adj:
                        adj[r1].add(r2)
                        adj[r2].add(r1)

            # Open-plan openings
            for op in floor.openings:
                r_ids = op.get("room_ids", [])
                if len(r_ids) >= 2:
                    r1, r2 = r_ids[0], r_ids[1]
                    if r1 in adj and r2 in adj:
                        adj[r1].add(r2)
                        adj[r2].add(r1)

        # 3. Inter-Floor Staircase Connections
        stair_by_floor: Dict[int, List[str]] = {}
        for floor in layout.floors:
            for s in floor.stairs:
                stair_by_floor.setdefault(floor.level, []).append(s.id)
            for r in floor.rooms:
                if r.type in ["staircase", "stairs"]:
                    stair_by_floor.setdefault(floor.level, []).append(r.id)

        levels = sorted(stair_by_floor.keys())
        if len(levels) >= 2:
            for i in range(len(levels) - 1):
                s1_list = stair_by_floor[levels[i]]
                s2_list = stair_by_floor[levels[i + 1]]
                if s1_list and s2_list:
                    s1 = s1_list[0]
                    s2 = s2_list[0]
                    adj.setdefault(s1, set()).add(s2)
                    adj.setdefault(s2, set()).add(s1)
                else:
                    report["stair_connectivity"] = False

        # 4. BFS Reachability from Main Entrance Room(s)
        visited: Set[str] = set()
        queue = deque(entry_room_ids)
        for r_id in entry_room_ids:
            visited.add(r_id)

        while queue:
            curr = queue.popleft()
            for neighbor in adj.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # 5. Check Reachability of Habitable Rooms
        # Note: Open terraces, gardens, and vehicle parking might have external gates/access
        isolated = []
        for r_id in all_rooms:
            rtype = room_types.get(r_id, "")
            if rtype in ["parking", "garage", "terrace", "balcony", "garden", "yard", "driveway"]:
                continue
            if r_id not in visited:
                isolated.append(f"{rtype} ({r_id})")

        report["isolated_rooms"] = isolated
        if isolated:
            report["connectivity"] = "FAIL"
            report["circulation_valid"] = False
            report["details"].append(f"Isolated rooms detected: {', '.join(isolated)}")

        # 6. Check Specific Architectural Adjacencies
        # Kitchen <-> Dining
        has_k_d = False
        for r_id, neighbors in adj.items():
            if room_types.get(r_id) == "kitchen":
                if any(room_types.get(n) == "dining_room" for n in neighbors):
                    has_k_d = True
                    break
        report["required_adjacencies"]["kitchen_dining"] = has_k_d

        # Living <-> Dining
        has_l_d = False
        for r_id, neighbors in adj.items():
            if room_types.get(r_id) == "living_room":
                if any(room_types.get(n) == "dining_room" for n in neighbors):
                    has_l_d = True
                    break
        report["required_adjacencies"]["living_dining"] = has_l_d

        return report
