"""Add the full-scan view to the static site (index.html, app.js, styles)."""
from pathlib import Path

BASE = Path("site-prototype/dist")
html = (BASE / "index.html").read_text(encoding="utf-8")
js = (BASE / "app.js").read_text(encoding="utf-8")

# 1) nav entry
anchor = '<button type="button" data-view="significant">'
assert anchor in html
html = html.replace(anchor, '<button type="button" data-view="fullScan">全扫描</button>' + anchor, 1)

# 2) view section
section = '''<section class="view" id="fullScan" hidden>
<h2>全扫描：暴露 × 结局</h2>
<p class="view-lede">每个"暴露—结局"配对独立估计，全部保留（含不显著结果），门槛为 n≥100。可先按暴露查结局，也可按结局查暴露。</p>
<div class="fs-controls">
  <div class="fs-tabs" role="tablist">
    <button type="button" class="fs-tab" data-dir="exposure" aria-pressed="true">按暴露查结局</button>
    <button type="button" class="fs-tab" data-dir="phenotype" aria-pressed="false">按结局查暴露</button>
  </div>
  <label class="fs-pick"><span id="fsPickLabel">选择暴露</span>
    <input id="fsSearch" type="search" placeholder="输入名称筛选…" autocomplete="off">
    <select id="fsSelect" size="8"></select>
  </label>
</div>
<p class="fs-meta" id="fsMeta">正在加载结果…</p>
<div class="tablewrap"><table class="fs-table"><thead><tr><th>对方指标</th><th>对比</th><th>估计值</th><th>95% CI</th><th>p</th><th>q</th><th>n</th></tr></thead><tbody id="fsBody"></tbody></table></div>
</section>
'''
marker = '<section class="view" id="groups" hidden>'
assert marker in html
html = html.replace(marker, section + marker, 1)

# 3) styles
style = '''
<style id="fullscan-style">
.fs-controls{display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start;margin:14px 0 8px}
.fs-tabs{display:flex;gap:6px}
.fs-tab{border:1px solid var(--line);background:#fff;border-radius:7px;padding:8px 12px;font-size:12.5px;color:#375668;cursor:pointer}
.fs-tab[aria-pressed="true"]{background:var(--navy);border-color:var(--navy);color:#fff}
.fs-pick{display:flex;flex-direction:column;gap:6px;min-width:320px;flex:1;font-size:12.5px;color:#375668}
.fs-pick input,.fs-pick select{border:1px solid var(--line);border-radius:7px;padding:8px 10px;font-size:13px;background:#fff}
.fs-pick select{min-height:150px}
.fs-meta{font-size:12.5px;color:#5b7482;margin:8px 0}
.fs-table{width:100%;border-collapse:collapse;font-size:12.5px}
.fs-table th,.fs-table td{padding:6px 8px;border-bottom:1px solid #e6eef2;text-align:left}
.fs-table td.num{text-align:right;font-variant-numeric:tabular-nums}
.fs-table tr.sig{background:#f3fbf6}
</style>
'''
html = html.replace("</head>", style + "</head>", 1)

(BASE / "index.html").write_text(html, encoding="utf-8")

# 4) app.js: loader + renderer appended
js += r'''

// ---- full scan (pair-driven results) ----
const fullScanState = { loaded: false, loading: null, dir: 'exposure', index: null, edges: [], byExposure: new Map(), byPhenotype: new Map() };

function fsLabel(kind, id, labels) {
  return labels[id] || id;
}

async function loadFullScan() {
  if (fullScanState.loaded) return;
  if (fullScanState.loading) return fullScanState.loading;
  fullScanState.loading = (async () => {
    const meta = byId('fsMeta');
    if (meta) meta.textContent = '正在加载索引…';
    const index = await fetch('scan/index.json', { cache: 'no-store' }).then(r => r.json());
    fullScanState.index = index;
    const labelMap = {};
    index.exposures.forEach(item => { labelMap[item.id] = item.label; });
    index.outcomes.forEach(item => { labelMap[item.id] = item.label; });
    fullScanState.labels = labelMap;
    if (meta) meta.textContent = `索引已载入：${index.exposures.length} 个暴露、${index.outcomes.length} 个结局，正在载入结果分片…`;
    const shards = await Promise.all(Array.from({ length: 8 }, (_, i) =>
      fetch(`scan/edges_${i}.json`, { cache: 'no-store' }).then(r => r.json())));
    fullScanState.edges = shards.flat();
    for (const row of fullScanState.edges) {
      const [e, p, term, est, se, lo, hi, pv, q, n] = row;
      const record = { e, p, term, est, se, lo, hi, pv, q, n };
      if (!fullScanState.byExposure.has(e)) fullScanState.byExposure.set(e, []);
      if (!fullScanState.byPhenotype.has(p)) fullScanState.byPhenotype.set(p, []);
      fullScanState.byExposure.get(e).push(record);
      fullScanState.byPhenotype.get(p).push(record);
    }
    fullScanState.loaded = true;
    if (meta) meta.textContent = '';
    document.querySelectorAll('.fs-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        fullScanState.dir = btn.dataset.dir;
        document.querySelectorAll('.fs-tab').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
        byId('fsPickLabel').textContent = fullScanState.dir === 'exposure' ? '选择暴露' : '选择结局';
        fillFsOptions();
      });
    });
    byId('fsSearch').addEventListener('input', fillFsOptions);
    byId('fsSelect').addEventListener('change', renderFsTable);
    fillFsOptions();
  })();
  return fullScanState.loading;
}

function fillFsOptions() {
  const index = fullScanState.index;
  if (!index) return;
  const dir = fullScanState.dir;
  const list = (dir === 'exposure' ? index.exposures : index.outcomes)
    .slice().sort((a, b) => b.n_results - a.n_results);
  const q = (byId('fsSearch').value || '').trim().toLowerCase();
  const filtered = q ? list.filter(item => (item.label + ' ' + item.id).toLowerCase().includes(q)) : list;
  const select = byId('fsSelect');
  select.innerHTML = '';
  filtered.slice(0, 400).forEach(item => {
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = `${item.label}（${item.n_results} 条）`;
    select.appendChild(option);
  });
  byId('fsMeta').textContent = `${filtered.length} 个可选${dir === 'exposure' ? '暴露' : '结局'}；全库 ${index.n_results.toLocaleString()} 条结果（n≥${index.min_n}）`;
  renderFsTable();
}

function fsTermLabel(term) {
  if (!term) return '—';
  if (term.startsWith('__bin_')) return '是 vs 否';
  const parts = term.split('_lvl');
  if (parts.length > 1) return '水平 ' + parts[1];
  return term;
}

function renderFsTable() {
  const dir = fullScanState.dir;
  const id = byId('fsSelect').value;
  const body = byId('fsBody');
  if (!body) return;
  body.innerHTML = '';
  if (!id) return;
  const rows = (dir === 'exposure' ? fullScanState.byExposure : fullScanState.byPhenotype).get(id) || [];
  if (!rows.length) {
    body.innerHTML = '<tr><td colspan="7">该指标暂无结果</td></tr>';
    return;
  }
  const sorted = rows.slice().sort((a, b) => (a.pv ?? 1) - (b.pv ?? 1));
  const limit = Math.min(sorted.length, 400);
  for (let i = 0; i < limit; i += 1) {
    const row = sorted[i];
    const otherId = dir === 'exposure' ? row.p : row.e;
    const other = fullScanState.labels[otherId] || otherId;
    const tr = document.createElement('tr');
    if (row.q != null && row.q < 0.05) tr.className = 'sig';
    tr.innerHTML = `<td>${other}</td><td>${fsTermLabel(row.term)}</td>` +
      `<td class="num">${row.est.toFixed(3)}</td>` +
      `<td class="num">${row.lo.toFixed(3)} ~ ${row.hi.toFixed(3)}</td>` +
      `<td class="num">${row.pv < 0.001 ? '<0.001' : row.pv.toFixed(3)}</td>` +
      `<td class="num">${row.q == null ? '—' : (row.q < 0.001 ? '<0.001' : row.q.toFixed(3))}</td>` +
      `<td class="num">${row.n.toLocaleString()}</td>`;
    body.appendChild(tr);
  }
  if (sorted.length > limit) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td colspan="7">仅显示前 ${limit} 条，共 ${sorted.length} 条</td>`;
    body.appendChild(tr);
  }
}
'''

(BASE / "app.js").write_text(js, encoding="utf-8")

# 5) hook in showView
js2 = (BASE / "app.js").read_text(encoding="utf-8")
js2 = js2.replace("  if (id === 'compare') loadCompare();",
                  "  if (id === 'fullScan') loadFullScan();\n  if (id === 'compare') loadCompare();", 1)
(BASE / "app.js").write_text(js2, encoding="utf-8")
print("site wired for full scan")
