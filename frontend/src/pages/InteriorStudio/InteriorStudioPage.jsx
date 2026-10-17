import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
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
    ArrowLeft,
    RefreshCw,
    Home,
    Compass,
    Eye,
    Maximize2,
    SlidersHorizontal,
    ExternalLink
} from 'lucide-react';
import { useProjectStore } from '../../store';
import { INTERIOR_DESIGNS, INTERIOR_CATEGORIES, BUDGET_TIERS, STYLE_OPTIONS } from '../../data/interiorCatalog';
import { interiorDesignService } from '../../services/interiorDesignService';
import { aiService } from '../../services/aiService';
import '../../styles/pages/interior-studio.css';

// ── Room Category Mapping & Non-Designable Room Filter ────────────────────────
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

const getDesignableCategory = (roomType = '') => {
    const t = roomType.toLowerCase().trim();
    if (NON_DESIGNABLE_TYPES.has(t)) return null;
    if (t.includes('guest')) return 'guest_room';
    if (t.includes('bed')) return 'bedroom';
    if (t.includes('living') || t.includes('hall') || t.includes('drawing') || t.includes('family') || t.includes('study')) return 'living_room';
    if (t.includes('kit')) return 'kitchen';
    if (t.includes('din')) return 'dining_room';
    if (t.includes('bath') || t.includes('toilet') || t.includes('powder')) return 'bathroom';
    return null;
};

// ── Customization Finish Options ─────────────────────────────────────────────
const FLOORING_OPTIONS = [
    { id: 'vitrified_tiles', name: 'Vitrified Tiles (Baseline included in civil)', diff: 0 },
    { id: 'anti_skid_tiles', name: 'Anti-Skid Vitrified (+₹10/sq ft)', diff: 10 },
    { id: 'terrazzo_tiles', name: 'Custom Terrazzo (+₹60/sq ft)', diff: 60 },
    { id: 'wooden_laminate', name: 'Wooden Laminate (+₹95/sq ft)', diff: 95 },
    { id: 'engineered_hardwood', name: 'Engineered Oak (+₹185/sq ft)', diff: 185 },
    { id: 'italian_marble', name: 'Italian Statuario Marble (+₹240/sq ft)', diff: 240 }
];

const WALL_OPTIONS = [
    { id: 'standard_emulsion', name: 'Standard Acrylic Emulsion (Baseline included in civil)', rate: 0 },
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

export default function InteriorStudioPage() {
    const params = useParams();
    const projectId = params.id || params.projectId;
    const navigate = useNavigate();

    const { currentProject, fetchProject, projects, fetchProjects } = useProjectStore();

    // ── Studio State ──────────────────────────────────────────────────────────
    const [project, setProject] = useState(null);
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

    // Save status & loading states
    const [isSaving, setIsSaving] = useState(false);
    const [isDirty, setIsDirty] = useState(false);
    const [saveNotice, setSaveNotice] = useState(null);
    const [loadingProject, setLoadingProject] = useState(true);
    const [loadingRooms, setLoadingRooms] = useState(true);
    const [projectError, setProjectError] = useState(null);
    const [roomsError, setRoomsError] = useState(null);
    const [hasFloorPlan, setHasFloorPlan] = useState(true);
    const [browseCatalogOnly, setBrowseCatalogOnly] = useState(false);

    // ── 1. Load Project Data ──────────────────────────────────────────────────
    const loadProject = useCallback(async () => {
        if (!projectId) {
            setLoadingProject(false);
            setProjectError('No project ID specified in URL.');
            return;
        }

        setLoadingProject(true);
        setProjectError(null);

        try {
            // First check store cache
            let proj = projects.find(p => p.id === projectId) || (currentProject?.id === projectId ? currentProject : null);

            // If not found in memory, fetch single project
            if (!proj) {
                const res = await fetchProject(projectId);
                if (res?.data) proj = res.data;
            }

            // Fallback: fetch all projects for user
            if (!proj) {
                const allRes = await fetchProjects();
                if (allRes?.data) {
                    proj = allRes.data.find(p => p.id === projectId);
                }
            }

            // LocalStorage cache fallback
            if (!proj) {
                const localProj = localStorage.getItem(`project_${projectId}`);
                if (localProj) {
                    try { proj = JSON.parse(localProj); } catch (_) {}
                }
            }

            if (proj) {
                setProject(proj);
                setProjectError(null);
                try { localStorage.setItem(`project_${projectId}`, JSON.stringify(proj)); } catch (_) {}
            } else {
                setProject(null);
                setProjectError(`Project "${projectId}" could not be found.`);
            }
        } catch (err) {
            console.error('[InteriorStudio] Error loading project:', err);
            setProjectError(err.message || 'Failed to load project details');
        } finally {
            setLoadingProject(false);
        }
    }, [projectId, projects, currentProject, fetchProject, fetchProjects]);

    useEffect(() => {
        loadProject();
    }, [loadProject]);

    // ── 2. Discover Layout Rooms (Strict Filtering: NO Staircases & NO Silent Mock Rooms) ──
    const loadRoomsAndSelections = useCallback(async () => {
        if (!projectId) return;

        setLoadingRooms(true);
        setRoomsError(null);

        try {
            // Try to get floor plans from Supabase / API
            let plans = [];
            try {
                plans = await aiService.getFloorPlans(projectId);
            } catch (err) {
                console.warn('[InteriorStudio] Supabase getFloorPlans failed, checking local cache:', err);
            }

            // Fallback check: localStorage
            if (!plans || plans.length === 0) {
                const localPlan = localStorage.getItem(`floorplan_${projectId}`);
                if (localPlan) {
                    try {
                        const parsed = JSON.parse(localPlan);
                        plans = [{ layout_data: parsed.layout_data || parsed }];
                    } catch (_) {}
                }
            }

            let discovered = [];
            let planFound = false;

            if (plans && plans.length > 0 && plans[0]?.layout_data?.floors) {
                planFound = true;
                const floors = plans[0].layout_data.floors;
                floors.forEach((floor, fIdx) => {
                    const floorDoors = floor.doors || [];
                    const floorWindows = floor.windows || [];
                    (floor.rooms || []).forEach(r => {
                        const cat = getDesignableCategory(r.type);
                        // Strictly filter out non-designable rooms!
                        if (cat) {
                            const w = parseFloat(r.width || 0);
                            const l = parseFloat(r.length || 0);
                            const rx = parseFloat(r.x || 0);
                            const ry = parseFloat(r.y || 0);
                            const calcArea = parseFloat(r.area || (w * l)) || (w && l ? Math.round(w * l) : 140);

                            // Extract doors connected to this room
                            const roomDoors = floorDoors.filter(d => {
                                if (d.room_ids && Array.isArray(d.room_ids)) return d.room_ids.includes(r.id);
                                if (d.room_id) return d.room_id === r.id;
                                const dx = parseFloat(d.x || 0);
                                const dy = parseFloat(d.y || 0);
                                return dx >= rx - 1 && dx <= rx + w + 1 && dy >= ry - 1 && dy <= ry + l + 1;
                            }).map(d => ({
                                id: d.id,
                                width: parseFloat(d.width || 3.0),
                                direction: d.direction || 'inward',
                                wall_id: d.wall_id
                            }));

                            // Extract windows connected to this room
                            const roomWindows = floorWindows.filter(win => {
                                if (win.room_ids && Array.isArray(win.room_ids)) return win.room_ids.includes(r.id);
                                if (win.room_id) return win.room_id === r.id;
                                const wx = parseFloat(win.x || 0);
                                const wy = parseFloat(win.y || 0);
                                return wx >= rx - 1 && wx <= rx + w + 1 && wy >= ry - 1 && wy <= ry + l + 1;
                            }).map(win => ({
                                id: win.id,
                                width: parseFloat(win.width || 4.0),
                                sill_height: win.sill_height,
                                wall_id: win.wall_id
                            }));

                            discovered.push({
                                id: r.id || `${r.type}_${fIdx}_${discovered.length}`,
                                name: r.label || r.name || r.type.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
                                type: r.type,
                                category: cat,
                                floorNumber: fIdx,
                                floorName: floor.name || (fIdx === 0 ? 'Ground Floor' : `Floor ${fIdx}`),
                                width: w,
                                length: l,
                                area: calcArea,
                                doors: roomDoors,
                                windows: roomWindows
                            });
                        }
                    });
                });
            }

            // CRITICAL: DO NOT silently invent mock rooms if no floor plan was generated!
            setHasFloorPlan(planFound && discovered.length > 0);
            setLayoutRooms(discovered);

            if (discovered.length > 0) {
                // Default active room to first living room or master bedroom, NEVER a staircase!
                const defaultRoom = discovered.find(r => r.category === 'living_room') || 
                                    discovered.find(r => r.category === 'bedroom') || 
                                    discovered[0];
                if (defaultRoom) {
                    setActiveRoomId(defaultRoom.id);
                    setSelectedCategory(defaultRoom.category);
                }
            } else {
                setActiveRoomId('');
            }

            // Load saved selections from backend / localStorage
            const savedPayload = await interiorDesignService.getProjectSelections(projectId).catch(() => null);
            if (savedPayload?.selections) {
                setSelections(savedPayload.selections);
                setIsDirty(false);
            }
        } catch (err) {
            console.warn('[InteriorStudio] Error loading rooms or selections:', err);
            setRoomsError(err.message || 'Failed to load room layouts');
        } finally {
            setLoadingRooms(false);
        }
    }, [projectId]);

    useEffect(() => {
        loadRoomsAndSelections();
    }, [loadRoomsAndSelections]);

    // Active Room Object
    const activeRoom = useMemo(() => {
        return layoutRooms.find(r => r.id === activeRoomId) || layoutRooms[0] || null;
    }, [layoutRooms, activeRoomId]);

    // Group designable rooms by floor
    const roomsByFloor = useMemo(() => {
        const groups = {};
        layoutRooms.forEach(room => {
            const fName = room.floorName || (room.floorNumber === 0 ? 'Ground Floor' : `Floor ${room.floorNumber}`);
            if (!groups[fName]) groups[fName] = [];
            groups[fName].push(room);
        });
        return groups;
    }, [layoutRooms]);

    // Count of rooms configured with an interior design
    const configuredCount = useMemo(() => {
        return layoutRooms.filter(r => Boolean(selections[r.id])).length;
    }, [layoutRooms, selections]);

    // Sum of additional interior upgrade costs across all configured rooms
    const totalInteriorCost = useMemo(() => {
        return Object.values(selections).reduce((sum, sel) => sum + (Number(sel.additional_cost) || 0), 0);
    }, [selections]);

    // Filter catalog designs by category, budget tier, style, and search text
    const filteredDesigns = useMemo(() => {
        return INTERIOR_DESIGNS.filter(design => {
            // Category filter
            if (selectedCategory !== 'all' && design.category !== selectedCategory) {
                return false;
            }
            // Budget tier filter
            if (selectedBudgetTier !== 'All' && design.budget_tier !== selectedBudgetTier) {
                return false;
            }
            // Style filter
            if (selectedStyle !== 'All' && design.style !== selectedStyle) {
                return false;
            }
            // Search query
            if (searchQuery.trim()) {
                const q = searchQuery.toLowerCase();
                const matchName = design.name.toLowerCase().includes(q);
                const matchDesc = design.description?.toLowerCase().includes(q);
                const matchStyle = design.style?.toLowerCase().includes(q);
                const matchCategory = design.category?.toLowerCase().includes(q);
                const matchMats = (design.fixtures_and_materials || []).some(m => m.toLowerCase().includes(q));
                const matchWall = design.wall_finish_default?.toLowerCase().includes(q);
                const matchFloor = design.flooring_default?.toLowerCase().includes(q);
                if (!matchName && !matchDesc && !matchStyle && !matchCategory && !matchMats && !matchWall && !matchFloor) {
                    return false;
                }
            }
            return true;
        });
    }, [selectedCategory, selectedBudgetTier, selectedStyle, searchQuery]);

    // Automatically sync category tab to active room category
    const handleSelectRoom = useCallback((roomId) => {
        setActiveRoomId(roomId);
        const room = layoutRooms.find(r => r.id === roomId);
        if (room && room.category) {
            setSelectedCategory(room.category);
        }
    }, [layoutRooms]);

    // Auto-sync active room when category tab is changed
    const handleSelectCategory = useCallback((categoryId) => {
        setSelectedCategory(categoryId);
        if (categoryId === 'all') return;

        // Auto-switch active room to the first room matching this category
        const currentActive = layoutRooms.find(r => r.id === activeRoomId);
        if (!currentActive || currentActive.category !== categoryId) {
            const firstMatching = layoutRooms.find(r => r.category === categoryId);
            if (firstMatching) {
                setActiveRoomId(firstMatching.id);
            }
        }
    }, [layoutRooms, activeRoomId]);

    // Open Detail Modal or Select Design ensuring category compatibility
    const handleOpenDetail = (design) => {
        if (layoutRooms.length === 0) {
            setActiveDetailDesign(design);
            return;
        }

        let targetRoom = activeRoom;
        if (!targetRoom || targetRoom.category !== design.category) {
            const matchingRoom = layoutRooms.find(r => r.category === design.category);
            if (matchingRoom) {
                targetRoom = matchingRoom;
                setActiveRoomId(matchingRoom.id);
                setSelectedCategory(design.category);
            } else {
                alert(`Notice: This floor plan does not contain a ${design.category.replace('_', ' ')}. Please select a design matching one of your layout rooms.`);
                return;
            }
        }
        setActiveDetailDesign(design);
    };

    // Quick Selection Handler
    const handleQuickSelect = (design) => {
        if (layoutRooms.length === 0) {
            alert('Notice: Please generate a floor plan in the Planner first before assigning room designs.');
            return;
        }

        let targetRoom = activeRoom;
        if (!targetRoom || targetRoom.category !== design.category) {
            targetRoom = layoutRooms.find(r => r.category === design.category);
            if (!targetRoom) {
                alert(`Notice: This floor plan does not have a ${design.category.replace('_', ' ')}.`);
                return;
            }
            setActiveRoomId(targetRoom.id);
            setSelectedCategory(design.category);
        }

        const area = targetRoom.area || 140;
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
            room_id: targetRoom.id,
            room_type: targetRoom.type,
            room_name: targetRoom.name,
            room_area_sqft: targetRoom.area,
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
            [targetRoom.id]: newSelection
        }));
        setIsDirty(true);
    };

    // Save Customization Modal Handler
    const handleSaveCustomization = (customizedSelection, applyToAllMatching = false) => {
        setSelections(prev => {
            const next = { ...prev, [customizedSelection.room_id]: customizedSelection };
            if (applyToAllMatching && activeRoom) {
                layoutRooms.forEach(r => {
                    if (r.category === activeRoom.category && r.id !== activeRoom.id) {
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

    // Save Selections to Backend & Local Cache
    const handleSaveToProject = async () => {
        if (!projectId) return;
        setIsSaving(true);
        setSaveNotice(null);
        try {
            const payload = {
                project_id: projectId,
                selections: selections,
                total_interior_cost: totalInteriorCost
            };
            await interiorDesignService.saveProjectSelections(projectId, payload);
            setIsDirty(false);
            setSaveNotice({ type: 'success', message: 'All room interior selections successfully saved!' });
            setTimeout(() => setSaveNotice(null), 4000);
        } catch (err) {
            setSaveNotice({ type: 'error', message: err.message || 'Failed to save selections' });
        } finally {
            setIsSaving(false);
        }
    };

    // Compare Handler
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

    // Room Compatibility Checker
    const checkRoomCompatibility = (design, room) => {
        if (!room) return { compatible: true, message: 'Dimension Verified' };
        const stList = (design.suitable_room_types || []).map(t => t.toLowerCase());
        const rType = (room.type || '').toLowerCase();
        
        let typeMatch = stList.includes('all') || stList.includes(rType) || design.category === room.category;
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

    const plotInfoString = useMemo(() => {
        if (!project) return '';
        const parts = [];
        if (project.plot_width && project.plot_length) {
            parts.push(`${project.plot_width} × ${project.plot_length} ft`);
        }
        if (project.facing) parts.push(`${project.facing.toUpperCase()} Facing`);
        if (project.floors) parts.push(`G+${project.floors - 1}`);
        return parts.join(' • ');
    }, [project]);

    // 5-Step Workflow Progress Indicator state
    const currentWorkflowStep = useMemo(() => {
        if (activeDetailDesign) return 4;
        if (isDirty) return 5;
        if (activeRoom && selections[activeRoom.id]) return 5;
        if (activeRoom) return 2;
        return 1;
    }, [activeDetailDesign, isDirty, activeRoom, selections]);

    // ── RENDER STATE 1: LOADING SCREEN ─────────────────────────────────────────
    if (loadingProject || (loadingRooms && !browseCatalogOnly)) {
        return (
            <div className="interior-studio-fullpage-root">
                <div className="studio-state-container">
                    <div className="studio-state-card loading-card">
                        <div className="studio-loading-spinner-wrap">
                            <div className="studio-spinner-ring" />
                            <Sparkles className="studio-spinner-icon" size={26} color="#38bdf8" />
                        </div>
                        <h2 className="studio-state-title">Loading Interior Studio</h2>
                        <p className="studio-state-desc">
                            Retrieving project geometry, floor plan layouts, and room data...
                        </p>
                        <div className="studio-loading-bar-wrap">
                            <div className="studio-loading-bar-indeterminate" />
                        </div>
                        <div style={{ marginTop: '1.75rem' }}>
                            <button className="btn-back-to-project" onClick={() => navigate(`/projects/${projectId}`)}>
                                <ArrowLeft size={14} />
                                <span>Back to Project</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // ── RENDER STATE 2: MISSING / ERRORED PROJECT ──────────────────────────────
    if (!project || projectError) {
        return (
            <div className="interior-studio-fullpage-root">
                <header className="interior-studio-header">
                    <div className="studio-header-left">
                        <button className="btn-back-to-project" onClick={() => navigate('/projects')}>
                            <ArrowLeft size={16} />
                            <span>Back to Projects</span>
                        </button>
                        <div className="studio-brand-group">
                            <h1 className="studio-page-title">
                                <Sparkles size={20} color="#38bdf8" />
                                Interior Design Studio
                            </h1>
                        </div>
                    </div>
                </header>
                <div className="studio-state-container">
                    <div className="studio-state-card error-card">
                        <div className="studio-state-icon-wrap warn">
                            <AlertTriangle size={36} color="#fbbf24" />
                        </div>
                        <h2 className="studio-state-title">Project Not Found</h2>
                        <p className="studio-state-desc">
                            {projectError || `Unable to locate project "${projectId}". It may have been deleted, or you might not have access.`}
                        </p>
                        <p className="studio-state-subdesc">
                            Verify the project ID or return to your projects dashboard.
                        </p>
                        <div className="studio-state-actions">
                            <button className="btn-studio-primary" onClick={() => navigate('/projects')}>
                                <Home size={15} />
                                <span>Return to Projects</span>
                            </button>
                            <button className="btn-studio-secondary" onClick={() => loadProject()}>
                                <RefreshCw size={15} />
                                <span>Retry Loading</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // ── RENDER STATE 3: MISSING FLOOR PLAN (DO NOT SILENTLY INVENT ROOMS) ───────
    if (!hasFloorPlan && layoutRooms.length === 0 && !browseCatalogOnly) {
        return (
            <div className="interior-studio-fullpage-root">
                <header className="interior-studio-header">
                    <div className="studio-header-left">
                        <button className="btn-back-to-project" onClick={() => navigate(`/projects/${projectId}`)}>
                            <ArrowLeft size={16} />
                            <span>Back to Project</span>
                        </button>
                        <div className="studio-brand-group">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <h1 className="studio-page-title">
                                    <Sparkles size={20} color="#38bdf8" />
                                    Interior Design Studio
                                </h1>
                                {project && (
                                    <span className="studio-project-pill">
                                        <Home size={12} />
                                        {project.name}
                                    </span>
                                )}
                            </div>
                            <p className="studio-subtitle">
                                {plotInfoString ? `${plotInfoString} • ` : ''}Plan-aware interior design engine
                            </p>
                        </div>
                    </div>
                </header>
                <div className="studio-state-container">
                    <div className="studio-state-card blueprint-card">
                        <div className="studio-state-icon-wrap blueprint">
                            <Layers size={36} color="#38bdf8" />
                        </div>
                        <span className="studio-state-badge">Floor Plan Required</span>
                        <h2 className="studio-state-title">Floor Plan Required for Interior Design</h2>
                        <p className="studio-state-desc">
                            Plan-aware interior styling requires verified room dimensions, walls, doors, and window openings generated from your floor plan.
                        </p>
                        <p className="studio-state-subdesc">
                            Please generate or select a floor plan first to personalize interior designs to your exact room geometry. We do not invent generic fake rooms.
                        </p>
                        <div className="studio-state-actions">
                            <button className="btn-studio-primary" onClick={() => navigate(`/projects/${projectId}/planner`)}>
                                <Compass size={15} />
                                <span>Generate Floor Plan in Planner</span>
                            </button>
                            <button className="btn-studio-secondary" onClick={() => navigate(`/projects/${projectId}`)}>
                                <ArrowLeft size={15} />
                                <span>Back to Project Workspace</span>
                            </button>
                            <button className="btn-studio-ghost" onClick={() => setBrowseCatalogOnly(true)}>
                                <Eye size={15} />
                                <span>Browse 32 Catalog Designs (Inspiration Only)</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="interior-studio-fullpage-root">
            {/* ── 1. DEDICATED FULL-PAGE STUDIO HEADER ───────────────────────── */}
            <header className="interior-studio-header">
                <div className="studio-header-left">
                    <button 
                        className="btn-back-to-project"
                        onClick={() => navigate(`/projects/${projectId}`)}
                        title="Return to Project Dashboard"
                    >
                        <ArrowLeft size={16} />
                        <span>Back to Project</span>
                    </button>

                    <div className="studio-brand-group">
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <h1 className="studio-page-title">
                                <Sparkles size={20} color="#38bdf8" />
                                Interior Design Studio
                            </h1>
                            {project && (
                                <span className="studio-project-pill">
                                    <Home size={12} />
                                    {project.name}
                                </span>
                            )}
                        </div>
                        <p className="studio-subtitle">
                            {plotInfoString ? `${plotInfoString} • ` : ''}Personalize 32 plan-aware interior styles grounded to your floor plan geometry.
                        </p>
                    </div>
                </div>

                <div className="studio-header-right">
                    {/* Saved Status Indicator */}
                    <div className={`save-status-indicator ${isDirty ? 'save-status-dirty' : 'save-status-saved'}`}>
                        {isDirty ? (
                            <span className="dirty-pulse-dot" />
                        ) : (
                            <CheckCircle size={14} color="#34d399" />
                        )}
                        <span>{isDirty ? 'Unsaved changes' : 'All changes saved'}</span>
                    </div>

                    {/* Total Interior Upgrade Cost Card */}
                    <div 
                        className="studio-estimate-card"
                        onClick={() => setIsSummaryModalOpen(true)}
                        title="Click to view full room-by-room breakdown"
                    >
                        <span className="estimate-label">Interior Upgrade Estimate</span>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                            <span className="estimate-amount">₹{totalInteriorCost.toLocaleString('en-IN')}</span>
                            <span className="estimate-rooms-count">({configuredCount}/{layoutRooms.length} rooms)</span>
                        </div>
                    </div>

                    {/* Header Action Buttons */}
                    <div className="studio-header-actions">
                        {comparedDesignIds.length >= 2 && (
                            <button className="btn-studio-action" onClick={() => setIsCompareModalOpen(true)}>
                                <Scale size={15} />
                                Compare ({comparedDesignIds.length})
                            </button>
                        )}
                        <button className="btn-studio-action" onClick={() => setIsSummaryModalOpen(true)}>
                            <Layers size={15} />
                            All Rooms ({configuredCount}/{layoutRooms.length})
                        </button>
                        <button 
                            className={`btn-studio-save ${isDirty ? 'is-dirty' : 'is-clean'}`}
                            onClick={handleSaveToProject}
                            disabled={isSaving || !isDirty}
                        >
                            {isSaving ? <RefreshCw size={15} className="animate-spin" /> : <Save size={15} />}
                            {isSaving ? 'Saving...' : 'Save Selections'}
                        </button>
                    </div>
                </div>
            </header>

            {/* ── WORKFLOW PROGRESS STEPPER (01 to 05) ────────────────────────── */}
            <div className="studio-workflow-stepper">
                <div className={`workflow-step ${currentWorkflowStep >= 1 ? 'is-complete' : ''} ${currentWorkflowStep === 1 ? 'is-active' : ''}`}>
                    <span className="step-number">01</span>
                    <span className="step-label">Select Room</span>
                </div>
                <div className="step-connector" />
                <div className={`workflow-step ${currentWorkflowStep >= 2 ? 'is-complete' : ''} ${currentWorkflowStep === 2 ? 'is-active' : ''}`}>
                    <span className="step-number">02</span>
                    <span className="step-label">Choose Design</span>
                </div>
                <div className="step-connector" />
                <div className={`workflow-step ${currentWorkflowStep >= 3 ? 'is-complete' : ''} ${currentWorkflowStep === 3 ? 'is-active' : ''}`}>
                    <span className="step-number">03</span>
                    <span className="step-label">Customize Finishes</span>
                </div>
                <div className="step-connector" />
                <div className={`workflow-step ${currentWorkflowStep >= 4 ? 'is-complete' : ''} ${currentWorkflowStep === 4 ? 'is-active' : ''}`}>
                    <span className="step-number">04</span>
                    <span className="step-label">Plan-Aware Blueprint</span>
                </div>
                <div className="step-connector" />
                <div className={`workflow-step ${currentWorkflowStep >= 5 ? 'is-complete' : ''} ${currentWorkflowStep === 5 ? 'is-active' : ''}`}>
                    <span className="step-number">05</span>
                    <span className="step-label">Save Selections</span>
                </div>
            </div>

            {/* Inspiration Mode Notice */}
            {browseCatalogOnly && layoutRooms.length === 0 && (
                <div className="studio-inspiration-banner">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Info size={16} color="#38bdf8" />
                        <span>
                            <strong>Inspiration Mode:</strong> You are browsing 32 interior catalog designs in inspiration preview mode. Generate a floor plan in Planner to personalize 2D blueprints to your exact room geometry.
                        </span>
                    </div>
                    <button 
                        className="btn-studio-primary" 
                        style={{ padding: '0.4rem 0.85rem', fontSize: '0.78rem' }} 
                        onClick={() => navigate(`/projects/${projectId}/planner`)}
                    >
                        <Compass size={13} />
                        <span>Generate Floor Plan</span>
                    </button>
                </div>
            )}

            {/* Notification Banner */}
            {saveNotice && (
                <div className={`studio-alert-banner ${saveNotice.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                    {saveNotice.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                    <span>{saveNotice.message}</span>
                </div>
            )}

            {/* ── 2. WORKSPACE LAYOUT (SIDEBAR + MAIN AREA) ─────────────────── */}
            <div className="interior-workspace-layout">
                {/* ── LEFT ROOM NAVIGATION SIDEBAR ─────────────────────────── */}
                <aside className="interior-room-sidebar">
                    <div className="sidebar-section-title">
                        <span>{layoutRooms.length > 0 ? 'Designable Rooms' : 'Catalog Navigation'}</span>
                        <span className="tab-count-pill">
                            {layoutRooms.length > 0 ? `${configuredCount} / ${layoutRooms.length} configured` : '32 Designs'}
                        </span>
                    </div>

                    {layoutRooms.length === 0 ? (
                        <div style={{ padding: '1.25rem 1rem', textAlign: 'center', background: 'rgba(30, 41, 59, 0.5)', borderRadius: '8px', border: '1px dashed #334155', margin: '0.75rem 0' }}>
                            <Layers size={28} color="#38bdf8" style={{ margin: '0 auto 0.5rem auto' }} />
                            <h4 style={{ fontSize: '0.88rem', fontWeight: 600, color: '#f8fafc', margin: '0 0 0.35rem 0' }}>Floor Plan Required</h4>
                            <p style={{ fontSize: '0.75rem', color: '#94a3b8', margin: '0 0 1rem 0', lineHeight: 1.4 }}>
                                Generate your floor plan in Planner to unlock room-by-room blueprint styling and automatic dimensions.
                            </p>
                            <button className="btn-studio-primary" style={{ width: '100%', fontSize: '0.78rem', justifyContent: 'center' }} onClick={() => navigate(`/projects/${projectId}/planner`)}>
                                <Compass size={13} />
                                <span>Go to Planner</span>
                            </button>
                        </div>
                    ) : (
                        Object.entries(roomsByFloor).map(([floorName, floorRooms]) => (
                            <div key={floorName} className="floor-group-container">
                                <div className="floor-group-header">{floorName}</div>
                                <div className="room-nav-list">
                                    {floorRooms.map(room => {
                                        const isCurrent = room.id === activeRoomId;
                                        const sel = selections[room.id];
                                        return (
                                            <div
                                                key={room.id}
                                                className={`room-nav-item ${isCurrent ? 'is-active' : ''}`}
                                                onClick={() => handleSelectRoom(room.id)}
                                            >
                                                <div className="room-nav-item-top">
                                                    <span className="room-nav-name">{room.name}</span>
                                                    <span className="room-nav-dims">{room.width}&apos;&times;{room.length}&apos;</span>
                                                </div>
                                                <div className="room-nav-dims">
                                                    {room.area} sq ft &bull; {room.type.replace('_', ' ')}
                                                </div>

                                                <div className={`room-nav-design-badge ${sel ? 'is-assigned' : ''}`}>
                                                    <span>{sel ? sel.design_name : 'Not configured (choose design)'}</span>
                                                    {sel && <Check size={12} color="#34d399" />}
                                                </div>

                                                {sel && (
                                                    <div className="room-nav-cost-row">
                                                        <span>Upgrade:</span>
                                                        <strong>+₹{(sel.additional_cost || 0).toLocaleString('en-IN')}</strong>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        ))
                    )}

                    <div className="sidebar-stats-footer">
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Total Designable Rooms:</span>
                            <strong style={{ color: '#f8fafc' }}>{layoutRooms.length}</strong>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span>Configured Rooms:</span>
                            <strong style={{ color: '#34d399' }}>{configuredCount} / {layoutRooms.length}</strong>
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
                                        <strong>Current Design:</strong> {selections[activeRoom.id] ? (
                                            <span style={{ color: '#38bdf8', fontWeight: 600 }}>{selections[activeRoom.id].design_name}</span>
                                        ) : (
                                            <span style={{ color: '#94a3b8' }}>None (choose from catalog below)</span>
                                        )}
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
                                        View Room Blueprint
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Category Tabs & Secondary Filter Bar */}
                    <div className="interior-filters-section">
                        <div className="category-tabs-row">
                            {INTERIOR_CATEGORIES.map(cat => (
                                <button
                                    key={cat.id}
                                    className={`category-tab-btn ${selectedCategory === cat.id ? 'is-active' : ''}`}
                                    onClick={() => handleSelectCategory(cat.id)}
                                >
                                    <span>{cat.name}</span>
                                    <span className="tab-count-pill">{cat.count}</span>
                                </button>
                            ))}
                        </div>

                        {selectedCategory !== 'all' && !layoutRooms.some(r => r.category === selectedCategory) && (
                            <div className="no-room-category-notice">
                                <AlertTriangle size={16} />
                                <span>This floor plan layout currently has no <strong>{selectedCategory.replace('_', ' ')}</strong>. You can browse these 32 catalog designs for inspiration or configure rooms existing in your plan.</span>
                            </div>
                        )}

                        <div className="filters-secondary-row">
                            <div className="filters-dropdowns">
                                <select className="select-filter" value={selectedBudgetTier} onChange={(e) => setSelectedBudgetTier(e.target.value)}>
                                    {BUDGET_TIERS.map(b => <option key={b} value={b}>Budget: {b}</option>)}
                                </select>
                                <select className="select-filter" value={selectedStyle} onChange={(e) => setSelectedStyle(e.target.value)}>
                                    {STYLE_OPTIONS.map(s => <option key={s} value={s}>Style: {s}</option>)}
                                </select>
                                <span className="designs-counter-text">
                                    Showing {filteredDesigns.length} of 32 distinct designs
                                </span>
                            </div>

                            <div className="search-box-wrap">
                                <Search size={14} className="search-box-icon" />
                                <input
                                    type="text"
                                    className="search-box-input"
                                    placeholder="Search materials, styles, fixtures..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Responsive 2–3-Column Gallery of 32 Design Cards */}
                    <div className="designs-gallery-grid">
                        {filteredDesigns.map(design => {
                            const isAssigned = selections[activeRoomId]?.design_id === design.id;
                            const isCompared = comparedDesignIds.includes(design.id);
                            const compat = checkRoomCompatibility(design, activeRoom);
                            const tierClass = `badge-tier-${design.budget_tier.toLowerCase().replace(' ', '-')}`;

                            return (
                                <div key={design.id} className={`design-gallery-card ${isAssigned ? 'is-assigned-to-room' : ''}`}>
                                    <div className="card-image-viewport" onClick={() => handleOpenDetail(design)}>
                                        <img 
                                            src={design.image_path} 
                                            alt={design.name} 
                                            loading="lazy"
                                            onError={(e) => {
                                                e.target.onerror = null;
                                                e.target.src = '/images/interiors/int_bed_01.jpg';
                                            }}
                                        />
                                        <span className="card-overlay-badge-left">{design.category.replace('_', ' ')} &bull; Reference Image</span>
                                        <span className={`card-overlay-badge-right ${tierClass}`}>{design.budget_tier}</span>
                                        {isAssigned && (
                                            <span className="card-selection-stamp">
                                                <Check size={13} /> Selected for {activeRoom?.name}
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
                                            <span className="feature-tag-pill">{design.wall_finish_default?.split('with')[0]?.trim()}</span>
                                            <span className="feature-tag-pill">{design.flooring_default?.split('(')[0]?.trim()}</span>
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
                                                title="Open plan-aware 2D blueprint & customize finishes"
                                                onClick={() => handleOpenDetail(design)}
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
                        handleSelectRoom(roomId);
                        setIsSummaryModalOpen(false);
                    }}
                />
            )}
        </div>
    );
}

// ── DETAIL & PLAN-AWARE PREVIEW MODAL ──────────────────────────────────────────
function DetailAndPreviewModal({ design, room, existingSelection, onClose, onSave }) {
    const [activeTab, setActiveTab] = useState('plan_blueprint');
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
                    doors: room.doors || [],
                    windows: room.windows || [],
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
        if (!room) {
            alert('Notice: Please generate a floor plan in the Planner first before saving room interior selections.');
            return;
        }

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
                            {design.style} &bull; {design.budget_tier} {room ? `• Configuring for ${room.name} (${room.width}'×${room.length}' • ${roomArea} sq ft)` : '• Architectural Preview'}
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
                        {room ? `Personalized 2D Blueprint (${room.width}' × ${room.length}' • ${roomArea} sq ft)` : 'Personalized 2D Blueprint (Plan Required)'}
                    </button>
                    <button 
                        className={`detail-tab-btn ${activeTab === 'aesthetic_concept' ? 'is-active' : ''}`}
                        onClick={() => setActiveTab('aesthetic_concept')}
                    >
                        <Sparkles size={15} />
                        Architectural Reference Image (Aesthetic Inspiration)
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
                                        Computing geometry-grounded layout for {room?.name}...
                                    </div>
                                ) : !room ? (
                                    <div style={{ color: '#94a3b8', padding: '2.5rem 1.5rem', textAlign: 'center' }}>
                                        <Layers size={36} color="#38bdf8" style={{ margin: '0 auto 0.75rem auto' }} />
                                        <h4 style={{ fontWeight: 600, color: '#f8fafc', margin: '0 0 0.35rem 0' }}>Floor Plan Not Generated</h4>
                                        <p style={{ fontSize: '0.85rem', color: '#94a3b8', maxWidth: '420px', margin: '0 auto', lineHeight: 1.5 }}>
                                            Generate your floor plan first to render the customized 2D blueprint grounded to your room&apos;s dimensions, doorways, and window clearances.
                                        </p>
                                    </div>
                                ) : planPreviewSvg ? (
                                    <div 
                                        style={{ width: '100%', height: '380px' }} 
                                        dangerouslySetInnerHTML={{ __html: planPreviewSvg }} 
                                    />
                                ) : (
                                    <div style={{ color: '#94a3b8', padding: '2rem' }}>Plan blueprint ready</div>
                                )}
                            </div>

                            <div style={{ fontSize: '0.78rem', color: '#94a3b8', background: 'rgba(255,255,255,0.03)', padding: '8px 12px', borderRadius: '6px', borderLeft: '3px solid #10b981' }}>
                                <strong style={{ color: '#e2e8f0' }}>Personalized 2D Architectural Blueprint:</strong> Grounded in your floor plan&apos;s exact dimensions ({room?.width}&apos; &times; {room?.length}&apos; &bull; {roomArea} sq ft), circulation pathways, and openings ({room?.doors?.length || 1} door, {room?.windows?.length || 1} window). Visualizes custom furniture joinery tailored specifically to {design.name}.
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
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            <div style={{ width: '100%', height: '360px', borderRadius: '10px', overflow: 'hidden', background: '#0f172a' }}>
                                <img src={design.image_path} alt={design.name} style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
                            </div>
                            <div style={{ fontSize: '0.78rem', color: '#94a3b8', background: 'rgba(255,255,255,0.03)', padding: '8px 12px', borderRadius: '6px', borderLeft: '3px solid #38bdf8' }}>
                                <strong style={{ color: '#e2e8f0' }}>Architectural Reference Image:</strong> High-definition photographic inspiration showcasing design materials, textures, lighting mood, and styling aesthetics for <strong>{design.name}</strong>. The corresponding 2D spatial arrangement tailored to your room is rendered under the <strong>Personalized 2D Blueprint</strong> tab.
                            </div>
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
                        Apply these finishes to all matching {room?.category?.replace('_', ' ')}s in this plan
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
}

// ── COMPARISON COMPONENT ──────────────────────────────────────────────────────
function ComparisonModal({ designs, room, onClose, onSelectDesign }) {
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
}

// ── ROOM SUMMARY MODAL ────────────────────────────────────────────────────────
function RoomSummaryModal({ layoutRooms, selections, totalCost, onClose, onSelectRoom }) {
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
                                            {sel ? `+₹${(sel.additional_cost || 0).toLocaleString('en-IN')}` : '₹0'}
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
                            <span>Total Estimated Interior Upgrade Cost:</span>
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
}
