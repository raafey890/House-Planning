/**
 * ArchitecturalRenderModal.jsx — Phase 6K & 6K.1
 *
 * Professional Architectural Rendering Studio Modal.
 * Produces photorealistic exterior and room-specific visualizations that preserve
 * approved architectural geometry.
 *
 * Capabilities:
 * - Robust Dual-Engine Architecture:
 *   1. Geometry-Verified 3D PBR (Three.js WebGL with memory bounds and context cleanup)
 *   2. Independent Geometry-Verified 2D Vector (Zero-WebGL Fallback, 100% reliable)
 *   3. Optional AI Concept Visualizer (Artistic Interpretation with honest diagnostics)
 * - Multi-environment lighting (Natural Daylight, Golden Hour Sunset, Architectural Night Mood)
 * - Exterior Elevation (Front, 3/4 Isometric Perspective, Street View) & Room-Specific Interior Perspectives
 * - Save to Project & Instant High-Res PNG Download (never saves blank/black stubs)
 * - Saved Renders Gallery Drawer
 */

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  Camera,
  Sparkles,
  Download,
  Save,
  Sun,
  Sunset,
  Moon,
  CheckCircle2,
  AlertTriangle,
  X,
  Layers,
  FolderArchive,
  RefreshCw,
  Info,
  ShieldCheck
} from 'lucide-react';

import { buildArchitecturalRenderingInput } from '../../services/architecturalRenderingInputBuilder';
import {
  renderArchitecturalScene,
  generateAIConceptRender,
  saveProjectRender,
  getSavedProjectRenders,
  downloadRenderAsPNG,
  checkWebGLCapability,
  isRenderDataUrlValid
} from '../../services/architecturalRenderEngine';

import '../../styles/components/architectural-render-modal.css';

const ArchitecturalRenderModal = ({
  isOpen,
  onClose,
  project,
  floorPlan,
  exteriorSelection,
  interiorSelections,
  initialTarget = 'exterior',
  initialRoomId = null
}) => {
  // Probe WebGL support on mount
  const webglCapability = useMemo(() => checkWebGLCapability(), []);

  // Rendering Spec derived from authoritative geometry
  const renderingInput = useMemo(() => {
    if (!isOpen || !project?.id) return null;
    try {
      return buildArchitecturalRenderingInput({
        project,
        floorPlan,
        exteriorSelection,
        interiorSelections
      });
    } catch (e) {
      console.error('Failed to construct rendering input:', e);
      return null;
    }
  }, [isOpen, project, floorPlan, exteriorSelection, interiorSelections]);

  // Studio Controls State
  // Default to 2D vector fallback if WebGL is unavailable on device
  const [engineMode, setEngineMode] = useState(
    webglCapability.supported ? 'pbr' : 'canvas_2d'
  );
  const [targetType, setTargetType] = useState(initialTarget); // 'exterior' | 'interior'
  const [selectedRoomId, setSelectedRoomId] = useState(initialRoomId || '');
  const [lightingMode, setLightingMode] = useState('daylight'); // 'daylight' | 'golden_hour' | 'night'
  const [viewAngle, setViewAngle] = useState('perspective'); // 'perspective' | 'front' | 'street'
  const [quality, setQuality] = useState('high'); // 'preview' | 'high' | 'presentation'

  // Render Execution State
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressText, setProgressText] = useState('');
  const [currentRender, setCurrentRender] = useState(null);
  const [errorNotice, setErrorNotice] = useState(null);
  const [isSaved, setIsSaved] = useState(false);

  // Gallery Drawer State
  const [isGalleryOpen, setIsGalleryOpen] = useState(false);
  const [savedRenders, setSavedRenders] = useState([]);

  // Container ref for layout lifecycle
  const viewportRef = useRef(null);

  // Load saved project renders
  useEffect(() => {
    if (project?.id) {
      setSavedRenders(getSavedProjectRenders(project.id));
    }
  }, [project?.id]);

  // Sync initial target
  useEffect(() => {
    if (isOpen) {
      setTargetType(initialTarget);
      if (initialRoomId) {
        setSelectedRoomId(initialRoomId);
      } else if (renderingInput?.rooms?.length > 0 && !selectedRoomId) {
        const livingRoom = renderingInput.rooms.find((r) => r.type.includes('living')) || renderingInput.rooms[0];
        setSelectedRoomId(livingRoom.id);
      }
    }
  }, [isOpen, initialTarget, initialRoomId, renderingInput]);

  // Execute Render Function
  const handleStartRender = useCallback(async () => {
    if (!renderingInput) return;

    setIsRendering(true);
    setProgress(5);
    setProgressText('Preparing Scene Specifications...');
    setErrorNotice(null);
    setIsSaved(false);

    try {
      if (engineMode === 'pbr' || engineMode === 'canvas_2d') {
        const result = await renderArchitecturalScene({
          renderingInput,
          targetType,
          roomId: targetType === 'interior' ? selectedRoomId : null,
          lightingMode,
          quality,
          viewAngle,
          engineType: engineMode,
          onProgress: (pct, msg) => {
            setProgress(pct);
            setProgressText(msg);
          }
        });

        if (result && isRenderDataUrlValid(result.dataUrl)) {
          setCurrentRender(result);
        } else {
          throw new Error('Generated render was invalid or empty. Please retry.');
        }
      } else {
        // AI Concept Generation
        setProgress(30);
        setProgressText('Contacting Neural Architecture Service...');
        const result = await generateAIConceptRender({
          renderingInput,
          targetType,
          roomId: targetType === 'interior' ? selectedRoomId : null,
          lightingMode,
          viewAngle
        });

        if (result.status === 'success' && isRenderDataUrlValid(result.dataUrl)) {
          setProgress(100);
          setProgressText('AI Concept Imagery Ready!');
          setCurrentRender(result);
        } else {
          setErrorNotice(result.errorDetail || 'AI Image generation failed.');
        }
      }
    } catch (err) {
      console.error('Rendering error:', err);
      setErrorNotice(err.message || 'An unexpected error occurred during rendering.');
    } finally {
      setIsRendering(false);
    }
  }, [renderingInput, engineMode, targetType, selectedRoomId, lightingMode, quality, viewAngle]);

  // Auto-render on initial open once viewport container is sized
  useEffect(() => {
    let animId;
    if (isOpen && renderingInput && !currentRender && !isRendering) {
      // Defer execution by a frame to allow modal container mount and layout stabilization
      animId = requestAnimationFrame(() => {
        handleStartRender();
      });
    }
    return () => {
      if (animId) cancelAnimationFrame(animId);
    };
  }, [isOpen, renderingInput]);

  // Save Render to Project
  const handleSaveRender = () => {
    if (!project?.id || !currentRender || !isRenderDataUrlValid(currentRender.dataUrl)) return;
    const updated = saveProjectRender(project.id, currentRender);
    setSavedRenders(updated);
    setIsSaved(true);
  };

  // Download Render as PNG
  const handleDownload = () => {
    if (!currentRender || !isRenderDataUrlValid(currentRender.dataUrl)) return;
    downloadRenderAsPNG(currentRender);
  };

  // Safe fallback switch handler
  const handleSwitchToLocalEngine = () => {
    setErrorNotice(null);
    if (webglCapability.supported) {
      setEngineMode('pbr');
    } else {
      setEngineMode('canvas_2d');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="render-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="render-modal-title">
      <div className="render-modal-container">
        {/* ── TOP HEADER ──────────────────────────────────────────────────── */}
        <div className="render-modal-header">
          <div className="render-modal-title-group">
            <div className="render-modal-title-icon">
              <Camera size={20} />
            </div>
            <div>
              <h2 id="render-modal-title" className="render-modal-title">
                Architectural Rendering Studio
              </h2>
              <p className="render-modal-subtitle">
                {project.name} • {renderingInput?.site.plotWidth} × {renderingInput?.site.plotLength} ft • Grounded in Approved Architecture
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              className="render-btn-secondary"
              onClick={() => setIsGalleryOpen(!isGalleryOpen)}
              title="View previously saved renders"
            >
              <FolderArchive size={14} />
              <span>Saved Renders ({savedRenders.length})</span>
            </button>
            <button className="render-modal-close-btn" onClick={onClose} aria-label="Close Studio">
              <X size={20} />
            </button>
          </div>
        </div>

        {/* ── STUDIO WORKSPACE ─────────────────────────────────────────────── */}
        <div className="render-modal-body">
          {/* LEFT: Configuration Sidebar */}
          <div className="render-config-sidebar">
            {/* 1. Rendering Engine Selector */}
            <div className="render-config-section">
              <label className="render-config-label">
                <Layers size={13} />
                <span>Rendering Engine</span>
              </label>
              <div className="render-engine-tabs">
                <button
                  className={`render-engine-tab ${engineMode === 'pbr' ? 'is-active' : ''}`}
                  onClick={() => setEngineMode('pbr')}
                  title={webglCapability.supported ? 'Three.js 3D PBR WebGL Engine' : 'WebGL unavailable on this device'}
                >
                  <span>3D PBR</span>
                  <span style={{ fontSize: '0.62rem', opacity: 0.75 }}>
                    {webglCapability.supported ? 'WebGL' : 'Disabled'}
                  </span>
                </button>
                <button
                  className={`render-engine-tab ${engineMode === 'canvas_2d' ? 'is-active' : ''}`}
                  onClick={() => setEngineMode('canvas_2d')}
                  title="Independent 2D Vector Architectural Engine (Zero-WebGL, 100% Guaranteed)"
                >
                  <span>2D Vector</span>
                  <span style={{ fontSize: '0.62rem', opacity: 0.75 }}>Zero-WebGL</span>
                </button>
                <button
                  className={`render-engine-tab ${engineMode === 'ai_concept' ? 'is-active' : ''}`}
                  onClick={() => setEngineMode('ai_concept')}
                  title="Generative AI Concept Art (Artistic Interpretation)"
                >
                  <span>AI Concept</span>
                  <span style={{ fontSize: '0.62rem', opacity: 0.75 }}>Artistic</span>
                </button>
              </div>

              {/* Engine Description / Diagnostic Note */}
              <span style={{ fontSize: '0.68rem', color: engineMode === 'ai_concept' ? '#fbbf24' : '#4ade80', marginTop: '2px' }}>
                {engineMode === 'pbr' && webglCapability.supported && '✓ 100% faithful to approved 3D walls, cantilevers, and finishes (Three.js WebGL)'}
                {engineMode === 'pbr' && !webglCapability.supported && '⚠ WebGL unavailable. Will automatically engage 2D Architectural Fallback.'}
                {engineMode === 'canvas_2d' && '✓ 100% faithful to approved floor plan & finishes (Independent 2D Vector Engine, Zero-WebGL)'}
                {engineMode === 'ai_concept' && '⚠ Generative concept visualization. Architectural dimensions not verified.'}
              </span>
            </div>

            {/* 2. Scene Target (Exterior Facade vs Specific Room) */}
            <div className="render-config-section">
              <label className="render-config-label">
                <Sparkles size={13} />
                <span>Scene Subject</span>
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '6px' }}>
                <button
                  className={`render-quality-btn ${targetType === 'exterior' ? 'is-active' : ''}`}
                  onClick={() => setTargetType('exterior')}
                >
                  <span className="render-quality-title">Exterior Facade</span>
                  <span className="render-quality-res">Full Elevation</span>
                </button>
                <button
                  className={`render-quality-btn ${targetType === 'interior' ? 'is-active' : ''}`}
                  onClick={() => setTargetType('interior')}
                >
                  <span className="render-quality-title">Room Interior</span>
                  <span className="render-quality-res">Specific Space</span>
                </button>
              </div>

              {/* Room Dropdown (if interior) */}
              {targetType === 'interior' && (
                <select
                  className="render-select-input"
                  value={selectedRoomId}
                  onChange={(e) => setSelectedRoomId(e.target.value)}
                  aria-label="Select Room to Render"
                >
                  {renderingInput?.rooms.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.floorName} — {r.name} ({r.width} × {r.length} ft, {r.area} sq ft)
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* 3. Lighting & Atmosphere */}
            <div className="render-config-section">
              <label className="render-config-label">
                <Sun size={13} />
                <span>Atmosphere & Lighting</span>
              </label>
              <div className="render-lighting-grid">
                <button
                  className={`render-lighting-btn ${lightingMode === 'daylight' ? 'is-active' : ''}`}
                  onClick={() => setLightingMode('daylight')}
                >
                  <Sun size={16} color="#38bdf8" />
                  <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>Daylight</span>
                </button>
                <button
                  className={`render-lighting-btn ${lightingMode === 'golden_hour' ? 'is-active' : ''}`}
                  onClick={() => setLightingMode('golden_hour')}
                >
                  <Sunset size={16} color="#f59e0b" />
                  <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>Sunset</span>
                </button>
                <button
                  className={`render-lighting-btn ${lightingMode === 'night' ? 'is-active' : ''}`}
                  onClick={() => setLightingMode('night')}
                >
                  <Moon size={16} color="#818cf8" />
                  <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>Night Mood</span>
                </button>
              </div>
            </div>

            {/* 4. Perspective / Angle (for exterior) */}
            {targetType === 'exterior' && (
              <div className="render-config-section">
                <label className="render-config-label">
                  <Camera size={13} />
                  <span>Perspective & Angle</span>
                </label>
                <select
                  className="render-select-input"
                  value={viewAngle}
                  onChange={(e) => setViewAngle(e.target.value)}
                >
                  <option value="perspective">3/4 Isometric Showcase</option>
                  <option value="front">Frontal Eye-Level Perspective</option>
                  <option value="street">Low Angle Street View</option>
                </select>
              </div>
            )}

            {/* 5. Output Quality Profile (for Local Engines) */}
            {engineMode !== 'ai_concept' && (
              <div className="render-config-section">
                <label className="render-config-label">
                  <Info size={13} />
                  <span>Output Quality Preset</span>
                </label>
                <div className="render-quality-grid">
                  <button
                    className={`render-quality-btn ${quality === 'preview' ? 'is-active' : ''}`}
                    onClick={() => setQuality('preview')}
                  >
                    <span className="render-quality-title">Preview</span>
                    <span className="render-quality-res">720p • Fast</span>
                  </button>
                  <button
                    className={`render-quality-btn ${quality === 'high' ? 'is-active' : ''}`}
                    onClick={() => setQuality('high')}
                  >
                    <span className="render-quality-title">High Quality</span>
                    <span className="render-quality-res">1080p Full HD</span>
                  </button>
                  <button
                    className={`render-quality-btn ${quality === 'presentation' ? 'is-active' : ''}`}
                    onClick={() => setQuality('presentation')}
                  >
                    <span className="render-quality-title">Presentation</span>
                    <span className="render-quality-res">4K UHD</span>
                  </button>
                </div>
                <span style={{ fontSize: '0.68rem', color: '#94a3b8' }}>
                  {quality === 'presentation'
                    ? 'Ultra high-definition 4K master render (3840 × 2160) with fine architectural detailing.'
                    : quality === 'high'
                    ? 'Full HD 1080p render (1920 × 1080) with soft shadow filters.'
                    : 'Instant 720p preview render (1280 × 720) for rapid composition review.'}
                </span>
              </div>
            )}

            {/* Render Action Button */}
            <button
              className="render-action-primary"
              onClick={handleStartRender}
              disabled={isRendering}
            >
              {isRendering ? (
                <>
                  <RefreshCw size={16} className="spin" />
                  <span>Rendering...</span>
                </>
              ) : (
                <>
                  <Camera size={16} />
                  <span>Render Architectural Photo</span>
                </>
              )}
            </button>
          </div>

          {/* RIGHT: High-Resolution Preview Viewport */}
          <div ref={viewportRef} className="render-preview-viewport">
            {/* Progress Overlay */}
            {isRendering && (
              <div className="render-progress-overlay">
                <div className="render-progress-bar-bg">
                  <div className="render-progress-bar-fill" style={{ width: `${progress}%` }} />
                </div>
                <span className="render-progress-text">{progressText} ({progress}%)</span>
              </div>
            )}

            {/* Error Diagnostics Banner */}
            {errorNotice && !isRendering && (
              <div style={{ margin: '1.5rem', padding: '1.25rem', background: '#450a0a', border: '1px solid #ef4444', borderRadius: '10px' }}>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                  <AlertTriangle size={20} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div>
                    <h4 style={{ margin: '0 0 4px 0', color: '#fee2e2', fontSize: '0.9rem' }}>
                      {engineMode === 'ai_concept' ? 'External AI Service Notice' : 'Rendering Notice'}
                    </h4>
                    <p style={{ margin: 0, color: '#fca5a5', fontSize: '0.78rem' }}>{errorNotice}</p>
                    <button
                      className="render-btn-accent"
                      onClick={handleSwitchToLocalEngine}
                      style={{ marginTop: '10px', padding: '6px 12px', fontSize: '0.75rem' }}
                    >
                      Switch to Local Geometry-Verified Engine
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Main Render Canvas / Image */}
            <div className="render-canvas-holder">
              {currentRender?.dataUrl && isRenderDataUrlValid(currentRender.dataUrl) ? (
                <>
                  <img
                    src={currentRender.dataUrl}
                    alt={currentRender.targetName || 'Architectural Render'}
                    className="render-output-image"
                  />

                  {/* Verification Pill */}
                  <div className={`render-verification-pill ${currentRender.isGeometryVerified ? 'verified' : 'concept'}`}>
                    {currentRender.isGeometryVerified ? (
                      <>
                        <CheckCircle2 size={14} color="#4ade80" />
                        <span>
                          {currentRender.engineType === 'canvas_2d' || currentRender.isFallbackEngine
                            ? 'Geometry-Verified 2D Architectural Render (Zero-WebGL)'
                            : 'Geometry-Verified 3D Architectural Render (PBR)'}
                        </span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle size={14} color="#fbbf24" />
                        <span>AI Concept Visualization (Artistic Interpretation)</span>
                      </>
                    )}
                  </div>
                </>
              ) : !isRendering ? (
                <div style={{ textAlign: 'center', color: '#94a3b8', padding: '3rem' }}>
                  <Camera size={48} style={{ opacity: 0.35, marginBottom: '1rem', color: '#38bdf8' }} />
                  <h3 style={{ color: '#f8fafc', fontSize: '1.1rem', marginBottom: '0.5rem' }}>Ready to Render</h3>
                  <p style={{ maxWidth: '380px', margin: '0 auto 1.5rem auto', fontSize: '0.82rem', color: '#64748b' }}>
                    Select your scene subject and atmosphere on the left, then click Render to produce high-resolution architectural photography.
                  </p>
                  <button
                    className="render-action-primary"
                    onClick={handleStartRender}
                    style={{ maxWidth: '280px', margin: '0 auto' }}
                  >
                    <Camera size={16} />
                    <span>Render Architectural Photo</span>
                  </button>
                </div>
              ) : null}
            </div>

            {/* Bottom Status & Export Bar */}
            {currentRender && isRenderDataUrlValid(currentRender.dataUrl) && (
              <div className="render-output-toolbar">
                <div className="render-metadata-chips">
                  <span className="render-chip">{currentRender.targetName}</span>
                  <span className="render-chip">{currentRender.resolution}</span>
                  <span className="render-chip" style={{ textTransform: 'capitalize' }}>
                    {currentRender.lightingMode?.replace('_', ' ')}
                  </span>
                  {currentRender.isFallbackEngine && (
                    <span className="render-chip" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
                      2D Vector Fallback
                    </span>
                  )}
                  {currentRender.metadata?.quality_notice && (
                    <span className="render-chip" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24', border: '1px solid rgba(245, 158, 11, 0.4)' }}>
                      ⚠ 1080p Clamped (GPU Limit)
                    </span>
                  )}
                  {currentRender.metadata?.room_dimensions && (
                    <span className="render-chip">{currentRender.metadata.room_dimensions}</span>
                  )}
                </div>

                <div className="render-output-actions">
                  <button
                    className="render-btn-secondary"
                    onClick={handleSaveRender}
                    disabled={isSaved || !isRenderDataUrlValid(currentRender.dataUrl)}
                    title={isSaved ? 'Saved to project storage' : 'Save render to project'}
                  >
                    <Save size={14} />
                    <span>{isSaved ? 'Saved to Project ✓' : 'Save to Project'}</span>
                  </button>

                  <button
                    className="render-btn-accent"
                    onClick={handleDownload}
                    disabled={!isRenderDataUrlValid(currentRender.dataUrl)}
                    title="Export full resolution PNG image"
                  >
                    <Download size={14} />
                    <span>Export PNG</span>
                  </button>
                </div>
              </div>
            )}

            {/* Saved Renders Gallery Drawer */}
            {isGalleryOpen && (
              <div className="render-gallery-drawer">
                <div className="render-gallery-header">
                  <h3 className="render-gallery-title">Project Saved Renders</h3>
                  <button
                    className="render-modal-close-btn"
                    onClick={() => setIsGalleryOpen(false)}
                    aria-label="Close Gallery"
                  >
                    <X size={16} />
                  </button>
                </div>

                <div className="render-gallery-list">
                  {savedRenders.length === 0 ? (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b', fontSize: '0.8rem' }}>
                      No saved renders yet. Click "Save to Project" to archive your architectural photos.
                    </div>
                  ) : (
                    savedRenders.map((item) => (
                      <div
                        key={item.id}
                        className="render-gallery-item"
                        onClick={() => {
                          setCurrentRender(item);
                          setIsSaved(true);
                        }}
                      >
                        <img src={item.dataUrl} alt={item.targetName} className="render-gallery-thumb" />
                        <div className="render-gallery-info">
                          <span className="render-gallery-item-name">{item.targetName}</span>
                          <span className="render-gallery-item-meta">
                            {item.resolution} • {item.lightingMode}
                          </span>
                          <span className="render-gallery-item-meta" style={{ opacity: 0.6 }}>
                            {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitecturalRenderModal;
