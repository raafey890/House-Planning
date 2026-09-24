import React from "react";
import { Link } from "react-router-dom";
import { Box, Globe } from "lucide-react";

function Footer() {
    return (
        <footer style={{ backgroundColor: 'var(--color-surface-alt)', borderTop: '1px solid var(--color-border)', padding: 'var(--space-16) 0 var(--space-8) 0' }}>
            <div className="container">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-12)', paddingBottom: 'var(--space-12)', borderBottom: '1px solid var(--color-border)' }}>
                    <div style={{ gridColumn: '1 / -1', '@media (min-width: 768px)': { gridColumn: 'span 2' } }}>
                        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', marginBottom: 'var(--space-6)' }}>
                            <Box size={24} color="var(--color-primary)" />
                            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0, color: 'var(--color-primary)', letterSpacing: '-0.02em' }}>AI House Planner</h2>
                        </Link>
                        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', maxWidth: '300px', lineHeight: 1.6 }}>
                            Intelligent architecture and design automation for the modern era.
                        </p>
                    </div>

                    <div>
                        <h4 style={{ color: 'var(--color-primary)', fontSize: '0.9rem', fontWeight: 600, marginBottom: 'var(--space-6)', letterSpacing: '1px' }}>PLATFORM</h4>
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <li><Link to="/planner" style={{ color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}>Architectural Planner</Link></li>
                            <li><Link to="/gallery" style={{ color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}>Design Gallery</Link></li>
                            <li><Link to="/pricing" style={{ color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}>Pricing</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 style={{ color: 'var(--color-primary)', fontSize: '0.9rem', fontWeight: 600, marginBottom: 'var(--space-6)', letterSpacing: '1px' }}>LEGAL</h4>
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            <li><Link to="#" style={{ color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}>Privacy Policy</Link></li>
                            <li><Link to="#" style={{ color: 'var(--color-text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}>Terms of Service</Link></li>
                        </ul>
                    </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 'var(--space-8)' }}>
                    <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', margin: 0 }}>© {new Date().getFullYear()} AI House Planner. All rights reserved.</p>
                    <div style={{ display: 'flex', gap: '16px' }}>
                        <a href="#" style={{ color: 'var(--color-text-muted)' }}><Globe size={18}/></a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;