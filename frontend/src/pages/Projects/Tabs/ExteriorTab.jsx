import React, { useState } from 'react';
import { Sun, Wand2, Image as ImageIcon } from 'lucide-react';

const ExteriorTab = ({ project }) => {
    const [selectedStyle, setSelectedStyle] = useState(project.design_style || 'Modern');

    const styles = ['Modern', 'Contemporary', 'Minimalist', 'Traditional', 'Luxury', 'Mediterranean'];

    // In production, this maps to exterior designs array fetched from Supabase
    const generatedDesigns = []; 

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%', overflowY: 'auto', paddingBottom: 'var(--space-8)' }}>
            
            {/* Generation Controls */}
            <div className="card card-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)', alignItems: 'flex-start' }}>
                <div style={{ flex: '1 1 200px' }}>
                    <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: '8px' }}>Project Context</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 500 }}>
                        {project.facing || 'Unknown'} Facing • G + {(project.floors || 1) - 1} • {project.plot_width || '?'}ft Frontage
                    </div>
                </div>
                
                <div style={{ flex: '1 1 200px' }}>
                    <label className="form-label">Architectural Style</label>
                    <select className="form-control" value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                        {styles.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>

                <div style={{ flex: '2 1 300px' }}>
                    <label className="form-label">Additional Prompt (Optional)</label>
                    <input type="text" className="form-control" placeholder="e.g., 'brick facade, large glass windows'" />
                </div>

                <div style={{ flex: '1 1 100%', display: 'flex', justifyContent: 'flex-end' }}>
                    <button className="btn btn-primary" disabled title="AI implementation pending in Phase 5" style={{ padding: '0 24px' }}>
                        <Wand2 size={16} style={{ marginRight: '8px' }} />
                        Generate Elevation
                    </button>
                </div>
            </div>

            {/* Gallery */}
            <div style={{ flex: 1 }}>
                <h3 className="text-h4 mb-4">Exterior Elevations</h3>
                
                {generatedDesigns.length === 0 ? (
                    <div className="card card-body" style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)' }}>
                        <Sun size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
                        <h4 className="text-h4" style={{ marginBottom: '8px' }}>No exterior elevations yet</h4>
                        <p style={{ fontSize: '0.9rem', maxWidth: '300px', textAlign: 'center' }}>
                            Generate photorealistic front-elevation concepts based on your project configuration.
                        </p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
                        {/* Will map generated designs here */}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ExteriorTab;
