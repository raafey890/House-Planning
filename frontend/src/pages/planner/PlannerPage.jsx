import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, Check, Plus, Minus, Loader2 } from 'lucide-react';
import usePlannerStore from '../../store/plannerStore';
import useAuthStore from '../../store/authStore';
import useProjectStore from '../../store/projectStore';
import '../../styles/pages/planner.css';

const STEPS = ['Plot Details', 'Room Requirements', 'Design Preferences', 'Review & Create'];

export default function PlannerPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const user = useAuthStore(state => state.user);
    const { currentProject, fetchProject } = useProjectStore();
    
    const [step, setStep] = useState(1);
    const [validationError, setValidationError] = useState('');

    const planner = usePlannerStore();
    const { loadProjectSettings, clearPlanner, saveToDatabase } = planner;

    useEffect(() => {
        if (id) {
            if (!currentProject || currentProject.id !== id) {
                fetchProject(id).then(({ data }) => {
                    if (data) loadProjectSettings(data);
                });
            } else {
                loadProjectSettings(currentProject);
            }
        }
    }, [id, currentProject, fetchProject, loadProjectSettings]);

    const handleNext = () => {
        setValidationError('');
        if (step === 1) {
            if (!planner.projectName.trim()) return setValidationError('Project name is required.');
            if (planner.plotWidth <= 0 || planner.plotLength <= 0) return setValidationError('Width and length must be positive numbers.');
            if (!planner.facing) return setValidationError('Facing direction is required.');
        }
        setStep(s => Math.min(s + 1, 4));
    };

    const handlePrev = () => {
        setValidationError('');
        setStep(s => Math.max(s - 1, 1));
    };

    const handleCreate = async () => {
        if (!user) {
            navigate('/login', { state: { returnTo: location.pathname } });
            return;
        }

        const { data, error } = await saveToDatabase();
        if (error) {
            setValidationError(error.message);
        } else {
            clearPlanner();
            navigate(`/projects/${data.id}`);
        }
    };

    const NumberInput = ({ label, field, min = 0, max = 20 }) => (
        <div className="planner-num-input">
            <span className="num-label">{label}</span>
            <div className="num-controls">
                <button type="button" onClick={() => planner.setField(field, Math.max(min, planner[field] - 1))} className="num-btn"><Minus size={16} /></button>
                <span className="num-value">{planner[field]}</span>
                <button type="button" onClick={() => planner.setField(field, Math.min(max, planner[field] + 1))} className="num-btn"><Plus size={16} /></button>
            </div>
        </div>
    );

    const Chip = ({ label, active, onClick }) => (
        <div className={`planner-chip ${active ? 'active' : ''}`} onClick={onClick}>
            {active && <Check size={14} />} {label}
        </div>
    );

    const SelectCard = ({ title, desc, active, onClick }) => (
        <div className={`planner-select-card ${active ? 'active' : ''}`} onClick={onClick}>
            <div className="card-title">{title} {active && <Check size={16} className="text-accent" />}</div>
            {desc && <div className="card-desc">{desc}</div>}
        </div>
    );

    const slideVariants = {
        enter: (direction) => ({
            x: direction > 0 ? 30 : -30,
            opacity: 0
        }),
        center: {
            x: 0,
            opacity: 1
        },
        exit: (direction) => ({
            x: direction < 0 ? 30 : -30,
            opacity: 0
        })
    };

    const area = planner.plotWidth * planner.plotLength;

    return (
        <div className="planner-layout">
            <div className="planner-container">
                
                {/* PROGRESS BAR */}
                <div className="planner-progress">
                    {STEPS.map((name, i) => {
                        const stepNum = i + 1;
                        let statusClass = 'upcoming';
                        if (stepNum === step) statusClass = 'current';
                        if (stepNum < step) statusClass = 'completed';
                        
                        return (
                            <React.Fragment key={stepNum}>
                                <div className={`progress-step ${statusClass}`}>
                                    <span className="step-num">0{stepNum}</span>
                                    <span className="step-name">{name}</span>
                                </div>
                                {stepNum < STEPS.length && <div className={`progress-line ${stepNum < step ? 'completed' : ''}`} />}
                            </React.Fragment>
                        );
                    })}
                </div>

                {validationError && (
                    <div className="planner-error">
                        {validationError}
                    </div>
                )}

                <div className="planner-grid">
                    
                    {/* LEFT COLUMN: FORM */}
                    <div className="planner-form-col">
                        <AnimatePresence mode="wait" custom={1}>
                            
                            {step === 1 && (
                                <motion.div key="step1" variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="planner-step-content">
                                    <h2 className="text-h2" style={{ marginBottom: '24px' }}>Define Your Plot</h2>
                                    <div className="form-group">
                                        <label className="form-label">Project Name</label>
                                        <input type="text" className="form-control" value={planner.projectName} onChange={e => planner.setField('projectName', e.target.value)} placeholder="e.g. Dream Home" />
                                    </div>
                                    <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                        <div className="form-group">
                                            <label className="form-label">Plot Width (ft)</label>
                                            <input type="number" className="form-control" value={planner.plotWidth || ''} onChange={e => planner.setField('plotWidth', Number(e.target.value))} />
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">Plot Length (ft)</label>
                                            <input type="number" className="form-control" value={planner.plotLength || ''} onChange={e => planner.setField('plotLength', Number(e.target.value))} />
                                        </div>
                                    </div>
                                    <div className="form-row" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                                        <div className="form-group">
                                            <label className="form-label">Facing Direction</label>
                                            <select className="form-control" value={planner.facing} onChange={e => planner.setField('facing', e.target.value)}>
                                                <option>North</option><option>East</option><option>South</option><option>West</option>
                                            </select>
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label">Number of Floors</label>
                                            <select className="form-control" value={planner.floors} onChange={e => planner.setField('floors', Number(e.target.value))}>
                                                <option value={1}>1 (Ground Only)</option><option value={2}>2 (G + 1)</option><option value={3}>3 (G + 2)</option><option value={4}>4+</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Location (City / Region)</label>
                                        <input type="text" className="form-control" value={planner.location} onChange={e => planner.setField('location', e.target.value)} placeholder="e.g. Hyderabad, Telangana" />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Budget (Optional INR)</label>
                                        <input type="number" className="form-control" value={planner.budget} onChange={e => planner.setField('budget', e.target.value)} placeholder="e.g. 5000000" />
                                    </div>
                                </motion.div>
                            )}

                            {step === 2 && (
                                <motion.div key="step2" variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="planner-step-content">
                                    <h2 className="text-h2" style={{ marginBottom: '24px' }}>Room Requirements</h2>
                                    <div className="core-rooms" style={{ display: 'grid', gap: '12px' }}>
                                        <NumberInput label="Bedrooms" field="bedrooms" min={1} />
                                        <NumberInput label="Bathrooms" field="bathrooms" min={1} />
                                        <NumberInput label="Kitchens" field="kitchens" min={1} />
                                        <NumberInput label="Living Rooms" field="livingRooms" min={1} />
                                    </div>
                                    
                                    <h3 style={{ marginTop: '32px', marginBottom: '16px', fontSize: '1.2rem', color: 'var(--color-primary)' }}>Additional Spaces</h3>
                                    <div className="chip-grid" style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                        <Chip label="Dining Room" active={planner.diningRooms > 0} onClick={() => planner.setField('diningRooms', planner.diningRooms > 0 ? 0 : 1)} />
                                        <Chip label="Parking" active={planner.parkingSpaces > 0} onClick={() => planner.setField('parkingSpaces', planner.parkingSpaces > 0 ? 0 : 1)} />
                                        <Chip label="Balcony" active={planner.balconies > 0} onClick={() => planner.setField('balconies', planner.balconies > 0 ? 0 : 1)} />
                                        <Chip label="Pooja Room" active={planner.poojaRoom} onClick={() => planner.setField('poojaRoom', !planner.poojaRoom)} />
                                        <Chip label="Study Room" active={planner.studyRoom} onClick={() => planner.setField('studyRoom', !planner.studyRoom)} />
                                        <Chip label="Utility Room" active={planner.utilityRoom} onClick={() => planner.setField('utilityRoom', !planner.utilityRoom)} />
                                        <Chip label="Store Room" active={planner.storeRoom} onClick={() => planner.setField('storeRoom', !planner.storeRoom)} />
                                        <Chip label="Guest Room" active={planner.guestRoom} onClick={() => planner.setField('guestRoom', !planner.guestRoom)} />
                                    </div>
                                </motion.div>
                            )}

                            {step === 3 && (
                                <motion.div key="step3" variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="planner-step-content">
                                    <h2 className="text-h2" style={{ marginBottom: '24px' }}>Design Preferences</h2>
                                    
                                    <div className="form-group">
                                        <label className="form-label">Architecture Style</label>
                                        <div className="card-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '12px' }}>
                                            {['Modern', 'Contemporary', 'Traditional', 'Minimal', 'Luxury'].map(style => (
                                                <SelectCard key={style} title={style} active={planner.architectureStyle === style} onClick={() => planner.setField('architectureStyle', style)} />
                                            ))}
                                        </div>
                                    </div>

                                    <div className="form-group" style={{ marginTop: '24px' }}>
                                        <label className="form-label">Interior Preference</label>
                                        <div className="card-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: '12px' }}>
                                            {['Modern', 'Minimal', 'Luxury', 'Traditional', 'Scandinavian'].map(style => (
                                                <SelectCard key={style} title={style} active={planner.interiorStyle === style} onClick={() => planner.setField('interiorStyle', style)} />
                                            ))}
                                        </div>
                                    </div>

                                    <div className="form-group" style={{ marginTop: '24px' }}>
                                        <label className="form-label">Priorities (Select multiple)</label>
                                        <div className="chip-grid" style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                                            {['Natural Light', 'Ventilation', 'Maximum Space', 'Privacy', 'Open Layout'].map(p => (
                                                <Chip key={p} label={p} active={planner.priorities.includes(p)} onClick={() => planner.togglePriority(p)} />
                                            ))}
                                        </div>
                                    </div>

                                    <div className="form-group" style={{ marginTop: '24px' }}>
                                        <label className="form-label">Special Requirements</label>
                                        <textarea className="form-control" rows={3} maxLength={300} placeholder="Need elderly-friendly ground-floor bedroom..." value={planner.specialRequirements} onChange={e => planner.setField('specialRequirements', e.target.value)}></textarea>
                                    </div>
                                </motion.div>
                            )}

                            {step === 4 && (
                                <motion.div key="step4" variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.3 }} className="planner-step-content review-step">
                                    <h2 className="text-h2" style={{ marginBottom: '24px' }}>Review Project</h2>
                                    
                                    <div className="review-section">
                                        <h3 className="review-title">PLOT</h3>
                                        <p>{planner.plotWidth} × {planner.plotLength} FT — {area.toLocaleString()} SQ FT</p>
                                        <p>{planner.facing} Facing — {planner.floors} Floor(s) {planner.location && `— ${planner.location}`}</p>
                                    </div>

                                    <div className="review-section">
                                        <h3 className="review-title">ROOMS</h3>
                                        <p>{planner.bedrooms} Bedrooms, {planner.bathrooms} Bathrooms, {planner.kitchens} Kitchen, {planner.livingRooms} Living Room</p>
                                    </div>

                                    <div className="review-section">
                                        <h3 className="review-title">ADDITIONAL SPACES</h3>
                                        <p style={{ color: 'var(--color-primary)' }}>{[
                                            planner.diningRooms > 0 && 'Dining Room',
                                            planner.parkingSpaces > 0 && 'Parking',
                                            planner.balconies > 0 && 'Balcony',
                                            planner.poojaRoom && 'Pooja Room',
                                            planner.studyRoom && 'Study Room',
                                            planner.utilityRoom && 'Utility Room',
                                            planner.storeRoom && 'Store Room',
                                            planner.guestRoom && 'Guest Room'
                                        ].filter(Boolean).join(', ') || 'None'}</p>
                                    </div>

                                    <div className="review-section">
                                        <h3 className="review-title">STYLE</h3>
                                        <p>{planner.architectureStyle} Architecture, {planner.interiorStyle} Interior</p>
                                        {planner.priorities.length > 0 && <p>Priorities: {planner.priorities.join(', ')}</p>}
                                    </div>

                                    {planner.budget && (
                                        <div className="review-section">
                                            <h3 className="review-title">BUDGET</h3>
                                            <p>₹{Number(planner.budget).toLocaleString('en-IN')}</p>
                                        </div>
                                    )}
                                </motion.div>
                            )}

                        </AnimatePresence>

                        <div className="planner-actions" style={{ display: 'flex', gap: '16px', marginTop: '48px' }}>
                            <button className="btn btn-outline" onClick={handlePrev} disabled={step === 1 || planner.loading}>
                                <ArrowLeft size={18} style={{ marginRight: '8px' }} /> Back
                            </button>
                            {step < 4 ? (
                                <button className="btn btn-primary" onClick={handleNext}>
                                    Next <ArrowRight size={18} style={{ marginLeft: '8px' }} />
                                </button>
                            ) : (
                                <button className="btn btn-primary" onClick={handleCreate} disabled={planner.loading}>
                                    {planner.loading ? <Loader2 size={18} className="spin" style={{ marginRight: '8px' }} /> : 'Create Project'}
                                    {!planner.loading && <ArrowRight size={18} style={{ marginLeft: '8px' }} />}
                                </button>
                            )}
                        </div>
                    </div>

                    {/* RIGHT COLUMN: PREVIEW */}
                    <div className="planner-preview-col">
                        <div className="preview-sticky">
                            {step === 1 && (
                                <div className="live-plot-preview">
                                    <div className="plot-box">
                                        <div className="plot-dim top">{planner.plotWidth} FT</div>
                                        <div className="plot-dim left">{planner.plotLength} FT</div>
                                        <div className="plot-area">PLOT</div>
                                    </div>
                                    <div className="plot-facing-indicator">
                                        ↑ {planner.facing?.toUpperCase()}
                                    </div>
                                    <div className="plot-stats">
                                        <div className="stat">{area.toLocaleString()} SQ FT</div>
                                        <div className="stat">{planner.facing?.toUpperCase()} FACING</div>
                                    </div>
                                </div>
                            )}

                            {step === 2 && (
                                <div className="live-summary">
                                    <h3 className="summary-title">HOUSE REQUIREMENTS</h3>
                                    <ul className="summary-list">
                                        <li><span>{planner.bedrooms}</span> Bedrooms</li>
                                        <li><span>{planner.bathrooms}</span> Bathrooms</li>
                                        <li><span>{planner.kitchens}</span> Kitchens</li>
                                        <li><span>{planner.livingRooms}</span> Living Rooms</li>
                                    </ul>
                                    <h4 className="summary-subtitle">ADDITIONAL</h4>
                                    <div className="summary-chips-preview">
                                        {[
                                            planner.diningRooms > 0 && 'Dining', planner.parkingSpaces > 0 && 'Parking',
                                            planner.balconies > 0 && 'Balcony', planner.poojaRoom && 'Pooja',
                                            planner.studyRoom && 'Study', planner.utilityRoom && 'Utility',
                                            planner.storeRoom && 'Store', planner.guestRoom && 'Guest'
                                        ].filter(Boolean).map(item => (
                                            <div key={item} className="sm-chip"><Check size={12} /> {item}</div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {step === 3 && (
                                <div className="live-summary">
                                    <h3 className="summary-title">DESIGN PROFILE</h3>
                                    <div style={{ marginBottom: '16px' }}>
                                        <div className="text-muted" style={{ fontSize: '0.85rem' }}>Architecture</div>
                                        <div style={{ fontWeight: 600, color: 'var(--color-primary)', fontSize: '1.1rem' }}>{planner.architectureStyle}</div>
                                    </div>
                                    <div style={{ marginBottom: '16px' }}>
                                        <div className="text-muted" style={{ fontSize: '0.85rem' }}>Interior</div>
                                        <div style={{ fontWeight: 600, color: 'var(--color-primary)', fontSize: '1.1rem' }}>{planner.interiorStyle}</div>
                                    </div>
                                    {planner.priorities.length > 0 && (
                                        <div>
                                            <div className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '8px' }}>Priorities</div>
                                            <div className="summary-chips-preview">
                                                {planner.priorities.map(p => <div key={p} className="sm-chip">{p}</div>)}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {step === 4 && (
                                <div className="live-summary success-ready">
                                    <div style={{ textAlign: 'center', color: 'var(--color-accent)' }}>
                                        <Check size={48} style={{ marginBottom: '16px', opacity: 0.8, margin: '0 auto' }} />
                                        <h3>Ready to Create</h3>
                                        <p style={{ color: 'var(--color-text-muted)', fontSize: '0.9rem', marginTop: '8px' }}>Your project workspace will be generated based on these parameters.</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}