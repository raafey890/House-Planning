import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useProjectStore, usePlannerStore } from '../../store';
import { Map, Grid, Image as ImageIcon, Calculator, Settings, ArrowLeft, Box as BoxIcon, Sun } from 'lucide-react';
import toast from 'react-hot-toast';

import OverviewTab from './Tabs/OverviewTab';
import FloorPlansTab from './Tabs/FloorPlansTab';
import InteriorTab from './Tabs/InteriorTab';
import ExteriorTab from './Tabs/ExteriorTab';
import ThreeDTab from './Tabs/ThreeDTab';
import EstimateTab from './Tabs/EstimateTab';

const ProjectWorkspace = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { projects, fetchProjects } = useProjectStore();
    const planner = usePlannerStore(); // Used just for checking readiness
    const { loadProjectSettings } = planner;
    const [activeTab, setActiveTab] = useState('overview');

    const project = projects.find(p => p.id === id);

    useEffect(() => {
        if (projects.length === 0) {
            fetchProjects();
        }
    }, [projects.length, fetchProjects]);

    useEffect(() => {
        if (project) {
            loadProjectSettings(project);
        }
    }, [project, loadProjectSettings]);

    if (!project) return <div style={{ padding: '4rem', textAlign: 'center' }}>Loading workspace...</div>;

    const tabs = [
        { id: 'overview', name: 'Overview', icon: <Map size={18} /> },
        { id: 'planner', name: 'Planner', icon: <Settings size={18} /> },
        { id: 'floorplans', name: 'Floor Plans', icon: <Grid size={18} /> },
        { id: 'interior', name: 'Interior', icon: <ImageIcon size={18} /> },
        { id: 'exterior', name: 'Exterior', icon: <Sun size={18} /> },
        { id: '3d', name: '3D View', icon: <BoxIcon size={18} /> },
        { id: 'estimate', name: 'Estimate', icon: <Calculator size={18} /> }
    ];

    const handleTabClick = (tabId) => {
        if (tabId === 'planner') {
            navigate(`/projects/${id}/planner`);
        } else {
            setActiveTab(tabId);
        }
    };

    return (
        <div style={{ maxWidth: 'var(--container-max-width)', margin: '0 auto', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 140px)' }}>
            <Link to="/projects" className="btn btn-ghost btn-sm" style={{ marginBottom: 'var(--space-4)', display: 'inline-flex', padding: 0, width: 'fit-content' }}>
                <ArrowLeft size={16} style={{ marginRight: '4px' }} /> Back to Projects
            </Link>
            
            {/* Context Header */}
            <div className="card" style={{ flexShrink: 0, marginBottom: 'var(--space-6)' }}>
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <h1 className="text-h2" style={{ margin: 0 }}>{project.name}</h1>
                        <p className="text-muted" style={{ margin: 0, marginTop: '4px', display: 'flex', gap: '12px', alignItems: 'center', fontSize: '0.9rem' }}>
                            {project.plot_length && project.plot_width ? (
                                <>
                                    <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{project.plot_length} × {project.plot_width} ft</span>
                                    <span>•</span>
                                    <span>{project.facing || 'Not set'} Facing</span>
                                    <span>•</span>
                                    <span>G + {(project.floors || 1) - 1}</span>
                                    <span>•</span>
                                    <span>{project.design_style || 'Style not set'}</span>
                                </>
                            ) : (
                                <span style={{ color: 'var(--color-error)' }}>Requirements pending</span>
                            )}
                        </p>
                    </div>
                    <button className="btn btn-outline btn-sm" onClick={() => navigate(`/projects/${id}/planner`)}>
                        Edit Requirements
                    </button>
                </div>
                
                {/* Tabs */}
                <div style={{ display: 'flex', overflowX: 'auto', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-alt)' }}>
                    {tabs.map(tab => (
                        <button 
                            key={tab.id}
                            onClick={() => handleTabClick(tab.id)}
                            style={{
                                padding: 'var(--space-3) var(--space-6)',
                                border: 'none',
                                background: activeTab === tab.id ? 'var(--color-surface-card)' : 'transparent',
                                borderBottom: activeTab === tab.id ? '2px solid var(--color-primary)' : '2px solid transparent',
                                cursor: 'pointer',
                                display: 'flex', alignItems: 'center', gap: '8px',
                                fontWeight: activeTab === tab.id ? 600 : 500,
                                color: activeTab === tab.id ? 'var(--color-primary)' : 'var(--color-text-muted)',
                                transition: 'all 0.2s',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            {tab.icon} {tab.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* TAB CONTENTS */}
            <div className="workspace-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                {activeTab === 'overview' && <OverviewTab project={project} planner={planner} />}
                {activeTab === 'floorplans' && <FloorPlansTab project={project} planner={planner} navigate={navigate} />}
                {activeTab === 'interior' && <InteriorTab project={project} planner={planner} navigate={navigate} />}
                {activeTab === 'exterior' && <ExteriorTab project={project} planner={planner} navigate={navigate} />}
                {activeTab === '3d' && <ThreeDTab project={project} />}
                {activeTab === 'estimate' && <EstimateTab project={project} />}
            </div>
        </div>
    );
};

export default ProjectWorkspace;
