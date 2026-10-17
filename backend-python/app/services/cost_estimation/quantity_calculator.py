"""
Quantity Calculator — Phase 6D.
Extracts geometry-derived measurements from validated LayoutData using Shapely.
Calculates area schedules, wall quantities, opening deductions, masonry volume,
concrete, structural steel allowance, flooring, finishes, and fixture counts.
Avoids double-counting and strictly separates indoor and outdoor spaces.
"""

import math
from typing import Dict, Any, List, Tuple
from shapely.geometry import box, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
from app.models.layout import LayoutData, Floor, Room, Wall, Door, Window
from app.models.cost_estimate import AreaScheduleSummary

# Types considered outdoor
_OUTDOOR_ROOM_TYPES = {"terrace", "courtyard", "garden", "balcony", "yard", "parking", "garage", "roof"}
_CIRCULATION_TYPES = {"corridor", "hallway", "circulation", "foyer", "stairs", "staircase"}
_WET_ROOM_TYPES = {"bathroom", "toilet", "washroom", "kitchen", "utility", "utility_room"}


class QuantityCalculator:
    def __init__(self, layout: LayoutData, custom_specs: Dict[str, Any] = None):
        self.layout = layout
        self.specs = custom_specs or {}

        # Configurable construction specifications with engineering defaults
        self.floor_height = float(self.specs.get("floor_height", 10.0))          # feet
        self.slab_thickness = float(self.specs.get("slab_thickness", 5.0)) / 12.0  # 5 inches in feet = 0.4167 ft
        self.ext_wall_thickness = float(self.specs.get("ext_wall_thickness", 9.0)) / 12.0  # 9 inches = 0.75 ft
        self.int_wall_thickness = float(self.specs.get("int_wall_thickness", 4.5)) / 12.0  # 4.5 inches = 0.375 ft
        self.steel_factor_kg_sqft = float(self.specs.get("steel_factor_kg_sqft", 4.0))     # 4.0 kg / sq ft BUA
        self.flooring_wastage_pct = float(self.specs.get("flooring_wastage_pct", 7.0))    # 7%
        self.brick_wastage_pct = float(self.specs.get("brick_wastage_pct", 5.0))          # 5%
        self.door_height_std = float(self.specs.get("door_height_std", 7.0))               # 7.0 ft
        self.door_height_main = float(self.specs.get("door_height_main", 7.5))             # 7.5 ft
        self.window_height_std = float(self.specs.get("window_height_std", 4.5))           # 4.5 ft
        self.window_height_vent = float(self.specs.get("window_height_vent", 2.5))         # 2.5 ft

    def calculate_area_schedule(self) -> AreaScheduleSummary:
        """
        Calculates exact area schedule from true polygon geometry.
        Strictly prevents double-counting and separates indoor and outdoor spaces.
        """
        plot_area = round(float(self.layout.plot.width * self.layout.plot.length), 2)

        # Ground floor constructed footprint
        built_up_by_floor: Dict[int, float] = {}
        indoor_room_by_floor: Dict[int, float] = {}

        total_bua = 0.0
        total_indoor = 0.0

        for floor in self.layout.floors:
            lvl = floor.level
            # 1. Genuine indoor rooms
            indoor_rooms = [
                r for r in floor.rooms
                if getattr(r, 'space_category', '') != 'outdoor'
                and (r.type or '').lower() not in _OUTDOOR_ROOM_TYPES
            ]

            # True polygon union for floor slab
            if indoor_rooms:
                room_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in indoor_rooms]
                floor_slab = unary_union(room_boxes)
                floor_bua = round(float(floor_slab.area), 2)
                floor_indoor = round(sum(r.width * r.length for r in indoor_rooms), 2)
            else:
                floor_bua = 0.0
                floor_indoor = 0.0

            built_up_by_floor[lvl] = floor_bua
            indoor_room_by_floor[lvl] = floor_indoor
            total_bua += floor_bua
            total_indoor += floor_indoor

        # Ground floor footprint from building_footprint or floor 0 slab
        gf_footprint = built_up_by_floor.get(0, 0.0)
        if self.layout.plot.building_footprint:
            footprint_val = self.layout.plot.building_footprint.get("constructed_area")
            if footprint_val and footprint_val > 0:
                gf_footprint = round(float(footprint_val), 2)

        # Collect ground site outdoor areas
        outdoor_areas: List[Dict[str, Any]] = []
        for site_area in getattr(self.layout.plot, "site_areas", []):
            outdoor_areas.append({
                "type": site_area.get("type", "site_area"),
                "area": round(float(site_area.get("area", 0.0)), 2),
                "label": site_area.get("label", site_area.get("type", "Outdoor Area")),
                "location": "plot_ground"
            })

        # Ground floor outdoor rooms if any
        if self.layout.floors:
            gf = self.layout.floors[0]
            for r in gf.rooms:
                if getattr(r, 'space_category', '') == 'outdoor' or (r.type or '').lower() in _OUTDOOR_ROOM_TYPES:
                    outdoor_areas.append({
                        "type": r.type,
                        "area": round(float(r.width * r.length), 2),
                        "label": r.label or r.type,
                        "location": "ground_floor"
                    })

        # Upper floor outdoor areas (balconies, open terraces, roof slab below)
        terrace_roof_areas: List[Dict[str, Any]] = []
        for floor in self.layout.floors:
            if floor.level > 0:
                all_upper_outdoor = list(getattr(floor, "outdoor_areas", []))
                for r in floor.rooms:
                    if getattr(r, 'space_category', '') == 'outdoor' or (r.type or '').lower() in _OUTDOOR_ROOM_TYPES:
                        if r not in all_upper_outdoor:
                            all_upper_outdoor.append(r)

                for out in all_upper_outdoor:
                    area_val = getattr(out, 'area', 0.0)
                    if not area_val or area_val <= 0:
                        area_val = out.width * out.length
                    terrace_roof_areas.append({
                        "type": getattr(out, 'type', 'outdoor_area'),
                        "area": round(float(area_val), 2),
                        "label": getattr(out, 'label', getattr(out, 'type', 'Upper Outdoor Space')),
                        "floor_level": floor.level
                    })

        # Calculate physical structural wall footprint from true wall lengths and thicknesses
        total_wall_footprint = 0.0
        for floor in self.layout.floors:
            indoor_rooms = [
                r for r in floor.rooms
                if getattr(r, 'space_category', '') != 'outdoor'
                and (r.type or '').lower() not in _OUTDOOR_ROOM_TYPES
            ]
            if indoor_rooms:
                room_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in indoor_rooms]
                floor_union = unary_union(room_boxes)
                ext_p = floor_union.boundary.length
                sum_p = sum(2.0 * (r.width + r.length) for r in indoor_rooms)
                int_l = max(0.0, (sum_p - ext_p) / 2.0)
                total_wall_footprint += (ext_p * self.ext_wall_thickness) + (int_l * self.int_wall_thickness)

        wall_footprint = round(total_wall_footprint, 2)

        return AreaScheduleSummary(
            plot_area=plot_area,
            ground_constructed_footprint=gf_footprint,
            built_up_by_floor=built_up_by_floor,
            total_built_up_area=round(total_bua, 2),
            indoor_room_area_by_floor=indoor_room_by_floor,
            total_indoor_room_area=round(total_indoor, 2),
            outdoor_areas=outdoor_areas,
            terrace_roof_areas=terrace_roof_areas,
            wall_footprint_area=wall_footprint,
            derivation_method="Shapely exact polygon union and disjoint room decomposition"
        )

    def calculate_wall_quantities(self) -> Dict[str, Any]:
        """
        Calculates exterior & interior wall lengths, gross wall areas,
        opening deductions (doors & windows), net wall areas, masonry volume,
        and plaster surface area.
        """
        total_ext_length = 0.0
        total_int_length = 0.0
        total_door_deduction_area = 0.0
        total_window_deduction_area = 0.0
        door_counts = {"main": 0, "internal": 0, "toilet": 0}
        window_counts = {"standard": 0, "ventilator": 0}

        for floor in self.layout.floors:
            indoor_rooms = [
                r for r in floor.rooms
                if getattr(r, 'space_category', '') != 'outdoor'
                and (r.type or '').lower() not in _OUTDOOR_ROOM_TYPES
            ]
            if not indoor_rooms:
                continue

            # Mathematically exact Shapely polygon boundary decomposition
            # This precisely separates the outer building envelope (exterior walls, 9" thickness)
            # from shared internal partitions (4.5" thickness) without double-counting shared walls.
            room_boxes = [box(r.x, r.y, r.x + r.width, r.y + r.length) for r in indoor_rooms]
            floor_union = unary_union(room_boxes)
            exterior_perimeter = floor_union.boundary.length
            sum_of_individual_perimeters = sum(2.0 * (r.width + r.length) for r in indoor_rooms)

            # Shared walls appear twice in the sum of individual room perimeters
            # Shared interior wall length = (sum(individual) - exterior) / 2
            interior_partition_length = max(0.0, (sum_of_individual_perimeters - exterior_perimeter) / 2.0)

            total_ext_length += exterior_perimeter
            total_int_length += interior_partition_length

            # Calculate door opening deductions on this floor
            for d in floor.doors:
                width = float(d.width)
                is_main = (d.type == "main_entrance" or "main" in (d.type or "").lower())
                is_toilet = any("bath" in r_id.lower() or "toilet" in r_id.lower() or "util" in r_id.lower() for r_id in d.room_ids)

                if is_main:
                    height = self.door_height_main
                    door_counts["main"] += 1
                elif is_toilet:
                    height = self.door_height_std
                    door_counts["toilet"] += 1
                else:
                    height = self.door_height_std
                    door_counts["internal"] += 1

                total_door_deduction_area += (width * height)

            # Calculate window opening deductions on this floor
            for w in floor.windows:
                width = float(w.width)
                is_vent = ("vent" in (w.type or "").lower() or (w.room_id and "bath" in w.room_id.lower()))
                if is_vent:
                    height = self.window_height_vent
                    window_counts["ventilator"] += 1
                else:
                    height = self.window_height_std
                    window_counts["standard"] += 1

                total_window_deduction_area += (width * height)

        # Fallback if doors/windows were not populated in layout
        if (door_counts["main"] + door_counts["internal"] + door_counts["toilet"]) == 0:
            # Typical residential rule of thumb: 1 main door + 1 per bedroom/kitchen + 1 per bath
            door_counts["main"] = 1
            door_counts["internal"] = max(2, len([r for fl in self.layout.floors for r in fl.rooms if (r.type or '').lower() in {'bedroom', 'kitchen', 'living_room', 'dining_room', 'pooja'}]))
            door_counts["toilet"] = max(1, len([r for fl in self.layout.floors for r in fl.rooms if (r.type or '').lower() in _WET_ROOM_TYPES]))
            total_door_deduction_area = (door_counts["main"] * 3.5 * self.door_height_main) + \
                                        (door_counts["internal"] * 3.0 * self.door_height_std) + \
                                        (door_counts["toilet"] * 2.5 * self.door_height_std)

        if (window_counts["standard"] + window_counts["ventilator"]) == 0:
            window_counts["standard"] = max(4, len([r for fl in self.layout.floors for r in fl.rooms if (r.type or '').lower() in {'bedroom', 'living_room', 'kitchen'}]) * 2)
            window_counts["ventilator"] = max(1, door_counts["toilet"])
            total_window_deduction_area = (window_counts["standard"] * 4.0 * self.window_height_std) + \
                                          (window_counts["ventilator"] * 2.0 * self.window_height_vent)

        gross_ext_area = total_ext_length * self.floor_height
        gross_int_area = total_int_length * self.floor_height
        gross_wall_area = gross_ext_area + gross_int_area

        # Apportion deductions: Windows are on exterior walls; doors are split between main (ext) and internal (int)
        ext_deductions = total_window_deduction_area + (door_counts["main"] * 3.5 * self.door_height_main)
        int_deductions = max(0.0, (total_door_deduction_area - (door_counts["main"] * 3.5 * self.door_height_main)))

        net_ext_area = max(0.0, gross_ext_area - ext_deductions)
        net_int_area = max(0.0, gross_int_area - int_deductions)
        net_wall_area = net_ext_area + net_int_area

        # Masonry Volume (cu ft)
        # Exterior walls: 9" (0.75 ft) thickness
        # Interior walls: 4.5" (0.375 ft) thickness
        ext_masonry_volume = net_ext_area * self.ext_wall_thickness
        int_masonry_volume = net_int_area * self.int_wall_thickness
        total_masonry_volume = round(ext_masonry_volume + int_masonry_volume, 2)

        # Brick quantity: ~13.5 standard red clay bricks per cu ft of masonry
        # With 5% handling & cutting wastage
        bricks_needed = math.ceil(total_masonry_volume * 13.5 * (1.0 + self.brick_wastage_pct / 100.0))

        # Plaster surface area (sq ft)
        # Interior faces of exterior walls (1 face) + Exterior faces of exterior walls (1 face) = 2 faces
        # Interior partition walls (2 faces)
        # Ceiling plaster = total indoor room area
        total_indoor_room_area = sum(
            sum(r.width * r.length for r in fl.rooms if getattr(r, 'space_category', '') != 'outdoor' and (r.type or '').lower() not in _OUTDOOR_ROOM_TYPES)
            for fl in self.layout.floors
        )
        wall_plaster_area = (net_ext_area * 2.0) + (net_int_area * 2.0)
        ceiling_plaster_area = total_indoor_room_area
        total_plaster_area = round(wall_plaster_area + ceiling_plaster_area, 2)

        # Internal wall & ceiling paint area
        internal_paint_area = round((net_ext_area * 1.0) + (net_int_area * 2.0) + ceiling_plaster_area, 2)
        # External weatherproof paint area
        external_paint_area = round(net_ext_area * 1.0, 2)

        return {
            "ext_wall_length_ft": round(total_ext_length, 2),
            "int_wall_length_ft": round(total_int_length, 2),
            "total_wall_length_ft": round(total_ext_length + total_int_length, 2),
            "gross_ext_wall_area_sqft": round(gross_ext_area, 2),
            "gross_int_wall_area_sqft": round(gross_int_area, 2),
            "gross_wall_area_sqft": round(gross_wall_area, 2),
            "door_deduction_sqft": round(total_door_deduction_area, 2),
            "window_deduction_sqft": round(total_window_deduction_area, 2),
            "total_opening_deductions_sqft": round(total_door_deduction_area + total_window_deduction_area, 2),
            "net_ext_wall_area_sqft": round(net_ext_area, 2),
            "net_int_wall_area_sqft": round(net_int_area, 2),
            "net_wall_area_sqft": round(net_wall_area, 2),
            "masonry_volume_cuft": total_masonry_volume,
            "bricks_count_pieces": bricks_needed,
            "total_plaster_area_sqft": total_plaster_area,
            "internal_paint_area_sqft": internal_paint_area,
            "external_paint_area_sqft": external_paint_area,
            "door_counts": door_counts,
            "window_counts": window_counts,
            "total_window_area_sqft": round(total_window_deduction_area, 2)
        }

    def calculate_concrete_and_steel(self, total_bua: float) -> Dict[str, Any]:
        """
        Calculates RCC concrete volumes (M20 grade: 1:1.5:3) and provisional steel reinforcement.
        Distinguishes geometry-derived slab volumes from provisional structural allowances.
        """
        # 1. Slab concrete (Geometry-derived: Total BUA * Slab Thickness)
        slab_concrete_cuft = total_bua * self.slab_thickness

        # 2. Beams, Columns, Footings concrete (Standard residential benchmark allowance: 0.12 cu ft / sq ft BUA)
        structural_allowance_cuft = total_bua * 0.12

        total_concrete_cuft = round(slab_concrete_cuft + structural_allowance_cuft, 2)
        total_concrete_cum = round(total_concrete_cuft * 0.0283168, 2)

        # Materials for M20 Concrete (1 : 1.5 : 3):
        # Dry mix factor = 1.54
        # Total dry volume = Total Concrete * 1.54
        dry_volume_cuft = total_concrete_cuft * 1.54
        ratio_sum = 1.0 + 1.5 + 3.0  # 5.5

        # Cement: (dry_volume / 5.5) / 1.226 cu ft per 50kg bag
        cement_cuft_conc = dry_volume_cuft / ratio_sum
        cement_bags_conc = math.ceil((cement_cuft_conc / 1.226) * 1.03)  # +3% wastage

        # Sand: (dry_volume * 1.5 / 5.5) cu ft
        sand_cuft_conc = round((dry_volume_cuft * 1.5 / ratio_sum) * 1.05, 2)  # +5% wastage

        # Coarse Aggregate: (dry_volume * 3.0 / 5.5) cu ft
        coarse_agg_cuft_conc = round((dry_volume_cuft * 3.0 / ratio_sum) * 1.05, 2)  # +5% wastage

        # 3. Structural Steel Reinforcement (TMT Fe550):
        # Provisional Allowance based on 4.0 kg per sq ft of BUA
        steel_kg = round(total_bua * self.steel_factor_kg_sqft, 2)
        steel_tonnes = round(steel_kg / 1000.0, 3)

        return {
            "slab_concrete_cuft": round(slab_concrete_cuft, 2),
            "structural_allowance_concrete_cuft": round(structural_allowance_cuft, 2),
            "total_concrete_cuft": total_concrete_cuft,
            "total_concrete_cum": total_concrete_cum,
            "cement_bags_concrete": cement_bags_conc,
            "sand_cuft_concrete": sand_cuft_conc,
            "coarse_aggregate_cuft_concrete": coarse_agg_cuft_conc,
            "steel_reinforcement_kg": steel_kg,
            "steel_reinforcement_tonnes": steel_tonnes,
            "steel_factor_applied": f"{self.steel_factor_kg_sqft} kg/sq ft BUA (Provisional residential allowance)"
        }

    def calculate_mortar_materials(self, masonry_volume_cuft: float, plaster_area_sqft: float) -> Dict[str, Any]:
        """
        Calculates cement bags and sand for brickwork mortar (1:6) and plastering mortar (1:4 ceiling, 1:6 wall).
        """
        # 1. Brickwork Mortar (1:6 mix): ~0.25 cu ft mortar per cu ft masonry
        # Dry volume factor = 1.33
        wet_mortar_brick_cuft = masonry_volume_cuft * 0.25
        dry_mortar_brick_cuft = wet_mortar_brick_cuft * 1.33
        cement_brick_cuft = dry_mortar_brick_cuft / 7.0
        cement_bags_brick = math.ceil((cement_brick_cuft / 1.226) * 1.05)
        sand_brick_cuft = round((dry_mortar_brick_cuft * 6.0 / 7.0) * 1.05, 2)

        # 2. Plaster Mortar (Average 15mm = 0.0492 ft thickness, 1:6 mix)
        wet_plaster_cuft = plaster_area_sqft * (0.5 / 12.0)  # ~12.5mm / 0.5 inch
        dry_plaster_cuft = wet_plaster_cuft * 1.33
        cement_plaster_cuft = dry_plaster_cuft / 7.0
        cement_bags_plaster = math.ceil((cement_plaster_cuft / 1.226) * 1.05)
        sand_plaster_cuft = round((dry_plaster_cuft * 6.0 / 7.0) * 1.05, 2)

        return {
            "cement_bags_brickwork": cement_bags_brick,
            "sand_cuft_brickwork": sand_brick_cuft,
            "cement_bags_plaster": cement_bags_plaster,
            "sand_cuft_plaster": sand_plaster_cuft,
            "total_cement_bags_mortar": cement_bags_brick + cement_bags_plaster,
            "total_sand_cuft_mortar": round(sand_brick_cuft + sand_plaster_cuft, 2)
        }

    def calculate_flooring_and_finishes(self, area_schedule: AreaScheduleSummary) -> Dict[str, Any]:
        """
        Calculates flooring quantities, skirting, and terrace waterproofing.
        Strictly excludes outdoor surfaces from indoor flooring.
        """
        # Indoor flooring = total indoor room area + wastage
        indoor_net_sqft = area_schedule.total_indoor_room_area
        indoor_gross_sqft = round(indoor_net_sqft * (1.0 + self.flooring_wastage_pct / 100.0), 2)

        # Outdoor paving (balconies, open terraces)
        upper_outdoor_net_sqft = sum(item.get("area", 0.0) for item in area_schedule.terrace_roof_areas if "roof" not in item.get("type", "").lower())
        outdoor_paving_gross_sqft = round(upper_outdoor_net_sqft * 1.08, 2)

        # Terrace & toilet waterproofing:
        # Open terraces + roof slabs + wet area floors
        terrace_roof_sum = sum(item.get("area", 0.0) for item in area_schedule.terrace_roof_areas)
        wet_rooms_area = sum(
            sum(r.width * r.length for r in fl.rooms if (r.type or '').lower() in _WET_ROOM_TYPES)
            for fl in self.layout.floors
        )
        waterproofing_sqft = round(terrace_roof_sum + wet_rooms_area, 2)

        # Skirting: approximate running feet as 12% of indoor sq ft
        skirting_rft = round(indoor_net_sqft * 0.12, 1)

        # Staircase granite treads & risers
        stair_area = sum(
            sum(r.width * r.length for r in fl.rooms if (r.type or '').lower() in {'staircase', 'stairs'})
            for fl in self.layout.floors
        )
        staircase_granite_sqft = round(stair_area * 1.35, 1) if stair_area > 0 else 0.0

        return {
            "indoor_flooring_net_sqft": indoor_net_sqft,
            "indoor_flooring_gross_sqft": indoor_gross_sqft,
            "outdoor_paving_gross_sqft": outdoor_paving_gross_sqft,
            "waterproofing_sqft": waterproofing_sqft,
            "skirting_running_ft": skirting_rft,
            "staircase_granite_sqft": staircase_granite_sqft
        }

    def calculate_fixtures_and_services(self, area_schedule: AreaScheduleSummary, wall_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates plumbing wet area points, electrical point allowances, and staircase railing.
        """
        # Wet areas count (bathrooms, toilets, kitchen, utility)
        wet_areas_count = sum(
            sum(1 for r in fl.rooms if (r.type or '').lower() in _WET_ROOM_TYPES)
            for fl in self.layout.floors
        )
        if wet_areas_count == 0:
            wet_areas_count = max(2, len(self.layout.floors) * 2)

        # Electrical points allowance: ~1 point per 22 sq ft of indoor area + 10 dedicated appliance points per floor
        indoor_sqft = area_schedule.total_indoor_room_area
        num_floors = len(self.layout.floors) or 1
        base_points = math.ceil(indoor_sqft / 22.0)
        dedicated_points = num_floors * 10
        total_electrical_points = base_points + dedicated_points

        # Staircase railing running feet
        has_stairs = any(
            any((r.type or '').lower() in {'staircase', 'stairs'} for r in fl.rooms)
            for fl in self.layout.floors
        )
        staircase_railing_rft = (num_floors - 1) * 28.0 if (has_stairs and num_floors > 1) else (28.0 if has_stairs else 0.0)

        return {
            "wet_areas_count": wet_areas_count,
            "total_electrical_points": total_electrical_points,
            "staircase_railing_rft": round(staircase_railing_rft, 1)
        }
