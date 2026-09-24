import React from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store';

const ProjectWorkspaceSection = () => {
    const { session } = useAuthStore();

    return (
        <section className="section-padding" style={{ backgroundColor: 'var(--color-surface-alt)' }}>
            <div className="container text-center">
                <span className="text-caption">Organization</span>
                <h2 className="text-h2 mt-2">Your architectural workspace</h2>
                <p style={{ margin: '0 auto var(--space-8)', maxWidth: '600px' }}>
                    Save multiple variations, iterate on designs, and keep all your floor plans, renders, and estimates neatly organized in one secure cloud dashboard.
                </p>

                <div style={{ display: 'flex', gap: 'var(--space-4)', justifyContent: 'center', flexWrap: 'wrap', marginBottom: 'var(--space-8)' }}>
                    {['Modern Villa (Draft)', 'Lake House (Generated)', 'Urban Apartment (Concept)'].map((proj, idx) => (
                        <div key={idx} className="card" style={{ width: '250px', textAlign: 'left' }}>
                            <div style={{ height: '120px', background: 'var(--color-border-light)', borderBottom: '1px solid var(--color-border)' }}></div>
                            <div className="card-body" style={{ padding: 'var(--space-4)' }}>
                                <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{proj}</div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '4px' }}>Updated 2 days ago</div>
                            </div>
                        </div>
                    ))}
                </div>

                <Link to={session ? "/dashboard" : "/login"} className="btn btn-primary">
                    {session ? "Open Dashboard" : "Create Your First Project"}
                </Link>
            </div>
        </section>
    );
};

export default ProjectWorkspaceSection;
