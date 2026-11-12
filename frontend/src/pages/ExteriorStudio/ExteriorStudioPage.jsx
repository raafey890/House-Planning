import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Sun,
  Moon,
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
  ArrowLeft,
  ArrowRight,
  RefreshCw,
  Home,
  Compass,
  Eye,
  SlidersHorizontal,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Building2,
  TreePine,
  Lightbulb,
  Palette,
  Camera,
  Download,
  Split,
  Image as ImageIcon,
  Maximize2,
  CheckSquare,
  RotateCcw,
  Copy,
  Undo,
  CheckCheck,
  HelpCircle,
  FileText,
  Box
} from 'lucide-react';
import { useProjectStore } from '../../store';
import { EXTERIOR_DESIGNS, EXTERIOR_CATEGORIES } from '../../data/exteriorCatalog';
import {
  HOUSE_COMPONENTS,
  COLOR_FAMILIES,
  COLOR_CATALOG,
  COLOR_PRESETS,
  MATERIAL_FINISH_TYPES,
  searchColors,
  isValidHex,
  normalizeHex
} from '../../data/exteriorColorCatalog';
import { exteriorDesignService } from '../../services/exteriorDesignService';
import { aiService } from '../../services/aiService';
const Exterior3DViewer = React.lazy(() => import('../../components/exterior/Exterior3DViewer'));
import ExteriorBlueprintViewer from '../../components/exterior/ExteriorBlueprintViewer';
import FloorPlanViewer from '../Projects/components/FloorPlanViewer';
import '../../styles/pages/exterior-studio.css';

const BUDGET_TIERS = ['All', 'Economy', 'Mid-Range', 'Premium', 'Luxury'];
const HOUSE_TYPES = ['All', 'Independent House', 'Villa', 'Duplex', 'Bungalow', 'Row House'];

const CLADDING_OPTIONS = [
  { id: 'none', name: 'None (Monolithic Plain Wall)', rate: 0 },
  { id: 'fluted_composite_louvers', name: 'Charcoal/Wood Fluted Composite Louvers (₹280/sq ft)', rate: 280 },
  { id: 'natural_teak_soffit', name: 'Natural Burma Teak Eaves & Battens (₹360/sq ft)', rate: 360 },
  { id: 'silver_quartzite_slabs', name: 'Honed Silver Quartzite Stone Panels (₹340/sq ft)', rate: 340 },
  { id: 'corten_steel_panels', name: 'Weathering Corten Steel Accent Box (₹450/sq ft)', rate: 450 },
  { id: 'terracotta_jaali_blocks', name: 'Handcrafted Terracotta Jaali Screen (₹240/sq ft)', rate: 240 },
  { id: 'laser_cut_brass_screens', name: 'Precision Laser-Cut Brass Lattice (₹450/sq ft)', rate: 450 },
  { id: 'italian_roman_travertine', name: 'Full-Height Italian Roman Travertine (₹550/sq ft)', rate: 550 },
  { id: 'bamboo_composite_louvers', name: 'Eco-Composite Bamboo Privacy Slats (₹360/sq ft)', rate: 360 }
];

export default function ExteriorStudioPage() {
  const params = useParams();
  const projectId = params.id || params.projectId;
  const navigate = useNavigate();

  const { currentProject, fetchProject, projects } = useProjectStore();

  // ── 1. Core Component State ──────────────────────────────────────────────────
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState(null);

  // 4-Step Wizard: 1 = Design, 2 = Customize, 3 = 3D Preview, 4 = Save
  const [currentStage, setCurrentStage] = useState(1);

  // Authoritative selected design state
  const [selectedDesignId, setSelectedDesignId] = useState(null);
  const defaultsInitializedRef = React.useRef(false);

  // Step 1 Selection Modal State
  const [showStep1Modal, setShowStep1Modal] = useState(false);

  // Catalog & Options State
  const [evaluatedOptions, setEvaluatedOptions] = useState([]);
  const [savedSelection, setSavedSelection] = useState(null);
  const [totalExteriorCost, setTotalExteriorCost] = useState(0);

  // Stage 1 Filters
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedBudgetTier, setSelectedBudgetTier] = useState('All');
  const [selectedHouseType, setSelectedHouseType] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedReasonsId, setExpandedReasonsId] = useState(null);

  // Stage 2 Color Customizer State (12 Components)
  const [activeComponentId, setActiveComponentId] = useState('primary_wall');
  const [customColors, setCustomColors] = useState({
    primary_wall: '#F4F4F0',
    secondary_wall: '#E5E7EB',
    accent_wall: '#2B313B',
    front_facade: '#F4F4F0',
    boundary_wall: '#E5E0D6',
    boundary_gate: '#30343B',
    door: '#8B5A2B',
    window_frame: '#20252B',
    window_glass_tint: '#7DD3FC',
    railing: '#1F2937',
    roof_parapet: '#343A40',
    exterior_trims: '#20252B'
  });

  const [customMaterials, setCustomMaterials] = useState({
    finish_type: 'matte_paint',
    cladding_type: 'none',
    door_material: 'solid_teak',
    railing_material: 'toughened_glass'
  });

  // History stack for Undo
  const [colorHistory, setColorHistory] = useState([]);

  // Search & HEX input
  const [colorSearchQuery, setColorSearchQuery] = useState('');
  const [selectedColorFamily, setSelectedColorFamily] = useState('all');
  const [customHexInput, setCustomHexInput] = useState('');
  const [hexInputTouched, setHexInputTouched] = useState(false);

  // Lighting & View Mode
  const [activeLightingMode, setActiveLightingMode] = useState('daylight');

  // Visualization Switcher Workspace State (Phase 6G.5)
  const [stage2ViewMode, setStage2ViewMode] = useState('3d'); // '3d' | 'elevation' | 'reference'
  const [stage3ViewMode, setStage3ViewMode] = useState('elevation'); // 'elevation' | '3d' | 'reference' | 'split'
  const [splitLeftMode, setSplitLeftMode] = useState('reference'); // 'reference' | 'elevation'

  // Stage 3 Technical CAD Elevation & Floor Plan State
  const [showCadView, setShowCadView] = useState(false);
  const [cadViewAngle, setCadViewAngle] = useState('front');
  const [cadSvg, setCadSvg] = useState(null);
  const [cadLoading, setCadLoading] = useState(false);
  const [cadError, setCadError] = useState(null);
  const [floorPlanLayout, setFloorPlanLayout] = useState(null);
  const [loadingFloorPlan, setLoadingFloorPlan] = useState(false);
  const [showRegenModal, setShowRegenModal] = useState(false);

  // ── 2. Load Project & Initial Data ──────────────────────────────────────────
  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setLoading(true);
      try {
        let p = currentProject;
        if (!p || p.id !== projectId) {
          if (projects && projects.length > 0) {
            p = projects.find((x) => x.id === projectId);
          }
          if (!p && fetchProject) {
            try {
              p = await fetchProject(projectId);
            } catch (_) {}
          }
        }

        if (!p) {
          const cached = localStorage.getItem(`project_${projectId}`);
          if (cached) {
            try { p = JSON.parse(cached); } catch (_) {}
          }
        }

        if (!isMounted) return;
        setProject(p || null);

        // ── Load genuine floor plan layout data with multi-tier fallback ────
        setLoadingFloorPlan(true);
        let fpData = null;

        // Tier 1: Check localStorage for cached floor plan
        const cachedFp = localStorage.getItem(`floorplan_${projectId}`);
        if (cachedFp) {
          try {
            const parsed = JSON.parse(cachedFp);
            const candidate = parsed.layout_data || parsed;
            if (candidate && Array.isArray(candidate.floors) && candidate.floors.length > 0) {
              fpData = candidate;
            }
          } catch (_) {}
        }

        // Tier 2: Check remote floor plans in Supabase
        if (!fpData) {
          try {
            const remotePlans = await aiService.getFloorPlans(projectId);
            if (remotePlans && remotePlans.length > 0) {
              const latestPlan = remotePlans[0];
              const candidate = latestPlan.layout_data || latestPlan;
              if (candidate && Array.isArray(candidate.floors) && candidate.floors.length > 0) {
                fpData = candidate;
                try {
                  localStorage.setItem(`floorplan_${projectId}`, JSON.stringify(fpData));
                } catch (_) {}
              }
            }
          } catch (err) {
            console.warn('[ExteriorStudio] Remote floor plan fetch notice:', err?.message || err);
          }
        }

        // Tier 3: Deterministic canonical architectural floor plan matching exact plot specs
        if (!fpData) {
          try {
            const activeProj = p || {
              id: projectId,
              plot_width: plotW,
              plot_length: plotL,
              facing: facing,
              floors: floors
            };
            fpData = generateCanonicalFloorPlan(activeProj);
            try {
              localStorage.setItem(`floorplan_${projectId}`, JSON.stringify(fpData));
            } catch (_) {}
          } catch (err) {
            console.warn('[ExteriorStudio] Canonical floor plan generation notice:', err);
          }
        }

        if (isMounted) {
          if (fpData) setFloorPlanLayout(fpData);
          setLoadingFloorPlan(false);
        }

        // Fetch evaluated options from backend
        try {
          const evaluated = await exteriorDesignService.getProjectExteriorOptions(projectId);
          if (isMounted && evaluated && evaluated.length > 0) {
            setEvaluatedOptions(evaluated);
          } else {
            fallbackCatalogEvaluation(p);
          }
        } catch (e) {
          fallbackCatalogEvaluation(p);
        }

        // Fetch saved project exterior selections
        try {
          const selData = await exteriorDesignService.getProjectSelection(projectId);
          if (isMounted && selData && selData.selection) {
            const sel = selData.selection;
            setSavedSelection(sel);
            if (sel.design_id) {
              setSelectedDesignId(sel.design_id);
            }
            setTotalExteriorCost(selData.total_exterior_cost || 0);

            if (sel.colors) {
              setCustomColors({
                primary_wall: sel.colors.primary_wall || '#F4F4F0',
                secondary_wall: sel.colors.secondary_wall || '#E5E7EB',
                accent_wall: sel.colors.accent_wall || '#2B313B',
                front_facade: sel.colors.front_facade || sel.colors.primary_wall || '#F4F4F0',
                boundary_wall: sel.colors.boundary_wall || '#E5E0D6',
                boundary_gate: sel.colors.boundary_gate || '#30343B',
                door: sel.colors.door || '#8B5A2B',
                window_frame: sel.colors.window_frame || '#20252B',
                window_glass_tint: sel.colors.window_glass_tint || '#7DD3FC',
                railing: sel.colors.railing || '#1F2937',
                roof_parapet: sel.colors.roof_parapet || '#343A40',
                exterior_trims: sel.colors.exterior_trims || '#20252B'
              });
            }
            if (sel.materials) {
              setCustomMaterials({
                finish_type: sel.materials.finish_type || 'matte_paint',
                cladding_type: sel.materials.cladding_type || 'none',
                door_material: sel.materials.door_material || 'solid_teak',
                railing_material: sel.materials.railing_material || 'toughened_glass'
              });
            }
          }
        } catch (e) {
          console.warn('[ExteriorStudio] Selections fallback:', e);
        }
      } catch (err) {
        console.error('[ExteriorStudio] Init error:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    function fallbackCatalogEvaluation(proj) {
      const plotW = proj?.plot_width || 30.0;
      const floors = proj?.floors || 2;
      const evaluated = EXTERIOR_DESIGNS.map((d) => {
        const floorMatch = d.suitable_floor_configs.includes(floors);
        const widthMatch = plotW >= (d.recommended_plot_size?.min_width_ft || 25.0);
        let status = 'compatible';
        let score = 95;
        const reasons = [];

        if (!floorMatch) {
          score -= 30;
          status = 'compatible_with_adjustments';
          reasons.push(`Optimized for ${d.suitable_floor_configs.join(', ')} floors (your project specifies G+${floors - 1}).`);
        }
        if (!widthMatch) {
          score -= 25;
          status = score < 60 ? 'not_recommended' : 'compatible_with_adjustments';
          reasons.push(`Requires minimum ${d.recommended_plot_size?.min_width_ft}ft frontage (plot is ${plotW}ft).`);
        }
        if (reasons.length === 0) {
          reasons.push(`Fully compatible with your ${plotW}ft frontage and G+${floors - 1} layout.`);
        }

        return {
          ...d,
          compatibility: {
            status,
            score,
            is_compatible: status !== 'not_recommended',
            reasons,
            adjustments: []
          }
        };
      });
      evaluated.sort((a, b) => b.compatibility.score - a.compatibility.score);
      setEvaluatedOptions(evaluated);
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, [projectId, currentProject, projects, fetchProject]);

  // Derive Active Selected Design (Authoritative State)
  const activeSelectedDesign = useMemo(() => {
    if (selectedDesignId) {
      const found = evaluatedOptions.find((d) => d.id === selectedDesignId);
      if (found) return found;
    }
    if (savedSelection?.design_id) {
      const found = evaluatedOptions.find((d) => d.id === savedSelection.design_id);
      if (found) return found;
    }
    return evaluatedOptions[0] || EXTERIOR_DESIGNS[0];
  }, [selectedDesignId, savedSelection, evaluatedOptions]);

  // Sync design defaults only ONCE on initial load if no saved selection exists
  useEffect(() => {
    if (!defaultsInitializedRef.current && activeSelectedDesign && !savedSelection) {
      defaultsInitializedRef.current = true;
      const p = activeSelectedDesign.primary_paint_color?.hex || '#F4F4F0';
      const a = activeSelectedDesign.secondary_paint_color?.hex || '#2B313B';
      setCustomColors({
        primary_wall: p,
        secondary_wall: '#E5E7EB',
        accent_wall: a,
        front_facade: p,
        boundary_wall: '#E5E0D6',
        boundary_gate: '#30343B',
        door: '#8B5A2B',
        window_frame: '#20252B',
        window_glass_tint: '#7DD3FC',
        railing: '#1F2937',
        roof_parapet: a,
        exterior_trims: '#20252B'
      });
      setCustomMaterials({
        finish_type: activeSelectedDesign.customization_defaults?.finish_type || 'matte_paint',
        cladding_type: activeSelectedDesign.customization_defaults?.cladding_type || 'none',
        door_material: activeSelectedDesign.customization_defaults?.door_material || 'solid_teak',
        railing_material: 'toughened_glass'
      });
    }
  }, [activeSelectedDesign, savedSelection]);

  // ── 3. Fetch CAD Vector Elevation Preview ────────────────────────────────────
  const fetchCadPreview = useCallback(async () => {
    if (!activeSelectedDesign || !project) return;
    setCadLoading(true);
    setCadError(null);
    try {
      const res = await exteriorDesignService.generatePersonalizedPreview({
        project_id: projectId,
        design_id: activeSelectedDesign.id,
        plot_width: project.plot_width || 30.0,
        plot_length: project.plot_length || 40.0,
        floors: project.floors || 2,
        plot_facing: project.facing || 'North',
        view_angle: cadViewAngle,
        lighting_mode: activeLightingMode,
        colors: customColors,
        materials: customMaterials,
        lighting: { style: 'architectural_grazers', fixture_count: 6 }
      });

      if (res && res.status === 'success') {
        setCadSvg(res.svg_content);
      } else {
        setCadError(res?.error_detail || 'Failed to render technical elevation');
      }
    } catch (err) {
      setCadError(err.message || 'Error generating CAD elevation');
    } finally {
      setCadLoading(false);
    }
  }, [projectId, activeSelectedDesign, project, cadViewAngle, activeLightingMode, customColors, customMaterials]);

  useEffect(() => {
    if (showCadView && activeSelectedDesign && project) {
      fetchCadPreview();
    }
  }, [showCadView, activeSelectedDesign, cadViewAngle, activeLightingMode, fetchCadPreview, project]);

  // ── 4. Calculate Live Cost Breakdown ──────────────────────────────────────────
  useEffect(() => {
    async function updateCost() {
      if (!activeSelectedDesign || !project) return;
      try {
        const costRes = await exteriorDesignService.calculateCost({
          project_id: projectId,
          design_id: activeSelectedDesign.id,
          plot_width: project.plot_width || 30.0,
          plot_length: project.plot_length || 40.0,
          floors: project.floors || 2,
          materials: customMaterials,
          lighting: { style: 'architectural_grazers', fixture_count: 6 }
        });
        if (costRes && costRes.total_exterior_cost) {
          setTotalExteriorCost(costRes.total_exterior_cost);
        }
      } catch (e) {
        // Local calculation fallback
        const plotW = project.plot_width || 30;
        const floors = project.floors || 2;
        const paintDiff = customMaterials.finish_type === 'matte_paint' ? 0 : 22.0;
        const wallArea = (plotW * 2 + (project.plot_length || 40) * 2) * 0.7 * floors * 10 * 0.8;
        const costPaint = Math.round(paintDiff * wallArea);
        const costClad = customMaterials.cladding_type === 'none' ? 0 : Math.round(plotW * floors * 10 * 0.3 * 300);
        setTotalExteriorCost(costPaint + costClad + 23200 + 25000 + 20000);
      }
    }
    updateCost();
  }, [activeSelectedDesign, project, projectId, customMaterials]);

  // ── 5. Color Search & Filtering ─────────────────────────────────────────────
  const availableSwatches = useMemo(() => {
    return searchColors(colorSearchQuery, selectedColorFamily);
  }, [colorSearchQuery, selectedColorFamily]);

  const isHexValid = useMemo(() => {
    return isValidHex(customHexInput);
  }, [customHexInput]);

  // Record undo state before modifying colors
  const pushHistory = useCallback(() => {
    setColorHistory((prev) => [
      ...prev.slice(-19), // keep last 20 states
      {
        colors: { ...customColors },
        materials: { ...customMaterials }
      }
    ]);
  }, [customColors, customMaterials]);

  const handleApplyHex = () => {
    if (isHexValid) {
      pushHistory();
      const normalized = normalizeHex(customHexInput);
      setCustomColors((prev) => ({
        ...prev,
        [activeComponentId]: normalized
      }));
    }
  };

  const handleApplyToAllWalls = () => {
    pushHistory();
    const currentColor = customColors[activeComponentId] || '#F4F4F0';
    setCustomColors((prev) => ({
      ...prev,
      primary_wall: currentColor,
      secondary_wall: currentColor,
      front_facade: currentColor
    }));
  };

  const handleApplyPreset = (preset) => {
    if (!preset || !preset.colors) return;
    pushHistory();
    setCustomColors((prev) => ({
      ...prev,
      ...preset.colors
    }));
  };

  // 4 Working Control Actions for Step 2
  const handleUndo = () => {
    if (colorHistory.length === 0) return;
    const previous = colorHistory[colorHistory.length - 1];
    setColorHistory((prev) => prev.slice(0, -1));
    setCustomColors(previous.colors);
    if (previous.materials) setCustomMaterials(previous.materials);
  };

  const handleResetColors = () => {
    if (!activeSelectedDesign) return;
    pushHistory();
    const p = activeSelectedDesign.primary_paint_color?.hex || '#F4F4F0';
    const a = activeSelectedDesign.secondary_paint_color?.hex || '#2B313B';
    setCustomColors({
      primary_wall: p,
      secondary_wall: '#E5E7EB',
      accent_wall: a,
      front_facade: p,
      boundary_wall: '#E5E0D6',
      boundary_gate: '#30343B',
      door: '#8B5A2B',
      window_frame: '#20252B',
      window_glass_tint: '#7DD3FC',
      railing: '#1F2937',
      roof_parapet: a,
      exterior_trims: '#20252B'
    });
  };

  const handleRestoreDefaults = () => {
    if (!activeSelectedDesign) return;
    pushHistory();
    handleResetColors();
    setCustomMaterials({
      finish_type: activeSelectedDesign.customization_defaults?.finish_type || 'matte_paint',
      cladding_type: activeSelectedDesign.customization_defaults?.cladding_type || 'none',
      door_material: 'solid_teak',
      railing_material: 'toughened_glass'
    });
  };

  const handleCancelChanges = () => {
    if (savedSelection) {
      if (savedSelection.colors) setCustomColors({ ...savedSelection.colors });
      if (savedSelection.materials) setCustomMaterials({ ...savedSelection.materials });
    } else {
      handleRestoreDefaults();
    }
  };

  // ── 6. Save Selection Handler ───────────────────────────────────────────────
  const handleSaveSelection = async (designToSave = activeSelectedDesign, andApply = false) => {
    if (!designToSave) return;
    setSaving(true);
    setSaveError(null);
    try {
      const payload = {
        project_id: projectId,
        selection: {
          project_id: projectId,
          design_id: designToSave.id,
          design_name: designToSave.name,
          category: designToSave.category,
          style: designToSave.style,
          colors: customColors,
          materials: customMaterials,
          lighting: { style: 'architectural_grazers', fixture_count: 6 },
          landscaping: {
            greenery_level: 'moderate',
            boundary_wall_style: 'matching_plaster',
            motorized_gate: true
          }
        }
      };

      const res = await exteriorDesignService.saveProjectSelection(projectId, payload);
      setSavedSelection(res.selection || payload.selection);
      if (res.total_exterior_cost) setTotalExteriorCost(res.total_exterior_cost);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);

      if (andApply) {
        setTimeout(() => {
          navigate(`/projects/${projectId}?tab=3d`);
        }, 1200);
      }
    } catch (e) {
      console.error('[ExteriorStudio] Save failed:', e);
      setSaveError(e.message || 'Failed to persist exterior configuration to project.');
    } finally {
      setSaving(false);
    }
  };

  // Step 1: Click Design Card
  const handleSelectDesignCard = (design) => {
    setSelectedDesignId(design.id);
    const newColors = {
      primary_wall: design.primary_paint_color?.hex || '#F4F4F0',
      secondary_wall: '#E5E7EB',
      accent_wall: design.secondary_paint_color?.hex || '#2B313B',
      front_facade: design.primary_paint_color?.hex || '#F4F4F0',
      boundary_wall: '#E5E0D6',
      boundary_gate: '#30343B',
      door: '#8B5A2B',
      window_frame: '#20252B',
      window_glass_tint: '#7DD3FC',
      railing: '#1F2937',
      roof_parapet: design.secondary_paint_color?.hex || '#343A40',
      exterior_trims: '#20252B'
    };
    const newMaterials = {
      finish_type: design.customization_defaults?.finish_type || 'matte_paint',
      cladding_type: design.customization_defaults?.cladding_type || 'none',
      door_material: design.customization_defaults?.door_material || 'solid_teak',
      railing_material: 'toughened_glass'
    };
    setCustomColors(newColors);
    setCustomMaterials(newMaterials);
    handleSaveSelection(design, false);
    setShowStep1Modal(true);
  };

  // Filter Catalog Items
  const filteredCatalog = useMemo(() => {
    return evaluatedOptions.filter((item) => {
      if (selectedCategory !== 'all' && item.category !== selectedCategory) {
        return false;
      }
      if (selectedBudgetTier !== 'All' && item.budget_tier !== selectedBudgetTier) {
        return false;
      }
      if (selectedHouseType !== 'All') {
        const hts = (item.suitable_house_types || []).map((x) => x.toLowerCase());
        if (!hts.includes(selectedHouseType.toLowerCase()) && !hts.includes('all')) {
          return false;
        }
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchName = item.name.toLowerCase().includes(q);
        const matchStyle = item.style.toLowerCase().includes(q);
        const matchDesc = item.description.toLowerCase().includes(q);
        const matchMats = (item.material_palette || []).some((m) => m.toLowerCase().includes(q));
        if (!matchName && !matchStyle && !matchDesc && !matchMats) {
          return false;
        }
      }
      return true;
    });
  }, [evaluatedOptions, selectedCategory, selectedBudgetTier, selectedHouseType, searchQuery]);

  // Download CAD SVG
  const handleDownloadCadSvg = () => {
    if (!cadSvg) return;
    const blob = new Blob([cadSvg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeSelectedDesign?.id || 'elevation'}_${cadViewAngle}_cad_elevation.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // ── Loading & Guard States ──────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="exterior-studio-fullpage-root" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: '#94a3b8' }}>
          <div className="fp-loading-spinner" style={{ margin: '0 auto 16px' }} />
          <p style={{ fontSize: '1rem', fontWeight: 500 }}>Opening Exterior Design Studio...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="exterior-studio-fullpage-root" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', maxWidth: '420px', padding: '2rem' }}>
          <AlertTriangle size={44} color="#f59e0b" style={{ margin: '0 auto 12px' }} />
          <h2 style={{ fontSize: '1.25rem', color: '#f8fafc', marginBottom: '8px' }}>Project Not Found</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '16px' }}>Could not load project requirements for elevation matching.</p>
          <Link to="/projects" className="btn btn-primary">
            <ArrowLeft size={16} /> Return to Projects
          </Link>
        </div>
      </div>
    );
  }

  const plotW = Number(floorPlanLayout?.plot?.width || project.plot_width) || 50;
  const plotL = Number(floorPlanLayout?.plot?.length || project.plot_length) || 80;
  const floors = Number(floorPlanLayout?.floors?.length || project.floors) || 2;
  const facing = floorPlanLayout?.plot?.facing || project.facing || 'South';

  const activeComponent = HOUSE_COMPONENTS.find((c) => c.id === activeComponentId) || HOUSE_COMPONENTS[0];

  return (
    <div className="exterior-studio-fullpage-root">
      {/* ── Studio Sticky Header ────────────────────────────────────────────── */}
      <header className="exterior-studio-header">
        <div className="studio-header-left">
          <Link to={`/projects/${projectId}`} className="btn-back-to-project">
            <ArrowLeft size={16} /> Workspace
          </Link>
          <div className="studio-brand-group">
            <h2 className="studio-page-title">
              <Sun size={20} style={{ color: '#38bdf8' }} /> Exterior Design Studio
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span className="studio-project-tag">{project.name}</span>
              <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                {plotW} × {plotL} ft • {floors > 1 ? `G + ${floors - 1} Floors` : 'Ground Floor'} • {facing} Facing
              </span>
            </div>
          </div>
        </div>

        {/* Cost & Save Status */}
        <div className="studio-header-right">
          {saveSuccess && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#10b981', fontSize: '0.85rem', fontWeight: 600 }}>
              <CheckCircle size={16} /> Saved to Project
            </span>
          )}
          {saveError && (
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#f87171', fontSize: '0.85rem', fontWeight: 600 }}>
              <AlertTriangle size={16} /> {saveError}
            </span>
          )}
          <div className="studio-cost-summary-pill" title="Incremental exterior upgrade over Phase 6D civil baseline">
            <span className="cost-label">Exterior Upgrade:</span>
            <span className="cost-amount">₹{totalExteriorCost.toLocaleString('en-IN')}</span>
          </div>
          <button
            className="btn btn-primary"
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.95rem', display: 'inline-flex', alignItems: 'center', gap: '6px', fontWeight: 600, background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)' }}
            onClick={() => navigate(`/projects/${projectId}?tab=3d`)}
            title="Proceed to Unified 3D House Model"
          >
            <Box size={14} />
            <span>Next: 3D View →</span>
          </button>
        </div>
      </header>

      {/* ── 4-Stage Wizard Progress Stepper: 1. Design, 2. Customize, 3. 3D Preview, 4. Save ── */}
      <div className="studio-stage-stepper-container">
        <nav className="studio-stage-stepper" aria-label="Exterior Design Wizard Progress">
          <button
            className={`stage-step-btn ${currentStage === 1 ? 'active' : ''} ${currentStage > 1 ? 'completed' : ''}`}
            onClick={() => setCurrentStage(1)}
          >
            <span className="stage-step-num">1</span>
            <span>Design</span>
          </button>

          <button
            className={`stage-step-btn ${currentStage === 2 ? 'active' : ''} ${currentStage > 2 ? 'completed' : ''}`}
            onClick={() => setCurrentStage(2)}
          >
            <span className="stage-step-num">2</span>
            <span>Customize</span>
          </button>

          <button
            className={`stage-step-btn ${currentStage === 3 ? 'active' : ''} ${currentStage > 3 ? 'completed' : ''}`}
            onClick={() => setCurrentStage(3)}
          >
            <span className="stage-step-num">3</span>
            <span>3D Preview</span>
          </button>

          <button
            className={`stage-step-btn ${currentStage === 4 ? 'active' : ''}`}
            onClick={() => setCurrentStage(4)}
          >
            <span className="stage-step-num">4</span>
            <span>Save</span>
          </button>
        </nav>

        {/* Wizard Navigation Controls */}
        <div className="stepper-nav-controls">
          {currentStage > 1 && (
            <button className="btn-step-nav prev" onClick={() => setCurrentStage(c => Math.max(1, c - 1))}>
              <ArrowLeft size={13} /> Back
            </button>
          )}
          {currentStage < 4 ? (
            <button className="btn-step-nav next" onClick={() => setCurrentStage(c => Math.min(4, c + 1))}>
              Continue <ArrowRight size={13} />
            </button>
          ) : (
            <button className="btn-step-nav next" onClick={() => handleSaveSelection(activeSelectedDesign, true)}>
              Save & Apply <CheckCheck size={14} />
            </button>
          )}
        </div>
      </div>

      {/* ── Active Selection Banner ─────────────────────────────────────────── */}
      <section className="studio-sub-header">
        <div className="active-selection-summary">
          <div className="selection-badge-col">
            <span className="active-pill-tag">ACTIVE SELECTION</span>
            <h3 className="active-design-name">{activeSelectedDesign?.name}</h3>
            <span className="active-design-meta">
              {activeSelectedDesign?.style} • {activeSelectedDesign?.budget_tier} • {activeSelectedDesign?.category?.replace(/_/g, ' ')}
            </span>
          </div>

          <div className="selection-actions-col">
            <button
              className="btn-studio-action secondary"
              onClick={() => setCurrentStage(2)}
              title="Customize exterior colors across all 12 architectural components"
            >
              <Palette size={15} /> Customize Colors
            </button>
            <button
              className="btn-studio-action secondary"
              onClick={() => setCurrentStage(3)}
              title="Review personal 3D model and floor plan alignment"
            >
              <Layers size={15} /> 3D Preview
            </button>
            <button
              className="btn-studio-action primary"
              onClick={() => handleSaveSelection()}
              disabled={saving}
            >
              {saving ? <RefreshCw size={15} className="spin" /> : <Save size={15} />}
              <span>{savedSelection?.design_id === activeSelectedDesign?.id ? 'Saved' : 'Save Selection'}</span>
            </button>
          </div>
        </div>
      </section>

      {/* ── Main Content Area: Step 1, Step 2, Step 3, Step 4 ───────────────── */}
      <main className="exterior-studio-content">
        {/* =================================================================== */}
        {/* STEP 1: SELECT EXTERIOR IMAGE                                       */}
        {/* =================================================================== */}
        {currentStage === 1 && (
          <div className="exterior-gallery-view">
            {/* Category Filter Tabs & Sub-Filters Bar */}
            <div className="studio-filter-section">
              <div className="filter-categories-scroll">
                <button
                  className={`filter-category-pill ${selectedCategory === 'all' ? 'active' : ''}`}
                  onClick={() => setSelectedCategory('all')}
                >
                  All Designs (32)
                </button>
                {EXTERIOR_CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    className={`filter-category-pill ${selectedCategory === cat.id ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat.id)}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>

              {/* Sub-Filters: Search, Budget Tier, House Type */}
              <div className="filter-controls-row">
                <div className="search-input-wrapper">
                  <Search size={16} className="search-input-icon" />
                  <input
                    type="text"
                    className="studio-search-input"
                    placeholder="Search by architectural style, materials, keywords..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button
                      className="btn-clear-search"
                      onClick={() => setSearchQuery('')}
                      style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer' }}
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>

                <div className="filter-select-wrapper" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.85rem', color: '#9ca3af' }}>Budget:</label>
                  <select
                    className="filter-dropdown-select"
                    value={selectedBudgetTier}
                    onChange={(e) => setSelectedBudgetTier(e.target.value)}
                  >
                    {BUDGET_TIERS.map((tier) => (
                      <option key={tier} value={tier}>{tier}</option>
                    ))}
                  </select>
                </div>

                <div className="filter-select-wrapper" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label style={{ fontSize: '0.85rem', color: '#9ca3af' }}>Type:</label>
                  <select
                    className="filter-dropdown-select"
                    value={selectedHouseType}
                    onChange={(e) => setSelectedHouseType(e.target.value)}
                  >
                    {HOUSE_TYPES.map((type) => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>

                <span className="catalog-counter-text">
                  Showing <strong>{filteredCatalog.length}</strong> of 32 designs
                </span>
              </div>
            </div>

            {/* Design Grid */}
            <div className="exterior-gallery-grid">
              {filteredCatalog.map((design) => {
                const isSelected = activeSelectedDesign?.id === design.id;
                const comp = design.compatibility || { status: 'compatible', score: 95, reasons: [] };
                const isCompatible = comp.status === 'compatible';
                const isAdjustable = comp.status === 'compatible_with_adjustments';
                const isExpanded = expandedReasonsId === design.id;

                return (
                  <div
                    key={design.id}
                    className={`exterior-card exterior-design-card ${isSelected ? 'selected-card is-selected' : ''}`}
                    onClick={(e) => {
                      // Avoid double triggering if clicking nested action buttons
                      if (e.target.closest('button')) return;
                      handleSelectDesignCard(design);
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    {/* Visual Selected Badge */}
                    {isSelected && (
                      <div className="card-selected-badge">
                        <Check size={12} /> SELECTED
                      </div>
                    )}

                    {/* Card Media Preview */}
                    <div className="card-image-box">
                      <img
                        src={design.image_path || design.image_url}
                        alt={design.name}
                        loading="lazy"
                        className="card-photo"
                      />
                      <div className="card-ref-badge">{design.budget_tier}</div>
                      <div className={`card-compat-badge ${comp.status}`} style={{ position: 'absolute', bottom: '10px', right: '10px' }}>
                        {isCompatible && <CheckCircle size={12} />}
                        {isAdjustable && <AlertTriangle size={12} />}
                        <span>{comp.score}% Match</span>
                      </div>
                    </div>

                    {/* Card Body */}
                    <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px' }}>
                        <h4 style={{ margin: 0, fontSize: '1.05rem', color: '#f8fafc', fontWeight: 700 }}>{design.name}</h4>
                        <span style={{ fontSize: '0.75rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px', whiteSpace: 'nowrap' }}>{design.style}</span>
                      </div>

                      <p style={{ margin: 0, fontSize: '0.82rem', color: '#94a3b8', lineHeight: 1.45, flex: 1 }}>{design.description}</p>

                      {/* Compatibility Summary */}
                      <div style={{ background: '#1e293b', padding: '8px 12px', borderRadius: '6px' }}>
                        <div
                          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', fontSize: '0.78rem', color: isCompatible ? '#10b981' : '#f59e0b' }}
                          onClick={() => setExpandedReasonsId(isExpanded ? null : design.id)}
                        >
                          <span>{isCompatible ? 'Fully Compatible with Plot Dimensions' : 'Compatible with Minor Adjustments'}</span>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </div>

                        {isExpanded && comp.reasons && comp.reasons.length > 0 && (
                          <ul style={{ margin: '6px 0 0', paddingLeft: '16px', fontSize: '0.74rem', color: '#cbd5e1' }}>
                            {comp.reasons.map((r, i) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                        )}
                      </div>

                      {/* Card Action Buttons */}
                      <div style={{ display: 'flex', gap: '8px', marginTop: 'auto', paddingTop: '8px' }}>
                        <button
                          className={`btn ${isSelected ? 'btn-primary' : 'btn-outline'}`}
                          style={{ flex: 1, fontSize: '0.82rem', padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                          onClick={() => handleSelectDesignCard(design)}
                        >
                          {isSelected ? (
                            <>
                              <CheckCircle size={15} /> Active Selection
                            </>
                          ) : (
                            'Select Design'
                          )}
                        </button>
                        <button
                          className="btn btn-outline"
                          style={{ padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          title="Proceed to customize colors"
                          onClick={() => {
                            handleSelectDesignCard(design);
                            setShowStep1Modal(false);
                            setCurrentStage(2);
                          }}
                        >
                          <Palette size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* STEP 2: CUSTOMIZE COLORS AND LIVE 3D PREVIEW (PHASE 6G.3 WORKSPACE) */}
        {/* =================================================================== */}
        {currentStage === 2 && (
          <div className="stage2-customizer-workspace">
            {/* ── LEFT PANEL: Component Selector, Searchable Palette, Presets, Finishes, Live Summary ── */}
            <div className="stage2-controls-panel">
              {/* 1. Component Selector Bar (12 Supported Components) */}
              <div className="component-selector-container">
                <div className="component-selector-header">
                  <span className="component-selector-title">
                    <Sliders size={16} color="#38bdf8" /> Choose Architectural Component to Color (12 Components)
                  </span>
                  <button
                    className="btn-apply-all-walls"
                    onClick={handleApplyToAllWalls}
                    title="Apply the current selected component's color to Main Walls, Secondary Walls, and Front Facade"
                  >
                    <Copy size={13} /> Apply to All Exterior Walls
                  </button>
                </div>

                <div className="component-pill-grid">
                  {HOUSE_COMPONENTS.map((comp) => {
                    const isActive = activeComponentId === comp.id;
                    const hex = customColors[comp.id] || comp.defaultHex;
                    return (
                      <button
                        key={comp.id}
                        className={`component-pill ${isActive ? 'active' : ''}`}
                        onClick={() => setActiveComponentId(comp.id)}
                      >
                        <div
                          className="component-pill-swatch"
                          style={{ backgroundColor: hex }}
                        />
                        <div className="component-pill-info">
                          <span className="component-pill-name">{comp.shortName}</span>
                          <span className="component-pill-hex">{hex}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* 2. Searchable Color Palette (Search input + 10 Families + Swatches + Validated HEX) */}
              <div className="color-search-panel">
                <div className="color-search-bar-row">
                  <div className="color-search-input-wrapper">
                    <Search size={16} />
                    <input
                      type="text"
                      className="color-search-input"
                      placeholder="Search color name or enter HEX code"
                      value={colorSearchQuery}
                      onChange={(e) => setColorSearchQuery(e.target.value)}
                    />
                    {colorSearchQuery && (
                      <button
                        className="btn-clear-search"
                        style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                        onClick={() => setColorSearchQuery('')}
                      >
                        <X size={14} />
                      </button>
                    )}
                  </div>

                  <span style={{ fontSize: '0.82rem', color: '#94a3b8', whiteSpace: 'nowrap' }}>
                    Editing: <strong style={{ color: '#38bdf8' }}>{activeComponent.name}</strong>
                  </span>
                </div>

                {/* 10 Color Family Chips */}
                <div className="family-chips-bar">
                  {COLOR_FAMILIES.map((fam) => (
                    <button
                      key={fam.id}
                      className={`family-chip-btn ${selectedColorFamily === fam.id ? 'active' : ''}`}
                      onClick={() => setSelectedColorFamily(fam.id)}
                    >
                      {fam.name}
                    </button>
                  ))}
                </div>

                {/* Filtered Swatch Grid with Contrast Borders */}
                <div className="color-swatch-grid">
                  {availableSwatches.map((sw) => {
                    const isPicked = (customColors[activeComponentId] || '').toUpperCase() === sw.hex.toUpperCase();
                    return (
                      <div
                        key={sw.name}
                        className={`palette-swatch-card ${isPicked ? 'active' : ''}`}
                        onClick={() => {
                          pushHistory();
                          setCustomColors((prev) => ({
                            ...prev,
                            [activeComponentId]: sw.hex
                          }));
                        }}
                      >
                        <div className="swatch-box" style={{ backgroundColor: sw.hex }}>
                          {isPicked && <Check size={13} color={sw.hex.toLowerCase() === '#ffffff' || sw.hex.toLowerCase() === '#fffff0' ? '#000000' : '#ffffff'} />}
                        </div>
                        <div className="swatch-card-details">
                          <span className="swatch-card-name" title={sw.name}>{sw.name}</span>
                          <span className="swatch-card-hex">{sw.hex}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Custom HEX Input with Live Validation Message & Native Picker */}
                <div className="custom-hex-toolbar">
                  <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Custom HEX:</span>
                  <div className="hex-input-group">
                    <span className="hex-prefix">#</span>
                    <input
                      type="text"
                      className="hex-field"
                      placeholder="D8C3A5"
                      maxLength={7}
                      value={customHexInput.replace('#', '')}
                      onChange={(e) => {
                        setCustomHexInput(e.target.value);
                        setHexInputTouched(true);
                      }}
                    />
                    {isHexValid && <Check size={14} color="#10b981" />}
                  </div>
                  <button
                    className="btn-apply-hex"
                    disabled={!isHexValid}
                    onClick={handleApplyHex}
                  >
                    Apply Hex
                  </button>

                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginLeft: 'auto' }}>
                    <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>Color Picker:</span>
                    <input
                      type="color"
                      className="custom-color-input"
                      value={customColors[activeComponentId] || '#F4F4F0'}
                      onChange={(e) => {
                        pushHistory();
                        setCustomColors((prev) => ({
                          ...prev,
                          [activeComponentId]: e.target.value
                        }));
                      }}
                      title="Choose custom color from palette wheel"
                    />
                  </div>
                </div>

                {/* Understandable Validation Message */}
                {hexInputTouched && customHexInput.trim().length > 0 && (
                  <div className={`hex-validation-message ${isHexValid ? 'valid' : 'invalid'}`}>
                    {isHexValid
                      ? `Valid HEX code #${customHexInput.replace('#', '').toUpperCase()}`
                      : 'Please enter a valid 3 or 6 digit HEX code (e.g., #D8C3A5 or #FFF).'}
                  </div>
                )}
              </div>

              {/* 3. Color Presets: 9 Curated Combinations */}
              <div className="presets-section-container">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Sparkles size={16} color="#f59e0b" /> Curated Architectural Schemes (9 Multi-Color Presets)
                  </h4>
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Clicking a preset applies all 12 components harmoniously</span>
                </div>

                <div className="presets-grid">
                  {COLOR_PRESETS.map((preset) => (
                    <div
                      key={preset.id}
                      className="preset-card"
                      onClick={() => handleApplyPreset(preset)}
                      title={`Apply ${preset.name} multi-color palette`}
                    >
                      <div className="preset-card-header">
                        <span className="preset-name">{preset.name}</span>
                        <div className="preset-color-strip">
                          <div className="preset-color-slice" style={{ backgroundColor: preset.colors.primary_wall }} />
                          <div className="preset-color-slice" style={{ backgroundColor: preset.colors.accent_wall }} />
                          <div className="preset-color-slice" style={{ backgroundColor: preset.colors.door }} />
                          <div className="preset-color-slice" style={{ backgroundColor: preset.colors.window_frame }} />
                        </div>
                      </div>
                      <p className="preset-description">{preset.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 4. Material Finishes Specification */}
              <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                  Material Finish & Architectural Cladding
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Wall Finish Specification</label>
                    <select
                      className="sidebar-select"
                      value={customMaterials.finish_type}
                      onChange={(e) => {
                        pushHistory();
                        setCustomMaterials((m) => ({ ...m, finish_type: e.target.value }));
                      }}
                    >
                      {MATERIAL_FINISH_TYPES.map((f) => (
                        <option key={f.id} value={f.id}>{f.name} {f.rateDiff > 0 ? `(+₹${f.rateDiff}/sq ft)` : '(Civil Baseline)'}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.78rem', color: '#94a3b8', display: 'block', marginBottom: '6px' }}>Feature Cladding / Louvers</label>
                    <select
                      className="sidebar-select"
                      value={customMaterials.cladding_type}
                      onChange={(e) => {
                        pushHistory();
                        setCustomMaterials((m) => ({ ...m, cladding_type: e.target.value }));
                      }}
                    >
                      {CLADDING_OPTIONS.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* 5. Current Customization Summary (Live 12-Component Table) */}
              <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Sliders size={15} color="#38bdf8" /> Current Customization Summary (12 Components)
                </span>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Click any element row to select it for editing</span>

                <div className="stage2-summary-table">
                  {HOUSE_COMPONENTS.map((comp) => {
                    const isEditing = activeComponentId === comp.id;
                    const hex = customColors[comp.id] || comp.defaultHex;
                    return (
                      <div
                        key={comp.id}
                        className={`stage2-table-row ${isEditing ? 'active' : ''}`}
                        onClick={() => setActiveComponentId(comp.id)}
                        title={`Click to edit ${comp.name}`}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden' }}>
                          <div
                            style={{
                              width: '14px',
                              height: '14px',
                              borderRadius: '50%',
                              backgroundColor: hex,
                              border: '1px solid rgba(255, 255, 255, 0.4)',
                              flexShrink: 0
                            }}
                          />
                          <span style={{ color: isEditing ? '#38bdf8' : '#e2e8f0', fontWeight: isEditing ? 700 : 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {comp.name}
                          </span>
                        </div>
                        <span style={{ fontFamily: 'monospace', color: '#94a3b8', fontSize: '0.72rem' }}>{hex}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 6. Working Controls: Undo, Reset Colors, Restore Defaults, Cancel Changes */}
              <div style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f8fafc' }}>Customization History & Actions</span>
                <div className="stage2-actions-toolbar">
                  <button
                    className="btn-ctrl-action"
                    onClick={handleUndo}
                    disabled={colorHistory.length === 0}
                    title="Undo last unsaved color or material change"
                  >
                    <Undo size={14} /> Undo ({colorHistory.length})
                  </button>

                  <button
                    className="btn-ctrl-action"
                    onClick={handleResetColors}
                    title="Reset colors to factory defaults of this exterior design"
                  >
                    <RotateCcw size={14} /> Reset Colors
                  </button>

                  <button
                    className="btn-ctrl-action"
                    onClick={handleRestoreDefaults}
                    title="Restore factory default colors and materials"
                  >
                    <RefreshCw size={14} /> Restore Defaults
                  </button>

                  <button
                    className="btn-ctrl-action"
                    onClick={handleCancelChanges}
                    title="Cancel unsaved changes and revert to project saved state"
                  >
                    <X size={14} /> Cancel Changes
                  </button>
                </div>
              </div>

              {/* 7. Incremental Cost Breakdown Card */}
              <div className="cost-breakdown-card" style={{ margin: 0 }}>
                <div className="cost-header-row">
                  <span className="cost-title">Incremental Elevation Upgrade</span>
                  <span className="cost-val">₹{totalExteriorCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="cost-note">
                  Covers premium surface acrylics, feature louvers, and architectural lighting over the Phase 6D civil baseline (zero double counting).
                </div>
              </div>
            </div>

            {/* ── RIGHT PANEL: Visualization Switcher Workspace (2D Elevation / 3D Preview / Reference Photo) ── */}
            <div className="stage2-preview-panel">
              <div className="stage2-preview-sticky-card">
                {/* Visualization Switcher Segmented Tabs */}
                <div className="exterior-view-switcher-tabs">
                  <button
                    className={`exterior-view-tab-btn ${stage2ViewMode === '3d' ? 'is-active' : ''}`}
                    onClick={() => setStage2ViewMode('3d')}
                  >
                    <Box size={14} />
                    <span>Personalized 3D Preview</span>
                  </button>
                  <button
                    className={`exterior-view-tab-btn ${stage2ViewMode === 'elevation' ? 'is-active' : ''}`}
                    onClick={() => setStage2ViewMode('elevation')}
                  >
                    <Compass size={14} />
                    <span>Personalized 2D Architectural Elevation</span>
                  </button>
                  <button
                    className={`exterior-view-tab-btn ${stage2ViewMode === 'reference' ? 'is-active' : ''}`}
                    onClick={() => setStage2ViewMode('reference')}
                  >
                    <Sparkles size={14} />
                    <span>Architectural Reference Image</span>
                  </button>
                </div>

                {/* Viewport content according to selected tab */}
                {stage2ViewMode === '3d' && (
                  <>
                    <div className="stage2-viewer-header-badge">
                      <div className="live-badge-dot" />
                      <span>LIVE 3D EXTERIOR PREVIEW — INTERACTIVE ORBIT</span>
                      <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: '#94a3b8' }}>
                        {plotW}′ × {plotL}′ • {facing} Facing
                      </span>
                    </div>

                    <div className="stage2-viewer-canvas-box">
                      <React.Suspense fallback={<div className="p-8 text-center text-muted" style={{ padding: '2rem', textAlign: 'center', color: '#94a3b8' }}>Loading 3D preview...</div>}>
                        <Exterior3DViewer
                          project={project}
                          selectedDesign={activeSelectedDesign}
                          customColors={customColors}
                          customMaterials={customMaterials}
                          lightingMode={activeLightingMode}
                          onToggleLighting={setActiveLightingMode}
                        />
                      </React.Suspense>
                    </div>
                  </>
                )}

                {stage2ViewMode === 'elevation' && (
                  <ExteriorBlueprintViewer
                    project={project}
                    selectedDesign={activeSelectedDesign}
                    customColors={customColors}
                    customMaterials={customMaterials}
                    lightingMode={activeLightingMode}
                    height="530px"
                    showToolbar={true}
                  />
                )}

                {stage2ViewMode === 'reference' && (
                  <div className="workspace-reference-container">
                    <div className="workspace-reference-photo-box">
                      <img
                        src={activeSelectedDesign?.image_path || activeSelectedDesign?.image_url}
                        alt={activeSelectedDesign?.name}
                        className="workspace-reference-photo"
                      />
                      <div className="comparison-label-badge">ARCHITECTURAL INSPIRATION</div>
                    </div>
                    <div className="workspace-reference-meta">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h4 style={{ margin: 0, fontSize: '1rem', color: '#f8fafc', fontWeight: 700 }}>
                          {activeSelectedDesign?.name}
                        </h4>
                        <span style={{ fontSize: '0.74rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                          {activeSelectedDesign?.category?.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.45 }}>
                        {activeSelectedDesign?.description}
                      </p>
                      <div className="rule-guarantee-note" style={{ margin: '8px 0 0' }}>
                        <Info size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
                        <span>
                          <strong>Styling Reference:</strong> Colors and finishes you select in the left panel update both the <strong>2D Architectural Elevation</strong> and the <strong>Personalized 3D House Preview</strong> in real time.
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Card Footer: Reference Image Thumbnail & Navigation Actions */}
                <div className="stage2-preview-footer">
                  <div className="stage2-ref-mini-box">
                    <img
                      src={activeSelectedDesign?.image_path || activeSelectedDesign?.image_url}
                      alt={activeSelectedDesign?.name}
                      className="stage2-ref-thumb"
                    />
                    <div>
                      <span className="ref-mini-title">{activeSelectedDesign?.name}</span>
                      <span className="ref-mini-sub">
                        {activeSelectedDesign?.category?.replace(/_/g, ' ')} • {activeSelectedDesign?.style}
                      </span>
                    </div>
                  </div>

                  <div className="stage2-footer-nav-btns">
                    <button
                      className="btn btn-outline"
                      onClick={() => setCurrentStage(1)}
                      style={{ fontSize: '0.8rem', padding: '0.45rem 0.8rem' }}
                    >
                      <ArrowLeft size={14} /> Back
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={() => setCurrentStage(3)}
                      style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem' }}
                    >
                      <span>Continue to Plan & 3D Review</span>
                      <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* STEP 3: PREVIEW PERSONALIZED 3D HOUSE                                */}
        {/* =================================================================== */}
        {currentStage === 3 && (
          <div className="stage3-dedicated-layout">
            {/* Top: Visualization Switcher Workspace Tabs */}
            <div className="exterior-view-switcher-tabs" style={{ borderRadius: '12px 12px 0 0', background: '#0d1527', border: '1px solid #1e293b', borderBottom: 'none' }}>
              <button
                className={`exterior-view-tab-btn ${stage3ViewMode === 'elevation' ? 'is-active' : ''}`}
                onClick={() => setStage3ViewMode('elevation')}
              >
                <Compass size={15} />
                <span>Personalized 2D Architectural Elevation</span>
              </button>
              <button
                className={`exterior-view-tab-btn ${stage3ViewMode === '3d' ? 'is-active' : ''}`}
                onClick={() => setStage3ViewMode('3d')}
              >
                <Box size={15} />
                <span>Personalized 3D House Preview</span>
              </button>
              <button
                className={`exterior-view-tab-btn ${stage3ViewMode === 'reference' ? 'is-active' : ''}`}
                onClick={() => setStage3ViewMode('reference')}
              >
                <Sparkles size={15} />
                <span>Architectural Reference Image</span>
              </button>
              <button
                className={`exterior-view-tab-btn ${stage3ViewMode === 'split' ? 'is-active' : ''}`}
                onClick={() => setStage3ViewMode('split')}
              >
                <Split size={15} />
                <span>Split Comparison View</span>
              </button>
            </div>

            {/* Mode 1: Full-Width Dedicated 2D Architectural Elevation Drafting */}
            {stage3ViewMode === 'elevation' && (
              <div style={{ borderRadius: '0 0 12px 12px', overflow: 'hidden' }}>
                <ExteriorBlueprintViewer
                  project={project}
                  selectedDesign={activeSelectedDesign}
                  customColors={customColors}
                  customMaterials={customMaterials}
                  lightingMode={activeLightingMode}
                  height="600px"
                  showToolbar={true}
                />
              </div>
            )}

            {/* Mode 2: Full-Width Dedicated 3D House Preview */}
            {stage3ViewMode === '3d' && (
              <div
                className="stage3-viewer-side-card"
                style={{ height: '620px', borderRadius: '0 0 12px 12px', border: '1px solid #1e293b', position: 'relative' }}
              >
                <div className="comparison-label-badge" style={{ zIndex: 12 }}>
                  PERSONALIZED 3D HOUSE PREVIEW — INTERACTIVE ORBIT
                </div>
                <React.Suspense fallback={<div className="p-8 text-center text-muted" style={{ padding: '4rem', textAlign: 'center', color: '#94a3b8' }}>Loading interactive 3D viewer...</div>}>
                  <Exterior3DViewer
                    project={project}
                    selectedDesign={activeSelectedDesign}
                    customColors={customColors}
                    customMaterials={customMaterials}
                    lightingMode={activeLightingMode}
                    onToggleLighting={setActiveLightingMode}
                  />
                </React.Suspense>
              </div>
            )}

            {/* Mode 3: Architectural Reference Image */}
            {stage3ViewMode === 'reference' && (
              <div className="workspace-reference-container" style={{ borderRadius: '0 0 12px 12px' }}>
                <div className="workspace-reference-photo-box" style={{ maxHeight: '480px' }}>
                  <img
                    src={activeSelectedDesign?.image_path || activeSelectedDesign?.image_url}
                    alt={activeSelectedDesign?.name}
                    className="workspace-reference-photo"
                  />
                  <div className="comparison-label-badge">ARCHITECTURAL REFERENCE</div>
                </div>
                <div className="workspace-reference-meta">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h4 style={{ margin: 0, fontSize: '1.1rem', color: '#f8fafc', fontWeight: 700 }}>
                      {activeSelectedDesign?.name}
                    </h4>
                    <span style={{ fontSize: '0.78rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
                      {activeSelectedDesign?.category?.replace(/_/g, ' ')} • {activeSelectedDesign?.style}
                    </span>
                  </div>
                  <p style={{ margin: '4px 0 0', fontSize: '0.84rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                    {activeSelectedDesign?.description}
                  </p>
                  <div className="rule-guarantee-note" style={{ margin: '8px 0 0' }}>
                    <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>
                      <strong>Styling & Proportion Inspiration:</strong> This reference photograph served as the architectural benchmark.
                      Your customized palette and materials are faithfully adapted to the {plotW}′ × {plotL}′ plot dimensions in both the 2D Elevation and 3D Model.
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Mode 4: Split Comparison Row (Reference / 2D Elevation vs 3D House Preview) */}
            {stage3ViewMode === 'split' && (
              <div className="stage3-comparison-row" style={{ marginTop: 0 }}>
                {/* Left Column: Reference Image OR 2D Elevation */}
                <div className="stage3-ref-side-card" style={{ borderRadius: '0 0 0 12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div className="elevation-segmented-pills">
                      <button
                        className={`elevation-pill-btn ${splitLeftMode === 'reference' ? 'is-active' : ''}`}
                        onClick={() => setSplitLeftMode('reference')}
                      >
                        <ImageIcon size={12} style={{ marginRight: '4px' }} /> Reference Photo
                      </button>
                      <button
                        className={`elevation-pill-btn ${splitLeftMode === 'elevation' ? 'is-active' : ''}`}
                        onClick={() => setSplitLeftMode('elevation')}
                      >
                        <Compass size={12} style={{ marginRight: '4px' }} /> 2D Elevation
                      </button>
                    </div>
                    <span style={{ fontSize: '0.72rem', color: '#38bdf8' }}>Comparison Left</span>
                  </div>

                  {splitLeftMode === 'reference' ? (
                    <>
                      <div className="stage3-ref-photo-wrap">
                        <img
                          src={activeSelectedDesign?.image_path || activeSelectedDesign?.image_url}
                          alt={activeSelectedDesign?.name}
                          className="stage3-ref-photo"
                        />
                        <div className="comparison-label-badge">ARCHITECTURAL REFERENCE</div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '8px' }}>
                        <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>{activeSelectedDesign?.name}</span>
                        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>{activeSelectedDesign?.style} • {activeSelectedDesign?.category?.replace(/_/g, ' ')}</span>
                        <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#cbd5e1', lineHeight: 1.4 }}>
                          {activeSelectedDesign?.description}
                        </p>
                      </div>
                    </>
                  ) : (
                    <div style={{ flex: 1, minHeight: '380px', display: 'flex', flexDirection: 'column' }}>
                      <ExteriorBlueprintViewer
                        project={project}
                        selectedDesign={activeSelectedDesign}
                        customColors={customColors}
                        customMaterials={customMaterials}
                        lightingMode={activeLightingMode}
                        height="380px"
                        showToolbar={false}
                      />
                    </div>
                  )}

                  <div className="rule-guarantee-note" style={{ marginTop: 'auto' }}>
                    <Info size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span>
                      <strong>Architectural Note:</strong> Compare your selected inspiration directly alongside the personalized interactive 3D model.
                    </span>
                  </div>
                </div>

                {/* Right Column: Personalized 3D House Preview */}
                <div className="stage3-viewer-side-card" style={{ borderRadius: '0 0 12px 0' }}>
                  <div className="comparison-label-badge" style={{ zIndex: 12 }}>
                    PERSONALIZED 3D HOUSE PREVIEW
                  </div>
                  <React.Suspense fallback={<div className="p-8 text-center text-muted" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>Loading 3D preview...</div>}>
                    <Exterior3DViewer
                      project={project}
                      selectedDesign={activeSelectedDesign}
                      customColors={customColors}
                      customMaterials={customMaterials}
                      lightingMode={activeLightingMode}
                      onToggleLighting={setActiveLightingMode}
                    />
                  </React.Suspense>
                </div>
              </div>
            )}

            {/* Bottom Row: Compact Floor Plan Summary & Compatibility Verification */}
            <div className="stage3-plan-summary-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={18} color="#10b981" /> Project Geometry & Floor Plan Verification
                </span>
                <span className="checklist-score-badge compatible">
                  <CheckCircle size={14} /> 95% Compatibility Match
                </span>
              </div>

              {/* Compact Plan Summary Grid */}
              <div className="plan-summary-grid">
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Plot Dimensions</span>
                  <span className="plan-summary-value">{plotW}′-0″ × {plotL}′-0″</span>
                </div>
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Orientation</span>
                  <span className="plan-summary-value">{facing} Facing</span>
                </div>
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Floor Levels</span>
                  <span className="plan-summary-value">{floors > 1 ? `G + ${floors - 1} Levels` : 'Ground Level'}</span>
                </div>
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Ground Floor Plan</span>
                  <span className="plan-summary-value" style={{ color: '#10b981' }}>Approved & Available</span>
                </div>
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Upper Floor Plan</span>
                  <span className="plan-summary-value" style={{ color: floors > 1 ? '#10b981' : '#94a3b8' }}>
                    {floors > 1 ? 'Approved & Available' : 'N/A (Single Floor)'}
                  </span>
                </div>
                <div className="plan-summary-item">
                  <span className="plan-summary-label">Source of Truth</span>
                  <span className="plan-summary-value" style={{ color: '#38bdf8' }}>Project Engine</span>
                </div>
              </div>

              {/* Strict Rule: Never Silently Alter Approved Floor Plans */}
              <div className="rule-guarantee-note">
                <Info size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>
                  <strong>Plan Protection Guarantee:</strong> Selecting an exterior design enhances visual styling and finishes
                  <strong> without modifying or replacing your approved floor-plan geometry</strong>.
                </span>
              </div>

              {/* Blueprint Toggle & Regeneration Action */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                <button
                  className="btn btn-outline"
                  style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem' }}
                  onClick={() => setShowCadView(!showCadView)}
                >
                  <Maximize2 size={14} /> {showCadView ? 'Hide Interior Floor Plan' : 'View Interior Floor Plan & CAD Layout'}
                </button>

                <button
                  className="btn btn-outline"
                  style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem', color: '#f59e0b', borderColor: '#f59e0b' }}
                  onClick={() => setShowRegenModal(true)}
                >
                  <RefreshCw size={14} /> Request Floor Plan Regeneration...
                </button>
              </div>

              {/* Optional Blueprint Viewport */}
              {showCadView && (
                <div
                  className="stage3-blueprint-container"
                  style={{
                    marginTop: '14px',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    border: '1px solid #334155',
                    background: '#0f172a',
                    boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)'
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '10px 16px',
                      background: '#1e293b',
                      borderBottom: '1px solid #334155',
                      flexWrap: 'wrap',
                      gap: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Layers size={16} color="#38bdf8" />
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc' }}>
                        Architectural Floor Plan CAD Working Drawing (Interior Rooms & Partitions)
                      </span>
                      <span
                        style={{
                          fontSize: '0.72rem',
                          background: '#0369a1',
                          color: '#e0f2fe',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontWeight: 600
                        }}
                      >
                        {plotW}′ × {plotL}′ • {facing} Facing • G+{floors > 1 ? floors - 1 : 0}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                      Drag to Pan • Wheel to Zoom • Level tabs above • Internal Room Dimensions
                    </span>
                  </div>
                  <div style={{ height: '520px', position: 'relative' }}>
                    <FloorPlanViewer
                      layoutData={floorPlanLayout}
                      plotWidth={plotW}
                      plotLength={plotL}
                      project={project}
                      loading={loadingFloorPlan}
                      loadingMessage="Loading architectural CAD blueprint..."
                    />
                  </div>
                </div>
              )}

              {/* Required Navigation Buttons */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  paddingTop: '16px',
                  marginTop: '12px',
                  borderTop: '1px solid #1f2937'
                }}
              >
                <button className="btn btn-outline" onClick={() => setCurrentStage(2)}>
                  <ArrowLeft size={16} /> Back to Customization
                </button>
                <button className="btn btn-primary" onClick={() => setCurrentStage(4)}>
                  <span>Save & Apply Exterior</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* =================================================================== */}
        {/* STEP 4: SAVE & APPLY EXTERIOR DESIGN                                */}
        {/* =================================================================== */}
        {currentStage === 4 && (
          <div className="stage4-review-container">
            <div className="stage4-summary-card">
              {/* Selected Elevation Header */}
              <div className="summary-hero-row">
                <img
                  src={activeSelectedDesign?.image_path || activeSelectedDesign?.image_url}
                  alt={activeSelectedDesign?.name}
                  className="summary-thumbnail"
                />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <span className="active-pill-tag">APPROVED EXTERIOR DESIGN</span>
                  <h3 style={{ margin: 0, fontSize: '1.3rem', color: '#f8fafc', fontWeight: 700 }}>
                    {activeSelectedDesign?.name}
                  </h3>
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                    {activeSelectedDesign?.style} • {activeSelectedDesign?.category?.replace(/_/g, ' ')} • {activeSelectedDesign?.budget_tier} Tier
                  </span>
                  <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: '#cbd5e1', maxWidth: '600px' }}>
                    {activeSelectedDesign?.description}
                  </p>
                </div>
              </div>

              {/* Applied Component Colors Grid (12 Items) */}
              <div>
                <h4 style={{ margin: '0 0 10px', fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc' }}>
                  Applied Component Colors (12 Architectural Elements)
                </h4>
                <div className="summary-colors-grid">
                  {HOUSE_COMPONENTS.map((comp) => {
                    const hex = customColors[comp.id] || comp.defaultHex;
                    return (
                      <div key={comp.id} className="summary-color-item">
                        <div
                          style={{
                            width: '20px',
                            height: '20px',
                            borderRadius: '50%',
                            backgroundColor: hex,
                            border: '1.5px solid rgba(255, 255, 255, 0.4)',
                            flexShrink: 0
                          }}
                        />
                        <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#f1f5f9' }}>{comp.shortName}</span>
                          <span style={{ fontSize: '0.7rem', color: '#94a3b8', fontFamily: 'monospace' }}>{hex}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Material Finishes & Cladding */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Wall Finish Specification</span>
                  <p style={{ margin: '4px 0 0', fontSize: '0.9rem', color: '#f1f5f9', fontWeight: 600 }}>
                    {MATERIAL_FINISH_TYPES.find((f) => f.id === customMaterials.finish_type)?.name || 'Matte Weatherproof Paint'}
                  </p>
                </div>
                <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '8px', border: '1px solid #334155' }}>
                  <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Architectural Cladding / Screens</span>
                  <p style={{ margin: '4px 0 0', fontSize: '0.9rem', color: '#f1f5f9', fontWeight: 600 }}>
                    {CLADDING_OPTIONS.find((c) => c.id === customMaterials.cladding_type)?.name || 'None'}
                  </p>
                </div>
              </div>

              {/* Incremental Cost Breakdown with Zero Double Counting Guarantee */}
              <div className="cost-breakdown-card">
                <div className="cost-header-row">
                  <span className="cost-title">Total Incremental Exterior Upgrade</span>
                  <span className="cost-val">₹{totalExteriorCost.toLocaleString('en-IN')}</span>
                </div>
                <div className="cost-note">
                  <strong>Civil Baseline Protection:</strong> Baseline RCC structural framing, external masonry, and standard sand-cement plaster
                  are already accounted for in the Phase 6D civil construction cost estimate.
                  This exterior package represents <strong>only the aesthetic surface upgrades</strong>, premium silicone acrylic finishes,
                  designer entrance portal, and architectural facade lighting (zero double counting).
                </div>
              </div>

              {/* Final Actions Bar */}
              <div className="summary-actions-bar">
                <button className="btn btn-outline" onClick={() => setCurrentStage(2)}>
                  <Palette size={15} /> Modify Colors
                </button>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button
                    className="btn btn-outline"
                    onClick={() => handleSaveSelection(activeSelectedDesign, false)}
                    disabled={saving}
                  >
                    {saving ? <RefreshCw size={15} className="spin" /> : <Save size={15} />}
                    <span>Save Changes</span>
                  </button>

                  <button
                    className="btn btn-primary"
                    onClick={() => handleSaveSelection(activeSelectedDesign, true)}
                    disabled={saving}
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '0.65rem 1.35rem', fontWeight: 600, background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)' }}
                  >
                    <CheckCheck size={16} />
                    <span>Save & Proceed to 3D View →</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ── Step 1: Design Selected Confirmation Modal ────────────────────── */}
      {showStep1Modal && currentStage === 1 && activeSelectedDesign && (
        <div className="step1-selection-modal-backdrop">
          <div className="step1-selection-modal">
            <div className="step1-modal-header">
              <div>
                <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle size={16} color="#10b981" /> Architectural Reference Selected
                </span>
                <div className="modal-step-indicator" style={{ display: 'flex', gap: '6px', alignItems: 'center', marginTop: '4px', fontSize: '0.74rem', color: '#94a3b8' }}>
                  <span className="wizard-step current" style={{ color: '#38bdf8', fontWeight: 700 }}>1 Design</span>
                  <span>→</span>
                  <span className="wizard-step">2 Customize</span>
                  <span>→</span>
                  <span className="wizard-step">3 3D Preview</span>
                  <span>→</span>
                  <span className="wizard-step">4 Save</span>
                </div>
              </div>
              <button
                onClick={() => setShowStep1Modal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="step1-modal-body">
              <img
                src={activeSelectedDesign.image_path || activeSelectedDesign.image_url}
                alt={activeSelectedDesign.name}
                className="step1-modal-img"
              />

              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <span className="active-pill-tag">{activeSelectedDesign.category?.replace(/_/g, ' ')}</span>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#f8fafc', fontWeight: 700 }}>
                  {activeSelectedDesign.name}
                </h3>
                <span style={{ fontSize: '0.82rem', color: '#cbd5e1' }}>
                  Style: <strong>{activeSelectedDesign.style}</strong> • {activeSelectedDesign.budget_tier} Tier
                </span>

                <div style={{ background: '#0f172a', padding: '10px 12px', borderRadius: '8px', border: '1px solid #1e293b', marginTop: '4px' }}>
                  <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Project Configuration</span>
                  <div style={{ display: 'flex', gap: '8px', marginTop: '6px', flexWrap: 'wrap' }}>
                    <span className="config-badge" style={{ background: '#1e293b', color: '#38bdf8', padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600 }}>
                      {plotW} × {plotL} ft
                    </span>
                    <span className="config-badge" style={{ background: '#1e293b', color: '#38bdf8', padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600 }}>
                      G+{floors - 1}
                    </span>
                    <span className="config-badge" style={{ background: '#1e293b', color: '#38bdf8', padding: '3px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600 }}>
                      {facing ? `${facing.charAt(0).toUpperCase() + facing.slice(1)} Facing` : 'South Facing'}
                    </span>
                  </div>
                </div>

                <p style={{ margin: '4px 0 0', fontSize: '0.78rem', color: '#94a3b8', lineHeight: 1.4 }}>
                  This selected architectural reference provides inspiration for your building's massing, facade reveals, and finish palettes.
                </p>
              </div>
            </div>

            <div className="step1-modal-footer">
              <button className="btn btn-outline" onClick={() => setShowStep1Modal(false)}>
                Back to Gallery
              </button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  setShowStep1Modal(false);
                  setCurrentStage(2);
                }}
              >
                <span>Continue to Customize</span>
                <ArrowRight size={15} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Floor Plan Regeneration Confirmation Modal ────────────────────── */}
      {showRegenModal && (
        <div className="modal-overlay-backdrop">
          <div className="modal-dialog-box">
            <div className="modal-header-row">
              <AlertTriangle size={24} />
              <h3 className="modal-title">Regenerate Floor Plan?</h3>
            </div>
            <p className="modal-body-text">
              Regenerating your floor plan will recalculate the entire internal room layout and reset room positions.
              <br /><br />
              <strong>Selecting an exterior design does NOT require plan regeneration</strong>, as this exterior option is already physically compatible with your plot dimensions.
            </p>
            <div className="modal-actions-row" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" onClick={() => setShowRegenModal(false)}>
                Keep Existing Floor Plan
              </button>
              <button
                className="btn btn-outline"
                style={{ borderColor: '#38bdf8', color: '#38bdf8' }}
                onClick={() => {
                  const canonical = generateCanonicalFloorPlan(project || {
                    id: projectId,
                    plot_width: plotW,
                    plot_length: plotL,
                    facing: facing,
                    floors: floors
                  });
                  setFloorPlanLayout(canonical);
                  try {
                    localStorage.setItem(`floorplan_${projectId}`, JSON.stringify(canonical));
                  } catch (_) {}
                  setShowRegenModal(false);
                }}
              >
                <Sparkles size={14} /> Re-sync Canonical Blueprint
              </button>
              <button
                className="btn btn-primary"
                style={{ background: '#dc2626', borderColor: '#dc2626' }}
                onClick={() => {
                  setShowRegenModal(false);
                  navigate(`/projects/${projectId}/planner`);
                }}
              >
                Proceed to Planner
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
