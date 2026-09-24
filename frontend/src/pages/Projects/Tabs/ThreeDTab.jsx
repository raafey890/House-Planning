import React from 'react';
import { Box as BoxIcon, Play } from 'lucide-react';

const ThreeDTab = ({ project }) => {
    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            
            {/* Viewer Toolbar Placeholder */}
            <div className="card" style={{ padding: 'var(--space-3) var(--space-6)', marginBottom: 'var(--space-4)', display: 'flex', gap: 'var(--space-4)', backgroundColor: 'var(--color-surface-card)' }}>
                <select className="form-control" style={{ width: 'auto', padding: '4px 8px', fontSize: '0.85rem' }} disabled>
                    <option>Ground Floor</option>
                    <option>First Floor</option>
                </select>
                <select className="form-control" style={{ width: 'auto', padding: '4px 8px', fontSize: '0.85rem' }} disabled>
                    <option>Perspective</option>
                    <option>Top Down</option>
                </select>
            </div>

            {/* Viewer Shell */}
            <div style={{ flex: 1, backgroundColor: '#e5ecef', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', zIndex: 10 }}>
                    <div style={{ padding: '24px', backgroundColor: 'var(--color-surface-card)', borderRadius: '50%', marginBottom: 'var(--space-4)', boxShadow: 'var(--shadow-md)' }}>
                        <BoxIcon size={48} color="var(--color-primary)" />
                    </div>
                    <h3 className="text-h3 mb-2">3D Model Not Generated</h3>
                    <p style={{ maxWidth: '400px', color: 'var(--color-text-muted)', marginBottom: 'var(--space-6)' }}>
                        3D visualization will be constructed automatically from your selected structured floor plan layout in the upcoming 3D implementation phase.
                    </p>
                    <button className="btn btn-outline" disabled title="Pending 3D pipeline">
                        <Play size={16} style={{ marginRight: '8px' }} />
                        Initialize 3D Renderer (Coming Soon)
                    </button>
                </div>

                {/* Decorative grid overlay for the empty state to look like a 3D grid space */}
                <div style={{
                    position: 'absolute', inset: 0, opacity: 0.1, pointerEvents: 'none',
                    backgroundImage: 'linear-gradient(var(--color-text-main) 1px, transparent 1px), linear-gradient(90deg, var(--color-text-main) 1px, transparent 1px)',
                    backgroundSize: '40px 40px',
                    transform: 'perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px)',
                    transformOrigin: 'top center'
                }}></div>
            </div>
        </div>
    );
};

export default ThreeDTab;
