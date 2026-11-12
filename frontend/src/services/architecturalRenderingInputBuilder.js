/**
 * architecturalRenderingInputBuilder.js — Phase 6K
 *
 * Authoritative pipeline that separates architectural geometry from visual rendering.
 * Extracts the canonical building dimensions, floor plans, fenestrations,
 * exterior selections, and room-specific interior configurations into a structured,
 * validated rendering specification.
 */

import { generateCanonicalFloorPlan } from './canonicalFloorPlanGenerator';

/**
 * Builds the complete, normalized rendering input model for a project.
 *
 * @param {Object} params
 * @param {Object} params.project - Base project metadata (plot_width, plot_length, floors, facing)
 * @param {Object} params.floorPlan - Approved floor-plan geometry (floors, rooms, walls, doors, windows)
 * @param {Object} params.exteriorSelection - Saved exterior design, 12-key colors, materials
 * @param {Object} params.interiorSelections - Saved interior selections dictionary keyed by room_id
 * @returns {Object} Structured rendering input specification
 */
export function buildArchitecturalRenderingInput({
  project,
  floorPlan,
  exteriorSelection,
  interiorSelections = {}
}) {
  if (!project?.id) {
    throw new Error('Valid project configuration is required to build rendering specification');
  }

  // 1. Authoritative Floor Plan Resolution
  let plan = floorPlan;
  if (!plan || !Array.isArray(plan.floors) || plan.floors.length === 0) {
    plan = generateCanonicalFloorPlan(project);
  }

  const pw = Number(project.plot_width) || 30;
  const pl = Number(project.plot_length) || 40;
  const numFloors = Math.max(1, Math.min(3, Number(project.floors) || plan.floors.length || 2));

  // Footprint bounds
  const bldgFp =
    plan.plot?.building_footprint ||
    plan.site_planning?.building_footprint || {
      x: 6,
      y: 8,
      width: pw * 0.75,
      length: pl * 0.65
    };

  // 2. Exterior Colors & Materials Specification
  const extColors = exteriorSelection?.selection?.colors || exteriorSelection?.colors || {
    primary_wall: '#F4F4F0',
    secondary_wall: '#E5E7EB',
    accent_wall: '#2B313B',
    front_facade: '#F4F4F0',
    boundary_wall: '#E5E0D6',
    boundary_gate: '#30343B',
    door: '#8B5A2B',
    window_frame: '#20252B',
    window_glass_tint: '#7DD3FC',
    railing: '#1F2937',
    roof_parapet: '#343A40',
    exterior_trims: '#20252B'
  };

  const extMaterials = exteriorSelection?.selection?.materials || exteriorSelection?.materials || {
    finish_type: 'matte_paint',
    cladding_type: 'none',
    door_material: 'solid_teak',
    railing_material: 'toughened_glass'
  };

  const extDesignMeta = {
    id: exteriorSelection?.selection?.design_id || exteriorSelection?.design_id || 'ext_mod_01',
    name: exteriorSelection?.selection?.design_name || exteriorSelection?.design_name || 'Modern Contemporary',
    category: exteriorSelection?.selection?.category || exteriorSelection?.category || 'modern_contemporary',
    style: exteriorSelection?.selection?.style || exteriorSelection?.style || 'Modern'
  };

  // 3. Normalized Room Specifications
  const roomsList = [];
  plan.floors.forEach((floorObj, floorIdx) => {
    if (floorIdx >= numFloors) return;

    const floorName = floorObj.name || (floorIdx === 0 ? 'Ground Floor' : `Floor ${floorIdx}`);
    const floorRooms = floorObj.rooms || [];
    const floorDoors = floorObj.doors || [];
    const floorWindows = floorObj.windows || [];

    floorRooms.forEach((room) => {
      // Find room-specific interior selection
      const savedSel =
        interiorSelections[room.id] ||
        Object.values(interiorSelections).find((s) => s && s.room_id === room.id) ||
        null;

      // Filter openings adjacent to this room
      const roomDoors = floorDoors.filter((d) => {
        if (!d.position) return true;
        return (
          d.position.x >= room.x - 2 &&
          d.position.x <= room.x + room.width + 2 &&
          d.position.y >= room.y - 2 &&
          d.position.y <= room.y + room.length + 2
        );
      });

      const roomWindows = floorWindows.filter((w) => {
        if (!w.position) return true;
        return (
          w.position.x >= room.x - 2 &&
          w.position.x <= room.x + room.width + 2 &&
          w.position.y >= room.y - 2 &&
          w.position.y <= room.y + room.length + 2
        );
      });

      roomsList.push({
        id: room.id,
        name: room.label || room.name || 'Room',
        type: room.type || 'living_room',
        floor: floorIdx,
        floorName,
        width: room.width,
        length: room.length,
        area: room.area || Math.round(room.width * room.length),
        x: room.x,
        y: room.y,
        doorsCount: roomDoors.length,
        windowsCount: roomWindows.length,
        doors: roomDoors,
        windows: roomWindows,
        selectedDesign: savedSel
          ? {
              designId: savedSel.design_id,
              designName: savedSel.design_name || savedSel.name,
              category: savedSel.category || savedSel.room_type,
              style: savedSel.style || 'Modern',
              wallFinish: savedSel.customizations?.wall_finish_choice || 'Smooth Plaster',
              flooring: savedSel.customizations?.flooring_choice || 'Vitrified Tiles',
              ceiling: savedSel.customizations?.ceiling_option_id || 'Gypsum False Ceiling',
              lightingPoints: savedSel.customizations?.lighting_points_count || 6
            }
          : {
              designId: 'default_civil',
              designName: 'Civil Baseline',
              category: room.type || 'living_room',
              style: 'Standard Architectural',
              wallFinish: 'Standard Emulsion',
              flooring: 'Vitrified Tiles',
              ceiling: 'Plain Plaster Ceiling',
              lightingPoints: 4
            }
      });
    });
  });

  return {
    projectId: project.id,
    projectName: project.name || 'Architectural Residence',
    metadata: {
      budget: project.budget,
      location: project.location,
      created_at: project.created_at,
      derived_at: new Date().toISOString()
    },
    site: {
      plotWidth: pw,
      plotLength: pl,
      facing: project.facing || 'North',
      floors: numFloors,
      footprint: bldgFp
    },
    exterior: {
      design: extDesignMeta,
      colors: extColors,
      materials: extMaterials
    },
    rooms: roomsList,
    authoritativePlan: plan,
    supportedQualityLevels: [
      { id: 'preview', label: 'Fast Preview', resolution: '1280 × 720', description: 'Fast WebGL viewport render with standard shading (~0.5s)' },
      { id: 'high', label: 'High Quality', resolution: '1920 × 1080', description: 'Full HD multi-sampled PBR render with soft shadows & ambient bounce (~1.5s)' },
      { id: 'presentation', label: 'Presentation (4K)', resolution: '3840 × 2160', description: 'Ultra HD 4K presentation export with contact occlusion & enhanced reflectance (~3.0s)' }
    ],
    supportedLightingModes: [
      { id: 'daylight', label: 'Natural Daylight', icon: 'Sun', description: 'Bright architectural sun at 5600K with crisp ambient shadows' },
      { id: 'golden_hour', label: 'Golden Hour (Sunset)', icon: 'Sunset', description: 'Warm 3200K low-angle sunlight with dramatic facade highlights' },
      { id: 'night', label: 'Architectural Night', icon: 'Moon', description: 'Deep twilight sky with warm luminous windows and facade wall sconces' }
    ]
  };
}
