import React, { useMemo } from 'react';

/**
 * ARCHITECTURAL ROOM PALETTE (Professional CAD Monochrome & Restrained Drafting Tones)
 */
const ROOM_COLORS = {
  living_room:    { fill: '#ffffff', stroke: '#0f172a' },
  drawing_room:   { fill: '#ffffff', stroke: '#0f172a' },
  bedroom:        { fill: '#ffffff', stroke: '#0f172a' },
  master_bedroom: { fill: '#ffffff', stroke: '#0f172a' },
  guest_room:     { fill: '#ffffff', stroke: '#0f172a' },
  kitchen:        { fill: '#ffffff', stroke: '#0f172a' },
  dining_room:    { fill: '#ffffff', stroke: '#0f172a' },
  bathroom:       { fill: '#f8fafc', stroke: '#0f172a' },
  toilet:         { fill: '#f8fafc', stroke: '#0f172a' },
  foyer:          { fill: '#ffffff', stroke: '#0f172a' },
  pooja_room:     { fill: '#ffffff', stroke: '#0f172a' },
  pooja:          { fill: '#ffffff', stroke: '#0f172a' },
  study_room:     { fill: '#ffffff', stroke: '#0f172a' },
  study:          { fill: '#ffffff', stroke: '#0f172a' },
  staircase:      { fill: '#f8fafc', stroke: '#0f172a' },
  stairs:         { fill: '#f8fafc', stroke: '#0f172a' },
  corridor:       { fill: '#ffffff', stroke: '#334155' },
  hallway:        { fill: '#ffffff', stroke: '#334155' },
  utility_room:   { fill: '#f8fafc', stroke: '#334155' },
  utility:        { fill: '#f8fafc', stroke: '#334155' },
  store_room:     { fill: '#f8fafc', stroke: '#334155' },
  store:          { fill: '#f8fafc', stroke: '#334155' },
  balcony:        { fill: '#ffffff', stroke: '#0f172a' },
  terrace:        { fill: '#ffffff', stroke: '#0f172a' },
  parking:        { fill: '#f8fafc', stroke: '#0f172a' },
  garage:         { fill: '#f8fafc', stroke: '#0f172a' },
  default:        { fill: '#ffffff', stroke: '#0f172a' },
};

function getRoomColor(type) {
  if (!type) return ROOM_COLORS.default;
  const key = type.toLowerCase().replace(/\s+/g, '_');
  return ROOM_COLORS[key] || ROOM_COLORS.default;
}

function formatFtIn(val) {
  if (val === undefined || val === null) return '';
  const rounded = Math.round(val * 10) / 10;
  const ft = Math.floor(rounded);
  const inch = Math.round((rounded - ft) * 12);
  return inch > 0 ? `${ft}'-${inch}"` : `${ft}'-0"`;
}

function formatMeters(val) {
  if (val === undefined || val === null) return '';
  return (val * 0.3048).toFixed(2);
}

// ─── Precision Engineering Grid Lines ───────────────────────────────────────
function ArchitecturalGrid({ width, length }) {
  const lines = [];
  for (let x = 0; x <= width; x += 5) {
    const isMajor = x % 10 === 0;
    lines.push(
      <line
        key={`gx-${x}`}
        x1={x} y1={0} x2={x} y2={length}
        stroke="#e2e8f0"
        strokeWidth={isMajor ? 0.04 : 0.02}
        opacity={isMajor ? 0.6 : 0.35}
      />
    );
  }
  for (let y = 0; y <= length; y += 5) {
    const isMajor = y % 10 === 0;
    lines.push(
      <line
        key={`gy-${y}`}
        x1={0} y1={y} x2={width} y2={y}
        stroke="#e2e8f0"
        strokeWidth={isMajor ? 0.04 : 0.02}
        opacity={isMajor ? 0.6 : 0.35}
      />
    );
  }
  return <g className="arch-grid">{lines}</g>;
}

// ─── Structural RCC Columns Generator & Numbered Tags ───────────────────────
function StructuralColumns({ rooms, plotWidth, plotLength }) {
  const columns = useMemo(() => {
    if (!rooms || rooms.length === 0) return [];
    const pts = [];

    // 1. Gather room corners
    rooms.forEach(r => {
      pts.push({ x: r.x, y: r.y });
      pts.push({ x: r.x + r.width, y: r.y });
      pts.push({ x: r.x, y: r.y + r.length });
      pts.push({ x: r.x + r.width, y: r.y + r.length });
    });

    // 2. Cluster close points (tolerance 1.4 ft)
    const clusters = [];
    pts.forEach(p => {
      const match = clusters.find(c => Math.hypot(c.x - p.x, c.y - p.y) < 1.4);
      if (match) {
        match.count += 1;
      } else {
        clusters.push({ x: p.x, y: p.y, count: 1 });
      }
    });

    // 3. Add intermediate columns for spans > 16 ft between aligned columns
    const finalCols = [...clusters];
    for (let i = 0; i < clusters.length; i++) {
      for (let j = i + 1; j < clusters.length; j++) {
        const c1 = clusters[i];
        const c2 = clusters[j];
        if (Math.abs(c1.y - c2.y) < 0.6 && Math.abs(c1.x - c2.x) >= 16.0 && Math.abs(c1.x - c2.x) <= 24.0) {
          const midX = (c1.x + c2.x) / 2;
          if (!finalCols.some(c => Math.hypot(c.x - midX, c.y - c1.y) < 4.0)) {
            finalCols.push({ x: midX, y: c1.y, count: 1 });
          }
        }
      }
    }

    // 4. Sort columns: Top to bottom (Y ascending), then Left to right (X ascending)
    finalCols.sort((a, b) => {
      if (Math.abs(a.y - b.y) > 2.0) return a.y - b.y;
      return a.x - b.x;
    });

    // 5. Build column objects with numbered callout tags
    const colW = 0.85;
    const colL = 1.35;
    return finalCols.map((col, idx) => {
      const numStr = String(idx + 1).padStart(2, '0');
      // Position tag slightly offset from column
      const tagOffset = 1.4;
      const isNearLeft = col.x < plotWidth * 0.4;
      const isNearRight = col.x > plotWidth * 0.6;
      const isNearTop = col.y < plotLength * 0.4;

      let tagX = col.x + (isNearLeft ? -tagOffset : isNearRight ? tagOffset : 0);
      let tagY = col.y + (isNearTop ? -tagOffset : tagOffset);
      if (!isNearLeft && !isNearRight) tagX += 1.2;

      return {
        id: `col-${idx + 1}`,
        x: col.x - colW / 2,
        y: col.y - colL / 2,
        w: colW,
        l: colL,
        tag: `(${numStr})`,
        tagX,
        tagY,
      };
    });
  }, [rooms, plotWidth, plotLength]);

  return (
    <g className="structural-columns">
      {columns.map(c => (
        <g key={c.id}>
          {/* Heavy black RCC Column */}
          <rect
            x={c.x} y={c.y}
            width={c.w} height={c.l}
            fill="#0f172a"
            stroke="#ffffff"
            strokeWidth={0.06}
          />
          {/* Connecting leader line from column to bubble */}
          <line
            x1={c.x + c.w / 2} y1={c.y + c.l / 2}
            x2={c.tagX} y2={c.tagY}
            stroke="#0f172a"
            strokeWidth={0.05}
            strokeDasharray="0.2 0.15"
          />
          {/* Numbered Tag Circle */}
          <circle
            cx={c.tagX} cy={c.tagY}
            r={0.72}
            fill="#ffffff"
            stroke="#0f172a"
            strokeWidth={0.09}
          />
          <text
            x={c.tagX} y={c.tagY + 0.05}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={0.42} fontWeight="bold" fill="#0f172a"
            fontFamily="'JetBrains Mono', 'Segoe UI', monospace"
          >
            {c.tag}
          </text>
        </g>
      ))}
    </g>
  );
}

// ─── Built-in Architectural Fixtures (Kitchen counter, W.C., W.B., Wardrobes) ─
function RoomFixtures({ room }) {
  if (!room) return null;
  const { x, y, width: w, length: l, type } = room;
  const rtype = (type || '').toLowerCase();

  // 1. Kitchen Cooking Platform ('KIT./OTTA') & Stainless Steel Sink
  if (rtype.includes('kitchen')) {
    const counterDepth = Math.min(2.0, l * 0.28);
    const counterLen = Math.min(w - 1.0, 10.0);
    const sinkW = 2.2;
    const sinkL = 1.4;
    const sinkX = x + 1.2;
    const sinkY = y + 0.3;

    return (
      <g className="kitchen-fixtures" style={{ pointerEvents: 'none' }}>
        {/* Counter platform along top wall */}
        <rect
          x={x} y={y}
          width={counterLen} height={counterDepth}
          fill="#f8fafc" stroke="#334155" strokeWidth={0.12}
        />
        {/* Fascia double line */}
        <line
          x1={x} y1={y + counterDepth - 0.2}
          x2={x + counterLen} y2={y + counterDepth - 0.2}
          stroke="#94a3b8" strokeWidth={0.06}
        />
        {/* Stainless Steel Sink Symbol */}
        <rect
          x={sinkX} y={sinkY}
          width={sinkW} height={sinkL}
          fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} rx={0.2}
        />
        <rect
          x={sinkX + 0.2} y={sinkY + 0.2}
          width={sinkW - 0.4} height={sinkL - 0.4}
          fill="#f1f5f9" stroke="#0284c7" strokeWidth={0.08} rx={0.15}
        />
        {/* Drain hole */}
        <circle cx={sinkX + sinkW / 2} cy={sinkY + sinkL / 2} r={0.14} fill="#0f172a" />
        {/* Faucet */}
        <circle cx={sinkX + sinkW / 2} cy={sinkY + 0.25} r={0.09} fill="#0f172a" />
        <line x1={sinkX + sinkW / 2} y1={sinkY + 0.25} x2={sinkX + sinkW / 2} y2={sinkY + 0.55} stroke="#0f172a" strokeWidth={0.08} />

        {/* Counter Callout Label */}
        <text
          x={x + counterLen / 2 + 1.5} y={y + counterDepth / 2}
          fontSize={0.42} fontWeight="bold" fill="#475569"
          fontFamily="'JetBrains Mono', monospace"
        >
          KIT. / OTTA (0.60M)
        </text>
      </g>
    );
  }

  // 2. Bathroom / Toilet: Water Closet (W.C.), Wash Basin (W.B.) & Shower
  if (rtype.includes('bath') || rtype.includes('toilet')) {
    const wcX = x + Math.min(1.2, w * 0.25);
    const wcY = y + 0.35;
    const wbX = x + w - 1.8;
    const wbY = y + 0.35;

    return (
      <g className="bathroom-fixtures" style={{ pointerEvents: 'none' }}>
        {/* Water Closet (W.C.) Commode */}
        <g transform={`translate(${wcX}, ${wcY})`}>
          {/* Cistern Tank */}
          <rect x={-0.8} y={0} width={1.6} height={0.65} fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} rx={0.1} />
          {/* Commode Bowl Oval */}
          <ellipse cx={0} cy={1.45} rx={0.58} ry={0.78} fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} />
          {/* Inner seat opening */}
          <ellipse cx={0} cy={1.48} rx={0.38} ry={0.54} fill="#f1f5f9" stroke="#64748b" strokeWidth={0.06} />
          <text x={0} y={2.6} fontSize={0.42} fontWeight="bold" fill="#0f172a" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
            W.C.
          </text>
        </g>

        {/* Wash Basin (W.B.) */}
        <g transform={`translate(${wbX}, ${wbY})`}>
          <path
            d="M -0.7 0 L 0.7 0 Q 0.7 1.1 0 1.2 Q -0.7 1.1 -0.7 0 Z"
            fill="#ffffff" stroke="#0f172a" strokeWidth={0.10}
          />
          <circle cx={0} cy={0.2} r={0.08} fill="#0f172a" />
          <circle cx={0} cy={0.65} r={0.10} fill="#64748b" />
          <text x={0} y={1.7} fontSize={0.42} fontWeight="bold" fill="#0f172a" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
            W.B.
          </text>
        </g>

        {/* Wet/Dry Shower Area Threshold */}
        {l >= 6.0 && (
          <line
            x1={x + 0.3} y1={y + l - 2.8}
            x2={x + w - 0.3} y2={y + l - 2.8}
            stroke="#94a3b8" strokeWidth={0.10} strokeDasharray="0.3 0.2"
          />
        )}
      </g>
    );
  }

  // 3. Bedroom: Built-in Cupboard / Wardrobe ('C.B.') with Vertical Louvers
  if (rtype.includes('bedroom')) {
    const cbDepth = Math.min(2.0, l * 0.2);
    const cbWidth = Math.min(5.5, w * 0.45);
    const cbX = x + w - cbWidth - 0.4;
    const cbY = y + 0.4;
    const slats = [];
    for (let sx = cbX + 0.35; sx < cbX + cbWidth - 0.2; sx += 0.35) {
      slats.push(
        <line
          key={`slat-${sx}`}
          x1={sx} y1={cbY} x2={sx} y2={cbY + cbDepth}
          stroke="#94a3b8" strokeWidth={0.06}
        />
      );
    }

    return (
      <g className="bedroom-fixtures" style={{ pointerEvents: 'none' }}>
        {/* Wardrobe boundary */}
        <rect
          x={cbX} y={cbY}
          width={cbWidth} height={cbDepth}
          fill="#f8fafc" stroke="#0f172a" strokeWidth={0.14}
        />
        {/* Louver slat lines */}
        {slats}
        {/* Cupboard label badge */}
        <rect
          x={cbX + cbWidth / 2 - 0.9} y={cbY + cbDepth / 2 - 0.32}
          width={1.8} height={0.64}
          fill="#ffffff" stroke="#0f172a" strokeWidth={0.08}
        />
        <text
          x={cbX + cbWidth / 2} y={cbY + cbDepth / 2 + 0.04}
          fontSize={0.42} fontWeight="bold" fill="#0f172a" textAnchor="middle" dominantBaseline="middle"
          fontFamily="'JetBrains Mono', monospace"
        >
          C.B.
        </text>
      </g>
    );
  }

  // 4. Store Room: Overhead Storage Loft Projection ('LOFT')
  if (rtype.includes('store') || rtype.includes('utility')) {
    return (
      <g className="store-fixtures" style={{ pointerEvents: 'none' }}>
        <line
          x1={x} y1={y + Math.min(2.4, l * 0.4)}
          x2={x + w} y2={y + Math.min(2.4, l * 0.4)}
          stroke="#475569" strokeWidth={0.12} strokeDasharray="0.4 0.2"
        />
        <text
          x={x + w / 2} y={y + 1.2}
          fontSize={0.45} fontWeight="bold" fill="#64748b" textAnchor="middle" dominantBaseline="middle"
          fontFamily="'JetBrains Mono', monospace"
        >
          LOFT / POTHMALA
        </text>
      </g>
    );
  }

  // 5. Pooja Room: Sacred Mandir Platform
  if (rtype.includes('pooja')) {
    const pw = Math.min(w - 1.2, 4.0);
    const pl = Math.min(l - 1.2, 1.8);
    const px = x + (w - pw) / 2;
    const py = y + 0.4;
    return (
      <g className="pooja-fixtures" style={{ pointerEvents: 'none' }}>
        <rect x={px} y={py} width={pw} height={pl} fill="#fefce8" stroke="#854d0e" strokeWidth={0.12} rx={0.2} />
        <rect x={px + 0.3} y={py + 0.3} width={pw - 0.6} height={pl - 0.6} fill="#ffffff" stroke="#854d0e" strokeWidth={0.08} />
        <text x={px + pw / 2} y={py + pl / 2} fontSize={0.42} fontWeight="bold" fill="#854d0e" textAnchor="middle" dominantBaseline="middle">
          MANDIR
        </text>
      </g>
    );
  }

  return null;
}

// ─── Subtle Outdoor / Site Areas ────────────────────────────────────────────
function SiteAreaShape({ area, isHovered, onHover, onClick }) {
  const type = area.type?.toLowerCase() || '';
  const isGarden = type.includes('garden') || type.includes('lawn');
  const isTerrace = type.includes('terrace');
  const isRoof = type.includes('roof');
  const isYard = type.includes('yard');
  const isParking = type.includes('park') || type.includes('garage');

  let fill = '#ffffff';
  let stroke = '#0f172a';
  let strokeDash = '0.6 0.3';

  if (isGarden) {
    fill = '#ffffff';
    stroke = '#0f172a';
  } else if (isTerrace) {
    fill = '#ffffff';
    stroke = '#0f172a';
  } else if (isRoof) {
    fill = '#f8fafc';
    stroke = '#475569';
    strokeDash = '0.8 0.4';
  } else if (isYard) {
    fill = '#ffffff';
    stroke = '#475569';
  } else if (isParking) {
    fill = '#ffffff';
    stroke = '#0f172a';
    strokeDash = 'none';
  }

  const cx = area.metadata?.center?.x ?? (area.x + area.width / 2);
  const cy = area.metadata?.center?.y ?? (area.y + area.length / 2);
  const displayLabel = (area.label || type.replace(/_/g, ' ')).toUpperCase();
  const isPolygon = area.polygon && area.polygon.length > 2;
  const polyPoints = isPolygon ? area.polygon.map(p => `${p.x},${p.y}`).join(' ') : '';
  const labelSize = Math.max(0.65, Math.min(0.95, Math.min(area.width, area.length) * 0.08));

  return (
    <g
      style={{ cursor: 'pointer', opacity: isHovered ? 1.0 : 0.95 }}
      onMouseEnter={() => onHover && onHover(area.id)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onClick && onClick(area)}
    >
      {isPolygon ? (
        <polygon
          points={polyPoints}
          fill={fill}
          stroke={stroke}
          strokeWidth={0.20}
          strokeDasharray={strokeDash}
        />
      ) : (
        <rect
          x={area.x} y={area.y}
          width={area.width} height={area.length}
          fill={fill}
          stroke={stroke}
          strokeWidth={0.20}
          strokeDasharray={strokeDash}
        />
      )}

      {/* Real CAD Stipple Pattern for Lawn */}
      {isGarden && (
        isPolygon ? (
          <polygon points={polyPoints} fill="url(#cad-lawn-stipple)" style={{ pointerEvents: 'none' }} />
        ) : (
          <rect x={area.x} y={area.y} width={area.width} height={area.length} fill="url(#cad-lawn-stipple)" style={{ pointerEvents: 'none' }} />
        )
      )}

      {isRoof && (
        isPolygon ? (
          <polygon points={polyPoints} fill="url(#roof-pattern)" style={{ pointerEvents: 'none' }} />
        ) : (
          <rect x={area.x} y={area.y} width={area.width} height={area.length} fill="url(#roof-pattern)" style={{ pointerEvents: 'none' }} />
        )
      )}

      {/* Discrete architectural annotation */}
      {area.width >= 4 && area.length >= 4 && (
        <g style={{ pointerEvents: 'none', fontFamily: "'JetBrains Mono', 'Segoe UI', monospace" }}>
          <text
            x={cx} y={cy - 0.4}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={labelSize}
            fontWeight="bold"
            fill="#0f172a"
            letterSpacing="0.06em"
          >
            {isGarden ? 'RAISED LAWN' : displayLabel}
          </text>
          <text
            x={cx} y={cy + 0.6}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={labelSize * 0.8}
            fontWeight="600"
            fill="#475569"
          >
            {formatMeters(area.width)}X{formatMeters(area.length)} ({formatFtIn(area.width)} × {formatFtIn(area.length)})
          </text>
        </g>
      )}
    </g>
  );
}

// ─── Indoor Room Shape with Two-Line CAD Typography & Built-in Fixtures ────
function RoomShape({ room, isHovered, onHover, onClick }) {
  const color = getRoomColor(room.type);
  const fill = isHovered ? '#f1f5f9' : color.fill;
  const strokeW = 0.22;
  const roomType = room.type?.toLowerCase() || '';

  const cx = room.x + room.width / 2;
  const cy = room.y + room.length / 2;
  const minDim = Math.min(room.width, room.length);

  // Scaled CAD typography
  let titleSize = 0.90;
  let subSize = 0.62;
  let isCompact = false;

  if (minDim >= 12.0) {
    titleSize = 1.05;
    subSize = 0.70;
  } else if (minDim >= 8.0) {
    titleSize = 0.88;
    subSize = 0.60;
  } else if (minDim >= 5.5) {
    titleSize = 0.74;
    subSize = 0.52;
  } else {
    titleSize = 0.58;
    subSize = 0.44;
    isCompact = true;
  }

  // Format label matching CAD standard (e.g. LIVING HALL, BED ROOM, KIT./DINING)
  let displayLabel = (room.label || room.type?.replace(/_/g, ' ') || 'ROOM').toUpperCase();
  if (displayLabel.includes('LIVING')) displayLabel = 'LIVING HALL';
  if (displayLabel.includes('KITCHEN') && !displayLabel.includes('DINING')) displayLabel = 'KITCHEN';

  const isPolygon = room.polygon && room.polygon.length > 2;
  const polyPoints = isPolygon ? room.polygon.map(p => `${p.x},${p.y}`).join(' ') : '';

  return (
    <g
      style={{ cursor: 'pointer' }}
      onMouseEnter={() => onHover && onHover(room.id)}
      onMouseLeave={() => onHover && onHover(null)}
      onClick={() => onClick && onClick(room)}
    >
      {/* Room boundary */}
      {isPolygon ? (
        <polygon
          points={polyPoints}
          fill={fill}
          stroke={color.stroke}
          strokeWidth={strokeW}
        />
      ) : (
        <rect
          x={room.x} y={room.y}
          width={room.width} height={room.length}
          fill={fill}
          stroke={color.stroke}
          strokeWidth={strokeW}
        />
      )}

      {/* Built-in Architectural Fixtures Layer */}
      <RoomFixtures room={room} />

      {/* CAD Two-Line Typography Hierarchy (ROOM NAME + DIMENSIONS) */}
      {isCompact ? (
        <g style={{ pointerEvents: 'none', fontFamily: "'Segoe UI', 'Inter', sans-serif" }}>
          <text
            x={cx} y={cy - subSize * 0.6}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={titleSize} fontWeight="bold" fill="#0f172a"
            letterSpacing="0.02em"
          >
            {displayLabel}
          </text>
          <text
            x={cx} y={cy + subSize * 0.7}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={subSize} fontWeight="600" fill="#334155"
          >
            {formatMeters(room.width)}X{formatMeters(room.length)}
          </text>
        </g>
      ) : (
        <g style={{ pointerEvents: 'none', fontFamily: "'Segoe UI', 'Inter', sans-serif" }}>
          <text
            x={cx} y={cy - subSize * 1.1}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={titleSize} fontWeight="bold" fill="#0f172a"
            letterSpacing="0.04em"
          >
            {displayLabel}
          </text>
          <text
            x={cx} y={cy + subSize * 0.25}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={subSize} fontWeight="bold" fill="#0f172a"
            fontFamily="'JetBrains Mono', monospace"
          >
            {formatMeters(room.width)}X{formatMeters(room.length)}
          </text>
          <text
            x={cx} y={cy + subSize * 1.55}
            textAnchor="middle" dominantBaseline="middle"
            fontSize={subSize * 0.85} fontWeight="500" fill="#475569"
            fontFamily="'JetBrains Mono', monospace"
          >
            ({formatFtIn(room.width)} × {formatFtIn(room.length)})
          </text>
        </g>
      )}
    </g>
  );
}

// ─── Wall Lines with Proper Hierarchy & Clean Caps ──────────────────────────
function WallLines({ walls }) {
  if (!walls || walls.length === 0) return null;
  return (
    <g className="arch-walls">
      {walls.map((wall, idx) => {
        const isExterior = wall.type === 'exterior';
        return (
          <line
            key={wall.id || `w-${idx}`}
            x1={wall.start.x} y1={wall.start.y}
            x2={wall.end.x}   y2={wall.end.y}
            stroke="#0f172a"
            strokeWidth={isExterior ? 0.75 : 0.38}
            strokeLinecap="square"
            strokeLinejoin="miter"
          />
        );
      })}
    </g>
  );
}

// ─── Architectural Doors (Real Gap, Opening Arc & Leaf, Architectural Code Tag) ─
function DoorShape({ door, rooms }) {
  if (!door || !door.position) return null;
  const { x, y } = door.position;
  const dw = door.width || 3.0;
  const isMainEntrance = door.type === 'main_entrance';
  const strokeColor = isMainEntrance ? '#dc2626' : '#0f172a';
  const strokeW = isMainEntrance ? 0.24 : 0.14;
  const gapThickness = 0.95; // Mask thick walls cleanly

  // Find owning room
  const ownerRoom = rooms?.find(r => door.room_ids?.includes(r.id));
  const rtype = (ownerRoom?.type || '').toLowerCase();

  // Architectural Code Tag (D, D1, D2)
  let doorCode = 'D1';
  let doorDim = '0.90X2.10';
  if (isMainEntrance) {
    doorCode = 'D';
    doorDim = '1.00X2.10';
  } else if (rtype.includes('bath') || rtype.includes('toilet') || rtype.includes('store') || rtype.includes('balcony')) {
    doorCode = 'D2';
    doorDim = '0.75X2.10';
  }

  let orientation = 'south'; // default
  if (ownerRoom) {
    const eps = 1.0;
    if (Math.abs(y - ownerRoom.y) < eps) orientation = 'north';
    else if (Math.abs(y - (ownerRoom.y + ownerRoom.length)) < eps) orientation = 'south';
    else if (Math.abs(x - ownerRoom.x) < eps) orientation = 'west';
    else if (Math.abs(x - (ownerRoom.x + ownerRoom.width)) < eps) orientation = 'east';
  }

  if (orientation === 'north') {
    const wallY = ownerRoom ? ownerRoom.y : y;
    return (
      <g key={door.id || `door-${x}-${y}`}>
        <rect x={x} y={wallY - gapThickness / 2} width={dw} height={gapThickness} fill="#ffffff" />
        <line x1={x} y1={wallY - 0.4} x2={x} y2={wallY + 0.4} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={x + dw} y1={wallY - 0.4} x2={x + dw} y2={wallY + 0.4} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={x} y1={wallY} x2={x} y2={wallY + dw} stroke={strokeColor} strokeWidth={strokeW} />
        <path d={`M ${x} ${wallY + dw} A ${dw} ${dw} 0 0 0 ${x + dw} ${wallY}`} fill="none" stroke={strokeColor} strokeWidth={strokeW * 0.8} strokeDasharray="0.3 0.15" />
        {/* Door Code Callout */}
        <g fontFamily="'JetBrains Mono', monospace">
          <text x={x + dw / 2} y={wallY + dw + 0.55} fontSize={0.38} fontWeight="bold" fill={strokeColor} textAnchor="middle">
            {doorCode} ({doorDim})
          </text>
        </g>
        {isMainEntrance && (
          <g>
            <rect x={x + dw / 2 - 1.4} y={wallY - 1.3} width={2.8} height={0.7} fill="#dc2626" rx={0.2} />
            <text x={x + dw / 2} y={wallY - 0.85} fontSize={0.42} fontWeight="bold" fill="#ffffff" textAnchor="middle">MAIN ENTRANCE</text>
          </g>
        )}
      </g>
    );
  }

  if (orientation === 'south') {
    const wallY = ownerRoom ? (ownerRoom.y + ownerRoom.length) : y;
    return (
      <g key={door.id || `door-${x}-${y}`}>
        <rect x={x} y={wallY - gapThickness / 2} width={dw} height={gapThickness} fill="#ffffff" />
        <line x1={x} y1={wallY - 0.4} x2={x} y2={wallY + 0.4} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={x + dw} y1={wallY - 0.4} x2={x + dw} y2={wallY + 0.4} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={x} y1={wallY} x2={x} y2={wallY - dw} stroke={strokeColor} strokeWidth={strokeW} />
        <path d={`M ${x} ${wallY - dw} A ${dw} ${dw} 0 0 1 ${x + dw} ${wallY}`} fill="none" stroke={strokeColor} strokeWidth={strokeW * 0.8} strokeDasharray="0.3 0.15" />
        <g fontFamily="'JetBrains Mono', monospace">
          <text x={x + dw / 2} y={wallY - dw - 0.3} fontSize={0.38} fontWeight="bold" fill={strokeColor} textAnchor="middle">
            {doorCode} ({doorDim})
          </text>
        </g>
        {isMainEntrance && (
          <g>
            <rect x={x + dw / 2 - 1.4} y={wallY + 0.6} width={2.8} height={0.7} fill="#dc2626" rx={0.2} />
            <text x={x + dw / 2} y={wallY + 1.05} fontSize={0.42} fontWeight="bold" fill="#ffffff" textAnchor="middle">MAIN ENTRANCE</text>
          </g>
        )}
      </g>
    );
  }

  if (orientation === 'west') {
    const wallX = ownerRoom ? ownerRoom.x : x;
    return (
      <g key={door.id || `door-${x}-${y}`}>
        <rect x={wallX - gapThickness / 2} y={y} width={gapThickness} height={dw} fill="#ffffff" />
        <line x1={wallX - 0.4} y1={y} x2={wallX + 0.4} y2={y} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={wallX - 0.4} y1={y + dw} x2={wallX + 0.4} y2={y + dw} stroke="#0f172a" strokeWidth={0.16} />
        <line x1={wallX} y1={y} x2={wallX + dw} y2={y} stroke={strokeColor} strokeWidth={strokeW} />
        <path d={`M ${wallX + dw} ${y} A ${dw} ${dw} 0 0 1 ${wallX} ${y + dw}`} fill="none" stroke={strokeColor} strokeWidth={strokeW * 0.8} strokeDasharray="0.3 0.15" />
        <g fontFamily="'JetBrains Mono', monospace">
          <text x={wallX + dw + 0.8} y={y + dw / 2} fontSize={0.38} fontWeight="bold" fill={strokeColor} textAnchor="middle" transform={`rotate(90 ${wallX + dw + 0.8} ${y + dw / 2})`}>
            {doorCode} ({doorDim})
          </text>
        </g>
        {isMainEntrance && (
          <g>
            <rect x={wallX - 2.8} y={y + dw / 2 - 0.35} width={2.6} height={0.7} fill="#dc2626" rx={0.2} />
            <text x={wallX - 1.5} y={y + dw / 2 + 0.1} fontSize={0.42} fontWeight="bold" fill="#ffffff" textAnchor="middle">MAIN ENTRY</text>
          </g>
        )}
      </g>
    );
  }

  // East wall
  const wallX = ownerRoom ? (ownerRoom.x + ownerRoom.width) : x;
  return (
    <g key={door.id || `door-${x}-${y}`}>
      <rect x={wallX - gapThickness / 2} y={y} width={gapThickness} height={dw} fill="#ffffff" />
      <line x1={wallX - 0.4} y1={y} x2={wallX + 0.4} y2={y} stroke="#0f172a" strokeWidth={0.16} />
      <line x1={wallX - 0.4} y1={y + dw} x2={wallX + 0.4} y2={y + dw} stroke="#0f172a" strokeWidth={0.16} />
      <line x1={wallX} y1={y} x2={wallX - dw} y2={y} stroke={strokeColor} strokeWidth={strokeW} />
      <path d={`M ${wallX - dw} ${y} A ${dw} ${dw} 0 0 0 ${wallX} ${y + dw}`} fill="none" stroke={strokeColor} strokeWidth={strokeW * 0.8} strokeDasharray="0.3 0.15" />
      <g fontFamily="'JetBrains Mono', monospace">
        <text x={wallX - dw - 0.8} y={y + dw / 2} fontSize={0.38} fontWeight="bold" fill={strokeColor} textAnchor="middle" transform={`rotate(-90 ${wallX - dw - 0.8} ${y + dw / 2})`}>
          {doorCode} ({doorDim})
        </text>
      </g>
      {isMainEntrance && (
        <g>
          <rect x={wallX + 0.5} y={y + dw / 2 - 0.35} width={2.6} height={0.7} fill="#dc2626" rx={0.2} />
          <text x={wallX + 1.8} y={y + dw / 2 + 0.1} fontSize={0.42} fontWeight="bold" fill="#ffffff" textAnchor="middle">MAIN ENTRY</text>
        </g>
      )}
    </g>
  );
}

// ─── Architectural Windows (Glazing, Sill & Sunshade Chhajja Projection) ───
function WindowShape({ window: win, plotWidth, plotLength, rooms }) {
  if (!win || !win.position) return null;
  const { x, y } = win.position;
  const ww = win.width || 4.0;
  const gapThickness = 0.9;
  const sillThickness = 0.42;
  const chhajjaProj = 1.5; // 1.5 ft / 0.45m RCC Sunshade projection

  // Find owner room to determine ventilator vs standard window
  const ownerRoom = rooms?.find(r => {
    if (win.room_id && r.id === win.room_id) return true;
    if (win.room_ids && win.room_ids.includes(r.id)) return true;
    return (r.x - 1.5 <= x && x <= r.x + r.width + 1.5 && r.y - 1.5 <= y && y <= r.y + r.length + 1.5);
  });
  const rtype = (ownerRoom?.type || '').toLowerCase();
  const isVentilator = rtype.includes('bath') || rtype.includes('toilet');

  let winCode = 'W';
  let winDim = '1.50X1.50';
  if (isVentilator) {
    winCode = 'V';
    winDim = '0.60X0.90';
  } else if (ww >= 5.5) {
    winCode = 'W1';
    winDim = '1.80X0.90';
  } else if (rtype.includes('kitchen')) {
    winCode = 'W3';
    winDim = '1.20X1.00';
  }

  // Detect orientation (North, South, East, West)
  const isNorthWall = y <= 3.0;
  const isSouthWall = y >= plotLength - 3.0;
  const isWestWall = x <= 3.0;
  const isEastWall = x >= plotWidth - 3.0;
  const isHorizontal = isNorthWall || isSouthWall || (!isWestWall && !isEastWall);

  if (isHorizontal) {
    const isTop = isNorthWall || y < plotLength / 2;
    const chhajjaY = isTop ? y - chhajjaProj : y + gapThickness / 2;

    return (
      <g key={win.id || `win-${x}-${y}`}>
        {/* Wall cutout */}
        <rect x={x} y={y - gapThickness / 2} width={ww} height={gapThickness} fill="#ffffff" />
        {/* Sill frame */}
        <rect x={x} y={y - sillThickness / 2} width={ww} height={sillThickness} fill="#ffffff" stroke="#0f172a" strokeWidth={0.12} />
        {/* Triple glazing lines */}
        <line x1={x} y1={y - 0.08} x2={x + ww} y2={y - 0.08} stroke="#0f172a" strokeWidth={0.08} />
        <line x1={x} y1={y + 0.08} x2={x + ww} y2={y + 0.08} stroke="#0f172a" strokeWidth={0.08} />

        {/* RCC Chhajja / Sunshade Projection (Dashed Line) */}
        <rect
          x={x - 0.5} y={chhajjaY}
          width={ww + 1.0} height={chhajjaProj}
          fill="none" stroke="#475569" strokeWidth={0.10} strokeDasharray="0.35 0.15"
        />

        {/* Window Code Tag */}
        <text
          x={x + ww / 2} y={isTop ? chhajjaY - 0.35 : chhajjaY + chhajjaProj + 0.65}
          fontSize={0.42} fontWeight="bold" fill="#0f172a" textAnchor="middle"
          fontFamily="'JetBrains Mono', monospace"
        >
          {winCode} ({winDim})
        </text>
      </g>
    );
  }

  // Vertical window on East or West wall
  const isLeft = isWestWall || x < plotWidth / 2;
  const chhajjaX = isLeft ? x - chhajjaProj : x + gapThickness / 2;

  return (
    <g key={win.id || `win-${x}-${y}`}>
      <rect x={x - gapThickness / 2} y={y} width={gapThickness} height={ww} fill="#ffffff" />
      <rect x={x - sillThickness / 2} y={y} width={sillThickness} height={ww} fill="#ffffff" stroke="#0f172a" strokeWidth={0.12} />
      <line x1={x - 0.08} y1={y} x2={x - 0.08} y2={y + ww} stroke="#0f172a" strokeWidth={0.08} />
      <line x1={x + 0.08} y1={y} x2={x + 0.08} y2={y + ww} stroke="#0f172a" strokeWidth={0.08} />

      {/* RCC Chhajja Projection */}
      <rect
        x={chhajjaX} y={y - 0.5}
        width={chhajjaProj} height={ww + 1.0}
        fill="none" stroke="#475569" strokeWidth={0.10} strokeDasharray="0.35 0.15"
      />

      {/* Window Code Tag */}
      <text
        x={isLeft ? chhajjaX - 0.4 : chhajjaX + chhajjaProj + 0.6}
        y={y + ww / 2}
        fontSize={0.42} fontWeight="bold" fill="#0f172a" textAnchor="middle" dominantBaseline="middle"
        transform={`rotate(${isLeft ? -90 : 90} ${isLeft ? chhajjaX - 0.4 : chhajjaX + chhajjaProj + 0.6} ${y + ww / 2})`}
        fontFamily="'JetBrains Mono', monospace"
      >
        {winCode} ({winDim})
      </text>
    </g>
  );
}

// ─── Authentic Numbered Staircase (Numbered Treads 1-17, Landing & Arrows) ──
function StairShape({ stair, floorLevel }) {
  if (!stair) return null;
  const { x, y, width: w, length: l } = stair;
  const isDogLegged = w >= 5.5 && l >= 8.5;
  const landingL = Math.min(3.5, l * 0.32);
  const flightL = l - landingL;
  const stepsPerFlight = 9;
  const stepH = flightL / stepsPerFlight;
  const halfW = (w - 0.4) / 2;

  const flight1Steps = [];
  const flight2Steps = [];

  for (let i = 0; i <= stepsPerFlight; i++) {
    const sy = y + l - landingL - i * stepH;
    // Flight 1 (Left going up)
    if (i < stepsPerFlight) {
      flight1Steps.push(
        <g key={`f1-${i}`}>
          <line x1={x} y1={sy} x2={x + halfW} y2={sy} stroke="#0f172a" strokeWidth={0.10} />
          <text
            x={x + halfW / 2} y={sy - stepH / 2}
            fontSize={0.34} fontWeight="bold" fill="#0f172a" textAnchor="middle" dominantBaseline="middle"
            fontFamily="'JetBrains Mono', monospace"
          >
            {i + 1}
          </text>
        </g>
      );
      // Flight 2 (Right returning)
      flight2Steps.push(
        <g key={`f2-${i}`}>
          <line x1={x + halfW + 0.4} y1={sy} x2={x + w} y2={sy} stroke="#0f172a" strokeWidth={0.10} />
          <text
            x={x + halfW + 0.4 + halfW / 2} y={sy - stepH / 2}
            fontSize={0.34} fontWeight="bold" fill="#0f172a" textAnchor="middle" dominantBaseline="middle"
            fontFamily="'JetBrains Mono', monospace"
          >
            {stepsPerFlight + (stepsPerFlight - i)}
          </text>
        </g>
      );
    }
  }

  const isUp = (floorLevel === 0);
  const dirLabel = isUp ? 'UP' : 'DN';

  return (
    <g key={stair.id || `stair-${x}-${y}`}>
      {/* Outer stair boundary */}
      <rect x={x} y={y} width={w} height={l} fill="#ffffff" stroke="#0f172a" strokeWidth={0.25} />

      {/* Mid Landing Slab */}
      <rect x={x} y={y} width={w} height={landingL} fill="#f8fafc" stroke="#0f172a" strokeWidth={0.14} />
      <text
        x={x + w / 2} y={y + landingL / 2}
        fontSize={0.42} fontWeight="bold" fill="#475569" textAnchor="middle" dominantBaseline="middle"
        fontFamily="'JetBrains Mono', monospace"
      >
        LANDING ({formatFtIn(landingL)})
      </text>

      {/* Central handrail space */}
      {isDogLegged && (
        <g>
          <line x1={x + halfW} y1={y + landingL} x2={x + halfW} y2={y + l} stroke="#0f172a" strokeWidth={0.16} />
          <line x1={x + halfW + 0.4} y1={y + landingL} x2={x + halfW + 0.4} y2={y + l} stroke="#0f172a" strokeWidth={0.16} />
        </g>
      )}

      {/* Flight steps */}
      {flight1Steps}
      {flight2Steps}

      {/* Flight Direction Arrow Path */}
      {isUp ? (
        <g style={{ pointerEvents: 'none' }}>
          {/* Start circle at step 1 */}
          <circle cx={x + halfW / 2} cy={y + l - 0.6} r={0.30} fill="#0f172a" />
          <line x1={x + halfW / 2} y1={y + l - 0.6} x2={x + halfW / 2} y2={y + landingL + 0.5} stroke="#0f172a" strokeWidth={0.14} />
          {/* Turn across landing */}
          <line x1={x + halfW / 2} y1={y + landingL + 0.5} x2={x + halfW + 0.4 + halfW / 2} y2={y + landingL + 0.5} stroke="#0f172a" strokeWidth={0.14} />
          {/* Turn down flight 2 */}
          <line x1={x + halfW + 0.4 + halfW / 2} y1={y + landingL + 0.5} x2={x + halfW + 0.4 + halfW / 2} y2={y + l - 1.2} stroke="#0f172a" strokeWidth={0.14} />
          <polygon
            points={`${x + halfW + 0.4 + halfW / 2},${y + l - 0.4} ${x + halfW + 0.4 + halfW / 2 - 0.35},${y + l - 1.2} ${x + halfW + 0.4 + halfW / 2 + 0.35},${y + l - 1.2}`}
            fill="#0f172a"
          />
          <text
            x={x + halfW / 2} y={y + l + 0.7}
            fontSize={0.55} fontWeight="bold" fill="#0f172a" textAnchor="middle"
            fontFamily="'JetBrains Mono', monospace"
          >
            UP
          </text>
        </g>
      ) : (
        <g style={{ pointerEvents: 'none' }}>
          <circle cx={x + halfW + 0.4 + halfW / 2} cy={y + l - 0.6} r={0.30} fill="#0f172a" />
          <line x1={x + halfW + 0.4 + halfW / 2} y1={y + l - 0.6} x2={x + halfW + 0.4 + halfW / 2} y2={y + landingL + 0.5} stroke="#0f172a" strokeWidth={0.14} />
          <line x1={x + halfW + 0.4 + halfW / 2} y1={y + landingL + 0.5} x2={x + halfW / 2} y2={y + landingL + 0.5} stroke="#0f172a" strokeWidth={0.14} />
          <line x1={x + halfW / 2} y1={y + landingL + 0.5} x2={x + halfW / 2} y2={y + l - 1.2} stroke="#0f172a" strokeWidth={0.14} />
          <polygon
            points={`${x + halfW / 2},${y + l - 0.4} ${x + halfW / 2 - 0.35},${y + l - 1.2} ${x + halfW / 2 + 0.35},${y + l - 1.2}`}
            fill="#0f172a"
          />
          <text
            x={x + halfW + 0.4 + halfW / 2} y={y + l + 0.7}
            fontSize={0.55} fontWeight="bold" fill="#0f172a" textAnchor="middle"
            fontFamily="'JetBrains Mono', monospace"
          >
            DN
          </text>
        </g>
      )}
    </g>
  );
}

// ─── Entrance Veranda with Steps, Level Marker & Lawn Stipple ────────────────
function VerandaAndLawn({ plot }) {
  const sb = plot.setbacks || {};
  const frontDepth = sb.front || 5.0;
  const pw = plot.width;
  const pl = plot.length;
  const facing = (plot.front_side || plot.facing || 'south').toLowerCase();

  if (facing !== 'south') return null;

  const verW = 6.0;
  const verL = 4.5;
  const verX = pw / 2 - verW / 2;
  const verY = pl - frontDepth - verL;

  return (
    <g className="arch-veranda" style={{ pointerEvents: 'none' }}>
      {/* Veranda steps leading to ground */}
      <g>
        <rect x={verX} y={verY + verL} width={verW} height={0.6} fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} />
        <rect x={verX + 0.4} y={verY + verL + 0.6} width={verW - 0.8} height={0.6} fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} />
        <rect x={verX + 0.8} y={verY + verL + 1.2} width={verW - 1.6} height={0.6} fill="#ffffff" stroke="#0f172a" strokeWidth={0.10} />
        <text x={verX + verW / 2} y={verY + verL + 1.05} fontSize={0.34} fontWeight="bold" fill="#0f172a" textAnchor="middle">
          UP
        </text>
      </g>
      {/* Veranda Level Marker */}
      <rect x={verX + verW / 2 - 1.5} y={verY + verL - 1.0} width={3.0} height={0.6} fill="#ffffff" stroke="#0f172a" strokeWidth={0.08} />
      <text x={verX + verW / 2} y={verY + verL - 0.6} fontSize={0.32} fontWeight="bold" fill="#0f172a" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
        +0.60M ROAD LVL
      </text>
    </g>
  );
}

// ─── Driveway & Gates ───────────────────────────────────────────────────────
function DrivewayAndGates({ plot }) {
  const gates = plot.gates || [];
  const dw = plot.driveway;

  return (
    <g className="arch-site-elements">
      {/* Driveway */}
      {dw && dw.points && dw.points.length > 1 && (
        <polyline
          points={dw.points.map(p => `${p.x},${p.y}`).join(' ')}
          fill="none"
          stroke="#94a3b8"
          strokeWidth={0.4}
          strokeDasharray="0.6 0.4"
        />
      )}

      {/* Gates */}
      {gates.map((g, idx) => {
        const isVehicle = g.type === 'vehicle';
        const gw = g.width || (isVehicle ? 9.0 : 3.5);
        const { x, y } = g.position || { x: 0, y: 0 };
        const label = isVehicle ? 'MAIN GATE' : 'PED. GATE';

        return (
          <g key={`gate-${idx}`}>
            <rect x={x - 0.4} y={y - 0.4} width={0.8} height={0.8} fill="#0f172a" />
            <rect x={x + gw - 0.4} y={y - 0.4} width={0.8} height={0.8} fill="#0f172a" />
            <rect x={x} y={y - 0.25} width={gw} height={0.5} fill="#0f172a" stroke="#0f172a" strokeWidth={0.1} />
            <text
              x={x + gw / 2} y={y}
              fontSize={0.42} fontWeight="bold" fill="#ffffff"
              textAnchor="middle" dominantBaseline="middle"
              style={{ pointerEvents: 'none', letterSpacing: '0.04em' }}
            >
              {label} ({formatFtIn(gw)})
            </text>
          </g>
        );
      })}
    </g>
  );
}

// ─── Road Representation with CAD Double Arrow & Level Marker ───────────────
function RoadElement({ plot }) {
  const facing = (plot.front_side || plot.facing || 'south').toLowerCase();
  const pw = plot.width;
  const pl = plot.length;
  const roadWidth = 30; // standard 30-ft road

  if (facing === 'south') {
    const yPos = pl + 1.5;
    return (
      <g className="arch-road">
        <line x1={-6} y1={yPos} x2={pw + 6} y2={yPos} stroke="#0f172a" strokeWidth={0.5} />
        <line x1={-6} y1={yPos + 2.5} x2={pw + 6} y2={yPos + 2.5} stroke="#94a3b8" strokeWidth={0.2} strokeDasharray="1.5 1.0" />
        <line x1={-6} y1={yPos + 5.0} x2={pw + 6} y2={yPos + 5.0} stroke="#0f172a" strokeWidth={0.5} />

        {/* Level badge */}
        <rect x={pw / 2 - 2.0} y={yPos + 0.4} width={4.0} height={0.65} fill="#ffffff" stroke="#0f172a" strokeWidth={0.08} />
        <text x={pw / 2} y={yPos + 0.85} fontSize={0.34} fontWeight="bold" fill="#0f172a" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
          0.0 M ROAD LVL
        </text>

        {/* CAD Double Arrow Road Name */}
        <text
          x={pw / 2} y={yPos + 3.0}
          fontSize={1.1} fontWeight="800" fill="#0f172a"
          textAnchor="middle" dominantBaseline="middle"
          letterSpacing="0.18em"
          fontFamily="'Segoe UI', 'Inter', sans-serif"
        >
          &lt;==== R O A D ====&gt;
        </text>
        <text
          x={pw / 2} y={yPos + 4.3}
          fontSize={0.48} fontWeight="600" fill="#64748b"
          textAnchor="middle"
        >
          {roadWidth}'-0" WIDE ACCESS ROAD ({facing.toUpperCase()} FACING)
        </text>
      </g>
    );
  }

  if (facing === 'north') {
    const yPos = -1.5;
    return (
      <g className="arch-road">
        <line x1={-6} y1={yPos} x2={pw + 6} y2={yPos} stroke="#0f172a" strokeWidth={0.5} />
        <line x1={-6} y1={yPos - 2.5} x2={pw + 6} y2={yPos - 2.5} stroke="#94a3b8" strokeWidth={0.2} strokeDasharray="1.5 1.0" />
        <line x1={-6} y1={yPos - 5.0} x2={pw + 6} y2={yPos - 5.0} stroke="#0f172a" strokeWidth={0.5} />

        <rect x={pw / 2 - 2.0} y={yPos - 1.05} width={4.0} height={0.65} fill="#ffffff" stroke="#0f172a" strokeWidth={0.08} />
        <text x={pw / 2} y={yPos - 0.6} fontSize={0.34} fontWeight="bold" fill="#0f172a" textAnchor="middle" fontFamily="'JetBrains Mono', monospace">
          0.0 M ROAD LVL
        </text>

        <text
          x={pw / 2} y={yPos - 3.0}
          fontSize={1.1} fontWeight="800" fill="#0f172a"
          textAnchor="middle" dominantBaseline="middle"
          letterSpacing="0.18em"
        >
          &lt;==== R O A D ====&gt;
        </text>
      </g>
    );
  }

  if (facing === 'east') {
    const xPos = pw + 1.5;
    return (
      <g className="arch-road">
        <line x1={xPos} y1={-6} x2={xPos} y2={pl + 6} stroke="#0f172a" strokeWidth={0.5} />
        <line x1={xPos + 2.5} y1={-6} x2={xPos + 2.5} y2={pl + 6} stroke="#94a3b8" strokeWidth={0.2} strokeDasharray="1.5 1.0" />
        <line x1={xPos + 5.0} y1={-6} x2={xPos + 5.0} y2={pl + 6} stroke="#0f172a" strokeWidth={0.5} />
        <text
          x={xPos + 2.5} y={pl / 2}
          fontSize={1.1} fontWeight="800" fill="#0f172a"
          textAnchor="middle" dominantBaseline="middle"
          transform={`rotate(90, ${xPos + 2.5}, ${pl / 2})`}
          letterSpacing="0.18em"
        >
          &lt;==== R O A D ====&gt;
        </text>
      </g>
    );
  }

  // West facing
  const xPos = -1.5;
  return (
    <g className="arch-road">
      <line x1={xPos} y1={-6} x2={xPos} y2={pl + 6} stroke="#0f172a" strokeWidth={0.5} />
      <line x1={xPos - 2.5} y1={-6} x2={xPos - 2.5} y2={pl + 6} stroke="#94a3b8" strokeWidth={0.2} strokeDasharray="1.5 1.0" />
      <line x1={xPos - 5.0} y1={-6} x2={xPos - 5.0} y2={pl + 6} stroke="#0f172a" strokeWidth={0.5} />
      <text
        x={xPos - 2.5} y={pl / 2}
        fontSize={1.1} fontWeight="800" fill="#0f172a"
        textAnchor="middle" dominantBaseline="middle"
        transform={`rotate(-90, ${xPos - 2.5}, ${pl / 2})`}
        letterSpacing="0.18em"
      >
        &lt;==== R O A D ====&gt;
      </text>
    </g>
  );
}

// ─── Setback Dimension Lines & Labels ───────────────────────────────────────
function SetbackDimensionAnnotations({ plot }) {
  const sb = plot.setbacks;
  if (!sb) return null;
  const pw = plot.width;
  const pl = plot.length;

  return (
    <g className="arch-setbacks" fontSize={0.65} fontFamily="'JetBrains Mono', monospace" fill="#64748b" textAnchor="middle" dominantBaseline="middle">
      {sb.front > 0 && (
        <text x={pw / 2} y={sb.front / 2} letterSpacing="0.06em">
          FRONT SETBACK {formatFtIn(sb.front)} ({formatMeters(sb.front)}M)
        </text>
      )}
      {sb.rear > 0 && (
        <text x={pw / 2} y={pl - sb.rear / 2} letterSpacing="0.06em">
          REAR SETBACK {formatFtIn(sb.rear)} ({formatMeters(sb.rear)}M)
        </text>
      )}
      {sb.left > 0 && (
        <text x={sb.left / 2} y={pl / 2} transform={`rotate(-90, ${sb.left / 2}, ${pl / 2})`} letterSpacing="0.06em">
          LEFT SETBACK {formatFtIn(sb.left)}
        </text>
      )}
      {sb.right > 0 && (
        <text x={pw - sb.right / 2} y={pl / 2} transform={`rotate(90, ${pw - sb.right / 2}, ${pl / 2})`} letterSpacing="0.06em">
          RIGHT SETBACK {formatFtIn(sb.right)}
        </text>
      )}
    </g>
  );
}

// ─── External Dimension Lines with 45° Architectural Slash Ticks ─────────────
function ExternalDimensions({ plot, facing }) {
  const { width, length } = plot;
  const tickSize = 0.65;
  const offset = 2.4;
  const fontSize = Math.max(0.85, Math.min(1.2, width * 0.035));
  const isEastFacing = (facing || '').toLowerCase() === 'east';

  const ArchTick = ({ x, y }) => (
    <line
      x1={x - tickSize / 2} y1={y + tickSize / 2}
      x2={x + tickSize / 2} y2={y - tickSize / 2}
      stroke="#0f172a" strokeWidth={0.16}
    />
  );

  const dimX = isEastFacing ? -offset : width + offset;
  const extX = isEastFacing ? -offset - 0.8 : width + offset + 0.8;
  const textX = isEastFacing ? -offset - 0.8 : width + offset + 0.8;
  const rot = isEastFacing ? -90 : 90;

  return (
    <g className="arch-dimensions" stroke="#0f172a" fill="#0f172a" fontFamily="'JetBrains Mono', monospace">
      {/* Top Dimension Line (Width) */}
      <line x1={0} y1={-offset} x2={width} y2={-offset} strokeWidth={0.12} />
      <line x1={0} y1={-offset - 0.8} x2={0} y2={0} strokeWidth={0.08} strokeDasharray="0.3 0.15" opacity={0.6} />
      <line x1={width} y1={-offset - 0.8} x2={width} y2={0} strokeWidth={0.08} strokeDasharray="0.3 0.15" opacity={0.6} />
      <ArchTick x={0} y={-offset} />
      <ArchTick x={width} y={-offset} />
      <text
        x={width / 2} y={-offset - 0.6}
        textAnchor="middle" fontSize={fontSize} fontWeight="700" stroke="none"
      >
        PLOT WIDTH: {formatFtIn(width)} ({formatMeters(width)} M)
      </text>

      {/* Side Dimension Line (Length) */}
      <line x1={dimX} y1={0} x2={dimX} y2={length} strokeWidth={0.12} />
      <line x1={isEastFacing ? 0 : width} y1={0} x2={extX} y2={0} strokeWidth={0.08} strokeDasharray="0.3 0.15" opacity={0.6} />
      <line x1={isEastFacing ? 0 : width} y1={length} x2={extX} y2={length} strokeWidth={0.08} strokeDasharray="0.3 0.15" opacity={0.6} />
      <ArchTick x={dimX} y={0} />
      <ArchTick x={dimX} y={length} />
      <text
        x={textX} y={length / 2}
        textAnchor="middle" dominantBaseline="middle"
        fontSize={fontSize} fontWeight="700" stroke="none"
        transform={`rotate(${rot}, ${textX}, ${length / 2})`}
      >
        PLOT LENGTH: {formatFtIn(length)} ({formatMeters(length)} M)
      </text>
    </g>
  );
}

// ─── Precision Architectural Compass Rose / North Arrow ──────────────────────
function ArchitecturalCompass({ x, y, facing }) {
  const facingLower = (facing || 'south').toLowerCase();
  let rotation = 0;
  if (facingLower === 'south') rotation = 0;
  else if (facingLower === 'north') rotation = 180;
  else if (facingLower === 'east') rotation = 270;
  else if (facingLower === 'west') rotation = 90;

  return (
    <g transform={`translate(${x}, ${y})`}>
      <circle cx={0} cy={0} r={1.8} fill="#ffffff" stroke="#0f172a" strokeWidth={0.12} />
      <circle cx={0} cy={0} r={1.5} fill="none" stroke="#94a3b8" strokeWidth={0.05} strokeDasharray="0.2 0.2" />

      {/* Rotating North Pointer */}
      <g transform={`rotate(${rotation})`}>
        <polygon points="0,-1.4 0.45,0 0,0" fill="#0f172a" />
        <polygon points="0,-1.4 -0.45,0 0,0" fill="#ffffff" stroke="#0f172a" strokeWidth={0.06} />
        <polygon points="0,1.4 0.45,0 0,0" fill="#94a3b8" />
        <polygon points="0,1.4 -0.45,0 0,0" fill="#cbd5e1" />
      </g>

      <text
        x={0} y={-2.1}
        fontSize={0.9} fontWeight="bold" fill="#0f172a" textAnchor="middle" dominantBaseline="middle"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        N
      </text>
      <text
        x={0} y={2.4}
        fontSize={0.45} fontWeight="600" fill="#64748b" textAnchor="middle"
        style={{ fontFamily: "'JetBrains Mono', monospace" }}
      >
        {facing.toUpperCase()}
      </text>
    </g>
  );
}

// ─── Graphic Scale Bar (0, 5, 10, 20 FT) ────────────────────────────────────
function GraphicScaleBar({ x, y }) {
  return (
    <g transform={`translate(${x}, ${y})`} style={{ fontFamily: "'JetBrains Mono', monospace" }}>
      <rect x={0} y={0} width={5} height={0.5} fill="#0f172a" stroke="#0f172a" strokeWidth={0.08} />
      <rect x={5} y={0} width={5} height={0.5} fill="#ffffff" stroke="#0f172a" strokeWidth={0.08} />
      <rect x={10} y={0} width={10} height={0.5} fill="#0f172a" stroke="#0f172a" strokeWidth={0.08} />

      <line x1={0} y1={-0.2} x2={0} y2={0.7} stroke="#0f172a" strokeWidth={0.08} />
      <line x1={5} y1={-0.2} x2={5} y2={0.7} stroke="#0f172a" strokeWidth={0.08} />
      <line x1={10} y1={-0.2} x2={10} y2={0.7} stroke="#0f172a" strokeWidth={0.08} />
      <line x1={20} y1={-0.2} x2={20} y2={0.7} stroke="#0f172a" strokeWidth={0.08} />

      <text x={0} y={-0.5} fontSize={0.55} fontWeight="600" fill="#0f172a" textAnchor="middle">0</text>
      <text x={5} y={-0.5} fontSize={0.55} fontWeight="600" fill="#0f172a" textAnchor="middle">5'</text>
      <text x={10} y={-0.5} fontSize={0.55} fontWeight="600" fill="#0f172a" textAnchor="middle">10'</text>
      <text x={20} y={-0.5} fontSize={0.55} fontWeight="600" fill="#0f172a" textAnchor="middle">20' FT</text>

      <text x={10} y={1.4} fontSize={0.48} fontWeight="500" fill="#64748b" textAnchor="middle" letterSpacing="0.04em">
        GRAPHIC SCALE: 1 UNIT = 1'-0" (FEET &amp; INCHES)
      </text>
    </g>
  );
}

// ─── Blueprint Title Block ──────────────────────────────────────────────────
function BlueprintTitleBlock({ plot, sheetTitle, floor, x, y, width }) {
  const pw = plot.width;
  const pl = plot.length;
  const facing = (plot.facing || 'SOUTH').toUpperCase();
  const indoorRooms = floor?.rooms?.filter(r => r.space_category !== 'outdoor' && !['garden', 'yard', 'terrace', 'balcony', 'parking', 'garage', 'roof'].includes(r.type?.toLowerCase())) || [];
  const roomCount = indoorRooms.length;

  return (
    <g transform={`translate(${x}, ${y})`} style={{ fontFamily: "'Inter', sans-serif" }}>
      <rect x={0} y={0} width={width} height={3.2} fill="#ffffff" stroke="#0f172a" strokeWidth={0.2} />
      <line x1={width * 0.45} y1={0} x2={width * 0.45} y2={3.2} stroke="#cbd5e1" strokeWidth={0.1} />
      <line x1={width * 0.78} y1={0} x2={width * 0.78} y2={3.2} stroke="#cbd5e1" strokeWidth={0.1} />

      {/* Sheet Title */}
      <text x={1.2} y={1.2} fontSize={0.95} fontWeight="800" fill="#0f172a" letterSpacing="0.04em">
        {sheetTitle}
      </text>
      <text x={1.2} y={2.3} fontSize={0.55} fontWeight="600" fill="#64748b" letterSpacing="0.02em">
        RESIDENTIAL ARCHITECTURAL WORKING DRAWING
      </text>

      {/* Project Specs */}
      <text x={width * 0.45 + 1.2} y={1.1} fontSize={0.58} fontWeight="600" fill="#334155">
        PLOT: <strong>{formatFtIn(pw)} × {formatFtIn(pl)} ({Math.round(pw * pl)} SQ FT / {formatMeters(pw)} × {formatMeters(pl)} M)</strong>
      </text>
      <text x={width * 0.45 + 1.2} y={2.2} fontSize={0.55} fontWeight="500" fill="#64748b">
        ORIENTATION: {facing} FACING | ROOMS ON LEVEL: {roomCount}
      </text>

      {/* Status / Compliance */}
      <text x={width * 0.78 + 1.2} y={1.1} fontSize={0.55} fontWeight="700" fill="#059669">
        VALIDATED BLUEPRINT
      </text>
      <text x={width * 0.78 + 1.2} y={2.2} fontSize={0.50} fontWeight="500" fill="#64748b">
        OR-TOOLS &amp; GEMINI AI ENGINE
      </text>
    </g>
  );
}

// ─── Single Floor Layout Content (Reusable for Single or Side-by-Side) ───────
function FloorContent({ plot, floor, floorLevel, hoveredRoomId, onRoomHover, onRoomClick }) {
  const pw = plot.width;
  const pl = plot.length;
  const indoorRooms = useMemo(() => {
    return floor?.rooms?.filter(r => r.space_category !== 'outdoor' && !['garden', 'yard', 'terrace', 'balcony', 'parking', 'garage', 'roof'].includes(r.type?.toLowerCase())) || [];
  }, [floor]);

  return (
    <g className={`arch-floor-level-${floorLevel}`}>
      {/* 1. Background Site & Outdoor Areas */}
      {floorLevel === 0 && (plot.site_areas || []).map(area => (
        <SiteAreaShape
          key={area.id}
          area={area}
          isHovered={hoveredRoomId === area.id}
          onHover={onRoomHover}
          onClick={onRoomClick}
        />
      ))}

      {/* Upper floor terraces & roof below */}
      {(floor?.outdoor_areas || []).map(area => (
        <SiteAreaShape
          key={area.id}
          area={area}
          isHovered={hoveredRoomId === area.id}
          onHover={onRoomHover}
          onClick={onRoomClick}
        />
      ))}

      {/* Buildable boundary indicator */}
      {plot.buildable_boundary && (
        <rect
          x={plot.setbacks?.left || 0}
          y={plot.setbacks?.front || 0}
          width={plot.buildable_boundary.width}
          height={plot.buildable_boundary.length}
          fill="none"
          stroke="#94a3b8"
          strokeWidth={0.14}
          strokeDasharray="0.6 0.3"
        />
      )}

      {/* Ground Floor Entrance Veranda with Steps */}
      {floorLevel === 0 && <VerandaAndLawn plot={plot} />}

      {/* Driveway & Gates on Ground Floor */}
      {floorLevel === 0 && <DrivewayAndGates plot={plot} />}

      {/* 2. Indoor Rooms (with built-in fixtures & CAD dimensions) */}
      {indoorRooms.map(room => (
        <RoomShape
          key={room.id}
          room={room}
          isHovered={hoveredRoomId === room.id}
          onHover={onRoomHover}
          onClick={onRoomClick}
        />
      ))}

      {/* 3. Structural RCC Columns & Numbered Callout Bubbles */}
      <StructuralColumns rooms={indoorRooms} plotWidth={pw} plotLength={pl} />

      {/* 4. Walls (Heavy Exterior, Medium Interior) */}
      <WallLines walls={floor?.walls} />

      {/* 5. Doors (Opening cutout, swing arc, D/D1/D2 tags) */}
      {floor?.doors?.map(door => (
        <DoorShape key={door.id} door={door} rooms={floor.rooms} />
      ))}

      {/* 6. Windows (Sill, triple glazing, Sunshade Chhajja, W/W1/V tags) */}
      {floor?.windows?.map(win => (
        <WindowShape key={win.id} window={win} plotWidth={pw} plotLength={pl} rooms={floor.rooms} />
      ))}

      {/* 7. Staircases (Treads 1-17, handrail, landing, UP/DN arrows) */}
      {floor?.stairs?.map(stair => (
        <StairShape key={stair.id} stair={stair} floorLevel={floorLevel} />
      ))}

      {/* Setback Annotations */}
      <SetbackDimensionAnnotations plot={plot} />
    </g>
  );
}

// ─── Site Plan Overview View (Footprint, Setbacks, Landscaping) ──────────────
function SitePlanView({ plot, hoveredRoomId, onRoomHover, onRoomClick }) {
  const pw = plot.width;
  const pl = plot.length;
  const sb = plot.setbacks || {};
  const bb = plot.buildable_boundary || {};
  const fp = plot.building_footprint;

  const fpArea = fp ? Math.round(fp.width * fp.length) : 0;
  const plotArea = Math.round(pw * pl);
  const coveragePct = plotArea > 0 ? ((fpArea / plotArea) * 100).toFixed(1) : '0.0';

  return (
    <g className="arch-site-plan-view">
      {/* 1. Base Site Areas (Garden, Yards, Parking) */}
      {(plot.site_areas || []).map(area => (
        <SiteAreaShape
          key={area.id}
          area={area}
          isHovered={hoveredRoomId === area.id}
          onHover={onRoomHover}
          onClick={onRoomClick}
        />
      ))}

      {/* 2. Buildable Envelope */}
      {bb.width > 0 && bb.length > 0 && (
        <rect
          x={sb.left || 0}
          y={sb.front || 0}
          width={bb.width}
          height={bb.length}
          fill="none"
          stroke="#0284c7"
          strokeWidth={0.2}
          strokeDasharray="0.8 0.4"
        />
      )}

      {/* 3. Building Footprint */}
      {fp && (
        <g>
          <rect
            x={fp.x} y={fp.y}
            width={fp.width} height={fp.length}
            fill="#e2e8f0"
            stroke="#0f172a"
            strokeWidth={0.65}
            strokeLinejoin="miter"
          />
          <rect
            x={fp.x} y={fp.y}
            width={fp.width} height={fp.length}
            fill="url(#footprint-hatch)"
          />
          <g style={{ fontFamily: "'Inter', sans-serif" }}>
            <rect
              x={fp.x + fp.width / 2 - 12} y={fp.y + fp.length / 2 - 2.0}
              width={24} height={4.0}
              fill="#ffffff" stroke="#0f172a" strokeWidth={0.16} rx={0.3}
            />
            <text
              x={fp.x + fp.width / 2} y={fp.y + fp.length / 2 - 0.6}
              fontSize={0.88} fontWeight="800" fill="#0f172a"
              textAnchor="middle" letterSpacing="0.04em"
            >
              PROPOSED BUILDING FOOTPRINT
            </text>
            <text
              x={fp.x + fp.width / 2} y={fp.y + fp.length / 2 + 0.8}
              fontSize={0.68} fontWeight="600" fill="#334155"
              textAnchor="middle"
            >
              {formatFtIn(fp.width)} × {formatFtIn(fp.length)} ({fpArea} SQ FT)
            </text>
          </g>
        </g>
      )}

      {/* 4. Driveway & Gates */}
      <DrivewayAndGates plot={plot} />

      {/* 5. Setback Annotations */}
      <SetbackDimensionAnnotations plot={plot} />

      {/* 6. Site Summary Legend */}
      <g transform={`translate(2.0, ${pl - 12.0})`} style={{ fontFamily: "'JetBrains Mono', monospace" }}>
        <rect x={0} y={0} width={18} height={9.5} fill="#ffffff" stroke="#0f172a" strokeWidth={0.16} />
        <rect x={0} y={0} width={18} height={1.8} fill="#0f172a" />
        <text x={9} y={1.2} fontSize={0.62} fontWeight="bold" fill="#ffffff" textAnchor="middle">
          SITE PLANNING METRICS
        </text>
        <text x={1} y={3.2} fontSize={0.52} fill="#334155">PLOT AREA: {plotArea} SQ FT</text>
        <text x={1} y={4.6} fontSize={0.52} fill="#334155">FOOTPRINT: {fpArea} SQ FT</text>
        <text x={1} y={6.0} fontSize={0.52} fill="#334155">GROUND COV: {coveragePct}%</text>
        <text x={1} y={7.4} fontSize={0.52} fill="#334155">OPEN SPACE: {plotArea - fpArea} SQ FT</text>
        <text x={1} y={8.8} fontSize={0.52} fill="#059669" fontWeight="bold">STATUS: COMPLIANT</text>
      </g>
    </g>
  );
}

// ─── Main FloorPlanSVG Component ────────────────────────────────────────────
const FloorPlanSVG = ({ layoutData, selectedFloor = 0, hoveredRoomId, onRoomHover, onRoomClick }) => {
  const plot = layoutData?.plot;
  const isSitePlan = (selectedFloor === 'site' || selectedFloor === 'site_plan');
  const isBothFloors = (selectedFloor === 'both' || selectedFloor === 'cad_sheet');

  const groundFloor = useMemo(() => {
    return layoutData?.floors?.find(f => f.level === 0) || layoutData?.floors?.[0] || null;
  }, [layoutData]);

  const firstFloor = useMemo(() => {
    return layoutData?.floors?.find(f => f.level === 1) || layoutData?.floors?.[1] || null;
  }, [layoutData]);

  const floor = useMemo(() => {
    if (!layoutData?.floors || isSitePlan || isBothFloors) return null;
    const targetLvl = typeof selectedFloor === 'number' ? selectedFloor : 0;
    return layoutData.floors.find(f => f.level === targetLvl)
      || layoutData.floors[targetLvl]
      || layoutData.floors[0]
      || null;
  }, [layoutData, selectedFloor, isSitePlan, isBothFloors]);

  if (!plot) return null;

  const pw = plot.width;
  const pl = plot.length;
  const facing = (plot.front_side || plot.facing || 'south').toLowerCase();

  // If both floors are requested side-by-side (AutoCAD Sheet Mode)
  if (isBothFloors && groundFloor && firstFloor) {
    const spacing = 12.0;
    const totalW = pw * 2 + spacing;
    const padL = 8.0;
    const padR = 10.0;
    const padT = 8.5;
    const padB = 18.0;

    const viewBox = `${-padL} ${-padT} ${totalW + padL + padR} ${pl + padT + padB}`;

    return (
      <svg
        viewBox={viewBox}
        style={{
          maxWidth: '100%', maxHeight: '100%', width: '100%', height: 'auto',
          display: 'block', background: '#ffffff', borderRadius: '4px'
        }}
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="arch-grid-pattern" width="5" height="5" patternUnits="userSpaceOnUse">
            <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#f1f5f9" strokeWidth="0.05" />
          </pattern>
          <pattern id="cad-lawn-stipple" width="2" height="2" patternUnits="userSpaceOnUse">
            <line x1="1" y1="0.6" x2="1" y2="1.4" stroke="#0f172a" strokeWidth="0.08" />
            <line x1="0.6" y1="1" x2="1.4" y2="1" stroke="#0f172a" strokeWidth="0.08" />
          </pattern>
          <pattern id="roof-pattern" width="1.8" height="1.8" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
            <line x1="0" y1="0" x2="0" y2="1.8" stroke="#94a3b8" strokeWidth="0.1" strokeDasharray="0.3 0.2" opacity="0.4" />
          </pattern>
        </defs>

        {/* ── LEFT PANE: EXI. GROUND FLOOR PLAN ── */}
        <g transform="translate(0, 0)">
          <rect x={0} y={0} width={pw} height={pl} fill="url(#arch-grid-pattern)" />
          <ArchitecturalGrid width={pw} length={pl} />
          <rect x={0} y={0} width={pw} height={pl} fill="none" stroke="#0f172a" strokeWidth={0.55} />

          <FloorContent
            plot={plot}
            floor={groundFloor}
            floorLevel={0}
            hoveredRoomId={hoveredRoomId}
            onRoomHover={onRoomHover}
            onClick={onRoomClick}
          />
          <RoadElement plot={plot} />
          <ExternalDimensions plot={plot} facing={facing} />

          {/* Subtitle matching reference AutoCAD drawing */}
          <text
            x={pw / 2} y={pl + 9.5}
            textAnchor="middle" fontSize={1.3} fontWeight="800" fill="#0f172a"
            letterSpacing="0.08em" fontFamily="'Segoe UI', sans-serif"
          >
            EXI. GROUND FLOOR PLAN
          </text>
        </g>

        {/* ── RIGHT PANE: FIRST FLOOR PLAN ── */}
        <g transform={`translate(${pw + spacing}, 0)`}>
          <rect x={0} y={0} width={pw} height={pl} fill="url(#arch-grid-pattern)" />
          <ArchitecturalGrid width={pw} length={pl} />
          <rect x={0} y={0} width={pw} height={pl} fill="none" stroke="#0f172a" strokeWidth={0.55} />

          <FloorContent
            plot={plot}
            floor={firstFloor}
            floorLevel={1}
            hoveredRoomId={hoveredRoomId}
            onRoomHover={onRoomHover}
            onClick={onRoomClick}
          />
          <ExternalDimensions plot={plot} facing={facing} />

          {/* Subtitle matching reference AutoCAD drawing */}
          <text
            x={pw / 2} y={pl + 9.5}
            textAnchor="middle" fontSize={1.3} fontWeight="800" fill="#0f172a"
            letterSpacing="0.08em" fontFamily="'Segoe UI', sans-serif"
          >
            FIRST FLOOR PLAN
          </text>
        </g>

        {/* ── SHARED SHEET ELEMENTS ── */}
        <ArchitecturalCompass x={-3.5} y={-3.5} facing={facing} />
        <GraphicScaleBar x={0} y={pl + 13.5} />
        <BlueprintTitleBlock
          plot={plot}
          sheetTitle="ARCHITECTURAL WORKING DRAWING (G+1 RESIDENCE)"
          floor={groundFloor}
          x={0}
          y={pl + 12.0}
          width={totalW}
        />
      </svg>
    );
  }

  // Single Floor View
  const padLeft = 8.0;
  const padRight = 10.0;
  const padTop = 8.5;
  const padBottom = 16.0;

  const viewX = -padLeft;
  const viewY = -padTop;
  const viewWidth = pw + padLeft + padRight;
  const viewHeight = pl + padTop + padBottom;
  const viewBox = `${viewX} ${viewY} ${viewWidth} ${viewHeight}`;

  const sheetTitle = isSitePlan
    ? 'SITE PLAN & ROOF OVERVIEW'
    : (floor?.level === 0 ? 'EXI. GROUND FLOOR PLAN' : (floor?.level === 1 ? 'FIRST FLOOR PLAN' : `FLOOR ${selectedFloor} PLAN`));

  return (
    <svg
      viewBox={viewBox}
      style={{
        maxWidth: '100%', maxHeight: '100%', width: '100%', height: 'auto',
        display: 'block', background: '#ffffff', borderRadius: '4px'
      }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <pattern id="arch-grid-pattern" width="5" height="5" patternUnits="userSpaceOnUse">
          <path d="M 5 0 L 0 0 0 5" fill="none" stroke="#f1f5f9" strokeWidth="0.05" />
        </pattern>
        <pattern id="footprint-hatch" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="1.2" stroke="#64748b" strokeWidth="0.12" opacity="0.3" />
        </pattern>
        <pattern id="roof-pattern" width="1.8" height="1.8" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
          <line x1="0" y1="0" x2="0" y2="1.8" stroke="#94a3b8" strokeWidth="0.1" strokeDasharray="0.3 0.2" opacity="0.4" />
        </pattern>
        <pattern id="cad-lawn-stipple" width="2" height="2" patternUnits="userSpaceOnUse">
          <line x1="1" y1="0.6" x2="1" y2="1.4" stroke="#0f172a" strokeWidth="0.08" />
          <line x1="0.6" y1="1" x2="1.4" y2="1" stroke="#0f172a" strokeWidth="0.08" />
        </pattern>
      </defs>

      {/* Grid Canvas */}
      <rect x={0} y={0} width={pw} height={pl} fill="url(#arch-grid-pattern)" />
      <ArchitecturalGrid width={pw} length={pl} />

      {/* Plot Boundary Border */}
      <rect
        x={0} y={0} width={pw} height={pl}
        fill="none"
        stroke="#0f172a"
        strokeWidth={0.55}
      />

      {/* ── Mode 1: Full Site Plan View ──────────────────────────────────────── */}
      {isSitePlan ? (
        <SitePlanView
          plot={plot}
          hoveredRoomId={hoveredRoomId}
          onRoomHover={onRoomHover}
          onClick={onRoomClick}
        />
      ) : (
        /* ── Mode 2: Detailed Floor Plan View (Ground or Upper) ──────────────── */
        <FloorContent
          plot={plot}
          floor={floor}
          floorLevel={floor?.level ?? selectedFloor}
          hoveredRoomId={hoveredRoomId}
          onRoomHover={onRoomHover}
          onClick={onRoomClick}
        />
      )}

      {/* ── Sheet Elements (Always Present) ─────────────────────────────────── */}
      <RoadElement plot={plot} />
      <ExternalDimensions plot={plot} facing={facing} />
      <ArchitecturalCompass x={-3.5} y={-3.5} facing={facing} />
      <GraphicScaleBar x={0} y={pl + 12.2} />
      <BlueprintTitleBlock
        plot={plot}
        sheetTitle={sheetTitle}
        floor={floor}
        x={0}
        y={pl + 8.0}
        width={pw}
      />
    </svg>
  );
};

export default FloorPlanSVG;
