import React, { useState, useMemo } from 'react';
import { ZoomIn, ZoomOut, Maximize, MousePointer2 } from 'lucide-react';

/**
 * Renders structured JSON floor plan data into an interactive SVG.
 * Handles automatic coordinate scaling to fit the container.
 */
const FloorPlanViewer = ({ layoutData, plotWidth, plotLength }) => {
    const [zoom, setZoom] = useState(1);
    const [hoveredRoom, setHoveredRoom] = useState(null);

    // If no data, show architectural empty state
    if (!layoutData || !layoutData.floors || layoutData.floors.length === 0) {
        return (
            <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--color-surface-alt)', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--color-border)', flexDirection: 'column' }}>
                <MousePointer2 size={48} color="var(--color-border)" style={{ marginBottom: '16px' }} />
                <h3 className="text-h4" style={{ color: 'var(--color-text-muted)' }}>Viewer Canvas Ready</h3>
                <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', maxWidth: '300px', textAlign: 'center' }}>
                    Generated structured layout data will be rendered here as interactive scalable geometry.
                </p>
            </div>
        );
    }

    // --- Geometry & Scaling Logic ---
    // The AI outputs coordinates where 1 unit = 1 ft usually, relative to 0,0.
    // We want to fit this into the SVG viewBox.
    // Let's assume the outer bounding box is plotWidth x plotLength.
    const w = plotWidth || layoutData.metadata?.bounding_box?.w || 40;
    const l = plotLength || layoutData.metadata?.bounding_box?.l || 60;
    
    // Add some padding to the viewBox
    const padding = 2;
    const viewBox = `${-padding} ${-padding} ${w + padding * 2} ${l + padding * 2}`;

    const floor = layoutData.floors[0]; // Just showing first floor for now

    const handleZoomIn = () => setZoom(z => Math.min(z + 0.2, 3));
    const handleZoomOut = () => setZoom(z => Math.max(z - 0.2, 0.5));
    const handleReset = () => setZoom(1);

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: '#f0f3f5', borderRadius: 'var(--radius-lg)', overflow: 'hidden', border: '1px solid var(--color-border)' }}>
            
            {/* Toolbar */}
            <div style={{ position: 'absolute', top: '16px', right: '16px', display: 'flex', gap: '8px', zIndex: 10, background: 'var(--color-surface-card)', padding: '4px', borderRadius: '8px', boxShadow: 'var(--shadow-sm)' }}>
                <button className="btn btn-ghost btn-sm" style={{ padding: '6px' }} onClick={handleZoomIn} title="Zoom In"><ZoomIn size={18} /></button>
                <button className="btn btn-ghost btn-sm" style={{ padding: '6px' }} onClick={handleZoomOut} title="Zoom Out"><ZoomOut size={18} /></button>
                <button className="btn btn-ghost btn-sm" style={{ padding: '6px' }} onClick={handleReset} title="Fit to Screen"><Maximize size={18} /></button>
            </div>

            {/* Scale Indicator */}
            <div style={{ position: 'absolute', bottom: '16px', left: '16px', zIndex: 10, background: 'rgba(255,255,255,0.8)', padding: '4px 12px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-main)' }}>
                Plot: {w}' × {l}'
            </div>

            {/* SVG Renderer */}
            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'auto' }}>
                <div style={{ transform: `scale(${zoom})`, transformOrigin: 'center center', transition: 'transform 0.2s ease-out', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <svg 
                        viewBox={viewBox} 
                        style={{ maxWidth: '100%', maxHeight: '100%', width: '100%', dropShadow: '0 10px 20px rgba(0,0,0,0.1)' }}
                        vectorEffect="non-scaling-stroke"
                    >
                        {/* Plot Boundary */}
                        <rect x="0" y="0" width={w} height={l} fill="#e5ecef" stroke="#c2d1d9" strokeWidth="0.2" strokeDasharray="0.5 0.5" />
                        
                        {/* Rooms */}
                        {floor.rooms?.map((room, i) => {
                            const isHovered = hoveredRoom === room.id;
                            const rx = room.position?.x || 0;
                            const ry = room.position?.y || 0;
                            const rw = room.dimensions?.width || 10;
                            const rl = room.dimensions?.length || 10;
                            
                            return (
                                <g 
                                    key={room.id || i}
                                    onMouseEnter={() => setHoveredRoom(room.id)}
                                    onMouseLeave={() => setHoveredRoom(null)}
                                    style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                                >
                                    {/* Room Area */}
                                    <rect 
                                        x={rx} y={ry} width={rw} height={rl} 
                                        fill={isHovered ? "var(--color-primary-light)" : "white"} 
                                        stroke="var(--color-text-main)" 
                                        strokeWidth="0.4"
                                        style={{ transition: 'fill 0.2s' }}
                                    />
                                    
                                    {/* Room Label */}
                                    <text x={rx + rw/2} y={ry + rl/2} textAnchor="middle" dominantBaseline="middle" fontSize="1.2" fontWeight="600" fill="var(--color-text-main)" style={{ pointerEvents: 'none' }}>
                                        {room.name?.toUpperCase()}
                                    </text>
                                    
                                    {/* Room Dimensions */}
                                    <text x={rx + rw/2} y={ry + rl/2 + 1.5} textAnchor="middle" dominantBaseline="middle" fontSize="0.8" fill="var(--color-text-muted)" style={{ pointerEvents: 'none' }}>
                                        {rw}' × {rl}'
                                    </text>
                                    
                                    {/* Render Doors placeholder if any */}
                                    {room.doors?.map((door, di) => {
                                        // Simplified door render based on wall
                                        let dx = rx, dy = ry, dw = 0, dl = 0;
                                        if (door.wall === 'south') { dx = rx + door.offset; dy = ry + rl - 0.2; dw = door.width; dl = 0.4; }
                                        if (door.wall === 'north') { dx = rx + door.offset; dy = ry - 0.2; dw = door.width; dl = 0.4; }
                                        if (door.wall === 'east') { dx = rx + rw - 0.2; dy = ry + door.offset; dw = 0.4; dl = door.width; }
                                        if (door.wall === 'west') { dx = rx - 0.2; dy = ry + door.offset; dw = 0.4; dl = door.width; }
                                        
                                        return <rect key={`d${di}`} x={dx} y={dy} width={dw} height={dl} fill="white" stroke="var(--color-text-main)" strokeWidth="0.1" />
                                    })}

                                    {/* Render Windows placeholder if any */}
                                    {room.windows?.map((win, wi) => {
                                        let wx = rx, wy = ry, ww = 0, wl = 0;
                                        if (win.wall === 'south') { wx = rx + win.offset; wy = ry + rl - 0.15; ww = win.width; wl = 0.3; }
                                        if (win.wall === 'north') { wx = rx + win.offset; wy = ry - 0.15; ww = win.width; wl = 0.3; }
                                        if (win.wall === 'east') { wx = rx + rw - 0.15; wy = ry + win.offset; ww = 0.3; wl = win.width; }
                                        if (win.wall === 'west') { wx = rx - 0.15; wy = ry + win.offset; ww = 0.3; wl = win.width; }
                                        
                                        return <rect key={`w${wi}`} x={wx} y={wy} width={ww} height={wl} fill="#cce0ff" stroke="var(--color-primary)" strokeWidth="0.1" />
                                    })}
                                </g>
                            )
                        })}
                    </svg>
                </div>
            </div>
        </div>
    );
};

export default FloorPlanViewer;
