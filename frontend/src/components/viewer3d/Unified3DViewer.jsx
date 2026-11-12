import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import {
  Sun,
  Moon,
  Home,
  Eye,
  Layers,
  Compass,
  RotateCw,
  RotateCcw,
  Maximize2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Info,
  Sparkles,
  Palette,
  DoorOpen,
  X,
  AlertTriangle,
  RefreshCw,
  Camera
} from 'lucide-react';
import ArchitecturalRenderModal from '../rendering/ArchitecturalRenderModal';
import { buildUnifiedHouseModel } from '../../services/unifiedHouseGeometryBuilder';
import { generateCanonicalFloorPlan } from '../../services/canonicalFloorPlanGenerator';
import { exteriorDesignService } from '../../services/exteriorDesignService';
import { interiorDesignService } from '../../services/interiorDesignService';
import { aiService } from '../../services/aiService';
import '../../styles/pages/unified-3d-viewer.css';

/**
 * Checks whether WebGL is supported by the client browser.
 */
function checkWebGLSupport() {
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch (_) {
    return false;
  }
}

export default function Unified3DViewer({
  project = {},
  initialViewMode = 'exterior',
  initialFloor = 'all'
}) {
  const projectId = project?.id;
  const navigate = useNavigate();

  const mountRef = useRef(null);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const controlsRef = useRef(null);
  const animFrameRef = useRef(null);
  const houseModelRef = useRef(null);
  const lightsRef = useRef({});

  // ── Viewer State ──────────────────────────────────────────────────────────
  const [viewMode, setViewMode] = useState(initialViewMode); // 'exterior' | 'interior' | 'top_down'
  const [currentFloor, setCurrentFloor] = useState(initialFloor); // 'all' | 0 | 1
  const [isNight, setIsNight] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [activeRoomId, setActiveRoomId] = useState('');
  const [activeRoomData, setActiveRoomData] = useState(null);
  const [roomAnchorsList, setRoomAnchorsList] = useState([]);

  // Data State
  const [floorPlan, setFloorPlan] = useState(null);
  const [exteriorSelection, setExteriorSelection] = useState(null);
  const [interiorSelections, setInteriorSelections] = useState({});
  const [loadingData, setLoadingData] = useState(true);
  const [webGLError, setWebGLError] = useState(false);
  const [initKey, setInitKey] = useState(0);

  // Architectural Render Studio Modal State
  const [isRenderModalOpen, setIsRenderModalOpen] = useState(false);
  const [renderModalTarget, setRenderModalTarget] = useState('exterior');
  const [renderModalRoomId, setRenderModalRoomId] = useState(null);

  // Animation Tween State
  const cameraTweenRef = useRef(null);

  // High-performance refs for animation loop
  const isRotatingRef = useRef(isRotating);
  const viewModeRef = useRef(viewMode);
  const activeRoomDataRef = useRef(activeRoomData);
  const isRenderModalOpenRef = useRef(isRenderModalOpen);

  useEffect(() => { isRotatingRef.current = isRotating; }, [isRotating]);
  useEffect(() => { viewModeRef.current = viewMode; }, [viewMode]);
  useEffect(() => { activeRoomDataRef.current = activeRoomData; }, [activeRoomData]);
  useEffect(() => { isRenderModalOpenRef.current = isRenderModalOpen; }, [isRenderModalOpen]);

  // ── 1. Fetch & Harmonize Project Data ─────────────────────────────────────
  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      if (!projectId) return;
      setLoadingData(true);

      try {
        // 1a. Load Floor Plan (localStorage cache -> Supabase remote -> Canonical Generator)
        let fp = null;
        const cachedFp = localStorage.getItem(`floorplan_${projectId}`);
        if (cachedFp) {
          try {
            const parsed = JSON.parse(cachedFp);
            fp = parsed.layout_data || parsed;
          } catch (_) {}
        }

        if (!fp || !Array.isArray(fp.floors) || fp.floors.length === 0) {
          try {
            const remotePlans = await aiService.getFloorPlans(projectId);
            if (remotePlans && remotePlans.length > 0) {
              fp = remotePlans[0].layout_data || remotePlans[0];
            }
          } catch (_) {}
        }

        if (!fp || !Array.isArray(fp.floors) || fp.floors.length === 0) {
          fp = generateCanonicalFloorPlan(project);
        }

        // 1b. Load Exterior Selection (localStorage -> API)
        let extSel = null;
        try {
          extSel = await exteriorDesignService.getProjectSelection(projectId);
        } catch (_) {}

        // 1c. Load Interior Room Selections (localStorage -> API)
        let intSels = {};
        try {
          const intRes = await interiorDesignService.getProjectSelections(projectId);
          intSels = intRes?.selections || {};
        } catch (_) {}

        if (isMounted) {
          setFloorPlan(fp);
          setExteriorSelection(extSel);
          setInteriorSelections(intSels);
        }
      } catch (err) {
        console.warn('[Unified3DViewer] Error loading project data:', err);
      } finally {
        if (isMounted) setLoadingData(false);
      }
    }

    loadData();
    return () => { isMounted = false; };
  }, [projectId, project]);

  // ── 2. Initialize Three.js Canvas & Lighting (Mount Once) ─────────────────
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    if (!checkWebGLSupport()) {
      setWebGLError(true);
      return;
    }

    setWebGLError(false);
    const width = container.clientWidth || 900;
    const height = container.clientHeight || 560;

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe8f2fb);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(16, 14, 20);
    cameraRef.current = camera;

    // WebGL Renderer with High Performance & Shadows
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      preserveDrawingBuffer: true,
      powerPreference: 'high-performance'
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.minDistance = 1.2;
    controls.maxDistance = 85.0;
    controls.maxPolarAngle = Math.PI / 2 - 0.02;
    controls.target.set(0, 2.0, 0);
    controlsRef.current = controls;

    // Lighting Setup
    const hemiLight = new THREE.HemisphereLight(0xf0f9ff, 0x64748b, 1.25);
    hemiLight.position.set(0, 50, 0);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xfffaed, 2.2);
    dirLight.position.set(22, 32, 24);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 140;
    dirLight.shadow.camera.left = -28;
    dirLight.shadow.camera.right = 28;
    dirLight.shadow.camera.top = 28;
    dirLight.shadow.camera.bottom = -28;
    dirLight.shadow.bias = -0.00005;
    dirLight.shadow.normalBias = 0.035;
    dirLight.shadow.radius = 1.8;
    scene.add(dirLight);

    const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.75);
    fillLight.position.set(-20, 16, -18);
    scene.add(fillLight);

    lightsRef.current = { hemiLight, dirLight, fillLight };

    // Render loop
    const animate = () => {
       animFrameRef.current = requestAnimationFrame(animate);

      // Pause background WebGL rendering if photo render modal is open
      if (isRenderModalOpenRef.current) {
        return;
      }

      // Smooth camera lerp tween
      if (cameraTweenRef.current) {
        const { startPos, endPos, startTarget, endTarget, startFov, endFov, startTime, duration } = cameraTweenRef.current;
        const elapsed = (Date.now() - startTime) / duration;
        const progress = Math.min(1.0, elapsed);
        const ease = 1 - Math.pow(1 - progress, 3); // Cubic ease out

        camera.position.lerpVectors(startPos, endPos, ease);
        controls.target.lerpVectors(startTarget, endTarget, ease);
        camera.lookAt(controls.target);

        if (startFov && endFov && startFov !== endFov) {
          camera.fov = THREE.MathUtils.lerp(startFov, endFov, ease);
          camera.updateProjectionMatrix();
        }

        if (progress >= 1.0) {
          camera.position.copy(endPos);
          controls.target.copy(endTarget);
          camera.lookAt(endTarget);
          if (endFov) {
            camera.fov = endFov;
            camera.updateProjectionMatrix();
          }
          controls.enabled = true;
          controls.update();
          cameraTweenRef.current = null;
        }
      } else {
        // Auto-turntable rotation if enabled
        if (isRotatingRef.current) {
          controls.autoRotate = true;
          controls.autoRotateSpeed = 2.0;
        } else {
          controls.autoRotate = false;
        }

        controls.update();

        // First-person walkthrough: clamp camera strictly within room boundary
        if (viewModeRef.current === 'interior' && activeRoomDataRef.current?.bounds) {
          const b = activeRoomDataRef.current.bounds;
          camera.position.x = Math.max(b.minX, Math.min(b.maxX, camera.position.x));
          camera.position.z = Math.max(b.minZ, Math.min(b.maxZ, camera.position.z));
          camera.position.y = Math.max(b.minY, Math.min(b.maxY, camera.position.y));
        }
      }

      renderer.render(scene, camera);
    };
    animate();

    // Resize observer
    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w === 0 || h === 0) return;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    let resizeObserver = null;
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        handleResize();
      });
      resizeObserver.observe(container);
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      if (resizeObserver) resizeObserver.disconnect();
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (controls) controls.dispose();
      if (renderer) {
        renderer.dispose();
        renderer.forceContextLoss();
        if (renderer.domElement && renderer.domElement.parentNode) {
          renderer.domElement.parentNode.removeChild(renderer.domElement);
        }
      }
      if (scene) {
        scene.traverse((obj) => {
          if (obj.geometry) obj.geometry.dispose();
          if (obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach((m) => m.dispose());
            else obj.material.dispose();
          }
        });
      }
    };
  }, [initKey]);

  // ── 3. Day / Night Atmosphere Update ─────────────────────────────────────
  useEffect(() => {
    const scene = sceneRef.current;
    const { hemiLight, dirLight, fillLight } = lightsRef.current;
    if (!scene || !dirLight) return;

    if (isNight) {
      scene.background = new THREE.Color(0x0a1120);
      if (hemiLight) {
        hemiLight.color.setHex(0x1e293b);
        hemiLight.groundColor.setHex(0x0f172a);
        hemiLight.intensity = 0.5;
      }
      dirLight.color.setHex(0x93c5fd);
      dirLight.intensity = 0.65;
      dirLight.position.set(-18, 24, 18);
      if (fillLight) {
        fillLight.color.setHex(0x1e3a8a);
        fillLight.intensity = 0.35;
      }
    } else {
      scene.background = new THREE.Color(0xe8f2fb);
      if (hemiLight) {
        hemiLight.color.setHex(0xf0f9ff);
        hemiLight.groundColor.setHex(0x64748b);
        hemiLight.intensity = 1.25;
      }
      dirLight.color.setHex(0xfffaed);
      dirLight.intensity = 2.2;
      dirLight.position.set(22, 32, 24);
      if (fillLight) {
        fillLight.color.setHex(0xdbeafe);
        fillLight.intensity = 0.75;
      }
    }
  }, [isNight]);

  // ── 4. Rebuild Unified 3D Building Geometry ──────────────────────────────
  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene || !floorPlan) return;

    if (houseModelRef.current) {
      scene.remove(houseModelRef.current);
      houseModelRef.current.traverse((obj) => {
        if (obj.geometry) obj.geometry.dispose();
      });
    }

    const { model, roomAnchors } = buildUnifiedHouseModel({
      project,
      floorPlan,
      exteriorSelection,
      interiorSelections,
      options: {
        currentFloor,
        viewMode,
        isNight
      }
    });

    houseModelRef.current = model;
    scene.add(model);
    setRoomAnchorsList(roomAnchors);

    // Sync active room anchor
    if (activeRoomId) {
      const found = roomAnchors.find((r) => r.id === activeRoomId);
      setActiveRoomData(found || null);
    }
  }, [project, floorPlan, exteriorSelection, interiorSelections, currentFloor, viewMode, isNight]);

  // ── 5. Smooth Camera Navigation Helper ────────────────────────────────────
  const animateCameraTo = useCallback((targetPos, targetLookAt, duration = 1200, targetFov = null) => {
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    if (!camera || !controls) return;

    controls.enabled = false;

    cameraTweenRef.current = {
      startPos: camera.position.clone(),
      endPos: new THREE.Vector3(targetPos.x, targetPos.y, targetPos.z),
      startTarget: controls.target.clone(),
      endTarget: new THREE.Vector3(targetLookAt.x, targetLookAt.y, targetLookAt.z),
      startFov: camera.fov,
      endFov: targetFov || camera.fov,
      startTime: Date.now(),
      duration
    };
  }, []);

  // ── 6. Navigation Actions ────────────────────────────────────────────────
  const handleSelectRoom = (roomId) => {
    setActiveRoomId(roomId);
    if (!roomId || roomId === 'exterior') {
      setViewMode('exterior');
      setCurrentFloor('all');
      setActiveRoomData(null);
      animateCameraTo({ x: 16, y: 14, z: 20 }, { x: 0, y: 2, z: 0 }, 1200, 42);
      return;
    }

    const anchor = roomAnchorsList.find((r) => r.id === roomId);
    if (!anchor) return;

    setViewMode('interior');
    setActiveRoomData(anchor);

    // Isolate to the room's floor for cutaway visibility
    setCurrentFloor(anchor.floor);

    // Animate camera directly into room at eye level with wide architectural FOV
    animateCameraTo(anchor.cameraPos, anchor.targetPos, 1300, 68);
  };

  const handlePrevRoom = () => {
    if (roomAnchorsList.length === 0) return;
    const idx = roomAnchorsList.findIndex((r) => r.id === activeRoomId);
    const prevIdx = (idx - 1 + roomAnchorsList.length) % roomAnchorsList.length;
    handleSelectRoom(roomAnchorsList[prevIdx].id);
  };

  const handleNextRoom = () => {
    if (roomAnchorsList.length === 0) return;
    const idx = roomAnchorsList.findIndex((r) => r.id === activeRoomId);
    const nextIdx = (idx + 1) % roomAnchorsList.length;
    handleSelectRoom(roomAnchorsList[nextIdx].id);
  };

  const handleSwitchViewMode = (mode) => {
    setViewMode(mode);
    if (mode === 'exterior') {
      setActiveRoomId('');
      setActiveRoomData(null);
      setCurrentFloor('all');
      animateCameraTo({ x: 16, y: 14, z: 20 }, { x: 0, y: 2, z: 0 }, 1200, 42);
    } else if (mode === 'top_down') {
      animateCameraTo({ x: 0, y: 32, z: 0.1 }, { x: 0, y: 0, z: 0 }, 1000, 42);
    } else if (mode === 'interior') {
      const roomList = roomAnchorsList.length > 0 ? roomAnchorsList : (houseModelRef.current?.userData?.roomAnchors || []);
      const livingRoom = roomList.find(
        (r) => (r.type || '').includes('living') || (r.name || '').toLowerCase().includes('living')
      );
      const targetAnchor = (activeRoomId && roomList.find((r) => r.id === activeRoomId)) || livingRoom || roomList[0];
      if (targetAnchor) {
        handleSelectRoom(targetAnchor.id);
      }
    }
  };

  const handleResetCamera = () => {
    setIsRotating(false);
    setViewMode('exterior');
    setCurrentFloor('all');
    setActiveRoomId('');
    setActiveRoomData(null);
    animateCameraTo({ x: 16, y: 14, z: 20 }, { x: 0, y: 2, z: 0 }, 1000, 42);
  };

  // Group rooms by floor for dropdown
  const roomsByFloor = useMemo(() => {
    const groups = {};
    roomAnchorsList.forEach((r) => {
      const fName = r.floorName || (r.floor === 0 ? 'Ground Floor' : `Floor ${r.floor}`);
      if (!groups[fName]) groups[fName] = [];
      groups[fName].push(r);
    });
    return groups;
  }, [roomAnchorsList]);

  // WebGL Error State
  if (webGLError) {
    return (
      <div className="unified-3d-page-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ maxWidth: '480px', textAlign: 'center', padding: '2.5rem', background: '#0f172a', borderRadius: '14px', border: '1px solid #ef4444', boxShadow: '0 20px 50px rgba(0,0,0,0.6)' }}>
          <AlertTriangle size={40} color="#ef4444" style={{ marginBottom: '1rem' }} />
          <h3 style={{ color: '#f8fafc', margin: '0 0 0.5rem 0', fontSize: '1.2rem' }}>Interactive 3D WebGL Unavailable</h3>
          <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginBottom: '1.75rem', lineHeight: 1.5 }}>
            Your browser or device does not currently have WebGL hardware acceleration enabled. You can still generate and view full high-resolution architectural elevations and room perspectives using our independent 2D Architectural Studio.
          </p>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="unified-action-btn active"
              onClick={() => {
                setRenderModalTarget('exterior');
                setIsRenderModalOpen(true);
              }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                background: 'linear-gradient(135deg, #0284c7, #2563eb)',
                color: '#fff',
                borderRadius: '8px',
                fontWeight: 600,
                border: 'none',
                cursor: 'pointer'
              }}
            >
              <Camera size={16} /> Open Architectural Studio (2D Fallback)
            </button>
            <button
              className="unified-action-btn"
              onClick={() => {
                setWebGLError(false);
                setInitKey((k) => k + 1);
              }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 16px' }}
            >
              <RefreshCw size={14} /> Retry 3D
            </button>
          </div>
        </div>

        {/* Studio Modal accessible in Zero-WebGL fallback */}
        <ArchitecturalRenderModal
          isOpen={isRenderModalOpen}
          onClose={() => setIsRenderModalOpen(false)}
          project={project}
          floorPlan={floorPlan}
          exteriorSelection={exteriorSelection}
          interiorSelections={interiorSelections}
          initialTarget={renderModalTarget}
          initialRoomId={renderModalRoomId}
        />
      </div>
    );
  }

  return (
    <div className="unified-3d-page-container">
      {/* ── TOP NAVIGATION TOOLBAR ────────────────────────────────────────── */}
      <div className="unified-3d-toolbar" role="toolbar" aria-label="3D Viewer Controls">
        {/* Left: View Mode Pills */}
        <div className="unified-3d-toolbar-group">
          <div className="unified-pill-group" role="group" aria-label="View Perspective">
            <button
              className={`unified-pill-btn ${viewMode === 'exterior' ? 'is-active' : ''}`}
              onClick={() => handleSwitchViewMode('exterior')}
              aria-label="Exterior 3D View"
              aria-pressed={viewMode === 'exterior'}
            >
              <Home size={14} />
              <span>Exterior View</span>
            </button>
            <button
              className={`unified-pill-btn ${viewMode === 'interior' ? 'is-active' : ''}`}
              onClick={() => handleSwitchViewMode('interior')}
              aria-label="Walk-in Room View"
              aria-pressed={viewMode === 'interior'}
            >
              <DoorOpen size={14} />
              <span>Enter House</span>
            </button>
            <button
              className={`unified-pill-btn ${viewMode === 'top_down' ? 'is-active' : ''}`}
              onClick={() => handleSwitchViewMode('top_down')}
              aria-label="Top-down Cutaway View"
              aria-pressed={viewMode === 'top_down'}
            >
              <Compass size={14} />
              <span>Top View</span>
            </button>
          </div>

          {/* Floor Level Selector */}
          <div className="unified-pill-group" role="group" aria-label="Floor Cutaway Level">
            <button
              className={`unified-pill-btn ${currentFloor === 'all' ? 'is-active' : ''}`}
              onClick={() => {
                setCurrentFloor('all');
                if (viewMode === 'interior') {
                  setViewMode('exterior');
                  setActiveRoomId('');
                  setActiveRoomData(null);
                  animateCameraTo({ x: 16, y: 14, z: 20 }, { x: 0, y: 2, z: 0 }, 1100, 42);
                }
              }}
              aria-label="All Floors View"
              aria-pressed={currentFloor === 'all'}
            >
              <span>All Floors</span>
            </button>
            <button
              className={`unified-pill-btn ${currentFloor === 0 ? 'is-active' : ''}`}
              onClick={() => {
                setCurrentFloor(0);
                if (viewMode === 'interior') {
                  setViewMode('exterior');
                  setActiveRoomId('');
                  setActiveRoomData(null);
                }
                animateCameraTo({ x: 14, y: 10, z: 18 }, { x: 0, y: 1.5, z: 0 }, 1100, 42);
              }}
              aria-label="Ground Floor Cutaway"
              aria-pressed={currentFloor === 0}
            >
              <span>Ground Floor</span>
            </button>
            {project.floors > 1 && (
              <button
                className={`unified-pill-btn ${currentFloor === 1 ? 'is-active' : ''}`}
                onClick={() => {
                  setCurrentFloor(1);
                  if (viewMode === 'interior') {
                    setViewMode('exterior');
                    setActiveRoomId('');
                    setActiveRoomData(null);
                  }
                  animateCameraTo({ x: 14, y: 13, z: 18 }, { x: 0, y: 3.5, z: 0 }, 1100, 42);
                }}
                aria-label="First Floor Cutaway"
                aria-pressed={currentFloor === 1}
              >
                <span>First Floor</span>
              </button>
            )}
          </div>
        </div>

        {/* Right: Room Dropdown Selector, Day/Night & Camera Actions */}
        <div className="unified-3d-toolbar-group">
          {/* Room Selector Dropdown */}
          <select
            className="unified-select"
            value={activeRoomId || 'exterior'}
            onChange={(e) => handleSelectRoom(e.target.value)}
            aria-label="Select Room to Walk In"
          >
            <option value="exterior">📍 Select Room to Inspect...</option>
            {Object.entries(roomsByFloor).map(([fName, rooms]) => (
              <optgroup key={fName} label={fName}>
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name} ({r.area} sq ft)
                  </option>
                ))}
              </optgroup>
            ))}
          </select>

          {/* Day / Night Mood Toggle */}
          <button
            className={`unified-action-btn ${isNight ? 'active' : ''}`}
            onClick={() => setIsNight(!isNight)}
            title={isNight ? 'Switch to Natural Daylight' : 'Switch to Luminous Night Mood'}
            aria-label={isNight ? 'Switch to Natural Daylight' : 'Switch to Luminous Night Mood'}
          >
            {isNight ? <Moon size={14} color="#f59e0b" /> : <Sun size={14} color="#38bdf8" />}
            <span>{isNight ? 'Night' : 'Daylight'}</span>
          </button>

          {/* Turntable Auto-Rotate */}
          <button
            className={`unified-action-btn ${isRotating ? 'active' : ''}`}
            onClick={() => setIsRotating(!isRotating)}
            title="Toggle 360° Turntable Rotation"
            aria-label="Toggle 360° Turntable Rotation"
            aria-pressed={isRotating}
          >
            <RotateCw size={14} className={isRotating ? 'spin' : ''} />
            <span>Orbit</span>
          </button>

          {/* Reset View */}
          <button
            className="unified-action-btn"
            onClick={handleResetCamera}
            title="Reset Camera to Exterior Perspective"
            aria-label="Reset Camera Perspective"
          >
            <RotateCcw size={14} />
            <span>Reset</span>
          </button>

          {/* Architectural Photo Render Studio */}
          <button
            className="unified-action-btn active"
            onClick={() => {
              setRenderModalTarget(viewMode === 'interior' && activeRoomData ? 'interior' : 'exterior');
              setRenderModalRoomId(activeRoomData?.id || null);
              setIsRenderModalOpen(true);
            }}
            title="Launch Realistic Architectural Rendering Studio"
            aria-label="Launch Realistic Architectural Rendering Studio"
            style={{
              background: 'linear-gradient(135deg, #0284c7, #2563eb)',
              color: '#ffffff',
              borderColor: '#0284c7',
              fontWeight: 600,
              boxShadow: '0 2px 10px rgba(2, 132, 199, 0.4)'
            }}
          >
            <Camera size={14} />
            <span>Photo Render</span>
          </button>
        </div>
      </div>

      {/* ── 3D CANVAS VIEWPORT ────────────────────────────────────────────── */}
      <div className="unified-3d-viewport">
        <div ref={mountRef} className="unified-3d-canvas-container" />

        {/* Top-Left Status HUD */}
        <div className="unified-viewport-badge">
          <div className="unified-badge-dot" />
          <span>
            {viewMode === 'interior' && activeRoomData
              ? `ROOM INSPECTION: ${activeRoomData.name.toUpperCase()}`
              : viewMode === 'top_down'
              ? 'TOP-DOWN CUTAWAY FLOOR PLAN'
              : 'UNIFIED 3D HOUSE VISUALIZATION'}
          </span>
          <span style={{ opacity: 0.6 }}>•</span>
          <span style={{ color: '#38bdf8' }}>
            {currentFloor === 'all'
              ? `Full Envelope (${project.plot_width || 30}′ × ${project.plot_length || 40}′)`
              : currentFloor === 0
              ? 'Ground Level Cutaway'
              : 'First Floor Cutaway'}
          </span>
        </div>

        {/* Floating Room Inspector HUD (When inside a room) */}
        {viewMode === 'interior' && activeRoomData && (
          <div className="unified-room-inspector-card" role="region" aria-label="Room Inspector Details">
            <div className="room-inspector-header">
              <h4 className="room-inspector-title">
                <Sparkles size={16} color="#38bdf8" />
                {activeRoomData.name}
              </h4>
              <span className="room-inspector-pill">{activeRoomData.floorName}</span>
            </div>

            <div className="room-inspector-grid">
              <div className="room-inspector-item">
                <span className="room-inspector-item-label">Area</span>
                <span className="room-inspector-item-val">{activeRoomData.area} sq ft</span>
              </div>
              <div className="room-inspector-item">
                <span className="room-inspector-item-label">Design Theme</span>
                <span className="room-inspector-item-val">
                  {activeRoomData.savedSelection?.design_name || 'Civil Baseline'}
                </span>
              </div>
              <div className="room-inspector-item">
                <span className="room-inspector-item-label">Wall Finish</span>
                <span className="room-inspector-item-val" style={{ textTransform: 'capitalize' }}>
                  {activeRoomData.savedSelection?.wall_finish_choice
                    ? activeRoomData.savedSelection.wall_finish_choice.replace(/_/g, ' ')
                    : 'Smooth Plaster'}
                </span>
              </div>
              <div className="room-inspector-item">
                <span className="room-inspector-item-label">Flooring Material</span>
                <span className="room-inspector-item-val" style={{ textTransform: 'capitalize' }}>
                  {activeRoomData.savedSelection?.flooring_choice
                    ? activeRoomData.savedSelection.flooring_choice.replace(/_/g, ' ')
                    : 'Vitrified Tiles'}
                </span>
              </div>
            </div>

            {/* Room-to-Room Walkthrough Navigation Row */}
            <div className="room-inspector-nav-row" style={{ display: 'flex', gap: '8px', justifyContent: 'space-between' }}>
              <button
                className="room-inspector-exit-btn"
                onClick={handlePrevRoom}
                style={{ flex: 1, justifyContent: 'center' }}
                aria-label="Navigate to Previous Room"
              >
                <ChevronLeft size={13} />
                <span>Prev Room</span>
              </button>
              <button
                className="room-inspector-exit-btn"
                onClick={handleNextRoom}
                style={{ flex: 1, justifyContent: 'center' }}
                aria-label="Navigate to Next Room"
              >
                <span>Next Room</span>
                <ChevronRight size={13} />
              </button>
            </div>

            <div className="room-inspector-actions">
              <button
                className="room-inspector-link-btn"
                style={{ background: 'rgba(2, 132, 199, 0.18)', borderColor: '#0284c7', color: '#38bdf8' }}
                onClick={() => {
                  setRenderModalTarget('interior');
                  setRenderModalRoomId(activeRoomData.id);
                  setIsRenderModalOpen(true);
                }}
                aria-label="Render Room Photo in Studio"
              >
                <Camera size={13} />
                <span>Render Room Photo</span>
              </button>

              <button
                className="room-inspector-link-btn"
                onClick={() => navigate(`/projects/${projectId}/interior`)}
                aria-label="Customize room in Interior Studio"
              >
                <Palette size={13} />
                <span>Customize in Interior Studio</span>
                <ExternalLink size={12} />
              </button>

              <button
                className="room-inspector-exit-btn"
                onClick={() => handleSelectRoom('exterior')}
                aria-label="Exit Room Inspection"
              >
                <X size={12} />
                <span>Exit Room</span>
              </button>
            </div>
          </div>
        )}

        {/* Viewport Control Instructions */}
        <div className="unified-viewport-hint">
          <Eye size={12} />
          <span>Left-Click Drag to Orbit • Right-Click Drag to Pan • Scroll to Zoom</span>
        </div>
      </div>

      {/* ── ARCHITECTURAL RENDERING STUDIO MODAL ────────────────────────────── */}
      <ArchitecturalRenderModal
        isOpen={isRenderModalOpen}
        onClose={() => setIsRenderModalOpen(false)}
        project={project}
        floorPlan={floorPlan}
        exteriorSelection={exteriorSelection}
        interiorSelections={interiorSelections}
        initialTarget={renderModalTarget}
        initialRoomId={renderModalRoomId}
      />
    </div>
  );
}
