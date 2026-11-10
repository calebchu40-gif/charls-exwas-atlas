// Find elements clipped without a scrollable ancestor.
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
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const mid = ++id;
  pending.set(mid, { resolve, reject });
  ws.send(JSON.stringify({ id: mid, method, params }));
});
const evaluate = async expression => {
  const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const views = ['overview', 'byPhenotype', 'byExposure', 'groups', 'exposures', 'phenotypes', 'metadata', 'associations', 'fullScan', 'significant', 'compare', 'network', 'crosswave', 'modules', 'topics', 'candidatePairExplorer'];
for (const [width, height] of [[1400, 1000], [390, 844]]) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 600 });
  await send('Page.navigate', { url: `${url}?t=${Date.now()}` });
  await new Promise(r => setTimeout(r, 2500));
  console.log(`\n== ${width}px`);
  for (const view of views) {
    const result = await evaluate(`(async () => {
      const nav = document.querySelector('.primary-nav [data-view="' + ${JSON.stringify(view)} + '"]');
      if (nav) nav.click(); else if (typeof showView === 'function') showView(${JSON.stringify(view)});
      await new Promise(r => setTimeout(r, 900));
      const inner = window.innerWidth;
      const clipped = [];
      document.querySelectorAll('#' + ${JSON.stringify(view)} + ' *').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return;
        if (rect.right <= inner + 2 && rect.left >= -2) return;
        let node = el;
        let scrollable = false;
        while (node && node !== document.body) {
          const style = getComputedStyle(node);
          if ((style.overflowX === 'auto' || style.overflowX === 'scroll') && node.scrollWidth > node.clientWidth + 2) { scrollable = true; break; }
          if (style.overflowX === 'hidden') { break; }
          node = node.parentElement;
        }
        if (!scrollable) clipped.push({ tag: el.tagName, id: el.id || '', cls: String(el.className || '').slice(0, 36), left: Math.round(rect.left), right: Math.round(rect.right) });
      });
      return { clipped: clipped.slice(0, 3) };
    })()`);
    if (result.clipped.length) console.log(view, JSON.stringify(result.clipped));
  }
}
ws.close();
