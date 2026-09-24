import React from 'react';
import { motion } from 'framer-motion';

const EstimatorSection = () => {
    const costBreakdown = [
        { label: "Material", value: "45%", amount: "₹ 2,250,000", color: "#f2efe9" },
        { label: "Labor", value: "25%", amount: "₹ 1,250,000", color: "var(--color-accent)" },
        { label: "Electrical", value: "10%", amount: "₹ 500,000", color: "var(--color-text-muted)" },
        { label: "Plumbing", value: "10%", amount: "₹ 500,000", color: "#4b7a64" },
        { label: "Interior", value: "10%", amount: "₹ 500,000", color: "#2a302d" },
    ];

    return (
        <section className="section-padding" style={{ backgroundColor: 'var(--color-surface-alt)' }}>
            <div className="container">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: 'var(--space-16)', alignItems: 'center' }}>
                    
                    {/* Left: Text */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-20%" }}
                        transition={{ duration: 0.8 }}
                    >
                        <span style={{ color: 'var(--color-accent)', fontWeight: 600, letterSpacing: '2px', fontSize: '0.85rem', display: 'block', marginBottom: 'var(--space-4)' }}>COST INTELLIGENCE</span>
                        <h2 className="text-display" style={{ fontSize: '3.5rem', marginBottom: 'var(--space-6)', color: 'var(--color-primary)' }}>Financial clarity.</h2>
                        <p style={{ color: 'var(--color-text-muted)', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: 'var(--space-8)' }}>
                            No more guesswork. Get instant, dynamic construction cost estimates based on your generated floor plan, structural complexity, and chosen material quality. 
                        </p>
                        <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                            * Values shown are illustrative examples.
                        </p>
                    </motion.div>

                    {/* Right: Premium Data Viz */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true, margin: "-20%" }}
                        transition={{ duration: 0.8 }}
                        style={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-8)', boxShadow: 'var(--shadow-lg)' }}
                    >
                        <div style={{ marginBottom: 'var(--space-8)' }}>
                            <div style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', marginBottom: '8px' }}>TOTAL ESTIMATED COST</div>
                            <div className="text-display" style={{ fontSize: '3.5rem', color: 'var(--color-primary)' }}>₹ 5,000,000</div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                            {costBreakdown.map((item, i) => (
                                <div key={i}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.9rem' }}>
                                        <span style={{ color: 'var(--color-text-main)', fontWeight: 500 }}>{item.label}</span>
                                        <span style={{ color: 'var(--color-text-muted)' }}>{item.amount}</span>
                                    </div>
                                    <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--color-surface-alt)', borderRadius: '2px', overflow: 'hidden' }}>
                                        <motion.div 
                                            initial={{ width: 0 }}
                                            whileInView={{ width: item.value }}
                                            viewport={{ once: true }}
                                            transition={{ delay: 0.2 + (i * 0.15), duration: 1, ease: "easeOut" }}
                                            style={{ height: '100%', backgroundColor: item.color, borderRadius: '2px' }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
};

export default EstimatorSection;
