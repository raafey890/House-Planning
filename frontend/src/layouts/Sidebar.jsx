import React, { useState } from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { Box, LayoutDashboard, FolderKanban, PenTool, Image as ImageIcon, Layers, Calculator, Settings, HelpCircle, LogOut } from 'lucide-react';
import { useAuthStore } from '../store';

const Sidebar = ({ isMobileOpen, setMobileOpen }) => {
    const { profile, signOut } = useAuthStore();
    const location = useLocation();
    
    const handleLogout = async () => {
        await signOut();
    };

    const mainNav = [
        { name: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard size={20} /> },
        { name: 'Projects', path: '/projects', icon: <FolderKanban size={20} /> },
    ];

    const upcomingNav = [
        { name: 'AI Studio', path: '/studio', icon: <PenTool size={20} />, badge: 'Soon' },
        { name: 'Floor Plans', path: '/plans', icon: <Layers size={20} />, badge: 'Soon' },
        { name: '3D Gallery', path: '/3d', icon: <ImageIcon size={20} />, badge: 'Soon' },
        { name: 'Estimator', path: '/estimator', icon: <Calculator size={20} />, badge: 'Soon' },
    ];

    const bottomNav = [
        { name: 'Settings', path: '/profile', icon: <Settings size={20} /> },
        { name: 'Support', path: '#', icon: <HelpCircle size={20} /> },
    ];

    return (
        <>
            {isMobileOpen && (
                <div className="mobile-overlay" onClick={() => setMobileOpen(false)}></div>
            )}
            
            <aside className={`sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
                <div className="sidebar-header">
                    <Link to="/dashboard" className="sidebar-brand">
                        <Box size={24} color="var(--color-primary)" />
                        <span className="sidebar-brand-text">AI House Planner</span>
                    </Link>
                </div>

                <div className="sidebar-nav">
                    <div style={{ padding: '0 var(--space-6)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '8px', marginTop: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Workspace
                    </div>
                    {mainNav.map((item) => (
                        <NavLink 
                            key={item.name} 
                            to={item.path} 
                            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                            onClick={() => setMobileOpen(false)}
                        >
                            {item.icon}
                            <span className="nav-label">{item.name}</span>
                        </NavLink>
                    ))}

                    <div style={{ padding: '0 var(--space-6)', fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '8px', marginTop: '24px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Features
                    </div>
                    {upcomingNav.map((item) => (
                        <div key={item.name} className="nav-item" style={{ opacity: 0.6, cursor: 'not-allowed' }}>
                            {item.icon}
                            <span className="nav-label">{item.name}</span>
                            {item.badge && <span className="nav-badge">{item.badge}</span>}
                        </div>
                    ))}
                </div>

                <div className="sidebar-footer">
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
                        {bottomNav.map((item) => (
                            <Link key={item.name} to={item.path} className="nav-item" style={{ padding: '8px' }}>
                                {item.icon}
                                <span className="nav-label">{item.name}</span>
                            </Link>
                        ))}
                        <button onClick={handleLogout} className="nav-item" style={{ padding: '8px', background: 'none', border: 'none', width: '100%', textAlign: 'left', cursor: 'pointer' }}>
                            <LogOut size={20} />
                            <span className="nav-label">Logout</span>
                        </button>
                    </div>

                    <Link to="/profile" className="user-profile-sm" style={{ textDecoration: 'none', color: 'inherit' }}>
                        {profile?.avatar_url ? (
                            <img src={profile.avatar_url} alt="User" style={{ width: '36px', height: '36px', borderRadius: '50%', objectFit: 'cover' }} />
                        ) : (
                            <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'var(--color-primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
                                {profile?.full_name?.charAt(0) || 'U'}
                            </div>
                        )}
                        <div className="user-details" style={{ flex: 1, overflow: 'hidden' }}>
                            <div style={{ fontWeight: 600, fontSize: '0.875rem', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                                {profile?.full_name || 'User'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Pro Plan</div>
                        </div>
                    </Link>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
