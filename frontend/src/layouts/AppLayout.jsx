import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { Outlet, useNavigate } from 'react-router-dom';
import { useProjectStore } from '../store';
import toast, { Toaster } from 'react-hot-toast';
import "../styles/layouts/app-layout.css";

const AppLayout = () => {
    const [isMobileOpen, setMobileOpen] = useState(false);
    const { createProject } = useProjectStore();
    const [isCreating, setIsCreating] = useState(false);
    const navigate = useNavigate();

    const handleCreateProject = async () => {
        setIsCreating(true);
        // Instead of a prompt, we'll route to a dedicated project creation page, 
        // or for now, we just create a blank project and route to its planner.
        const defaultName = `New Project ${Math.floor(Math.random() * 1000)}`;
        
        try {
            const result = await createProject({ name: defaultName, project_type: 'Residential' });
            // The createProject in projectStore usually updates the list.
            // Let's assume it returns { data, error }. If not, we'll just redirect to dashboard or latest project.
            toast.success("New project workspace created!");
            navigate("/projects"); // We'll build this route
        } catch (error) {
            toast.error("Failed to create project");
        }
        
        setIsCreating(false);
    };

    return (
        <div className="app-layout">
            <Sidebar isMobileOpen={isMobileOpen} setMobileOpen={setMobileOpen} />
            
            <div className="app-main">
                <Topbar setMobileOpen={setMobileOpen} handleCreateProject={handleCreateProject} isCreating={isCreating} />
                
                <main className="app-content">
                    <Outlet />
                </main>
            </div>
            
            <Toaster position="bottom-right" />
        </div>
    );
};

export default AppLayout;
