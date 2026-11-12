import React from "react";
import { Link } from "react-router-dom";
import { Box, Globe } from "lucide-react";

function Footer() {
    return (
        <footer style={{ backgroundColor: 'var(--color-surface-alt)', borderTop: '1px solid var(--color-border)', padding: 'var(--space-16) 0 var(--space-8) 0' }}>
            <div className="container">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-12)', paddingBottom: 'var(--space-12)', borderBottom: '1px solid var(--color-border)' }}>
                    <div style={{ gridColumn: '1 / -1', '@media (min-width: 768px)': { gridColumn: 'span 2' } }}>
                        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none', marginBottom: 'var(--space-4)' }}>
                            <Box size={26} color="#C6A46A" />
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, margin: 0, color: 'var(--color-primary)', letterSpacing: '0.14em', lineHeight: 1.15 }}>
                                    ROY DESIGNS
                                </h2>
                                <span style={{ fontSize: '0.62rem', color: '#C6A46A', letterSpacing: '0.08em', textTransform: 'uppercase', fontWeight: 600 }}>
                                    AI House Planning &amp; Visualization System
                                </span>
                            </div>
                        </Link>
                        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.88rem', maxWidth: '340px', lineHeight: 1.6, marginTop: '8px' }}>
                            AI-Powered Architecture &amp; Design. Intelligent floor planning, luxury styling, 3D visualization, and automated estimation.
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
                    <p style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem', margin: 0 }}>
                        © {new Date().getFullYear()} ROY DESIGNS. All rights reserved.
                    </p>
                    <div style={{ display: 'flex', gap: '16px' }}>
                        <a href="#" style={{ color: 'var(--color-text-muted)' }}><Globe size={18}/></a>
                    </div>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
