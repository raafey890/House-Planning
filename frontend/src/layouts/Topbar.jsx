import React from 'react';
import { Menu, Bell } from 'lucide-react';
import { useLocation } from 'react-router-dom';

const Topbar = ({ setMobileOpen }) => {
    const location = useLocation();
    
    // Simple breadcrumb logic
    let pageTitle = "Dashboard";
    if (location.pathname.includes('/projects')) pageTitle = "Project Workspace";
    if (location.pathname.includes('/planner')) pageTitle = "Project Planner";
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
            </div>
        </header>
    );
};

export default Topbar;
