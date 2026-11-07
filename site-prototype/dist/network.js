// Exposure-exposure correlation network for the 2011 wave.
// Reads the aggregate JSON produced by scripts/analyze_wave1_exposure_network.py.
const networkGroups = {
  '住房': '#2f6fbe',
  '燃料': '#e67e22',
  '社区': '#2ca02c',
  '社会经济': '#8e44ad',
  '行为': '#c0392b',
};

function renderNetwork(payload) {
  const canvas = byId('networkCanvas');
  if (!canvas) return;
  const nodes = payload.nodes;
  const edges = payload.edges;
  const size = 460;
  const centre = size / 2;
  const radius = 150;
  const positions = new Map();
  nodes.forEach((node, index) => {
    const angle = (2 * Math.PI * index) / nodes.length - Math.PI / 2;
    positions.set(node.id, {
      x: centre + radius * Math.cos(angle),
      y: centre + radius * Math.sin(angle),
      angle,
      node,
    });
  });
  const parts = [`<svg viewBox="0 0 ${size} ${size}" width="100%" height="${size}" role="img" aria-label="暴露相关网络">`];
  for (const edge of edges) {
    const a = positions.get(edge.source);
    const b = positions.get(edge.target);
    if (!a || !b) continue;
    const width = 0.8 + 4 * Math.abs(edge.rho);
    const colour = edge.rho >= 0 ? '#2f6fbe' : '#c0392b';
    const opacity = 0.25 + 0.6 * Math.abs(edge.rho);
    const mx = (a.x + b.x) / 2 + (centre - (a.x + b.x) / 2) * 0.35;
    const my = (a.y + b.y) / 2 + (centre - (a.y + b.y) / 2) * 0.35;
    parts.push(`<path d="M${a.x.toFixed(1)},${a.y.toFixed(1)} Q${mx.toFixed(1)},${my.toFixed(1)} ${b.x.toFixed(1)},${b.y.toFixed(1)}"
      fill="none" stroke="${colour}" stroke-width="${width.toFixed(2)}" stroke-opacity="${opacity.toFixed(2)}">
      <title>${edge.source} – ${edge.target}: ρ=${edge.rho.toFixed(3)}, q=${edge.q}</title></path>`);
  }
  for (const [id, position] of positions) {
    const { node, x, y, angle } = position;
    const colour = networkGroups[node.group] || '#607584';
    const cos = Math.cos(angle);
    const sin = Math.sin(angle);
    const labelRadius = radius + 30;
    const anchor = cos > 0.3 ? 'start' : (cos < -0.3 ? 'end' : 'middle');
    const labelX = centre + labelRadius * cos;
    const labelY = centre + labelRadius * sin + (Math.abs(cos) <= 0.3 ? (sin > 0 ? 14 : -8) : 4);
    parts.push(`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="9" fill="${colour}"><title>${node.label}（${node.group}）· ${node.field}</title></circle>`);
    parts.push(`<text x="${labelX.toFixed(1)}" y="${labelY.toFixed(1)}" text-anchor="${anchor}" font-size="12" fill="#24485a">${node.label}</text>`);
  }
  parts.push('</svg>');
  canvas.innerHTML = parts.join('');

  const body = byId('networkRows');
  body.replaceChildren();
  const labelOf = new Map(nodes.map(node => [node.id, node.label]));
  for (const edge of [...edges].sort((a, b) => Math.abs(b.rho) - Math.abs(a.rho))) {
    const tr = document.createElement('tr');
    const qText = edge.q < 0.001 ? '<0.001' : edge.q.toFixed(3);
    const rows = [labelOf.get(edge.source) || edge.source, labelOf.get(edge.target) || edge.target,
                  edge.rho.toFixed(3), qText, edge.n];
    for (const value of rows) {
      const td = document.createElement('td');
      td.textContent = String(value);
      tr.append(td);
    }
    body.append(tr);
  }
  const dropped = payload.dropped_nodes && payload.dropped_nodes.length
    ? ` · 本波无以下字段：${payload.dropped_nodes.join('、')}`
    : '';
  byId('networkCount').textContent = `${payload.wave} 年 · ${nodes.length} 个暴露 · ${edges.length} 条 |ρ|≥${payload.min_abs_r} 且 q<${payload.alpha} 的边 · n=${payload.n_rows.toLocaleString()}${dropped}`;
}

const networkCache = new Map();

async function loadNetwork(wave) {
  const target = wave || byId('networkWave')?.value || '2011';
  if (networkCache.has(target)) {
    renderNetwork(networkCache.get(target));
    return;
  }
  byId('networkCount').textContent = `正在载入 ${target} 网络…`;
  try {
    const response = await fetch(`./exposure_network_${target}_v1.json?v=1`, { cache: 'no-cache' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    networkCache.set(target, payload);
    renderNetwork(payload);
  } catch (error) {
    byId('networkCount').textContent = `网络数据载入失败：${error.message}`;
  }
}

document.querySelectorAll('[data-view="network"]').forEach(button =>
  button.addEventListener('click', () => setTimeout(() => loadNetwork(), 0)));
const networkWave = byId('networkWave');
if (networkWave) networkWave.addEventListener('change', () => loadNetwork(networkWave.value));
if (location.hash === '#network') setTimeout(() => loadNetwork(), 300);
