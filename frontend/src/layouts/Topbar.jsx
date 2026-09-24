import React from 'react';
import { Menu, Plus, Bell } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const Topbar = ({ setMobileOpen, handleCreateProject, isCreating }) => {
    const location = useLocation();
    
    // Simple breadcrumb logic
    let pageTitle = "Dashboard";
    if (location.pathname.includes('/projects')) pageTitle = "Project Workspace";
    if (location.pathname.includes('/profile')) pageTitle = "Account Settings";

    return (
        <header className="topbar">
            <div className="topbar-left">
                <button className="mobile-menu-toggle" onClick={() => setMobileOpen(true)}>
                    <Menu size={24} />
                </button>
                <h1 className="topbar-title">{pageTitle}</h1>
            </div>
            
            <div className="topbar-actions">
                <button className="btn btn-ghost btn-sm" style={{ padding: '8px' }} title="Notifications">
                    <Bell size={18} />
                </button>
                
                <button 
                    className="btn btn-primary btn-sm" 
                    onClick={handleCreateProject}
                    disabled={isCreating}
                >
                    {isCreating ? "Creating..." : <><Plus size={16} style={{marginRight: '4px'}}/> New Project</>}
                </button>
            </div>
        </header>
    );
};

export default Topbar;
