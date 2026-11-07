// Browser regression for the public atlas.
//
// Usage: node scripts/browser_regression.mjs [site-url]
// Requires a Chrome/Edge instance exposing CDP on 127.0.0.1:9222 and a static
// server for the site (for example `npx serve site-prototype/dist -l 8777`).
//
// The checks mirror the regressions fixed in the November 2026 polish pass:
// a navigation target that hides every section, a tab strip bound to the view
// router, an in-page anchor treated as a view, an off-screen overflow menu, a
// clipped heatmap, labels that leave the canvas, and a catalog that cannot page.
//
// Every wait polls for a condition instead of sleeping a fixed time, so the same
// script is usable on a laptop and on a slower CI runner.
const base = 'http://127.0.0.1:9222';
const url = process.argv[2] || 'http://127.0.0.1:8777/index.html';

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function openTarget() {
  for (let attempt = 0; attempt < 40; attempt += 1) {
    try {
      const response = await fetch(`${base}/json/new?url=about:blank`, { method: 'PUT' });
      if (response.ok) return await response.json();
    } catch {
      // browser not listening yet
    }
    await sleep(500);
  }
  throw new Error('no CDP endpoint on 127.0.0.1:9222');
}

const target = await openTarget();
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

const evaluate = async (expression, timeoutMs = 30000) => {
  const result = await Promise.race([
    send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }),
    new Promise((_, reject) => setTimeout(() => reject(new Error('eval timeout')), timeoutMs)),
  ]);
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};

const waitFor = async (expression, timeoutMs = 20000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      if (await evaluate(expression, 8000)) return true;
    } catch {
      // page still navigating
    }
    await sleep(250);
  }
  return false;
};

const results = [];
const check = (name, ok, detail) => {
  results.push({ name, ok });
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${detail === undefined ? '' : ` — ${detail}`}`);
};

const openView = async view => {
  const found = await waitFor(`!!document.querySelector('.special-nav-menu [data-view="${view}"]')`);
  if (found) {
    await evaluate(`document.querySelector('.special-nav summary').click()`);
    await sleep(150);
    await evaluate(`document.querySelector('.special-nav-menu [data-view="${view}"]').click()`);
  }
  return waitFor(`document.body.dataset.view === '${view}'`);
};

await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
await waitFor(`document.querySelectorAll('.primary-nav > button').length === 6`, 30000);

// ---------------------------------------------------------------- desktop pass
const nav = await evaluate(`(() => ({
  primary: [...document.querySelectorAll('.primary-nav > button')].length,
  hasMore: !!document.querySelector('details.special-nav'),
  views: [...document.querySelectorAll('.primary-nav > button')].map(b => b.dataset.view),
}))()`);
check('six primary entry points plus the overflow menu',
  nav.primary === 6 && nav.hasMore, JSON.stringify(nav.views));

const viewWalk = await evaluate(`(async () => {
  const targets = ['overview','byPhenotype','byExposure','groups','exposures','phenotypes','topics'];
  const bad = [];
  for (const target of targets) {
    showView(target);
    await new Promise(r => setTimeout(r, 120));
    const visible = [...document.querySelectorAll('.view')].filter(v => !v.hidden).map(v => v.id);
    if (visible.length !== 1 || visible[0] !== target) bad.push([target, visible]);
  }
  return bad;
})()`);
check('every primary target reveals exactly its own section', viewWalk.length === 0, JSON.stringify(viewWalk));

const anchor = await evaluate(`(async () => {
  document.querySelector('a.toplink').click();
  await new Promise(r => setTimeout(r, 600));
  const visible = [...document.querySelectorAll('.view')].filter(v => !v.hidden).map(v => v.id);
  return { visible, hasTarget: !!document.getElementById('method') };
})()`);
check('the methods link scrolls instead of blanking the page',
  anchor.hasTarget && anchor.visible.length === 1, JSON.stringify(anchor.visible));

const focus = await evaluate(`(async () => {
  document.querySelector('.primary-nav [data-view="phenotypes"]').click();
  await new Promise(r => setTimeout(r, 400));
  const active = document.activeElement;
  return { tag: active.tagName, text: active.textContent.slice(0, 24) };
})()`);
check('a view change moves focus to its heading', focus.tag === 'H2', `${focus.tag} ${focus.text}`);

const modulesReady = await openView('modules');
await waitFor(`document.querySelectorAll('#moduleTabs button[data-module]').length >= 5`);
const tabs = await evaluate(`(async () => {
  const button = document.querySelector('#moduleTabs button[data-module="mental"]');
  button.click();
  await new Promise(r => setTimeout(r, 400));
  return {
    view: document.body.dataset.view,
    rows: document.querySelectorAll('#moduleBody table tbody tr').length,
    label: document.querySelector('#moduleBody table tbody tr td')?.textContent || '',
  };
})()`);
check('the research tab strip does not hide the page', modulesReady && tabs.view === 'modules' && tabs.rows > 0,
  `${tabs.rows} rows`);
check('the research tables carry Chinese labels', /[\u4e00-\u9fff]/.test(tabs.label), tabs.label.slice(0, 32));

await openView('associations');
await waitFor(`document.querySelectorAll('#rows tr').length > 0`, 30000);
const associations = await evaluate(`(async () => {
  const all = document.getElementById('associationShowAll');
  if (all) all.click();
  await new Promise(r => setTimeout(r, 600));
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

await openView('exposures');
await waitFor(`document.querySelectorAll('#eRows tr').length > 0`, 40000);
const catalog = await evaluate(`(async () => {
  const before = document.querySelectorAll('#eRows tr').length;
  const more = document.getElementById('eMore');
  if (more && !more.hidden) { more.click(); await new Promise(r => setTimeout(r, 500)); }
  return { before, after: document.querySelectorAll('#eRows tr').length };
})()`);
check('the catalog pages past the first hundred rows', catalog.before === 100 && catalog.after === 200,
  `${catalog.before} → ${catalog.after}`);

await openView('network');
await waitFor(`document.querySelectorAll('#networkCanvas svg text').length > 0`, 30000);
const network = await evaluate(`(() => {
  const texts = [...document.querySelectorAll('#networkCanvas svg text')];
  return { labels: texts.length, outside: texts.filter(t => t.getBBox().x < 0).length };
})()`);
check('no network label leaves the canvas', network.outside === 0 && network.labels > 0,
  `${network.labels} labels`);

// ----------------------------------------------------------------- mobile pass
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await send('Page.navigate', { url });
await waitFor(`document.querySelectorAll('.primary-nav > button').length === 6`, 30000);

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
    await new Promise(r => setTimeout(r, 400));
    out.push([target, document.documentElement.scrollWidth]);
  }
  return out;
})()`);
const tooWide = overflow.filter(([, width]) => width > 391);
check('no view scrolls horizontally on a phone', tooWide.length === 0, JSON.stringify(overflow));

await openView('associations');
await waitFor(`document.querySelectorAll('#rows tr').length > 0`, 30000);
const heatmap = await evaluate(`(async () => {
  const all = document.getElementById('associationShowAll');
  if (all) all.click();
  await new Promise(r => setTimeout(r, 600));
  const blocks = document.getElementById('heatmapBlocks');
  return { client: blocks.clientWidth, scroll: blocks.scrollWidth };
})()`);
check('the heatmap scrolls inside its panel instead of clipping', heatmap.scroll > heatmap.client,
  `${heatmap.client} / ${heatmap.scroll}`);

await openView('modules');
await waitFor(`document.querySelectorAll('#moduleBody svg.forest text').length > 0`, 30000);
const figureText = await evaluate(`(() => {
  const svg = document.querySelector('#moduleBody svg.forest');
  if (!svg) return null;
  const scale = svg.getBoundingClientRect().width / (svg.viewBox.baseVal.width || 1);
  const sizes = [...svg.querySelectorAll('text')].map(node => parseFloat(getComputedStyle(node).fontSize) * scale);
  return { scale: Math.round(scale * 100) / 100, min: Math.round(Math.min(...sizes) * 10) / 10 };
})()`);
check('figure labels stay legible on a phone', figureText !== null && figureText.min >= 9,
  figureText ? `${figureText.min}px at scale ${figureText.scale}` : 'no figure');

await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
await waitFor(`document.querySelectorAll('.primary-nav > button').length === 6`, 30000);

const escapeMenu = await evaluate(`(async () => {
  const details = document.querySelector('details.special-nav');
  details.querySelector('summary').click();
  await new Promise(r => setTimeout(r, 200));
  const opened = details.hasAttribute('open');
  details.querySelector('summary').focus();
  return { opened };
})()`);
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
await sleep(250);
const escapeResult = await evaluate(`(() => {
  const details = document.querySelector('details.special-nav');
  return { closed: !details.hasAttribute('open'), focused: document.activeElement === details.querySelector('summary') };
})()`);
check('Escape closes the overflow menu and restores focus',
  escapeMenu.opened && escapeResult.closed && escapeResult.focused, JSON.stringify(escapeResult));

await evaluate(`document.body.focus()`);
await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
await sleep(300);
const focusRing = await evaluate(`(() => {
  const active = document.activeElement;
  const style = getComputedStyle(active);
  return { tag: active.tagName, visible: active.matches(':focus-visible'), outline: style.outlineStyle + ' ' + style.outlineWidth };
})()`);
check('keyboard focus is visible', focusRing.visible && focusRing.outline.startsWith('solid'),
  `${focusRing.tag} ${focusRing.outline}`);

await fetch(`${base}/json/close/${target.id}`).catch(() => {});
const failed = results.filter(r => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} browser checks passed`);
await sleep(300);
process.exit(failed.length === 0 ? 0 : 1);
