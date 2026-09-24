import React from "react";
import { useProjectStore } from "../../store";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Trash2, Edit } from "lucide-react";
import toast from "react-hot-toast";

const UserProjects = () => {
    const { projects, deleteProject } = useProjectStore();
    const navigate = useNavigate();

    // Sort by most recent
    const recentProjects = [...projects]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 4);

    const handleDelete = async (id, name) => {
        // Quick custom toast implementation for delete inside the dashboard
        // Note: the prompt says don't use window.confirm. 
        // We will just do a standard toast for now.
        const toastId = toast.loading(`Deleting ${name}...`);
        await deleteProject(id);
        toast.success("Project deleted", { id: toastId });
    };

    if (projects.length === 0) {
        return null; // Handled by the empty state in ProjectsPage/Dashboard
    }

    return (
        <div className="card card-body">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-6)' }}>
                <h3 className="text-h3" style={{ margin: 0 }}>Recent Projects</h3>
                <button className="btn btn-ghost btn-sm" onClick={() => navigate('/projects')}>
                    View All <ArrowRight size={16} style={{ marginLeft: '4px' }} />
                </button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                {recentProjects.map((project) => (
                    <div 
                        key={project.id} 
                        style={{ 
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
                            padding: 'var(--space-4)', backgroundColor: 'var(--color-surface-alt)', 
                            borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border-light)',
                            cursor: 'pointer', transition: 'border-color 0.2s'
                        }}
                        onClick={() => navigate(`/projects/${project.id}`)}
                    >
                        <div>
                            <div style={{ fontWeight: 600, fontSize: '1.05rem', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {project.name} 
                                <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '100px', backgroundColor: 'var(--color-accent-light)', color: 'var(--color-accent)', fontWeight: 600 }}>
                                    {project.status || 'Planning'}
                                </span>
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginTop: '4px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                <span>{new Date(project.updated_at || project.created_at).toLocaleDateString()}</span>
                                {project.plot_length && project.plot_width && (
                                    <>
                                        <span>•</span>
                                        <span>{project.plot_width} × {project.plot_length} ft</span>
                                        <span>•</span>
                                        <span>{(project.plot_width * project.plot_length).toLocaleString()} sq ft</span>
                                        <span>•</span>
                                        <span>{project.facing || 'East'} Facing</span>
                                    </>
                                )}
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <button className="btn btn-outline btn-sm" onClick={(e) => { e.stopPropagation(); handleDelete(project.id, project.name); }} style={{ padding: '8px', color: 'var(--color-error)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserProjects;