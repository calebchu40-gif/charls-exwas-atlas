// Browser regression for the public atlas.
//
// Usage: node scripts/browser_regression.cjs [site-url]
// Requires a Chrome/Edge instance exposing CDP on 127.0.0.1:9222 and a static
// server for the site (for example `npx serve site-prototype/dist -l 8777`).
//
// The checks mirror the regressions fixed in the November 2026 polish pass:
// a view target that hides every section, a tab strip bound to the view router,
// an in-page anchor treated as a view, an off-screen overflow menu, a clipped
// heatmap, labels that leave the canvas, and a catalog that cannot page.
const base = 'http://127.0.0.1:9222';
const url = process.argv[2] || 'http://127.0.0.1:8777/index.html';

const target = await (await fetch(`${base}/json/new?url=about:blank`, { method: 'PUT' })).json();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let id = 0;
const pending = new Map();
ws.onmessage = event => {
  const msg = JSON.parse(event.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  }
};
const send = (method, params = {}) => {
  const mid = ++id;
  ws.send(JSON.stringify({ id: mid, method, params }));
  return new Promise((resolve, reject) => pending.set(mid, { resolve, reject }));
};
const sleep = ms => new Promise(r => setTimeout(r, ms));
const evaluate = async (expression, timeoutMs = 25000) => {
  const result = await Promise.race([
    send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
    new Promise((_, reject) => setTimeout(() => reject(new Error('eval timeout')), timeoutMs)),
  ]);
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};

const results = [];
const check = (name, ok, detail) => {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${detail === undefined ? '' : ` — ${detail}`}`);
};

await send('Page.enable');
await send('Runtime.enable');

const load = async (reload) => {
  await send('Page.navigate', { url });
  await sleep(reload ? 4200 : 3200);
};

// ---------------------------------------------------------------- desktop pass
await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
await load(false);

const nav = await evaluate(`(() => ({
  primary: [...document.querySelectorAll('.primary-nav > button')].length,
  hasMore: !!document.querySelector('details.special-nav'),
  views: [...document.querySelectorAll('.primary-nav > button')].map(b => b.dataset.view),
}))()`);
check('six primary entry points plus the overflow menu',
  nav.primary === 6 && nav.hasMore, JSON.stringify(nav.views));

const viewWalk = await evaluate(`(async () => {
  const targets = ['overview','byPhenotype','byExposure','groups','exposures','phenotypes','topics','associations','network','crosswave','modules','metadata'];
  const bad = [];
  for (const target of targets) {
    showView(target);
    await new Promise(r => setTimeout(r, 120));
    const visible = [...document.querySelectorAll('.view')].filter(v => !v.hidden).map(v => v.id);
    if (visible.length !== 1 || visible[0] !== target) bad.push([target, visible]);
  }
  return bad;
})()`);
check('every navigation target reveals exactly its own section', viewWalk.length === 0, JSON.stringify(viewWalk));

const anchor = await evaluate(`(async () => {
  document.querySelector('a.toplink').click();
  await new Promise(r => setTimeout(r, 600));
  const visible = [...document.querySelectorAll('.view')].filter(v => !v.hidden).map(v => v.id);
  return { visible, hasTarget: !!document.getElementById('method') };
})()`);
check('the methods link scrolls instead of blanking the page',
  anchor.hasTarget && anchor.visible.length === 1, JSON.stringify(anchor.visible));

const tabs = await evaluate(`(async () => {
  document.querySelector('.special-nav summary').click();
  await new Promise(r => setTimeout(r, 200));
  document.querySelector('.special-nav-menu [data-view="modules"]').click();
  await new Promise(r => setTimeout(r, 4200));
  const button = document.querySelector('#moduleTabs button[data-module="mental"]');
  button.click();
  await new Promise(r => setTimeout(r, 700));
  return {
    view: document.body.dataset.view,
    rows: document.querySelectorAll('#moduleBody table tbody tr').length,
    label: document.querySelector('#moduleBody table tbody tr td')?.textContent || '',
  };
})()`);
check('the research tab strip does not hide the page', tabs.view === 'modules' && tabs.rows > 0,
  `${tabs.rows} rows`);
check('the research tables carry Chinese labels', /[\u4e00-\u9fff]/.test(tabs.label), tabs.label.slice(0, 32));

const associations = await evaluate(`(async () => {
  showView('associations');
  await new Promise(r => setTimeout(r, 2400));
  const all = document.getElementById('associationShowAll');
  if (all) all.click();
  await new Promise(r => setTimeout(r, 800));
  const first = document.querySelector('#rows tr td');
  return {
    rows: document.querySelectorAll('#rows tr').length,
    heatmaps: document.querySelectorAll('.heatmap-table').length,
    firstCell: first ? first.textContent : '',
    exportButton: !!document.getElementById('associationExport'),
  };
})()`);
check('the association browser renders all reviewed rows', associations.rows === 950 && associations.heatmaps > 0,
  `${associations.rows} rows / ${associations.heatmaps} heatmaps`);
check('the association table shows label plus CHARLS code', associations.firstCell.includes('（'),
  associations.firstCell.slice(0, 40));

const catalog = await evaluate(`(async () => {
  showView('exposures');
  await new Promise(r => setTimeout(r, 2400));
  const before = document.querySelectorAll('#eRows tr').length;
  const more = document.getElementById('eMore');
  if (more && !more.hidden) { more.click(); await new Promise(r => setTimeout(r, 700)); }
  return { before, after: document.querySelectorAll('#eRows tr').length };
})()`);
check('the catalog pages past the first hundred rows', catalog.before === 100 && catalog.after === 200,
  `${catalog.before} → ${catalog.after}`);

const network = await evaluate(`(async () => {
  document.querySelector('.special-nav summary').click();
  await new Promise(r => setTimeout(r, 200));
  document.querySelector('.special-nav-menu [data-view="network"]').click();
  await new Promise(r => setTimeout(r, 3200));
  const texts = [...document.querySelectorAll('#networkCanvas svg text')];
  return { labels: texts.length, outside: texts.filter(t => t.getBBox().x < 0).length };
})()`);
check('no network label leaves the canvas', network.outside === 0 && network.labels > 0,
  `${network.labels} labels`);

// ----------------------------------------------------------------- mobile pass
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await load(true);

const menu = await evaluate(`(async () => {
  document.querySelector('.special-nav summary').click();
  await new Promise(r => setTimeout(r, 250));
  const rect = document.querySelector('.special-nav-menu').getBoundingClientRect();
  const inside = rect.left >= 0 && rect.right <= window.innerWidth + 1;
  document.body.click();
  return { left: Math.round(rect.left), right: Math.round(rect.right), vw: window.innerWidth, inside };
})()`);
check('the overflow menu opens inside the phone viewport', menu.inside,
  `${menu.left}–${menu.right} of ${menu.vw}`);

const overflow = await evaluate(`(async () => {
  const out = [];
  for (const target of ['overview','associations','modules','exposures','topics']) {
    showView(target);
    await new Promise(r => setTimeout(r, 500));
    out.push([target, document.documentElement.scrollWidth]);
  }
  return out;
})()`);
const tooWide = overflow.filter(([, width]) => width > 391);
check('no view scrolls horizontally on a phone', tooWide.length === 0, JSON.stringify(overflow));

const heatmap = await evaluate(`(async () => {
  showView('associations');
  await new Promise(r => setTimeout(r, 2600));
  const all = document.getElementById('associationShowAll');
  if (all) all.click();
  await new Promise(r => setTimeout(r, 900));
  const blocks = document.getElementById('heatmapBlocks');
  return { client: blocks.clientWidth, scroll: blocks.scrollWidth };
})()`);
check('the heatmap scrolls inside its panel instead of clipping', heatmap.scroll > heatmap.client,
  `${heatmap.client} / ${heatmap.scroll}`);

await fetch(`${base}/json/close/${target.id}`).catch(() => {});
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} browser checks passed`);
await sleep(300);
process.exit(failed.length === 0 ? 0 : 1);
