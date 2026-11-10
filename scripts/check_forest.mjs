// Measure the modules forest figure layout after it renders.
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
await send('Emulation.setDeviceMetricsOverride', { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: `${url}?t=${Date.now()}` });
await new Promise(r => setTimeout(r, 3000));
const info = await evaluate(`(async () => {
  const navButton = document.querySelector('.primary-nav [data-view="modules"]');
  const loadError = '';
  if (navButton) navButton.click();
  await new Promise(r => setTimeout(r, 1200));
  const tab = document.querySelector('#moduleTabs button[data-module="forest"]');
  if (tab) tab.click();
  const start = Date.now();
  while (Date.now() - start < 40000 && !document.querySelector('#moduleBody svg')) {
    await new Promise(r => setTimeout(r, 400));
  }
  const figure = document.querySelector('#moduleBody .figure-scroll');
  const svg = figure ? figure.querySelector('svg') : null;
  const wrap = figure ? figure.getBoundingClientRect() : null;
  const svgRect = svg ? svg.getBoundingClientRect() : null;
  const texts = figure ? [...figure.querySelectorAll('text')].slice(0, 3).map(t => ({ text: t.textContent, left: Math.round(t.getBoundingClientRect().left), w: Math.round(t.getBoundingClientRect().width) })) : [];
  return {
    bodyText: (document.getElementById('moduleBody')||{}).textContent.slice(0, 160),
    loadError,
    bodySvg: !!svg, wrapW: wrap ? Math.round(wrap.width) : 0,
    wrapScrollW: figure ? figure.scrollWidth : 0, scrollLeft: figure ? figure.scrollLeft : 0,
    svgW: svgRect ? Math.round(svgRect.width) : 0, svgLeft: svgRect ? Math.round(svgRect.left) : 0,
    texts,
  };
})()`);
console.log(JSON.stringify(info));
ws.close();
