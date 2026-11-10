"""Remove results-first overview blocks and add a usage-first entry panel."""
from pathlib import Path

BASE = Path("site-prototype/dist")
html = (BASE / "index.html").read_text(encoding="utf-8")
js = (BASE / "app.js").read_text(encoding="utf-8")

# 1) homepage: drop the overview figures, add a two-button entry panel
start = html.index('<section class="overview-figures" id="homeOverview"')
end = html.index('</section>', start) + len('</section>')
entry = '''<section class="entry-panel" aria-label="开始使用">
      <button type="button" class="entry-card" data-entry="exposure">
        <b>按暴露查结局</b>
        <span>选一个暴露指标，查看它与全部结局的结果</span>
      </button>
      <button type="button" class="entry-card" data-entry="phenotype">
        <b>按结局查暴露</b>
        <span>选一个结局指标，查看全部暴露对它的结果</span>
      </button>
    </section>'''
html = html[:start] + entry + html[end:]

# 2) modules: drop the result strip
start = html.index('<section class="preview" id="resultStrip"')
end = html.index('</section>', start) + len('</section>')
html = html[:start] + html[end:]

# 3) styles
style = '''
<style id="entry-style">
.entry-panel{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:26px 0 8px}
.entry-card{display:flex;flex-direction:column;gap:6px;align-items:flex-start;text-align:left;background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px 22px;cursor:pointer}
.entry-card:hover{border-color:#9fc2cf;box-shadow:0 6px 18px rgba(24,61,84,.08)}
.entry-card b{font-size:18px;color:var(--navy)}
.entry-card span{font-size:13px;color:#5b7482}
@media(max-width:800px){.entry-panel{grid-template-columns:1fr}}
</style>
'''
html = html.replace("</head>", style + "</head>", 1)
html = html.replace("app.js?v=286", "app.js?v=287")

# 4) JS: stop loading removed blocks and wire entry buttons
js = js.replace("setTimeout(loadHomeOverview, 300);\n", "", 1)
js = js.replace("  if (id === 'modules') loadHomePreview();\n", "", 1)
entry_hook = """
document.querySelectorAll('.entry-card').forEach(card => card.addEventListener('click', () => {
  const dir = card.dataset.entry;
  fullScanState.dir = dir;
  showView('fullScan');
}));
"""
anchor = "document.querySelectorAll('.overview-view [data-view]').forEach(btn => btn.addEventListener('click', () => showView(btn.dataset.view)));"
assert anchor in js, "entry anchor missing"
js = js.replace(anchor, anchor + entry_hook, 1)

# keep the tab labels in sync when the direction is preset from the entry card
js = js.replace("    byId('fsPickLabel').textContent = fullScanState.dir === 'exposure' ? '选择暴露' : '选择结局';",
                "    byId('fsPickLabel').textContent = fullScanState.dir === 'exposure' ? '选择暴露' : '选择结局';\n    document.querySelectorAll('.fs-tab').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.dir === fullScanState.dir)));",
                1)

(BASE / "index.html").write_text(html, encoding="utf-8")
(BASE / "app.js").write_text(js, encoding="utf-8")
print("results-first blocks removed; entry panel added")
