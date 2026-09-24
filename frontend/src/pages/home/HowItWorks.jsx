import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

/* ─────────────────────────────────────────────────
   STEP 01 VISUAL — Plot Definition
───────────────────────────────────────────────── */
const PlotVisual = () => {
    const ref = useRef(null);
    const rawX = useMotionValue(0);
    const rawY = useMotionValue(0);
    const x = useSpring(rawX, { stiffness: 80, damping: 20 });
    const y = useSpring(rawY, { stiffness: 80, damping: 20 });
    const panX = useTransform(x, [-1, 1], [-5, 5]);
    const panY = useTransform(y, [-1, 1], [-5, 5]);

    const onMove = (e) => {
        const r = ref.current?.getBoundingClientRect();
        if (!r) return;
        rawX.set((e.clientX - r.left - r.width / 2) / (r.width / 2));
        rawY.set((e.clientY - r.top - r.height / 2) / (r.height / 2));
    };

    return (
        <motion.div
            ref={ref}
            onPointerMove={onMove}
            onPointerLeave={() => { rawX.set(0); rawY.set(0); }}
            style={{
                width: '100%', height: '100%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                position: 'relative',
                backgroundColor: 'var(--color-surface-alt)',
                border: '1px solid var(--color-border)',
                borderRadius: '12px',
                overflow: 'hidden'
            }}
        >
            <motion.div style={{ position: 'absolute', inset: 0, x: panX, y: panY, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg viewBox="0 0 300 300" style={{ width: '80%', height: '80%', overflow: 'visible' }}>
                    <defs>
                        <pattern id="plotGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
                        </pattern>
                    </defs>
                    <rect x="0" y="0" width="300" height="300" fill="url(#plotGrid)" />
                    
                    {/* Plot Outline */}
                    <rect x="60" y="40" width="180" height="220" fill="rgba(75,122,100,0.08)" stroke="rgba(75,122,100,0.8)" strokeWidth="2" strokeDasharray="6 4" />
                    
                    {/* Dimensions */}
                    <line x1="60" y1="20" x2="240" y2="20" stroke="var(--color-accent)" strokeWidth="1" />
                    <line x1="60" y1="15" x2="60" y2="25" stroke="var(--color-accent)" strokeWidth="1" />
                    <line x1="240" y1="15" x2="240" y2="25" stroke="var(--color-accent)" strokeWidth="1" />
                    <text x="150" y="12" fill="var(--color-accent)" fontSize="10" fontWeight="600" textAnchor="middle">30 FT</text>

                    <line x1="260" y1="40" x2="260" y2="260" stroke="var(--color-accent)" strokeWidth="1" />
                    <line x1="255" y1="40" x2="265" y2="40" stroke="var(--color-accent)" strokeWidth="1" />
                    <line x1="255" y1="260" x2="265" y2="260" stroke="var(--color-accent)" strokeWidth="1" />
                    <text x="270" y="150" fill="var(--color-accent)" fontSize="10" fontWeight="600" textAnchor="middle" transform="rotate(90 270 150)">40 FT</text>
                    
                    {/* Labels inside */}
                    <text x="150" y="140" fill="rgba(255,255,255,0.8)" fontSize="16" fontWeight="700" letterSpacing="2" textAnchor="middle">PLOT</text>
                    <text x="150" y="160" fill="rgba(255,255,255,0.4)" fontSize="10" letterSpacing="1" textAnchor="middle">1,200 SQ FT</text>
                    
                    {/* Compass */}
                    <g transform="translate(150, 275)">
                        <text x="0" y="10" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">↑ NORTH</text>
                    </g>
                    <g transform="translate(260, 150)">
                        <text x="30" y="4" fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">→ EAST</text>
                    </g>
                </svg>
            </motion.div>
        </motion.div>
    );
};

/* ─────────────────────────────────────────────────
   STEP 02 VISUAL — Requirements Configurator
───────────────────────────────────────────────── */
const RequirementsVisual = () => {
    return (
        <div style={{ width: '100%', height: '100%', backgroundColor: 'var(--color-surface-alt)', border: '1px solid var(--color-border)', borderRadius: '12px', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '2px' }}>HOUSE REQUIREMENTS</div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {[
                    { label: 'Bedrooms', val: '3' },
                    { label: 'Bathrooms', val: '2' },
                    { label: 'Floors', val: '1' }
                ].map((row, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '12px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <span style={{ color: 'var(--color-text-main)', fontWeight: 500 }}>{row.label}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <button style={{ background: 'transparent', border: '1px solid var(--color-border)', color: 'var(--color-text-muted)', width: '28px', height: '28px', borderRadius: '4px', cursor: 'default' }}>−</button>
                            <span style={{ color: 'var(--color-primary)', width: '12px', textAlign: 'center', fontWeight: 600 }}>{row.val}</span>
                            <button style={{ background: 'transparent', border: '1px solid var(--color-border)', color: 'var(--color-text-muted)', width: '28px', height: '28px', borderRadius: '4px', cursor: 'default' }}>+</button>
                        </div>
                    </div>
                ))}
            </div>

            <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '12px' }}>Selected spaces:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {['Living Room', 'Kitchen', 'Parking', 'Pooja Room', 'Balcony'].map((chip, i) => (
                        <div key={i} style={{ padding: '6px 12px', borderRadius: '20px', backgroundColor: 'rgba(75,122,100,0.15)', border: '1px solid rgba(75,122,100,0.4)', color: 'var(--color-primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span style={{ color: 'var(--color-accent)' }}>✓</span> {chip}
                        </div>
                    ))}
                </div>
            </div>

            <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginBottom: '12px' }}>Optional:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {['Study', 'Dining', 'Home Office'].map((chip, i) => (
                        <div key={i} style={{ padding: '6px 12px', borderRadius: '20px', backgroundColor: 'transparent', border: '1px dashed var(--color-border)', color: 'var(--color-text-muted)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span>+</span> {chip}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────────────
   STEP 03 VISUAL — Generated Plan
───────────────────────────────────────────────── */
const PlanVisual = () => {
    return (
        <div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: 'var(--color-surface-alt)', border: '1px solid var(--color-border)', borderRadius: '12px', padding: '24px', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: '24px', right: '24px', backgroundColor: 'rgba(75,122,100,0.1)', border: '1px solid rgba(75,122,100,0.3)', padding: '6px 12px', borderRadius: '6px', fontSize: '0.7rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '1px', zIndex: 10 }}>
                AI GENERATED PLAN
            </div>
            
            <svg viewBox="0 0 300 240" style={{ width: '100%', height: '100%' }}>
                {/* Outer walls */}
                <rect x="20" y="20" width="260" height="200" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="2" />
                
                {/* Inner walls */}
                <line x1="20" y1="120" x2="280" y2="120" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />
                <line x1="120" y1="20" x2="120" y2="120" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />
                <line x1="180" y1="120" x2="180" y2="220" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />
                <line x1="20" y1="180" x2="180" y2="180" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" />

                {/* Rooms fills to denote separate areas slightly */}
                <rect x="22" y="22" width="96" height="96" fill="rgba(75,122,100,0.1)" />
                <rect x="122" y="22" width="156" height="96" fill="rgba(75,122,100,0.05)" />
                <rect x="22" y="122" width="156" height="56" fill="rgba(75,122,100,0.08)" />
                <rect x="22" y="182" width="156" height="36" fill="rgba(75,122,100,0.03)" />
                <rect x="182" y="122" width="96" height="96" fill="rgba(75,122,100,0.06)" />

                {/* Labels */}
                <g textAnchor="middle" fill="rgba(255,255,255,0.8)" fontSize="8" fontWeight="600">
                    <text x="70" y="65">MASTER BED</text>
                    <text x="70" y="77" fill="var(--color-accent)" fontSize="6">12' × 14'</text>

                    <text x="200" y="65">BEDROOM</text>
                    <text x="200" y="77" fill="var(--color-accent)" fontSize="6">11' × 12'</text>

                    <text x="100" y="145">LIVING</text>
                    <text x="100" y="157" fill="var(--color-accent)" fontSize="6">14' × 16'</text>

                    <text x="100" y="195">KITCHEN</text>
                    <text x="100" y="207" fill="var(--color-accent)" fontSize="6">10' × 11'</text>

                    <text x="230" y="165">BATH</text>
                    <text x="230" y="177" fill="var(--color-accent)" fontSize="6">6' × 8'</text>
                </g>

                {/* Door indicators */}
                <path d="M120,80 Q135,70 135,80" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" strokeDasharray="2 1" />
                <path d="M180,180 Q195,170 195,180" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" strokeDasharray="2 1" />
                <path d="M80,120 Q80,135 95,135" fill="none" stroke="var(--color-text-muted)" strokeWidth="1" strokeDasharray="2 1" />
            </svg>
            
            <div style={{ position: 'absolute', bottom: '24px', left: '24px', display: 'flex', gap: '8px' }}>
                <span style={{ fontSize: '0.65rem', padding: '4px 8px', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.05)', color: 'var(--color-text-muted)' }}>OPTIMIZING SPACE</span>
                <span style={{ fontSize: '0.65rem', padding: '4px 8px', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.05)', color: 'var(--color-text-muted)' }}>NATURAL LIGHT</span>
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────────────
   STEP 04 VISUAL — Visualization
───────────────────────────────────────────────── */
const FinalVisualization = () => {
    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Main Exterior Image */}
            <div style={{ position: 'relative', flex: '2', borderRadius: '12px', overflow: 'hidden' }}>
                <img src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1000" alt="Exterior" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                <div style={{ position: 'absolute', bottom: '16px', left: '16px', backgroundColor: 'rgba(13,15,14,0.85)', backdropFilter: 'blur(8px)', padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <div style={{ fontSize: '0.65rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '1px' }}>EXTERIOR</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)', fontWeight: 500 }}>Modern Elevation</div>
                </div>
            </div>
            
            {/* Lower row: Interior + Metadata */}
            <div style={{ display: 'flex', gap: '16px', flex: '1', minHeight: '140px' }}>
                <div style={{ position: 'relative', flex: '1.5', borderRadius: '12px', overflow: 'hidden' }}>
                    <img src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=600" alt="Interior" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    <div style={{ position: 'absolute', bottom: '12px', left: '12px', backgroundColor: 'rgba(13,15,14,0.85)', backdropFilter: 'blur(8px)', padding: '6px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <div style={{ fontSize: '0.6rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '1px' }}>INTERIOR</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--color-primary)', fontWeight: 500 }}>Living Room</div>
                    </div>
                </div>
                <div style={{ flex: '1', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ flex: 1, backgroundColor: 'var(--color-surface-alt)', border: '1px solid var(--color-border)', borderRadius: '10px', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '0 16px' }}>
                        <div style={{ fontSize: '0.65rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '1px', marginBottom: '4px' }}>COST ESTIMATE</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--color-primary)' }}>Preview Available</div>
                    </div>
                    <div style={{ flex: 1, backgroundColor: 'rgba(75,122,100,0.05)', border: '1px dashed rgba(75,122,100,0.3)', borderRadius: '10px', display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '0 16px' }}>
                        <div style={{ fontSize: '0.65rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '1px', marginBottom: '4px' }}>3D VIEW</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>Coming Soon</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────────────
   MAIN SECTION
───────────────────────────────────────────────── */
const HowItWorks = () => {
    const steps = [
        {
            num: '01',
            title: 'DEFINE YOUR PLOT',
            desc: 'Input your exact plot dimensions, facing direction, and structural constraints. The AI Engine establishes the architectural boundaries for your future home.',
            Visual: PlotVisual,
            flip: false
        },
        {
            num: '02',
            title: 'SHAPE YOUR REQUIREMENTS',
            desc: 'Select the rooms and lifestyle spaces required for the home. Define your precise spatial needs before generating layouts.',
            Visual: RequirementsVisual,
            flip: true
        },
        {
            num: '03',
            title: 'GENERATE YOUR PLAN',
            desc: 'Watch as AI processes the plot and room requirements to produce an optimized architectural floor plan.',
            Visual: PlanVisual,
            flip: false
        },
        {
            num: '04',
            title: 'VISUALIZE YOUR HOME',
            desc: 'Bring the generated 2D plan to life with interior, exterior, cost estimation and future 3D visualization.',
            Visual: FinalVisualization,
            flip: true
        }
    ];

    return (
        <section id="how-it-works" style={{ backgroundColor: 'var(--color-surface)' }}>
            <div style={{ maxWidth: '1500px', margin: '0 auto', padding: '70px 5vw' }}>
                
                <div style={{ textAlign: 'center', marginBottom: '80px' }}>
                    <div style={{ fontSize: '0.8rem', letterSpacing: '3px', color: 'var(--color-accent)', fontWeight: 700, marginBottom: '16px' }}>THE INTELLIGENT WORKFLOW</div>
                    <h2 className="text-display" style={{ fontSize: 'clamp(2.4rem, 4vw, 3.5rem)', margin: 0, color: 'var(--color-primary)', lineHeight: 1.1 }}>
                        From plot to perfect plan.
                    </h2>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '80px' }}>
                    {steps.map((step, i) => {
                        const { num, title, desc, Visual, flip } = step;
                        const isFlipped = flip;

                        return (
                            <div key={i} className={`process-row ${isFlipped ? 'row-flipped' : ''}`} style={{
                                display: 'grid',
                                gridTemplateColumns: '1fr',
                                gap: '40px',
                                alignItems: 'center',
                                width: '100%',
                            }}>
                                
                                {/* TEXT BLOCK */}
                                <motion.div 
                                    className="process-text"
                                    initial={{ opacity: 0, x: -30 }}
                                    whileInView={{ opacity: 1, x: 0 }}
                                    viewport={{ once: true, amount: 0.25 }}
                                    transition={{ duration: 0.7 }}
                                    style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
                                >
                                    <div style={{ fontSize: '0.75rem', color: 'var(--color-accent)', fontWeight: 700, letterSpacing: '3px', marginBottom: '16px' }}>STEP {num}</div>
                                    <h3 style={{ fontSize: 'clamp(1.6rem, 3vw, 2.2rem)', color: 'var(--color-primary)', fontWeight: 700, letterSpacing: '1px', marginBottom: '20px', lineHeight: 1.2 }}>{title}</h3>
                                    <p style={{ fontSize: '1.05rem', color: 'var(--color-text-muted)', lineHeight: 1.7, maxWidth: '420px', margin: 0 }}>{desc}</p>
                                </motion.div>

                                {/* VISUAL BLOCK */}
                                <motion.div 
                                    className="process-visual"
                                    initial={{ opacity: 0, x: 35, scale: 0.98 }}
                                    whileInView={{ opacity: 1, x: 0, scale: 1 }}
                                    viewport={{ once: true, amount: 0.25 }}
                                    transition={{ duration: 0.8 }}
                                    style={{ width: '100%', maxWidth: '800px', height: '450px', margin: '0 auto' }}
                                >
                                    <Visual />
                                </motion.div>
                                
                            </div>
                        );
                    })}
                </div>

            </div>

            <style dangerouslySetInnerHTML={{__html: `
                @media (min-width: 900px) {
                    .process-row {
                        grid-template-columns: minmax(360px, 0.8fr) minmax(500px, 1.2fr) !important;
                        gap: 80px !important;
                    }
                    .row-flipped .process-text {
                        order: 2;
                    }
                    .row-flipped .process-visual {
                        order: 1;
                    }
                }
            `}} />
        </section>
    );
};

export default HowItWorks;
