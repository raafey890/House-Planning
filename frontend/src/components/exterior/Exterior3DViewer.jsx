import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  Sun,
  Moon,
  Camera,
  RotateCw,
  RotateCcw,
  Sparkles
} from 'lucide-react';

/**
 * Exterior3DViewer — Phase 6G.3
 *
 * Professional Dimension-Grounded Architectural 3D House Model.
 * Features:
 * - High-speed material color updates (in-place GPU buffer updates, zero geometry thrashing)
 * - Balanced architectural lighting: Hemisphere skylight + directional sunlight + soft fill
 * - Zero self-shadow acne (tuned normalBias and shadow bias)
 * - Luminous night atmosphere with 2700K glowing interior windows and warm facade accents
 * - Responsive non-overlapping top toolbar with Camera presets, Day/Night, Turntable, Reset & Snapshot
 * - Accurate representation across all 12 customizable components
 */
const Exterior3DViewer = ({
  project,
  selectedDesign,
  customColors,
  customMaterials,
  lightingMode = 'daylight',
  onToggleLighting,
  className = ''
}) => {
  const mountRef = useRef(null);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const animFrameRef = useRef(null);
  const houseGroupRef = useRef(null);
  const lightsRef = useRef({});
  const materialsRef = useRef({});

  const [isNight, setIsNight] = useState(lightingMode === 'night');
  const [isRotating, setIsRotating] = useState(false);
  const [activePreset, setActivePreset] = useState('front_left');

  // Sync internal night state with prop
  useEffect(() => {
    setIsNight(lightingMode === 'night');
  }, [lightingMode]);

  // Project dimensions
  const plotW = Number(project?.plot_width) || 30;
  const plotL = Number(project?.plot_length) || 40;
  const floors = Number(project?.floors) || 2;
  const facing = project?.facing || 'North';

  // Architectural category
  const category = selectedDesign?.category || 'modern_contemporary';
  const isTraditionalOrClay =
    category === 'traditional_indian' || category === 'mediterranean';
  const isMinimal = category === 'minimalist';
  const isLuxury = category === 'luxury_villa';
  const isIndianModern = category === 'indian_modern';

  // Helper to validate and clean hex
  const safeHex = (hex, fallback) => {
    if (!hex || typeof hex !== 'string') return fallback;
    const clean = hex.trim();
    return /^[0-9A-Fa-f]{3}$|^[0-9A-Fa-f]{6}$|^#[0-9A-Fa-f]{3}$|^#[0-9A-Fa-f]{6}$/.test(clean)
      ? (clean.startsWith('#') ? clean : `#${clean}`)
      : fallback;
  };

  // ── 1. Initialize Three.js Scene, Camera, Renderer, Controls & Lighting ──
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 520;

    // 1. Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(isNight ? 0x0a0f1d : 0xe6f0fa);
    sceneRef.current = scene;

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    cameraRef.current = camera;

    // 3. Renderer with high dynamic range tone mapping & sRGB output
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      preserveDrawingBuffer: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.3;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 6;
    controls.maxDistance = 75;
    controls.maxPolarAngle = Math.PI / 2 - 0.02; // Prevent clipping under site plinth
    controlsRef.current = controls;

    // 5. Balanced Architectural Lighting System (Natural Sunlight + Skylight Bounce)
    // 5a. Ambient & Hemisphere Light (Skylight + Ground bounce)
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x64748b, 1.4);
    hemiLight.position.set(0, 50, 0);
    scene.add(hemiLight);

    // 5b. Primary Directional Sunlight
    const dirLight = new THREE.DirectionalLight(0xfffaed, 2.2);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 120;
    dirLight.shadow.camera.left = -22;
    dirLight.shadow.camera.right = 22;
    dirLight.shadow.camera.top = 22;
    dirLight.shadow.camera.bottom = -22;
    // Eliminates self-shadow acne on walls:
    dirLight.shadow.bias = -0.00005;
    dirLight.shadow.normalBias = 0.04;
    dirLight.position.set(20, 30, 22);
    scene.add(dirLight);

    // 5c. Secondary Fill Light (Soft counter-angle sky reflection)
    const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.9);
    fillLight.position.set(-22, 18, -16);
    scene.add(fillLight);

    // 5d. Warm Entrance Porch Sconce (Night illumination)
    const porchLight = new THREE.PointLight(0xffd166, isNight ? 3.5 : 0, 12);
    porchLight.position.set(0, 3.2, 5.5);
    porchLight.castShadow = true;
    scene.add(porchLight);

    // 5e. Facade Grazer Spotlight (Night illumination)
    const facadeSpot = new THREE.SpotLight(0xffb703, isNight ? 4.0 : 0, 16, Math.PI / 4, 0.4, 1.2);
    facadeSpot.position.set(-3.5, 0.3, 5.5);
    facadeSpot.target.position.set(-3.5, 6, 4);
    scene.add(facadeSpot);
    scene.add(facadeSpot.target);

    lightsRef.current = { hemiLight, dirLight, fillLight, porchLight, facadeSpot };

    // 6. Site Ground & Landscaping Plinth
    const groundGeo = new THREE.PlaneGeometry(70, 70);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x1f2937,
      roughness: 0.9,
      metalness: 0.05
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Paved Plot Plinth (reflects project dimensions)
    const plotScale = 0.32;
    const siteW = Math.max(plotW * plotScale, 9);
    const siteL = Math.max(plotL * plotScale, 11);

    const plinthGeo = new THREE.BoxGeometry(siteW + 1.2, 0.3, siteL + 1.2);
    const plinthMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      roughness: 0.85
    });
    const plinth = new THREE.Mesh(plinthGeo, plinthMat);
    plinth.position.y = 0.15;
    plinth.receiveShadow = true;
    scene.add(plinth);

    // Paved Stone Walkway / Driveway
    const driveGeo = new THREE.BoxGeometry(siteW * 0.42, 0.02, siteL * 0.48);
    const driveMat = new THREE.MeshStandardMaterial({
      color: 0x475569,
      roughness: 0.7
    });
    const drive = new THREE.Mesh(driveGeo, driveMat);
    drive.position.set(siteW * 0.22, 0.31, siteL * 0.25);
    drive.receiveShadow = true;
    scene.add(drive);

    // Set Initial Camera Position (3/4 front-left perspective)
    const houseCenterY = (floors * 2.85) / 2;
    camera.position.set(-16, houseCenterY + 7, 19);
    controls.target.set(0, houseCenterY, 0);
    controls.update();

    // Resize Observer / Window Resize Handler
    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    // Render Loop
    const animate = () => {
      animFrameRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // ── 2. Update Lighting Between Daylight and Night Mode ───────────────────
  useEffect(() => {
    const scene = sceneRef.current;
    const { hemiLight, dirLight, fillLight, porchLight, facadeSpot } = lightsRef.current;
    if (!scene || !dirLight) return;

    if (isNight) {
      // Twilight Night Scene
      scene.background = new THREE.Color(0x0a0f1d);
      if (hemiLight) {
        hemiLight.color.setHex(0x38bdf8);
        hemiLight.groundColor.setHex(0x0f172a);
        hemiLight.intensity = 0.75;
      }
      dirLight.color.setHex(0x93c5fd);
      dirLight.intensity = 0.85;
      dirLight.position.set(-16, 24, 16);

      if (fillLight) {
        fillLight.color.setHex(0x1e293b);
        fillLight.intensity = 0.35;
      }
      if (porchLight) porchLight.intensity = 3.5;
      if (facadeSpot) facadeSpot.intensity = 4.0;
    } else {
      // Crisp Natural Daylight
      scene.background = new THREE.Color(0xe6f0fa);
      if (hemiLight) {
        hemiLight.color.setHex(0xffffff);
        hemiLight.groundColor.setHex(0x64748b);
        hemiLight.intensity = 1.4;
      }
      dirLight.color.setHex(0xfffaed);
      dirLight.intensity = 2.2;
      dirLight.position.set(20, 30, 22);

      if (fillLight) {
        fillLight.color.setHex(0xdbeafe);
        fillLight.intensity = 0.9;
      }
      if (porchLight) porchLight.intensity = 0;
      if (facadeSpot) facadeSpot.intensity = 0;
    }

    if (rendererRef.current && sceneRef.current && cameraRef.current) {
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    }
  }, [isNight]);

  // ── 3. Auto-rotation Control ─────────────────────────────────────────────
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = isRotating;
      controlsRef.current.autoRotateSpeed = 2.2;
    }
  }, [isRotating]);

  // ── 4. Build / Rebuild House Geometry (Only on Structural Changes) ───────
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;

    // Dispose old house group
    if (houseGroupRef.current) {
      scene.remove(houseGroupRef.current);
      houseGroupRef.current.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
      });
    }

    const houseGroup = new THREE.Group();
    houseGroupRef.current = houseGroup;

    // Dimensional scaling
    const plotScale = 0.32;
    const bldgW = Math.max(plotW * plotScale * 0.74, 6.5);
    const bldgD = Math.max(plotL * plotScale * 0.65, 7.5);
    const floorH = 2.85;
    const numFloors = Math.min(Math.max(floors, 1), 3);

    // Create & Register 12 Dedicated Standard Materials in Ref
    const mats = {
      primary_wall: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.primary_wall, '#F4F4F0')),
        roughness: isMinimal ? 0.95 : 0.85,
        metalness: 0.05
      }),
      secondary_wall: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.secondary_wall, '#E5E7EB')),
        roughness: 0.85,
        metalness: 0.05
      }),
      accent_wall: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.accent_wall, '#2B313B')),
        roughness: 0.6,
        metalness: isLuxury ? 0.25 : 0.1
      }),
      front_facade: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.front_facade || customColors?.primary_wall, '#F4F4F0')),
        roughness: 0.55,
        metalness: 0.15
      }),
      boundary_wall: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.boundary_wall, '#E5E0D6')),
        roughness: 0.85,
        metalness: 0.03
      }),
      boundary_gate: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.boundary_gate, '#30343B')),
        roughness: 0.35,
        metalness: 0.75
      }),
      door: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.door, '#8B5A2B')),
        roughness: 0.45,
        metalness: 0.15
      }),
      window_frame: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.window_frame, '#20252B')),
        roughness: 0.35,
        metalness: 0.6
      }),
      window_glass_tint: new THREE.MeshStandardMaterial({
        color: isNight ? 0xfff3a0 : new THREE.Color(safeHex(customColors?.window_glass_tint, '#7DD3FC')),
        emissive: isNight ? 0xf59e0b : 0x000000,
        emissiveIntensity: isNight ? 2.4 : 0.0,
        roughness: 0.1,
        metalness: 0.85,
        transparent: true,
        opacity: isNight ? 0.95 : 0.65
      }),
      railing: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.railing, '#1F2937')),
        roughness: 0.3,
        metalness: 0.7
      }),
      roof_parapet: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.roof_parapet, '#343A40')),
        roughness: 0.75,
        metalness: 0.05
      }),
      exterior_trims: new THREE.MeshStandardMaterial({
        color: new THREE.Color(safeHex(customColors?.exterior_trims, '#20252B')),
        roughness: 0.4,
        metalness: 0.5
      })
    };
    materialsRef.current = mats;

    const concreteSlabMat = new THREE.MeshStandardMaterial({
      color: 0xd6d3d1,
      roughness: 0.8
    });

    // ── Build Each Floor Massing ──────────────────────────────────────────
    for (let f = 0; f < numFloors; f++) {
      const floorBaseY = 0.3 + f * floorH;
      const isGround = f === 0;

      // Cantilever projection on upper floors for modern / duplex
      const cantileverZ = !isGround && !isTraditionalOrClay ? 0.6 : 0;
      const fWidth = !isGround && isMinimal ? bldgW * 0.95 : bldgW;
      const fDepth = bldgD;

      // 1. Primary Wall Mass
      const wallGeo = new THREE.BoxGeometry(fWidth, floorH, fDepth);
      const wallMesh = new THREE.Mesh(wallGeo, mats.primary_wall);
      wallMesh.userData = { componentId: 'primary_wall' };
      wallMesh.position.set(0, floorBaseY + floorH / 2, cantileverZ / 2);
      wallMesh.castShadow = true;
      wallMesh.receiveShadow = true;
      houseGroup.add(wallMesh);

      // 2. Secondary Wall Mass (Side Flank / Rear Wing Return)
      const sideWallGeo = new THREE.BoxGeometry(0.12, floorH * 0.98, fDepth * 0.7);
      const sideWallMesh = new THREE.Mesh(sideWallGeo, mats.secondary_wall);
      sideWallMesh.userData = { componentId: 'secondary_wall' };
      sideWallMesh.position.set(fWidth / 2 + 0.05, floorBaseY + floorH / 2, -fDepth * 0.1);
      sideWallMesh.castShadow = true;
      houseGroup.add(sideWallMesh);

      // 3. Accent Feature Cladding (Left vertical column)
      const accentGeo = new THREE.BoxGeometry(fWidth * 0.32, floorH + 0.02, 0.18);
      const accentMesh = new THREE.Mesh(accentGeo, mats.accent_wall);
      accentMesh.userData = { componentId: 'accent_wall' };
      accentMesh.position.set(
        -fWidth * 0.32,
        floorBaseY + floorH / 2,
        fDepth / 2 + cantileverZ / 2 + 0.08
      );
      accentMesh.castShadow = true;
      houseGroup.add(accentMesh);

      // 4. Front Facade Architectural Portal Surround
      const facadePortalGeo = new THREE.BoxGeometry(fWidth * 0.42, 0.16, 0.25);
      const facadePortalMesh = new THREE.Mesh(facadePortalGeo, mats.front_facade);
      facadePortalMesh.userData = { componentId: 'front_facade' };
      facadePortalMesh.position.set(
        fWidth * 0.15,
        floorBaseY + floorH - 0.08,
        fDepth / 2 + cantileverZ / 2 + 0.12
      );
      facadePortalMesh.castShadow = true;
      houseGroup.add(facadePortalMesh);

      // If Indian Modern: Add terracotta jaali screen element
      if (isIndianModern) {
        const jaaliGeo = new THREE.BoxGeometry(fWidth * 0.26, floorH * 0.85, 0.1);
        const jaaliMat = new THREE.MeshStandardMaterial({
          color: 0xb85333,
          roughness: 0.9
        });
        const jaaliMesh = new THREE.Mesh(jaaliGeo, jaaliMat);
        jaaliMesh.position.set(
          -fWidth * 0.32,
          floorBaseY + floorH / 2,
          fDepth / 2 + cantileverZ / 2 + 0.18
        );
        houseGroup.add(jaaliMesh);
      }

      // Ground Floor Entrance & Windows
      if (isGround) {
        // Main Entrance Door
        const doorGeo = new THREE.BoxGeometry(1.2, 2.2, 0.15);
        const doorMesh = new THREE.Mesh(doorGeo, mats.door);
        doorMesh.userData = { componentId: 'door' };
        doorMesh.position.set(fWidth * 0.15, floorBaseY + 1.1, fDepth / 2 + 0.08);
        doorMesh.castShadow = true;
        houseGroup.add(doorMesh);

        // Entrance Portico Canopy (Exterior Trims)
        const canopyGeo = new THREE.BoxGeometry(2.4, 0.15, 1.6);
        const canopyMesh = new THREE.Mesh(canopyGeo, mats.exterior_trims);
        canopyMesh.userData = { componentId: 'exterior_trims' };
        canopyMesh.position.set(fWidth * 0.15, floorBaseY + 2.3, fDepth / 2 + 0.8);
        canopyMesh.castShadow = true;
        houseGroup.add(canopyMesh);

        // Ground Floor Panoramic Picture Window
        const winGeo = new THREE.BoxGeometry(2.0, 1.6, 0.1);
        const winMesh = new THREE.Mesh(winGeo, mats.window_glass_tint);
        winMesh.userData = { componentId: 'window_glass_tint' };
        winMesh.position.set(fWidth * 0.28, floorBaseY + 1.25, fDepth / 2 + 0.06);
        houseGroup.add(winMesh);

        // Window Frame
        const frameGeo = new THREE.BoxGeometry(2.1, 1.7, 0.08);
        const frameMesh = new THREE.Mesh(frameGeo, mats.window_frame);
        frameMesh.userData = { componentId: 'window_frame' };
        frameMesh.position.set(fWidth * 0.28, floorBaseY + 1.25, fDepth / 2 + 0.04);
        houseGroup.add(frameMesh);
      } else {
        // Upper Floor Large Window
        const winGeo = new THREE.BoxGeometry(fWidth * 0.45, 1.9, 0.1);
        const winMesh = new THREE.Mesh(winGeo, mats.window_glass_tint);
        winMesh.userData = { componentId: 'window_glass_tint' };
        winMesh.position.set(fWidth * 0.18, floorBaseY + 1.2, fDepth / 2 + cantileverZ / 2 + 0.06);
        houseGroup.add(winMesh);

        // Upper Window Frame
        const upperFrameGeo = new THREE.BoxGeometry(fWidth * 0.46, 2.0, 0.08);
        const upperFrameMesh = new THREE.Mesh(upperFrameGeo, mats.window_frame);
        upperFrameMesh.userData = { componentId: 'window_frame' };
        upperFrameMesh.position.set(fWidth * 0.18, floorBaseY + 1.2, fDepth / 2 + cantileverZ / 2 + 0.04);
        houseGroup.add(upperFrameMesh);

        // Balcony Slab
        const balcSlabGeo = new THREE.BoxGeometry(fWidth * 0.52, 0.2, 1.2);
        const balcSlab = new THREE.Mesh(balcSlabGeo, concreteSlabMat);
        balcSlab.position.set(fWidth * 0.18, floorBaseY + 0.1, fDepth / 2 + cantileverZ / 2 + 0.6);
        balcSlab.castShadow = true;
        balcSlab.receiveShadow = true;
        houseGroup.add(balcSlab);

        // Balcony Railing
        const railGeo = new THREE.BoxGeometry(fWidth * 0.5, 0.95, 0.05);
        const railMesh = new THREE.Mesh(railGeo, mats.railing);
        railMesh.userData = { componentId: 'railing' };
        railMesh.position.set(fWidth * 0.18, floorBaseY + 0.65, fDepth / 2 + cantileverZ / 2 + 1.15);
        houseGroup.add(railMesh);
      }

      // Side Windows & Frames
      const sideWinGeo = new THREE.BoxGeometry(0.1, 1.4, 1.6);
      const sideWin = new THREE.Mesh(sideWinGeo, mats.window_glass_tint);
      sideWin.userData = { componentId: 'window_glass_tint' };
      sideWin.position.set(fWidth / 2 + 0.04, floorBaseY + 1.3, 0);
      houseGroup.add(sideWin);

      const sideFrameGeo = new THREE.BoxGeometry(0.08, 1.5, 1.7);
      const sideFrame = new THREE.Mesh(sideFrameGeo, mats.window_frame);
      sideFrame.userData = { componentId: 'window_frame' };
      sideFrame.position.set(fWidth / 2 + 0.03, floorBaseY + 1.3, 0);
      houseGroup.add(sideFrame);
    }

    // ── Roof Level ────────────────────────────────────────────────────────
    const totalBuildingH = 0.3 + numFloors * floorH;

    if (isTraditionalOrClay) {
      // Sloping Pitched Clay Tile Roof
      const roofH = 1.9;
      const roofOverhang = 0.8;
      const roofGeo = new THREE.ConeGeometry(
        Math.hypot(bldgW + roofOverhang, bldgD + roofOverhang) * 0.42,
        roofH,
        4
      );
      roofGeo.rotateY(Math.PI / 4);
      const roofMesh = new THREE.Mesh(roofGeo, mats.roof_parapet);
      roofMesh.userData = { componentId: 'roof_parapet' };
      roofMesh.position.set(0, totalBuildingH + roofH / 2, 0);
      roofMesh.castShadow = true;
      houseGroup.add(roofMesh);
    } else {
      // Modern Terrace with Parapet
      const parapetGeo = new THREE.BoxGeometry(bldgW + 0.2, 0.8, bldgD + 0.2);
      const parapetMesh = new THREE.Mesh(parapetGeo, mats.roof_parapet);
      parapetMesh.userData = { componentId: 'roof_parapet' };
      parapetMesh.position.set(0, totalBuildingH + 0.4, 0);
      parapetMesh.castShadow = true;
      houseGroup.add(parapetMesh);

      // Terrace Core
      const terraceCoreGeo = new THREE.BoxGeometry(bldgW - 0.4, 0.82, bldgD - 0.4);
      const terraceCoreMat = new THREE.MeshStandardMaterial({
        color: 0x94a3b8,
        roughness: 0.9
      });
      const terraceCore = new THREE.Mesh(terraceCoreGeo, terraceCoreMat);
      terraceCore.position.set(0, totalBuildingH + 0.42, 0);
      houseGroup.add(terraceCore);

      // Architectural Modern Pergola
      const pergolaGeo = new THREE.BoxGeometry(bldgW * 0.4, 0.15, bldgD * 0.35);
      const pergolaMesh = new THREE.Mesh(pergolaGeo, mats.exterior_trims);
      pergolaMesh.userData = { componentId: 'exterior_trims' };
      pergolaMesh.position.set(bldgW * 0.2, totalBuildingH + 1.8, -bldgD * 0.15);
      pergolaMesh.castShadow = true;
      houseGroup.add(pergolaMesh);

      const colGeo = new THREE.BoxGeometry(0.12, 1.8, 0.12);
      const col1 = new THREE.Mesh(colGeo, mats.exterior_trims);
      col1.userData = { componentId: 'exterior_trims' };
      col1.position.set(bldgW * 0.38, totalBuildingH + 0.9, -bldgD * 0.3);
      houseGroup.add(col1);
    }

    // ── Boundary Wall & Front Gate ─────────────────────────────────────────
    const wallHeight = 1.1;
    const boundaryThick = 0.18;
    const frontWallZ = (plotL * plotScale) / 2 + 0.3;

    const leftWallGeo = new THREE.BoxGeometry(bldgW * 0.35, wallHeight, boundaryThick);
    const leftWall = new THREE.Mesh(leftWallGeo, mats.boundary_wall);
    leftWall.userData = { componentId: 'boundary_wall' };
    leftWall.position.set(-bldgW * 0.32, wallHeight / 2 + 0.3, frontWallZ);
    leftWall.castShadow = true;
    houseGroup.add(leftWall);

    const rightWallGeo = new THREE.BoxGeometry(bldgW * 0.2, wallHeight, boundaryThick);
    const rightWall = new THREE.Mesh(rightWallGeo, mats.boundary_wall);
    rightWall.userData = { componentId: 'boundary_wall' };
    rightWall.position.set(bldgW * 0.4, wallHeight / 2 + 0.3, frontWallZ);
    rightWall.castShadow = true;
    houseGroup.add(rightWall);

    const gateGeo = new THREE.BoxGeometry(bldgW * 0.36, wallHeight * 0.9, 0.06);
    const gateMesh = new THREE.Mesh(gateGeo, mats.boundary_gate);
    gateMesh.userData = { componentId: 'boundary_gate' };
    gateMesh.position.set(bldgW * 0.08, wallHeight * 0.45 + 0.3, frontWallZ);
    gateMesh.castShadow = true;
    houseGroup.add(gateMesh);

    scene.add(houseGroup);
  }, [plotW, plotL, floors, category]);

  // ── 5. Instant In-Place Material Color & Finish Synchronization ──────────
  // Runs immediately when customColors or customMaterials change without rebuilding geometry!
  useEffect(() => {
    if (!materialsRef.current || Object.keys(materialsRef.current).length === 0) return;
    const mats = materialsRef.current;
    if (typeof window !== 'undefined') {
      window.__exteriorViewerMaterials = mats;
    }

    // Apply Colors
    if (mats.primary_wall) {
      mats.primary_wall.color.set(safeHex(customColors?.primary_wall, '#F4F4F0'));
      mats.primary_wall.needsUpdate = true;
    }
    if (mats.secondary_wall) {
      mats.secondary_wall.color.set(safeHex(customColors?.secondary_wall, '#E5E7EB'));
      mats.secondary_wall.needsUpdate = true;
    }
    if (mats.accent_wall) {
      mats.accent_wall.color.set(safeHex(customColors?.accent_wall, '#2B313B'));
      mats.accent_wall.needsUpdate = true;
    }
    if (mats.front_facade) {
      mats.front_facade.color.set(safeHex(customColors?.front_facade || customColors?.primary_wall, '#F4F4F0'));
      mats.front_facade.needsUpdate = true;
    }
    if (mats.boundary_wall) {
      mats.boundary_wall.color.set(safeHex(customColors?.boundary_wall, '#E5E0D6'));
      mats.boundary_wall.needsUpdate = true;
    }
    if (mats.boundary_gate) {
      mats.boundary_gate.color.set(safeHex(customColors?.boundary_gate, '#30343B'));
      mats.boundary_gate.needsUpdate = true;
    }
    if (mats.door) {
      mats.door.color.set(safeHex(customColors?.door, '#8B5A2B'));
      mats.door.needsUpdate = true;
    }
    if (mats.window_frame) {
      mats.window_frame.color.set(safeHex(customColors?.window_frame, '#20252B'));
      mats.window_frame.needsUpdate = true;
    }
    if (mats.railing) {
      mats.railing.color.set(safeHex(customColors?.railing, '#1F2937'));
      mats.railing.needsUpdate = true;
    }
    if (mats.roof_parapet) {
      mats.roof_parapet.color.set(safeHex(customColors?.roof_parapet, '#343A40'));
      mats.roof_parapet.needsUpdate = true;
    }
    if (mats.exterior_trims) {
      mats.exterior_trims.color.set(safeHex(customColors?.exterior_trims, '#20252B'));
      mats.exterior_trims.needsUpdate = true;
    }

    // Window Glass with Night mode emission
    if (mats.window_glass_tint) {
      if (isNight) {
        mats.window_glass_tint.color.setHex(0xfff3a0);
        mats.window_glass_tint.emissive.setHex(0xf59e0b);
        mats.window_glass_tint.emissiveIntensity = 2.4;
        mats.window_glass_tint.opacity = 0.95;
      } else {
        mats.window_glass_tint.color.set(safeHex(customColors?.window_glass_tint, '#7DD3FC'));
        mats.window_glass_tint.emissive.setHex(0x000000);
        mats.window_glass_tint.emissiveIntensity = 0.0;
        mats.window_glass_tint.opacity = 0.65;
      }
      mats.window_glass_tint.needsUpdate = true;
    }

    // Material finish properties (roughness & metalness)
    const fType = customMaterials?.finish_type || 'matte_paint';
    let finishRoughness = 0.85;
    let finishMetalness = 0.05;
    if (fType === 'smooth_acrylic') { finishRoughness = 0.55; finishMetalness = 0.05; }
    else if (fType === 'textured_grit') { finishRoughness = 0.98; finishMetalness = 0.02; }
    else if (fType === 'board_concrete') { finishRoughness = 0.90; finishMetalness = 0.08; }
    else if (fType === 'laterite_stone') { finishRoughness = 0.92; finishMetalness = 0.04; }
    else if (fType === 'dholpur_sandstone') { finishRoughness = 0.88; finishMetalness = 0.05; }
    else if (fType === 'limestone_wash') { finishRoughness = 0.96; finishMetalness = 0.0; }
    else if (fType === 'fluted_battens') { finishRoughness = 0.60; finishMetalness = 0.15; }

    if (mats.primary_wall) {
      mats.primary_wall.roughness = finishRoughness;
      mats.primary_wall.metalness = finishMetalness;
      mats.primary_wall.needsUpdate = true;
    }
    if (mats.secondary_wall) {
      mats.secondary_wall.roughness = finishRoughness;
      mats.secondary_wall.metalness = finishMetalness;
      mats.secondary_wall.needsUpdate = true;
    }

    // Force instantaneous repaint
    if (rendererRef.current && sceneRef.current && cameraRef.current) {
      rendererRef.current.render(sceneRef.current, cameraRef.current);
    }
  }, [customColors, customMaterials, isNight]);

  // ── 6. Camera Presets ────────────────────────────────────────────────────
  const setCameraPreset = (preset) => {
    setActivePreset(preset);
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    if (!camera || !controls) return;

    const houseCenterY = (floors * 2.85) / 2;

    switch (preset) {
      case 'front':
        camera.position.set(0, houseCenterY + 1.0, 24);
        controls.target.set(0, houseCenterY, 0);
        break;
      case 'front_left':
        camera.position.set(-16, houseCenterY + 7, 19);
        controls.target.set(0, houseCenterY, 0);
        break;
      case 'front_right':
        camera.position.set(16, houseCenterY + 7, 19);
        controls.target.set(0, houseCenterY, 0);
        break;
      case 'top':
        camera.position.set(0, 32, 10);
        controls.target.set(0, 0, 0);
        break;
      default:
        break;
    }
    controls.update();
  };

  // ── 7. Snapshot PNG Download ─────────────────────────────────────────────
  const handleCaptureSnapshot = () => {
    const renderer = rendererRef.current;
    if (!renderer) return;
    const dataURL = renderer.domElement.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = dataURL;
    const projName = (project?.name || 'house').toLowerCase().replace(/\s+/g, '_');
    a.download = `${projName}_3d_exterior_${activePreset}_${isNight ? 'night' : 'day'}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div
      className={`exterior-3d-wrapper ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: '480px',
        borderRadius: '16px',
        overflow: 'hidden',
        background: isNight ? '#0a0f1d' : '#e6f0fa'
      }}
    >
      {/* 3D Canvas Mount */}
      <div ref={mountRef} style={{ width: '100%', height: '100%', minHeight: '480px' }} />

      {/* ── Responsive Non-Overlapping Top Bar ── */}
      <div className="viewer-top-bar-v3">
        {/* Camera Angle Presets */}
        <div className="viewer-presets-pill-group">
          <span className="viewer-group-label">View</span>
          <button
            type="button"
            className={`btn-viewer-preset ${activePreset === 'front' ? 'active' : ''}`}
            onClick={() => setCameraPreset('front')}
            title="Direct Front Elevation"
          >
            Front
          </button>
          <button
            type="button"
            className={`btn-viewer-preset ${activePreset === 'front_left' ? 'active' : ''}`}
            onClick={() => setCameraPreset('front_left')}
            title="3/4 Front-Left Perspective"
          >
            3/4 Left
          </button>
          <button
            type="button"
            className={`btn-viewer-preset ${activePreset === 'front_right' ? 'active' : ''}`}
            onClick={() => setCameraPreset('front_right')}
            title="3/4 Front-Right Perspective"
          >
            3/4 Right
          </button>
          <button
            type="button"
            className={`btn-viewer-preset ${activePreset === 'top' ? 'active' : ''}`}
            onClick={() => setCameraPreset('top')}
            title="Top-Down Bird's Eye View"
          >
            Aerial
          </button>
        </div>

        {/* View Actions: Day/Night, Turntable, Reset Camera, Snapshot */}
        <div className="viewer-actions-pill-group">
          <button
            type="button"
            className={`btn-viewer-action ${isNight ? 'night-active' : ''}`}
            onClick={() => {
              const next = !isNight;
              setIsNight(next);
              onToggleLighting?.(next ? 'night' : 'daylight');
            }}
            title="Toggle Daylight Sun / Night Atmosphere"
          >
            {isNight ? <Moon size={14} color="#fde047" /> : <Sun size={14} color="#f59e0b" />}
            <span>{isNight ? 'Night Atmosphere' : 'Daylight Sun'}</span>
          </button>

          <button
            type="button"
            className={`btn-viewer-action ${isRotating ? 'active' : ''}`}
            onClick={() => setIsRotating((r) => !r)}
            title="Auto-rotate 360° architectural model"
          >
            <RotateCw size={14} className={isRotating ? 'spin' : ''} />
            <span>Turntable</span>
          </button>

          <button
            type="button"
            className="btn-viewer-action"
            onClick={() => setCameraPreset('front_left')}
            title="Reset Camera to Default Perspective"
          >
            <RotateCcw size={14} />
            <span>Reset Camera</span>
          </button>

          <button
            type="button"
            className="btn-viewer-action"
            onClick={handleCaptureSnapshot}
            title="Export 3D Architectural View as PNG"
          >
            <Camera size={14} />
            <span>Capture 3D</span>
          </button>
        </div>
      </div>

      {/* ── Responsive Non-Overlapping Bottom Bar ── */}
      <div className="viewer-bottom-bar-v3">
        {/* Grounding Info Badge */}
        <div className="viewer-bottom-left-badge">
          <span className="ground-dot" />
          <span className="ground-tag-full" style={{ color: '#38bdf8', fontWeight: 700 }}>DIMENSION GROUNDED</span>
          <span className="ground-tag-short" style={{ color: '#38bdf8', fontWeight: 700 }}>GROUNDED</span>
          <span className="badge-sep">•</span>
          <span>{plotW}′ × {plotL}′ Plot</span>
          <span className="badge-sep">•</span>
          <span>{floors > 1 ? `G + ${floors - 1} Floors` : 'Ground Floor'}</span>
          <span className="badge-sep">•</span>
          <span>{facing} Facing</span>
        </div>

        {/* Interactive Helper Badge */}
        <div className="viewer-bottom-right-badge">
          <span className="hint-full">Drag to Orbit • Scroll to Zoom • Right-click to Pan</span>
          <span className="hint-short">Drag to Orbit • Scroll to Zoom</span>
        </div>
      </div>
    </div>
  );
};

export default Exterior3DViewer;
