/**
 * Exterior Architectural Blueprint & Vector Elevation Generator — Phase 6G.5.
 * Generates plan-aware, architecturally accurate vector 2D elevations (SVG)
 * based on the project's actual plot dimensions, floor configuration, orientation,
 * selected design catalog features, and custom paint/material swatches.
 *
 * Supports two rendering themes:
 * 1. "blueprint": Classic cyan/white technical drafting blueprint with architectural grid and datum markers.
 * 2. "rendered": Photorealistic vector elevation with material textures, day/night lighting, and real paint colors.
 *
 * Supports three view angles:
 * - "front": Orthographic Front Facade Elevation.
 * - "front_left": 3/4 Isometric Perspective from front-left with 3D depth massing.
 * - "front_right": 3/4 Isometric Perspective from front-right with 3D depth massing.
 */

function sanitizeHex(color, fallback = '#F4F4F0') {
  if (!color || typeof color !== 'string') return fallback;
  const c = color.trim();
  if (/^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(c)) return c;
  return fallback;
}

function darkenColor(hexColor, factor = 0.72) {
  let hex = hexColor.replace('#', '');
  if (hex.length === 3) hex = hex.split('').map(x => x + x).join('');
  try {
    const r = Math.max(0, Math.min(255, Math.floor(parseInt(hex.slice(0, 2), 16) * factor)));
    const g = Math.max(0, Math.min(255, Math.floor(parseInt(hex.slice(2, 4), 16) * factor)));
    const b = Math.max(0, Math.min(255, Math.floor(parseInt(hex.slice(4, 6), 16) * factor)));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  } catch (_) {
    return '#1e293b';
  }
}

export function generateExteriorElevationSvg({
  project = {},
  selectedDesign = {},
  customColors = {},
  customMaterials = {},
  lightingMode = 'daylight',
  viewAngle = 'front',
  themeMode = 'blueprint' // 'blueprint' | 'rendered'
}) {
  const plotW = Math.max(15, Math.min(120, Number(project.plot_width || 30)));
  const plotL = Math.max(20, Math.min(200, Number(project.plot_length || 40)));
  const floors = Math.max(1, Math.min(4, Number(project.floors || 2)));
  const facing = project.facing || 'South';
  const designName = selectedDesign?.name || 'Architectural Modern Elevation';
  const designStyle = selectedDesign?.style || 'Modern Contemporary';
  const designId = selectedDesign?.id || 'ext_mod_01';
  const isNight = lightingMode === 'night';
  const isBlueprint = themeMode === 'blueprint';

  // Resolved authoritative colors
  const cPrimary = sanitizeHex(customColors.primary_wall, '#F5F2EA');
  const cAccent = sanitizeHex(customColors.accent_wall, '#343A40');
  const cBoundary = sanitizeHex(customColors.boundary_wall, '#E5E0D6');
  const cDoor = sanitizeHex(customColors.door, '#60452F');
  const cWindow = sanitizeHex(customColors.window_frame, '#20252B');
  const cGlassTint = sanitizeHex(customColors.window_glass_tint, '#7DD3FC');
  const cRailing = sanitizeHex(customColors.railing, '#1F2937');
  const cGate = sanitizeHex(customColors.boundary_gate, '#30343B');

  // Blueprint specific linework palette
  const bpBg = '#0a192f';
  const bpLinePrimary = '#f8fafc';
  const bpLineCyan = '#38bdf8';
  const bpLineMuted = '#64748b';
  const bpGrid = 'rgba(56, 189, 248, 0.12)';
  const bpHatch = 'rgba(56, 189, 248, 0.25)';

  // Dimensions
  const viewW = 1000;
  const viewH = 680;
  const groundY = 560;
  const plinthH = 26; // ~1.5 ft plinth height
  const plinthY = groundY - plinthH;
  const floorHeightPx = 112; // ~10.5 ft per floor
  const bldgH = floors * floorHeightPx;
  const bldgTopY = plinthY - bldgH;

  // Building width scaled to plot frontage
  const scaleW = Math.min(1.3, Math.max(0.7, plotW / 30.0));
  const bldgW = Math.min(740, Math.max(440, 530 * scaleW));
  const bldgX = (viewW - bldgW) / 2;

  // Cladding type
  const cladding = customMaterials.finish_type || selectedDesign?.materials?.cladding || 'fluted_louvers';

  const defs = [];

  if (isBlueprint) {
    // ── Technical Blueprint Grid & Hatching Defs
    defs.push(`
      <pattern id="bpGridSmall" width="10" height="10" patternUnits="userSpaceOnUse">
        <path d="M 10 0 L 0 0 0 10" fill="none" stroke="${bpGrid}" stroke-width="0.5" />
      </pattern>
      <pattern id="bpGridLarge" width="50" height="50" patternUnits="userSpaceOnUse">
        <rect width="50" height="50" fill="url(#bpGridSmall)" />
        <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(56, 189, 248, 0.25)" stroke-width="1" />
      </pattern>
      <pattern id="bpHatchWall" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="8" stroke="${bpHatch}" stroke-width="1.2" />
      </pattern>
      <pattern id="bpHatchPlinth" width="6" height="6" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="6" stroke="rgba(148, 163, 184, 0.3)" stroke-width="1" />
      </pattern>
      <pattern id="bpCladdingLouvers" width="10" height="20" patternUnits="userSpaceOnUse">
        <rect width="10" height="20" fill="rgba(56, 189, 248, 0.08)" />
        <line x1="9" y1="0" x2="9" y2="20" stroke="${bpLineCyan}" stroke-width="1.2" />
      </pattern>
    `);
  } else {
    // ── Rendered Vector Elevation Defs
    if (isNight) {
      defs.push(`
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#050811" />
          <stop offset="50%" stop-color="#0f172a" />
          <stop offset="100%" stop-color="#1e293b" />
        </linearGradient>
        <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.9" />
          <stop offset="30%" stop-color="#93c5fd" stop-opacity="0.25" />
          <stop offset="100%" stop-color="#1e293b" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="windowGlow" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fef08a" stop-opacity="0.95" />
          <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.85" />
        </linearGradient>
      `);
    } else if (lightingMode === 'golden_hour') {
      defs.push(`
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#c2410c" />
          <stop offset="40%" stop-color="#f97316" />
          <stop offset="75%" stop-color="#fde047" />
          <stop offset="100%" stop-color="#fef08a" />
        </linearGradient>
        <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#fffbeb" stop-opacity="0.9" />
          <stop offset="30%" stop-color="#f59e0b" stop-opacity="0.3" />
          <stop offset="100%" stop-color="#c2410c" stop-opacity="0" />
        </radialGradient>
        <linearGradient id="windowGlow" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fef08a" stop-opacity="0.9" />
          <stop offset="60%" stop-color="#f59e0b" stop-opacity="0.8" />
          <stop offset="100%" stop-color="#b45309" stop-opacity="0.85" />
        </linearGradient>
      `);
    } else {
      defs.push(`
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#60a5fa" />
          <stop offset="55%" stop-color="#bae6fd" />
          <stop offset="100%" stop-color="#f0f9ff" />
        </linearGradient>
        <linearGradient id="windowGlow" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="${cGlassTint}" stop-opacity="0.85" />
          <stop offset="60%" stop-color="#0284c7" stop-opacity="0.7" />
          <stop offset="100%" stop-color="#0369a1" stop-opacity="0.9" />
        </linearGradient>
      `);
    }

    // Cladding Pattern
    defs.push(`
      <pattern id="renderedCladding" width="12" height="24" patternUnits="userSpaceOnUse">
        <rect width="12" height="24" fill="${cAccent}" />
        <line x1="11" y1="0" x2="11" y2="24" stroke="#0f172a" stroke-width="1.5" stroke-opacity="0.4" />
      </pattern>
      <linearGradient id="groundGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#334155" />
        <stop offset="25%" stop-color="#1e293b" />
        <stop offset="100%" stop-color="#0f172a" />
      </linearGradient>
    `);
  }

  const parts = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${viewW} ${viewH}" width="100%" height="100%" style="background:${isBlueprint ? bpBg : '#0f172a'};border-radius:10px;font-family:'JetBrains Mono',ui-monospace,Menlo,monospace;">`);
  parts.push(`<defs>${defs.join('')}</defs>`);

  // 1. Background Grid / Sky
  if (isBlueprint) {
    parts.push(`<rect width="${viewW}" height="${viewH}" fill="url(#bpGridLarge)" />`);
  } else {
    parts.push(`<rect width="${viewW}" height="${groundY}" fill="url(#skyGrad)" />`);
    parts.push(`<rect x="0" y="${groundY}" width="${viewW}" height="${viewH - groundY}" fill="url(#groundGrad)" />`);
  }

  // 2. Main Building Geometry Calculation
  const isIsoLeft = viewAngle === 'front_left' || viewAngle === 'perspective' || viewAngle === 'street';
  const isIsoRight = viewAngle === 'front_right';
  const isoOffsetX = isIsoLeft ? 45 : (isIsoRight ? -45 : 0);
  const isoDepthW = (isIsoLeft || isIsoRight) ? 55 : 0;

  const wallStroke = isBlueprint ? bpLinePrimary : '#0f172a';
  const wallStrokeW = isBlueprint ? '1.5' : '2';
  const wallFill = isBlueprint ? 'url(#bpHatchWall)' : cPrimary;
  const accentFill = isBlueprint ? 'url(#bpCladdingLouvers)' : 'url(#renderedCladding)';
  const plinthFill = isBlueprint ? 'url(#bpHatchPlinth)' : '#334155';
  const doorFill = isBlueprint ? 'rgba(56, 189, 248, 0.25)' : cDoor;
  const glassFill = isBlueprint ? 'rgba(56, 189, 248, 0.15)' : 'url(#windowGlow)';
  const slabFill = isBlueprint ? '#0f294d' : '#1e293b';

  // 3. Shaded 3D Side Depth Wall (Isometric Views)
  if (isIsoLeft) {
    const sideX = bldgX + isoOffsetX - isoDepthW;
    const sideFill = isBlueprint ? 'rgba(15, 23, 42, 0.8)' : darkenColor(cPrimary, 0.72);
    parts.push(`
      <polygon points="${sideX},${bldgTopY + 12} ${bldgX + isoOffsetX},${bldgTopY} ${bldgX + isoOffsetX},${plinthY} ${sideX},${plinthY + 8}"
        fill="${sideFill}" stroke="${wallStroke}" stroke-width="${wallStrokeW}" />
      <line x1="${sideX}" y1="${plinthY + 8}" x2="${sideX}" y2="${groundY}" stroke="${bpLineMuted}" stroke-dasharray="2,2" />
    `);
  } else if (isIsoRight) {
    const sideX = bldgX + bldgW + isoOffsetX;
    const sideFill = isBlueprint ? 'rgba(15, 23, 42, 0.8)' : darkenColor(cPrimary, 0.72);
    parts.push(`
      <polygon points="${sideX},${bldgTopY} ${sideX + isoDepthW},${bldgTopY + 12} ${sideX + isoDepthW},${plinthY + 8} ${sideX},${plinthY}"
        fill="${sideFill}" stroke="${wallStroke}" stroke-width="${wallStrokeW}" />
      <line x1="${sideX + isoDepthW}" y1="${plinthY + 8}" x2="${sideX + isoDepthW}" y2="${groundY}" stroke="${bpLineMuted}" stroke-dasharray="2,2" />
    `);
  }

  // 4. Ground Datum Line
  parts.push(`
    <line x1="30" y1="${groundY}" x2="${viewW - 30}" y2="${groundY}" stroke="${isBlueprint ? bpLineCyan : '#475569'}" stroke-width="2.5" />
    <text x="36" y="${groundY + 18}" fill="${isBlueprint ? bpLineCyan : '#94a3b8'}" font-size="10" font-weight="700">
      GL: ±0.00m (NATURAL GROUND LEVEL)
    </text>
  `);

  // 5. Plinth Level & Step Approach
  parts.push(`
    <rect x="${bldgX + isoOffsetX - 15}" y="${plinthY}" width="${bldgW + 30}" height="${plinthH}"
      fill="${plinthFill}" stroke="${wallStroke}" stroke-width="${wallStrokeW}" />
    <line x1="${bldgX + isoOffsetX - 20}" y1="${plinthY}" x2="${bldgX + bldgW + isoOffsetX + 20}" y2="${plinthY}"
      stroke="${isBlueprint ? bpLineCyan : '#64748b'}" stroke-width="1.8" />
  `);

  // 6. Main Building Facade Envelope
  parts.push(`
    <rect x="${bldgX + isoOffsetX}" y="${bldgTopY}" width="${bldgW}" height="${bldgH}"
      fill="${wallFill}" stroke="${wallStroke}" stroke-width="${wallStrokeW}" />
  `);

  // 7. Accent Architectural Projection / Column
  const accentColW = bldgW * 0.36;
  const accentX = bldgX + isoOffsetX + (bldgW - accentColW) - 15;
  parts.push(`
    <rect x="${accentX}" y="${bldgTopY - 14}" width="${accentColW}" height="${bldgH + 14}"
      fill="${accentFill}" stroke="${wallStroke}" stroke-width="${wallStrokeW}" />
    <rect x="${accentX - 4}" y="${bldgTopY - 18}" width="${accentColW + 8}" height="8"
      fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
  `);

  // 8. Floor-by-Floor Fenestrations, Slabs, Balconies
  for (let f = 0; f < floors; f++) {
    const floorY = plinthY - ((f + 1) * floorHeightPx);
    const floorNum = f;

    // Floor Slab Projection Band
    if (f > 0) {
      parts.push(`
        <rect x="${bldgX + isoOffsetX - 10}" y="${floorY + floorHeightPx - 10}" width="${bldgW + 20}" height="14"
          fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
      `);
    }

    if (floorNum === 0) {
      // ── Ground Level: Main Portal, Front Door & Windows
      const portalW = 120;
      const portalH = 92;
      const portalX = bldgX + isoOffsetX + 50;
      const portalY = plinthY - portalH;

      // Entrance Canopy Slab
      parts.push(`
        <rect x="${portalX - 16}" y="${portalY - 14}" width="${portalW + 32}" height="12"
          fill="${isBlueprint ? slabFill : cAccent}" stroke="${wallStroke}" stroke-width="1.5" />
        <line x1="${portalX - 10}" y1="${portalY - 14}" x2="${portalX - 10}" y2="${portalY - 32}" stroke="${isBlueprint ? bpLineCyan : '#94a3b8'}" stroke-width="2" />
        <line x1="${portalX + portalW + 10}" y1="${portalY - 14}" x2="${portalX + portalW + 10}" y2="${portalY - 32}" stroke="${isBlueprint ? bpLineCyan : '#94a3b8'}" stroke-width="2" />
      `);

      // Main Entrance Door (46px x 82px)
      const doorW = 46;
      const doorH = 82;
      const doorX = portalX + 10;
      const doorY = plinthY - doorH;
      parts.push(`
        <rect x="${doorX}" y="${doorY}" width="${doorW}" height="${doorH}"
          fill="${doorFill}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
        <rect x="${doorX + doorW - 8}" y="${doorY + 32}" width="3" height="24" fill="${isBlueprint ? bpLineCyan : '#d97706'}" />
      `);

      // Ground Floor Picture Window
      const winW = 88;
      const winH = 68;
      const winX = portalX + doorW + 26;
      const winY = plinthY - winH - 12;
      parts.push(`
        <rect x="${winX}" y="${winY}" width="${winW}" height="${winH}"
          fill="${glassFill}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2.5" />
        <line x1="${winX + winW / 2}" y1="${winY}" x2="${winX + winW / 2}" y2="${winY + winH}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
        <line x1="${winX}" y1="${winY + winH / 2}" x2="${winX + winW}" y2="${winY + winH / 2}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="1.5" />
      `);

      // Accent Column Ribbon Slit Window
      const acWinX = accentX + 24;
      const acWinW = accentColW - 48;
      const acWinH = 70;
      const acWinY = plinthY - acWinH - 12;
      parts.push(`
        <rect x="${acWinX}" y="${acWinY}" width="${acWinW}" height="${acWinH}"
          fill="${glassFill}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
        <line x1="${acWinX + acWinW / 3}" y1="${acWinY}" x2="${acWinX + acWinW / 3}" y2="${acWinY + acWinH}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="1.5" />
        <line x1="${acWinX + (2 * acWinW) / 3}" y1="${acWinY}" x2="${acWinX + (2 * acWinW) / 3}" y2="${acWinY + acWinH}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="1.5" />
      `);
    } else {
      // ── Upper Floor: Cantilever Balcony & Glazed Sliding Doors
      const balcW = bldgW * 0.48;
      const balcX = bldgX + isoOffsetX + 35;
      const balcH = 38; // Railing height ~3.5 ft
      const balcY = floorY + floorHeightPx - balcH - 10;

      // Sliding French Window / Terrace Door behind Balcony
      const upperDoorW = balcW - 40;
      const upperDoorH = 80;
      const upperDoorX = balcX + 20;
      const upperDoorY = floorY + floorHeightPx - upperDoorH - 10;

      parts.push(`
        <rect x="${upperDoorX}" y="${upperDoorY}" width="${upperDoorW}" height="${upperDoorH}"
          fill="${glassFill}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
        <line x1="${upperDoorX + upperDoorW / 2}" y1="${upperDoorY}" x2="${upperDoorX + upperDoorW / 2}" y2="${upperDoorY + upperDoorH}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
      `);

      // Cantilever Balcony Slab & Railing
      parts.push(`
        <rect x="${balcX - 12}" y="${floorY + floorHeightPx - 10}" width="${balcW + 24}" height="10"
          fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
        <rect x="${balcX - 12}" y="${balcY}" width="${balcW + 24}" height="${balcH}"
          fill="${isBlueprint ? 'rgba(56, 189, 248, 0.12)' : 'rgba(125, 211, 252, 0.25)'}"
          stroke="${isBlueprint ? bpLineCyan : cRailing}" stroke-width="2" />
        <line x1="${balcX - 12}" y1="${balcY}" x2="${balcX + balcW + 12}" y2="${balcY}" stroke="${isBlueprint ? bpLineCyan : cRailing}" stroke-width="3" />
      `);

      // Balcony balusters / glass divider lines
      for (let s = 1; s < 4; s++) {
        const sx = balcX - 12 + (s * (balcW + 24)) / 4;
        parts.push(`<line x1="${sx}" y1="${balcY}" x2="${sx}" y2="${balcY + balcH}" stroke="${isBlueprint ? bpLineCyan : cRailing}" stroke-width="1.5" />`);
      }

      // Upper Accent Box Window
      const upAcWinX = accentX + 24;
      const upAcWinW = accentColW - 48;
      const upAcWinH = 75;
      const upAcWinY = floorY + 16;
      parts.push(`
        <rect x="${upAcWinX}" y="${upAcWinY}" width="${upAcWinW}" height="${upAcWinH}"
          fill="${glassFill}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="2" />
        <line x1="${upAcWinX + upAcWinW / 2}" y1="${upAcWinY}" x2="${upAcWinX + upAcWinW / 2}" y2="${upAcWinY + upAcWinH}" stroke="${isBlueprint ? bpLineCyan : cWindow}" stroke-width="1.5" />
      `);
    }
  }

  // 9. Parapet Wall & Overhanging Roof Slab
  parts.push(`
    <rect x="${bldgX + isoOffsetX - 14}" y="${bldgTopY - 24}" width="${bldgW + 28}" height="16"
      fill="${slabFill}" stroke="${wallStroke}" stroke-width="2" />
    <line x1="${bldgX + isoOffsetX - 16}" y1="${bldgTopY - 24}" x2="${bldgX + bldgW + isoOffsetX + 16}" y2="${bldgTopY - 24}"
      stroke="${isBlueprint ? bpLineCyan : '#94a3b8'}" stroke-width="2.5" />
  `);

  // 10. Boundary Wall & Motorized Entrance Gate in Foreground
  const boundH = 50; // ~4.5 ft boundary wall
  const boundY = groundY - boundH;
  const gateW = 140;
  const gateX = bldgX + isoOffsetX + 35;
  const gateY = groundY - 48;

  // Left boundary wall
  parts.push(`
    <rect x="${bldgX + isoOffsetX - 40}" y="${boundY}" width="${gateX - (bldgX + isoOffsetX - 40)}" height="${boundH}"
      fill="${isBlueprint ? 'url(#bpHatchWall)' : cBoundary}" stroke="${wallStroke}" stroke-width="2" />
    <rect x="${bldgX + isoOffsetX - 45}" y="${boundY - 6}" width="16" height="${boundH + 6}" fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
    <rect x="${gateX - 12}" y="${boundY - 8}" width="14" height="${boundH + 8}" fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
  `);

  // Right boundary wall
  parts.push(`
    <rect x="${gateX + gateW}" y="${boundY}" width="${bldgX + bldgW + isoOffsetX + 40 - (gateX + gateW)}" height="${boundH}"
      fill="${isBlueprint ? 'url(#bpHatchWall)' : cBoundary}" stroke="${wallStroke}" stroke-width="2" />
    <rect x="${gateX + gateW}" y="${boundY - 8}" width="14" height="${boundH + 8}" fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
    <rect x="${bldgX + bldgW + isoOffsetX + 30}" y="${boundY - 6}" width="16" height="${boundH + 6}" fill="${slabFill}" stroke="${wallStroke}" stroke-width="1.5" />
  `);

  // Entrance Sliding Gate with horizontal slats
  parts.push(`
    <rect x="${gateX}" y="${gateY}" width="${gateW}" height="48"
      fill="${isBlueprint ? 'rgba(56, 189, 248, 0.15)' : cGate}" stroke="${isBlueprint ? bpLineCyan : '#1e293b'}" stroke-width="2" />
  `);
  for (let g = 1; g < 6; g++) {
    const gy = gateY + g * 8;
    parts.push(`<line x1="${gateX}" y1="${gy}" x2="${gateX + gateW}" y2="${gy}" stroke="${isBlueprint ? bpLineCyan : '#475569'}" stroke-width="1" />`);
  }

  // 11. Datum Level Markers on Right Margin
  const datumX = viewW - 130;
  const levels = [
    { label: '±0.00m Ground', y: groundY },
    { label: '+0.45m Plinth', y: plinthY }
  ];
  for (let f = 1; f < floors; f++) {
    const fy = plinthY - (f * floorHeightPx);
    levels.push({ label: `+${(0.45 + f * 3.2).toFixed(2)}m Floor ${f}`, y: fy });
  }
  levels.push({ label: `+${(0.45 + floors * 3.2 + 0.9).toFixed(2)}m Parapet`, y: bldgTopY - 24 });

  parts.push(`<g id="datum-markers">`);
  levels.forEach(lvl => {
    parts.push(`
      <line x1="${bldgX + bldgW + isoOffsetX + 20}" y1="${lvl.y}" x2="${datumX + 20}" y2="${lvl.y}"
        stroke="${isBlueprint ? bpLineCyan : '#64748b'}" stroke-width="1" stroke-dasharray="3,3" opacity="0.6" />
      <polygon points="${datumX + 20},${lvl.y} ${datumX + 28},${lvl.y - 5} ${datumX + 28},${lvl.y + 5}" fill="${isBlueprint ? bpLineCyan : '#38bdf8'}" />
      <text x="${datumX + 34}" y="${lvl.y + 4}" fill="${isBlueprint ? bpLinePrimary : '#e2e8f0'}" font-size="10" font-weight="600">
        ${lvl.label}
      </text>
    `);
  });
  parts.push(`</g>`);

  // 12. Frontage Dimension Line on Bottom
  const dimY = groundY + 44;
  parts.push(`
    <g id="frontage-dimension">
      <line x1="${bldgX + isoOffsetX}" y1="${dimY}" x2="${bldgX + bldgW + isoOffsetX}" y2="${dimY}"
        stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.8" />
      <line x1="${bldgX + isoOffsetX}" y1="${groundY + 36}" x2="${bldgX + isoOffsetX}" y2="${dimY + 8}" stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.5" />
      <line x1="${bldgX + bldgW + isoOffsetX}" y1="${groundY + 36}" x2="${bldgX + bldgW + isoOffsetX}" y2="${dimY + 8}" stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.5" />
      <polygon points="${bldgX + isoOffsetX},${dimY} ${bldgX + isoOffsetX + 10},${dimY - 4} ${bldgX + isoOffsetX + 10},${dimY + 4}" fill="${isBlueprint ? bpLineCyan : '#38bdf8'}" />
      <polygon points="${bldgX + bldgW + isoOffsetX},${dimY} ${bldgX + bldgW + isoOffsetX - 10},${dimY - 4} ${bldgX + bldgW + isoOffsetX - 10},${dimY + 4}" fill="${isBlueprint ? bpLineCyan : '#38bdf8'}" />
      <rect x="${viewW / 2 - 100}" y="${dimY - 12}" width="200" height="24" rx="4"
        fill="${isBlueprint ? '#0f294d' : '#0f172a'}" stroke="${isBlueprint ? bpLineCyan : '#334155'}" stroke-width="1" />
      <text x="${viewW / 2}" y="${dimY + 4}" fill="#f8fafc" font-size="11" font-weight="700" text-anchor="middle">
        ${plotW}′-0″ (${(plotW * 0.3048).toFixed(2)}m) PLOT FRONTAGE
      </text>
    </g>
  `);

  // 13. Building Height Dimension Line on Left
  const dimLeftX = bldgX + isoOffsetX - 50;
  parts.push(`
    <g id="height-dimension">
      <line x1="${dimLeftX}" y1="${plinthY}" x2="${dimLeftX}" y2="${bldgTopY - 24}"
        stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.8" />
      <line x1="${dimLeftX - 8}" y1="${plinthY}" x2="${bldgX + isoOffsetX - 30}" y2="${plinthY}" stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.5" />
      <line x1="${dimLeftX - 8}" y1="${bldgTopY - 24}" x2="${bldgX + isoOffsetX - 30}" y2="${bldgTopY - 24}" stroke="${isBlueprint ? bpLineCyan : '#38bdf8'}" stroke-width="1.5" />
      <polygon points="${dimLeftX},${plinthY} ${dimLeftX - 4},${plinthY - 10} ${dimLeftX + 4},${plinthY - 10}" fill="${isBlueprint ? bpLineCyan : '#38bdf8'}" />
      <polygon points="${dimLeftX},${bldgTopY - 24} ${dimLeftX - 4},${bldgTopY - 14} ${dimLeftX + 4},${bldgTopY - 14}" fill="${isBlueprint ? bpLineCyan : '#38bdf8'}" />
      <text x="${dimLeftX - 10}" y="${(plinthY + bldgTopY - 24) / 2}" fill="#f8fafc" font-size="10" font-weight="700" text-anchor="middle" transform="rotate(-90 ${dimLeftX - 10} ${(plinthY + bldgTopY - 24) / 2})">
        ${(floors * 10.5 + 2.5).toFixed(1)}′ HT
      </text>
    </g>
  `);

  // 14. Professional Architectural Title Block (Top Left)
  const angleLabel = {
    front: 'ORTHOGRAPHIC FRONT ELEVATION',
    front_left: '3/4 ISOMETRIC PERSPECTIVE (FRONT-LEFT)',
    front_right: '3/4 ISOMETRIC PERSPECTIVE (FRONT-RIGHT)'
  }[viewAngle] || 'FRONT ELEVATION';

  const themeLabel = isBlueprint ? 'TECHNICAL BLUEPRINT WORKING DRAWING' : 'ARCHITECTURAL COLOR ELEVATION';

  parts.push(`
    <g id="title-block">
      <rect x="24" y="20" width="360" height="82" rx="8"
        fill="${isBlueprint ? 'rgba(11, 26, 48, 0.95)' : 'rgba(15, 23, 42, 0.92)'}"
        stroke="${isBlueprint ? bpLineCyan : '#334155'}" stroke-width="1.5" />
      <text x="38" y="42" fill="${bpLineCyan}" font-size="12" font-weight="800" letter-spacing="0.5">
        ${designName.toUpperCase()}
      </text>
      <text x="38" y="58" fill="#f8fafc" font-size="10" font-weight="700">
        ${angleLabel}
      </text>
      <text x="38" y="74" fill="#94a3b8" font-size="9">
        ${themeLabel} • G+${floors - 1} Levels • ${facing} Facing
      </text>
      <text x="38" y="88" fill="#64748b" font-size="8.5">
        Plot: ${plotW}′×${plotL}′ • Drawing Ref: EL-01 • Scale: 1:100
      </text>
    </g>
  `);

  // 15. Applied Color Palette Legend Swatches (Top Right)
  parts.push(`
    <g id="palette-swatches">
      <rect x="${viewW - 200}" y="20" width="176" height="38" rx="6"
        fill="${isBlueprint ? 'rgba(11, 26, 48, 0.95)' : 'rgba(15, 23, 42, 0.92)'}"
        stroke="${isBlueprint ? bpLineCyan : '#334155'}" stroke-width="1.2" />
      <text x="${viewW - 192}" y="32" fill="#94a3b8" font-size="7.5" font-weight="700" letter-spacing="0.5">
        APPLIED PALETTE
      </text>
      <circle cx="${viewW - 180}" cy="46" r="7" fill="${cPrimary}" stroke="#475569" stroke-width="1" />
      <circle cx="${viewW - 150}" cy="46" r="7" fill="${cAccent}" stroke="#475569" stroke-width="1" />
      <circle cx="${viewW - 120}" cy="46" r="7" fill="${cDoor}" stroke="#475569" stroke-width="1" />
      <circle cx="${viewW - 90}" cy="46" r="7" fill="${cWindow}" stroke="#475569" stroke-width="1" />
      <circle cx="${viewW - 60}" cy="46" r="7" fill="${cGlassTint}" stroke="#475569" stroke-width="1" />
      <circle cx="${viewW - 30}" cy="46" r="7" fill="${cBoundary}" stroke="#475569" stroke-width="1" />
    </g>
  `);

  parts.push('</svg>');
  return parts.join('\n');
}
