const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('site-prototype/dist/app.js', 'utf8');
const html = fs.readFileSync('site-prototype/dist/index.html', 'utf8');
for (const id of ['associationFilters', 'associationExposure', 'associationPhenotype', 'associationWave', 'associationModel']) {
  assert.ok(html.includes(`id="${id}"`), `results browser needs ${id}`);
}
const start = source.indexOf('function renderAssociationRows() {');
const end = source.indexOf('\nfunction addOptions(', start);
assert.notEqual(start, -1, 'association row renderer should exist');
assert.notEqual(end, -1, 'association loader boundary should exist');

class Element {
  constructor() { this.children = []; this.hidden = false; this.textContent = ''; this.value = ''; this.dataset = {}; }
  replaceChildren() { this.children = []; }
  append(child) { this.children.push(child); }
  addEventListener() {}
}

const elements = new Map();
for (const id of ['associationExposure', 'associationPhenotype', 'associationWave', 'associationModel', 'associationFilters', 'rows', 'empty', 'count']) {
  elements.set(id, new Element());
}
elements.get('associationWave').value = '2011';
const fixtureRows = [
  { analysis_id: 'a1', disclosure_status: 'approved_public_aggregate', exposure_concept_id: 'water', exposure_variable: 'i017', phenotype_concept_id: 'glucose', phenotype_variable: 'bl_glu', wave: '2011', model_id: 'M1', estimate_type: 'linear', contrast: 'yes vs no', variance_design: 'reviewed', estimate: '0.2', standard_error: '0.1', ci_lower: '0.0', ci_upper: '0.4', n_model: '100', fit_status: 'success' },
  { analysis_id: 'a2', disclosure_status: 'approved_public_aggregate', exposure_concept_id: 'water', exposure_variable: 'i017', phenotype_concept_id: 'glucose', phenotype_variable: 'bl_glu', wave: '2013', model_id: 'M1', estimate_type: 'linear', contrast: 'yes vs no', variance_design: 'reviewed', estimate: '0.3', standard_error: '0.1', ci_lower: '0.1', ci_upper: '0.5', n_model: '90', fit_status: 'success' },
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
      families: [{ family_id: 'fixture', family_size: 2, rows: fixtureRows }],
    }),
  }),
};
vm.runInNewContext(`${source.slice(start, end)}\nglobalThis.renderRows = renderAssociationRows; globalThis.loadResults = renderAssociations;`, context);

async function main() {
context.renderRows();
assert.equal(elements.get('rows').children.length, 1, 'wave filter should retain only its matching approved row');
assert.match(elements.get('rows').children[0].children[0].textContent, /water · i017/);
assert.equal(elements.get('rows').children[0].children[4].title, 'linear · yes vs no · reviewed');
assert.match(elements.get('count').textContent, /1 \/ 2/);
assert.equal(elements.get('empty').hidden, true);

elements.get('associationWave').value = '2020';
context.renderRows();
assert.equal(elements.get('rows').children.length, 0);
assert.equal(elements.get('empty').hidden, false);
assert.equal(elements.get('empty').textContent, '当前筛选条件下没有结果。');
elements.get('associationWave').value = '';
await context.loadResults();
assert.equal(elements.get('rows').children.length, 2, 'loader should render the complete approved payload family');
assert.equal(elements.get('associationFilters').hidden, false);
assert.ok(elements.get('associationExposure').children.some(option => option.value === 'water'));
assert.match(elements.get('count').textContent, /2 \/ 2/);
console.log('PASS: reviewed association browser loads approved payloads and filters aggregate rows safely');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
