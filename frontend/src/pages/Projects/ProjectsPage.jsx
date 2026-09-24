import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProjectStore } from '../../store';
import { Plus, FolderKanban, Map, Trash2, ArrowRight, Home, Calendar, IndianRupee, Layers } from 'lucide-react';
import toast from 'react-hot-toast';

const ProjectsPage = () => {
    const { projects, fetchProjects, loading, deleteProject, error } = useProjectStore();
    const navigate = useNavigate();
    const [projectToDelete, setProjectToDelete] = useState(null);

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    const handleCreateProject = () => {
        navigate('/planner');
    };

    const confirmDelete = async () => {
        if (!projectToDelete) return;
        const toastId = toast.loading("Deleting project...");
        const res = await deleteProject(projectToDelete.id);
        if (res.error) {
            toast.error(res.error.message || "Failed to delete project", { id: toastId });
        } else {
            toast.success("Project deleted", { id: toastId });
        }
        setProjectToDelete(null);
    };

    // Helper to format currency
    const formatCurrency = (amount) => {
        if (!amount) return 'Not set';
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    };

    return (
        <div style={{ maxWidth: 'var(--container-max-width)', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-8)' }}>
                <div>
                    <h1 className="text-h2" style={{ margin: 0 }}>My Projects</h1>
                    <p className="text-muted" style={{ margin: 0, marginTop: '4px' }}>Manage your architectural workspaces and designs.</p>
                </div>
                <button 
                    className="btn btn-primary" 
                    onClick={handleCreateProject}
                    style={{ 
                        padding: '0 24px', 
                        height: '48px', 
                        fontSize: '1rem', 
                        fontWeight: 600,
                        borderRadius: 'var(--radius-lg)'
                    }}
                >
                    <Plus size={20} style={{ marginRight: '8px' }} /> New Project
                </button>
            </div>

            {error && (
                <div style={{ padding: 'var(--space-4)', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-6)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                    <strong>Error fetching projects:</strong> {error}
                </div>
            )}

            {loading ? (
                <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                    <div className="animate-spin" style={{ display: 'inline-block', border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)', borderRadius: '50%', width: '24px', height: '24px', marginBottom: '16px' }}></div>
                    <p>Loading your workspaces...</p>
                </div>
            ) : projects.length === 0 ? (
                <div className="card card-body" style={{ textAlign: 'center', padding: 'var(--space-12) var(--space-6)', backgroundColor: 'var(--color-surface-alt)' }}>
                    <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--color-surface-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto var(--space-6)', border: '1px solid var(--color-border-light)' }}>
                        <FolderKanban size={40} color="var(--color-primary)" />
                    </div>
                    <h3 className="text-h2" style={{ marginBottom: 'var(--space-3)' }}>Start designing your first home</h3>
                    <p className="text-muted" style={{ maxWidth: '480px', margin: '0 auto var(--space-8)', fontSize: '1.05rem', lineHeight: 1.6 }}>
                        Create a project workspace to begin generating floor plans, exploring interiors, and estimating construction costs with AI.
                    </p>
                    <button 
                        className="btn btn-primary" 
                        onClick={handleCreateProject}
                        style={{ 
                            padding: '0 32px', 
                            height: '52px', 
                            fontSize: '1.05rem', 
                            fontWeight: 600,
                            borderRadius: 'var(--radius-lg)'
                        }}
                    >
                        Create First Project
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 'var(--space-6)' }}>
                    {projects.map((project) => {
                        const area = (project.plot_length && project.plot_width) ? project.plot_length * project.plot_width : null;
                        
                        return (
                            <div key={project.id} className="card card-interactive" style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
                                {/* Card Header Image / Graphic */}
                                <div style={{ height: '120px', background: 'linear-gradient(135deg, var(--color-surface-alt) 0%, var(--color-surface-card) 100%)', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid var(--color-border-light)' }}>
                                    <Home size={32} color="var(--color-text-muted)" style={{ opacity: 0.5 }} />
                                    <span style={{ 
                                        position: 'absolute', top: '16px', right: '16px', 
                                        background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
                                        padding: '4px 12px', borderRadius: '100px', 
                                        fontSize: '0.75rem', fontWeight: 600, color: '#fff' 
                                    }}>
                                        {project.status || 'Draft'}
                                    </span>
                                </div>
                                
                                {/* Card Body */}
                                <div className="card-body" style={{ flex: 1, padding: 'var(--space-5)', display: 'flex', flexDirection: 'column' }}>
                                    <h3 className="text-h3" style={{ margin: '0 0 var(--space-1) 0', fontSize: '1.25rem' }}>{project.name}</h3>
                                    <p style={{ margin: '0 0 var(--space-4) 0', fontSize: '0.85rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                        <Calendar size={14} /> Created {new Date(project.created_at).toLocaleDateString()}
                                    </p>
                                    
                                    {/* Data Grid */}
                                    <div style={{ 
                                        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)', 
                                        marginBottom: 'var(--space-6)', flex: 1,
                                        fontSize: '0.9rem', color: 'var(--color-text)'
                                    }}>
                                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                            <Map size={16} style={{ color: 'var(--color-primary)', marginTop: '2px' }} />
                                            <div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>Dimensions</div>
                                                <div style={{ fontWeight: 500 }}>{project.plot_width && project.plot_length ? `${project.plot_width} × ${project.plot_length} ft` : 'Not set'}</div>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                            <Layers size={16} style={{ color: 'var(--color-primary)', marginTop: '2px' }} />
                                            <div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>Area</div>
                                                <div style={{ fontWeight: 500 }}>{area ? `${area.toLocaleString()} sq ft` : 'Not set'}</div>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                            <Home size={16} style={{ color: 'var(--color-primary)', marginTop: '2px' }} />
                                            <div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>Floors / Facing</div>
                                                <div style={{ fontWeight: 500 }}>{project.floors || 1} Floor(s) • {project.facing || 'Unknown'}</div>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                            <IndianRupee size={16} style={{ color: 'var(--color-primary)', marginTop: '2px' }} />
                                            <div>
                                                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500 }}>Budget</div>
                                                <div style={{ fontWeight: 500 }}>{formatCurrency(project.budget)}</div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    {/* Actions */}
                                    <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                                        <button 
                                            className="btn btn-primary" 
                                            style={{ flex: 1, padding: '0', height: '40px', justifyContent: 'center' }}
                                            onClick={() => navigate(`/projects/${project.id}`)}
                                        >
                                            Open Workspace <ArrowRight size={16} style={{ marginLeft: '6px' }} />
                                        </button>
                                        <button 
                                            className="btn btn-outline"
                                            onClick={() => setProjectToDelete(project)}
                                            style={{ 
                                                width: '40px', height: '40px', padding: 0, 
                                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                borderColor: 'var(--color-border)', color: 'var(--color-error)',
                                                backgroundColor: 'rgba(239, 68, 68, 0.05)'
                                            }}
                                            aria-label="Delete project"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Custom Delete Modal */}
            {projectToDelete && (
                <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-4)' }}>
                    <div className="card card-body" style={{ width: '100%', maxWidth: '440px', backgroundColor: 'var(--color-surface-card)', padding: 'var(--space-6)' }}>
                        <h3 className="text-h2" style={{ marginTop: 0, color: 'var(--color-error)', display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ padding: '8px', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '50%', display: 'flex' }}>
                                <Trash2 size={24} color="var(--color-error)" />
                            </div>
                            Delete Project
                        </h3>
                        <p style={{ margin: 'var(--space-4) 0', fontSize: '1.05rem', lineHeight: 1.5, color: 'var(--color-text)' }}>
                            Are you sure you want to delete <strong>{projectToDelete.name}</strong>? 
                        </p>
                        <p style={{ margin: '0 0 var(--space-6) 0', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
                            This action will permanently erase all associated requirements, floor plans, and 3D designs. This cannot be undone.
                        </p>
                        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                            <button className="btn btn-outline" style={{ flex: 1, height: '48px', fontSize: '1rem' }} onClick={() => setProjectToDelete(null)}>Cancel</button>
                            <button className="btn btn-primary" style={{ flex: 1, height: '48px', fontSize: '1rem', backgroundColor: 'var(--color-error)', borderColor: 'var(--color-error)' }} onClick={confirmDelete}>Yes, Delete Project</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProjectsPage;
