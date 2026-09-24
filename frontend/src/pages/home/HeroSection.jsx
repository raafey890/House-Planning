import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const HeroSection = () => {
    const stageRef = useRef(null);

    // Raw mouse MotionValues (no state, no re-render)
    const rawX = useMotionValue(0);
    const rawY = useMotionValue(0);

    // Smooth springs — heavy, fluid
    const springCfg = { stiffness: 80, damping: 20, mass: 1 };
    const x = useSpring(rawX, springCfg);
    const y = useSpring(rawY, springCfg);

    // -- House image transforms --
    const imgX       = useTransform(x, [-1, 1], [-12, 12]);
    const imgY       = useTransform(y, [-1, 1], [-8,  8]);
    const imgRotateX = useTransform(y, [-1, 1], [3,  -3]);
    const imgRotateY = useTransform(x, [-1, 1], [-4,  4]);

    // -- Project card (farther depth = more movement) --
    const cardX = useTransform(x, [-1, 1], [-22, 22]);
    const cardY = useTransform(y, [-1, 1], [-16, 16]);

    // -- Badge (closest layer = most movement) --
    const badgeX = useTransform(x, [-1, 1], [-28, 28]);
    const badgeY = useTransform(y, [-1, 1], [-18, 18]);

    // -- Grid (background, least movement) --
    const gridX = useTransform(x, [-1, 1], [-6, 6]);
    const gridY = useTransform(y, [-1, 1], [-4, 4]);

    const handleMove = (e) => {
        const el = stageRef.current;
        if (!el) return;
        const r = el.getBoundingClientRect();
        rawX.set((e.clientX - r.left - r.width  / 2) / (r.width  / 2));
        rawY.set((e.clientY - r.top  - r.height / 2) / (r.height / 2));
    };

    const handleLeave = () => {
        rawX.set(0);
        rawY.set(0);
    };

    return (
        <section className="hero-section">
            <div className="hero-container">

                    {/* ── LEFT: Content ── */}
                    <motion.div
                        className="hero-content"
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                    >
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: '24px' }}>
                            INTELLIGENT ARCHITECTURE
                        </span>
                        <h1 className="text-display" style={{ fontSize: 'clamp(3rem, 6vw, 5rem)', lineHeight: 1.1, marginBottom: '24px', color: 'var(--color-primary)' }}>
                            Design your home with AI precision.
                        </h1>
                        <p style={{ fontSize: '1.1rem', color: 'var(--color-text-muted)', maxWidth: '480px', marginBottom: '32px', lineHeight: 1.6 }}>
                            From plot dimensions and room requirements to intelligent floor plans, visual design and construction planning.
                        </p>
                        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
                            <Link to="/planner" className="btn btn-primary btn-lg"
                                style={{ backgroundColor: 'var(--color-accent)', color: '#fff', border: 'none', padding: '0 32px' }}>
                                Start Designing <ArrowRight size={18} style={{ marginLeft: '8px' }} />
                            </Link>
                            <a href="#how-it-works" className="btn btn-outline btn-lg"
                                style={{ borderColor: 'rgba(255,255,255,0.15)', color: 'var(--color-primary)' }}>
                                Explore Platform
                            </a>
                        </div>
                    </motion.div>

                    {/* ── RIGHT: Interactive Parallax Stage ── */}
                    <motion.div
                        ref={stageRef}
                        onPointerMove={handleMove}
                        onPointerLeave={handleLeave}
                        initial={{ opacity: 0, scale: 0.96 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1.1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
                        style={{
                            position: 'relative',
                            height: '600px',
                            perspective: '1200px',
                            cursor: 'none',
                        }}
                    >
                        {/* ── Grid / blueprint layer (background, least movement) ── */}
                        <motion.div
                            style={{
                                position: 'absolute',
                                inset: -40,
                                border: '1px solid rgba(255,255,255,0.06)',
                                pointerEvents: 'none',
                                x: gridX,
                                y: gridY,
                            }}
                        >
                            <div style={{ position:'absolute', left:'50%', top:0, bottom:0, borderLeft:'1px dashed rgba(255,255,255,0.06)' }} />
                            <div style={{ position:'absolute', top:'50%', left:0, right:0, borderTop:'1px dashed rgba(255,255,255,0.06)' }} />
                        </motion.div>

                        {/* ── House image (base layer) ── */}
                        <motion.div
                            style={{
                                position: 'absolute',
                                inset: 0,
                                margin: 'auto',
                                width: '85%',
                                height: '75%',
                                top: '50%',
                                left: '50%',
                                /* NO static transform here — Framer owns the transform */
                                borderRadius: '8px',
                                overflow: 'hidden',
                                boxShadow: '0 30px 60px rgba(0,0,0,0.7)',
                                backgroundImage: 'url("https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=1200")',
                                backgroundSize: 'cover',
                                backgroundPosition: 'center',
                                // Motion values — Framer handles translateX/Y + rotateX/Y in one transform
                                x: imgX,
                                y: imgY,
                                rotateX: imgRotateX,
                                rotateY: imgRotateY,
                                translateX: '-50%',
                                translateY: '-50%',
                            }}
                        >
                            <div style={{ position:'absolute', inset:0, background:'linear-gradient(to top, rgba(7,8,7,0.85) 0%, transparent 40%)' }} />
                        </motion.div>

                        {/* ── Project Details card (mid layer) ── */}
                        <motion.div
                            style={{
                                position: 'absolute',
                                bottom: '6%',
                                left: '2%',
                                backgroundColor: 'rgba(13,15,14,0.88)',
                                backdropFilter: 'blur(14px)',
                                border: '1px solid rgba(255,255,255,0.1)',
                                padding: '20px 24px',
                                borderRadius: '6px',
                                boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                                x: cardX,
                                y: cardY,
                                zIndex: 2,
                            }}
                        >
                            <div style={{ fontSize:'0.7rem', color:'var(--color-accent)', fontWeight:700, letterSpacing:'2px', marginBottom:'12px' }}>PROJECT 01</div>
                            <div style={{ color:'var(--color-primary)', fontSize:'1.05rem', fontWeight:600, marginBottom:'8px' }}>30 × 40 FT</div>
                            <div style={{ color:'var(--color-text-muted)', fontSize:'0.82rem', marginBottom:'4px' }}>EAST FACING</div>
                            <div style={{ color:'var(--color-text-muted)', fontSize:'0.82rem' }}>3 BEDROOMS</div>
                        </motion.div>

                        {/* ── AI Badge (front layer — most movement) ── */}
                        <motion.div
                            style={{
                                position: 'absolute',
                                top: '14%',
                                right: '4%',
                                backgroundColor: 'var(--color-accent)',
                                color: '#fff',
                                padding: '10px 20px',
                                borderRadius: '999px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                fontSize: '0.85rem',
                                fontWeight: 600,
                                boxShadow: '0 10px 30px rgba(75,122,100,0.45)',
                                x: badgeX,
                                y: badgeY,
                                zIndex: 3,
                            }}
                        >
                            <Sparkles size={15} /> AI Generated
                        </motion.div>

                    </motion.div>
                    {/* ── END Stage ── */}

                </div>
            <div style={{ position:'absolute', bottom:0, left:0, right:0, height:'20vh', background:'linear-gradient(to top, var(--color-background), transparent)', zIndex:1, pointerEvents:'none' }} />
        </section>
    );
};

export default HeroSection;