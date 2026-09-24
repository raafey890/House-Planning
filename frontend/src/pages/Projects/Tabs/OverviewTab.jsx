import React from 'react';
import { Grid, Clock, Sparkles } from 'lucide-react';

const OverviewTab = ({ project, planner }) => {
    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)', overflowY: 'auto', paddingBottom: 'var(--space-8)' }}>
            
            <div className="card card-body" style={{ gridColumn: '1 / -1', background: 'var(--color-surface-alt)', border: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                    <h3 className="text-h3" style={{ marginBottom: '8px' }}>Project Ready for Generation</h3>
                    <p className="text-muted" style={{ margin: 0 }}>Your structural inputs and design preferences have been saved. Ready to generate AI floor plans.</p>
                </div>
                <button className="btn btn-primary" onClick={() => alert('AI Generation phase coming next.')}>
                    <Sparkles size={18} style={{ marginRight: '8px' }} /> Generate Floor Plan
                </button>
            </div>

            <div className="card card-body">
                <h3 className="text-h4 mb-4">Project Details</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.95rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Status</span> <span style={{ fontWeight: 600, color: 'var(--color-accent)' }}>Planning</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Location</span> <span style={{ fontWeight: 600 }}>{project.location || 'Not set'}</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Plot Area</span> <span style={{ fontWeight: 600 }}>{project.plot_length ? (project.plot_length * project.plot_width).toLocaleString() : 0} sq ft</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Budget</span> <span style={{ fontWeight: 600 }}>{project.budget ? `₹${Number(project.budget).toLocaleString('en-IN')}` : 'Not set'}</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Created</span> <span style={{ fontWeight: 600 }}>{new Date(project.created_at).toLocaleDateString()}</span></div>
                </div>
            </div>
            
            <div className="card card-body">
                <h3 className="text-h4 mb-4">Module Status</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.95rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Floor Plan</span> <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>Ready to Generate</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Interior</span> <span style={{ fontWeight: 500 }}>Available after floor plan</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Exterior</span> <span style={{ fontWeight: 500 }}>Available after floor plan</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">3D View</span> <span style={{ fontWeight: 500 }}>Coming Soon</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><span className="text-muted">Cost Estimate</span> <span style={{ fontWeight: 500 }}>Not Generated</span></div>
                </div>
            </div>
        </div>
    );
};

export default OverviewTab;
