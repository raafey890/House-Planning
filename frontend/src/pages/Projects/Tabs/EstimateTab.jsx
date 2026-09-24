import React from 'react';
import { Calculator, FileText, CheckCircle2 } from 'lucide-react';

const EstimateTab = ({ project }) => {
    
    // In production, this would be fetched from the estimations table for this project
    const estimate = null; 

    /*
    const estimate = {
        total_cost: 4500000,
        materials: 2500000,
        labor: 1200000,
        electrical: 300000,
        plumbing: 250000,
        other: 250000,
        created_at: new Date().toISOString()
    };
    */

    if (!estimate) {
        return (
            <div className="card card-body text-center" style={{ padding: '4rem 2rem', margin: 'auto', maxWidth: '600px' }}>
                <Calculator size={48} color="var(--color-border)" style={{ margin: '0 auto var(--space-4)' }} />
                <h3 className="text-h3">Cost Estimation Not Ready</h3>
                <p className="text-muted" style={{ marginBottom: 'var(--space-6)' }}>
                    Complete your floor plan layout to generate an intelligent material and labor breakdown. 
                    The estimation engine requires precise room dimensions to calculate costs.
                </p>
                <button className="btn btn-primary" disabled title="Requires completed floor plan">
                    Generate Estimate (Locked)
                </button>
            </div>
        );
    }

    // Example rendering when data exists
    const maxBar = Math.max(estimate.materials, estimate.labor, estimate.electrical, estimate.plumbing, estimate.other);
    
    const BreakdownBar = ({ label, value, color }) => (
        <div style={{ marginBottom: 'var(--space-4)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.9rem', fontWeight: 500 }}>
                <span>{label}</span>
                <span>₹ {value.toLocaleString()}</span>
            </div>
            <div style={{ height: '8px', width: '100%', backgroundColor: 'var(--color-surface-alt)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${(value / maxBar) * 100}%`, backgroundColor: color, borderRadius: '4px' }}></div>
            </div>
        </div>
    );

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
            
            <div className="card card-body">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-6)' }}>
                    <div>
                        <h3 className="text-h4 text-muted mb-2">Total Estimated Cost</h3>
                        <div className="text-display" style={{ fontSize: '2.5rem', color: 'var(--color-primary)' }}>
                            ₹ {estimate.total_cost.toLocaleString()}
                        </div>
                    </div>
                    <button className="btn btn-outline btn-sm">
                        <FileText size={16} style={{ marginRight: '6px' }} /> Export PDF
                    </button>
                </div>

                {project.budget && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', backgroundColor: estimate.total_cost <= project.budget ? 'var(--color-success-light)' : 'var(--color-error-light)', borderRadius: '8px', marginBottom: 'var(--space-6)' }}>
                        <CheckCircle2 size={20} color={estimate.total_cost <= project.budget ? 'var(--color-success)' : 'var(--color-error)'} />
                        <span style={{ fontSize: '0.9rem', fontWeight: 500, color: estimate.total_cost <= project.budget ? 'var(--color-success-dark)' : 'var(--color-error-dark)' }}>
                            {estimate.total_cost <= project.budget ? 'Within your target budget' : 'Over your target budget'} (₹ {project.budget.toLocaleString()})
                        </span>
                    </div>
                )}

                <h4 className="text-h4 mb-4">Cost Breakdown</h4>
                <BreakdownBar label="Materials" value={estimate.materials} color="#4a90e2" />
                <BreakdownBar label="Labor" value={estimate.labor} color="#f39c12" />
                <BreakdownBar label="Electrical" value={estimate.electrical} color="#e74c3c" />
                <BreakdownBar label="Plumbing" value={estimate.plumbing} color="#2ecc71" />
                <BreakdownBar label="Other" value={estimate.other} color="#9b59b6" />
            </div>

            <div className="card card-body">
                <h3 className="text-h4 mb-4">Estimation Context</h3>
                <div style={{ fontSize: '0.9rem', color: 'var(--color-text-main)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--color-border)' }}>
                        <span className="text-muted">Plot Area</span> <strong>{project.plot_length * project.plot_width} sq ft</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--color-border)' }}>
                        <span className="text-muted">Floors</span> <strong>G + {project.floors - 1}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--color-border)' }}>
                        <span className="text-muted">Quality/Style</span> <strong>{project.design_style || 'Standard'}</strong>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span className="text-muted">Generated</span> <strong>{new Date(estimate.created_at).toLocaleDateString()}</strong>
                    </div>
                </div>
            </div>

        </div>
    );
};

export default EstimateTab;
