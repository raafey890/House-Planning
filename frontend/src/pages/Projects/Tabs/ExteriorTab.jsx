import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sun, Sparkles, SlidersHorizontal, ArrowRight, ShieldCheck } from 'lucide-react';

const ExteriorTab = ({ project, navigate: propNavigate }) => {
  const localNavigate = useNavigate();
  const navigate = propNavigate || localNavigate;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', height: '100%', overflowY: 'auto', paddingBottom: 'var(--space-8)' }}>
      <div className="card" style={{ padding: '2.5rem', textAlign: 'center', background: 'linear-gradient(135deg, #111827 0%, #0f172a 100%)', border: '1px solid #1f2937', borderRadius: '12px' }}>
        <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem auto' }}>
          <Sun size={32} />
        </div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 0.75rem 0' }}>
          Dedicated Exterior Design Studio
        </h2>
        <p style={{ fontSize: '0.95rem', color: '#94a3b8', maxWidth: '580px', margin: '0 auto 1.75rem auto', lineHeight: '1.6' }}>
          Explore 32 distinct architectural elevations across 8 styles (Modern Contemporary, Minimalist, Luxury Villa, Traditional Indian, Indian Modern, Mediterranean, Tropical Contemporary, and Premium Duplex) evaluated in real-time against your project's frontage and floor configuration.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <button
            className="btn btn-primary"
            onClick={() => navigate(`/projects/${project.id}/exterior`)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.75rem', fontSize: '1rem', fontWeight: 600 }}
          >
            <SlidersHorizontal size={18} /> Open Exterior Design Studio <ArrowRight size={16} />
          </button>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '1.5rem', marginTop: '2rem', fontSize: '0.8rem', color: '#64748b' }}>
          <span>✓ 32 Architectural Designs</span>
          <span>•</span>
          <span>✓ Plan-Aware Compatibility</span>
          <span>•</span>
          <span>✓ Zero Civil Double-Counting</span>
        </div>
      </div>
    </div>
  );
};

export default ExteriorTab;
