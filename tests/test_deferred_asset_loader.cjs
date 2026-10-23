const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const source = fs.readFileSync('site-prototype/dist/app.js', 'utf8');
const html = fs.readFileSync('site-prototype/dist/index.html', 'utf8');
assert.ok(html.includes('app.js?v=59'), 'HTML should cache-bust the updated app loader');
const start = source.indexOf('const deferredViewLoaders = new Map();');
const end = source.indexOf('let candidatePairExplorerLoaded;', start);
assert.notEqual(start, -1, 'deferred loader helper should exist');
assert.notEqual(end, -1, 'deferred loader helper boundary should exist');
const deferredViews = [...source.matchAll(/deferJson\('\.\/[^']+','([^']+)'\)/g)].map((match) => match[1]);
assert.equal(deferredViews.length, 21, 'all topic catalogs should use the lazy loader');
for (const view of deferredViews) {
  assert.ok(html.includes(`id="${view}"`), `deferred view ${view} should exist in the page`);
}
const statusMap = source.match(/const statusIds = \{([^}]+)\}/);
assert.ok(statusMap, 'deferred view loading status map should exist');
for (const [, statusId] of statusMap[1].matchAll(/:'([^']+)'/g)) {
  assert.ok(html.includes(`id="${statusId}"`), `loading status ${statusId} should exist in the page`);
}
assert.ok(source.includes("candidatePairExplorerLoaded=fetch('./candidate_pair_explorer_v1.json"));
assert.ok(source.includes('fetch(`./catalog_${role}.json?v=1`'));
assert.ok(source.includes("loadCatalog('e')"));
assert.ok(source.includes("loadCatalog('p')"));
assert.ok(source.includes("loadCatalog('c')"));
assert.ok(!/^const \w+\s*=\s*fetch\(/m.test(source), 'no JSON request should start during script initialization');

let fetchCount = 0;
const context = {
  fetch: async () => {
    fetchCount += 1;
    return { ok: true, json: async () => ({ loaded: true }) };
  },
};
vm.runInNewContext(
  `${source.slice(start, end)}\nglobalThis.loaderTest = { deferredViewLoaders, deferJson };`,
  context,
);

async function main() {
  const { deferredViewLoaders, deferJson } = context.loaderTest;
  const pending = deferJson('./fixture.json', 'fixtureView');
  assert.equal(fetchCount, 0, 'asset must not be fetched before its view opens');
  deferredViewLoaders.get('fixtureView')();
  deferredViewLoaders.get('fixtureView')();
  const result = await pending;
  assert.equal(fetchCount, 1, 'opening a view more than once must fetch only once');
  assert.equal(JSON.stringify(result), '{"loaded":true}');
  console.log('PASS: deferred JSON loads once on view entry');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
