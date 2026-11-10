"""Redesign the homepage overview and fix the clipped nav menus."""
from pathlib import Path

BASE = Path("site-prototype/dist")
html = (BASE / "index.html").read_text(encoding="utf-8")
js = (BASE / "app.js").read_text(encoding="utf-8")

# 1) nav must not clip its dropdown panels
html = html.replace(
    ".primary-nav{display:flex;gap:6px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:thin;padding-bottom:2px}",
    ".primary-nav{display:flex;gap:6px;flex-wrap:wrap;overflow:visible;padding-bottom:2px}",
    1,
)

# 2) hero stats reflect the scan size
start = html.index('<div class="stats" aria-label="目录进度">')
end = html.index('<section class="overview-figures"', start)
new_stats = '''<div class="stats" aria-label="全库规模">
      <div class="stat"><b>113,201</b><span>公开关联结果</span></div>
      <div class="stat"><b>758</b><span>暴露指标</span></div>
      <div class="stat"><b>181</b><span>结局指标</span></div>
      <div class="stat"><b>453,993</b><span>次加权模型拟合</span></div>
    </div>
    <p class="stats-note">5 个调查波次 · 91,543 个"暴露—结局"配对 · 全部结果公开（含不显著）· 不发布个体数据</p>
    '''
html = html[:start] + new_stats + html[end:]

# 3) replace the six-card grid with full-width scale sections
start = html.index('<section class="overview-figures" id="homeOverview"')
end = html.index('</section>', start) + len('</section>')
new_section = '''<section class="overview-figures" id="homeOverview" aria-label="数据概览" hidden>
      <div class="ov-scale">
        <div class="ov-kpi"><b>453,993</b><span>模型拟合</span></div>
        <div class="ov-arrow">→</div>
        <div class="ov-kpi"><b>136,129</b><span>配对结果</span></div>
        <div class="ov-arrow">→</div>
        <div class="ov-kpi accent"><b>113,201</b><span>公开结果（n≥100）</span></div>
      </div>
      <div class="ov-wide">
        <h3>五波拟合量</h3>
        <p class="preview-sub">每个波次独立拟合，跨波合并为配对结果</p>
        <div id="overviewWaves" class="stack-box"></div>
      </div>
      <div class="ov-two">
        <article class="ov-card">
          <h3>结果构成</h3>
          <p class="preview-sub">显著与不显著全部保留</p>
          <div id="overviewMix" class="donut-box"></div>
        </article>
        <article class="ov-card">
          <h3>结果最多的暴露</h3>
          <p class="preview-sub">按配对数量排序</p>
          <div id="overviewECats" class="preview-bars"></div>
        </article>
      </div>
      <div class="ov-two">
        <article class="ov-card">
          <h3>结果最多的结局</h3>
          <p class="preview-sub">按配对数量排序</p>
          <div id="overviewPCats" class="preview-bars"></div>
        </article>
        <article class="ov-card">
          <h3>波次与问卷模块</h3>
          <p class="preview-sub">字段来源流向，取前六模块</p>
          <div id="overviewFlow" class="sankey-box"></div>
        </article>
      </div>
    </section>'''
html = html[:start] + new_section + html[end:]

# 4) styles
style = '''
<style id="home-v2-style">
.ov-scale{display:flex;align-items:center;gap:16px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 22px;margin-bottom:14px;flex-wrap:wrap}
.ov-kpi b{display:block;font-size:26px;color:var(--navy);line-height:1.15}
.ov-kpi span{font-size:12px;color:var(--muted)}
.ov-kpi.accent b{color:#1f6f57}
.ov-arrow{color:#9fb3c0;font-size:20px}
.ov-wide{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:14px}
.ov-two{display:grid;grid-template-columns:1.05fr .95fr;gap:14px;margin-bottom:14px}
.ov-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.ov-card h3,.ov-wide h3{margin:0 0 2px;font-size:15px}
@media(max-width:800px){.ov-two{grid-template-columns:1fr}.ov-scale{flex-direction:column;align-items:flex-start}}
</style>
'''
html = html.replace("</head>", style + "</head>", 1)

# 5) bump script version
html = html.replace("app.js?v=285", "app.js?v=286")

(BASE / "index.html").write_text(html, encoding="utf-8")

# 6) renderer
old_start = js.index("function renderHomeOverview(data) {")
old_end = js.index("function loadHomeOverview()")
new_render = '''function renderHomeOverview(data) {
  const box = byId('homeOverview');
  if (!box || !data) return;
  const stats = data.stats || {};
  if (byId('overviewMix')) {
    overviewDonut(byId('overviewMix'), data.mix.map(item => ({ label: item.label, value: item.value, color: item.color })));
  }
  const waveBox = byId('overviewWaves');
  if (waveBox && data.waves) {
    const max = Math.max(...data.waves.map(row => row.fits), 1);
    waveBox.innerHTML = data.waves.map(row => `<div class="stack-row"><span class="stack-label">${row.wave}</span>` +
      `<span class="stack-track"><i class="seg e" style="width:${(row.fits / max * 100).toFixed(1)}%" title="拟合 ${row.fits}"></i></span>` +
      `<span class="stack-value">${row.fits.toLocaleString()}</span></div>`).join('');
  }
  const drawTop = (target, rows) => {
    if (!target || !rows) return;
    const max = Math.max(...rows.map(item => item.n), 1);
    target.replaceChildren(...rows.map(item => previewRow(item.label, item.n.toLocaleString(), item.n / max * 100, { plain: true })));
  };
  drawTop(byId('overviewECats'), data.top_exposures);
  drawTop(byId('overviewPCats'), data.top_outcomes);
  if (byId('overviewFlow') && data.flow) overviewSankey(byId('overviewFlow'), data.flow);
  box.hidden = false;
}

'''
js = js[:old_start] + new_render + js[old_end:]

js = js.replace("homeOverviewLoaded = fetch('./home_overview_v1.json?v=1', { cache: 'no-cache' })",
                "homeOverviewLoaded = fetch('./home_overview_v2.json?v=2', { cache: 'no-cache' })", 1)

(BASE / "app.js").write_text(js, encoding="utf-8")
print("homepage redesigned, nav unclipped")
