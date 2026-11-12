import * as THREE from 'three';
import { generateCanonicalFloorPlan } from './canonicalFloorPlanGenerator';

/**
 * Unified House 3D Geometry Builder — Phase 6J Enhanced
 *
 * Grounded in:
 * 1. Approved Project Floor Plans & Room Geometry (dimensions, levels, walls, doors, windows, stairs)
 * 2. Selected Exterior Design (facade colors, cladding, door, window frames, railing, boundary)
 * 3. Saved Interior Design Selections per Room (flooring choice, wall finish, furniture, lighting)
 * 4. Architectural Realism (cantilevers, fenestrations, mullions, copings, wardrobes, vanities)
 * 5. Walkthrough collision bounds for reliable eye-level camera navigation
 */

export function buildUnifiedHouseModel({
  project,
  floorPlan,
  exteriorSelection,
  interiorSelections = {},
  options = {}
}) {
  const {
    currentFloor = 'all', // 'all' | 0 | 1 | 2
    viewMode = 'exterior', // 'exterior' | 'interior' | 'top_down'
    isNight = false
  } = options;

  // 1. Resolve authoritative floor plan
  let plan = floorPlan;
  if (!plan || !Array.isArray(plan.floors) || plan.floors.length === 0) {
    plan = generateCanonicalFloorPlan(project);
  }

  const rootGroup = new THREE.Group();
  rootGroup.name = 'UnifiedHouseRoot';

  // Dimensional Scaling: 1 foot = 0.3 meters / Three.js units
  const FT_TO_M = 0.3;
  const pw = Number(project?.plot_width) || 30;
  const pl = Number(project?.plot_length) || 40;
  const numFloors = Math.max(1, Math.min(3, Number(project?.floors) || plan.floors.length || 2));
  const floorHeight = 3.0; // 3.0 meters per level (~10 ft)
  const wallHeight = 2.75;
  const slabThick = 0.22;
  const plinthHeight = 0.45; // Plinth elevation above site level

  // Footprint bounds for centering in world space
  const bldgFp =
    plan.plot?.building_footprint ||
    plan.site_planning?.building_footprint || {
      x: 6,
      y: 8,
      width: pw * 0.75,
      length: pl * 0.65
    };

  const centerFtX = bldgFp.x + bldgFp.width / 2;
  const centerFtY = bldgFp.y + bldgFp.length / 2;

  // Helper coordinate transforms: 2D plan feet -> 3D world meters
  const toWorldX = (ftX) => (ftX - centerFtX) * FT_TO_M;
  const toWorldZ = (ftY) => (ftY - centerFtY) * FT_TO_M;
  const toWorldDim = (ftDim) => ftDim * FT_TO_M;

  // 2. Resolve Exterior Custom Colors & Materials
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

  // Helper safe color
  const safeColor = (hex, fallback = '#e2e8f0') => {
    try {
      if (!hex || typeof hex !== 'string') return new THREE.Color(fallback);
      const clean = hex.trim();
      return new THREE.Color(clean.startsWith('#') ? clean : `#${clean}`);
    } catch (_) {
      return new THREE.Color(fallback);
    }
  };

  // 3. Shared Architectural Material Palette
  const materials = {
    // Exterior Facade
    extPrimary: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.primary_wall, '#F4F4F0'),
      roughness: 0.82,
      metalness: 0.04
    }),
    extAccent: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.accent_wall, '#2B313B'),
      roughness: 0.65,
      metalness: 0.08
    }),
    extTrim: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.exterior_trims, '#20252B'),
      roughness: 0.45,
      metalness: 0.25
    }),
    extPlinth: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#1e293b'),
      roughness: 0.65,
      metalness: 0.12
    }),
    extSlab: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#f1f5f9'),
      roughness: 0.72,
      metalness: 0.05
    }),
    extCoping: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.roof_parapet || extColors.exterior_trims, '#343A40'),
      roughness: 0.5,
      metalness: 0.15
    }),
    extDoor: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.door, '#8B5A2B'),
      roughness: 0.4,
      metalness: 0.15
    }),
    extWindowFrame: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.window_frame, '#20252B'),
      roughness: 0.35,
      metalness: 0.65
    }),
    extGlass: new THREE.MeshPhysicalMaterial({
      color: safeColor(extColors.window_glass_tint, '#7DD3FC'),
      transmission: 0.88,
      opacity: 0.4,
      transparent: true,
      roughness: 0.05,
      metalness: 0.1,
      ior: 1.52
    }),
    extGlassNight: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#fffae6'),
      emissive: new THREE.Color('#f59e0b'),
      emissiveIntensity: 0.62,
      roughness: 0.25,
      metalness: 0.08,
      transparent: true,
      opacity: 0.85
    }),
    glassRailing: new THREE.MeshPhysicalMaterial({
      color: new THREE.Color('#cbd5e1'),
      transmission: 0.92,
      opacity: 0.35,
      transparent: true,
      roughness: 0.08,
      ior: 1.48
    }),
    railingMetal: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.railing, '#1F2937'),
      roughness: 0.25,
      metalness: 0.85
    }),
    boundaryWall: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.boundary_wall, '#E5E0D6'),
      roughness: 0.85,
      metalness: 0.04
    }),
    boundaryGate: new THREE.MeshStandardMaterial({
      color: safeColor(extColors.boundary_gate, '#30343B'),
      roughness: 0.35,
      metalness: 0.75
    }),
    lawnGrass: new THREE.MeshStandardMaterial({
      color: new THREE.Color(isNight ? '#162e19' : '#3e7039'),
      roughness: 0.95,
      metalness: 0.02
    }),
    drivewayPaver: new THREE.MeshStandardMaterial({
      color: new THREE.Color(isNight ? '#334155' : '#64748b'),
      roughness: 0.75,
      metalness: 0.05
    }),
    pathwayPaving: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#94a3b8'),
      roughness: 0.7,
      metalness: 0.06
    }),

    // Interior General
    intPartitionWall: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#f8fafc'),
      roughness: 0.88,
      metalness: 0.02
    }),
    intDoorWood: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#78350f'),
      roughness: 0.48,
      metalness: 0.1
    }),

    // Interior Flooring Types
    floorVitrified: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#ede8de'),
      roughness: 0.18,
      metalness: 0.08
    }),
    floorItalianMarble: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#f8f8f6'),
      roughness: 0.09,
      metalness: 0.12
    }),
    floorHardwood: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#8a5a36'),
      roughness: 0.45,
      metalness: 0.05
    }),
    floorBathroomTile: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#475569'),
      roughness: 0.55,
      metalness: 0.05
    }),
    floorTerracePaver: new THREE.MeshStandardMaterial({
      color: new THREE.Color('#b45309'),
      roughness: 0.75,
      metalness: 0.05
    }),

    // Furniture Standard Materials
    furnitureFabricDark: new THREE.MeshStandardMaterial({ color: new THREE.Color('#1e293b'), roughness: 0.88 }),
    furnitureFabricLight: new THREE.MeshStandardMaterial({ color: new THREE.Color('#f8fafc'), roughness: 0.85 }),
    furnitureFabricAccent: new THREE.MeshStandardMaterial({ color: new THREE.Color('#0369a1'), roughness: 0.82 }),
    furnitureWoodWarm: new THREE.MeshStandardMaterial({ color: new THREE.Color('#78350f'), roughness: 0.52 }),
    furnitureWoodDark: new THREE.MeshStandardMaterial({ color: new THREE.Color('#1e293b'), roughness: 0.42 }),
    furnitureWardrobeWood: new THREE.MeshStandardMaterial({ color: new THREE.Color('#3e2723'), roughness: 0.48 }),
    furnitureCounterGranite: new THREE.MeshStandardMaterial({ color: new THREE.Color('#0f172a'), roughness: 0.22, metalness: 0.25 }),
    furnitureMetalChrome: new THREE.MeshStandardMaterial({ color: new THREE.Color('#e2e8f0'), roughness: 0.18, metalness: 0.9 }),
    furnitureMirror: new THREE.MeshStandardMaterial({ color: new THREE.Color('#ffffff'), roughness: 0.04, metalness: 0.98 }),
    luminaireFixture: new THREE.MeshStandardMaterial({ color: new THREE.Color('#0f172a'), roughness: 0.3, metalness: 0.85 }),
    furnitureRug: new THREE.MeshStandardMaterial({ color: new THREE.Color('#cbd5e1'), roughness: 0.96, metalness: 0.01 })
  };

  // 4. Build Ground, Driveway & Site Landscaping
  const siteGroup = new THREE.Group();
  siteGroup.name = 'SiteGroup';

  const siteW = pw * FT_TO_M * 1.35;
  const siteL = pl * FT_TO_M * 1.35;

  // Grass Base
  const grassGeo = new THREE.PlaneGeometry(siteW, siteL);
  const grassMesh = new THREE.Mesh(grassGeo, materials.lawnGrass);
  grassMesh.rotation.x = -Math.PI / 2;
  grassMesh.position.y = 0;
  grassMesh.receiveShadow = true;
  siteGroup.add(grassMesh);

  // Driveway
  const dwW = toWorldDim(14.0);
  const dwL = toWorldDim(bldgFp.y + 4);
  const dwGeo = new THREE.PlaneGeometry(dwW, dwL);
  const dwMesh = new THREE.Mesh(dwGeo, materials.drivewayPaver);
  dwMesh.rotation.x = -Math.PI / 2;
  dwMesh.position.set(toWorldX(bldgFp.x + bldgFp.width - 7), 0.012, toWorldZ(bldgFp.y / 2));
  dwMesh.receiveShadow = true;
  siteGroup.add(dwMesh);

  // Driveway Edging Curb
  const dwCurbGeo = new THREE.BoxGeometry(dwW + 0.16, 0.03, dwL + 0.16);
  const dwCurbMesh = new THREE.Mesh(dwCurbGeo, materials.extCoping);
  dwCurbMesh.position.set(dwMesh.position.x, 0.01, dwMesh.position.z);
  dwCurbMesh.receiveShadow = true;
  siteGroup.add(dwCurbMesh);

  // Stepping stones / walkway from driveway to entrance
  for (let s = 0; s < 5; s++) {
    const stepMesh = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.03, 0.45), materials.pathwayPaving);
    stepMesh.position.set(
      toWorldX(bldgFp.x + 8) + s * 0.4,
      0.02,
      toWorldZ(bldgFp.y + 3) - s * 0.55
    );
    stepMesh.receiveShadow = true;
    siteGroup.add(stepMesh);
  }

  // Boundary Walls & Gate
  const bwThick = 0.2;
  const bwHeight = 1.35;
  const halfSiteW = siteW / 2;
  const halfSiteL = siteL / 2;

  // Rear Wall
  const rearWallMesh = new THREE.Mesh(new THREE.BoxGeometry(siteW, bwHeight, bwThick), materials.boundaryWall);
  rearWallMesh.position.set(0, bwHeight / 2, -halfSiteL);
  rearWallMesh.castShadow = true;
  siteGroup.add(rearWallMesh);

  // Left Wall
  const leftWallMesh = new THREE.Mesh(new THREE.BoxGeometry(bwThick, bwHeight, siteL), materials.boundaryWall);
  leftWallMesh.position.set(-halfSiteW, bwHeight / 2, 0);
  leftWallMesh.castShadow = true;
  siteGroup.add(leftWallMesh);

  // Right Wall
  const rightWallMesh = new THREE.Mesh(new THREE.BoxGeometry(bwThick, bwHeight, siteL), materials.boundaryWall);
  rightWallMesh.position.set(halfSiteW, bwHeight / 2, 0);
  rightWallMesh.castShadow = true;
  siteGroup.add(rightWallMesh);

  // Front Wall (Split with Entrance Gate)
  const frontWallSegW = (siteW - dwW) / 2;
  const frontWallMesh1 = new THREE.Mesh(new THREE.BoxGeometry(frontWallSegW, bwHeight, bwThick), materials.boundaryWall);
  frontWallMesh1.position.set(-halfSiteW + frontWallSegW / 2, bwHeight / 2, halfSiteL);
  frontWallMesh1.castShadow = true;
  siteGroup.add(frontWallMesh1);

  // Gate Pillars (Piers) with Coping Caps
  const pierW = 0.42;
  const pierH = bwHeight + 0.2;
  const pierGeo = new THREE.BoxGeometry(pierW, pierH, pierW);
  const pierCapGeo = new THREE.BoxGeometry(pierW + 0.08, 0.06, pierW + 0.08);

  const pierL = new THREE.Mesh(pierGeo, materials.boundaryWall);
  pierL.position.set(dwMesh.position.x - dwW / 2 - pierW / 2, pierH / 2, halfSiteL);
  siteGroup.add(pierL);

  const capL = new THREE.Mesh(pierCapGeo, materials.extCoping);
  capL.position.set(pierL.position.x, pierH + 0.03, halfSiteL);
  siteGroup.add(capL);

  const pierR = new THREE.Mesh(pierGeo, materials.boundaryWall);
  pierR.position.set(dwMesh.position.x + dwW / 2 + pierW / 2, pierH / 2, halfSiteL);
  siteGroup.add(pierR);

  const capR = new THREE.Mesh(pierCapGeo, materials.extCoping);
  capR.position.set(pierR.position.x, pierH + 0.03, halfSiteL);
  siteGroup.add(capR);

  // Entrance Slatted Architectural Gate
  const gateW = dwW * 0.96;
  const gateH = bwHeight * 0.92;
  const gateMesh = new THREE.Mesh(new THREE.BoxGeometry(gateW, gateH, 0.06), materials.boundaryGate);
  gateMesh.position.set(dwMesh.position.x, gateH / 2, halfSiteL);
  gateMesh.castShadow = true;
  siteGroup.add(gateMesh);

  // Gate Vertical Louver Accents
  const numLouvers = 12;
  for (let lv = 0; lv < numLouvers; lv++) {
    const louverMesh = new THREE.Mesh(new THREE.BoxGeometry(0.04, gateH * 0.92, 0.08), materials.extTrim);
    louverMesh.position.set(
      dwMesh.position.x - gateW / 2 + (lv + 0.5) * (gateW / numLouvers),
      gateH / 2,
      halfSiteL
    );
    siteGroup.add(louverMesh);
  }

  // Gate Pillar Night Lighting
  if (isNight) {
    const gateLightL = new THREE.PointLight(0xffbe6b, 1.4, 6.0, 1.8);
    gateLightL.position.set(pierL.position.x, pierH + 0.25, halfSiteL - 0.2);
    siteGroup.add(gateLightL);

    const gateLightR = new THREE.PointLight(0xffbe6b, 1.4, 6.0, 1.8);
    gateLightR.position.set(pierR.position.x, pierH + 0.25, halfSiteL - 0.2);
    siteGroup.add(gateLightR);
  }

  rootGroup.add(siteGroup);

  // 5. Build Floor Levels, Rooms, Walls, Slabs, Fenestrations, and Furniture
  const roomAnchors = [];
  const floorsGroup = new THREE.Group();
  floorsGroup.name = 'BuildingFloors';

  plan.floors.forEach((floorObj, floorIdx) => {
    if (floorIdx >= numFloors) return;

    // Floor visibility filter based on currentFloor selection
    const isLevelVisible = currentFloor === 'all' || Number(currentFloor) === floorIdx;
    if (!isLevelVisible) return;

    const floorGroup = new THREE.Group();
    floorGroup.name = `FloorLevel_${floorIdx}_${floorObj.name}`;

    const baseElevation = plinthHeight + floorIdx * floorHeight;
    const isTopLevel = floorIdx === numFloors - 1;

    // ── A. Floor Concrete Base Slab with Architectural Cantilever Overhang ───────
    // Overhang of 0.3m (~1 ft) beyond building perimeter creates depth and shadow line
    const cantilever = 0.32;
    const slabW = toWorldDim(bldgFp.width) + cantilever * 2;
    const slabD = toWorldDim(bldgFp.length) + cantilever * 2;

    const slabMesh = new THREE.Mesh(
      new THREE.BoxGeometry(slabW, slabThick, slabD),
      floorIdx === 0 ? materials.extPlinth : materials.extSlab
    );
    slabMesh.position.set(0, baseElevation - slabThick / 2, 0);
    slabMesh.receiveShadow = true;
    slabMesh.castShadow = true;
    floorGroup.add(slabMesh);

    // Architectural Slab Underside Reveal Band
    if (floorIdx > 0) {
      const slabTrim = new THREE.Mesh(
        new THREE.BoxGeometry(slabW + 0.04, 0.05, slabD + 0.04),
        materials.extTrim
      );
      slabTrim.position.set(0, baseElevation - 0.025, 0);
      floorGroup.add(slabTrim);
    }

    // ── B. Room Slabs & Individual Flooring Assignment ───────────────────────
    floorObj.rooms.forEach((room) => {
      const rw = toWorldDim(room.width);
      const rl = toWorldDim(room.length);
      const rx = toWorldX(room.x + room.width / 2);
      const rz = toWorldZ(room.y + room.length / 2);
      const ry = baseElevation + 0.01;

      // Look up saved interior selection for this specific room:
      // Priority 1: Exact room ID
      // Priority 2: Direct room category without bleeding to unrelated rooms
      const roomTypeClean = (room.type || '').toLowerCase();
      const roomNameClean = (room.label || room.name || '').toLowerCase();

      const savedSel =
        interiorSelections[room.id] ||
        Object.values(interiorSelections).find((s) => {
          if (!s) return false;
          if (s.room_id === room.id) return true;
          const sType = (s.room_type || s.category || '').toLowerCase();
          const sName = (s.room_name || '').toLowerCase();

          // Strict type matching preventing bedroom cross-contamination
          if (roomTypeClean.includes('master') && !sType.includes('master')) return false;
          if (!roomTypeClean.includes('master') && sType.includes('master')) return false;

          if (sType && roomTypeClean && sType === roomTypeClean) return true;
          if (sName && roomNameClean && sName === roomNameClean) return true;
          return false;
        });

      let roomFloorMat = materials.floorVitrified;
      const flooringChoice = savedSel?.flooring_choice;
      const roomType = room.type || '';

      if (flooringChoice === 'italian_marble' || savedSel?.style === 'Luxury') {
        roomFloorMat = materials.floorItalianMarble;
      } else if (
        flooringChoice === 'hardwood_parquet' ||
        roomType.includes('bed') ||
        roomType.includes('study')
      ) {
        roomFloorMat = materials.floorHardwood;
      } else if (roomType.includes('bath')) {
        roomFloorMat = materials.floorBathroomTile;
      } else if (roomType.includes('balcony') || roomType.includes('terrace')) {
        roomFloorMat = materials.floorTerracePaver;
      } else if (roomType.includes('parking')) {
        roomFloorMat = materials.drivewayPaver;
      }

      // Room Floor Mesh
      const roomFloorGeo = new THREE.PlaneGeometry(rw * 0.98, rl * 0.98);
      const roomFloorMesh = new THREE.Mesh(roomFloorGeo, roomFloorMat);
      roomFloorMesh.rotation.x = -Math.PI / 2;
      roomFloorMesh.position.set(rx, ry, rz);
      roomFloorMesh.receiveShadow = true;
      roomFloorMesh.userData = {
        roomId: room.id,
        roomName: room.label || room.name,
        roomType: room.type,
        floorIdx,
        savedSelection: savedSel || null
      };
      floorGroup.add(roomFloorMesh);

      // Walkthrough Room Bounding Box & Camera Navigation Anchor
      const roomBounds = {
        minX: rx - rw * 0.44,
        maxX: rx + rw * 0.44,
        minZ: rz - rl * 0.44,
        maxZ: rz + rl * 0.44,
        minY: ry + 0.8,
        maxY: ry + 2.5,
        eyeLevel: ry + 1.6
      };

      roomAnchors.push({
        id: room.id,
        name: room.label || room.name,
        type: room.type,
        floor: floorIdx,
        floorName: floorObj.name,
        area: room.area,
        center: { x: rx, y: ry, z: rz },
        bounds: roomBounds,
        cameraPos: {
          x: rx - Math.min(rw * 0.35, 1.8),
          y: ry + 1.6,
          z: rz + Math.min(rl * 0.35, 1.8)
        },
        targetPos: {
          x: rx + Math.min(rw * 0.15, 0.6),
          y: ry + 1.0,
          z: rz - Math.min(rl * 0.15, 0.6)
        },
        savedSelection: savedSel || null
      });

      // ── C. Furniture Placement Per Room Category ───────────────────────────
      const furnGroup = new THREE.Group();
      furnGroup.name = `Furniture_${room.id}`;
      furnGroup.position.set(rx, ry, rz);

      if (roomType === 'living_room') {
        // Deep L-Shaped Sectional Sofa
        const sofaBase = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.55, 0.42, rl * 0.35), materials.furnitureFabricDark);
        sofaBase.position.set(0, 0.21, rl * 0.15);
        sofaBase.castShadow = true;
        furnGroup.add(sofaBase);

        const sofaBack = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.55, 0.45, 0.18), materials.furnitureFabricDark);
        sofaBack.position.set(0, 0.45, rl * 0.3);
        sofaBack.castShadow = true;
        furnGroup.add(sofaBack);

        // Toss Cushions (Accent Color)
        [-rw * 0.18, 0, rw * 0.18].forEach((cx) => {
          const cushion = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.25, 0.12), materials.furnitureFabricAccent);
          cushion.position.set(cx, 0.5, rl * 0.22);
          furnGroup.add(cushion);
        });

        // Designer Coffee Table
        const table = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.32, 0.32, rl * 0.2), materials.furnitureWoodWarm);
        table.position.set(0, 0.16, -rl * 0.05);
        table.castShadow = true;
        furnGroup.add(table);

        // Area Rug
        const rug = new THREE.Mesh(new THREE.PlaneGeometry(rw * 0.65, rl * 0.5), materials.furnitureFabricLight);
        rug.rotation.x = -Math.PI / 2;
        rug.position.set(0, 0.015, rl * 0.05);
        furnGroup.add(rug);

        // Media Console / TV Wall Shelf
        const tvConsole = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.6, 0.4, 0.35), materials.furnitureWoodDark);
        tvConsole.position.set(0, 0.2, -rl * 0.42);
        furnGroup.add(tvConsole);

        const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.45, 0.65, 0.04), materials.furnitureCounterGranite);
        tvScreen.position.set(0, 0.95, -rl * 0.44);
        furnGroup.add(tvScreen);
      } else if (roomType.includes('bed')) {
        // King / Queen Bed with Headboard placed against rear wall (Z = -rl / 2)
        const bedW = Math.min(rw * 0.46, 1.95);
        const bedL = Math.min(rl * 0.52, 2.05);

        // Rear wall of room is at -rl / 2
        const headboardThick = 0.12;
        const headboardH = 1.25;
        const headboardZ = -rl / 2 + headboardThick / 2 + 0.04;

        // Upholstered Headboard
        const headboard = new THREE.Mesh(
          new THREE.BoxGeometry(bedW * 1.15, headboardH, headboardThick),
          materials.furnitureFabricDark
        );
        headboard.position.set(0, headboardH / 2, headboardZ);
        headboard.castShadow = true;
        furnGroup.add(headboard);

        // Mattress
        const mattressZ = headboardZ + headboardThick / 2 + bedL / 2;
        const mattress = new THREE.Mesh(new THREE.BoxGeometry(bedW, 0.48, bedL), materials.furnitureFabricLight);
        mattress.position.set(0, 0.24, mattressZ);
        mattress.castShadow = true;
        furnGroup.add(mattress);

        // Bed Area Rug under mattress
        const rugMesh = new THREE.Mesh(new THREE.BoxGeometry(bedW * 1.45, 0.015, bedL * 1.2), materials.furnitureRug || materials.furnitureFabricLight);
        rugMesh.position.set(0, 0.01, mattressZ + 0.1);
        rugMesh.receiveShadow = true;
        furnGroup.add(rugMesh);

        // Duvet / Quilt Runner
        const duvet = new THREE.Mesh(new THREE.BoxGeometry(bedW * 0.96, 0.05, bedL * 0.55), materials.furnitureFabricAccent);
        duvet.position.set(0, 0.49, mattressZ + bedL * 0.18);
        furnGroup.add(duvet);

        // Pillows
        const pillowGeo = new THREE.BoxGeometry(bedW * 0.36, 0.14, 0.38);
        const pillowZ = headboardZ + headboardThick / 2 + 0.26;
        const pillowL = new THREE.Mesh(pillowGeo, materials.furnitureFabricLight);
        pillowL.position.set(-bedW * 0.24, 0.53, pillowZ);
        furnGroup.add(pillowL);

        const pillowR = new THREE.Mesh(pillowGeo, materials.furnitureFabricLight);
        pillowR.position.set(bedW * 0.24, 0.53, pillowZ);
        furnGroup.add(pillowR);

        // Dual Nightstands with Lamps
        const nsW = 0.45;
        const nsH = 0.44;
        const nsD = 0.38;
        const nsZ = headboardZ + headboardThick / 2 + nsD / 2;
        const nsXOffset = bedW / 2 + nsW / 2 + 0.08;

        const nsGeo = new THREE.BoxGeometry(nsW, nsH, nsD);
        const nsL = new THREE.Mesh(nsGeo, materials.furnitureWoodWarm);
        nsL.position.set(-nsXOffset, nsH / 2, nsZ);
        furnGroup.add(nsL);

        const nsR = new THREE.Mesh(nsGeo, materials.furnitureWoodWarm);
        nsR.position.set(nsXOffset, nsH / 2, nsZ);
        furnGroup.add(nsR);

        // Bedside Lamps
        const lampGeo = new THREE.CylinderGeometry(0.08, 0.14, 0.24, 12);
        const lampL = new THREE.Mesh(lampGeo, materials.furnitureFabricLight);
        lampL.position.set(-nsXOffset, nsH + 0.12, nsZ);
        furnGroup.add(lampL);

        const lampR = new THREE.Mesh(lampGeo, materials.furnitureFabricLight);
        lampR.position.set(nsXOffset, nsH + 0.12, nsZ);
        furnGroup.add(lampR);

        // Full-Height Fitted Wardrobe strictly along the side wall (+X)
        // Depth 0.60m along X, length along Z, flush against X = rw/2, completely separated from bed
        const wdrDepth = 0.60;
        const wdrLen = Math.min(rl * 0.44, 2.2);
        const wdrH = wallHeight * 0.88;
        const wdrX = rw / 2 - wdrDepth / 2 - 0.04;
        const wdrZ = rl * 0.12;

        const wardrobe = new THREE.Mesh(new THREE.BoxGeometry(wdrDepth, wdrH, wdrLen), materials.furnitureWardrobeWood);
        wardrobe.position.set(wdrX, wdrH / 2, wdrZ);
        wardrobe.castShadow = true;
        furnGroup.add(wardrobe);

        // Wardrobe chrome handles
        const handleL = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.35, 0.02), materials.furnitureMetalChrome);
        handleL.position.set(wdrX - wdrDepth / 2 - 0.01, wdrH * 0.5, wdrZ - 0.15);
        furnGroup.add(handleL);

        const handleR = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.35, 0.02), materials.furnitureMetalChrome);
        handleR.position.set(wdrX - wdrDepth / 2 - 0.01, wdrH * 0.5, wdrZ + 0.15);
        furnGroup.add(handleR);

        // Media Console / TV Screen on Front Wall (Z = rl / 2)
        const tvConsoleW = Math.min(rw * 0.42, 1.6);
        const tvConsole = new THREE.Mesh(new THREE.BoxGeometry(tvConsoleW, 0.42, 0.35), materials.furnitureWoodDark);
        tvConsole.position.set(0, 0.21, rl / 2 - 0.22);
        furnGroup.add(tvConsole);

        const tvScreen = new THREE.Mesh(new THREE.BoxGeometry(tvConsoleW * 0.85, 0.65, 0.04), materials.furnitureCounterGranite);
        tvScreen.position.set(0, 0.95, rl / 2 - 0.08);
        furnGroup.add(tvScreen);

        // Luxury Master Bedroom End-of-Bed Bench
        if (roomType.includes('master') || rw * rl > 25) {
          const benchW = bedW * 0.85;
          const benchH = 0.40;
          const benchD = 0.42;
          const bench = new THREE.Mesh(new THREE.BoxGeometry(benchW, benchH, benchD), materials.furnitureFabricAccent);
          bench.position.set(0, benchH / 2, mattressZ + bedL / 2 + benchD / 2 + 0.12);
          bench.castShadow = true;
          furnGroup.add(bench);
        }
      } else if (roomType === 'dining_room') {
        // 6-Seater Dining Table
        const dTable = new THREE.Mesh(new THREE.BoxGeometry(rw * 0.52, 0.74, rl * 0.36), materials.furnitureWoodWarm);
        dTable.position.set(0, 0.37, 0);
        dTable.castShadow = true;
        furnGroup.add(dTable);

        // Dining Chairs
        [-rw * 0.2, 0, rw * 0.2].forEach((cx) => {
          const chair1 = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.85, 0.38), materials.furnitureFabricDark);
          chair1.position.set(cx, 0.425, rl * 0.26);
          furnGroup.add(chair1);

          const chair2 = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.85, 0.38), materials.furnitureFabricDark);
          chair2.position.set(cx, 0.425, -rl * 0.26);
          furnGroup.add(chair2);
        });

        // Suspended Dining Pendant Light
        const pendantGeo = new THREE.ConeGeometry(0.25, 0.25, 16);
        const pendant = new THREE.Mesh(pendantGeo, materials.furnitureMetalChrome);
        pendant.position.set(0, wallHeight - 0.7, 0);
        furnGroup.add(pendant);
      } else if (roomType === 'kitchen') {
        // Modular Kitchen Counters with Granite Top
        const counterW = rw * 0.75;
        const counterD = 0.65;
        const counterH = 0.84;

        const counterBase = new THREE.Mesh(new THREE.BoxGeometry(counterW, counterH, counterD), materials.furnitureWoodDark);
        counterBase.position.set(0, counterH / 2, -rl * 0.35);
        furnGroup.add(counterBase);

        const counterTop = new THREE.Mesh(new THREE.BoxGeometry(counterW + 0.04, 0.06, counterD + 0.04), materials.furnitureCounterGranite);
        counterTop.position.set(0, counterH + 0.03, -rl * 0.35);
        furnGroup.add(counterTop);

        // Undermount Sink & Faucet
        const sinkMesh = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.02, 0.4), materials.furnitureMetalChrome);
        sinkMesh.position.set(-counterW * 0.25, counterH + 0.065, -rl * 0.35);
        furnGroup.add(sinkMesh);

        // Overhead Wall Cabinets
        const wallCabH = 0.65;
        const wallCab = new THREE.Mesh(new THREE.BoxGeometry(counterW, wallCabH, 0.38), materials.furnitureWoodWarm);
        wallCab.position.set(0, counterH + 0.8 + wallCabH / 2, -rl * 0.42);
        furnGroup.add(wallCab);
      } else if (roomType.includes('bath')) {
        // Floating Vanity Counter & Ceramic Basin
        const vW = rw * 0.48;
        const vanity = new THREE.Mesh(new THREE.BoxGeometry(vW, 0.45, 0.48), materials.furnitureWoodDark);
        vanity.position.set(0, 0.55, -rl * 0.36);
        furnGroup.add(vanity);

        const basin = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.22, 0.14, 16), materials.furnitureFabricLight);
        basin.position.set(0, 0.84, -rl * 0.36);
        furnGroup.add(basin);

        // Frameless Mirror
        const mirror = new THREE.Mesh(new THREE.PlaneGeometry(vW * 0.85, 0.75), materials.furnitureMirror);
        mirror.position.set(0, 1.45, -rl * 0.36 + 0.25);
        furnGroup.add(mirror);

        // Wall-hung Commode (WC)
        const wcBase = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.4, 0.55), materials.furnitureFabricLight);
        wcBase.position.set(rw * 0.28, 0.2, rl * 0.15);
        furnGroup.add(wcBase);
      } else if (roomType.includes('balcony') || roomType.includes('terrace')) {
        // Balcony Tempered Glass Railing
        const railH = 1.05;
        const railMesh = new THREE.Mesh(new THREE.BoxGeometry(rw, railH, 0.04), materials.glassRailing);
        railMesh.position.set(0, railH / 2, rl / 2);
        furnGroup.add(railMesh);

        // Top Metal Handrail
        const topRailMesh = new THREE.Mesh(new THREE.BoxGeometry(rw * 1.02, 0.06, 0.08), materials.railingMetal);
        topRailMesh.position.set(0, railH + 0.03, rl / 2);
        furnGroup.add(topRailMesh);

        // Corner Posts
        [-rw / 2, rw / 2].forEach((px) => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.06, railH + 0.06, 0.06), materials.railingMetal);
          post.position.set(px, (railH + 0.06) / 2, rl / 2);
          furnGroup.add(post);
        });
      }

      floorGroup.add(furnGroup);

      // ── D. Room Interior Warm Illumination Point Light ─────────────────────
      if (room.space_category !== 'outdoor') {
        const roomLight = new THREE.PointLight(
          new THREE.Color(isNight ? 0xffeaaf : 0xfff7ed),
          isNight ? 1.8 : 0.8,
          Math.max(rw, rl) * 2.5,
          1.8
        );
        roomLight.position.set(rx, ry + wallHeight - 0.2, rz);
        floorGroup.add(roomLight);
      }
    });

    // ── E. Walls Network Construction ─────────────────────────────────────────
    const wallsArray = floorObj.walls || [];
    if (wallsArray.length > 0) {
      wallsArray.forEach((w) => {
        const x1 = toWorldX(w.start.x);
        const z1 = toWorldZ(w.start.y);
        const x2 = toWorldX(w.end.x);
        const z2 = toWorldZ(w.end.y);

        const dx = x2 - x1;
        const dz = z2 - z1;
        const length = Math.sqrt(dx * dx + dz * dz);
        if (length < 0.05) return;

        const angle = Math.atan2(dz, dx);
        const thickness = toWorldDim(w.thickness || (w.type === 'exterior' ? 0.75 : 0.38));

        const wallGeo = new THREE.BoxGeometry(length, wallHeight, thickness);
        const wallMat = w.type === 'exterior' ? materials.extPrimary : materials.intPartitionWall;
        const wallMesh = new THREE.Mesh(wallGeo, wallMat);

        wallMesh.position.set(
          (x1 + x2) / 2,
          baseElevation + wallHeight / 2,
          (z1 + z2) / 2
        );
        wallMesh.rotation.y = -angle;
        wallMesh.castShadow = true;
        wallMesh.receiveShadow = true;
        floorGroup.add(wallMesh);
      });
    }

    // ── Helper: Find Closest Wall for Fenestration Orientation & Thickness ────
    const findClosestWall = (px, pz) => {
      let closest = null;
      let minDistSq = Infinity;
      wallsArray.forEach((w) => {
        const x1 = toWorldX(w.start.x);
        const z1 = toWorldZ(w.start.y);
        const x2 = toWorldX(w.end.x);
        const z2 = toWorldZ(w.end.y);
        const dx = x2 - x1;
        const dz = z2 - z1;
        const lenSq = dx * dx + dz * dz;
        if (lenSq < 0.001) return;
        let t = ((px - x1) * dx + (pz - z1) * dz) / lenSq;
        t = Math.max(0, Math.min(1, t));
        const projX = x1 + t * dx;
        const projZ = z1 + t * dz;
        const dSq = (px - projX) * (px - projX) + (pz - projZ) * (pz - projZ);
        if (dSq < minDistSq) {
          minDistSq = dSq;
          closest = { wall: w, angle: Math.atan2(dz, dx), dist: Math.sqrt(dSq), dx, dz };
        }
      });
      return closest;
    };

    // ── F. Architectural Doors Placement ──────────────────────────────────────
    const doorsArray = floorObj.doors || [];
    doorsArray.forEach((door) => {
      const dw = toWorldDim(door.width || 3.0);
      const isMainDoor = door.type === 'main_entrance';
      const dh = isMainDoor ? 2.4 : 2.1;
      const dx = toWorldX(door.position?.x ?? 0);
      const dz = toWorldZ(door.position?.y ?? 0);
      const dy = baseElevation + dh / 2;

      const closest = findClosestWall(dx, dz);
      const wallAngle = closest && closest.dist < 1.5 ? closest.angle : 0;
      const wallThick = closest?.wall
        ? toWorldDim(closest.wall.thickness || (closest.wall.type === 'exterior' ? 0.75 : 0.38))
        : 0.23;

      const doorGroup = new THREE.Group();
      doorGroup.name = `Door_${door.id}`;
      doorGroup.position.set(dx, dy, dz);
      doorGroup.rotation.y = -wallAngle;

      // Outer Frame (proud of wall by 0.04m so it cleanly trims the opening)
      const fThick = 0.07;
      const frameDepth = wallThick + 0.04;
      const frameGeo = new THREE.BoxGeometry(dw + fThick * 2, dh + fThick, frameDepth);
      const frameMesh = new THREE.Mesh(frameGeo, materials.extWindowFrame);
      frameMesh.position.y = fThick / 2;
      doorGroup.add(frameMesh);

      // Door Leaf
      const leafMat = isMainDoor ? materials.extDoor : materials.intDoorWood;
      const leafGeo = new THREE.BoxGeometry(dw * 0.94, dh * 0.98, 0.06);
      const leafMesh = new THREE.Mesh(leafGeo, leafMat);
      leafMesh.castShadow = true;
      doorGroup.add(leafMesh);

      // Handle Hardware
      const handleGeo = new THREE.CylinderGeometry(0.016, 0.016, isMainDoor ? 0.65 : 0.2, 12);
      const handleMesh = new THREE.Mesh(handleGeo, materials.furnitureMetalChrome);
      handleMesh.position.set(dw * 0.35, 0, frameDepth / 2 + 0.01);
      doorGroup.add(handleMesh);

      // Entrance Porch Canopy & Light (Night)
      if (isMainDoor) {
        const canopyMesh = new THREE.Mesh(
          new THREE.BoxGeometry(dw * 1.35, 0.08, 0.8),
          materials.extAccent
        );
        canopyMesh.position.set(0, dh / 2 + 0.12, 0.4);
        canopyMesh.castShadow = true;
        doorGroup.add(canopyMesh);

        if (isNight) {
          const porchLight = new THREE.PointLight(0xffd17a, 2.2, 8.0, 1.8);
          porchLight.position.set(0, dh / 2 + 0.45, 0.6);
          doorGroup.add(porchLight);

          const sconce = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.08, 0.18, 12), materials.luminaireFixture);
          sconce.position.set(0, dh / 2 + 0.45, 0.2);
          doorGroup.add(sconce);
        }
      }

      floorGroup.add(doorGroup);
    });

    // ── G. Architectural Windows & Glazing ─────────────────────────────────────
    const windowsArray = floorObj.windows || [];
    windowsArray.forEach((win) => {
      const ww = toWorldDim(win.width || 4.0);
      const wh = 1.45;
      const sillH = 0.9;
      const wx = toWorldX(win.position?.x ?? 0);
      const wz = toWorldZ(win.position?.y ?? 0);
      const wy = baseElevation + sillH + wh / 2;

      const closest = findClosestWall(wx, wz);
      const wallAngle = closest && closest.dist < 1.5 ? closest.angle : 0;
      const wallThick = closest?.wall
        ? toWorldDim(closest.wall.thickness || (closest.wall.type === 'exterior' ? 0.75 : 0.38))
        : 0.23;

      const winGroup = new THREE.Group();
      winGroup.name = `Window_${win.id}`;
      winGroup.position.set(wx, wy, wz);
      winGroup.rotation.y = -wallAngle;

      // Outer Window Frame casing — proud of wall by 0.06m to prevent wall occlusion
      const fThick = 0.06;
      const frameDepth = wallThick + 0.06;
      const frameGeo = new THREE.BoxGeometry(ww + fThick * 2, wh + fThick * 2, frameDepth);
      const frameMesh = new THREE.Mesh(frameGeo, materials.extWindowFrame);
      winGroup.add(frameMesh);

      // Projecting Architectural Sill Stone
      const sillGeo = new THREE.BoxGeometry(ww + 0.22, 0.065, frameDepth + 0.08);
      const sillMesh = new THREE.Mesh(sillGeo, materials.extCoping);
      sillMesh.position.set(0, -wh / 2 - 0.03, 0);
      sillMesh.castShadow = true;
      winGroup.add(sillMesh);

      // Projecting Window Lintel Band (Above Frame)
      const lintelGeo = new THREE.BoxGeometry(ww + 0.16, 0.065, frameDepth + 0.04);
      const lintelMesh = new THREE.Mesh(lintelGeo, materials.extAccent);
      lintelMesh.position.set(0, wh / 2 + 0.03, 0);
      winGroup.add(lintelMesh);

      // Window Glass (Transparent in Day, Warm Luminous in Night)
      const glassMat = isNight ? materials.extGlassNight : materials.extGlass;
      const glassGeo = new THREE.BoxGeometry(ww * 0.96, wh * 0.96, 0.025);
      const glassMesh = new THREE.Mesh(glassGeo, glassMat);
      winGroup.add(glassMesh);

      // Central Vertical Mullion
      const mullion = new THREE.Mesh(new THREE.BoxGeometry(0.045, wh, frameDepth * 0.75), materials.extWindowFrame);
      winGroup.add(mullion);

      floorGroup.add(winGroup);
    });

    // ── H. Stairs Core (Connecting Ground to Upper Level) ─────────────────────
    if (floorObj.stairs && floorObj.stairs.length > 0) {
      floorObj.stairs.forEach((stair) => {
        const sx = toWorldX(stair.x + stair.width / 2);
        const sz = toWorldZ(stair.y + stair.length / 2);
        const sw = toWorldDim(stair.width);
        const sl = toWorldDim(stair.length);

        const numSteps = 16;
        const stepH = floorHeight / numSteps;
        const stepD = (sl * 0.85) / (numSteps / 2);

        for (let i = 0; i < numSteps / 2; i++) {
          const stepGeo = new THREE.BoxGeometry(sw * 0.45, (i + 1) * stepH, stepD);
          const stepMesh = new THREE.Mesh(stepGeo, materials.extSlab);
          stepMesh.position.set(
            sx - sw * 0.25,
            baseElevation + ((i + 1) * stepH) / 2,
            sz - sl * 0.4 + i * stepD
          );
          stepMesh.castShadow = true;
          floorGroup.add(stepMesh);
        }
      });
    }

    // ── I. Top Parapet & Roof Slab with Coping Stones ─────────────────────────
    if (currentFloor === 'all' && isTopLevel) {
      const roofY = baseElevation + wallHeight + slabThick / 2;
      const roofMesh = new THREE.Mesh(new THREE.BoxGeometry(slabW * 1.02, slabThick, slabD * 1.02), materials.extSlab);
      roofMesh.position.set(0, roofY, 0);
      roofMesh.castShadow = true;
      floorGroup.add(roofMesh);

      // Roof terrace paver flooring surface
      const terraceDeck = new THREE.Mesh(
        new THREE.PlaneGeometry(slabW * 0.96, slabD * 0.96),
        materials.floorTerracePaver
      );
      terraceDeck.rotation.x = -Math.PI / 2;
      terraceDeck.position.set(0, roofY + slabThick / 2 + 0.005, 0);
      floorGroup.add(terraceDeck);

      // Parapet perimeter
      const parapetH = 0.85;
      const pThick = 0.24;
      const halfW = (slabW * 1.0) / 2;
      const halfD = (slabD * 1.0) / 2;

      // Parapet Walls using extPrimary (seamless building facade)
      const pFront = new THREE.Mesh(new THREE.BoxGeometry(slabW * 1.0, parapetH, pThick), materials.extPrimary);
      pFront.position.set(0, roofY + parapetH / 2, halfD - pThick / 2);
      floorGroup.add(pFront);

      const pBack = new THREE.Mesh(new THREE.BoxGeometry(slabW * 1.0, parapetH, pThick), materials.extPrimary);
      pBack.position.set(0, roofY + parapetH / 2, -halfD + pThick / 2);
      floorGroup.add(pBack);

      const pLeft = new THREE.Mesh(new THREE.BoxGeometry(pThick, parapetH, slabD * 1.0), materials.extPrimary);
      pLeft.position.set(-halfW + pThick / 2, roofY + parapetH / 2, 0);
      floorGroup.add(pLeft);

      const pRight = new THREE.Mesh(new THREE.BoxGeometry(pThick, parapetH, slabD * 1.0), materials.extPrimary);
      pRight.position.set(halfW - pThick / 2, roofY + parapetH / 2, 0);
      floorGroup.add(pRight);

      // Parapet Accent Reveal Band (Horizontal design groove / frieze under coping)
      const friezeH = 0.12;
      const friezeTrim = new THREE.Mesh(
        new THREE.BoxGeometry(slabW * 1.01, friezeH, slabD * 1.01),
        materials.extAccent
      );
      friezeTrim.position.set(0, roofY + parapetH - friezeH / 2, 0);
      floorGroup.add(friezeTrim);

      // Parapet Coping Stones (Extending 0.04m beyond parapet edge)
      const capH = 0.06;
      const capThick = pThick + 0.08;
      const capMat = materials.extCoping;

      const capFront = new THREE.Mesh(new THREE.BoxGeometry(slabW * 1.0 + 0.08, capH, capThick), capMat);
      capFront.position.set(0, roofY + parapetH + capH / 2, halfD - pThick / 2);
      floorGroup.add(capFront);

      const capBack = new THREE.Mesh(new THREE.BoxGeometry(slabW * 1.0 + 0.08, capH, capThick), capMat);
      capBack.position.set(0, roofY + parapetH + capH / 2, -halfD + pThick / 2);
      floorGroup.add(capBack);

      const capLeft = new THREE.Mesh(new THREE.BoxGeometry(capThick, capH, slabD * 1.0), capMat);
      capLeft.position.set(-halfW + pThick / 2, roofY + parapetH + capH / 2, 0);
      floorGroup.add(capLeft);

      const capRight = new THREE.Mesh(new THREE.BoxGeometry(capThick, capH, slabD * 1.0), capMat);
      capRight.position.set(halfW - pThick / 2, roofY + parapetH + capH / 2, 0);
      floorGroup.add(capRight);
    }

    floorsGroup.add(floorGroup);
  });

  rootGroup.add(floorsGroup);
  rootGroup.userData = { roomAnchors };

  return {
    model: rootGroup,
    roomAnchors,
    plan,
    materials
  };
}
