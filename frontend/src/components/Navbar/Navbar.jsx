import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Box } from 'lucide-react';
import { motion, useScroll, useTransform } from 'framer-motion';
import UserMenu from "./UserMenu";

function Navbar() {
    const { scrollY } = useScroll();
    
    // Background becomes opaque dark on scroll
    const backgroundColor = useTransform(
        scrollY,
        [0, 100],
        ['rgba(7, 8, 7, 0)', 'rgba(7, 8, 7, 0.85)']
    );

    // Border appears on scroll
    const borderBottom = useTransform(
        scrollY,
        [0, 100],
        ['1px solid rgba(255, 255, 255, 0)', '1px solid rgba(255, 255, 255, 0.05)']
    );

    // Backdrop filter applies on scroll
    const backdropFilter = useTransform(
        scrollY,
        [0, 100],
        ['blur(0px)', 'blur(16px)']
    );

    return (
        <motion.header 
            style={{ 
                position: 'fixed', 
                top: 0, left: 0, right: 0, 
                height: 'var(--header-height)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0 var(--space-8)',
                zIndex: 100,
                backgroundColor,
                borderBottom,
                backdropFilter,
                WebkitBackdropFilter: backdropFilter
            }}
        >
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
                <Box size={24} color="var(--color-primary)" />
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--color-primary)', letterSpacing: '-0.02em' }}>AI House Planner</h2>
            </Link>

            <nav style={{ display: 'none', '@media (min-width: 768px)': { display: 'block' } }}>
                <ul style={{ display: 'flex', gap: 'var(--space-8)', listStyle: 'none', margin: 0, padding: 0 }}>
                    {['Home', 'How It Works', 'Features', 'Gallery', 'Pricing'].map((item) => (
                        <li key={item}>
                            <Link 
                                to={item === 'Home' ? '/' : `/${item.toLowerCase().replace(/\s+/g, '-')}`} 
                                style={{ 
                                    textDecoration: 'none', 
                                    color: 'var(--color-text-muted)', 
                                    fontSize: '0.9rem', 
                                    fontWeight: 500,
                                    transition: 'color var(--transition-fast)' 
                                }}
                                onMouseEnter={(e) => e.target.style.color = 'var(--color-primary)'}
                                onMouseLeave={(e) => e.target.style.color = 'var(--color-text-muted)'}
                            >
                                {item}
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                <UserMenu />
                <button className="mobile-menu-button" style={{ background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', display: 'block' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
            </div>
        </motion.header>
    );
}

export default Navbar;