import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  Sun,
  Moon,
  Camera,
  RotateCw,
  RotateCcw,
  Download,
  Eye,
  Maximize2,
  Sliders,
  Layers
} from 'lucide-react';

/**
 * Exterior3DViewer — Phase 6G
 *
 * Dimension-grounded interactive 3D WebGL house massing model.
 * Adapts to:
 * - Real plot width, plot length, and floor count (G, G+1, G+2)
 * - Selected design architectural language (Modern, Minimalist, Luxury, Traditional, etc.)
 * - Dynamic custom colors: primary_wall, accent_wall, door, railing
 * - Real-time Day / Night lighting with 2700K window interior emission & exterior sconces
 * - Camera angle presets (Front, 3/4 Left, 3/4 Right, Bird's Eye)
 * - Auto-rotation turntable & high-res PNG snapshot export
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

  const [isNight, setIsNight] = useState(lightingMode === 'night');
  const [isRotating, setIsRotating] = useState(false);
  const [activePreset, setActivePreset] = useState('front_left');

  // Sync internal state with prop
  useEffect(() => {
    setIsNight(lightingMode === 'night');
  }, [lightingMode]);

  // Dimensions
  const plotW = Number(project?.plot_width) || 30;
  const plotL = Number(project?.plot_length) || 40;
  const floors = Number(project?.floors) || 2;
  const facing = project?.facing || 'North';

  // Extract All 12 Customizable Component Colors
  const primaryColorHex =
    customColors?.primary_wall ||
    selectedDesign?.primary_paint_color?.hex ||
    '#F4F4F0';
  const secondaryColorHex =
    customColors?.secondary_wall ||
    '#E5E7EB';
  const accentColorHex =
    customColors?.accent_wall ||
    selectedDesign?.secondary_paint_color?.hex ||
    '#2B313B';
  const frontFacadeColorHex =
    customColors?.front_facade ||
    primaryColorHex;
  const boundaryWallColorHex =
    customColors?.boundary_wall ||
    '#E5E0D6';
  const boundaryGateColorHex =
    customColors?.boundary_gate ||
    '#30343B';
  const doorColorHex =
    customColors?.door ||
    '#8B5A2B';
  const windowFrameColorHex =
    customColors?.window_frame ||
    '#20252B';
  const windowGlassColorHex =
    customColors?.window_glass_tint ||
    '#7DD3FC';
  const railingColorHex =
    customColors?.railing ||
    '#1F2937';
  const roofParapetColorHex =
    customColors?.roof_parapet ||
    accentColorHex;
  const exteriorTrimsColorHex =
    customColors?.exterior_trims ||
    '#20252B';

  const finishType = customMaterials?.finish_type || 'matte_paint';

  // Architectural category
  const category = selectedDesign?.category || 'modern_contemporary';
  const isTraditionalOrClay =
    category === 'traditional_indian' || category === 'mediterranean';
  const isMinimal = category === 'minimalist';
  const isLuxury = category === 'luxury_villa';
  const isTropical = category === 'tropical_contemporary';
  const isIndianModern = category === 'indian_modern';

  // Initialize Three.js Scene
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 520;

    // 1. Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // 2. Camera
    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000);
    cameraRef.current = camera;

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      preserveDrawingBuffer: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 4. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 6;
    controls.maxDistance = 65;
    controls.maxPolarAngle = Math.PI / 2 - 0.03; // Don't clip under ground
    controlsRef.current = controls;

    // 5. Lighting Setup
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xfff8eb, 1.8);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 100;
    dirLight.shadow.camera.left = -20;
    dirLight.shadow.camera.right = 20;
    dirLight.shadow.camera.top = 20;
    dirLight.shadow.camera.bottom = -20;
    dirLight.shadow.bias = -0.0005;
    dirLight.position.set(16, 26, 18);
    scene.add(dirLight);

    // Warm sconce light at entrance
    const porchLight = new THREE.PointLight(0xffdf80, 0, 10);
    porchLight.position.set(0, 3.2, 5.5);
    porchLight.castShadow = true;
    scene.add(porchLight);

    // Facade graze spot
    const facadeSpot = new THREE.SpotLight(0xffaa44, 0, 14, Math.PI / 5, 0.4, 1.2);
    facadeSpot.position.set(-3.5, 0.2, 5.5);
    facadeSpot.target.position.set(-3.5, 6, 4);
    scene.add(facadeSpot);
    scene.add(facadeSpot.target);

    lightsRef.current = { ambientLight, dirLight, porchLight, facadeSpot };

    // 6. Base / Site Ground
    const groundGeo = new THREE.PlaneGeometry(60, 60);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x223326,
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
      color: 0x475569,
      roughness: 0.85
    });
    const plinth = new THREE.Mesh(plinthGeo, plinthMat);
    plinth.position.y = 0.15;
    plinth.receiveShadow = true;
    scene.add(plinth);

    // Stone Walkway / Driveway
    const driveGeo = new THREE.BoxGeometry(siteW * 0.42, 0.02, siteL * 0.48);
    const driveMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      roughness: 0.7
    });
    const drive = new THREE.Mesh(driveGeo, driveMat);
    drive.position.set(siteW * 0.22, 0.31, siteL * 0.25);
    drive.receiveShadow = true;
    scene.add(drive);

    // Set Initial Camera Position (Isometric 3/4 front-left)
    const houseCenterY = (floors * 3.0) / 2;
    camera.position.set(-16, houseCenterY + 7, 19);
    controls.target.set(0, houseCenterY, 0);
    controls.update();

    // Resize Handler
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

  // Update Environment / Day-Night Lighting
  useEffect(() => {
    const scene = sceneRef.current;
    const { ambientLight, dirLight, porchLight, facadeSpot } = lightsRef.current;
    if (!scene || !ambientLight || !dirLight) return;

    if (isNight) {
      // Twilight Night
      scene.background = new THREE.Color(0x0a0f1d);
      ambientLight.color.setHex(0x1e293b);
      ambientLight.intensity = 0.4;

      dirLight.color.setHex(0x38bdf8);
      dirLight.intensity = 0.25;
      dirLight.position.set(-10, 20, -10);

      porchLight.intensity = 2.4;
      facadeSpot.intensity = 2.8;
    } else {
      // Crisp Natural Daylight
      scene.background = new THREE.Color(0xe6f0fa);
      ambientLight.color.setHex(0xffffff);
      ambientLight.intensity = 0.85;

      dirLight.color.setHex(0xfff8eb);
      dirLight.intensity = 1.8;
      dirLight.position.set(16, 26, 18);

      porchLight.intensity = 0;
      facadeSpot.intensity = 0;
    }
  }, [isNight]);

  // Auto-rotation
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.autoRotate = isRotating;
      controlsRef.current.autoRotateSpeed = 2.0;
    }
  }, [isRotating]);

  // Build / Rebuild House Geometry on Parameter Changes
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;

    // Remove existing house group
    if (houseGroupRef.current) {
      scene.remove(houseGroupRef.current);
      houseGroupRef.current.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
          else obj.material.dispose();
        }
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

    // Determine roughness & metalness modifier based on finishType
    let finishRoughness = 0.75;
    let finishMetalness = 0.05;
    if (finishType === 'matte') { finishRoughness = 0.95; finishMetalness = 0.0; }
    else if (finishType === 'satin') { finishRoughness = 0.65; finishMetalness = 0.05; }
    else if (finishType === 'gloss') { finishRoughness = 0.25; finishMetalness = 0.15; }
    else if (finishType === 'textured') { finishRoughness = 0.98; finishMetalness = 0.02; }
    else if (finishType === 'stone') { finishRoughness = 0.85; finishMetalness = 0.08; }
    else if (finishType === 'wood') { finishRoughness = 0.55; finishMetalness = 0.05; }
    else if (finishType === 'metal') { finishRoughness = 0.35; finishMetalness = 0.8; }
    else if (finishType === 'glass_tint') { finishRoughness = 0.1; finishMetalness = 0.9; }

    // Dedicated materials for all 12 components:
    // 1. Primary Wall Material
    const wallPrimaryMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(primaryColorHex),
      roughness: isMinimal ? 0.95 : finishRoughness,
      metalness: finishMetalness
    });

    // 2. Secondary Wall Material (recessed & side surfaces)
    const wallSecondaryMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(secondaryColorHex),
      roughness: finishRoughness,
      metalness: finishMetalness
    });

    // 3. Accent Wall Material
    const wallAccentMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(accentColorHex),
      roughness: 0.6,
      metalness: isLuxury ? 0.25 : 0.1
    });

    // 4. Front Facade Feature Material
    const frontFacadeMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(frontFacadeColorHex),
      roughness: 0.55,
      metalness: 0.15
    });

    // 5. Boundary Wall Material
    const boundaryWallMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(boundaryWallColorHex),
      roughness: 0.85,
      metalness: 0.03
    });

    // 6. Boundary Gate Material
    const boundaryGateMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(boundaryGateColorHex),
      roughness: 0.35,
      metalness: 0.75
    });

    // 7. Door Material
    const doorMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(doorColorHex),
      roughness: 0.45,
      metalness: 0.15
    });

    // 8. Window Frame Material
    const windowFrameMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(windowFrameColorHex),
      roughness: 0.35,
      metalness: 0.6
    });

    // 9. Window Glass Material (Tinted)
    const windowGlassMat = new THREE.MeshStandardMaterial({
      color: isNight ? 0xfff3a0 : new THREE.Color(windowGlassColorHex),
      emissive: isNight ? 0xf59e0b : 0x000000,
      emissiveIntensity: isNight ? 1.6 : 0.0,
      roughness: 0.1,
      metalness: 0.85,
      transparent: true,
      opacity: isNight ? 0.95 : 0.6
    });

    // 10. Railing Material
    const railingMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(railingColorHex),
      roughness: 0.3,
      metalness: 0.7
    });

    // 11. Roof Parapet Material
    const roofParapetMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(roofParapetColorHex),
      roughness: 0.75,
      metalness: 0.05
    });

    // 12. Exterior Trims Material
    const exteriorTrimsMat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(exteriorTrimsColorHex),
      roughness: 0.4,
      metalness: 0.5
    });

    const concreteSlabMat = new THREE.MeshStandardMaterial({
      color: 0xd6d3d1,
      roughness: 0.8
    });

    // ── Build Each Floor ──────────────────────────────────────────────────
    for (let f = 0; f < numFloors; f++) {
      const floorBaseY = 0.3 + f * floorH;
      const isGround = f === 0;
      const isTop = f === numFloors - 1;

      // Cantilever projection on upper floors for modern / duplex
      const cantileverZ = !isGround && !isTraditionalOrClay ? 0.6 : 0;
      const fWidth = !isGround && isMinimal ? bldgW * 0.95 : bldgW;
      const fDepth = bldgD;

      // 1. Floor Wall Mass (Primary Wall)
      const wallGeo = new THREE.BoxGeometry(fWidth, floorH, fDepth);
      const wallMesh = new THREE.Mesh(wallGeo, wallPrimaryMat);
      wallMesh.position.set(0, floorBaseY + floorH / 2, cantileverZ / 2);
      wallMesh.castShadow = true;
      wallMesh.receiveShadow = true;
      houseGroup.add(wallMesh);

      // 2. Secondary Wall Mass (Side Flank / Rear Wing Return)
      const sideWallGeo = new THREE.BoxGeometry(0.12, floorH * 0.98, fDepth * 0.7);
      const sideWallMesh = new THREE.Mesh(sideWallGeo, wallSecondaryMat);
      sideWallMesh.position.set(fWidth / 2 + 0.05, floorBaseY + floorH / 2, -fDepth * 0.1);
      sideWallMesh.castShadow = true;
      houseGroup.add(sideWallMesh);

      // 3. Accent Cladding Vertical Feature (left side of facade)
      const accentGeo = new THREE.BoxGeometry(
        fWidth * 0.32,
        floorH + 0.02,
        0.18
      );
      const accentMesh = new THREE.Mesh(accentGeo, wallAccentMat);
      accentMesh.position.set(
        -fWidth * 0.32,
        floorBaseY + floorH / 2,
        fDepth / 2 + cantileverZ / 2 + 0.08
      );
      accentMesh.castShadow = true;
      houseGroup.add(accentMesh);

      // 4. Front Facade Feature Surround (Architectural Portal Frame)
      const facadePortalGeo = new THREE.BoxGeometry(
        fWidth * 0.42,
        0.16,
        0.25
      );
      const facadePortalMesh = new THREE.Mesh(facadePortalGeo, frontFacadeMat);
      facadePortalMesh.position.set(
        fWidth * 0.15,
        floorBaseY + floorH - 0.08,
        fDepth / 2 + cantileverZ / 2 + 0.12
      );
      facadePortalMesh.castShadow = true;
      houseGroup.add(facadePortalMesh);

      // If Indian Modern: Add terracotta jaali pattern geometry
      if (isIndianModern) {
        const jaaliGeo = new THREE.BoxGeometry(
          fWidth * 0.26,
          floorH * 0.85,
          0.1
        );
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

      // Ground Floor Entrance or Upper Floor Windows
      if (isGround) {
        // Entrance Grand Door
        const doorGeo = new THREE.BoxGeometry(1.2, 2.2, 0.15);
        const doorMesh = new THREE.Mesh(doorGeo, doorMat);
        doorMesh.position.set(fWidth * 0.15, floorBaseY + 1.1, fDepth / 2 + 0.08);
        doorMesh.castShadow = true;
        houseGroup.add(doorMesh);

        // Entrance Canopy / Portico (Exterior Trims)
        const canopyGeo = new THREE.BoxGeometry(2.4, 0.15, 1.6);
        const canopyMesh = new THREE.Mesh(canopyGeo, exteriorTrimsMat);
        canopyMesh.position.set(
          fWidth * 0.15,
          floorBaseY + 2.3,
          fDepth / 2 + 0.8
        );
        canopyMesh.castShadow = true;
        houseGroup.add(canopyMesh);

        // Ground Floor Picture Window
        const winGeo = new THREE.BoxGeometry(2.0, 1.6, 0.1);
        const winMesh = new THREE.Mesh(winGeo, windowGlassMat);
        winMesh.position.set(
          fWidth * 0.28,
          floorBaseY + 1.25,
          fDepth / 2 + 0.06
        );
        houseGroup.add(winMesh);

        // Window Frame
        const frameGeo = new THREE.BoxGeometry(2.1, 1.7, 0.08);
        const frameMesh = new THREE.Mesh(frameGeo, windowFrameMat);
        frameMesh.position.set(
          fWidth * 0.28,
          floorBaseY + 1.25,
          fDepth / 2 + 0.04
        );
        houseGroup.add(frameMesh);
      } else {
        // Upper Floor Large Panoramic Window / Sliding Balcony Door
        const winGeo = new THREE.BoxGeometry(fWidth * 0.45, 1.9, 0.1);
        const winMesh = new THREE.Mesh(winGeo, windowGlassMat);
        winMesh.position.set(
          fWidth * 0.18,
          floorBaseY + 1.2,
          fDepth / 2 + cantileverZ / 2 + 0.06
        );
        houseGroup.add(winMesh);

        // Upper Window Frame
        const upperFrameGeo = new THREE.BoxGeometry(fWidth * 0.46, 2.0, 0.08);
        const upperFrameMesh = new THREE.Mesh(upperFrameGeo, windowFrameMat);
        upperFrameMesh.position.set(
          fWidth * 0.18,
          floorBaseY + 1.2,
          fDepth / 2 + cantileverZ / 2 + 0.04
        );
        houseGroup.add(upperFrameMesh);

        // Cantilevered Balcony Slab
        const balcSlabGeo = new THREE.BoxGeometry(fWidth * 0.52, 0.2, 1.2);
        const balcSlab = new THREE.Mesh(balcSlabGeo, concreteSlabMat);
        balcSlab.position.set(
          fWidth * 0.18,
          floorBaseY + 0.1,
          fDepth / 2 + cantileverZ / 2 + 0.6
        );
        balcSlab.castShadow = true;
        balcSlab.receiveShadow = true;
        houseGroup.add(balcSlab);

        // Balcony Railing
        const railGeo = new THREE.BoxGeometry(fWidth * 0.5, 0.95, 0.05);
        const railMesh = new THREE.Mesh(railGeo, railingMat);
        railMesh.position.set(
          fWidth * 0.18,
          floorBaseY + 0.65,
          fDepth / 2 + cantileverZ / 2 + 1.15
        );
        houseGroup.add(railMesh);
      }

      // Side Windows
      const sideWinGeo = new THREE.BoxGeometry(0.1, 1.4, 1.6);
      const sideWin = new THREE.Mesh(sideWinGeo, windowGlassMat);
      sideWin.position.set(fWidth / 2 + 0.04, floorBaseY + 1.3, 0);
      houseGroup.add(sideWin);

      // Side Window Frame
      const sideFrameGeo = new THREE.BoxGeometry(0.08, 1.5, 1.7);
      const sideFrame = new THREE.Mesh(sideFrameGeo, windowFrameMat);
      sideFrame.position.set(fWidth / 2 + 0.03, floorBaseY + 1.3, 0);
      houseGroup.add(sideFrame);
    }

    // ── Roof Level ────────────────────────────────────────────────────────
    const totalBuildingH = 0.3 + numFloors * floorH;

    if (isTraditionalOrClay) {
      // Sloping Pitched Clay Tile Roof (Mangalore / Spanish Terracotta)
      const roofH = 1.9;
      const roofOverhang = 0.8;
      const roofGeo = new THREE.ConeGeometry(
        Math.hypot(bldgW + roofOverhang, bldgD + roofOverhang) * 0.42,
        roofH,
        4
      );
      roofGeo.rotateY(Math.PI / 4);
      const roofMesh = new THREE.Mesh(roofGeo, roofParapetMat);
      roofMesh.position.set(0, totalBuildingH + roofH / 2, 0);
      roofMesh.castShadow = true;
      houseGroup.add(roofMesh);
    } else {
      // Modern Flat Terrace with Parapet Wall
      const parapetGeo = new THREE.BoxGeometry(bldgW + 0.2, 0.8, bldgD + 0.2);
      const parapetMesh = new THREE.Mesh(parapetGeo, roofParapetMat);
      parapetMesh.position.set(0, totalBuildingH + 0.4, 0);
      parapetMesh.castShadow = true;
      houseGroup.add(parapetMesh);

      // Terrace Hollow Core
      const terraceCoreGeo = new THREE.BoxGeometry(bldgW - 0.4, 0.82, bldgD - 0.4);
      const terraceCoreMat = new THREE.MeshStandardMaterial({
        color: 0x94a3b8,
        roughness: 0.9
      });
      const terraceCore = new THREE.Mesh(terraceCoreGeo, terraceCoreMat);
      terraceCore.position.set(0, totalBuildingH + 0.42, 0);
      houseGroup.add(terraceCore);

      // Architectural Modern Pergola (Exterior Trims)
      const pergolaGeo = new THREE.BoxGeometry(bldgW * 0.4, 0.15, bldgD * 0.35);
      const pergolaMesh = new THREE.Mesh(pergolaGeo, exteriorTrimsMat);
      pergolaMesh.position.set(bldgW * 0.2, totalBuildingH + 1.8, -bldgD * 0.15);
      pergolaMesh.castShadow = true;
      houseGroup.add(pergolaMesh);

      // Pergola Support Columns (Exterior Trims)
      const colGeo = new THREE.BoxGeometry(0.12, 1.8, 0.12);
      const col1 = new THREE.Mesh(colGeo, exteriorTrimsMat);
      col1.position.set(bldgW * 0.38, totalBuildingH + 0.9, -bldgD * 0.3);
      houseGroup.add(col1);
    }

    // ── Boundary Wall & Front Gate ─────────────────────────────────────────
    const wallHeight = 1.1;
    const boundaryThick = 0.18;
    const frontWallZ = (plotL * plotScale) / 2 + 0.3;

    // Left Front Compound Wall
    const leftWallGeo = new THREE.BoxGeometry(bldgW * 0.35, wallHeight, boundaryThick);
    const leftWall = new THREE.Mesh(leftWallGeo, boundaryWallMat);
    leftWall.position.set(-bldgW * 0.32, wallHeight / 2 + 0.3, frontWallZ);
    leftWall.castShadow = true;
    houseGroup.add(leftWall);

    // Right Front Compound Wall
    const rightWallGeo = new THREE.BoxGeometry(bldgW * 0.2, wallHeight, boundaryThick);
    const rightWall = new THREE.Mesh(rightWallGeo, boundaryWallMat);
    rightWall.position.set(bldgW * 0.4, wallHeight / 2 + 0.3, frontWallZ);
    rightWall.castShadow = true;
    houseGroup.add(rightWall);

    // Front Sliding Gate (Slatted Metal)
    const gateGeo = new THREE.BoxGeometry(bldgW * 0.36, wallHeight * 0.9, 0.06);
    const gateMesh = new THREE.Mesh(gateGeo, boundaryGateMat);
    gateMesh.position.set(bldgW * 0.08, wallHeight * 0.45 + 0.3, frontWallZ);
    gateMesh.castShadow = true;
    houseGroup.add(gateMesh);

    scene.add(houseGroup);
  }, [
    plotW,
    plotL,
    floors,
    primaryColorHex,
    secondaryColorHex,
    accentColorHex,
    frontFacadeColorHex,
    boundaryWallColorHex,
    boundaryGateColorHex,
    doorColorHex,
    windowFrameColorHex,
    windowGlassColorHex,
    railingColorHex,
    roofParapetColorHex,
    exteriorTrimsColorHex,
    finishType,
    category,
    isNight
  ]);

  // Camera Presets
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

  // Snapshot PNG Download
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
    <div className={`exterior-3d-wrapper ${className}`} style={{ position: 'relative', width: '100%', height: '100%', minHeight: '480px', borderRadius: '16px', overflow: 'hidden', background: isNight ? '#0a0f1d' : '#e6f0fa' }}>
      {/* 3D Canvas Mount */}
      <div ref={mountRef} style={{ width: '100%', height: '100%', minHeight: '480px' }} />

      {/* Floating Control Overlay: View Presets */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          left: '16px',
          display: 'flex',
          gap: '6px',
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(8px)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          zIndex: 10
        }}
      >
        <button
          onClick={() => setCameraPreset('front')}
          style={{
            padding: '6px 12px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            background: activePreset === 'front' ? 'var(--color-accent, #3b82f6)' : 'transparent',
            color: '#ffffff',
            transition: 'all 0.15s ease'
          }}
          title="Direct Front Elevation"
        >
          Front Elevation
        </button>
        <button
          onClick={() => setCameraPreset('front_left')}
          style={{
            padding: '6px 12px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            background: activePreset === 'front_left' ? 'var(--color-accent, #3b82f6)' : 'transparent',
            color: '#ffffff',
            transition: 'all 0.15s ease'
          }}
          title="3/4 Front-Left Perspective"
        >
          Perspective Left
        </button>
        <button
          onClick={() => setCameraPreset('front_right')}
          style={{
            padding: '6px 12px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            background: activePreset === 'front_right' ? 'var(--color-accent, #3b82f6)' : 'transparent',
            color: '#ffffff',
            transition: 'all 0.15s ease'
          }}
          title="3/4 Front-Right Perspective"
        >
          Perspective Right
        </button>
        <button
          onClick={() => setCameraPreset('top')}
          style={{
            padding: '6px 12px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer',
            background: activePreset === 'top' ? 'var(--color-accent, #3b82f6)' : 'transparent',
            color: '#ffffff',
            transition: 'all 0.15s ease'
          }}
          title="Top-Down Bird's Eye View"
        >
          Aerial
        </button>
      </div>

      {/* Floating Control Overlay: Day/Night, Turntable, Snapshot */}
      <div
        style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          display: 'flex',
          gap: '8px',
          zIndex: 10
        }}
      >
        {/* Day/Night Toggle */}
        <button
          onClick={() => {
            const next = !isNight;
            setIsNight(next);
            onToggleLighting?.(next ? 'night' : 'daylight');
          }}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 14px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            background: isNight ? '#1e293b' : '#ffffff',
            color: isNight ? '#fde047' : '#0f172a',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          title="Toggle Day / Night Architectural Lighting"
        >
          {isNight ? <Moon size={14} color="#fde047" /> : <Sun size={14} color="#f59e0b" />}
          <span>{isNight ? 'Night Atmosphere' : 'Daylight Sun'}</span>
        </button>

        {/* Turntable Auto-Rotate */}
        <button
          onClick={() => setIsRotating(r => !r)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            background: isRotating ? 'var(--color-accent, #3b82f6)' : 'rgba(15, 23, 42, 0.75)',
            color: '#ffffff',
            cursor: 'pointer',
            backdropFilter: 'blur(8px)'
          }}
          title="Auto-rotate 360° architectural model"
        >
          <RotateCw size={15} />
        </button>

        {/* Reset Camera to Default Perspective */}
        <button
          onClick={() => setCameraPreset('front_left')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            background: 'rgba(15, 23, 42, 0.75)',
            color: '#ffffff',
            cursor: 'pointer',
            backdropFilter: 'blur(8px)'
          }}
          title="Reset Camera to Default Perspective"
        >
          <RotateCcw size={15} />
        </button>

        {/* Snapshot PNG */}
        <button
          onClick={handleCaptureSnapshot}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 14px',
            fontSize: '0.75rem',
            fontWeight: 600,
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            background: 'rgba(15, 23, 42, 0.75)',
            color: '#ffffff',
            cursor: 'pointer',
            backdropFilter: 'blur(8px)'
          }}
          title="Export 3D Architectural View as PNG"
        >
          <Camera size={14} />
          <span>Capture 3D</span>
        </button>
      </div>

      {/* Grounding Info Badge (Bottom Left) */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          left: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(8px)',
          padding: '6px 14px',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: '#ffffff',
          fontSize: '0.72rem',
          zIndex: 10
        }}
      >
        <span style={{ color: 'var(--color-accent, #60a5fa)', fontWeight: 600 }}>DIMENSION GROUNDED</span>
        <span>•</span>
        <span>{plotW}′ × {plotL}′ Plot</span>
        <span>•</span>
        <span>{floors > 1 ? `G + ${floors - 1} Floors` : 'Ground Floor'}</span>
        <span>•</span>
        <span>{facing} Facing</span>
      </div>

      {/* Interactive Helper Badge (Bottom Right) */}
      <div
        style={{
          position: 'absolute',
          bottom: '16px',
          right: '16px',
          background: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(8px)',
          padding: '5px 12px',
          borderRadius: '6px',
          color: 'rgba(255, 255, 255, 0.7)',
          fontSize: '0.68rem',
          zIndex: 10
        }}
      >
        Drag to Orbit • Scroll to Zoom • Right-click to Pan
      </div>
    </div>
  );
};

export default Exterior3DViewer;
