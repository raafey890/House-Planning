import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    Calculator,
    FileSpreadsheet,
    Printer,
    Edit3,
    RefreshCw,
    AlertCircle,
    CheckCircle2,
    Info,
    X,
    Building2,
    Hammer,
    Layers,
    DollarSign,
    Sparkles,
    Compass
} from 'lucide-react';
import { costEstimationService } from '../../../services/costEstimationService';
import { interiorDesignService } from '../../../services/interiorDesignService';
import { exteriorDesignService } from '../../../services/exteriorDesignService';
import '../../../styles/pages/cost-estimate.css';

const CATEGORY_NAMES = {
    all: 'All Items',
    materials: 'Materials',
    structural_steel: 'Structural Steel',
    masonry: 'Masonry',
    flooring: 'Flooring',
    finishes: 'Plaster & Finishes',
    openings: 'Doors & Windows',
    services: 'Plumbing & Electrical',
    labor: 'Labor Workmanship'
};

const EstimateTab = ({ project, setActiveTab }) => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [recalculating, setRecalculating] = useState(false);
    const [error, setError] = useState(null);
    const [estimate, setEstimate] = useState(null);
    const [interiorData, setInteriorData] = useState(null);
    const [exteriorData, setExteriorData] = useState(null);
    const [activeCategory, setActiveCategory] = useState('all');

    // Rates editing modal state
    const [isRatesModalOpen, setIsRatesModalOpen] = useState(false);
    const [editableRates, setEditableRates] = useState({});

    // Load initial estimate on mount
    useEffect(() => {
        loadEstimate();
    }, [project.id]);

    const loadEstimate = async () => {
        setLoading(true);
        setError(null);
        try {
            const [costData, intData, extData] = await Promise.all([
                costEstimationService.getLatestEstimate(project.id),
                interiorDesignService.getProjectSelections(project.id).catch(() => null),
                exteriorDesignService.getProjectSelection(project.id).catch(() => null)
            ]);
            setEstimate(costData);
            setInteriorData(intData);
            setExteriorData(extData);
            initializeEditableRates(costData.rates_snapshot);
        } catch (err) {
            console.error('Failed to load estimate:', err);
            setError(err.message || 'Could not load cost estimate.');
        } finally {
            setLoading(false);
        }
    };

    const initializeEditableRates = (ratesSnapshot) => {
        if (!ratesSnapshot) return;
        const initial = {};
        Object.entries(ratesSnapshot).forEach(([key, item]) => {
            initial[key] = item.unit_rate;
        });
        setEditableRates(initial);
    };

    const handleRateChange = (key, value) => {
        const numVal = parseFloat(value);
        setEditableRates(prev => ({
            ...prev,
            [key]: isNaN(numVal) ? '' : numVal
        }));
    };

    const handleRecalculate = async () => {
        if (!estimate) return;
        setRecalculating(true);
        setError(null);
        try {
            // Filter only valid positive numbers
            const validatedRates = {};
            Object.entries(editableRates).forEach(([k, v]) => {
                if (typeof v === 'number' && v >= 0) {
                    validatedRates[k] = v;
                }
            });

            const updated = await costEstimationService.recalculateEstimate(
                project.id,
                estimate.estimate_id,
                validatedRates,
                null,
                estimate.floor_plan_id
            );
            setEstimate(updated);
            initializeEditableRates(updated.rates_snapshot);
            setIsRatesModalOpen(false);
        } catch (err) {
            console.error('Recalculation error:', err);
            setError(err.message || 'Failed to recalculate estimate.');
        } finally {
            setRecalculating(false);
        }
    };

    const handleResetRates = async () => {
        try {
            const benchmark = await costEstimationService.getBenchmarkRates(project.id);
            initializeEditableRates(benchmark.rates);
        } catch (err) {
            console.error('Failed to reset rates:', err);
        }
    };

    const handleExportCsv = async () => {
        try {
            await costEstimationService.downloadCsv(project.id);
        } catch (err) {
            alert('Failed to export CSV: ' + err.message);
        }
    };

    const handlePrint = () => {
        window.print();
    };

    // ── LOADING STATE ──────────────────────────────────────────────────────────
    if (loading) {
        return (
            <div className="card card-body text-center" style={{ padding: '5rem 2rem', margin: 'auto', maxWidth: '600px' }}>
                <Calculator size={48} className="animate-pulse" style={{ margin: '0 auto 1.5rem', color: '#10b981' }} />
                <h3 className="text-h3">Calculating Construction Estimate</h3>
                <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
                    Extracting room perimeters, wall deductions, and structural concrete quantities from your validated floor plan...
                </p>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center', color: '#94a3b8', fontSize: '0.9rem' }}>
                    <RefreshCw size={16} className="animate-spin" /> Hyderabad Benchmark Pricing Engine (INR ₹)
                </div>
            </div>
        );
    }

    // ── EMPTY / ERROR STATE ───────────────────────────────────────────────────
    if (error && !estimate) {
        return (
            <div className="card card-body text-center" style={{ padding: '4rem 2rem', margin: 'auto', maxWidth: '600px' }}>
                <AlertCircle size={48} color="#ef4444" style={{ margin: '0 auto 1rem' }} />
                <h3 className="text-h3">Estimate Not Available</h3>
                <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
                    {error}
                </p>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                    <button className="btn btn-primary" onClick={loadEstimate}>
                        <RefreshCw size={16} style={{ marginRight: '6px' }} /> Retry Estimation
                    </button>
                </div>
            </div>
        );
    }

    if (!estimate) return null;

    const { cost_summary, area_schedule, line_items, rates_snapshot, assumptions_and_limitations, disclaimer } = estimate;

    // Filter line items based on category
    const filteredItems = activeCategory === 'all'
        ? line_items
        : line_items.filter(item => item.category === activeCategory);

    // Group rates by category for the modal
    const ratesByCategory = {};
    if (rates_snapshot) {
        Object.entries(rates_snapshot).forEach(([key, item]) => {
            const cat = item.category || 'general';
            if (!ratesByCategory[cat]) ratesByCategory[cat] = [];
            ratesByCategory[cat].push({ key, ...item });
        });
    }

    return (
        <div className="cost-estimate-container">
            {/* Header & Controls */}
            <div className="estimate-header">
                <div className="estimate-title-group">
                    <h2>Construction Cost Estimate</h2>
                    <div className="estimate-meta-tags">
                        <span className="meta-badge location">📍 {estimate.location_profile}</span>
                        <span className="meta-badge benchmark">Currency: {estimate.currency} ({estimate.currency_symbol})</span>
                        <span className="meta-badge benchmark">✓ Geometry-Derived Engine</span>
                    </div>
                </div>

                <div className="estimate-actions">
                    <button className="btn btn-outline btn-sm" onClick={() => setIsRatesModalOpen(true)}>
                        <Edit3 size={15} style={{ marginRight: '6px' }} /> Edit Unit Rates
                    </button>
                    <button className="btn btn-outline btn-sm" onClick={handleExportCsv} title="Download CSV Breakdown">
                        <FileSpreadsheet size={15} style={{ marginRight: '6px' }} /> Export CSV
                    </button>
                    <button className="btn btn-outline btn-sm" onClick={handlePrint} title="Print or Save PDF">
                        <Printer size={15} style={{ marginRight: '6px' }} /> Print / PDF
                    </button>
                    <button className="btn btn-outline btn-sm" onClick={loadEstimate} title="Refresh Estimate">
                        <RefreshCw size={15} />
                    </button>
                </div>
            </div>

            {/* Error banner if recalculation failed */}
            {error && (
                <div style={{ padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid #ef4444', borderRadius: '8px', color: '#fca5a5', fontSize: '0.875rem' }}>
                    <AlertCircle size={16} style={{ display: 'inline', marginRight: '6px' }} />
                    {error}
                </div>
            )}

            {/* Top Summary Metrics Cards */}
            <div className="estimate-summary-grid">
                {/* Hero Total Card */}
                <div className="estimate-metric-card hero">
                    <div>
                        <div className="metric-label">
                            <span>TOTAL ESTIMATED PROJECT COST</span>
                            <Sparkles size={18} color="#10b981" />
                        </div>
                        <div className="metric-value-huge">
                            ₹ {cost_summary.grand_total.toLocaleString('en-IN')}
                        </div>
                        <div className="metric-subtext">
                            Estimated cost per sq ft: <strong>₹ {cost_summary.cost_per_sq_ft.toLocaleString('en-IN')} / sq ft</strong>
                        </div>
                        <div className="metric-subtext" style={{ fontSize: '0.75rem' }}>
                            Based on {cost_summary.cost_per_sq_ft_denominator}
                        </div>

                        {(interiorData?.total_interior_cost > 0 || (exteriorData?.selection?.additional_cost || exteriorData?.total_exterior_cost || 0) > 0) && (
                            <div style={{ marginTop: '0.65rem', paddingTop: '0.6rem', borderTop: '1px solid rgba(255,255,255,0.15)', fontSize: '0.85rem' }}>
                                <span style={{ color: '#94a3b8' }}>Turnkey Total (Civil + Upgrades): </span>
                                <strong style={{ color: '#38bdf8', fontSize: '1.05rem' }}>
                                    ₹ {(cost_summary.grand_total + (interiorData?.total_interior_cost || 0) + (exteriorData?.selection?.additional_cost || exteriorData?.total_exterior_cost || 0)).toLocaleString('en-IN')}
                                </strong>
                                <div style={{ fontSize: '0.74rem', color: '#94a3b8', marginTop: '2px' }}>
                                    Civil: ₹ {cost_summary.grand_total.toLocaleString('en-IN')}
                                    {interiorData?.total_interior_cost > 0 && ` • Interiors: ₹ ${interiorData.total_interior_cost.toLocaleString('en-IN')}`}
                                    {(exteriorData?.selection?.additional_cost || exteriorData?.total_exterior_cost || 0) > 0 && ` • Exterior: ₹ ${(exteriorData?.selection?.additional_cost || exteriorData?.total_exterior_cost || 0).toLocaleString('en-IN')}`}
                                </div>
                            </div>
                        )}
                    </div>

                    {project.budget && (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 12px',
                            borderRadius: '6px',
                            marginTop: '0.75rem',
                            background: cost_summary.grand_total <= project.budget ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                            color: cost_summary.grand_total <= project.budget ? '#34d399' : '#f87171',
                            fontSize: '0.85rem',
                            fontWeight: 600
                        }}>
                            <CheckCircle2 size={16} />
                            {cost_summary.grand_total <= project.budget
                                ? `Within your target budget (₹ ${project.budget.toLocaleString('en-IN')})`
                                : `Exceeds target budget by ₹ ${(cost_summary.grand_total - project.budget).toLocaleString('en-IN')}`
                            }
                        </div>
                    )}
                </div>

                {/* Materials Total */}
                <div className="estimate-metric-card">
                    <div className="metric-label">
                        <span>RAW MATERIALS</span>
                        <Building2 size={16} color="#60a5fa" />
                    </div>
                    <div className="metric-value-large" style={{ color: '#60a5fa' }}>
                        ₹ {cost_summary.materials_cost.toLocaleString('en-IN')}
                    </div>
                    <div className="metric-subtext">
                        Cement, Steel, Bricks, Sand, Aggregates & Flooring Tiles
                    </div>
                </div>

                {/* Labor Total */}
                <div className="estimate-metric-card">
                    <div className="metric-label">
                        <span>CIVIL & FINISHING LABOR</span>
                        <Hammer size={16} color="#f59e0b" />
                    </div>
                    <div className="metric-value-large" style={{ color: '#f59e0b' }}>
                        ₹ {cost_summary.labor_cost.toLocaleString('en-IN')}
                    </div>
                    <div className="metric-subtext">
                        Masonry, Shuttering, Bar Bending, Tiling & Painting
                    </div>
                </div>

                {/* Openings & Fixtures */}
                <div className="estimate-metric-card">
                    <div className="metric-label">
                        <span>OPENINGS & FIXTURES</span>
                        <Layers size={16} color="#a855f7" />
                    </div>
                    <div className="metric-value-large" style={{ color: '#a855f7' }}>
                        ₹ {cost_summary.openings_and_fixtures_cost.toLocaleString('en-IN')}
                    </div>
                    <div className="metric-subtext">
                        Main Teak Door, Flush Doors, UPVC Windows & SS Railing
                    </div>
                </div>

                {/* Services & Overhead */}
                <div className="estimate-metric-card">
                    <div className="metric-label">
                        <span>SERVICES & CONTINGENCY</span>
                        <DollarSign size={16} color="#38bdf8" />
                    </div>
                    <div className="metric-value-large" style={{ color: '#38bdf8' }}>
                        ₹ {(cost_summary.services_cost + cost_summary.contingency_cost + cost_summary.contractor_overhead_cost).toLocaleString('en-IN')}
                    </div>
                    <div className="metric-subtext">
                        Plumbing, Electrical, 5% Contingency & 10% Contractor Overhead
                    </div>
                </div>

                {/* Interior Upgrades Package (Phase 6E.1) */}
                <div className="estimate-metric-card" style={{
                    background: interiorData?.total_interior_cost > 0 
                        ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(30, 41, 59, 0.95))' 
                        : undefined,
                    borderColor: interiorData?.total_interior_cost > 0 ? 'rgba(56, 189, 248, 0.4)' : undefined
                }}>
                    <div className="metric-label">
                        <span>INTERIOR UPGRADES (PHASE 6E.1)</span>
                        <Sparkles size={16} color="#38bdf8" />
                    </div>
                    {interiorData?.total_interior_cost > 0 ? (
                        <>
                            <div className="metric-value-large" style={{ color: '#38bdf8' }}>
                                ₹ {interiorData.total_interior_cost.toLocaleString('en-IN')}
                            </div>
                            <div className="metric-subtext">
                                Configured for {Object.keys(interiorData.selections || {}).length} rooms in Interior Studio
                            </div>
                            <Link 
                                to={`/projects/${project.id}/interior`} 
                                style={{ marginTop: '8px', fontSize: '0.8rem', color: '#38bdf8', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            >
                                Edit Interior Finishes →
                            </Link>
                        </>
                    ) : (
                        <>
                            <div className="metric-value-large" style={{ color: '#94a3b8', fontSize: '1.1rem' }}>
                                ₹ 0 (Not Configured)
                            </div>
                            <div className="metric-subtext">
                                Baseline vitrified tiles & plaster are in civil cost.
                            </div>
                            <Link 
                                to={`/projects/${project.id}/interior`} 
                                style={{ marginTop: '8px', fontSize: '0.8rem', color: '#38bdf8', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                            >
                                Personalize 32 Interior Styles →
                            </Link>
                        </>
                    )}
                </div>

                {/* Exterior Upgrades Package (Phase 6G) */}
                {(() => {
                    const extAdditionalCost = exteriorData?.selection?.additional_cost || exteriorData?.total_exterior_cost || 0;
                    return (
                        <div className="estimate-metric-card" style={{
                            background: extAdditionalCost > 0 
                                ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(30, 41, 59, 0.95))' 
                                : undefined,
                            borderColor: extAdditionalCost > 0 ? 'rgba(16, 185, 129, 0.4)' : undefined
                        }}>
                            <div className="metric-label">
                                <span>EXTERIOR UPGRADES (PHASE 6G)</span>
                                <Building2 size={16} color="#10b981" />
                            </div>
                            {extAdditionalCost > 0 ? (
                                <>
                                    <div className="metric-value-large" style={{ color: '#10b981' }}>
                                        ₹ {extAdditionalCost.toLocaleString('en-IN')}
                                    </div>
                                    <div className="metric-subtext">
                                        {exteriorData?.selection?.design_name || 'Selected Architecture Package'}
                                    </div>
                                    <Link 
                                        to={`/projects/${project.id}/exterior`} 
                                        style={{ marginTop: '8px', fontSize: '0.8rem', color: '#10b981', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                                    >
                                        Edit Exterior Finishes →
                                    </Link>
                                </>
                            ) : (
                                <>
                                    <div className="metric-value-large" style={{ color: '#94a3b8', fontSize: '1.1rem' }}>
                                        ₹ 0 (Civil Baseline)
                                    </div>
                                    <div className="metric-subtext">
                                        Standard plaster & basic exterior paint included in civil.
                                    </div>
                                    <Link 
                                        to={`/projects/${project.id}/exterior`} 
                                        style={{ marginTop: '8px', fontSize: '0.8rem', color: '#10b981', textDecoration: 'none', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                                    >
                                        Personalize 32 Exterior Styles →
                                    </Link>
                                </>
                            )}
                        </div>
                    );
                })()}
            </div>

            {/* Area Schedule & Geometry Context Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                {/* Area Schedule Card */}
                <div className="area-schedule-card">
                    <h4>
                        <Building2 size={18} color="#10b981" />
                        Validated Geometry Area Schedule
                    </h4>
                    <div className="area-stats-row">
                        <span className="text-muted">Total Plot Area</span>
                        <strong>{area_schedule.plot_area} sq ft</strong>
                    </div>
                    <div className="area-stats-row">
                        <span className="text-muted">Ground Constructed Footprint</span>
                        <strong>{area_schedule.ground_constructed_footprint} sq ft</strong>
                    </div>
                    <div className="area-stats-row">
                        <span className="text-muted">Total Constructed Built-Up Area (BUA)</span>
                        <strong style={{ color: '#10b981' }}>{area_schedule.total_built_up_area} sq ft</strong>
                    </div>
                    <div className="area-stats-row">
                        <span className="text-muted">Net Indoor Usable Room Area</span>
                        <strong>{area_schedule.total_indoor_room_area} sq ft</strong>
                    </div>
                    <div className="area-stats-row">
                        <span className="text-muted">Structural Wall Footprint Area</span>
                        <strong>{area_schedule.wall_footprint_area} sq ft</strong>
                    </div>
                    {area_schedule.terrace_roof_areas && area_schedule.terrace_roof_areas.length > 0 && (
                        <div className="area-stats-row">
                            <span className="text-muted">Upper Terraces & Balconies</span>
                            <strong>
                                {area_schedule.terrace_roof_areas.reduce((acc, x) => acc + (x.area || 0), 0)} sq ft ({area_schedule.terrace_roof_areas.length} spaces)
                            </strong>
                        </div>
                    )}
                </div>

                {/* Cost Distribution Progress Bars */}
                <div className="breakdown-section">
                    <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: 600, color: '#f1f5f9' }}>
                        Cost Breakdown by Discipline
                    </h4>

                    {/* Progress bars */}
                    <div className="breakdown-bar-item">
                        <div className="breakdown-label-row">
                            <span style={{ color: '#60a5fa' }}>Materials</span>
                            <span>₹ {cost_summary.materials_cost.toLocaleString('en-IN')} ({Math.round(cost_summary.materials_cost / cost_summary.grand_total * 100)}%)</span>
                        </div>
                        <div className="breakdown-track">
                            <div className="breakdown-fill" style={{ width: `${(cost_summary.materials_cost / cost_summary.grand_total) * 100}%`, background: '#60a5fa' }}></div>
                        </div>
                    </div>

                    <div className="breakdown-bar-item">
                        <div className="breakdown-label-row">
                            <span style={{ color: '#f59e0b' }}>Civil & Finishing Labor</span>
                            <span>₹ {cost_summary.labor_cost.toLocaleString('en-IN')} ({Math.round(cost_summary.labor_cost / cost_summary.grand_total * 100)}%)</span>
                        </div>
                        <div className="breakdown-track">
                            <div className="breakdown-fill" style={{ width: `${(cost_summary.labor_cost / cost_summary.grand_total) * 100}%`, background: '#f59e0b' }}></div>
                        </div>
                    </div>

                    <div className="breakdown-bar-item">
                        <div className="breakdown-label-row">
                            <span style={{ color: '#a855f7' }}>Openings & Fixtures</span>
                            <span>₹ {cost_summary.openings_and_fixtures_cost.toLocaleString('en-IN')} ({Math.round(cost_summary.openings_and_fixtures_cost / cost_summary.grand_total * 100)}%)</span>
                        </div>
                        <div className="breakdown-track">
                            <div className="breakdown-fill" style={{ width: `${(cost_summary.openings_and_fixtures_cost / cost_summary.grand_total) * 100}%`, background: '#a855f7' }}></div>
                        </div>
                    </div>

                    <div className="breakdown-bar-item">
                        <div className="breakdown-label-row">
                            <span style={{ color: '#38bdf8' }}>Services (Plumbing & Electrical)</span>
                            <span>₹ {cost_summary.services_cost.toLocaleString('en-IN')} ({Math.round(cost_summary.services_cost / cost_summary.grand_total * 100)}%)</span>
                        </div>
                        <div className="breakdown-track">
                            <div className="breakdown-fill" style={{ width: `${(cost_summary.services_cost / cost_summary.grand_total) * 100}%`, background: '#38bdf8' }}></div>
                        </div>
                    </div>

                    <div className="breakdown-bar-item">
                        <div className="breakdown-label-row">
                            <span style={{ color: '#94a3b8' }}>Contingency & Contractor Overhead</span>
                            <span>₹ {(cost_summary.contingency_cost + cost_summary.contractor_overhead_cost).toLocaleString('en-IN')} ({Math.round((cost_summary.contingency_cost + cost_summary.contractor_overhead_cost) / cost_summary.grand_total * 100)}%)</span>
                        </div>
                        <div className="breakdown-track">
                            <div className="breakdown-fill" style={{ width: `${((cost_summary.contingency_cost + cost_summary.contractor_overhead_cost) / cost_summary.grand_total) * 100}%`, background: '#94a3b8' }}></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detailed Line Items Table */}
            <div className="line-items-section">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, color: '#f1f5f9' }}>
                        Material & Work Quantity Schedule ({filteredItems.length} Items)
                    </h3>

                    {/* Category Filter Chips */}
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                        {Object.entries(CATEGORY_NAMES).map(([catKey, catLabel]) => (
                            <button
                                key={catKey}
                                className={`btn btn-sm ${activeCategory === catKey ? 'btn-primary' : 'btn-outline'}`}
                                onClick={() => setActiveCategory(catKey)}
                                style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}
                            >
                                {catLabel}
                            </button>
                        ))}
                    </div>
                </div>

                <table className="line-items-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Basis / Type</th>
                            <th style={{ textAlign: 'right' }}>Quantity</th>
                            <th>Unit</th>
                            <th style={{ textAlign: 'right' }}>Unit Rate (₹)</th>
                            <th style={{ textAlign: 'right' }}>Amount (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredItems.map(item => (
                            <tr key={item.id}>
                                <td className="item-desc-cell">
                                    <div className="item-title">{item.item_name}</div>
                                    <div className="item-formula">{item.formula}</div>
                                </td>
                                <td>
                                    <span className={`badge-tag ${item.classification}`}>
                                        {item.classification === 'geometry_derived' && '📐 Geometry Derived'}
                                        {item.classification === 'provisional_allowance' && '⚠️ Provisional Allowance'}
                                        {item.classification === 'fixture_count' && '🔢 Fixture Count'}
                                        {item.classification === 'specification_derived' && '📋 Specification Mix'}
                                    </span>
                                </td>
                                <td style={{ textAlign: 'right', fontWeight: 600 }}>
                                    {item.quantity.toLocaleString('en-IN')}
                                </td>
                                <td style={{ color: '#94a3b8' }}>{item.unit}</td>
                                <td style={{ textAlign: 'right', color: '#cbd5e1' }}>
                                    ₹ {item.unit_rate.toLocaleString('en-IN')}
                                </td>
                                <td style={{ textAlign: 'right', fontWeight: 700, color: '#f8fafc' }}>
                                    ₹ {item.amount.toLocaleString('en-IN')}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Assumptions & Limitations Panel */}
            <div className="estimate-notes-card">
                <h4>
                    <Info size={16} style={{ display: 'inline', marginRight: '6px', color: '#60a5fa' }} />
                    Engineering Assumptions & Transparency Notice
                </h4>
                <ul>
                    {assumptions_and_limitations.map((note, idx) => (
                        <li key={idx}>{note}</li>
                    ))}
                </ul>
                <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', fontStyle: 'italic', color: '#94a3b8' }}>
                    {disclaimer}
                </div>
            </div>

            {/* ── END-TO-END WORKFLOW ROADMAP ─────────────────────────────────── */}
            <div style={{
                marginTop: '1.5rem',
                padding: '1.25rem 1.5rem',
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                borderRadius: '12px',
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <CheckCircle2 size={18} color="#10b981" />
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                            Full Project Planning & Visualization Flow Complete
                        </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: '#10b981', background: 'rgba(16, 185, 129, 0.1)', padding: '3px 10px', borderRadius: '9999px', fontWeight: 600, border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                        All 6 Stages Integrated
                    </span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '8px' }}>
                    {[
                        { num: '01', title: 'Requirements', tab: 'planner', action: () => navigate(`/projects/${project.id}/planner`) },
                        { num: '02', title: 'Floor Plans', tab: 'floorplans', action: () => setActiveTab ? setActiveTab('floorplans') : navigate(`/projects/${project.id}?tab=floorplans`) },
                        { num: '03', title: 'Interior Studio', tab: 'interior', action: () => navigate(`/projects/${project.id}/interior`) },
                        { num: '04', title: 'Exterior Studio', tab: 'exterior', action: () => navigate(`/projects/${project.id}/exterior`) },
                        { num: '05', title: 'Unified 3D View', tab: '3d', action: () => setActiveTab ? setActiveTab('3d') : navigate(`/projects/${project.id}?tab=3d`) },
                        { num: '06', title: 'Cost Estimate', tab: 'estimate', active: true }
                    ].map(step => (
                        <div
                            key={step.num}
                            onClick={step.action}
                            style={{
                                padding: '10px 12px',
                                background: step.active ? 'rgba(56, 189, 248, 0.15)' : 'rgba(30, 41, 59, 0.7)',
                                border: `1px solid ${step.active ? '#38bdf8' : 'rgba(255, 255, 255, 0.08)'}`,
                                borderRadius: '8px',
                                cursor: step.action ? 'pointer' : 'default',
                                transition: 'all 0.15s ease'
                            }}
                        >
                            <div style={{ fontSize: '0.7rem', color: step.active ? '#38bdf8' : '#94a3b8', fontWeight: 700 }}>
                                Step {step.num}
                            </div>
                            <div style={{ fontSize: '0.82rem', fontWeight: 600, color: step.active ? '#ffffff' : '#cbd5e1', marginTop: '2px' }}>
                                {step.title}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── EDIT RATES MODAL / DRAWER ────────────────────────────────────── */}
            {isRatesModalOpen && (
                <div className="rates-modal-backdrop" onClick={() => setIsRatesModalOpen(false)}>
                    <div className="rates-modal" onClick={e => e.stopPropagation()}>
                        <div className="rates-modal-header">
                            <div>
                                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#f8fafc' }}>
                                    Edit Construction Unit Rates
                                </h3>
                                <p style={{ margin: '0.2rem 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
                                    Adjust local rates in INR (₹). Instant recalculation without rerunning the floor plan solver.
                                </p>
                            </div>
                            <button className="btn btn-outline btn-sm" onClick={() => setIsRatesModalOpen(false)}>
                                <X size={18} />
                            </button>
                        </div>

                        <div className="rates-modal-body">
                            {Object.entries(ratesByCategory).map(([catKey, items]) => (
                                <div key={catKey} className="rates-category-group">
                                    <h4>{CATEGORY_NAMES[catKey] || catKey}</h4>
                                    <div className="rates-grid">
                                        {items.map(item => (
                                            <div key={item.key} className="rate-input-card">
                                                <label title={item.description || item.name}>
                                                    {item.name}
                                                </label>
                                                <div className="rate-input-row">
                                                    <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>₹</span>
                                                    <input
                                                        type="number"
                                                        min="0"
                                                        step="0.5"
                                                        value={editableRates[item.key] !== undefined ? editableRates[item.key] : item.unit_rate}
                                                        onChange={e => handleRateChange(item.key, e.target.value)}
                                                    />
                                                    <span style={{ color: '#94a3b8', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                                                        / {item.unit}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="rates-modal-footer">
                            <button className="btn btn-outline" onClick={handleResetRates} title="Reset all to Hyderabad Benchmark">
                                Reset to Hyderabad Benchmark
                            </button>
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <button className="btn btn-outline" onClick={() => setIsRatesModalOpen(false)}>
                                    Cancel
                                </button>
                                <button className="btn btn-primary" onClick={handleRecalculate} disabled={recalculating}>
                                    {recalculating ? (
                                        <>
                                            <RefreshCw size={15} className="animate-spin" style={{ marginRight: '6px' }} />
                                            Recalculating...
                                        </>
                                    ) : (
                                        'Apply & Recalculate Now'
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EstimateTab;
