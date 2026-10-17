import React, { useState, useEffect, useMemo } from 'react';
import { 
    Layers, 
    Sparkles, 
    Check, 
    Sliders, 
    Scale, 
    Info, 
    Save, 
    X, 
    CheckCircle, 
    AlertTriangle, 
    Search, 
    Copy, 
    Maximize2,
    RefreshCw,
    Home,
    Compass,
    Eye
} from 'lucide-react';
import { INTERIOR_DESIGNS, INTERIOR_CATEGORIES, BUDGET_TIERS, STYLE_OPTIONS } from '../../../data/interiorCatalog';
import { interiorDesignService } from '../../../services/interiorDesignService';
import { aiService } from '../../../services/aiService';
import '../../../styles/pages/interior-studio.css';

const FLOORING_OPTIONS = [
    { id: 'vitrified_tiles', name: 'Vitrified Tiles (Baseline)', diff: 0 },
    { id: 'anti_skid_tiles', name: 'Anti-Skid Vitrified (+₹10/sq ft)', diff: 10 },
    { id: 'terrazzo_tiles', name: 'Custom Terrazzo (+₹60/sq ft)', diff: 60 },
    { id: 'wooden_laminate', name: 'Wooden Laminate (+₹95/sq ft)', diff: 95 },
    { id: 'engineered_hardwood', name: 'Engineered Oak (+₹185/sq ft)', diff: 185 },
    { id: 'italian_marble', name: 'Italian Statuario Marble (+₹240/sq ft)', diff: 240 }
];

const WALL_OPTIONS = [
    { id: 'standard_emulsion', name: 'Standard Acrylic Emulsion (Baseline)', rate: 0 },
    { id: 'velvet_luxury_emulsion', name: 'Luxury Velvet Emulsion (+₹26/sq ft)', rate: 26 },
    { id: 'limewash_texture', name: 'Artisanal Limewash (+₹58/sq ft)', rate: 58 },
    { id: 'fluted_louvers', name: 'Charcoal/Oak Fluted Louvers (+₹288/sq ft)', rate: 288 },
    { id: 'wood_veneer_paneling', name: 'Natural Veneer Paneling (+₹348/sq ft)', rate: 348 },
    { id: 'bookmatched_marble_slab', name: 'Bookmatched Marble Feature (+₹618/sq ft)', rate: 618 },
    { id: 'exposed_brick_cladding', name: 'Terracotta Brick Tile (+₹148/sq ft)', rate: 148 }
];

const CEILING_OPTIONS = [
    { id: 'none', name: 'Standard Plaster & Whitewash (No Drop Ceiling)' },
    { id: 'int_ceil_01', name: 'Modern Perimeter Gypsum Drop with Magnetic Track (₹135/sq ft)' },
    { id: 'int_ceil_02', name: 'Recessed LED Tray Ceiling with Warm Glow (₹140/sq ft)' },
    { id: 'int_ceil_03', name: 'Curved Architectural Cove Ceiling (₹160/sq ft)' },
    { id: 'int_ceil_04', name: 'Natural Suspended Wood Rafters (₹145/sq ft + insets)' }
];

const InteriorTab = ({ project, planner }) => {
    // ── State ─────────────────────────────────────────────────────────────────
    const [layoutRooms, setLayoutRooms] = useState([]);
    const [activeRoomId, setActiveRoomId] = useState('');
    const [selections, setSelections] = useState({});
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedBudgetTier, setSelectedBudgetTier] = useState('All');
    const [selectedStyle, setSelectedStyle] = useState('All');
    const [searchQuery, setSearchQuery] = useState('');

    // Modals
    const [comparedDesignIds, setComparedDesignIds] = useState([]);
    const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
    const [activeDetailDesign, setActiveDetailDesign] = useState(null);
    const [isSummaryModalOpen, setIsSummaryModalOpen] = useState(false);

    // Save status
    const [isSaving, setIsSaving] = useState(false);
    const [isDirty, setIsDirty] = useState(false);
    const [saveNotice, setSaveNotice] = useState(null);

    // ── 1. Discover Layout Rooms from Actual Floor Plan ────────────────────────
    useEffect(() => {
        let isMounted = true;
        const loadLayoutRooms = async () => {
            try {
                const plans = await aiService.getFloorPlans(project.id);
                let discovered = [];

                const NON_DESIGNABLE_TYPES = new Set([
                    'staircase', 'stairs', 'stair',
                    'corridor', 'passage', 'passageway', 'hallway',
                    'foyer', 'lobby', 'entry',
                    'open_terrace', 'terrace', 'balcony', 'roof_slab_below',
                    'parking', 'garage', 'driveway',
                    'utility', 'utility_room', 'wash_area',
                    'store_room', 'store',
                    'pooja', 'pooja_room',
                    'duct', 'shaft', 'void', 'sitout', 'porch', 'yard', 'setback'
                ]);

                if (plans && plans.length > 0 && plans[0].layout_data?.floors) {
                    const floors = plans[0].layout_data.floors;
                    floors.forEach((floor, fIdx) => {
                        (floor.rooms || []).forEach(r => {
                            const rType = (r.type || '').toLowerCase();
                            if (!NON_DESIGNABLE_TYPES.has(rType)) {
                                const w = parseFloat(r.width || 0);
                                const l = parseFloat(r.length || 0);
                                discovered.push({
                                    id: r.id || `${r.type}_${fIdx}_${discovered.length}`,
                                    name: r.label || r.name || r.type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
                                    type: r.type,
                                    floorNumber: fIdx,
                                    floorName: floor.name || (fIdx === 0 ? 'Ground Floor' : `Floor ${fIdx}`),
                                    width: w,
                                    length: l,
                                    area: parseFloat(r.area || (w * l))
                                });
                            }
                        });
                    });
                }

                // Fallback to planner requirements if no floor plan generated yet
                if (discovered.length === 0) {
                    discovered = [
                        { id: 'room_lr_01', name: 'Living Room', type: 'living_room', floorNumber: 0, floorName: 'Ground Floor', width: 14.0, length: 16.0, area: 224.0 },
                        { id: 'room_kit_01', name: 'Kitchen', type: 'kitchen', floorNumber: 0, floorName: 'Ground Floor', width: 10.0, length: 11.0, area: 110.0 },
                        { id: 'room_din_01', name: 'Dining Room', type: 'dining_room', floorNumber: 0, floorName: 'Ground Floor', width: 11.0, length: 12.0, area: 132.0 },
                        { id: 'room_mbr_01', name: 'Master Bedroom', type: 'master_bedroom', floorNumber: 0, floorName: 'Ground Floor', width: 13.0, length: 14.0, area: 182.0 },
                        { id: 'room_bath_01', name: 'Master Bathroom', type: 'bathroom', floorNumber: 0, floorName: 'Ground Floor', width: 6.0, length: 8.0, area: 48.0 }
                    ];
                    if (planner?.bedrooms > 1) {
                        discovered.push({ id: 'room_bed_02', name: 'Bedroom 2', type: 'bedroom', floorNumber: 1, floorName: 'First Floor', width: 12.0, length: 13.0, area: 156.0 });
                        discovered.push({ id: 'room_bath_02', name: 'Common Bathroom', type: 'bathroom', floorNumber: 1, floorName: 'First Floor', width: 6.0, length: 7.0, area: 42.0 });
                    }
                }

                if (isMounted) {
                    setLayoutRooms(discovered);
                    if (discovered.length > 0 && !activeRoomId) {
                        const defaultRoom = discovered.find(r => r.type.includes('living')) || discovered.find(r => r.type.includes('bed')) || discovered[0];
                        setActiveRoomId(defaultRoom.id);
                    }
                }

                // Load saved selections from database
                const savedPayload = await interiorDesignService.getProjectSelections(project.id).catch(() => null);
                if (isMounted && savedPayload?.selections) {
                    setSelections(savedPayload.selections);
                    setIsDirty(false);
                }
            } catch (err) {
                console.warn('Could not load plan or interior selections:', err);
            }
        };

        loadLayoutRooms();
        return () => { isMounted = false; };
    }, [project.id]);

    // Active Room Object
    const activeRoom = useMemo(() => {
        return layoutRooms.find(r => r.id === activeRoomId) || layoutRooms[0] || null;
    }, [layoutRooms, activeRoomId]);

    // Automatically sync category filter to active room type
    useEffect(() => {
        if (!activeRoom) return;
        const norm = activeRoom.type.toLowerCase();
        if (norm.includes('bed') && !norm.includes('guest')) setSelectedCategory('bedroom');
        else if (norm.includes('guest')) setSelectedCategory('guest_room');
        else if (norm.includes('living') || norm.includes('hall')) setSelectedCategory('living_room');
        else if (norm.includes('kit')) setSelectedCategory('kitchen');
        else if (norm.includes('bath') || norm.includes('toilet')) setSelectedCategory('bathroom');
        else if (norm.includes('din')) setSelectedCategory('dining_room');
        else setSelectedCategory('all');
    }, [activeRoomId]);

    // Group rooms by floor for clean sidebar navigation
    const roomsByFloor = useMemo(() => {
        const groups = {};
        layoutRooms.forEach(room => {
            const fName = room.floorName || 'Ground Floor';
            if (!groups[fName]) groups[fName] = [];
            groups[fName].push(room);
        });
        return groups;
    }, [layoutRooms]);

    // ── 2. Filter 32 Catalog Items ────────────────────────────────────────────
    const filteredDesigns = useMemo(() => {
        return INTERIOR_DESIGNS.filter(d => {
            if (selectedCategory !== 'all' && d.category !== selectedCategory) return false;
            if (selectedBudgetTier !== 'All' && d.budget_tier.toLowerCase() !== selectedBudgetTier.toLowerCase()) return false;
            if (selectedStyle !== 'All' && !d.style.toLowerCase().includes(selectedStyle.toLowerCase())) return false;
            if (searchQuery.trim()) {
                const q = searchQuery.toLowerCase();
                const matchName = d.name.toLowerCase().includes(q);
                const matchDesc = d.description.toLowerCase().includes(q);
                const matchStyle = d.style.toLowerCase().includes(q);
                const matchMat = (d.fixtures_and_materials || []).some(m => m.toLowerCase().includes(q));
                if (!matchName && !matchDesc && !matchStyle && !matchMat) return false;
            }
            return true;
        });
    }, [selectedCategory, selectedBudgetTier, selectedStyle, searchQuery]);

    // Total Interior Additional Cost across all configured rooms
    const totalInteriorCost = useMemo(() => {
        return Object.values(selections).reduce((acc, s) => acc + (s.additional_cost || 0), 0);
    }, [selections]);

    // ── 3. Quick Selection & Customization Handlers ───────────────────────────
    const handleQuickSelect = (design) => {
        if (!activeRoom) return;

        const area = activeRoom.area || 140;
        let diffRate = 0;
        if (design.budget_tier === 'Luxury') diffRate = 240;
        else if (design.budget_tier === 'Premium') diffRate = 185;
        else if (design.budget_tier === 'Mid-Range') diffRate = 95;

        const flooringCost = diffRate * area;
        const falseCeiling = area * 135;
        const millwork = design.cost_parameters?.modular_cabinets_rate_rft ? 48000 : (design.category === 'bedroom' ? 85000 : 35000);
        const lighting = 15000;
        const estCost = flooringCost + falseCeiling + millwork + lighting;

        const newSelection = {
            room_id: activeRoom.id,
            room_type: activeRoom.type,
            room_name: activeRoom.name,
            room_area_sqft: activeRoom.area,
            design_id: design.id,
            design_name: design.name,
            category: design.category,
            style: design.style,
            wall_finish_choice: 'standard_emulsion',
            flooring_choice: 'vitrified_tiles',
            ceiling_option_id: 'int_ceil_01',
            lighting_points_count: 6,
            additional_cost: estCost,
            cost_breakdown: {
                flooring_upgrade: flooringCost,
                wall_treatment: 0,
                false_ceiling: falseCeiling,
                lighting_and_electrical: lighting,
                modular_cabinetry_and_millwork: millwork,
                fixtures_and_accents: 8000
            }
        };

        setSelections(prev => ({
            ...prev,
            [activeRoom.id]: newSelection
        }));
        setIsDirty(true);
    };

    const handleSaveCustomization = (customizedSelection, applyToAllMatching = false) => {
        setSelections(prev => {
            const next = { ...prev, [customizedSelection.room_id]: customizedSelection };
            if (applyToAllMatching && activeRoom) {
                layoutRooms.forEach(r => {
                    if (r.type === activeRoom.type && r.id !== activeRoom.id) {
                        const area = r.area || activeRoom.area;
                        const scale = area / (activeRoom.area || 1);
                        next[r.id] = {
                            ...customizedSelection,
                            room_id: r.id,
                            room_name: r.name,
                            room_area_sqft: area,
                            additional_cost: Math.round(customizedSelection.additional_cost * scale)
                        };
                    }
                });
            }
            return next;
        });
        setIsDirty(true);
        setActiveDetailDesign(null);
    };

    const handleSaveToProject = async () => {
        setIsSaving(true);
        setSaveNotice(null);
        try {
            const payload = {
                project_id: project.id,
                selections: selections,
                total_interior_cost: totalInteriorCost
            };
            await interiorDesignService.saveProjectSelections(project.id, payload);
            setIsDirty(false);
            setSaveNotice({ type: 'success', message: 'All room interior selections saved successfully to project!' });
            setTimeout(() => setSaveNotice(null), 4000);
        } catch (err) {
            setSaveNotice({ type: 'error', message: err.message || 'Failed to save selections' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleToggleCompare = (designId) => {
        setComparedDesignIds(prev => {
            if (prev.includes(designId)) return prev.filter(id => id !== designId);
            if (prev.length >= 4) {
                alert('You can compare a maximum of 4 designs simultaneously.');
                return prev;
            }
            return [...prev, designId];
        });
    };

    const comparedDesigns = useMemo(() => {
        return comparedDesignIds.map(id => INTERIOR_DESIGNS.find(d => d.id === id)).filter(Boolean);
    }, [comparedDesignIds]);

    const checkRoomCompatibility = (design, room) => {
        if (!room) return { compatible: true, message: 'Dimension Verified' };
        const stList = (design.suitable_room_types || []).map(t => t.toLowerCase());
        const rType = (room.type || '').toLowerCase();
        
        let typeMatch = stList.includes('all') || stList.includes(rType);
        if (!typeMatch) {
            if (rType.includes('bed') && stList.some(s => s.includes('bed'))) typeMatch = true;
            if (rType.includes('guest') && stList.some(s => s.includes('guest') || s.includes('bed'))) typeMatch = true;
            if (rType.includes('living') && stList.some(s => s.includes('living') || s.includes('hall'))) typeMatch = true;
            if (rType.includes('bath') && stList.some(s => s.includes('bath') || s.includes('toilet'))) typeMatch = true;
        }

        if (!typeMatch) {
            return { compatible: false, message: `Designed for ${design.category.replace('_', ' ')}` };
        }

        const minDim = Math.min(room.width || 0, room.length || 0);
        if (design.id === 'int_kit_03' && minDim > 0 && minDim < 8.5) {
            return { compatible: false, message: `Requires 8.5ft width (current: ${minDim}ft)` };
        }
        if (design.id === 'int_kit_04' && minDim > 0 && minDim < 7.5) {
            return { compatible: false, message: `Requires 7.5ft width (current: ${minDim}ft)` };
        }

        return { compatible: true, message: 'Dimension Verified' };
    };

    return (
        <div className="interior-studio-root">
            {/* ── 1. CLEAN FULL-WIDTH PAGE HEADER ──────────────────────────── */}
            <header className="interior-studio-header">
                <div className="studio-header-left">
                    <div className="studio-brand-group">
                        <h2>
                            <Sparkles size={22} color="#38bdf8" />
                            Interior Design Studio
                        </h2>
                        <p className="studio-subtitle">
                            Configure interior architecture, finishes & plan-aware layouts for your house plan.
                        </p>
                    </div>

                    <div className="studio-project-tag">
                        <Home size={13} />
                        <span>{project.name || 'House Plan'}</span>
                    </div>
                </div>

                <div className="studio-header-right">
                    <div className={`save-status-indicator ${isDirty ? 'save-status-dirty' : 'save-status-saved'}`}>
                        {isDirty ? <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#fbbf24' }} /> : <CheckCircle size={14} />}
                        <span>{isDirty ? 'Unsaved changes' : 'All selections saved'}</span>
                    </div>

                    <div className="studio-estimate-card">
                        <span className="estimate-label">Total Interior Estimate</span>
                        <span className="estimate-amount">₹{totalInteriorCost.toLocaleString('en-IN')}</span>
                    </div>

                    <div className="studio-header-actions">
                        {comparedDesignIds.length >= 2 && (
                            <button className="btn-studio-action" onClick={() => setIsCompareModalOpen(true)}>
                                <Scale size={15} />
                                Compare ({comparedDesignIds.length})
                            </button>
                        )}
                        <button className="btn-studio-action" onClick={() => setIsSummaryModalOpen(true)}>
                            <Layers size={15} />
                            All Rooms ({Object.keys(selections).length}/{layoutRooms.length})
                        </button>
                        <button 
                            className="btn-studio-select" 
                            onClick={handleSaveToProject}
                            disabled={isSaving}
                        >
                            {isSaving ? <RefreshCw size={15} className="animate-spin" /> : <Save size={15} />}
                            Save Selections
                        </button>
                    </div>
                </div>
            </header>

            {/* Save Notice */}
            {saveNotice && (
                <div className={`card-compat-notice ${saveNotice.type === 'success' ? 'compat-pass' : 'compat-warn'}`} style={{ margin: '0.5rem 1.75rem 0 1.75rem' }}>
                    {saveNotice.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    <span>{saveNotice.message}</span>
                </div>
            )}

            {/* ── 2. WORKSPACE LAYOUT (SIDEBAR + MAIN AREA) ─────────────────── */}
            <div className="interior-workspace-layout">
                {/* ── LEFT ROOM NAVIGATION SIDEBAR ─────────────────────────── */}
                <aside className="interior-room-sidebar">
                    <div className="sidebar-section-title">
                        <span>House Plan Rooms</span>
                        <span className="tab-count-pill">{layoutRooms.length}</span>
                    </div>

                    {Object.entries(roomsByFloor).map(([floorName, floorRooms]) => (
                        <div key={floorName}>
                            <div className="floor-group-header">{floorName}</div>
                            <div className="room-nav-list">
                                {floorRooms.map(room => {
                                    const isCurrent = room.id === activeRoomId;
                                    const sel = selections[room.id];
                                    return (
                                        <div
                                            key={room.id}
                                            className={`room-nav-item ${isCurrent ? 'is-active' : ''}`}
                                            onClick={() => setActiveRoomId(room.id)}
                                        >
                                            <div className="room-nav-item-top">
                                                <span className="room-nav-name">{room.name}</span>
                                                <span className="room-nav-dims">{room.width}&apos;&times;{room.length}&apos;</span>
                                            </div>
                                            <div className="room-nav-dims">
                                                {room.area} sq ft &bull; {room.type.replace('_', ' ')}
                                            </div>

                                            <div className={`room-nav-design-badge ${sel ? 'is-assigned' : ''}`}>
                                                <span>{sel ? sel.design_name : 'Not configured'}</span>
                                                {sel && <Check size={12} color="#34d399" />}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}

                    <div className="sidebar-stats-footer">
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Configured Rooms:</span>
                            <strong style={{ color: '#f8fafc' }}>{Object.keys(selections).length} / {layoutRooms.length}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Total Upgrades:</span>
                            <strong style={{ color: '#38bdf8' }}>₹{totalInteriorCost.toLocaleString('en-IN')}</strong>
                        </div>
                    </div>
                </aside>

                {/* ── RIGHT MAIN GALLERY & WORKSPACE ───────────────────────── */}
                <main className="interior-main-content">
                    {/* Active Room Focus Banner */}
                    {activeRoom && (
                        <div className="active-room-banner">
                            <div className="active-room-info">
                                <h3>
                                    <Compass size={18} color="#38bdf8" />
                                    Designing: {activeRoom.name}
                                </h3>
                                <div className="active-room-specs">
                                    <span><strong>Floor:</strong> {activeRoom.floorName}</span>
                                    <span><strong>Dimensions:</strong> {activeRoom.width}&apos; &times; {activeRoom.length}&apos;</span>
                                    <span><strong>Clear Usable Area:</strong> {activeRoom.area} sq ft</span>
                                    <span>
                                        <strong>Current Selection:</strong> {selections[activeRoom.id] ? selections[activeRoom.id].design_name : 'None (Choose below)'}
                                    </span>
                                </div>
                            </div>

                            <div className="active-room-banner-actions">
                                {selections[activeRoom.id] && (
                                    <button 
                                        className="btn-studio-action"
                                        onClick={() => {
                                            const d = INTERIOR_DESIGNS.find(x => x.id === selections[activeRoom.id].design_id);
                                            if (d) setActiveDetailDesign(d);
                                        }}
                                    >
                                        <Eye size={15} />
                                        View Plan Blueprint
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Category Tabs & Filter Bar */}
                    <div className="interior-filters-section">
                        <div className="category-tabs-row">
                            {INTERIOR_CATEGORIES.map(cat => (
                                <button
                                    key={cat.id}
                                    className={`category-tab-btn ${selectedCategory === cat.id ? 'is-active' : ''}`}
                                    onClick={() => setSelectedCategory(cat.id)}
                                >
                                    <span>{cat.name}</span>
                                    <span className="tab-count-pill">{cat.count}</span>
                                </button>
                            ))}
                        </div>

                        <div className="filters-secondary-row">
                            <div className="filters-dropdowns">
                                <select className="select-filter" value={selectedBudgetTier} onChange={(e) => setSelectedBudgetTier(e.target.value)}>
                                    {BUDGET_TIERS.map(b => <option key={b} value={b}>Budget: {b}</option>)}
                                </select>
                                <select className="select-filter" value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                                    {STYLE_OPTIONS.map(s => <option key={s} value={s}>Style: {s}</option>)}
                                </select>
                                <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
                                    Showing {filteredDesigns.length} of 32 distinct designs
                                </span>
                            </div>

                            <div className="search-box-wrap">
                                <Search size={14} className="search-box-icon" />
                                <input
                                    type="text"
                                    className="search-box-input"
                                    placeholder="Search materials, styles..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Responsive 2–3-Column Gallery of Design Cards */}
                    <div className="designs-gallery-grid">
                        {filteredDesigns.map(design => {
                            const isAssigned = selections[activeRoomId]?.design_id === design.id;
                            const isCompared = comparedDesignIds.includes(design.id);
                            const compat = checkRoomCompatibility(design, activeRoom);
                            const tierClass = `badge-tier-${design.budget_tier.toLowerCase().replace(' ', '-')}`;

                            return (
                                <div key={design.id} className={`design-gallery-card ${isAssigned ? 'is-assigned-to-room' : ''}`}>
                                    <div className="card-image-viewport" onClick={() => setActiveDetailDesign(design)}>
                                        <img src={design.image_path} alt={design.name} loading="lazy" />
                                        <span className="card-overlay-badge-left">{design.category.replace('_', ' ')}</span>
                                        <span className={`card-overlay-badge-right ${tierClass}`}>{design.budget_tier}</span>
                                        {isAssigned && (
                                            <span className="card-selection-stamp">
                                                <Check size={13} /> Assigned to {activeRoom?.name}
                                            </span>
                                        )}
                                    </div>

                                    <div className="card-details-content">
                                        <div className="card-heading-row">
                                            <h4 className="card-title-text">{design.name}</h4>
                                            <span className="card-style-label">{design.style}</span>
                                        </div>

                                        <p className="card-desc-text">{design.description}</p>

                                        <div className="card-features-strip">
                                            <span className="feature-tag-pill">{design.wall_finish_default.split('with')[0].trim()}</span>
                                            <span className="feature-tag-pill">{design.flooring_default.split('(')[0].trim()}</span>
                                            {(design.fixtures_and_materials || []).slice(0, 1).map((m, i) => (
                                                <span key={i} className="feature-tag-pill">{m}</span>
                                            ))}
                                        </div>

                                        <div className={`card-compat-notice ${compat.compatible ? 'compat-pass' : 'compat-warn'}`}>
                                            {compat.compatible ? <CheckCircle size={14} /> : <AlertTriangle size={14} />}
                                            <span>{compat.message}</span>
                                        </div>
                                    </div>

                                    <div className="card-action-bar">
                                        <label className="compare-checkbox-label">
                                            <input
                                                type="checkbox"
                                                checked={isCompared}
                                                onChange={() => handleToggleCompare(design.id)}
                                            />
                                            Compare
                                        </label>

                                        <div className="card-actions-group-right">
                                            <button 
                                                className="btn-studio-action"
                                                title="Open plan-aware preview & full customization"
                                                onClick={() => setActiveDetailDesign(design)}
                                            >
                                                <Sliders size={14} style={{ marginRight: '4px' }} />
                                                Configure
                                            </button>
                                            <button
                                                className={`btn-studio-select ${isAssigned ? 'is-selected' : ''}`}
                                                onClick={() => handleQuickSelect(design)}
                                            >
                                                {isAssigned ? <Check size={14} /> : null}
                                                {isAssigned ? 'Selected' : 'Select'}
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </main>
            </div>

            {/* ── 3. INTERACTIVE DESIGN DETAILS & PLAN-AWARE PREVIEW MODAL ───── */}
            {activeDetailDesign && (
                <DetailAndPreviewModal
                    design={activeDetailDesign}
                    room={activeRoom}
                    existingSelection={selections[activeRoom?.id]}
                    onClose={() => setActiveDetailDesign(null)}
                    onSave={handleSaveCustomization}
                />
            )}

            {/* ── 4. COMPARISON MODAL (2 TO 4 DESIGNS) ───────────────────────── */}
            {isCompareModalOpen && (
                <ComparisonModal
                    designs={comparedDesigns}
                    room={activeRoom}
                    onClose={() => setIsCompareModalOpen(false)}
                    onSelectDesign={(design) => {
                        handleQuickSelect(design);
                        setIsCompareModalOpen(false);
                    }}
                />
            )}

            {/* ── 5. ALL ROOMS SUMMARY MODAL ─────────────────────────────────── */}
            {isSummaryModalOpen && (
                <RoomSummaryModal
                    layoutRooms={layoutRooms}
                    selections={selections}
                    totalCost={totalInteriorCost}
                    onClose={() => setIsSummaryModalOpen(false)}
                    onSelectRoom={(roomId) => {
                        setActiveRoomId(roomId);
                        setIsSummaryModalOpen(false);
                    }}
                />
            )}
        </div>
    );
};

// ── DETAIL & PLAN-AWARE PREVIEW MODAL ──────────────────────────────────────────
const DetailAndPreviewModal = ({ design, room, existingSelection, onClose, onSave }) => {
    const [activeTab, setActiveTab] = useState('plan_blueprint'); // 'plan_blueprint' | 'aesthetic_concept'
    const [wallChoice, setWallChoice] = useState(existingSelection?.wall_finish_choice || 'standard_emulsion');
    const [flooringChoice, setFlooringChoice] = useState(existingSelection?.flooring_choice || 'vitrified_tiles');
    const [ceilingOption, setCeilingOption] = useState(existingSelection?.ceiling_option_id || 'int_ceil_01');
    const [lightingPoints, setLightingPoints] = useState(existingSelection?.lighting_points_count || 6);
    const [applyToAll, setApplyToAll] = useState(false);

    // Plan-aware preview state
    const [planPreviewSvg, setPlanPreviewSvg] = useState(null);
    const [planClearances, setPlanClearances] = useState([]);
    const [loadingPreview, setLoadingPreview] = useState(false);

    const roomArea = room?.area || 140;

    // Load personalized geometry-grounded preview
    useEffect(() => {
        let isMounted = true;
        const fetchPersonalizedPreview = async () => {
            if (!room) return;
            setLoadingPreview(true);
            try {
                const res = await interiorDesignService.generatePersonalizedPreview({
                    room_id: room.id,
                    room_name: room.name,
                    room_type: room.type,
                    room_width: room.width,
                    room_length: room.length,
                    room_area: room.area,
                    floor_name: room.floorName,
                    design_id: design.id,
                    customizations: {
                        flooring_choice: flooringChoice,
                        lighting_points_count: lightingPoints,
                        ceiling_option_id: ceilingOption
                    }
                });
                if (isMounted && res.preview_svg) {
                    setPlanPreviewSvg(res.preview_svg);
                    setPlanClearances(res.clearances || []);
                }
            } catch (err) {
                console.warn('Could not fetch personalized preview:', err);
            } finally {
                if (isMounted) setLoadingPreview(false);
            }
        };

        fetchPersonalizedPreview();
        return () => { isMounted = false; };
    }, [room, design.id, flooringChoice, lightingPoints, ceilingOption]);

    // Live Zero Double-Counting Cost Computation
    const calculatedBreakdown = useMemo(() => {
        const floorObj = FLOORING_OPTIONS.find(f => f.id === flooringChoice) || FLOORING_OPTIONS[0];
        const flooringUpgrade = floorObj.diff * roomArea;

        const wallObj = WALL_OPTIONS.find(w => w.id === wallChoice) || WALL_OPTIONS[0];
        const wallTreatment = wallObj.rate * 80;

        let ceilingRate = 135;
        if (ceilingOption === 'none') ceilingRate = 0;
        else if (ceilingOption === 'int_ceil_02') ceilingRate = 140;
        else if (ceilingOption === 'int_ceil_03') ceilingRate = 160;
        else if (ceilingOption === 'int_ceil_04') ceilingRate = 145;
        const falseCeiling = ceilingRate * roomArea;

        const lightingCost = (lightingPoints * 1200) + (design.budget_tier === 'Luxury' ? 25000 : 15000);
        const modularCost = design.category === 'kitchen' ? 58000 : (['bedroom', 'guest_room'].includes(design.category) ? 85000 : 35000);
        const fixtures = design.category === 'bathroom' ? 22000 : 12000;

        const subtotal = flooringUpgrade + wallTreatment + falseCeiling + lightingCost + modularCost + fixtures;

        return {
            flooring_upgrade: Math.round(flooringUpgrade),
            wall_treatment: Math.round(wallTreatment),
            false_ceiling: Math.round(falseCeiling),
            lighting_and_electrical: Math.round(lightingCost),
            modular_cabinetry_and_millwork: Math.round(modularCost),
            fixtures_and_accents: Math.round(fixtures),
            total: Math.round(subtotal)
        };
    }, [wallChoice, flooringChoice, ceilingOption, lightingPoints, roomArea, design]);

    const handleApply = () => {
        const payload = {
            room_id: room.id,
            room_type: room.type,
            room_name: room.name,
            room_area_sqft: room.area,
            design_id: design.id,
            design_name: design.name,
            category: design.category,
            style: design.style,
            wall_finish_choice: wallChoice,
            flooring_choice: flooringChoice,
            ceiling_option_id: ceilingOption,
            lighting_points_count: lightingPoints,
            additional_cost: calculatedBreakdown.total,
            cost_breakdown: calculatedBreakdown
        };
        onSave(payload, applyToAll);
    };

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-card" style={{ maxWidth: '1000px' }} onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div>
                        <h3>{design.name}</h3>
                        <small style={{ color: '#94a3b8' }}>
                            {design.style} &bull; {design.budget_tier} &bull; Configuring for {room?.name} ({room?.width}&apos;&times;{room?.length}&apos; &bull; {roomArea} sq ft)
                        </small>
                    </div>
                    <button className="btn-modal-close" onClick={onClose}><X size={20} /></button>
                </div>

                <div className="detail-modal-tabs">
                    <button 
                        className={`detail-tab-btn ${activeTab === 'plan_blueprint' ? 'is-active' : ''}`}
                        onClick={() => setActiveTab('plan_blueprint')}
                    >
                        <Compass size={15} />
                        Plan-Aware Room Blueprint
                    </button>
                    <button 
                        className={`detail-tab-btn ${activeTab === 'aesthetic_concept' ? 'is-active' : ''}`}
                        onClick={() => setActiveTab('aesthetic_concept')}
                    >
                        <Sparkles size={15} />
                        Aesthetic Styling Concept
                    </button>
                </div>

                <div className="modal-body">
                    {/* Viewport: Either Plan-Aware Blueprint or Aesthetic Concept */}
                    {activeTab === 'plan_blueprint' ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            <div className="plan-preview-container">
                                {loadingPreview ? (
                                    <div style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <RefreshCw size={18} className="animate-spin" />
                                        Computing geometry-grounded layout...
                                    </div>
                                ) : planPreviewSvg ? (
                                    <div 
                                        style={{ width: '100%', height: '380px' }} 
                                        dangerouslySetInnerHTML={{ __html: planPreviewSvg }} 
                                    />
                                ) : (
                                    <div style={{ color: '#94a3b8' }}>Plan blueprint ready</div>
                                )}
                            </div>

                            {planClearances.length > 0 && (
                                <div className="plan-clearances-banner">
                                    <strong>Geometric Circulation & Clearance Verification:</strong>
                                    {planClearances.map((c, idx) => (
                                        <span key={idx}>&bull; {c}</span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div style={{ width: '100%', height: '360px', borderRadius: '10px', overflow: 'hidden', background: '#0f172a' }}>
                            <img src={design.image_path} alt={design.name} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                        </div>
                    )}

                    {/* Architectural Concept Details */}
                    <p style={{ margin: '0.25rem 0', fontSize: '0.88rem', color: '#cbd5e1', lineHeight: '1.5' }}>
                        {design.description}
                    </p>

                    {/* Customizer Form & Cost Breakdown */}
                    <div className="customizer-grid">
                        <div className="customizer-section">
                            <label className="customizer-label">
                                <span>Flooring Material Upgrade</span>
                                <small>Baseline vitrified is included in civil</small>
                            </label>
                            <select className="custom-select" value={flooringChoice} onChange={e => setFlooringChoice(e.target.value)}>
                                {FLOORING_OPTIONS.map(f => (
                                    <option key={f.id} value={f.id}>{f.name}</option>
                                ))}
                            </select>

                            <label className="customizer-label" style={{ marginTop: '0.75rem' }}>
                                <span>Wall Finish & Accent Paneling</span>
                                <small>Feature wall cladding</small>
                            </label>
                            <select className="custom-select" value={wallChoice} onChange={e => setWallChoice(e.target.value)}>
                                {WALL_OPTIONS.map(w => (
                                    <option key={w.id} value={w.id}>{w.name}</option>
                                ))}
                            </select>

                            <label className="customizer-label" style={{ marginTop: '0.75rem' }}>
                                <span>False Ceiling Specification</span>
                                <small>Drop ceiling & cove profile</small>
                            </label>
                            <select className="custom-select" value={ceilingOption} onChange={e => setCeilingOption(e.target.value)}>
                                {CEILING_OPTIONS.map(c => (
                                    <option key={c.id} value={c.id}>{c.name}</option>
                                ))}
                            </select>

                            <label className="customizer-label" style={{ marginTop: '0.75rem' }}>
                                <span>Lighting Fixture Points</span>
                                <small>₹1,200/fixture point</small>
                            </label>
                            <div className="counter-input-row">
                                <button className="btn-counter" onClick={() => setLightingPoints(p => Math.max(0, p - 1))}>-</button>
                                <span className="counter-value">{lightingPoints} pts</span>
                                <button className="btn-counter" onClick={() => setLightingPoints(p => p + 1)}>+</button>
                            </div>
                        </div>

                        {/* Cost Breakdown Card */}
                        <div className="cost-breakdown-card">
                            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#f8fafc' }}>
                                Incremental Cost Breakdown
                            </h4>
                            <div className="breakdown-row">
                                <span>Flooring Upgrade Differential</span>
                                <span>₹{calculatedBreakdown.flooring_upgrade.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row">
                                <span>Accent Wall Treatment</span>
                                <span>₹{calculatedBreakdown.wall_treatment.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row">
                                <span>Gypsum False Ceiling</span>
                                <span>₹{calculatedBreakdown.false_ceiling.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row">
                                <span>Lighting & Profile Channels</span>
                                <span>₹{calculatedBreakdown.lighting_and_electrical.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row">
                                <span>Modular Cabinetry & Millwork</span>
                                <span>₹{calculatedBreakdown.modular_cabinetry_and_millwork.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row">
                                <span>Fixtures & Hardware Accents</span>
                                <span>₹{calculatedBreakdown.fixtures_and_accents.toLocaleString('en-IN')}</span>
                            </div>
                            <div className="breakdown-row total">
                                <span>Total Room Additional Cost</span>
                                <span>₹{calculatedBreakdown.total.toLocaleString('en-IN')}</span>
                            </div>

                            <p className="no-double-count-note">
                                <strong>Zero Double-Counting:</strong> Baseline civil plaster, basic paint, standard vitrified tiles and standard wiring are already in your Phase 6D estimate. Only the upgrade differential is calculated here.
                            </p>
                        </div>
                    </div>

                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: '#cbd5e1', marginTop: '0.5rem' }}>
                        <input
                            type="checkbox"
                            checked={applyToAll}
                            onChange={e => setApplyToAll(e.target.checked)}
                            style={{ accentColor: '#2563eb' }}
                        />
                        Apply these finishes to all matching {room?.type?.replace('_', ' ')}s in this plan
                    </label>
                </div>

                <div className="modal-footer">
                    <button className="btn-studio-action" onClick={onClose}>Cancel</button>
                    <button className="btn-studio-select" onClick={handleApply}>
                        <Check size={16} style={{ marginRight: '6px' }} />
                        Save & Apply to {room?.name}
                    </button>
                </div>
            </div>
        </div>
    );
};

// ── COMPARISON COMPONENT ──────────────────────────────────────────────────────
const ComparisonModal = ({ designs, room, onClose, onSelectDesign }) => {
    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-card" style={{ maxWidth: '1100px' }} onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Compare Interior Designs for {room?.name}</h3>
                    <button className="btn-modal-close" onClick={onClose}><X size={20} /></button>
                </div>

                <div className="modal-body">
                    <div className="comparison-table-wrap">
                        <table className="comparison-table">
                            <thead>
                                <tr>
                                    <th>Feature</th>
                                    {designs.map(d => (
                                        <td key={d.id}>
                                            <img src={d.image_path} alt={d.name} className="comparison-img-thumb" />
                                            <h4 style={{ margin: '0 0 0.2rem 0', fontSize: '1rem', color: '#f8fafc' }}>{d.name}</h4>
                                            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{d.style} &bull; {d.budget_tier}</span>
                                        </td>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <th>Wall Treatment</th>
                                    {designs.map(d => <td key={d.id}>{d.wall_finish_default}</td>)}
                                </tr>
                                <tr>
                                    <th>Flooring Concept</th>
                                    {designs.map(d => <td key={d.id}>{d.flooring_default}</td>)}
                                </tr>
                                <tr>
                                    <th>Ceiling Concept</th>
                                    {designs.map(d => <td key={d.id}>{d.ceiling_concept}</td>)}
                                </tr>
                                <tr>
                                    <th>Furniture & Storage</th>
                                    {designs.map(d => <td key={d.id}>{d.furniture_concept}</td>)}
                                </tr>
                                <tr>
                                    <th>Materials & Hardware</th>
                                    {designs.map(d => (
                                        <td key={d.id}>
                                            <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.78rem' }}>
                                                {(d.fixtures_and_materials || []).map((m, i) => <li key={i}>{m}</li>)}
                                            </ul>
                                        </td>
                                    ))}
                                </tr>
                                <tr>
                                    <th>Select Action</th>
                                    {designs.map(d => (
                                        <td key={d.id}>
                                            <button className="btn-studio-select" style={{ width: '100%', justifyContent: 'center' }} onClick={() => onSelectDesign(d)}>
                                                Select for {room?.name}
                                            </button>
                                        </td>
                                    ))}
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

// ── ROOM SUMMARY MODAL ────────────────────────────────────────────────────────
const RoomSummaryModal = ({ layoutRooms, selections, totalCost, onClose, onSelectRoom }) => {
    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-card" style={{ maxWidth: '650px' }} onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>House Plan Interior Selections</h3>
                    <button className="btn-modal-close" onClick={onClose}><X size={20} /></button>
                </div>

                <div className="modal-body">
                    <div className="room-summary-list">
                        {layoutRooms.map(room => {
                            const sel = selections[room.id];
                            return (
                                <div key={room.id} className="room-summary-item">
                                    <div className="room-summary-info">
                                        <h4>{room.name}</h4>
                                        <div className="room-summary-meta">
                                            {room.floorName} &bull; {room.width}&apos;&times;{room.length}&apos; ({room.area} sq ft)
                                        </div>
                                        <div style={{ marginTop: '0.3rem', fontSize: '0.82rem', color: sel ? '#38bdf8' : '#64748b' }}>
                                            {sel ? `Design: ${sel.design_name} (${sel.style})` : 'Not configured yet'}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="room-summary-cost">
                                            {sel ? `₹${(sel.additional_cost || 0).toLocaleString('en-IN')}` : '₹0'}
                                        </div>
                                        <button 
                                            className="btn-studio-action" 
                                            style={{ marginTop: '0.4rem', fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                                            onClick={() => onSelectRoom(room.id)}
                                        >
                                            {sel ? 'Edit' : 'Configure'}
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="cost-breakdown-card" style={{ marginTop: '0.5rem' }}>
                        <div className="breakdown-row total">
                            <span>Total Estimated Interior Cost:</span>
                            <span>₹{totalCost.toLocaleString('en-IN')}</span>
                        </div>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="btn-studio-action" onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
};

export default InteriorTab;
