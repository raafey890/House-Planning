/**
 * Exterior Color & Material Catalog — Phase 6G.1
 * 
 * Provides:
 * - 12 customizable exterior house components
 * - 10 color families with 70+ authentic architectural paint and finish shades
 * - 9 curated multi-color architectural schemes / presets
 * - Material finish options with live Three.js properties & cost rates
 * - Search & validation utilities
 */

export const HOUSE_COMPONENTS = [
  {
    id: 'primary_wall',
    name: 'Main Exterior Walls',
    shortName: 'Main Walls',
    description: 'Primary perimeter exterior walls and main building mass',
    defaultHex: '#F4F4F0',
    category: 'walls'
  },
  {
    id: 'secondary_wall',
    name: 'Secondary Walls',
    shortName: 'Secondary',
    description: 'Recessed volume blocks, side elevations, and rear walls',
    defaultHex: '#E5E7EB',
    category: 'walls'
  },
  {
    id: 'accent_wall',
    name: 'Accent & Feature Walls',
    shortName: 'Accent Walls',
    description: 'Cantilevered boxes, cladding panels, and vertical facade elements',
    defaultHex: '#2B313B',
    category: 'walls'
  },
  {
    id: 'front_facade',
    name: 'Front Facade Feature',
    shortName: 'Front Facade',
    description: 'Entrance portal framing, architrave band, and front facade reveals',
    defaultHex: '#F4F4F0',
    category: 'facade'
  },
  {
    id: 'boundary_wall',
    name: 'Boundary Wall',
    shortName: 'Boundary Wall',
    description: 'Compound perimeter walling and gate pillars',
    defaultHex: '#E5E0D6',
    category: 'site'
  },
  {
    id: 'boundary_gate',
    name: 'Boundary Gate',
    shortName: 'Front Gate',
    description: 'Sliding or swing vehicular and pedestrian gate',
    defaultHex: '#30343B',
    category: 'site'
  },
  {
    id: 'door',
    name: 'Entrance Door',
    shortName: 'Entrance Door',
    description: 'Main grand entrance portal and pivot door',
    defaultHex: '#8B5A2B',
    category: 'fenestration'
  },
  {
    id: 'window_frame',
    name: 'Window Frames',
    shortName: 'Window Frames',
    description: 'Powder-coated aluminum/UPVC frames, mullions, and external sills',
    defaultHex: '#20252B',
    category: 'fenestration'
  },
  {
    id: 'window_glass_tint',
    name: 'Window Glass Tint',
    shortName: 'Glass Tint',
    description: 'Glazing tint and solar control reflective pane tone',
    defaultHex: '#7DD3FC',
    category: 'fenestration'
  },
  {
    id: 'railing',
    name: 'Balcony Railings',
    shortName: 'Railings',
    description: 'Upper terrace balustrades, glass channels, and metal railings',
    defaultHex: '#1F2937',
    category: 'accents'
  },
  {
    id: 'roof_parapet',
    name: 'Roof & Parapet Finish',
    shortName: 'Roof & Parapet',
    description: 'Terrace coping band, roof fascia, and parapet trims',
    defaultHex: '#343A40',
    category: 'roof'
  },
  {
    id: 'exterior_trims',
    name: 'Exterior Trims & Pergola',
    shortName: 'Trims & Pergola',
    description: 'Portico canopy, rooftop pergola, support columns, and louvers',
    defaultHex: '#20252B',
    category: 'accents'
  }
];

export const COLOR_FAMILIES = [
  { id: 'all', name: 'All Colors' },
  { id: 'whites_creams', name: 'Whites & Creams' },
  { id: 'beiges_earth', name: 'Beiges & Earth' },
  { id: 'greys_charcoals', name: 'Greys & Charcoals' },
  { id: 'browns_wood', name: 'Browns & Wood' },
  { id: 'reds_terracotta', name: 'Reds & Terracotta' },
  { id: 'blues', name: 'Blues' },
  { id: 'greens', name: 'Greens' },
  { id: 'black_dark', name: 'Black & Dark' },
  { id: 'gold_metallic', name: 'Gold & Metallic' },
  { id: 'custom', name: 'Custom Colors' }
];

export const COLOR_CATALOG = [
  // ── Whites & Creams ────────────────────────────────────────────────────────
  { name: 'Pure White', hex: '#FFFFFF', family: 'whites_creams', tags: ['white', 'clean', 'modern', 'minimal'] },
  { name: 'Bone White', hex: '#F4F4F0', family: 'whites_creams', tags: ['white', 'bone', 'soft', 'stucco'] },
  { name: 'Ivory', hex: '#FFFFF0', family: 'whites_creams', tags: ['ivory', 'warm', 'classic', 'cream'] },
  { name: 'Pearl White', hex: '#F8F6F0', family: 'whites_creams', tags: ['pearl', 'white', 'luxurious'] },
  { name: 'Cream', hex: '#FFFDD0', family: 'whites_creams', tags: ['cream', 'warm', 'traditional'] },
  { name: 'Alabaster', hex: '#F2F0EB', family: 'whites_creams', tags: ['alabaster', 'warm white', 'subtle'] },
  { name: 'Chalk White', hex: '#F7F7F7', family: 'whites_creams', tags: ['chalk', 'neutral', 'matte'] },
  { name: 'Nordic Linen', hex: '#EAE6DF', family: 'whites_creams', tags: ['linen', 'nordic', 'scandinavian'] },

  // ── Beiges & Earth Tones ───────────────────────────────────────────────────
  { name: 'Classic Beige', hex: '#F5F5DC', family: 'beiges_earth', tags: ['beige', 'neutral', 'stone'] },
  { name: 'Sandstone', hex: '#D8C3A5', family: 'beiges_earth', tags: ['sandstone', 'dholpur', 'warm', 'desert'] },
  { name: 'Warm Travertine', hex: '#E6D7C3', family: 'beiges_earth', tags: ['travertine', 'roman', 'marble', 'luxury'] },
  { name: 'Desert Sand', hex: '#EDC9AF', family: 'beiges_earth', tags: ['desert', 'sand', 'warm', 'clay'] },
  { name: 'Khaki Plaster', hex: '#C3B091', family: 'beiges_earth', tags: ['khaki', 'earth', 'matte'] },
  { name: 'Limestone Cream', hex: '#EBE6DD', family: 'beiges_earth', tags: ['limestone', 'cream', 'mineral'] },
  { name: 'Biscotti', hex: '#E2D4B7', family: 'beiges_earth', tags: ['biscotti', 'warm beige', 'mediterranean'] },
  { name: 'Wheat Pale', hex: '#F5DEB3', family: 'beiges_earth', tags: ['wheat', 'golden', 'sunlit'] },

  // ── Greys & Charcoals ──────────────────────────────────────────────────────
  { name: 'Warm Grey', hex: '#808080', family: 'greys_charcoals', tags: ['grey', 'gray', 'neutral', 'concrete'] },
  { name: 'Slate Grey', hex: '#708090', family: 'greys_charcoals', tags: ['slate', 'grey', 'stone', 'modern'] },
  { name: 'Charcoal', hex: '#36454F', family: 'greys_charcoals', tags: ['charcoal', 'dark grey', 'deep', 'zinc'] },
  { name: 'Anthracite', hex: '#293133', family: 'greys_charcoals', tags: ['anthracite', 'matte', 'frame'] },
  { name: 'Cool Ash', hex: '#D1D5DB', family: 'greys_charcoals', tags: ['ash', 'light grey', 'modern'] },
  { name: 'Graphite', hex: '#27292B', family: 'greys_charcoals', tags: ['graphite', 'dark', 'industrial'] },
  { name: 'Storm Grey', hex: '#4F5D75', family: 'greys_charcoals', tags: ['storm', 'blue grey', 'slate'] },
  { name: 'Concrete Grey', hex: '#8D99AE', family: 'greys_charcoals', tags: ['concrete', 'brutalist', 'raw'] },

  // ── Browns & Wood Tones ────────────────────────────────────────────────────
  { name: 'Teak', hex: '#8B5A2B', family: 'browns_wood', tags: ['teak', 'wood', 'timber', 'warm brown'] },
  { name: 'Walnut', hex: '#5C4033', family: 'browns_wood', tags: ['walnut', 'deep brown', 'hardwood'] },
  { name: 'Chocolate Brown', hex: '#3D2314', family: 'browns_wood', tags: ['chocolate', 'brown', 'espresso'] },
  { name: 'Roasted Coffee', hex: '#4B3621', family: 'browns_wood', tags: ['coffee', 'rich', 'timber'] },
  { name: 'Rich Chestnut', hex: '#7B3F00', family: 'browns_wood', tags: ['chestnut', 'reddish brown', 'mahogany'] },
  { name: 'Honey Oak', hex: '#BA8759', family: 'browns_wood', tags: ['oak', 'honey', 'golden brown'] },
  { name: 'Cedar Bark', hex: '#704214', family: 'browns_wood', tags: ['cedar', 'natural', 'timber'] },
  { name: 'Deep Espresso', hex: '#2B1700', family: 'browns_wood', tags: ['espresso', 'dark wood', 'entrance'] },

  // ── Reds & Terracotta ──────────────────────────────────────────────────────
  { name: 'Terracotta', hex: '#C25E3E', family: 'reds_terracotta', tags: ['terracotta', 'clay', 'warm', 'jaali'] },
  { name: 'Brick Red', hex: '#CB4154', family: 'reds_terracotta', tags: ['brick', 'red', 'wirecut', 'exposed'] },
  { name: 'Rustic Clay', hex: '#B35434', family: 'reds_terracotta', tags: ['clay', 'mangalore', 'tile', 'roof'] },
  { name: 'Burnt Sienna', hex: '#E97451', family: 'reds_terracotta', tags: ['sienna', 'earthy', 'warm'] },
  { name: 'Crimson Accent', hex: '#990000', family: 'reds_terracotta', tags: ['crimson', 'accent', 'bold'] },
  { name: 'Jaipur Pink', hex: '#C88A83', family: 'reds_terracotta', tags: ['jaipur', 'pink', 'sandstone', 'haveli'] },
  { name: 'Coral Earth', hex: '#D97454', family: 'reds_terracotta', tags: ['coral', 'warm', 'spanish'] },
  { name: 'Tuscan Red', hex: '#7C3030', family: 'reds_terracotta', tags: ['tuscan', 'deep red', 'mediterranean'] },

  // ── Blues ──────────────────────────────────────────────────────────────────
  { name: 'Navy Blue', hex: '#000080', family: 'blues', tags: ['navy', 'dark blue', 'nautical'] },
  { name: 'Midnight Navy', hex: '#1B263B', family: 'blues', tags: ['midnight', 'navy', 'luxury'] },
  { name: 'Slate Blue', hex: '#6A5ACD', family: 'blues', tags: ['slate blue', 'cool', 'accent'] },
  { name: 'Sky Blue', hex: '#87CEEB', family: 'blues', tags: ['sky', 'light blue', 'glass tint'] },
  { name: 'Aegean Blue', hex: '#4E6E81', family: 'blues', tags: ['aegean', 'coastal', 'mediterranean'] },
  { name: 'Indigo Mist', hex: '#3D405B', family: 'blues', tags: ['indigo', 'muted blue', 'sophisticated'] },
  { name: 'Steel Blue', hex: '#4682B4', family: 'blues', tags: ['steel', 'modern blue', 'metallic'] },
  { name: 'Ocean Breeze', hex: '#2A9D8F', family: 'blues', tags: ['ocean', 'teal', 'tropical'] },

  // ── Greens ─────────────────────────────────────────────────────────────────
  { name: 'Sage Green', hex: '#9CAF88', family: 'greens', tags: ['sage', 'soft green', 'muted', 'natural'] },
  { name: 'Olive Green', hex: '#556B2F', family: 'greens', tags: ['olive', 'earthy green', 'traditional'] },
  { name: 'Forest Green', hex: '#228B22', family: 'greens', tags: ['forest', 'deep green', 'biophilic'] },
  { name: 'Deep Emerald', hex: '#046307', family: 'greens', tags: ['emerald', 'rich green', 'luxury'] },
  { name: 'Eucalyptus', hex: '#5F8575', family: 'greens', tags: ['eucalyptus', 'blue green', 'contemporary'] },
  { name: 'Cypress Dark', hex: '#344E41', family: 'greens', tags: ['cypress', 'dark green', 'architectural'] },
  { name: 'Moss Green', hex: '#8A9A5B', family: 'greens', tags: ['moss', 'natural green', 'tropical'] },
  { name: 'Mint Frost', hex: '#A8D5BA', family: 'greens', tags: ['mint', 'pale green', 'crisp'] },

  // ── Black & Dark Accents ───────────────────────────────────────────────────
  { name: 'Black', hex: '#0A0A0A', family: 'black_dark', tags: ['black', 'jet black', 'bold', 'modern'] },
  { name: 'Onyx', hex: '#0F0F0F', family: 'black_dark', tags: ['onyx', 'deep black', 'monolithic'] },
  { name: 'Dark Iron', hex: '#1C1F24', family: 'black_dark', tags: ['iron', 'shou sugi ban', 'charred'] },
  { name: 'Charcoal Night', hex: '#1E232A', family: 'black_dark', tags: ['charcoal', 'night', 'accents'] },
  { name: 'Pitch Black', hex: '#050505', family: 'black_dark', tags: ['pitch', 'stark', 'trim'] },
  { name: 'Obsidian', hex: '#16161D', family: 'black_dark', tags: ['obsidian', 'volcanic', 'basalt'] },

  // ── Gold & Metallic Accents ────────────────────────────────────────────────
  { name: 'Gold', hex: '#D4AF37', family: 'gold_metallic', tags: ['gold', 'metallic', 'luxury', 'brass'] },
  { name: 'Champagne Bronze', hex: '#B89778', family: 'gold_metallic', tags: ['champagne', 'bronze', 'anodized'] },
  { name: 'Antique Brass', hex: '#CD7F32', family: 'gold_metallic', tags: ['brass', 'antique', 'traditional'] },
  { name: 'Weathered Copper', hex: '#B87333', family: 'gold_metallic', tags: ['copper', 'corten', 'patina'] },
  { name: 'Brushed Aluminum', hex: '#A8A9AD', family: 'gold_metallic', tags: ['aluminum', 'silver', 'metallic'] },
  { name: 'Rose Gold Tone', hex: '#B76E79', family: 'gold_metallic', tags: ['rose gold', 'warm metal', 'accent'] }
];

export const COLOR_PRESETS = [
  {
    id: 'modern_white_charcoal',
    name: 'Modern White & Charcoal',
    description: 'Crisp alabaster walling with deep charcoal architectural box reveals and bronze trims.',
    colors: {
      primary_wall: '#F5F2EA',
      secondary_wall: '#EAE6DF',
      accent_wall: '#343A40',
      front_facade: '#F5F2EA',
      boundary_wall: '#E5E0D6',
      boundary_gate: '#30343B',
      door: '#60452F',
      window_frame: '#20252B',
      window_glass_tint: '#7DD3FC',
      railing: '#1F2937',
      roof_parapet: '#343A40',
      exterior_trims: '#20252B'
    }
  },
  {
    id: 'cream_walnut',
    name: 'Cream & Walnut',
    description: 'Warm cream masonry accented by dark walnut timber portal and antique bronze frames.',
    colors: {
      primary_wall: '#FFFDD0',
      secondary_wall: '#F5F2EB',
      accent_wall: '#5C4033',
      front_facade: '#FFFDD0',
      boundary_wall: '#F5F2EB',
      boundary_gate: '#4B3621',
      door: '#4B3621',
      window_frame: '#3E342B',
      window_glass_tint: '#7DD3FC',
      railing: '#3E342B',
      roof_parapet: '#5C4033',
      exterior_trims: '#3E342B'
    }
  },
  {
    id: 'white_teak',
    name: 'White & Teak',
    description: 'Minimal pure white cubic volumes warmed with natural Burma teak vertical louvers.',
    colors: {
      primary_wall: '#FFFFFF',
      secondary_wall: '#F4F4F0',
      accent_wall: '#8B5A2B',
      front_facade: '#8B5A2B',
      boundary_wall: '#FFFFFF',
      boundary_gate: '#1C1F24',
      door: '#8B5A2B',
      window_frame: '#1C1F24',
      window_glass_tint: '#93C5FD',
      railing: '#8B5A2B',
      roof_parapet: '#FFFFFF',
      exterior_trims: '#1C1F24'
    }
  },
  {
    id: 'beige_sandstone',
    name: 'Beige & Sandstone',
    description: 'Earthy beige plaster harmonized with honed Dholpur sandstone slabs and chestnut timber.',
    colors: {
      primary_wall: '#F5F5DC',
      secondary_wall: '#EBE6DD',
      accent_wall: '#D8C3A5',
      front_facade: '#D8C3A5',
      boundary_wall: '#F5F5DC',
      boundary_gate: '#3E342B',
      door: '#7B3F00',
      window_frame: '#3E342B',
      window_glass_tint: '#7DD3FC',
      railing: '#3E342B',
      roof_parapet: '#D8C3A5',
      exterior_trims: '#D8C3A5'
    }
  },
  {
    id: 'grey_natural_wood',
    name: 'Grey & Natural Wood',
    description: 'Contemporary Scandinavian cool grey massing warmed with honey oak cladding panels.',
    colors: {
      primary_wall: '#D1D5DB',
      secondary_wall: '#E5E7EB',
      accent_wall: '#BA8759',
      front_facade: '#BA8759',
      boundary_wall: '#D1D5DB',
      boundary_gate: '#111827',
      door: '#8B5A2B',
      window_frame: '#111827',
      window_glass_tint: '#7DD3FC',
      railing: '#111827',
      roof_parapet: '#4B5563',
      exterior_trims: '#111827'
    }
  },
  {
    id: 'ivory_gold',
    name: 'Ivory & Gold',
    description: 'Palatial Italian Roman Travertine ivory combined with champagne bronze and gold accents.',
    colors: {
      primary_wall: '#FFFFF0',
      secondary_wall: '#FFFDD0',
      accent_wall: '#D4AF37',
      front_facade: '#FFFFF0',
      boundary_wall: '#FFFFF0',
      boundary_gate: '#B89778',
      door: '#3D2314',
      window_frame: '#B89778',
      window_glass_tint: '#93C5FD',
      railing: '#D4AF37',
      roof_parapet: '#FFFFF0',
      exterior_trims: '#B89778'
    }
  },
  {
    id: 'terracotta_cream',
    name: 'Terracotta & Cream',
    description: 'Authentic Indian tropical modernism with warm clay red jaali screens and ivory lime wash.',
    colors: {
      primary_wall: '#FFFDD0',
      secondary_wall: '#F5F2EB',
      accent_wall: '#C25E3E',
      front_facade: '#C25E3E',
      boundary_wall: '#FFFDD0',
      boundary_gate: '#C25E3E',
      door: '#8B5A2B',
      window_frame: '#3E342B',
      window_glass_tint: '#7DD3FC',
      railing: '#3E342B',
      roof_parapet: '#C25E3E',
      exterior_trims: '#C25E3E'
    }
  },
  {
    id: 'sage_green_white',
    name: 'Sage Green & White',
    description: 'Serene biophilic botanical house palette with muted sage green accents and bone white walls.',
    colors: {
      primary_wall: '#FFFFFF',
      secondary_wall: '#F8F9FA',
      accent_wall: '#9CAF88',
      front_facade: '#9CAF88',
      boundary_wall: '#FFFFFF',
      boundary_gate: '#2F3E46',
      door: '#556B2F',
      window_frame: '#2F3E46',
      window_glass_tint: '#A7F3D0',
      railing: '#2F3E46',
      roof_parapet: '#9CAF88',
      exterior_trims: '#2F3E46'
    }
  },
  {
    id: 'luxury_white_black',
    name: 'Luxury White & Black',
    description: 'High-contrast minimalist luxury villa with stark white stucco and jet black accents.',
    colors: {
      primary_wall: '#FFFFFF',
      secondary_wall: '#F4F4F0',
      accent_wall: '#0A0A0A',
      front_facade: '#0A0A0A',
      boundary_wall: '#FFFFFF',
      boundary_gate: '#000000',
      door: '#0A0A0A',
      window_frame: '#000000',
      window_glass_tint: '#60A5FA',
      railing: '#000000',
      roof_parapet: '#0A0A0A',
      exterior_trims: '#000000'
    }
  }
];

export const MATERIAL_FINISH_TYPES = [
  { id: 'matte_paint', name: 'Matte Weatherproof Paint', rateDiff: 0, roughness: 0.95, metalness: 0.0, description: 'Zero-sheen smooth weather-shield mineral coating (included in base estimate).' },
  { id: 'satin_paint', name: 'Satin Silk Emulsion', rateDiff: 8, roughness: 0.65, metalness: 0.05, description: 'Low-sheen elegant wipeable silicone acrylic finish (+₹8/sq ft).' },
  { id: 'gloss_paint', name: 'High-Gloss Architectural Enamel', rateDiff: 12, roughness: 0.25, metalness: 0.12, description: 'Reflective gloss finish for accent portals and trims (+₹12/sq ft).' },
  { id: 'textured_paint', name: 'Textured Acrylic Stucco', rateDiff: 18, roughness: 0.9, metalness: 0.05, description: 'Fine granular sandstone texture with anti-crack flex (+₹18/sq ft).' },
  { id: 'stone_cladding', name: 'Natural Sandstone / Travertine Cladding', rateDiff: 34, roughness: 0.75, metalness: 0.15, description: 'Dry-clad 20mm natural stone feature wall (+₹34/sq ft).' },
  { id: 'wood_finish', name: 'Exterior Teak Wood Louvers', rateDiff: 45, roughness: 0.45, metalness: 0.1, description: 'PU-coated outdoor weather-resistant hardwood battens (+₹45/sq ft).' },
  { id: 'metal_finish', name: 'PVD Powder-Coated Metal Panel', rateDiff: 38, roughness: 0.35, metalness: 0.75, description: 'Rust-proof anodized architectural aluminum facade box (+₹38/sq ft).' },
  { id: 'glass_tint', name: 'Solar Low-E Reflective Glazing', rateDiff: 25, roughness: 0.1, metalness: 0.9, description: 'Thermal-insulating tinted safety glazing (+₹25/sq ft).' }
];

/**
 * Validates a 3 or 6 digit hex color string (with or without #).
 */
export function isValidHex(hex) {
  if (!hex || typeof hex !== 'string') return false;
  return /^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(hex.trim());
}

/**
 * Normalizes hex string with a leading '#'.
 */
export function normalizeHex(hex) {
  if (!hex) return '#000000';
  const clean = hex.trim();
  return clean.startsWith('#') ? clean.toUpperCase() : `#${clean.toUpperCase()}`;
}

/**
 * Search colors in catalog by name, tag, or family.
 */
export function searchColors(query, family = 'all') {
  let filtered = COLOR_CATALOG;
  if (family && family !== 'all' && family !== 'custom') {
    filtered = filtered.filter(c => c.family === family);
  }
  if (!query || !query.trim()) {
    return filtered;
  }
  const q = query.toLowerCase().trim();
  return filtered.filter(c => {
    return (
      c.name.toLowerCase().includes(q) ||
      c.hex.toLowerCase().includes(q) ||
      c.tags.some(t => t.toLowerCase().includes(q))
    );
  });
}
