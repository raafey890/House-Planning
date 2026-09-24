import React, { useRef } from 'react';
import { CheckCircle2 } from 'lucide-react';
import { motion, useMotionValue, useSpring, useTransform, useReducedMotion } from 'framer-motion';

const FloorPlanShowcase = () => {
    const prefersReducedMotion = useReducedMotion();
    const containerRef = useRef(null);

    // Pointer Parallax Configs
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const handlePointerMove = (e) => {
        if (!containerRef.current || prefersReducedMotion) return;
        const rect = containerRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        mouseX.set((e.clientX - centerX) / (rect.width / 2));
        mouseY.set((e.clientY - centerY) / (rect.height / 2));
    };

    const handlePointerLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    const springConfig = { damping: 40, stiffness: 100, mass: 1 };
    const smoothX = useSpring(mouseX, springConfig);
    const smoothY = useSpring(mouseY, springConfig);

    // Layer Depth (0.25x, 0.5x, 0.8x, 1x)
    const gridX = useTransform(smoothX, [-1, 1], [-2, 2]); // 0.25x roughly
    const gridY = useTransform(smoothY, [-1, 1], [-2, 2]);
    
    const planX = useTransform(smoothX, [-1, 1], [-6, 6]); // 0.5x
    const planY = useTransform(smoothY, [-1, 1], [-6, 6]);
    
    const annotationX = useTransform(smoothX, [-1, 1], [-12, 12]); // 0.8x
    const annotationY = useTransform(smoothY, [-1, 1], [-12, 12]);
    
    const metaX = useTransform(smoothX, [-1, 1], [-18, 18]); // 1x
    const metaY = useTransform(smoothY, [-1, 1], [-18, 18]);

    return (
        <section 
            style={{ backgroundColor: '#F4F1EB', position: 'relative', overflow: 'hidden', padding: 'var(--space-24) 0' }}
            onPointerMove={handlePointerMove}
            onPointerLeave={handlePointerLeave}
            ref={containerRef}
        >
            {/* Subtle architectural background grid for the light section */}
            <motion.div style={{ position: 'absolute', inset: -20, opacity: 0.1, pointerEvents: 'none', backgroundImage: 'linear-gradient(#2A302D 1px, transparent 1px), linear-gradient(90deg, #2A302D 1px, transparent 1px)', backgroundSize: '40px 40px', x: gridX, y: gridY }}></motion.div>

            <div className="container" style={{ position: 'relative', zIndex: 2 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', '@media(minWidth: 992px)': { gridTemplateColumns: '1fr 1.2fr' }, gap: 'var(--space-16)', alignItems: 'center' }}>
                    
                    {/* LEFT: Text Content */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        transition={{ duration: 0.8 }}
                    >
                        <span style={{ color: '#4b7a64', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>CORE TECHNOLOGY</span>
                        <div style={{ overflow: 'hidden', marginBottom: 'var(--space-6)' }}>
                            <motion.h2 className="text-display" style={{ fontSize: 'clamp(2.5rem, 4vw, 3.5rem)', color: '#18191B', lineHeight: 1.1, margin: 0 }}
                                initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6 }} viewport={{ once: true }}
                            >
                                Generative<br/>Layout<br/>Intelligence
                            </motion.h2>
                        </div>
                        <motion.p 
                            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.3 }} viewport={{ once: true }}
                            style={{ color: '#5e646b', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: 'var(--space-8)', maxWidth: '400px' }}
                        >
                            Our AI understands spatial relationships and architectural norms. It automatically generates high-quality structured floor plans optimized for your specific plot size, facing direction, and lifestyle constraints.
                        </motion.p>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {["Accurate room dimensions", "Strategic door & window placement", "Multiple plan variations", "Exportable structured layout data"].map((f, i) => (
                                <motion.div 
                                    key={i} 
                                    initial={{ opacity: 0, y: 10 }} 
                                    whileInView={{ opacity: 1, y: 0 }} 
                                    viewport={{ once: true }}
                                    transition={{ delay: 0.4 + (i * 0.1) }}
                                    style={{ display: 'flex', alignItems: 'center', gap: '12px' }}
                                >
                                    <div style={{ backgroundColor: 'rgba(75, 122, 100, 0.1)', padding: '6px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <CheckCircle2 size={16} color="#4b7a64" />
                                    </div>
                                    <span style={{ fontSize: '1rem', color: '#18191B', fontWeight: 500 }}>{f}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    {/* RIGHT: Light Architectural Floor Plan Visual */}
                    <div style={{ position: 'relative', height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', perspective: 1000 }}>
                        
                        <motion.div 
                            initial={{ scale: 0.95, opacity: 0 }}
                            whileInView={{ scale: 1, opacity: 1 }}
                            viewport={{ once: true, margin: "-20%" }}
                            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
                            style={{ 
                                width: '100%', height: '100%', 
                                border: '1px solid rgba(24, 25, 27, 0.1)', 
                                borderRadius: 'var(--radius-lg)', 
                                backgroundColor: '#FFFFFF', 
                                position: 'relative', overflow: 'hidden', 
                                display: 'flex', alignItems: 'center', justifyContent: 'center', 
                                boxShadow: '0 20px 40px rgba(0,0,0,0.08)' 
                            }}
                        >
                            {/* Blueprint SVG Animation (Layer: Plan 0.5x) */}
                            <motion.svg viewBox="-2 -2 44 64" style={{ width: '80%', height: '80%', x: planX, y: planY }}>
                                {/* Boundary */}
                                <motion.rect 
                                    initial={{ pathLength: 0 }} whileInView={{ pathLength: 1 }} transition={{ duration: 1.5, ease: "easeInOut" }} viewport={{ once: true }}
                                    x="0" y="0" width="40" height="60" fill="none" stroke="#A3A6A4" strokeWidth="0.2" strokeDasharray="0.5 0.5" 
                                />
                                {/* Rooms */}
                                <motion.rect initial={{ fill: "transparent" }} whileInView={{ fill: "#F4F1EB" }} transition={{ delay: 0.8, duration: 0.8 }} viewport={{ once: true }} x="2" y="2" width="16" height="20" stroke="#18191B" strokeWidth="0.3" />
                                <motion.text initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 1.2 }} x="10" y="11" textAnchor="middle" fontSize="1.5" fill="#18191B" fontWeight="600">LIVING</motion.text>
                                
                                <motion.rect initial={{ fill: "transparent" }} whileInView={{ fill: "#F9F8F6" }} transition={{ delay: 1.0, duration: 0.8 }} viewport={{ once: true }} x="20" y="2" width="18" height="15" stroke="#18191B" strokeWidth="0.3" />
                                <motion.text initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 1.4 }} x="29" y="9" textAnchor="middle" fontSize="1.2" fill="#5e646b" fontWeight="600">KITCHEN</motion.text>
                                
                                <motion.rect initial={{ fill: "transparent" }} whileInView={{ fill: "#F9F8F6" }} transition={{ delay: 1.2, duration: 0.8 }} viewport={{ once: true }} x="2" y="24" width="16" height="18" stroke="#18191B" strokeWidth="0.3" />
                                <motion.text initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 1.6 }} x="10" y="32" textAnchor="middle" fontSize="1.2" fill="#5e646b" fontWeight="600">BEDROOM 1</motion.text>
                            </motion.svg>

                            {/* Blueprint Annotations (Layer: Annotation 0.8x) */}
                            <motion.svg viewBox="-2 -2 44 64" style={{ width: '80%', height: '80%', position: 'absolute', inset: 0, margin: 'auto', pointerEvents: 'none', x: annotationX, y: annotationY }}>
                                <motion.line initial={{ pathLength: 0 }} whileInView={{ pathLength: 1 }} transition={{ delay: 2, duration: 1 }} viewport={{ once: true }} x1="2" y1="-1" x2="40" y2="-1" stroke="#4b7a64" strokeWidth="0.2" />
                                <motion.text initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 2.5 }} x="21" y="-1.5" textAnchor="middle" fontSize="1" fill="#4b7a64" fontWeight="600">30'</motion.text>
                                
                                <motion.line initial={{ pathLength: 0 }} whileInView={{ pathLength: 1 }} transition={{ delay: 2.2, duration: 1 }} viewport={{ once: true }} x1="41" y1="0" x2="41" y2="60" stroke="#4b7a64" strokeWidth="0.2" />
                                <motion.text initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 2.7 }} x="42" y="30" textAnchor="middle" fontSize="1" fill="#4b7a64" fontWeight="600" transform="rotate(90 42 30)">40'</motion.text>
                            </motion.svg>
                        </motion.div>

                        {/* Floating Details - Dark Charcoal Translucent (Layer: Metadata 1x) */}
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ delay: 2.4, duration: 0.6, type: "spring", stiffness: 100 }}
                            style={{ 
                                position: 'absolute', bottom: '-20px', left: '-20px', 
                                backgroundColor: 'rgba(24, 25, 27, 0.95)', backdropFilter: 'blur(12px)',
                                padding: 'var(--space-6)', width: '220px',
                                borderRadius: 'var(--radius-sm)',
                                color: '#F2F0EA',
                                boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
                                x: metaX, y: metaY
                            }}
                        >
                            <div style={{ fontWeight: 600, fontSize: '0.85rem', letterSpacing: '2px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '8px', marginBottom: '12px', color: '#4b7a64' }}>
                                PROJECT 01
                            </div>
                            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px', color: '#8c938f' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Plot:</span> <b style={{color: '#fff'}}>30 × 40 FT</b></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Facing:</span> <b style={{color: '#fff'}}>EAST</b></div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>Beds:</span> <b style={{color: '#fff'}}>3</b></div>
                            </div>
                        </motion.div>
                    </div>
                    
                </div>
            </div>
            
            <style dangerouslySetInnerHTML={{__html: `
                @media (min-width: 992px) {
                    .container > div {
                        grid-template-columns: 1fr 1.2fr;
                    }
                }
            `}} />
        </section>
    );
};

export default FloorPlanShowcase;
