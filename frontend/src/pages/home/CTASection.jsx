import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const CTASection = () => {
    return (
        <section className="section-padding" style={{ position: 'relative', overflow: 'hidden', minHeight: '80vh', display: 'flex', alignItems: 'center' }}>
            
            {/* Dark immersive background */}
            <div style={{ position: 'absolute', inset: 0, backgroundColor: 'var(--color-surface-alt)', zIndex: 0 }}></div>
            
            {/* Cinematic Light Source */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '800px', height: '800px', background: 'radial-gradient(circle, rgba(55,89,73,0.15) 0%, transparent 60%)', zIndex: 1, pointerEvents: 'none' }}></div>

            <div className="container" style={{ position: 'relative', zIndex: 2, textAlign: 'center' }}>
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: "-20%" }}
                    transition={{ duration: 1 }}
                >
                    <h2 className="text-display" style={{ fontSize: 'clamp(3rem, 6vw, 6rem)', lineHeight: 1.1, margin: 0, color: 'var(--color-text-muted)' }}>
                        YOUR PLOT.<br />
                        YOUR REQUIREMENTS.<br />
                        <span style={{ color: 'var(--color-primary)' }}>YOUR HOME.</span>
                    </h2>
                    
                    <p style={{ margin: 'var(--space-8) auto', fontSize: '1.25rem', color: '#a0a0a0', maxWidth: '600px' }}>
                        Designed intelligently. Start planning your architectural vision today.
                    </p>

                    {/* Magnetic-like CTA (Framer Motion makes it easy to add whileHover scale, but "magnetic" implies tracking mouse. 
                        To keep performance high on a CTA, we use a simple elegant hover scale) */}
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} style={{ display: 'inline-block' }}>
                        <Link to="/signup" className="btn btn-primary btn-lg" style={{ padding: '0 var(--space-12)', height: '64px', fontSize: '1.1rem', backgroundColor: 'var(--color-accent)', color: '#fff', border: 'none' }}>
                            Start Your Project <ArrowRight size={20} style={{ marginLeft: '12px' }} />
                        </Link>
                    </motion.div>
                </motion.div>
            </div>
        </section>
    );
};

export default CTASection;