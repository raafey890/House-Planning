import React, { useRef, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';
import { Box } from 'lucide-react';

const ThreeDSection = () => {
    const containerRef = useRef(null);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

    const handleMouseMove = (e) => {
        if (!containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width * 2 - 1;
        const y = (e.clientY - rect.top) / rect.height * 2 - 1;
        setMousePosition({ x, y });
    };

    const handleMouseLeave = () => {
        setMousePosition({ x: 0, y: 0 });
    };

    const springConfig = { damping: 30, stiffness: 100 };
    const rotateX = useSpring(mousePosition.y * -5, springConfig);
    const rotateY = useSpring(mousePosition.x * 5, springConfig);

    return (
        <section className="section-padding" style={{ backgroundColor: 'var(--color-surface)', overflow: 'hidden' }}>
            <div className="container">
                
                <div style={{ textAlign: 'center', marginBottom: 'var(--space-12)' }}>
                    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>IMMERSIVE EXPLORATION</span>
                        <h2 className="text-display" style={{ fontSize: 'clamp(2.5rem, 4vw, 3.5rem)', color: 'var(--color-primary)', margin: 0 }}>Step inside before you build.</h2>
                    </motion.div>
                </div>

                {/* Smaller, premium 3D presentation stage */}
                <motion.div
                    ref={containerRef}
                    onMouseMove={handleMouseMove}
                    onMouseLeave={handleMouseLeave}
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true, margin: "-10%" }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    style={{ 
                        perspective: 1200,
                        width: '100%', 
                        maxWidth: '900px', 
                        margin: '0 auto', 
                        height: '450px', 
                        position: 'relative'
                    }}
                >
                    <motion.div
                        style={{
                            width: '100%', height: '100%',
                            borderRadius: 'var(--radius-lg)',
                            position: 'relative',
                            transformStyle: 'preserve-3d',
                            rotateX, rotateY
                        }}
                    >
                        {/* Base Render Image */}
                        <div style={{ 
                            position: 'absolute', inset: 0, 
                            backgroundImage: 'url("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1200")',
                            backgroundSize: 'cover', backgroundPosition: 'center',
                            borderRadius: 'var(--radius-lg)',
                            boxShadow: '0 30px 60px rgba(0,0,0,0.6)',
                            transform: 'translateZ(-20px)'
                        }}>
                            <div style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(7, 8, 7, 0.4)' }}></div>
                        </div>

                        {/* Wireframe / Grid overlay (simulating a 3D workspace layer) */}
                        <div style={{ 
                            position: 'absolute', inset: -20, 
                            backgroundImage: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)', 
                            backgroundSize: '30px 30px',
                            transform: 'translateZ(30px)', pointerEvents: 'none',
                            borderRadius: 'var(--radius-lg)',
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}></div>

                        {/* Center Icon */}
                        <div style={{ 
                            position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%) translateZ(60px)',
                            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px'
                        }}>
                            <div style={{ backgroundColor: 'rgba(13, 15, 14, 0.8)', padding: '16px', borderRadius: '50%', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.1)' }}>
                                <Box size={32} color="var(--color-primary)" />
                            </div>
                        </div>

                        {/* Floating Labels */}
                        <div style={{ position: 'absolute', top: '10%', left: '10%', transform: 'translateZ(40px)', color: 'var(--color-primary)', fontSize: '0.75rem', letterSpacing: '2px', fontWeight: 600 }}>ORBIT</div>
                        <div style={{ position: 'absolute', bottom: '10%', right: '10%', transform: 'translateZ(40px)', color: 'var(--color-primary)', fontSize: '0.75rem', letterSpacing: '2px', fontWeight: 600 }}>ZOOM</div>
                        <div style={{ position: 'absolute', top: '50%', right: '5%', transform: 'translateZ(40px)', color: 'var(--color-text-muted)', fontSize: '0.75rem', letterSpacing: '2px', fontWeight: 600 }}>MULTI-FLOOR</div>

                    </motion.div>

                    {/* Coming Soon Badge (Outside the 3D rotation, stays flat to screen) */}
                    <div style={{ position: 'absolute', bottom: '-20px', left: '50%', transform: 'translateX(-50%)', zIndex: 10 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', padding: '12px 24px', backgroundColor: 'rgba(13, 15, 14, 0.95)', backdropFilter: 'blur(12px)', borderRadius: '99px', border: '1px solid var(--color-border)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
                            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-accent)', boxShadow: '0 0 10px var(--color-accent)' }}></div>
                            <span style={{ color: '#fff', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '1px' }}>3D EXPERIENCE — IN DEVELOPMENT</span>
                        </div>
                    </div>

                </motion.div>

            </div>
        </section>
    );
};

export default ThreeDSection;
