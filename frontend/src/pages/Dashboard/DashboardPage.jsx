import React, { useEffect } from "react";
import DashboardAnalytics from "./DashboardAnalytics";
import UserProjects from "./UserProjects";
import { useProjectStore, useAuthStore } from "../../store";
import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

const DashboardPage = () => {
    const { fetchProjects, loading } = useProjectStore();
    const { profile } = useAuthStore();
    const navigate = useNavigate();

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    const handleCreateProject = () => {
        navigate("/planner");
    };

    const firstName = profile?.full_name?.split(' ')[0] || "Architect";

    return (
        <div style={{ maxWidth: 'var(--container-max-width)', margin: '0 auto' }}>
            <div style={{ marginBottom: 'var(--space-8)' }}>
                <h1 className="text-display" style={{ fontSize: '2.5rem', margin: '0 0 var(--space-2) 0' }}>Welcome back, {firstName}.</h1>
                <p className="text-muted" style={{ fontSize: '1.1rem', margin: 0 }}>Continue designing your dream home.</p>
            </div>
            
            <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-8)' }}>
                <button className="btn btn-primary" onClick={handleCreateProject}>
                    <Plus size={18} style={{marginRight: '6px'}}/> Create New Project
                </button>
                <button className="btn btn-outline" onClick={() => navigate('/projects')}>
                    View All Projects
                </button>
            </div>

            {loading ? (
                <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading workspace...</div>
            ) : (
                <>
                    <DashboardAnalytics />
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-8)', marginTop: 'var(--space-8)' }}>
                        <UserProjects />
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardPage;