import React from 'react';
import { Calculator, ArrowRight, Sun, Layers, CheckCircle } from 'lucide-react';
import Unified3DViewer from '../../../components/viewer3d/Unified3DViewer';

/**
 * ThreeDTab — Phase 6H & 6L
 *
 * Dedicated Project-Level Interactive 3D Visualization Tab.
 * Unifies:
 * - Approved canonical/project floor-plan geometry (walls, slabs, doors, windows, stairs, rooms)
 * - Saved exterior design, 12-component colors, and facade materials
 * - Saved interior design selections per room (flooring, wall finishes, furniture, lighting)
 * - Multi-level dollhouse floor isolation (All, Ground Floor, First Floor)
 * - Camera room navigation & real-time Room Inspector HUD
 */
const ThreeDTab = ({ project, setActiveTab, navigate }) => {
  if (!project?.id) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>
        No active project configuration found. Please select a valid project.
      </div>
    );
  }

  const handleProceedToEstimate = () => {
    if (setActiveTab) {
      setActiveTab('estimate');
    } else if (navigate) {
      navigate(`/projects/${project.id}?tab=estimate`);
    }
  };

  const handleBackToExterior = () => {
    if (navigate) {
      navigate(`/projects/${project.id}/exterior`);
    }
  };

  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Unified3DViewer project={project} />

      {/* Guided Bottom Workflow Navigation Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 20px',
        background: 'rgba(15, 23, 42, 0.95)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: 'rgba(56, 189, 248, 0.1)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#38bdf8'
          }}>
            <CheckCircle size={18} color="#10b981" />
          </div>
          <div>
            <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span>Step 5 of 6: 3D House Visualization</span>
              <span style={{ fontSize: '0.72rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>Verified</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.78rem', color: '#94a3b8' }}>
              Floor-plan geometry, exterior facade, and interior rooms are unified. Ready for construction budgeting.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            className="btn btn-outline btn-sm"
            style={{ fontSize: '0.8rem', padding: '0.5rem 0.9rem', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
            onClick={handleBackToExterior}
          >
            <Sun size={14} />
            <span>Modify Exterior</span>
          </button>

          <button
            className="btn btn-primary btn-sm"
            style={{
              fontSize: '0.85rem',
              padding: '0.55rem 1.25rem',
              fontWeight: 700,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
              border: '1px solid rgba(56, 189, 248, 0.4)',
              boxShadow: '0 4px 14px rgba(37, 99, 235, 0.35)'
            }}
            onClick={handleProceedToEstimate}
          >
            <Calculator size={15} />
            <span>Proceed to Cost Estimate</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ThreeDTab;
