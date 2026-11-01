const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('site-prototype/dist/app.js', 'utf8');
const html = fs.readFileSync('site-prototype/dist/index.html', 'utf8');
for (const id of ['associationFilters', 'associationExposure', 'associationPhenotype', 'associationWave', 'associationModel']) {
  assert.ok(html.includes(`id="${id}"`), `results browser needs ${id}`);
}
const start = source.indexOf('let heatmapRows=[];');
const end = source.indexOf('\nfunction addOptions(', start);
assert.notEqual(start, -1, 'association heatmap and row renderer should exist');
assert.notEqual(end, -1, 'association loader boundary should exist');

class Element {
  constructor() { this.children = []; this.hidden = false; this.textContent = ''; this.value = ''; this.dataset = {}; }
  replaceChildren() { this.children = []; }
  append(child) { this.children.push(child); }
  addEventListener(type, handler) { this.events = this.events || {}; this.events[type] = handler; }
}

const elements = new Map();
for (const id of ['associationExposure', 'associationPhenotype', 'associationWave', 'associationModel', 'associationFit', 'associationSearch', 'associationSort', 'associationClear', 'associationSummary', 'associationFilters', 'rows', 'empty', 'count']) {
  elements.set(id, new Element());
}
elements.get('associationWave').value = '2011';
const fixtureRows = [
  { analysis_id: 'a1', disclosure_status: 'approved_public_aggregate', exposure_concept_id: 'water', exposure_variable: 'i017', phenotype_concept_id: 'glucose', phenotype_variable: 'bl_glu', wave: '2011', model_id: 'M1', estimate_type: 'linear', contrast: 'yes vs no', variance_design: 'reviewed', estimate: '0.2', standard_error: '0.1', ci_lower: '0.0', ci_upper: '0.4', p_value: '0.02', q_value_by: '0.08', p_bonferroni: '0.04', n_model: '100', fit_status: 'success' },
  { analysis_id: 'a2', disclosure_status: 'approved_public_aggregate', exposure_concept_id: 'water', exposure_variable: 'i017', phenotype_concept_id: 'glucose', phenotype_variable: 'bl_glu', wave: '2013', model_id: 'M1', estimate_type: 'linear', contrast: 'yes vs no', variance_design: 'reviewed', estimate: '0.3', standard_error: '0.1', ci_lower: '0.1', ci_upper: '0.5', p_value: '0.01', q_value_by: '0.06', p_bonferroni: '0.03', n_model: '90', fit_status: 'success' },
  { analysis_id: 'a3', disclosure_status: 'withheld', exposure_concept_id: 'water', exposure_variable: 'i017', phenotype_concept_id: 'glucose', phenotype_variable: 'bl_glu', wave: '2011', model_id: 'M1', estimate_type: 'linear', contrast: 'yes vs no', variance_design: '', estimate: '', standard_error: '', ci_lower: '', ci_upper: '', p_value: '', q_value_by: '', p_bonferroni: '', n_model: '', fit_status: 'withheld_disclosure' },
];
const context = {
  associationRows: fixtureRows,
  byId: id => elements.get(id),
  document: { createElement: () => new Element() },
  Option: class extends Element { constructor(text, value) { super(); this.textContent = text; this.value = value; } },
  fetch: async () => ({
    ok: true,
    status: 200,
    json: async () => ({
      schema_version: 1,
      release_status: 'disclosure_reviewed',
      generated_at: '2026-10-27T10:00:00+08:00',
      families: [{ family_id: 'fixture', family_size: 3, rows: fixtureRows }],
    }),
  }),
};
vm.runInNewContext(`${source.slice(start, end)}\nglobalThis.renderRows = renderAssociationRows; globalThis.loadResults = renderAssociations;`
  + '\nglobalThis.heatmapFormat = heatmapFormat; globalThis.heatmapColor = heatmapColor; globalThis.heatmapScale = heatmapScale;', context);

async function main() {
context.renderRows();
assert.equal(elements.get('rows').children.length, 2, 'wave filter should include its approved and withheld rows');
assert.match(elements.get('rows').children[0].children[0].textContent, /water · i017/);
assert.equal(elements.get('rows').children[0].children[4].title, 'linear · yes vs no · reviewed');
assert.match(elements.get('count').textContent, /2 \/ 3/);
assert.equal(elements.get('empty').hidden, true);
const withheldCells = elements.get('rows').children[1].children;
assert.deepEqual(withheldCells.slice(5, 10).map(cell => cell.textContent), ['—', '—', '—', '—', '—']);
assert.match(withheldCells[10].textContent, /披露审查抑制/);

elements.get('associationWave').value = '2020';
context.renderRows();
assert.equal(elements.get('rows').children.length, 0);
assert.equal(elements.get('empty').hidden, false);
assert.equal(elements.get('empty').textContent, '当前筛选条件下没有结果。');
elements.get('associationWave').value = '';
await context.loadResults();
assert.equal(elements.get('rows').children.length, 3, 'loader should retain the complete family including withheld rows');
assert.equal(elements.get('associationFilters').hidden, false);
assert.ok(elements.get('associationExposure').children.some(option => option.value === 'water'));
assert.match(elements.get('count').textContent, /3 \/ 3/);

elements.get('associationFit').value = 'withheld';
context.renderRows();
assert.equal(elements.get('rows').children.length, 1, 'withheld filter should show the suppressed registry row');
assert.match(elements.get('associationSummary').textContent, /披露抑制 1 条/);
elements.get('associationFit').value = '';
elements.get('associationSearch').value = 'bl_glu';
context.renderRows();
assert.equal(elements.get('rows').children.length, 3, 'search should match the source variable code');
elements.get('associationClear').events.click();
assert.equal(elements.get('associationSearch').value, '');
assert.match(elements.get('count').textContent, /3 \/ 3/);

// Heatmap helpers are pure and must stay deterministic for the reviewed payload.
assert.equal(context.heatmapFormat('0.1234'), '0.12');
assert.equal(context.heatmapFormat(''), '—');
assert.equal(context.heatmapFormat('12.34'), '12.3');
assert.equal(context.heatmapScale(fixtureRows), 0.3);
const positive = context.heatmapColor('estimate', { fit_status: 'success', estimate: '0.2', estimate_type: 'beta' }, 0.3);
const negative = context.heatmapColor('estimate', { fit_status: 'success', estimate: '-0.2', estimate_type: 'beta' }, 0.3);
assert.match(positive, /rgba\(32,110,190/);
assert.match(negative, /rgba\(190,70,60/);
assert.match(context.heatmapColor('estimate', { fit_status: 'inestimable', estimate: '' }, 0.3), /#f2f2f2/);
assert.match(context.heatmapColor('q', { fit_status: 'success', estimate: '0.2', q_value_by: '0.001' }, 0.3), /rgba\(31,119,180/);
console.log('PASS: reviewed association browser loads approved payloads and filters aggregate rows safely');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
