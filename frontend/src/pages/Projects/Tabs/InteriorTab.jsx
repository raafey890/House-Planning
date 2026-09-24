import React, { useState } from 'react';
import { Image as ImageIcon, Wand2, Trash2, Heart } from 'lucide-react';

const InteriorTab = ({ project, planner }) => {
    const [selectedRoom, setSelectedRoom] = useState('Living Room');
    const [selectedStyle, setSelectedStyle] = useState(project.design_style || 'Modern');

    const availableRooms = [
        'Living Room', 
        ...(planner.bedrooms > 0 ? ['Master Bedroom', 'Bedroom'] : []),
        ...(planner.kitchens > 0 ? ['Kitchen'] : []),
        ...(planner.diningRooms > 0 ? ['Dining Room'] : []),
        ...(planner.bathrooms > 0 ? ['Bathroom'] : []),
        ...(planner.studyRoom ? ['Study Room'] : [])
    ];

    const styles = ['Modern', 'Minimalist', 'Contemporary', 'Luxury', 'Traditional', 'Industrial'];

    // In production, this maps to designs array fetched from Supabase
    const generatedDesigns = []; 

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%', overflowY: 'auto', paddingBottom: 'var(--space-8)' }}>
            
            {/* Generation Controls */}
            <div className="card card-body" style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-6)', alignItems: 'flex-end' }}>
                <div style={{ flex: '1 1 200px' }}>
                    <label className="form-label">Select Room</label>
                    <select className="form-control" value={selectedRoom} onChange={(e) => setSelectedRoom(e.target.value)}>
                        {availableRooms.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                </div>
                
                <div style={{ flex: '1 1 200px' }}>
                    <label className="form-label">Interior Style</label>
                    <select className="form-control" value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                        {styles.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>

                <div style={{ flex: '2 1 300px' }}>
                    <label className="form-label">Additional Prompt (Optional)</label>
                    <input type="text" className="form-control" placeholder="e.g., 'warm lighting, oak wood flooring'" />
                </div>

                <div style={{ flex: '0 0 auto' }}>
                    <button className="btn btn-primary" disabled title="AI implementation pending in Phase 5" style={{ padding: '0 24px' }}>
                        <Wand2 size={16} style={{ marginRight: '8px' }} />
                        Generate Interior
                    </button>
                </div>
            </div>

            {/* Gallery */}
            <div style={{ flex: 1 }}>
                <h3 className="text-h4 mb-4">Interior Concepts</h3>
                
                {generatedDesigns.length === 0 ? (
                    <div className="card card-body" style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)' }}>
                        <ImageIcon size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
                        <h4 className="text-h4" style={{ marginBottom: '8px' }}>No interior designs yet</h4>
                        <p style={{ fontSize: '0.9rem', maxWidth: '300px', textAlign: 'center' }}>
                            Select a room and style above to generate photorealistic interior concepts.
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

export default InteriorTab;
