import React, { useState } from 'react';
import FloorPlanViewer from '../components/FloorPlanViewer';
import { PenTool, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

const FloorPlansTab = ({ project, planner, navigate }) => {
    const [generating, setGenerating] = useState(false);
    
    // Check if requirements exist
    const hasRequirements = project.plot_length && project.plot_width;

    // Use development fixture ONLY to verify renderer if uncommented. 
    // In production, this reads from project.floor_plans array via Supabase.
    // We will leave it null to show the architectural empty state per F4 requirements: 
    // "If real AI API is not implemented yet, DO NOT generate fake data."
    const layoutData = null; 
    
    /* 
    // Example layout structure format for when AI is implemented:
    const layoutData = {
        version: "1.0",
        metadata: { bounding_box: { w: project.plot_width, l: project.plot_length } },
        floors: [{
            level: 0,
            rooms: [
                { id: 'r1', name: 'Master Bed', position: { x: 2, y: 2 }, dimensions: { width: 12, length: 14 } }
            ]
        }]
    };
    */

    if (!hasRequirements) {
        return (
            <div className="card card-body text-center" style={{ padding: '4rem 2rem', margin: 'auto', maxWidth: '500px' }}>
                <AlertCircle size={48} color="var(--color-error)" style={{ margin: '0 auto var(--space-4)' }} />
                <h3 className="text-h3">Requirements Missing</h3>
                <p className="text-muted" style={{ marginBottom: 'var(--space-6)' }}>
                    Complete your project requirements before generating a floor plan.
                </p>
                <button className="btn btn-primary" onClick={() => navigate(`/projects/${project.id}/planner`)}>
                    Complete Planner
                </button>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', gap: 'var(--space-6)', height: '100%', overflow: 'hidden' }}>
            
            {/* LEFT AREA: VIEWER */}
            <div style={{ flex: 1, minWidth: 0, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <FloorPlanViewer 
                    layoutData={layoutData} 
                    plotWidth={project.plot_width} 
                    plotLength={project.plot_length} 
                />
            </div>

            {/* RIGHT AREA: PANEL */}
            <div style={{ width: '350px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', overflowY: 'auto', paddingRight: '4px' }}>
                
                {/* Generation Panel */}
                <div className="card card-body">
                    <h3 className="text-h4 mb-4">Generation Settings</h3>
                    
                    <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)', padding: '12px', background: 'var(--color-surface-alt)', borderRadius: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}><span>Plot:</span> <strong>{project.plot_length}×{project.plot_width} ft</strong></div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}><span>Facing:</span> <strong>{project.facing}</strong></div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Floors:</span> <strong>G + {(project.floors || 1) - 1}</strong></div>
                    </div>

                    <div className="form-group">
                        <label className="form-label" style={{ fontSize: '0.85rem' }}>Optimization Priority (Optional)</label>
                        <select className="form-control" style={{ fontSize: '0.9rem', padding: '8px' }}>
                            <option>Balanced</option>
                            <option>Space Efficiency</option>
                            <option>Natural Light</option>
                            <option>Vastu / Feng Shui</option>
                        </select>
                    </div>

                    <button 
                        className="btn btn-primary" 
                        style={{ width: '100%', marginTop: 'var(--space-4)' }}
                        disabled={true} 
                        title="AI implementation pending in Phase 5"
                    >
                        <PenTool size={16} style={{ marginRight: '6px' }} />
                        Generate AI Floor Plan (Soon)
                    </button>
                    <p style={{ fontSize: '0.75rem', textAlign: 'center', color: 'var(--color-text-muted)', marginTop: '8px' }}>
                        AI generation will be enabled in the upcoming AI implementation phase.
                    </p>
                </div>

                {/* Plan Versions (Empty State) */}
                <div className="card card-body" style={{ flex: 1 }}>
                    <h3 className="text-h4 mb-4">Plan Versions</h3>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '200px', color: 'var(--color-text-muted)', textAlign: 'center' }}>
                        <Grid size={32} style={{ opacity: 0.5, marginBottom: '8px' }} />
                        <span style={{ fontSize: '0.85rem', maxWidth: '200px' }}>Generated layout options will appear here for comparison.</span>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default FloorPlansTab;
