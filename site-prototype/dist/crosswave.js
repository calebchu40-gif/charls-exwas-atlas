// Cross-wave consistency view: DerSimonian-Laird pooled estimates for
// exposure-phenotype pairs measured in more than one wave.
let crossWavePairs = [];

function crossWaveForest(pair) {
  const box = byId('crossWaveForest');
  if (!box) return;
  if (!pair) {
    box.innerHTML = '<p class="muted">点击表格中的一行查看森林图。</p>';
    return;
  }
  const rows = [...pair.inputs, { wave: '合并', estimate: pair.pooled, ci_lower: pair.ci_lower, ci_upper: pair.ci_upper, pooled: true }];
  const width = 900, rowHeight = 34, left = 220, right = 120;
  const min = Math.min(...rows.map(r => r.ci_lower));
  const max = Math.max(...rows.map(r => r.ci_upper));
  const span = Math.max(max - min, 1e-6);
  const x = value => left + ((value - min) / span) * (width - left - right);
  const height = rows.length * rowHeight + 30;
  const parts = [`<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" role="img" aria-label="forest plot">`];
  const zero = x(0);
  parts.push(`<line x1="${zero}" y1="6" x2="${zero}" y2="${height - 18}" stroke="#c9d6de" stroke-dasharray="3 3"/>`);
  rows.forEach((row, index) => {
    const y = 18 + index * rowHeight;
    const colour = row.pooled ? '#183d54' : '#2f6fbe';
    parts.push(`<text x="${left - 12}" y="${y + 5}" text-anchor="end" font-size="12" fill="#33475b">${row.wave}${row.pooled ? '（DL）' : ''}</text>`);
    parts.push(`<line x1="${x(row.ci_lower)}" y1="${y}" x2="${x(row.ci_upper)}" y2="${y}" stroke="${colour}" stroke-width="2"/>`);
    parts.push(`<circle cx="${x(row.estimate)}" cy="${y}" r="${row.pooled ? 6 : 4}" fill="${colour}"/>`);
    parts.push(`<text x="${width - 10}" y="${y + 5}" text-anchor="end" font-size="12" fill="#33475b">${row.estimate.toFixed(3)} [${row.ci_lower.toFixed(3)}, ${row.ci_upper.toFixed(3)}]</text>`);
  });
  parts.push('</svg>');
  box.innerHTML = parts.join('') +
    `<p class="browse-legend">${pair.exposure_concept_id} × ${pair.phenotype_concept_id} · ${pair.contrast || '—'} · k=${pair.k} · I²=${pair.i2.toFixed(0)}% · ${pair.metric === 'OR' ? '优势比（对数合并后回变换）' : '标准化 β'}</p>`;
}

function renderCrossWave() {
  const body = byId('crossWaveRows');
  if (!body) return;
  const term = byId('crossWaveSearch').value.trim().toLowerCase();
  const wavePair = byId('crossWaveWaves').value;
  const rows = crossWavePairs.filter(pair => {
    if (wavePair && pair.waves.join('+') !== wavePair) return false;
    if (!term) return true;
    return [pair.exposure_concept_id, pair.phenotype_concept_id, pair.contrast]
      .some(value => String(value || '').toLowerCase().includes(term));
  });
  body.replaceChildren();
  for (const pair of rows) {
    const tr = document.createElement('tr');
    const isOR = pair.metric === 'OR';
    const cells = [
      pair.exposure_concept_id,
      pair.contrast || '—',
      pair.phenotype_concept_id,
      pair.waves.join(' / '),
      `${pair.pooled.toFixed(isOR ? 2 : 3)}${isOR ? ' (OR)' : ''}`,
      `${pair.ci_lower.toFixed(isOR ? 2 : 3)} – ${pair.ci_upper.toFixed(isOR ? 2 : 3)}`,
      pair.i2.toFixed(0) + '%',
      pair.p < 0.001 ? '<0.001' : pair.p.toFixed(3),
      pair.sign_consistent ? '一致' : '不一致',
    ];
    for (const cell of cells) {
      const td = document.createElement('td');
      td.textContent = String(cell);
      tr.append(td);
    }
    tr.addEventListener('click', () => crossWaveForest(pair));
    body.append(tr);
  }
  byId('crossWaveCount').textContent = `${rows.length} / ${crossWavePairs.length} 对 · 至少两波可合并`;
}

async function loadCrossWave() {
  if (crossWavePairs.length) return;
  try {
    const response = await fetch('./cross_wave_meta_v1.json?v=1', { cache: 'no-cache' });
    const payload = await response.json();
    crossWavePairs = payload.pairs;
    const waveSelect = byId('crossWaveWaves');
    const combos = [...new Set(crossWavePairs.map(pair => pair.waves.join('+')))].sort();
    waveSelect.replaceChildren(new Option('全部波次组合', ''));
    for (const combo of combos) waveSelect.append(new Option(combo.replace('+', ' + '), combo));
    waveSelect.addEventListener('change', renderCrossWave);
    byId('crossWaveSearch').addEventListener('input', renderCrossWave);
    crossWaveForest(null);
    renderCrossWave();
  } catch (error) {
    byId('crossWaveCount').textContent = `跨波数据载入失败：${error.message}`;
  }
}

document.querySelectorAll('[data-view="crosswave"]').forEach(button =>
  button.addEventListener('click', () => setTimeout(loadCrossWave, 0)));
if (location.hash === '#crosswave') setTimeout(loadCrossWave, 300);
