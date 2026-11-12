import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Download,
  Layers,
  Compass,
  Palette,
  Eye,
  Maximize2,
  FileCode,
  Image as ImageIcon,
  CheckCircle2,
  Info,
  Sliders,
  Move
} from 'lucide-react';
import { generateExteriorElevationSvg } from '../../services/exteriorBlueprintGenerator';
import { exteriorDesignService } from '../../services/exteriorDesignService';

export default function ExteriorBlueprintViewer({
  project = {},
  selectedDesign = {},
  customColors = {},
  customMaterials = {},
  lightingMode = 'daylight',
  initialViewAngle = 'front',
  height = '540px',
  showToolbar = true
}) {
  const [viewAngle, setViewAngle] = useState(initialViewAngle);
  const [themeMode, setThemeMode] = useState('blueprint'); // 'blueprint' | 'rendered'
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [serverSvg, setServerSvg] = useState(null);
  const [loading, setLoading] = useState(false);

  const containerRef = useRef(null);

  // 1. Fetch server-generated SVG if backend is accessible, fallback to client generator
  useEffect(() => {
    let isMounted = true;
    async function fetchServerPreview() {
      if (!selectedDesign?.id || !project) return;
      setLoading(true);
      try {
        const res = await exteriorDesignService.generatePersonalizedPreview({
          project_id: project.id || 'current_project',
          design_id: selectedDesign.id,
          plot_width: project.plot_width || 30.0,
          plot_length: project.plot_length || 40.0,
          floors: project.floors || 2,
          plot_facing: project.facing || 'South',
          view_angle: viewAngle,
          lighting_mode: lightingMode,
          colors: customColors,
          materials: customMaterials
        });
        if (isMounted && res?.status === 'success' && res?.svg_content) {
          setServerSvg(res.svg_content);
        }
      } catch (err) {
        // Fallback gracefully to client generator with zero disruption
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchServerPreview();
    return () => { isMounted = false; };
  }, [project, selectedDesign, customColors, customMaterials, lightingMode, viewAngle]);

  // 2. High-precision client elevation SVG
  const clientSvg = useMemo(() => {
    return generateExteriorElevationSvg({
      project,
      selectedDesign,
      customColors,
      customMaterials,
      lightingMode,
      viewAngle,
      themeMode
    });
  }, [project, selectedDesign, customColors, customMaterials, lightingMode, viewAngle, themeMode]);

  // Determine active SVG to render:
  // If in blueprint mode, use high-contrast client blueprint generator.
  // If in rendered mode, use server SVG if available, or client rendered generator.
  const activeSvg = useMemo(() => {
    if (themeMode === 'blueprint') return clientSvg;
    return serverSvg || clientSvg;
  }, [themeMode, serverSvg, clientSvg]);

  // 3. Pan and Zoom Interactions
  const handleZoomIn = () => setZoom(z => Math.min(2.5, Number((z + 0.2).toFixed(1))));
  const handleZoomOut = () => setZoom(z => Math.max(0.6, Number((z - 0.2).toFixed(1))));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e) => {
    if (e.button !== 0) return; // Only left-click drag
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY * -0.0015;
    setZoom(z => Math.min(2.5, Math.max(0.6, Number((z + delta).toFixed(2)))));
  };

  // 4. Export Clean SVG
  const handleExportSvg = () => {
    if (!activeSvg) return;
    const blob = new Blob([activeSvg], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${project.name || 'Project'}_${selectedDesign.id || 'elevation'}_${viewAngle}_${themeMode}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // 5. Export Clean High-Resolution PNG via Canvas
  const handleExportPng = () => {
    if (!activeSvg) return;
    const canvas = document.createElement('canvas');
    canvas.width = 2000;
    canvas.height = 1360;
    const ctx = canvas.getContext('2d');
    const img = new Image();
    const svgBlob = new Blob([activeSvg], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      ctx.fillStyle = themeMode === 'blueprint' ? '#0a192f' : '#0f172a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);

      const pngUrl = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = pngUrl;
      a.download = `${project.name || 'Project'}_${selectedDesign.id || 'elevation'}_${viewAngle}_${themeMode}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
    img.src = url;
  };

  const plotW = project.plot_width || 30;
  const plotL = project.plot_length || 40;
  const floors = project.floors || 2;
  const facing = project.facing || 'South';

  return (
    <div className="exterior-blueprint-viewer-root">
      {/* ── TOP DRAWING CONTROLS TOOLBAR ─────────────────────────────────── */}
      {showToolbar && (
        <div className="elevation-toolbar">
          {/* Left: View Angle & Theme Mode Switchers */}
          <div className="elevation-toolbar-group">
            <div className="elevation-segmented-pills">
              <button
                className={`elevation-pill-btn ${viewAngle === 'front' ? 'is-active' : ''}`}
                onClick={() => setViewAngle('front')}
                title="Front Elevation (Orthographic)"
              >
                Front View
              </button>
              <button
                className={`elevation-pill-btn ${viewAngle === 'front_left' ? 'is-active' : ''}`}
                onClick={() => setViewAngle('front_left')}
                title="Front-Left 3/4 Isometric Perspective"
              >
                3/4 Left View
              </button>
              <button
                className={`elevation-pill-btn ${viewAngle === 'front_right' ? 'is-active' : ''}`}
                onClick={() => setViewAngle('front_right')}
                title="Front-Right 3/4 Isometric Perspective"
              >
                3/4 Right View
              </button>
            </div>

            <div className="elevation-segmented-pills">
              <button
                className={`elevation-pill-btn ${themeMode === 'blueprint' ? 'is-active' : ''}`}
                onClick={() => setThemeMode('blueprint')}
                title="Technical Drafting Blueprint with Grid & Datums"
              >
                <Compass size={13} style={{ marginRight: '4px' }} />
                Blueprint Drafting
              </button>
              <button
                className={`elevation-pill-btn ${themeMode === 'rendered' ? 'is-active' : ''}`}
                onClick={() => setThemeMode('rendered')}
                title="Photorealistic Architectural Vector Color Elevation"
              >
                <Palette size={13} style={{ marginRight: '4px' }} />
                Color Elevation
              </button>
            </div>
          </div>

          {/* Right: Zoom & Export Controls */}
          <div className="elevation-toolbar-group">
            <div className="elevation-zoom-controls">
              <button className="elevation-tool-btn" onClick={handleZoomOut} title="Zoom Out (-)">
                <ZoomOut size={14} />
              </button>
              <span className="elevation-zoom-tag">{Math.round(zoom * 100)}%</span>
              <button className="elevation-tool-btn" onClick={handleZoomIn} title="Zoom In (+)">
                <ZoomIn size={14} />
              </button>
              <button className="elevation-tool-btn" onClick={handleReset} title="Reset View (1:1)">
                <RotateCcw size={13} />
              </button>
            </div>

            <div className="elevation-export-actions">
              <button
                className="elevation-action-btn"
                onClick={handleExportSvg}
                title="Export Clean Architectural Vector Drawing as SVG"
              >
                <FileCode size={13} /> SVG
              </button>
              <button
                className="elevation-action-btn"
                onClick={handleExportPng}
                title="Export Clean High-Resolution 2000px Drawing as PNG"
              >
                <Download size={13} /> PNG
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── DRAWING CANVAS VIEWPORT ─────────────────────────────────────── */}
      <div
        className="elevation-canvas-container"
        ref={containerRef}
        style={{ height }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        onDoubleClick={handleReset}
      >
        <div
          className="elevation-svg-stage"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.15s ease-out',
            cursor: isDragging ? 'grabbing' : 'grab'
          }}
          dangerouslySetInnerHTML={{ __html: activeSvg }}
        />

        {/* Drag Pan Hint Overlay */}
        <div className="elevation-viewport-watermark">
          <Move size={12} />
          <span>Drag to Pan • Wheel to Zoom • Double-click to Reset</span>
        </div>
      </div>

      {/* ── ARCHITECTURAL NOTE & LEGEND BANNER ──────────────────────────── */}
      <div className="elevation-info-footer">
        <div className="elevation-footer-meta">
          <div className="elevation-meta-chip">
            <span className="meta-chip-label">FRONTAGE</span>
            <span className="meta-chip-val">{plotW}′-0″</span>
          </div>
          <div className="elevation-meta-chip">
            <span className="meta-chip-label">ORIENTATION</span>
            <span className="meta-chip-val">{facing} Facing</span>
          </div>
          <div className="elevation-meta-chip">
            <span className="meta-chip-label">LEVELS</span>
            <span className="meta-chip-val">G + {floors > 1 ? floors - 1 : 0}</span>
          </div>
          <div className="elevation-meta-chip">
            <span className="meta-chip-label">SCALE</span>
            <span className="meta-chip-val">1:100</span>
          </div>
        </div>

        <div className="elevation-footer-disclaimer">
          <Info size={14} color="#38bdf8" style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>
            <strong>Personalized 2D Architectural Elevation:</strong> Facade working drawing grounded in your plot&apos;s dimensions ({plotW}&apos; &times; {plotL}&apos; &bull; {facing} Facing &bull; G+{floors - 1}). Distinct from interior floor plans, this technical elevation illustrates exterior massing, fenestrations, and applied finishes.
          </span>
        </div>
      </div>
    </div>
  );
}
