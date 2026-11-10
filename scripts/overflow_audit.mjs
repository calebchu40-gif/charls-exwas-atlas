// Audit horizontal overflow for every view at desktop and phone widths.
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
const evaluate = async expression => {
  const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text);
  return result.result.value;
};
await send('Page.enable');
await send('Runtime.enable');
await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });

const widths = [[1400, 1000], [390, 844]];
const views = ['overview', 'byPhenotype', 'byExposure', 'groups', 'exposures', 'phenotypes', 'metadata', 'associations', 'fullScan', 'significant', 'compare', 'network', 'crosswave', 'modules', 'topics', 'chronicConcepts', 'cancerSites', 'disabilityHistory', 'verifiedCodes', 'lifeHistoryExposures', 'housingCatalog', 'householdRentalIncome', 'householdCovidEconomics', 'functionalConcepts', 'healthWorkLimitations', 'moodConcepts', 'cognitionConcepts', 'behaviorExposures', 'healthSymptoms', 'foodEnvironment', 'workExposures', 'communityExposures', 'socialExposures', 'healthcareAccess', 'bloodBiomarkers', 'objectiveMeasures', 'candidatePairExplorer'];

for (const [width, height] of widths) {
  await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: width < 600 });
  await send('Page.navigate', { url: `${url}?t=${Date.now()}` });
  await new Promise(r => setTimeout(r, 3000));
  const report = [];
  for (const view of views) {
    const info = await evaluate(`(async () => {
      if (typeof showView === 'function') showView(${JSON.stringify(view)});
      await new Promise(r => setTimeout(r, 250));
      const doc = document.documentElement;
      const inner = window.innerWidth;
      const offenders = [];
      document.querySelectorAll('#' + ${JSON.stringify(view)} + ' *').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) return;
        if (rect.right > inner + 2 || rect.left < -2) {
          offenders.push({ tag: el.tagName, id: el.id || '', cls: String(el.className || '').slice(0, 40),
            left: Math.round(rect.left), right: Math.round(rect.right) });
        }
      });
      return { view: ${JSON.stringify(view)}, docWidth: doc.scrollWidth, inner,
        overflow: doc.scrollWidth - inner, offenders: offenders.slice(0, 4) };
    })()`);
    report.push(info);
  }
  const bad = report.filter(item => item.overflow > 2);
  console.log(`\n== ${width}px: ${bad.length} views overflow; ${report.filter(item => item.offenders.length).length} with overflowing elements`);
  for (const item of bad) console.log(JSON.stringify(item));
}
ws.close();
