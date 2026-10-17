import React, { useState, useEffect, useRef } from 'react';
import FloorPlanViewer from '../components/FloorPlanViewer';
import { PenTool, AlertTriangle, Info, Grid, Loader2, RefreshCw, Calendar, CheckCircle, Sparkles } from 'lucide-react';
import { aiService } from '../../../services/aiService';

/**
 * FloorPlansTab — Phase 6C.3 Demo Reliability
 *
 * Features:
 * - Professional step-by-step progress messages during generation
 * - Graceful fallback: if AI fails but a saved plan exists, show it with a gentle notice
 * - No alarming red error boxes for transient AI issues
 * - Compact warning-style notices for recoverable failures
 * - Full red error only for truly fatal/unrecoverable states
 */

// ── Generation progress steps for deterministic planning engine ──────────────
const PROGRESS_STEPS = [
    { delay: 0,    text: 'Analyzing plot & buildable boundary...' },
    { delay: 1500, text: 'Planning architectural zones & program...' },
    { delay: 3500, text: 'Solving room layout & adjacencies (CP-SAT)...' },
    { delay: 6500, text: 'Validating geometry & circulation...' },
    { delay: 9000, text: 'Preparing architectural drawing...' },
];

const FloorPlansTab = ({ project, planner, navigate }) => {
    const [generating, setGenerating]         = useState(false);
    const [statusMessage, setStatusMessage]   = useState('');
    const [error, setError]                   = useState(null); // { message, type: 'warning' | 'error', retryable }
    const [notice, setNotice]                 = useState(null); // { message, type: 'info' | 'success' }
    const [layoutData, setLayoutData]         = useState(null);
    const [savedPlans, setSavedPlans]         = useState([]);
    const [loadingPlans, setLoadingPlans]     = useState(true);
    const [selectedPlanId, setSelectedPlanId] = useState(null);
    const [validationResults, setValidationResults] = useState(null);
    const [metricsData, setMetricsData]       = useState(null);
    const progressTimers = useRef([]);

    const hasRequirements = project.plot_length && project.plot_width;

    // ── Load saved plans on mount ────────────────────────────────────────────
    useEffect(() => {
        if (hasRequirements) {
            loadSavedPlans();
        } else {
            setLoadingPlans(false);
        }
    }, [project.id]); // eslint-disable-line react-hooks/exhaustive-deps

    // ── Cleanup progress timers on unmount ───────────────────────────────────
    useEffect(() => {
        return () => progressTimers.current.forEach(clearTimeout);
    }, []);

    const loadSavedPlans = async (skipLayoutOverride = false) => {
        setLoadingPlans(true);
        try {
            // 1. Hydrate from local cache immediately for zero-latency rendering
            const cached = localStorage.getItem(`floorplan_${project.id}`);
            let hadCached = false;
            if (cached) {
                try {
                    const parsed = JSON.parse(cached);
                    const lData = parsed.layout_data || parsed;
                    if (lData && lData.floors) {
                        setLayoutData(lData);
                        setSelectedPlanId('cached-plan');
                        setSavedPlans([{ id: 'cached-plan', version_name: 'Architectural Blueprint V1', layout_data: lData, created_at: new Date().toISOString() }]);
                        setMetricsData(lData.metrics || null);
                        hadCached = true;
                    }
                } catch (_) {}
            }

            // 2. Fetch remote plans with a 2-second timeout to prevent UI freezes
            const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Supabase timeout')), 2000));
            const plans = await Promise.race([aiService.getFloorPlans(project.id), timeoutPromise]);
            if (plans && plans.length > 0) {
                setSavedPlans(plans);
                if (!skipLayoutOverride) {
                    setLayoutData(plans[0].layout_data);
                    setSelectedPlanId(plans[0].id);
                    setValidationResults(null);
                    setMetricsData(plans[0].layout_data?.metrics || null);
                }
            }
        } catch (err) {
            console.warn('[FloorPlansTab] Network sync notice:', err.message);
        } finally {
            setLoadingPlans(false);
        }
    };

    // ── Start progress step animation ────────────────────────────────────────
    const startProgressSteps = () => {
        progressTimers.current.forEach(clearTimeout);
        progressTimers.current = [];

        PROGRESS_STEPS.forEach(({ delay, text }) => {
            const timer = setTimeout(() => setStatusMessage(text), delay);
            progressTimers.current.push(timer);
        });
    };

    const stopProgressSteps = () => {
        progressTimers.current.forEach(clearTimeout);
        progressTimers.current = [];
    };

    // ── Generate new plan ────────────────────────────────────────────────────
    const handleGenerate = async () => {
        setGenerating(true);
        setError(null);
        setNotice(null);
        setValidationResults(null);
        setMetricsData(null);
        setStatusMessage('Analyzing your requirements...');
        startProgressSteps();

        try {
            const result = await aiService.generateFloorPlan(project.id);

            stopProgressSteps();

            if (result.status === 'fallback_saved') {
                // AI failed but we have a saved plan — show it with a gentle notice
                setLayoutData(result.layout_data);
                setSelectedPlanId(result.floor_plan_id);
                setValidationResults(result.validation);
                setMetricsData(result.metrics);
                setNotice({
                    message: result.message || "Live generation couldn't complete. Showing your most recent saved plan.",
                    type: 'info'
                });
                setStatusMessage('');
            } else {
                // Fresh generation succeeded — use the returned layout directly
                console.log('[FloorPlansTab] Fresh generation result:', {
                    status: result.status,
                    floor_plan_id: result.floor_plan_id,
                    floors: result.layout_data?.floors?.length,
                    gf_rooms: result.layout_data?.floors?.[0]?.rooms?.length,
                    ff_rooms: result.layout_data?.floors?.[1]?.rooms?.length,
                });
                setLayoutData(result.layout_data);
                setSelectedPlanId(result.floor_plan_id || null);
                setValidationResults(result.validation);
                setMetricsData(result.metrics);
                setStatusMessage('');
                setNotice({ message: 'Floor plan generated successfully!', type: 'success' });

                // Refresh versions list but DO NOT overwrite the active layout
                await loadSavedPlans(true);
            }
        } catch (err) {
            stopProgressSteps();
            console.error('Generation error:', err);

            const isRetryable = err.retryable !== false;
            const code = err.code || 'UNKNOWN';

            // Decide error severity
            if (code === 'AUTH_REQUIRED' || code === 'NETWORK_ERROR') {
                setError({
                    message: err.message,
                    type: 'error',
                    retryable: isRetryable
                });
            } else {
                // AI provider issues — show as a recoverable warning, not a fatal error
                setError({
                    message: err.message || "Floor plan generation couldn't complete right now. Please retry in a moment.",
                    type: 'warning',
                    retryable: isRetryable
                });
            }
            setStatusMessage('');
        } finally {
            setGenerating(false);
        }
    };

    // ── Switch between saved plan versions ───────────────────────────────────
    const handleSelectPlan = (plan) => {
        setLayoutData(plan.layout_data);
        setSelectedPlanId(plan.id);
        setError(null);
        setNotice(null);
        setValidationResults(null); // hide past generation validation when switching
        setMetricsData(plan.layout_data?.metrics || null);
    };

    // ── Missing requirements gate ────────────────────────────────────────────
    if (!hasRequirements) {
        return (
            <div className="card card-body text-center" style={{ padding: '4rem 2rem', margin: 'auto', maxWidth: '500px' }}>
                <AlertTriangle size={48} color="var(--color-error)" style={{ margin: '0 auto var(--space-4)' }} />
                <h3 className="text-h3">Requirements Missing</h3>
                <p className="text-muted" style={{ marginBottom: 'var(--space-6)' }}>
                    Complete your project requirements before generating a floor plan.
                </p>
                <button className="btn btn-primary" onClick={() => navigate(`/projects/${project.id}/planner`)}>
                    Complete Planner
                </button>
            </div>
        );
    }

    // ── Inline notice/banner component ───────────────────────────────────────
    const renderNotice = () => {
        if (!notice) return null;

        const isSuccess = notice.type === 'success';
        const bgColor = isSuccess
            ? 'rgba(34, 197, 94, 0.08)'
            : 'rgba(59, 130, 246, 0.08)';
        const borderColor = isSuccess
            ? 'rgba(34, 197, 94, 0.25)'
            : 'rgba(59, 130, 246, 0.25)';
        const textColor = isSuccess
            ? 'rgb(34, 197, 94)'
            : 'rgb(147, 175, 210)';
        const Icon = isSuccess ? CheckCircle : Info;

        return (
            <div style={{
                display: 'flex', alignItems: 'flex-start', gap: '8px',
                padding: '10px 12px', background: bgColor,
                border: `1px solid ${borderColor}`,
                borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)',
                fontSize: '0.82rem', lineHeight: 1.5, color: textColor
            }}>
                <Icon size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>{notice.message}</span>
            </div>
        );
    };

    // ── Inline error/warning component ───────────────────────────────────────
    const renderError = () => {
        if (!error) return null;

        const isWarning = error.type === 'warning';
        const bgColor = isWarning
            ? 'rgba(245, 158, 11, 0.08)'
            : 'rgba(239, 68, 68, 0.08)';
        const borderColor = isWarning
            ? 'rgba(245, 158, 11, 0.25)'
            : 'rgba(239, 68, 68, 0.25)';
        const textColor = isWarning
            ? 'rgb(217, 151, 49)'
            : 'var(--color-error)';
        const Icon = isWarning ? AlertTriangle : AlertTriangle;

        return (
            <div style={{
                display: 'flex', flexDirection: 'column', gap: '8px',
                padding: '10px 12px', background: bgColor,
                border: `1px solid ${borderColor}`,
                borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)',
                fontSize: '0.82rem', lineHeight: 1.5
            }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', color: textColor }}>
                    <Icon size={14} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>{error.message}</span>
                </div>
                {error.retryable && !generating && (
                    <button
                        className="btn btn-sm"
                        style={{
                            alignSelf: 'flex-start', marginLeft: '22px',
                            fontSize: '0.75rem', padding: '4px 12px',
                            background: 'rgba(255,255,255,0.06)',
                            border: `1px solid ${borderColor}`,
                            color: textColor, borderRadius: 'var(--radius-sm)',
                            cursor: 'pointer'
                        }}
                        onClick={handleGenerate}
                    >
                        <RefreshCw size={10} style={{ marginRight: '4px' }} />
                        Retry Generation
                    </button>
                )}
            </div>
        );
    };

    // ── Main layout ─────────────────────────────────────────────────────────
    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(0, 1fr) 310px',
            gap: '24px',
            alignItems: 'start'
        }}>

            {/* ── LEFT: Floor Plan Viewer ──────────────────────────────────── */}
            <div style={{ height: '650px', minHeight: '400px', maxHeight: '80vh' }}>
                <FloorPlanViewer
                    layoutData={layoutData}
                    plotWidth={project.plot_width}
                    plotLength={project.plot_length}
                    project={project}
                    loading={generating || loadingPlans}
                    loadingMessage={statusMessage}
                />
            </div>

            {/* ── RIGHT: Controls ──────────────────────────────────────────── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

                {/* Generation card */}
                <div className="card card-body" style={{ padding: 'var(--space-6)' }}>
                    <h3 style={{
                        fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.1em',
                        color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)',
                        textTransform: 'uppercase'
                    }}>
                        Generation Settings
                    </h3>

                    {/* Project summary */}
                    <div style={{
                        padding: '12px', background: 'var(--color-surface-alt)',
                        borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)',
                        fontSize: '0.875rem', lineHeight: 1.8
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-muted)' }}>Plot</span>
                            <strong>{project.plot_width} × {project.plot_length} ft</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-muted)' }}>Facing</span>
                            <strong>{project.facing || 'Not set'}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-muted)' }}>Floors</span>
                            <strong>G + {(project.floors || 1) - 1}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: 'var(--color-text-muted)' }}>Style</span>
                            <strong>{project.design_style || 'Modern'}</strong>
                        </div>
                    </div>

                    {/* Notice banner (success / info) */}
                    {renderNotice()}

                    {/* Validation & Quality badges */}
                    {validationResults && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: 'var(--space-4)' }}>
                            {[
                                { key: 'geometry', label: 'Geometry', val: !validationResults?.errors?.length },
                                { key: 'circulation', label: 'Circulation', val: metricsData?.quality?.circulation_valid ?? true },
                                { key: 'main_entrance', label: 'Main Entrance', val: validationResults.main_entrance },
                                { key: 'stair_alignment', label: 'Stair Connectivity', val: validationResults.stair_alignment && validationResults.stair_present },
                                { key: 'kitchen_dining', label: 'Kitchen/Dining', val: metricsData?.quality?.required_adjacencies?.kitchen_dining ?? true },
                                { key: 'parking_connection', label: 'Parking Access', val: validationResults.parking_connection },
                                { key: 'vehicle_gate', label: 'Vehicle Gate', val: validationResults.vehicle_gate }
                            ].map(item => {
                                const passed = item.val !== false;
                                return (
                                    <span key={item.key} style={{
                                        display: 'inline-flex', alignItems: 'center', gap: '4px',
                                        fontSize: '0.75rem', padding: '4px 8px', borderRadius: '4px',
                                        background: passed ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                        color: passed ? '#16a34a' : '#dc2626', border: `1px solid ${passed ? '#bbf7d0' : '#fecaca'}`
                                    }}>
                                        {passed ? '✅' : '❌'} {item.label}
                                    </span>
                                );
                            })}
                        </div>
                    )}

                    {/* Metrics card */}
                    {metricsData && (
                        <div style={{
                            padding: '12px', background: 'var(--color-surface-alt)',
                            borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)',
                            fontSize: '0.875rem', lineHeight: 1.8
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: 'var(--color-text-muted)' }}>Plot Coverage</span>
                                <strong>{metricsData.totals?.plot_coverage_pct ?? '--'}%</strong>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: 'var(--color-text-muted)' }}>Buildable Coverage</span>
                                <strong>{metricsData.totals?.buildable_coverage_pct ?? '--'}%</strong>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: 'var(--color-text-muted)' }}>Internal Utilization</span>
                                <strong>{metricsData.totals?.internal_building_utilization_pct ?? '--'}%</strong>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                <span style={{ color: 'var(--color-text-muted)' }}>Classified Plot</span>
                                <strong>{metricsData.totals?.classified_plot_pct ?? '--'}%</strong>
                            </div>
                            {metricsData.architectural_quality && (
                                <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--color-border)', paddingTop: '6px', marginTop: '6px' }}>
                                    <span style={{ color: '#16a34a', fontWeight: 600 }}>Architectural Quality</span>
                                    <strong style={{ color: '#16a34a' }}>{metricsData.architectural_quality.total_score} / 100</strong>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Error / warning banner */}
                    {renderError()}

                    {/* Generate button */}
                    <button
                        className="btn btn-primary"
                        style={{
                            width: '100%', padding: '11px', fontWeight: 700,
                            letterSpacing: '0.05em', display: 'flex',
                            alignItems: 'center', justifyContent: 'center', gap: '8px'
                        }}
                        disabled={generating}
                        onClick={handleGenerate}
                    >
                        {generating
                            ? <Loader2 size={15} style={{ animation: 'spin 1s linear infinite' }} />
                            : <PenTool size={15} />
                        }
                        {generating ? 'Generating...' : '✦ Generate AI Floor Plan'}
                    </button>

                    {generating && statusMessage && (
                        <p style={{
                            fontSize: '0.78rem', textAlign: 'center',
                            color: 'var(--color-text-muted)', marginTop: '10px', lineHeight: 1.4
                        }}>
                            {statusMessage}
                        </p>
                    )}

                    {/* Refresh link */}
                    {!generating && (
                        <button
                            className="btn btn-ghost btn-sm"
                            style={{
                                width: '100%', marginTop: '8px', fontSize: '0.78rem',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
                                opacity: 0.7
                            }}
                            onClick={loadSavedPlans}
                        >
                            <RefreshCw size={11} /> Refresh Plans
                        </button>
                    )}

                    {/* Quick navigation to Interior Design Studio */}
                    {layoutData && !generating && (
                        <button
                            className="btn btn-outline btn-sm"
                            style={{
                                width: '100%', marginTop: '12px', padding: '9px 12px',
                                fontSize: '0.82rem', fontWeight: 600,
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                                borderColor: 'var(--color-primary)', color: 'var(--color-primary)'
                            }}
                            onClick={() => navigate(`/projects/${project.id}/interior`)}
                        >
                            <Sparkles size={14} /> Open Interior Design Studio →
                        </button>
                    )}
                </div>

                {/* Plan versions card */}
                <div className="card card-body" style={{ padding: 'var(--space-6)' }}>
                    <h3 style={{
                        fontSize: '0.8rem', fontWeight: 700, letterSpacing: '0.1em',
                        color: 'var(--color-text-muted)', marginBottom: 'var(--space-4)',
                        textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '8px'
                    }}>
                        Plan Versions
                        <span style={{
                            background: 'var(--color-surface-alt)', borderRadius: 'var(--radius-full)',
                            padding: '1px 8px', fontSize: '0.7rem', fontWeight: 600,
                            color: 'var(--color-text-muted)', border: '1px solid var(--color-border)'
                        }}>
                            {savedPlans.length}
                        </span>
                    </h3>

                    {loadingPlans ? (
                        <div style={{ textAlign: 'center', padding: '20px 0', fontSize: '0.82rem', color: 'var(--color-text-muted)' }}>
                            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }} />
                            <span style={{ marginLeft: '8px' }}>Loading...</span>
                        </div>
                    ) : savedPlans.length === 0 ? (
                        <div style={{
                            display: 'flex', flexDirection: 'column', alignItems: 'center',
                            padding: '24px 0', color: 'var(--color-text-muted)', textAlign: 'center'
                        }}>
                            <Grid size={26} style={{ opacity: 0.25, marginBottom: '8px' }} />
                            <span style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-text-main)' }}>No plans yet.</span>
                            <span style={{ fontSize: '0.78rem', marginTop: '4px', opacity: 0.6, maxWidth: '180px', lineHeight: 1.4 }}>
                                Your generated plans will appear here.
                            </span>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '280px', overflowY: 'auto' }}>
                            {savedPlans.map((plan, i) => (
                                <div
                                    key={plan.id}
                                    className={`fp-plan-version ${selectedPlanId === plan.id ? 'selected' : ''}`}
                                    onClick={() => handleSelectPlan(plan)}
                                >
                                    <div className="fp-plan-version-name">
                                        {plan.version_name || `Version ${savedPlans.length - i}`}
                                    </div>
                                    <div className="fp-plan-version-date">
                                        <Calendar size={10} />
                                        {new Date(plan.created_at).toLocaleDateString('en-IN', {
                                            day: '2-digit', month: 'short', year: 'numeric'
                                        })}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};

export default FloorPlansTab;
