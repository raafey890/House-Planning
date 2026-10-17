import React, { useState, useMemo, useEffect, useRef } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, MousePointer2, Download, Image as ImageIcon, Move } from 'lucide-react';
import FloorPlanSVG from '../../../components/floorplan/FloorPlanSVG';
import '../../../styles/pages/floorplan-viewer.css';

/**
 * FloorPlanViewer — Phase 6G Enhanced
 *
 * Wraps FloorPlanSVG with:
 * - Toolbar (floor selector + zoom/pan controls + SVG/PNG exports)
 * - Interactive mouse-drag panning & wheel zoom
 * - SVG viewport with transform
 * - Info bar showing plot/metrics + hovered room
 * - Collapsible raw JSON section for dev inspection
 * - Loading overlay
 * - Empty state when no layout exists yet
 */
const FloorPlanViewer = ({ layoutData, plotWidth, plotLength, project, loading, loadingMessage }) => {
  const [zoom, setZoom] = useState(1.0);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedFloor, setSelectedFloor] = useState(0);
  const [hoveredRoom, setHoveredRoom] = useState(null);
  const viewportRef = useRef(null);

  const zoomIn    = () => setZoom(z => Math.min(+(z + 0.25).toFixed(2), 4.0));
  const zoomOut   = () => setZoom(z => Math.max(+(z - 0.25).toFixed(2), 0.25));
  const fitPlot   = () => { setZoom(1.0); setPan({ x: 0, y: 0 }); };
  const fitBuilding = () => { setZoom(1.5); setPan({ x: 0, y: 0 }); };
  const resetZoom = () => { setZoom(1.25); setPan({ x: 0, y: 0 }); setSelectedFloor(0); };

  // Mouse pan handlers
  const handlePointerDown = (e) => {
    // Only drag with primary mouse button
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    e.currentTarget.setPointerCapture?.(e.pointerId);
  };

  const handlePointerMove = (e) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handlePointerUp = (e) => {
    if (isDragging) {
      setIsDragging(false);
      e.currentTarget.releasePointerCapture?.(e.pointerId);
    }
  };

  // Wheel zoom
  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY < 0 ? 0.15 : -0.15;
    setZoom(z => Math.min(Math.max(+(z + delta).toFixed(2), 0.25), 4.0));
  };

  // Export as SVG
  const handleExportSVG = () => {
    const svgEl = viewportRef.current?.querySelector('svg');
    if (!svgEl) return;
    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);
    if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const projName = (project?.name || 'house_plan').toLowerCase().replace(/\s+/g, '_');
    a.download = `${projName}_floorplan_level_${selectedFloor}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Export as PNG
  const handleExportPNG = () => {
    const svgEl = viewportRef.current?.querySelector('svg');
    if (!svgEl) return;
    const serializer = new XMLSerializer();
    let source = serializer.serializeToString(svgEl);
    if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
      source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
    }
    const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' });
    const blobURL = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.onload = () => {
      const scale = 2.5;
      const width = (svgEl.viewBox?.baseVal?.width || svgEl.clientWidth || 1000) * scale;
      const height = (svgEl.viewBox?.baseVal?.height || svgEl.clientHeight || 800) * scale;
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      const pngURL = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = pngURL;
      const projName = (project?.name || 'house_plan').toLowerCase().replace(/\s+/g, '_');
      a.download = `${projName}_floorplan_level_${selectedFloor}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobURL);
    };
    img.src = blobURL;
  };

  useEffect(() => {
    if (layoutData && !loading) {
      setZoom(1.25);
      setPan({ x: 0, y: 0 });
    }
  }, [layoutData, loading]);

  // Derive hovered room label for info bar
  const hoveredRoomLabel = useMemo(() => {
    if (!hoveredRoom || !layoutData) return null;
    if (selectedFloor === 'site') {
      const siteArea = layoutData.plot?.site_areas?.find(a => a.id === hoveredRoom);
      return siteArea ? siteArea.label : null;
    }
    const floor = layoutData.floors?.find(f => f.level === selectedFloor)
      || layoutData.floors?.[selectedFloor]
      || layoutData.floors?.[0];
    const room = floor?.rooms?.find(r => r.id === hoveredRoom);
    if (room) return room.label;
    const outdoor = floor?.outdoor_areas?.find(a => a.id === hoveredRoom);
    if (outdoor) return outdoor.label;
    const siteArea = layoutData.plot?.site_areas?.find(a => a.id === hoveredRoom);
    return siteArea ? siteArea.label : null;
  }, [hoveredRoom, layoutData, selectedFloor]);

  // Metrics (may be empty object)
  const metrics = layoutData?.metrics || {};
  const plot    = layoutData?.plot;

  // ── Empty state ─────────────────────────────────────────────────────────────
  if (!loading && (!layoutData || !layoutData.floors || layoutData.floors.length === 0)) {
    const pw = plotWidth || project?.plot_width;
    const pl = plotLength || project?.plot_length;
    const floorText = project?.floors > 1 ? `G + ${project.floors - 1}` : 'Ground Floor';

    return (
      <div className="fp-empty-state">
        <MousePointer2 size={44} color="var(--color-text-muted)" style={{ opacity: 0.4 }} />
        <h3>READY TO GENERATE</h3>
        <p>
          Create your first AI-assisted floor plan from your saved project requirements.
          Click <strong>Generate AI Floor Plan</strong> to begin.
        </p>
        {pw && pl && (
          <div style={{
            display: 'flex', gap: '8px', alignItems: 'center',
            fontSize: '0.82rem', fontWeight: 500, color: 'var(--color-text-main)',
            background: 'var(--color-surface-card)', padding: '6px 16px',
            borderRadius: 'var(--radius-full)', border: '1px solid var(--color-border-light)',
            marginTop: '4px'
          }}>
            <span>{pw} × {pl} ft</span>
            <span style={{ opacity: 0.3 }}>•</span>
            <span>{project?.facing || 'Unknown'} Facing</span>
            <span style={{ opacity: 0.3 }}>•</span>
            <span>{floorText}</span>
          </div>
        )}
      </div>
    );
  }

  const floors = layoutData?.floors || [];
  const displayW = plot?.width  || plotWidth  || 30;
  const displayL = plot?.length || plotLength || 40;

  return (
    <div className="fp-viewer-container">

      {/* ── Loading overlay ──────────────────────────────────────────────────── */}
      {loading && (
        <div className="fp-loading-overlay">
          <div className="fp-loading-spinner" />
          <div className="fp-loading-text">
            {loadingMessage || 'Generating your AI floor plan...'}
          </div>
        </div>
      )}

      {/* ── Toolbar ─────────────────────────────────────────────────────────── */}
      <div className="fp-toolbar">
        {/* Floor tabs */}
        <div className="fp-floor-tabs">
          {floors.map((floor, idx) => (
            <button
              key={floor.level ?? idx}
              className={`fp-floor-tab ${selectedFloor === (floor.level ?? idx) ? 'active' : ''}`}
              onClick={() => setSelectedFloor(floor.level ?? idx)}
            >
              {floor.name || `Floor ${idx}`}
            </button>
          ))}
          {floors.length > 1 && (
            <button
              key="both-tab"
              className={`fp-floor-tab ${selectedFloor === 'both' ? 'active' : ''}`}
              onClick={() => setSelectedFloor('both')}
            >
              Side-by-Side Blueprint
            </button>
          )}
          <button
            key="site-tab"
            className={`fp-floor-tab ${selectedFloor === 'site' ? 'active' : ''}`}
            onClick={() => setSelectedFloor('site')}
          >
            Site Plan
          </button>
        </div>

        {/* Zoom & Pan controls */}
        <div className="fp-zoom-controls">
          <button className="fp-zoom-btn" onClick={zoomIn} title="Zoom In (+)"><ZoomIn size={13} /></button>
          <span className="fp-zoom-label">{Math.round(zoom * 100)}%</span>
          <button className="fp-zoom-btn" onClick={zoomOut} title="Zoom Out (-)"><ZoomOut size={13} /></button>
          <button className="fp-zoom-btn" onClick={fitPlot} title="Fit Plot"><Maximize2 size={13} /></button>
          <button className="fp-zoom-btn" onClick={fitBuilding} title="Fit Building"><Maximize2 size={13} /></button>
          <button className="fp-zoom-btn" onClick={resetZoom} title="Reset View"><RotateCcw size={13} /></button>
        </div>

        {/* CAD Export Actions */}
        <div className="fp-export-controls">
          <button
            className="fp-export-btn"
            onClick={handleExportSVG}
            title="Download Vector CAD SVG Blueprint"
          >
            <Download size={13} />
            <span>SVG</span>
          </button>
          <button
            className="fp-export-btn"
            onClick={handleExportPNG}
            title="Download High-Resolution PNG Blueprint"
          >
            <ImageIcon size={13} />
            <span>PNG</span>
          </button>
        </div>
      </div>

      {/* ── Interactive Pan & Zoom SVG Viewport ──────────────────────────────── */}
      <div
        ref={viewportRef}
        className={`fp-svg-viewport ${isDragging ? 'is-dragging' : ''}`}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onWheel={handleWheel}
        style={{ cursor: isDragging ? 'grabbing' : 'grab', userSelect: 'none', touchAction: 'none' }}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: 'center center',
            transition: isDragging ? 'none' : 'transform 0.12s ease-out',
            width: '100%',
            maxWidth: selectedFloor === 'both' ? '1400px' : '850px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            pointerEvents: isDragging ? 'none' : 'auto'
          }}
        >
          {layoutData && (
            <FloorPlanSVG
              layoutData={layoutData}
              selectedFloor={selectedFloor}
              hoveredRoomId={hoveredRoom}
              onRoomHover={setHoveredRoom}
            />
          )}
        </div>
      </div>

      {/* ── Info bar ────────────────────────────────────────────────────────── */}
      <div className="fp-info-bar">
        <span className="fp-info-badge">
          Plot: <strong>{displayW}′ × {displayL}′</strong>
        </span>

        {metrics.totals?.plot_coverage_pct !== undefined && (
          <>
            <span className="fp-info-sep" />
            <span className="fp-info-badge">
              Plot Cov: <strong>{metrics.totals.plot_coverage_pct}%</strong>
            </span>
          </>
        )}

        {metrics.totals?.buildable_coverage_pct !== undefined && (
          <>
            <span className="fp-info-sep" />
            <span className="fp-info-badge">
              Build Cov: <strong>{metrics.totals.buildable_coverage_pct}%</strong>
            </span>
          </>
        )}

        {metrics.totals?.internal_building_utilization_pct !== undefined && (
          <>
            <span className="fp-info-sep" />
            <span className="fp-info-badge">
              Internal Util: <strong>{metrics.totals.internal_building_utilization_pct}%</strong>
            </span>
          </>
        )}

        {hoveredRoomLabel && (
          <>
            <span className="fp-info-sep" />
            <span className="fp-hovered-room">{hoveredRoomLabel}</span>
          </>
        )}

        <div style={{ flex: 1 }} />
        <span style={{ fontSize: '0.7rem', opacity: 0.4 }}>1 unit = 1 ft</span>
      </div>

      {/* ── Collapsible raw data ─────────────────────────────────────────────── */}
      {layoutData && (
        <details className="fp-raw-data">
          <summary>View Layout Data (Developer)</summary>
          <div style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.25)', fontSize: '0.75rem', borderBottom: '1px solid var(--color-border)', lineHeight: '1.6' }}>
            <div><strong>Generation ID:</strong> {layoutData.metadata?.generation_id || project?.id || 'live'}</div>
            <div><strong>Created At:</strong> {layoutData.metadata?.created_at || new Date().toISOString()}</div>
            <div><strong>Engine:</strong> {layoutData.metadata?.generation_engine || 'deterministic'}</div>
            <div><strong>Variant / Seed:</strong> {layoutData.metadata?.variant || 'balanced'} (Seed: {layoutData.metadata?.seed ?? '42'})</div>
            <div><strong>Quality Score:</strong> {layoutData.metadata?.architectural_quality?.total_score ?? metrics?.architectural_quality?.total_score ?? '--'} / 100</div>
          </div>
          <pre>{JSON.stringify(layoutData, null, 2)}</pre>
        </details>
      )}
    </div>
  );
};

export default FloorPlanViewer;
