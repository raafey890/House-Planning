import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProjectStore } from '../../store';
import { Plus, Search, FolderKanban, MoreVertical, Map, Edit, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

const ProjectsPage = () => {
    const { projects, fetchProjects, loading, deleteProject, createProject } = useProjectStore();
    const navigate = useNavigate();

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    const handleCreateProject = async () => {
        const name = prompt("Enter new project name:");
        if (name) {
            const toastId = toast.loading("Creating workspace...");
            await createProject({ name, project_type: 'Residential' });
            toast.success("Workspace created", { id: toastId });
        }
    };

    const handleDelete = async (id, name) => {
        if (window.confirm(`Are you sure you want to delete ${name}? This cannot be undone.`)) { // Will replace with modal if time permits, prompt allows simple for now, but instructions say "do not use window.confirm". I will build a custom modal state.
            // Wait, instruction says: "Do NOT use browser window.confirm() if the design system already has a modal/dialog component."
            // There's no modal component built yet in F1/F2, but let's build a quick inline or custom state.
            // Actually, I can just use a state for `projectToDelete` and show a custom modal.
            toast.loading("Deleting project...");
            await deleteProject(id);
            toast.dismiss();
            toast.success("Project deleted");
        }
    };

    // To comply strictly with "no window.confirm", I'll create a simple state-based modal.
    const [projectToDelete, setProjectToDelete] = React.useState(null);

    const confirmDelete = async () => {
        if (!projectToDelete) return;
        const toastId = toast.loading("Deleting project...");
        await deleteProject(projectToDelete.id);
        toast.success("Project deleted", { id: toastId });
        setProjectToDelete(null);
    };

    return (
        <div style={{ maxWidth: 'var(--container-max-width)', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-8)' }}>
                <div>
                    <h1 className="text-h2" style={{ margin: 0 }}>All Projects</h1>
                    <p className="text-muted" style={{ margin: 0 }}>Manage your architectural workspaces and designs.</p>
                </div>
                <button className="btn btn-primary" onClick={handleCreateProject}>
                    <Plus size={18} style={{ marginRight: '6px' }} /> New Project
                </button>
            </div>

            {loading ? (
                <div style={{ padding: '4rem', textAlign: 'center' }}>Loading projects...</div>
            ) : projects.length === 0 ? (
                <div className="card card-body" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
                    <FolderKanban size={48} color="var(--color-border)" style={{ margin: '0 auto var(--space-4)' }} />
                    <h3 className="text-h3" style={{ marginBottom: 'var(--space-2)' }}>Start designing your first home</h3>
                    <p style={{ maxWidth: '400px', margin: '0 auto var(--space-6)' }}>Create a project workspace to begin generating floor plans, exploring interiors, and estimating construction costs.</p>
                    <button className="btn btn-primary" onClick={handleCreateProject}>Create First Project</button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
                    {projects.map((project) => (
                        <div key={project.id} className="card card-interactive" style={{ display: 'flex', flexDirection: 'column' }}>
                            <div style={{ height: '140px', background: 'var(--color-surface-alt)', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Map size={40} color="var(--color-border)" />
                                <span style={{ position: 'absolute', top: '12px', right: '12px', background: 'var(--color-surface-card)', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>Draft</span>
                            </div>
                            <div className="card-body" style={{ flex: 1, padding: 'var(--space-4)' }}>
                                <h3 className="text-h4" style={{ margin: '0 0 var(--space-2) 0' }}>{project.name}</h3>
                                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)' }}>
                                    {project.plot_length && project.plot_width 
                                        ? `${project.plot_length} × ${project.plot_width} ft • ${project.facing || 'Unknown'} Facing`
                                        : 'Plot dimensions not set'}
                                </div>
                                <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
                                    <button 
                                        className="btn btn-primary btn-sm" 
                                        style={{ flex: 1 }}
                                        onClick={() => navigate(`/projects/${project.id}`)}
                                    >
                                        Open Workspace
                                    </button>
                                    <button 
                                        className="btn btn-outline btn-sm"
                                        onClick={() => setProjectToDelete(project)}
                                        style={{ padding: 'var(--space-2)', borderColor: 'var(--color-error)', color: 'var(--color-error)' }}
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Custom Delete Modal */}
            {projectToDelete && (
                <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-4)' }}>
                    <div className="card card-body" style={{ width: '100%', maxWidth: '400px', backgroundColor: 'var(--color-surface-card)' }}>
                        <h3 className="text-h3" style={{ marginTop: 0, color: 'var(--color-error)' }}>Delete Project</h3>
                        <p>Are you sure you want to delete <strong>{projectToDelete.name}</strong>? This action will permanently erase all associated requirements, floor plans, and designs. This cannot be undone.</p>
                        <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-6)' }}>
                            <button className="btn btn-ghost" style={{ flex: 1 }} onClick={() => setProjectToDelete(null)}>Cancel</button>
                            <button className="btn btn-primary" style={{ flex: 1, backgroundColor: 'var(--color-error)' }} onClick={confirmDelete}>Yes, Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProjectsPage;
