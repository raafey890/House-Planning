import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion';

/* ─────────────────────────────────────────────────────────────
   CAPABILITY VISUAL COMPONENTS
───────────────────────────────────────────────────────────── */

// 01. Intelligent Planning
const IntelligentPlanningVisual = ({ x, y }) => (
    <motion.div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '12px', overflow: 'hidden' }}>
        <motion.div style={{ position: 'absolute', inset: 0, x: useTransform(x, v => v * 0.5), y: useTransform(y, v => v * 0.5) }}>
            <svg viewBox="0 0 400 300" style={{ width: '100%', height: '100%' }}>
                {/* Background Grid */}
                <pattern id="planGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
                </pattern>
                <rect width="100%" height="100%" fill="url(#planGrid)" />
                {/* Floor Plan */}
                <g stroke="var(--color-text-muted)" strokeWidth="1.5" fill="none">
                    <rect x="50" y="50" width="300" height="200" fill="rgba(75,122,100,0.05)" />
                    <line x1="200" y1="50" x2="200" y2="250" />
                    <line x1="50" y1="150" x2="200" y2="150" />
                    <line x1="200" y1="180" x2="350" y2="180" />
                </g>
                <g fill="var(--color-text-main)" fontSize="10" fontWeight="600" letterSpacing="1" textAnchor="middle">
                    <text x="125" y="95">MASTER BED</text>
                    <text x="125" y="110" fill="var(--color-accent)" fontSize="8">12' × 14'</text>
                    
                    <text x="125" y="195">BATH</text>
                    <text x="125" y="210" fill="var(--color-accent)" fontSize="8">6' × 8'</text>
                    
                    <text x="275" y="110">LIVING</text>
                    <text x="275" y="125" fill="var(--color-accent)" fontSize="8">14' × 16'</text>

                    <text x="275" y="210">KITCHEN</text>
                    <text x="275" y="225" fill="var(--color-accent)" fontSize="8">10' × 11'</text>
                </g>
                <g stroke="var(--color-accent)" strokeWidth="1">
                    <line x1="50" y1="30" x2="350" y2="30" />
                    <text x="200" y="22" fill="var(--color-accent)" fontSize="9" textAnchor="middle" stroke="none">30 FT</text>
                    <line x1="370" y1="50" x2="370" y2="250" />
                    <text x="375" y="150" fill="var(--color-accent)" fontSize="9" textAnchor="middle" stroke="none" transform="rotate(90 375 150)">40 FT</text>
                </g>
            </svg>
        </motion.div>
        <FloatingMetadata x={x} y={y} title="PLOT SPECS" lines={["30 × 40 FT", "EAST FACING", "3 BEDROOMS"]} />
    </motion.div>
);

// 02. Interior Design
const InteriorVisual = ({ x, y }) => (
    <motion.div style={{ width: '100%', height: '100%', position: 'relative', borderRadius: '12px', overflow: 'hidden' }}>
        <motion.img 
            src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=1000" 
            style={{ width: '110%', height: '110%', objectFit: 'cover', position: 'absolute', top: '-5%', left: '-5%', x: useTransform(x, v => v * 0.4), y: useTransform(y, v => v * 0.4) }} 
        />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(7,8,7,0.7) 0%, transparent 40%)' }} />
        <FloatingMetadata x={x} y={y} title="AI INTERIOR" lines={["MODERN LIVING ROOM"]} right />
    </motion.div>
);

// 03. Exterior Design
const ExteriorVisual = ({ x, y }) => (
    <motion.div style={{ width: '100%', height: '100%', position: 'relative', borderRadius: '12px', overflow: 'hidden' }}>
        <motion.img 
            src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1000" 
            style={{ width: '110%', height: '110%', objectFit: 'cover', position: 'absolute', top: '-5%', left: '-5%', x: useTransform(x, v => v * 0.4), y: useTransform(y, v => v * 0.4) }} 
        />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(7,8,7,0.7) 0%, transparent 40%)' }} />
        <FloatingMetadata x={x} y={y} title="EXTERIOR DESIGN" lines={["MODERN ELEVATION"]} right />
    </motion.div>
);

// 04. Interactive 3D
const Interactive3DVisual = ({ x, y }) => (
    <motion.div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '12px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <motion.div style={{ position: 'absolute', inset: 0, x: useTransform(x, v => v * 0.6), y: useTransform(y, v => v * 0.6), display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg viewBox="0 0 300 300" style={{ width: '70%', height: '70%', overflow: 'visible' }}>
                <defs>
                    <pattern id="grid3d" width="30" height="30" patternUnits="userSpaceOnUse">
                        <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />
                    </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid3d)" />
                {/* 3D Wireframe Cube/House */}
                <g stroke="var(--color-accent)" strokeWidth="1.5" fill="none">
                    <polygon points="100,200 200,200 250,150 150,150" fill="rgba(75,122,100,0.1)" />
                    <polygon points="100,100 200,100 250,50 150,50" />
                    <polygon points="100,100 100,200 150,150 150,50" fill="rgba(75,122,100,0.2)" />
                    <polygon points="200,100 200,200 250,150 250,50" fill="rgba(75,122,100,0.05)" />
                    <line x1="100" y1="100" x2="200" y2="100" />
                    <line x1="200" y1="100" x2="200" y2="200" />
                    <line x1="100" y1="200" x2="200" y2="200" />
                    <line x1="100" y1="100" x2="100" y2="200" />
                </g>
                <circle cx="150" cy="125" r="110" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" strokeDasharray="5 5" />
                <circle cx="150" cy="125" r="3" fill="var(--color-text-main)" />
            </svg>
        </motion.div>
        <FloatingMetadata x={x} y={y} title="INTERACTIVE 3D" lines={["COMING SOON"]} />
    </motion.div>
);

// 05. Cost Intelligence
const CostVisual = ({ x, y }) => {
    const bars = [
        { label: 'MATERIALS', w: '85%' },
        { label: 'LABOR', w: '65%' },
        { label: 'ELECTRICAL', w: '40%' },
        { label: 'PLUMBING', w: '35%' },
        { label: 'INTERIORS', w: '50%' }
    ];
    return (
        <motion.div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '12px', padding: '40px', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <motion.div style={{ x: useTransform(x, v => v * 0.4), y: useTransform(y, v => v * 0.4), width: '100%' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', letterSpacing: '2px', marginBottom: '24px' }}>CONSTRUCTION ESTIMATE</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', width: '100%' }}>
                    {bars.map((b, i) => (
                        <div key={i}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--color-text-main)', marginBottom: '6px' }}>
                                <span>{b.label}</span>
                            </div>
                            <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                                <motion.div initial={{ width: 0 }} animate={{ width: b.w }} transition={{ duration: 1, delay: i * 0.1 }} style={{ height: '100%', backgroundColor: 'var(--color-accent)' }} />
                            </div>
                        </div>
                    ))}
                </div>
            </motion.div>
            <FloatingMetadata x={x} y={y} title="COST INTELLIGENCE" lines={["ILLUSTRATIVE BREAKDOWN"]} right />
        </motion.div>
    );
};

// 06. Project Workspace
const WorkspaceVisual = ({ x, y }) => (
    <motion.div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: '12px', padding: '40px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <motion.div style={{ x: useTransform(x, v => v * 0.5), y: useTransform(y, v => v * 0.5), width: '80%', backgroundColor: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '24px', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}>
            <div style={{ fontSize: '1.2rem', color: 'var(--color-primary)', fontWeight: 600, marginBottom: '8px' }}>DREAM HOME</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '24px' }}>30 × 40 FT • East Facing</div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {['Floor Plan', 'Interior', 'Exterior', 'Estimate'].map((item, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: i < 3 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}>
                        <span style={{ fontSize: '0.9rem', color: 'var(--color-text-main)' }}>{item}</span>
                        <div style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: 'rgba(75,122,100,0.2)', border: '1px solid var(--color-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-accent)' }} />
                        </div>
                    </div>
                ))}
            </div>
        </motion.div>
        <FloatingMetadata x={x} y={y} title="WORKSPACE" lines={["CENTRALIZED MANAGEMENT"]} right />
    </motion.div>
);

// Floating Metadata Chip (Parallax)
const FloatingMetadata = ({ x, y, title, lines, right = false }) => {
    return (
        <motion.div
            style={{
                position: 'absolute',
                bottom: '8%',
                [right ? 'right' : 'left']: '8%',
                backgroundColor: 'rgba(13,15,14,0.9)',
                backdropFilter: 'blur(12px)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '6px',
                padding: '12px 16px',
                x: useTransform(x, v => v * 1.5),
                y: useTransform(y, v => v * 1.5),
                boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                zIndex: 10
            }}
        >
            <div style={{ color: 'var(--color-accent)', fontSize: '0.65rem', fontWeight: 700, letterSpacing: '2px', marginBottom: '4px' }}>{title}</div>
            {lines.map((line, i) => (
                <div key={i} style={{ color: i === 0 ? 'var(--color-primary)' : 'var(--color-text-muted)', fontSize: i === 0 ? '0.85rem' : '0.75rem', fontWeight: i === 0 ? 500 : 400, marginTop: '2px' }}>{line}</div>
            ))}
        </motion.div>
    );
};


/* ─────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────── */

const capabilities = [
    { num: "01", title: "Intelligent Planning", desc: "Algorithmic generation of structured floor plans optimized for flow, light, and architectural viability.", Visual: IntelligentPlanningVisual },
    { num: "02", title: "Interior Design", desc: "Photorealistic interior concepts generated across dozens of distinct architectural styles and moods.", Visual: InteriorVisual },
    { num: "03", title: "Exterior Design", desc: "Breathtaking elevation models transitioning layout mathematics into physical street presence.", Visual: ExteriorVisual },
    { num: "04", title: "Interactive 3D", desc: "Step inside your generated structure with dynamic 3D rendering and multi-floor navigation.", Visual: Interactive3DVisual },
    { num: "05", title: "Cost Intelligence", desc: "Predictive construction economics breaking down material, labor, and finishing costs.", Visual: CostVisual },
    { num: "06", title: "Project Workspace", desc: "A centralized command center preserving all your plots, versions, and architectural artifacts.", Visual: WorkspaceVisual }
];

const FeaturesSection = () => {
    const [activeIndex, setActiveIndex] = useState(0);
    const containerRef = useRef(null);
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 992;

    // Mouse Tracking for Parallax
    const rawX = useMotionValue(0);
    const rawY = useMotionValue(0);
    const springConfig = { damping: 30, stiffness: 100, mass: 1 };
    const mouseX = useSpring(rawX, springConfig);
    const mouseY = useSpring(rawY, springConfig);

    const handlePointerMove = (e) => {
        if (isMobile || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
        const y = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
        rawX.set(x * 10); // ±10px base movement
        rawY.set(y * 8);  // ±8px base movement
    };

    const handlePointerLeave = () => {
        rawX.set(0);
        rawY.set(0);
    };

    // Parallax values for the main floating container
    const rotateX = useTransform(mouseY, v => -v * 0.2); // ±1.6deg
    const rotateY = useTransform(mouseX, v => v * 0.2);  // ±2deg

    return (
        <section 
            id="capabilities"
            ref={containerRef}
            onPointerMove={handlePointerMove}
            onPointerLeave={handlePointerLeave}
            style={{ 
                backgroundColor: 'var(--color-background)', 
                padding: '100px 0', 
                position: 'relative',
                overflow: 'hidden',
                perspective: '1200px'
            }}
        >
            <div className="container" style={{ position: 'relative', zIndex: 2 }}>
                
                <motion.div 
                    initial={{ opacity: 0, y: 20 }} 
                    whileInView={{ opacity: 1, y: 0 }} 
                    viewport={{ once: true, margin: '-10%' }} 
                    style={{ 
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textAlign: 'center', 
                        width: '100%',
                        maxWidth: '1000px', 
                        margin: '0 auto 80px auto' 
                    }}
                >
                    <div style={{ color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '3px', fontSize: '0.8rem', marginBottom: '16px' }}>PLATFORM CAPABILITIES</div>
                    <h2 className="text-display" style={{ fontSize: 'clamp(2.5rem, 4vw, 3.5rem)', margin: 0, color: 'var(--color-primary)', lineHeight: 1.1 }}>End-to-end architecture.</h2>
                </motion.div>

                <div className="capabilities-layout" style={{ position: 'relative', display: 'flex', alignItems: 'flex-start' }}>
                    
                    {/* LEFT: Capabilities List */}
                    <div style={{ flex: '1 1 50%', display: 'flex', flexDirection: 'column', gap: '8px', zIndex: 2, position: 'relative' }}>
                        {capabilities.map((cap, idx) => {
                            const isActive = activeIndex === idx;
                            return (
                                <div 
                                    key={idx}
                                    className="capability-item"
                                    onMouseEnter={() => !isMobile && setActiveIndex(idx)}
                                    onClick={() => setActiveIndex(idx)}
                                    tabIndex={0}
                                    onKeyDown={(e) => { if(e.key === 'Enter') setActiveIndex(idx) }}
                                    style={{ 
                                        padding: '24px 0', 
                                        cursor: 'pointer',
                                        borderBottom: '1px solid rgba(255,255,255,0.05)',
                                        opacity: isActive ? 1 : 0.4,
                                        transition: 'all 0.4s ease',
                                        outline: 'none'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'baseline', gap: '24px' }}>
                                        <span style={{ color: isActive ? 'var(--color-accent)' : 'inherit', fontSize: '1rem', fontWeight: 600, fontFamily: 'var(--font-family-display)', fontStyle: 'italic' }}>{cap.num}</span>
                                        <h3 style={{ fontSize: 'clamp(1.5rem, 2.5vw, 2.2rem)', margin: 0, color: 'var(--color-primary)', transition: 'color 0.4s' }}>{cap.title}</h3>
                                    </div>
                                    
                                    <AnimatePresence>
                                        {isActive && (
                                            <motion.div 
                                                initial={{ opacity: 0, height: 0 }} 
                                                animate={{ opacity: 1, height: 'auto' }} 
                                                exit={{ opacity: 0, height: 0 }}
                                                transition={{ duration: 0.3 }}
                                                style={{ overflow: 'hidden' }}
                                            >
                                                <div style={{ padding: '16px 0 0 42px' }}>
                                                    {/* Subtle expanding line */}
                                                    <motion.div initial={{ width: 0 }} animate={{ width: '40px' }} style={{ height: '2px', backgroundColor: 'var(--color-accent)', marginBottom: '16px' }} />
                                                    <p style={{ color: 'var(--color-text-muted)', fontSize: '1.05rem', lineHeight: 1.6, maxWidth: '400px', margin: 0 }}>
                                                        {cap.desc}
                                                    </p>
                                                    
                                                    {/* MOBILE ONLY: Render visual right underneath when active */}
                                                    <div className="mobile-visual-wrapper" style={{ marginTop: '32px', height: '300px', width: '100%', display: 'none' }}>
                                                        <cap.Visual x={mouseX} y={mouseY} />
                                                    </div>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            );
                        })}
                    </div>

                    {/* RIGHT: Floating Visual Preview (Desktop Only) */}
                    <div className="desktop-visual-wrapper" style={{ flex: '1 1 50%', height: '520px', position: 'sticky', top: '20vh', display: 'flex', justifyContent: 'flex-end', pointerEvents: 'none' }}>
                        <motion.div 
                            style={{ 
                                width: '100%', 
                                maxWidth: '600px',
                                height: '100%', 
                                position: 'relative',
                                x: mouseX,
                                y: mouseY,
                                rotateX,
                                rotateY,
                                transformStyle: 'preserve-3d'
                            }}
                        >
                            <AnimatePresence mode="wait">
                                {capabilities.map((cap, idx) => (
                                    activeIndex === idx && (
                                        <motion.div
                                            key={idx}
                                            initial={{ opacity: 0, scale: 0.96, filter: 'blur(6px)', y: 20, clipPath: 'inset(0 100% 0 0)' }}
                                            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)', y: 0, clipPath: 'inset(0 0% 0 0)' }}
                                            exit={{ opacity: 0, scale: 0.96, filter: 'blur(6px)', y: -15, transition: { duration: 0.3 } }}
                                            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                                            style={{ position: 'absolute', inset: 0, transformStyle: 'preserve-3d' }}
                                        >
                                            <cap.Visual x={mouseX} y={mouseY} />
                                        </motion.div>
                                    )
                                ))}
                            </AnimatePresence>
                        </motion.div>
                    </div>

                </div>
            </div>

            <style dangerouslySetInnerHTML={{__html: `
                @media (max-width: 991px) {
                    .desktop-visual-wrapper {
                        display: none !important;
                    }
                    .mobile-visual-wrapper {
                        display: block !important;
                    }
                    .capabilities-layout {
                        flex-direction: column;
                    }
                }
            `}} />
        </section>
    );
};

export default FeaturesSection;