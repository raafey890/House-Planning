import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useMotionValue, useSpring, useReducedMotion } from 'framer-motion';

const DesignShowcase = () => {
    const prefersReducedMotion = useReducedMotion();
    const containerRef = useRef(null);
    const { scrollYProgress } = useScroll({
        target: containerRef,
        offset: ["start end", "end start"]
    });

    const interiorImg = "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=1600";
    const exteriorImg = "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&q=80&w=1600";

    // Scroll Parallax (Scaling and Translating based on scroll progress)
    const yParallaxInterior = useTransform(scrollYProgress, [0, 1], prefersReducedMotion ? [0, 0] : [-30, 30]);
    const scaleInterior = useTransform(scrollYProgress, [0, 0.5], prefersReducedMotion ? [1, 1] : [1.05, 1]);
    
    const yParallaxExterior = useTransform(scrollYProgress, [0.3, 1], prefersReducedMotion ? [0, 0] : [30, -30]);
    const scaleExterior = useTransform(scrollYProgress, [0.3, 0.8], prefersReducedMotion ? [1, 1] : [1.05, 1]);

    // Pointer Parallax Configs
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    const handlePointerMove = (e, targetRef) => {
        if (!targetRef.current || prefersReducedMotion) return;
        const rect = targetRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        mouseX.set((e.clientX - centerX) / (rect.width / 2));
        mouseY.set((e.clientY - centerY) / (rect.height / 2));
    };

    const handlePointerLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    // Interior Pointer Springs (Lighter)
    const interiorSpringConfig = { damping: 30, stiffness: 100, mass: 1 };
    const intSmoothX = useSpring(mouseX, interiorSpringConfig);
    const intSmoothY = useSpring(mouseY, interiorSpringConfig);
    
    const intImgX = useTransform(intSmoothX, [-1, 1], [-5, 5]);
    const intImgY = useTransform(intSmoothY, [-1, 1], [-5, 5]);
    const intTextX = useTransform(intSmoothX, [-1, 1], [-15, 15]);
    const intTextY = useTransform(intSmoothY, [-1, 1], [-10, 10]);

    // Exterior Pointer Springs (Heavier/Slower)
    const exteriorSpringConfig = { damping: 50, stiffness: 80, mass: 1.5 };
    const extSmoothX = useSpring(mouseX, exteriorSpringConfig);
    const extSmoothY = useSpring(mouseY, exteriorSpringConfig);
    
    const extImgX = useTransform(extSmoothX, [-1, 1], [-3, 3]);
    const extImgY = useTransform(extSmoothY, [-1, 1], [-3, 3]);
    const extTextX = useTransform(extSmoothX, [-1, 1], [-10, 10]);
    const extTextY = useTransform(extSmoothY, [-1, 1], [-6, 6]);

    const interiorRef = useRef(null);
    const exteriorRef = useRef(null);

    return (
        <section ref={containerRef} style={{ backgroundColor: 'var(--color-background)' }}>
            
            {/* Interior Section */}
            <div 
                ref={interiorRef}
                onPointerMove={(e) => handlePointerMove(e, interiorRef)}
                onPointerLeave={handlePointerLeave}
                style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', position: 'relative', overflow: 'hidden', perspective: 1000 }}
            >
                <motion.div 
                    style={{ position: 'absolute', inset: -20, zIndex: 0, y: yParallaxInterior, scale: scaleInterior, x: intImgX }}
                >
                    <div style={{ width: '100%', height: '100%', backgroundImage: `url(${interiorImg})`, backgroundSize: 'cover', backgroundPosition: 'center' }}></div>
                </motion.div>
                
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to right, rgba(7,8,7,0.95) 0%, rgba(7,8,7,0.4) 50%, transparent 100%)', zIndex: 1, pointerEvents: 'none' }}></div>

                <div className="container" style={{ position: 'relative', zIndex: 2, width: '100%' }}>
                    <motion.div 
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        transition={{ duration: 0.8 }}
                        style={{ maxWidth: '550px', x: intTextX, y: intTextY }}
                    >
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>AI INTERIOR</span>
                        <h2 className="text-display" style={{ fontSize: 'clamp(3.5rem, 5vw, 4.5rem)', color: '#fff', lineHeight: 1.1, marginBottom: 'var(--space-6)', overflow: 'hidden' }}>
                            <motion.span initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }} style={{ display: 'block' }}>DESIGN THE</motion.span>
                            <motion.span initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }} style={{ display: 'block' }}>FEELING OF</motion.span>
                            <motion.span initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }} style={{ display: 'block' }}>EVERY ROOM.</motion.span>
                        </h2>
                        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.4 }} style={{ color: '#d1d1d1', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: 'var(--space-8)' }}>
                            Transform 2D floor plans into breathtaking 3D interior renders instantly. Experiment with luxury, minimalist, and contemporary styles to find the perfect atmosphere for your home.
                        </motion.p>
                        
                        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.6 }} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                            {['Modern', 'Minimal', 'Luxury', 'Traditional'].map(style => (
                                <div key={style} style={{ border: '1px solid rgba(255,255,255,0.2)', padding: '8px 16px', borderRadius: '4px', backdropFilter: 'blur(10px)', color: style === 'Modern' ? 'var(--color-primary)' : '#888', backgroundColor: style === 'Modern' ? 'rgba(255,255,255,0.1)' : 'transparent', fontSize: '0.85rem', letterSpacing: '1px' }}>
                                    {style.toUpperCase()}
                                </div>
                            ))}
                        </motion.div>
                    </motion.div>
                </div>
            </div>

            {/* Exterior Section */}
            <div 
                ref={exteriorRef}
                onPointerMove={(e) => handlePointerMove(e, exteriorRef)}
                onPointerLeave={handlePointerLeave}
                style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', position: 'relative', overflow: 'hidden', perspective: 1000 }}
            >
                <motion.div 
                    style={{ position: 'absolute', inset: -20, zIndex: 0, y: yParallaxExterior, scale: scaleExterior, x: extImgX }}
                >
                    <div style={{ width: '100%', height: '100%', backgroundImage: `url(${exteriorImg})`, backgroundSize: 'cover', backgroundPosition: 'center' }}></div>
                </motion.div>
                
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to left, rgba(7,8,7,0.95) 0%, rgba(7,8,7,0.4) 50%, transparent 100%)', zIndex: 1, pointerEvents: 'none' }}></div>

                <div className="container" style={{ position: 'relative', zIndex: 2, width: '100%', display: 'flex', justifyContent: 'flex-end' }}>
                    <motion.div 
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        transition={{ duration: 0.8 }}
                        style={{ maxWidth: '500px', textAlign: 'right', x: extTextX, y: extTextY }}
                    >
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>ELEVATION GENERATION</span>
                        <h2 className="text-display" style={{ fontSize: 'clamp(3.5rem, 5vw, 4.5rem)', color: '#fff', lineHeight: 1.1, marginBottom: 'var(--space-6)', overflow: 'hidden' }}>
                            <motion.span initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6, ease: "easeOut" }} style={{ display: 'block' }}>FROM PLAN</motion.span>
                            <motion.span initial={{ y: "100%" }} whileInView={{ y: 0 }} transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }} style={{ display: 'block' }}>TO PRESENCE.</motion.span>
                        </h2>
                        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.3 }} style={{ color: '#d1d1d1', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: 'var(--space-8)' }}>
                            Visualize the facade of your future home. The AI interprets structural constraints, floors, and dimensions to generate structurally viable and stunning architectural elevations.
                        </motion.p>
                        
                        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ delay: 0.5 }} style={{ display: 'inline-block', border: '1px solid rgba(255,255,255,0.2)', padding: '12px 24px', borderRadius: '4px', backdropFilter: 'blur(10px)', color: '#fff', fontSize: '0.9rem', letterSpacing: '1px' }}>
                            CONTEMPORARY FACADE
                        </motion.div>
                    </motion.div>
                </div>
            </div>

        </section>
    );
};

export default DesignShowcase;
