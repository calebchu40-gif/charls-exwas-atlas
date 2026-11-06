// Browse-by-phenotype / browse-by-exposure views.
//
// The NHANES Phenome-Exposome Atlas is organised around two entry points: pick a
// phenotype and see its exposures, or pick an exposure and see its phenotypes.
// These views implement that interaction on top of the disclosure-reviewed
// association payload already loaded by app.js. No new data source is used.

const browseState = {
  phenotype: { concept: '', wave: '', sort: 'q' },
  exposure: { concept: '', wave: '', sort: 'q' },
};
let browseInitDone = false;

function browseNumber(value) {
  if (value === '' || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function browseFormat(value, digits = 3) {
  const number = browseNumber(value);
  if (number === null) return '—';
  const magnitude = Math.abs(number);
  if (magnitude !== 0 && (magnitude < 0.001 || magnitude >= 10000)) return number.toExponential(1);
  return number.toPrecision(digits);
}

async function browseRows() {
  if (associationRows.length) return associationRows;
  try {
    await renderAssociations();
  } catch (error) {
    /* the associations view already reports the failure */
  }
  return associationRows;
}

function browseConcepts(rows, mode) {
  const key = mode === 'phenotype' ? 'phenotype_concept_id' : 'exposure_concept_id';
  const labelKey = mode === 'phenotype' ? 'phenotype_variable' : 'exposure_variable';
  const map = new Map();
  for (const row of rows) {
    const id = row[key];
    if (!id) continue;
    if (!map.has(id)) map.set(id, { id, variable: row[labelKey] || '', count: 0 });
    map.get(id).count += 1;
  }
  return [...map.values()].sort((a, b) => a.id.localeCompare(b.id));
}

function browseDisplay(item) {
  return `${item.id} [${item.variable || '—'}]`;
}

function browseFiltered(mode) {
  const state = browseState[mode];
  const otherKey = mode === 'phenotype' ? 'exposure_concept_id' : 'phenotype_concept_id';
  const selfKey = mode === 'phenotype' ? 'phenotype_concept_id' : 'exposure_concept_id';
  const rows = associationRows.filter(row =>
    row[selfKey] === state.concept && (!state.wave || row.wave === state.wave));
  const sort = state.sort;
  rows.sort((a, b) => {
    if (sort === 'effect') {
      const av = Math.abs(browseNumber(a.estimate) ?? 0);
      const bv = Math.abs(browseNumber(b.estimate) ?? 0);
      return bv - av;
    }
    const av = browseNumber(a.q_value_by) ?? Infinity;
    const bv = browseNumber(b.q_value_by) ?? Infinity;
    return av === bv ? 0 : av - bv;
  });
  return { rows, otherKey };
}

function browseChart(mode, rows, otherKey) {
  const container = byId(`browse${mode === 'phenotype' ? 'Phenotype' : 'Exposure'}Chart`);
  if (!container) return;
  const top = rows.filter(row => row.fit_status === 'success' && browseNumber(row.estimate) !== null).slice(0, 15);
  if (!top.length) {
    container.innerHTML = '<p class="muted">当前筛选下没有可绘制的估计值。</p>';
    return;
  }
  const hasOR = top.some(row => row.estimate_type === 'odds_ratio');
  const magnitudeOf = row => {
    const estimate = browseNumber(row.estimate) ?? 0;
    return row.estimate_type === 'odds_ratio'
      ? Math.abs(Math.log(Math.max(estimate, 1e-6)))
      : Math.abs(estimate);
  };
  const width = 1040, barHeight = 22, gap = 8;
  const labelWidth = 330, plotLeft = 350, plotRight = 1005;
  const zero = (plotLeft + plotRight) / 2;
  const half = (plotRight - plotLeft) / 2;
  const height = top.length * (barHeight + gap) + 26;
  const max = Math.max(...top.map(magnitudeOf), 1e-9);
  const parts = [`<svg viewBox="0 0 ${width} ${height}" width="100%" height="${height}" role="img" aria-label="top associations">`];
  parts.push(`<line x1="${zero}" y1="4" x2="${zero}" y2="${height - 20}" stroke="#c9d6de" stroke-width="1"/>`);
  top.forEach((row, index) => {
    const y = 8 + index * (barHeight + gap);
    const estimate = browseNumber(row.estimate) ?? 0;
    const isOR = row.estimate_type === 'odds_ratio';
    const positive = isOR ? Math.log(Math.max(estimate, 1e-6)) >= 0 : estimate >= 0;
    const length = Math.max(2, magnitudeOf(row) / max * half);
    const x = positive ? zero : zero - length;
    const color = positive ? '#2f6fbe' : '#c0392b';
    const contrast = row.contrast ? ' · ' + row.contrast.slice(-24) : '';
    const label = `${row[otherKey]}${contrast}`;
    const short = label.length > 42 ? label.slice(0, 41) + '…' : label;
    const q = browseNumber(row.q_value_by);
    parts.push(`<text x="${labelWidth}" y="${y + barHeight / 2 + 4}" text-anchor="end" font-size="11.5" fill="#33475b">${escapeXml(short)}</text>`);
    parts.push(`<rect x="${x}" y="${y}" width="${length}" height="${barHeight}" rx="3" fill="${color}" fill-opacity="0.82"><title>${escapeXml(label)}: ${estimate.toFixed(3)} (q ${q === null ? '—' : q.toExponential(1)})</title></rect>`);
    const value = isOR ? estimate.toFixed(2) : `${estimate >= 0 ? '+' : ''}${estimate.toFixed(3)}`;
    const valueX = positive ? x + length + 6 : x - 6;
    parts.push(`<text x="${valueX}" y="${y + barHeight / 2 + 4}" text-anchor="${positive ? 'start' : 'end'}" font-size="11.5" fill="#33475b">${value}${q !== null && q < 0.05 ? ' *' : ''}</text>`);
  });
  parts.push('</svg>');
  container.innerHTML = parts.join('');
  container.insertAdjacentHTML('beforeend',
    hasOR
      ? '<p class="browse-legend">条形长度按 log 劣势比（OR）绘制，零线为 OR=1；蓝色 OR&gt;1、红色 OR&lt;1；* 表示该族 BY q &lt; 0.05。</p>'
      : '<p class="browse-legend">条形从零线向两侧绘制，长度 = 效应绝对值（每标准差）；蓝色为正、红色为负；* 表示该族 BY q &lt; 0.05。</p>');
}

function escapeXml(text) {
  return String(text).replace(/[<>&"]/g, ch => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' }[ch]));
}

function browseTable(mode, rows, otherKey) {
  const body = byId(`browse${mode === 'phenotype' ? 'Phenotype' : 'Exposure'}Rows`);
  if (!body) return;
  body.replaceChildren();
  for (const row of rows) {
    const tr = document.createElement('tr');
    const effect = row.fit_status === 'success'
      ? `${browseFormat(row.estimate)} (${browseFormat(row.ci_lower)} to ${browseFormat(row.ci_upper)})`
      : '—';
    const cells = [
      `${row[otherKey]}${row.contrast ? ' · ' + row.contrast : ''}`,
      row.wave,
      row.model_id,
      effect,
      browseFormat(row.p_value),
      browseFormat(row.q_value_by),
      row.n_model || '—',
      browseStatusLabel(row.fit_status),
    ];
    for (const cell of cells) {
      const td = document.createElement('td');
      td.textContent = String(cell ?? '—');
      tr.append(td);
    }
    body.append(tr);
  }
}


function browseStatusLabel(status) {
  return ({
    success: '已估计',
    withheld_disclosure: '披露抑制',
    blocked_measurement_rule: '测量规则待核',
    inestimable: '不可估计',
    code_error: '代码错误',
  })[status] || status || '—';
}

function renderBrowse(mode) {
  const rows = associationRows;
  if (!rows.length) return;
  const prefix = mode === 'phenotype' ? 'Phenotype' : 'Exposure';
  const state = browseState[mode];
  const input = byId(`browse${prefix}Input`);
  const list = byId(`browse${prefix}Options`);
  const waveSelect = byId(`browse${prefix}Wave`);
  const sortSelect = byId(`browse${prefix}Sort`);
  const concepts = browseConcepts(rows, mode);
  if (!list.dataset.filled) {
    list.replaceChildren();
    for (const item of concepts) {
      const option = document.createElement('option');
      option.value = browseDisplay(item);
      list.append(option);
    }
    list.dataset.filled = 'true';
  }
  const byDisplay = new Map(concepts.map(item => [browseDisplay(item), item]));
  if (!byDisplay.has(input.value)) {
    const fallback = mode === 'phenotype' ? 'blood_hemoglobin' : 'running_water_at_residence';
    const preferred = concepts.find(item => item.id === state.concept)
      || concepts.find(item => item.id === fallback)
      || concepts[0];
    input.value = preferred ? browseDisplay(preferred) : '';
  }
  const chosen = byDisplay.get(input.value);
  state.concept = chosen ? chosen.id : '';
  if (!waveSelect.dataset.filled) {
    const waves = [...new Set(rows.map(row => row.wave).filter(Boolean))].sort();
    waveSelect.replaceChildren(new Option('全部波次', ''));
    for (const wave of waves) waveSelect.append(new Option(wave, wave));
    waveSelect.dataset.filled = 'true';
  }
  if (!chosen) return;
  const { rows: filtered, otherKey } = browseFiltered(mode);
  const summary = byId(`browse${prefix}Summary`);
  summary.textContent = `${chosen.id}（${chosen.variable || '变量未记录'}）· ${filtered.length} 条关联`
    + (state.wave ? ` · ${state.wave}` : ' · 全部波次')
    + ` · 显著 q<0.05：${filtered.filter(row => (browseNumber(row.q_value_by) ?? 1) < 0.05).length}`;
  browseChart(mode, filtered, otherKey);
  browseTable(mode, filtered, otherKey);
}

function initBrowse() {
  if (browseInitDone) return;
  browseInitDone = true;
  for (const mode of ['phenotype', 'exposure']) {
    const prefix = mode === 'phenotype' ? 'Phenotype' : 'Exposure';
    const input = byId(`browse${prefix}Input`);
    const waveSelect = byId(`browse${prefix}Wave`);
    const sortSelect = byId(`browse${prefix}Sort`);
    if (!input) continue;
    input.addEventListener('input', () => {
      browseState[mode].concept = '';
      renderBrowse(mode);
    });
    waveSelect.addEventListener('change', () => {
      browseState[mode].wave = waveSelect.value;
      renderBrowse(mode);
    });
    sortSelect.addEventListener('change', () => {
      browseState[mode].sort = sortSelect.value;
      renderBrowse(mode);
    });
  }
  browseRows().then(() => {
    renderBrowse('phenotype');
    renderBrowse('exposure');
  });
}

// Initialise when the view is opened: wrap showView so button clicks, deep
// links and the browser's back button all trigger the same path.
const browseOriginalShowView = showView;
showView = function (id) {
  browseOriginalShowView(id);
  if ((id === 'browsePhenotype' || id === 'byPhenotype' || id === 'browseExposure' || id === 'byExposure') && !browseInitDone) {
    setTimeout(initBrowse, 0);
  }
};
