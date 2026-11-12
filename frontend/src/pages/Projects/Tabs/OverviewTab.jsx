import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  CheckCircle2,
  Clock,
  ArrowRight,
  Palette,
  Layers,
  Box,
  Calculator,
  Building2,
  ExternalLink,
  ShieldCheck,
  Eye,
  RefreshCw,
  FileText,
  Check,
  Compass,
  MapPin,
  Calendar,
  DollarSign
} from 'lucide-react';
import { exteriorDesignService } from '../../../services/exteriorDesignService';
import { EXTERIOR_DESIGNS } from '../../../data/exteriorCatalog';
import { aiService } from '../../../services/aiService';
import { interiorDesignService } from '../../../services/interiorDesignService';
import { costEstimationService } from '../../../services/costEstimationService';
import '../../../styles/pages/project-overview.css';

const formatLabel = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
};

const formatCurrency = (val) => {
  if (!val && val !== 0) return '₹0';
  const num = Math.round(Number(val));
  return `₹${num.toLocaleString('en-IN')}`;
};

const OverviewTab = ({ project, planner, setActiveTab, navigate }) => {
  const [loading, setLoading] = useState(true);
  const [exteriorData, setExteriorData] = useState(null);
  const [floorPlansCount, setFloorPlansCount] = useState(0);
  const [interiorRoomsCount, setInteriorRoomsCount] = useState(0);
  const [costEstimate, setCostEstimate] = useState(null);

  const loadData = useCallback(async () => {
    if (!project?.id) return;
    setLoading(true);

    try {
      // 1. Fetch Exterior Selection
      const extRes = await exteriorDesignService.getProjectSelection(project.id);
      if (extRes && extRes.selection && extRes.selection.design_id) {
        setExteriorData(extRes);
      } else {
        // Fallback check in localStorage directly if backend returned empty
        const cached = localStorage.getItem(`exterior_selection_${project.id}`);
        if (cached) {
          try {
            const parsed = JSON.parse(cached);
            if (parsed?.selection?.design_id) {
              setExteriorData(parsed);
            }
          } catch (_) {}
        }
      }

      // 2. Fetch Floor Plans Count
      try {
        const plans = await aiService.getFloorPlans(project.id);
        if (Array.isArray(plans)) {
          setFloorPlansCount(plans.length);
        }
      } catch (err) {
        if (project.floor_plans && Array.isArray(project.floor_plans)) {
          setFloorPlansCount(project.floor_plans.length);
        }
      }

      // 3. Fetch Interior Selections Count
      try {
        const intRes = await interiorDesignService.getProjectSelections(project.id);
        if (intRes?.selections) {
          setInteriorRoomsCount(Object.keys(intRes.selections).length);
        }
      } catch (_) {}

      // 4. Fetch Cost Estimate
      try {
        const estRes = await costEstimationService.getLatestEstimate(project.id);
        if (estRes && (estRes.total_cost || estRes.id)) {
          setCostEstimate(estRes);
        }
      } catch (_) {}
    } catch (e) {
      console.warn('[OverviewTab] Error loading project modules state:', e);
    } finally {
      setLoading(false);
    }
  }, [project?.id, project?.floor_plans]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Find matching catalog design for rich details & reference photo
  const selectedDesignId = exteriorData?.selection?.design_id;
  const catalogDesign = selectedDesignId
    ? EXTERIOR_DESIGNS.find((d) => d.id === selectedDesignId)
    : null;

  const designName =
    exteriorData?.selection?.design_name ||
    catalogDesign?.name ||
    'Custom Exterior Elevation';

  const designStyle =
    catalogDesign?.style ||
    exteriorData?.selection?.style ||
    formatLabel(exteriorData?.selection?.category) ||
    'Modern Contemporary';

  const imagePath =
    catalogDesign?.image_path ||
    (selectedDesignId ? `/images/exteriors/${selectedDesignId}.jpg` : '/images/exteriors/ext_mod_02.jpg');

  const colors = exteriorData?.selection?.colors || {};
  const materials = exteriorData?.selection?.materials || {};
  const totalExtCost =
    exteriorData?.total_exterior_cost ||
    catalogDesign?.pricing?.base_elevation_cost ||
    0;

  const hasExterior = Boolean(selectedDesignId);
  const hasFloorPlan = floorPlansCount > 0;
  const hasInterior = interiorRoomsCount > 0;
  const hasEstimate = Boolean(costEstimate);

  const formattedDate = project.created_at
    ? new Date(project.created_at).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    : 'Recently';

  const updatedExteriorTime = exteriorData?.updated_at
    ? new Date(exteriorData.updated_at).toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short'
      })
    : null;

  return (
    <div className="overview-page-wrapper">
      {/* ── TOP MILESTONE BANNER ────────────────────────────────────────── */}
      <div className="overview-status-banner">
        <div className="overview-banner-content">
          <div className="overview-banner-icon">
            {hasExterior ? <Building2 size={24} /> : <Sparkles size={24} />}
          </div>
          <div>
            <h3 className="overview-banner-title">
              {hasExterior
                ? 'Architectural Elevation Configured & Synchronized'
                : hasFloorPlan
                ? 'Floor Plans Generated — Select Exterior Elevation'
                : 'Project Initialized — Ready for Generation'}
            </h3>
            <p className="overview-banner-desc">
              {hasExterior
                ? `Saved elevation "${designName}" (${designStyle}) with personalized color palette and materials. Ready for full 3D review and cost consolidation.`
                : hasFloorPlan
                ? 'Your architectural floor plan is configured. Proceed to Exterior Studio to choose from 32 curated designs and preview in 3D.'
                : 'Your structural dimensions and design preferences are set. Generate your initial architectural floor plan or open the design studios.'}
            </p>
          </div>
        </div>

        <div className="overview-banner-actions">
          {hasExterior ? (
            <>
              <button
                className="btn btn-primary"
                onClick={() =>
                  navigate
                    ? navigate(`/projects/${project.id}/exterior`)
                    : (window.location.href = `/projects/${project.id}/exterior`)
                }
              >
                <Palette size={16} style={{ marginRight: '6px' }} />
                Open Exterior Studio
              </button>
              <button
                className="btn btn-outline"
                onClick={() => setActiveTab && setActiveTab('3d')}
              >
                <Eye size={16} style={{ marginRight: '6px' }} />
                View 3D House
              </button>
            </>
          ) : (
            <>
              <button
                className="btn btn-primary"
                onClick={() => setActiveTab && setActiveTab('floorplans')}
              >
                <Sparkles size={16} style={{ marginRight: '6px' }} />
                {hasFloorPlan ? 'View Floor Plans' : 'Generate Floor Plan'}
              </button>
              <button
                className="btn btn-outline"
                onClick={() =>
                  navigate
                    ? navigate(`/projects/${project.id}/exterior`)
                    : (window.location.href = `/projects/${project.id}/exterior`)
                }
              >
                <Palette size={16} style={{ marginRight: '6px' }} />
                Choose Exterior Design
              </button>
            </>
          )}
        </div>
      </div>

      {/* ── TWO-COLUMN ROW: PROJECT DETAILS & MODULE STATUS ───────────── */}
      <div className="overview-two-col-grid">
        {/* Project Details Card */}
        <div className="overview-card" id="overview-project-details-card">
          <div className="overview-card-header">
            <h3 className="overview-card-title">
              <Building2 size={18} color="#38bdf8" /> Project Details
            </h3>
            <span className="pill-badge pill-badge-ready">
              {project.status || 'Active Design'}
            </span>
          </div>

          <div className="overview-card-body">
            <div className="detail-item-row">
              <span className="detail-label">Location / City</span>
              <span className="detail-value">{project.location || 'Bengaluru, KA'}</span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Plot Dimensions</span>
              <span className="detail-value">
                {project.plot_width && project.plot_length
                  ? `${project.plot_width} ft (W) × ${project.plot_length} ft (L)`
                  : '30 ft × 40 ft'}
              </span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Total Plot Area</span>
              <span className="detail-value">
                {project.plot_width && project.plot_length
                  ? `${(project.plot_width * project.plot_length).toLocaleString('en-IN')} sq ft`
                  : '1,200 sq ft'}
              </span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Vastu / Plot Facing</span>
              <span className="detail-value">{project.facing ? `${project.facing} Facing` : 'East Facing'}</span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Floor Configuration</span>
              <span className="detail-value">
                G + {(project.floors || 1) - 1} Floor{project.floors > 2 ? 's' : ''} ({project.floors || 1} Levels)
              </span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Target Budget</span>
              <span className="detail-value" style={{ color: '#10b981' }}>
                {project.budget
                  ? `₹${Number(project.budget).toLocaleString('en-IN')}`
                  : '₹55,00,000'}
              </span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Design Style</span>
              <span className="detail-value">{project.design_style || 'Modern Contemporary'}</span>
            </div>
            <div className="detail-item-row">
              <span className="detail-label">Created Date</span>
              <span className="detail-value">{formattedDate}</span>
            </div>
          </div>

          <div className="overview-card-footer">
            <button
              className="btn btn-ghost btn-sm"
              onClick={() =>
                navigate
                  ? navigate(`/projects/${project.id}/planner`)
                  : (window.location.href = `/projects/${project.id}/planner`)
              }
            >
              Edit Requirements & Plot Data →
            </button>
          </div>
        </div>

        {/* Module Status Card */}
        <div className="overview-card" id="overview-module-status-card">
          <div className="overview-card-header">
            <h3 className="overview-card-title">
              <Layers size={18} color="#38bdf8" /> Module Status
            </h3>
            <span className="pill-badge pill-badge-ready">
              {hasExterior && hasFloorPlan ? '4 / 6 Ready' : '3 / 6 Ready'}
            </span>
          </div>

          <div className="overview-card-body">
            <div className="module-status-list">
              {/* 1. Structural Planner */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.12)', color: '#10b981' }}>
                    <FileText size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">1. Structural Planner</span>
                    <span className="module-desc-sub">
                      {project.plot_width && project.plot_length
                        ? `${project.plot_width}×${project.plot_length} ft • ${project.facing || 'East'} • G+${(project.floors || 1) - 1}`
                        : 'Inputs configured'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className="pill-badge pill-badge-saved">Saved</span>
                  <button
                    className="module-action-link-btn"
                    onClick={() =>
                      navigate
                        ? navigate(`/projects/${project.id}/planner`)
                        : (window.location.href = `/projects/${project.id}/planner`)
                    }
                  >
                    Edit
                  </button>
                </div>
              </div>

              {/* 2. Floor Plans */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8' }}>
                    <Layers size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">2. Floor Plans</span>
                    <span className="module-desc-sub">
                      {hasFloorPlan
                        ? `${floorPlansCount} layout version${floorPlansCount > 1 ? 's' : ''} available`
                        : 'Architectural blueprint generator'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className={`pill-badge ${hasFloorPlan ? 'pill-badge-saved' : 'pill-badge-ready'}`}>
                    {hasFloorPlan ? 'Generated' : 'Ready'}
                  </span>
                  <button
                    className="module-action-link-btn"
                    onClick={() => setActiveTab && setActiveTab('floorplans')}
                  >
                    {hasFloorPlan ? 'View' : 'Generate'}
                  </button>
                </div>
              </div>

              {/* 3. Interior Studio */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(168, 85, 247, 0.12)', color: '#a855f7' }}>
                    <Palette size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">3. Interior Studio</span>
                    <span className="module-desc-sub">
                      {hasInterior
                        ? `${interiorRoomsCount} room${interiorRoomsCount > 1 ? 's' : ''} customized`
                        : '32 curated room palettes'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className={`pill-badge ${hasInterior ? 'pill-badge-saved' : 'pill-badge-ready'}`}>
                    {hasInterior ? 'Configured' : 'Ready'}
                  </span>
                  <button
                    className="module-action-link-btn"
                    onClick={() =>
                      navigate
                        ? navigate(`/projects/${project.id}/interior`)
                        : (window.location.href = `/projects/${project.id}/interior`)
                    }
                  >
                    Open
                  </button>
                </div>
              </div>

              {/* 4. Exterior Studio */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b' }}>
                    <Building2 size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">4. Exterior Studio</span>
                    <span className="module-desc-sub">
                      {hasExterior
                        ? `${designName} • ${designStyle}`
                        : '32 designs with real-time 3D sync'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className={`pill-badge ${hasExterior ? 'pill-badge-saved' : 'pill-badge-ready'}`}>
                    {hasExterior ? 'Saved' : 'Ready'}
                  </span>
                  <button
                    className="module-action-link-btn"
                    onClick={() =>
                      navigate
                        ? navigate(`/projects/${project.id}/exterior`)
                        : (window.location.href = `/projects/${project.id}/exterior`)
                    }
                  >
                    Open
                  </button>
                </div>
              </div>

              {/* 5. 3D View */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(34, 197, 94, 0.12)', color: '#22c55e' }}>
                    <Box size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">5. 3D Visualization</span>
                    <span className="module-desc-sub">
                      {hasExterior
                        ? 'Synchronized with customized materials'
                        : 'WebGL OrbitControls & Daylight cycle'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className="pill-badge pill-badge-ready">Ready</span>
                  <button
                    className="module-action-link-btn"
                    onClick={() => setActiveTab && setActiveTab('3d')}
                  >
                    Launch
                  </button>
                </div>
              </div>

              {/* 6. Cost Estimate */}
              <div className="module-status-item">
                <div className="module-meta-group">
                  <div className="module-icon-wrap" style={{ background: 'rgba(236, 72, 153, 0.12)', color: '#ec4899' }}>
                    <Calculator size={16} />
                  </div>
                  <div className="module-text-info">
                    <span className="module-name-title">6. Cost Estimate</span>
                    <span className="module-desc-sub">
                      {hasEstimate
                        ? `Latest: ${formatCurrency(costEstimate.total_cost)}`
                        : 'Material, labor & finishes BOQ'}
                    </span>
                  </div>
                </div>
                <div className="module-badge-action-group">
                  <span className={`pill-badge ${hasEstimate ? 'pill-badge-saved' : 'pill-badge-ready'}`}>
                    {hasEstimate ? 'Calculated' : 'Ready'}
                  </span>
                  <button
                    className="module-action-link-btn"
                    onClick={() => setActiveTab && setActiveTab('estimate')}
                  >
                    Calculate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── SAVED EXTERIOR ARCHITECTURE SHOWCASE CARD ──────────────────── */}
      {hasExterior ? (
        <div className="saved-exterior-showcase-card" id="saved-exterior-showcase">
          <div className="overview-card-header">
            <h3 className="overview-card-title">
              <Building2 size={20} color="#f59e0b" /> Saved Exterior Architecture & Elevation
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span className="pill-badge pill-badge-saved">
                <Check size={12} /> Saved Selection
              </span>
              <button
                className="btn btn-outline btn-sm"
                onClick={() =>
                  navigate
                    ? navigate(`/projects/${project.id}/exterior`)
                    : (window.location.href = `/projects/${project.id}/exterior`)
                }
              >
                <Palette size={14} style={{ marginRight: '6px' }} />
                Open in Exterior Studio
              </button>
            </div>
          </div>

          <div className="saved-exterior-content-layout">
            {/* Left Photo & 3D Hint */}
            <div className="saved-exterior-photo-col">
              <div className="saved-exterior-img-wrap">
                <img
                  src={imagePath}
                  alt={designName}
                  className="saved-exterior-img"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/images/exteriors/ext_mod_02.jpg';
                  }}
                />
                <div className="saved-exterior-badge-overlay">
                  ARCHITECTURAL REFERENCE
                </div>
              </div>
              <div className="saved-exterior-3d-hint">
                <Eye size={16} color="#38bdf8" style={{ flexShrink: 0 }} />
                <span>
                  Interactive 3D model applies these colors to walls, trims, doors, and glazing in real time.
                </span>
              </div>
            </div>

            {/* Right Details, Swatches & Specifications */}
            <div className="saved-exterior-details-col">
              <div className="saved-exterior-title-group">
                <h4 className="saved-exterior-name">{designName}</h4>
                <div className="saved-exterior-meta-line">
                  <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{designStyle}</span>
                  <span style={{ opacity: 0.4 }}>•</span>
                  <span>ID: <code style={{ color: '#38bdf8' }}>{selectedDesignId}</code></span>
                  {updatedExteriorTime && (
                    <>
                      <span style={{ opacity: 0.4 }}>•</span>
                      <span>Last saved: {updatedExteriorTime}</span>
                    </>
                  )}
                </div>
              </div>

              {/* Color Swatches Grid */}
              <div>
                <span
                  style={{
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: '#94a3b8',
                    display: 'block',
                    marginBottom: '8px'
                  }}
                >
                  Applied Color Scheme
                </span>
                <div className="color-swatches-grid">
                  <div className="color-swatch-chip">
                    <div
                      className="swatch-color-box"
                      style={{ backgroundColor: colors.primary_wall || '#F5F2EA' }}
                    />
                    <div className="swatch-label-wrap">
                      <span className="swatch-name">Primary Wall</span>
                      <span className="swatch-hex">{colors.primary_wall || '#F5F2EA'}</span>
                    </div>
                  </div>

                  <div className="color-swatch-chip">
                    <div
                      className="swatch-color-box"
                      style={{ backgroundColor: colors.accent_wall || '#343A40' }}
                    />
                    <div className="swatch-label-wrap">
                      <span className="swatch-name">Accent Wall</span>
                      <span className="swatch-hex">{colors.accent_wall || '#343A40'}</span>
                    </div>
                  </div>

                  <div className="color-swatch-chip">
                    <div
                      className="swatch-color-box"
                      style={{ backgroundColor: colors.door || '#60452F' }}
                    />
                    <div className="swatch-label-wrap">
                      <span className="swatch-name">Main Door</span>
                      <span className="swatch-hex">{colors.door || '#60452F'}</span>
                    </div>
                  </div>

                  <div className="color-swatch-chip">
                    <div
                      className="swatch-color-box"
                      style={{ backgroundColor: colors.window_frame || '#20252B' }}
                    />
                    <div className="swatch-label-wrap">
                      <span className="swatch-name">Window Frames</span>
                      <span className="swatch-hex">{colors.window_frame || '#20252B'}</span>
                    </div>
                  </div>

                  <div className="color-swatch-chip">
                    <div
                      className="swatch-color-box"
                      style={{ backgroundColor: colors.window_glass_tint || '#7DD3FC' }}
                    />
                    <div className="swatch-label-wrap">
                      <span className="swatch-name">Glass Tint</span>
                      <span className="swatch-hex">{colors.window_glass_tint || '#7DD3FC'}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Material Specifications */}
              <div>
                <span
                  style={{
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: '#94a3b8',
                    display: 'block',
                    marginBottom: '8px'
                  }}
                >
                  Architectural Materials & Texture
                </span>
                <div className="specs-tag-row">
                  <span className="spec-tag">
                    <ShieldCheck size={14} color="#38bdf8" />
                    Finish: {formatLabel(materials.finish_type || 'smooth_stucco')}
                  </span>
                  <span className="spec-tag">
                    <Layers size={14} color="#f59e0b" />
                    Cladding: {formatLabel(materials.cladding_type || 'natural_teak_soffit')}
                  </span>
                  <span className="spec-tag">
                    <Building2 size={14} color="#10b981" />
                    Door: {formatLabel(materials.door_material || 'pivot_teak')}
                  </span>
                </div>
              </div>

              {/* Cost & Guarantee Bar */}
              <div className="saved-exterior-cost-bar">
                <div>
                  <span style={{ fontSize: '0.74rem', color: '#94a3b8', display: 'block' }}>
                    Incremental Exterior Elevation Cost
                  </span>
                  <span className="cost-amount-tag">
                    {formatCurrency(totalExtCost)}
                  </span>
                </div>
                <div className="cost-guarantee-text">
                  Includes multi-coat exterior emulsion, weather-resistant louvers, architectural door fittings, and premium double-glazed glazing.
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Empty State Card if no exterior is chosen */
        <div className="empty-state-showcase-card">
          <div className="empty-state-icon-circle">
            <Building2 size={28} />
          </div>
          <div>
            <h4 style={{ margin: '0 0 6px 0', fontSize: '1.2rem', color: '#f8fafc' }}>
              No Exterior Elevation Selected Yet
            </h4>
            <p style={{ margin: 0, fontSize: '0.88rem', color: '#94a3b8', maxWidth: '520px' }}>
              Choose from 32 curated architectural designs across 8 categories, customize wall paints and materials, and synchronize your selection directly with the interactive 3D house.
            </p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() =>
              navigate
                ? navigate(`/projects/${project.id}/exterior`)
                : (window.location.href = `/projects/${project.id}/exterior`)
            }
          >
            <Palette size={16} style={{ marginRight: '6px' }} />
            Browse Exterior Designs & Customize →
          </button>
        </div>
      )}
    </div>
  );
};

export default OverviewTab;
