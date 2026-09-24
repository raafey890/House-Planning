import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, MoveUpRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const GalleryPreview = () => {
    const prefersReducedMotion = useReducedMotion();
    
    const images = [
        { src: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&q=80&w=1200", title: "Modern Exterior", subtitle: "Elevation" },
        { src: "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=800", title: "Minimalist Living", subtitle: "Interior" },
        { src: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=800", title: "Structured Layout", subtitle: "Floor Plan" }
    ];

    // Variants for the gallery items
    const itemVariants = {
        rest: { opacity: 1 },
        hover: { opacity: 1 }
    };
    
    const imgVariants = {
        rest: { scale: 1 },
        hover: { scale: prefersReducedMotion ? 1 : 1.04 }
    };
    
    const overlayVariants = {
        rest: { opacity: 0 },
        hover: { opacity: 1 }
    };

    const textVariants = {
        rest: { y: 20 },
        hover: { y: 0 }
    };
    
    const arrowVariants = {
        rest: { x: 0, y: 0 },
        hover: { x: 4, y: -4 }
    };

    return (
        <section className="section-padding" style={{ backgroundColor: 'var(--color-surface-alt)' }}>
            <div className="container">
                
                <div style={{ display: 'flex', flexDirection: 'column', '@media(minWidth: 768px)': { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end' }, marginBottom: 'var(--space-12)' }}>
                    <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>GALLERY</span>
                        <h2 className="text-display" style={{ fontSize: 'clamp(2.5rem, 4vw, 3.5rem)', margin: 0, color: 'var(--color-primary)' }}>Architectural Archive.</h2>
                    </motion.div>
                    <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} style={{ marginTop: 'var(--space-6)' }}>
                        <Link to="/gallery" className="btn btn-ghost" style={{ color: 'var(--color-primary)', padding: 0 }}>
                            Explore Archive <ArrowRight size={18} style={{ marginLeft: '8px' }} />
                        </Link>
                    </motion.div>
                </div>

                <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr', 
                    gap: 'var(--space-4)', 
                    height: 'auto', 
                    minHeight: '600px' 
                }} className="gallery-grid">
                    
                    {/* Img 1: Large Exterior (Left) */}
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1, duration: 0.8 }}
                        style={{ position: 'relative', overflow: 'hidden', borderRadius: 'var(--radius-lg)', cursor: 'pointer', minHeight: '300px' }}
                        variants={itemVariants} initial="rest" whileHover="hover" animate="rest"
                        className="gallery-item-left"
                    >
                        <motion.img 
                            src={images[0].src} 
                            variants={imgVariants}
                            transition={{ duration: 0.6, ease: "easeOut" }}
                            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                        />
                        <motion.div 
                            variants={overlayVariants}
                            transition={{ duration: 0.3 }}
                            style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(7,8,7,0.9), transparent)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 'var(--space-8)' }}
                        >
                            <motion.div variants={textVariants} transition={{ duration: 0.4, ease: "easeOut" }} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                                <div>
                                    <div style={{ color: 'var(--color-accent)', fontSize: '0.85rem', letterSpacing: '1px', fontWeight: 600, marginBottom: '8px' }}>{images[0].subtitle.toUpperCase()}</div>
                                    <h4 style={{ color: '#fff', fontSize: '2rem', margin: 0, fontFamily: 'var(--font-family-display)' }}>{images[0].title}</h4>
                                </div>
                                <div style={{ backgroundColor: 'var(--color-primary)', color: 'var(--color-background)', padding: '12px', borderRadius: '50%' }}>
                                    <motion.div variants={arrowVariants} transition={{ duration: 0.3 }}>
                                        <MoveUpRight size={24} />
                                    </motion.div>
                                </div>
                            </motion.div>
                        </motion.div>
                    </motion.div>

                    {/* Right Column Stack */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }} className="gallery-column-right">
                        
                        {/* Img 2: Interior (Top Right) */}
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.3, duration: 0.8 }}
                            style={{ flex: 1, position: 'relative', overflow: 'hidden', borderRadius: 'var(--radius-lg)', cursor: 'pointer', minHeight: '250px' }}
                            variants={itemVariants} initial="rest" whileHover="hover" animate="rest"
                        >
                            <motion.img 
                                src={images[1].src} 
                                variants={imgVariants}
                                transition={{ duration: 0.6, ease: "easeOut" }}
                                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                            />
                            <motion.div 
                                variants={overlayVariants}
                                transition={{ duration: 0.3 }}
                                style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(7,8,7,0.9), transparent)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 'var(--space-6)' }}
                            >
                                <motion.div variants={textVariants} transition={{ duration: 0.4, ease: "easeOut" }}>
                                    <div style={{ color: 'var(--color-accent)', fontSize: '0.75rem', letterSpacing: '1px', fontWeight: 600, marginBottom: '4px' }}>{images[1].subtitle.toUpperCase()}</div>
                                    <h4 style={{ color: '#fff', fontSize: '1.25rem', margin: 0 }}>{images[1].title}</h4>
                                </motion.div>
                            </motion.div>
                        </motion.div>

                        {/* Img 3: Floor Plan (Bottom Right) */}
                        <motion.div 
                            initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.5, duration: 0.8 }}
                            style={{ flex: 1, position: 'relative', overflow: 'hidden', borderRadius: 'var(--radius-lg)', cursor: 'pointer', minHeight: '250px' }}
                            variants={itemVariants} initial="rest" whileHover="hover" animate="rest"
                        >
                            <motion.img 
                                src={images[2].src} 
                                variants={imgVariants}
                                transition={{ duration: 0.6, ease: "easeOut" }}
                                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                            />
                            <motion.div 
                                variants={overlayVariants}
                                transition={{ duration: 0.3 }}
                                style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(7,8,7,0.9), transparent)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 'var(--space-6)' }}
                            >
                                <motion.div variants={textVariants} transition={{ duration: 0.4, ease: "easeOut" }}>
                                    <div style={{ color: 'var(--color-accent)', fontSize: '0.75rem', letterSpacing: '1px', fontWeight: 600, marginBottom: '4px' }}>{images[2].subtitle.toUpperCase()}</div>
                                    <h4 style={{ color: '#fff', fontSize: '1.25rem', margin: 0 }}>{images[2].title}</h4>
                                </motion.div>
                            </motion.div>
                        </motion.div>

                    </div>
                </div>
            </div>

            <style dangerouslySetInnerHTML={{__html: `
                @media (min-width: 992px) {
                    .gallery-grid {
                        grid-template-columns: 2fr 1fr !important;
                    }
                }
            `}} />
        </section>
    );
};

export default GalleryPreview;
