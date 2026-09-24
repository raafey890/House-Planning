import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import "../styles/layouts/app-layout.css";

const AppLayout = () => {
    const [isMobileOpen, setMobileOpen] = useState(false);

    return (
        <div className="app-layout">
            <Sidebar isMobileOpen={isMobileOpen} setMobileOpen={setMobileOpen} />
            
            <div className="app-main">
                <Topbar setMobileOpen={setMobileOpen} />
                
                <main className="app-content">
                    <Outlet />
                </main>
            </div>
            
            <Toaster position="bottom-right" />
        </div>
    );
};

export default AppLayout;
