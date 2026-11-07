// Special analyses: fuel gradient, jointly adjusted household model and effect
// modification. Each tab renders one aggregate JSON produced overnight.

const moduleData = { gradient: null, joint: null, interaction: null, health: null, solid: null, trajectory: null, replication: null, stability: null, anthropometry: null, ageGradient: null, lifestyle: null, strata: null, replication2015: null, anthropometryFull: null, calibration: null, forest: null, gradient2015: null, mental: null, sleep: null };

function moduleNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function moduleTable(rows, columns) {
  const table = document.createElement('table');
  const thead = document.createElement('thead');
  const headRow = document.createElement('tr');
  for (const column of columns) {
    const th = document.createElement('th');
    th.textContent = column.label;
    headRow.append(th);
  }
  thead.append(headRow);
  const tbody = document.createElement('tbody');
  for (const row of rows) {
    const tr = document.createElement('tr');
    for (const column of columns) {
      const td = document.createElement('td');
      td.textContent = column.value(row);
      tr.append(td);
    }
    tbody.append(tr);
  }
  table.append(thead, tbody);
  return table;
}

function gradientTable(payload) {
  const rows = payload.results;
  return moduleTable(rows, [
    { label: '结局', value: row => row.phenotype_concept_id },
    { label: '每等级 β', value: row => row.estimate.toFixed(3) },
    { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
    { label: 'q', value: row => row.q < 0.001 ? '<0.001' : row.q.toFixed(3) },
    { label: 'n', value: row => row.n },
  ]);
}

function jointTable(payload) {
  const rows = payload.results;
  return moduleTable(rows, [
    { label: '结局', value: row => row.phenotype_concept_id },
    { label: '暴露项', value: row => row.term },
    { label: 'β', value: row => row.estimate.toFixed(3) },
    { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
    { label: 'q', value: row => row.q_value_by < 0.001 ? '<0.001' : row.q_value_by.toFixed(3) },
    { label: 'n', value: row => row.n_model },
  ]);
}

function interactionTable(payload) {
  const rows = payload.interactions;
  return moduleTable(rows, [
    { label: '分层', value: row => row.stratum },
    { label: '暴露', value: row => row.exposure_concept_id },
    { label: '结局', value: row => row.phenotype_concept_id },
    { label: '高', value: row => `${row.label_high} ${row.estimate_high.toFixed(3)}` },
    { label: '低', value: row => `${row.label_low} ${row.estimate_low.toFixed(3)}` },
    { label: '差值 p', value: row => row.p_interaction < 0.001 ? '<0.001' : row.p_interaction.toFixed(3) },
  ]);
}

async function loadModules() {
  if (moduleData.gradient) {
    renderModules();
    return;
  }
  try {
    const [gradient, joint, interaction, health, solid, trajectory, replication, stability, anthropometry, ageGradient, lifestyle, strata, replication2015, forest, mental] = await Promise.all([
      fetch('./fuel_gradient_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./joint_household_model_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./effect_modification_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./health_index_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./solid_fuel_blood_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./trajectories_v1.json?v=2', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./replication_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./network_stability_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./wave2013_solid_fuel_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./age_gradient_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./lifestyle_restricted_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./uric_strata_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./wave2015_solid_fuel_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./evidence_forest_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./mental_health_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
    ]);
    moduleData.gradient = gradient;
    moduleData.joint = joint;
    moduleData.interaction = interaction;
    moduleData.health = health;
    moduleData.solid = solid;
    moduleData.trajectory = trajectory;
    moduleData.replication = replication;
    moduleData.stability = stability;
    moduleData.anthropometry = anthropometry;
    moduleData.ageGradient = ageGradient;
    moduleData.lifestyle = lifestyle;
    moduleData.strata = strata;
    moduleData.replication2015 = replication2015;
    moduleData.forest = forest;
    moduleData.mental = mental;
    renderModules();
  } catch (error) {
    byId('moduleBody').textContent = `专项分析载入失败：${error.message}`;
  }
}


const SVG_NS = 'http://www.w3.org/2000/svg';

function svgNode(tag, attrs) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, String(value));
  return node;
}

function renderForest(payload) {
  const entries = payload.entries;
  const width = 900, labelWidth = 320, plotWidth = width - labelWidth - 40, rowHeight = 24;
  const height = entries.length * rowHeight + 56;
  const values = entries.flatMap(row => [row.ci_lower, row.ci_upper]);
  const min = Math.min(...values, 0), max = Math.max(...values, 0);
  const span = max - min || 1;
  const x = value => labelWidth + ((value - min) / span) * plotWidth;
  const svg = svgNode('svg', { viewBox: `0 0 ${width} ${height}`, width: '100%', class: 'forest' });

  svg.append(svgNode('line', { x1: x(0), x2: x(0), y1: 12, y2: height - 12,
    stroke: '#9fb3bf', 'stroke-dasharray': '3 3' }));
  entries.forEach((row, index) => {
    const y = 28 + index * rowHeight;
    const label = svgNode('text', { x: 0, y: y + 4, 'font-size': 12, fill: '#2d4857' });
    label.textContent = row.label;
    svg.append(label);
    svg.append(svgNode('line', { x1: x(row.ci_lower), x2: x(row.ci_upper), y1: y, y2: y,
      stroke: '#7f9aa8', 'stroke-width': 1.5 }));
    svg.append(svgNode('circle', { cx: x(row.estimate), cy: y, r: 4,
      fill: row.estimate < 0 ? '#1f5f8b' : '#b26a2c' }));
  });
  return svg;
}

function renderModules() {
  const target = byId('moduleBody');
  if (!target || !moduleData.gradient) return;
  const active = byId('moduleTabs').dataset.active || 'gradient';
  target.replaceChildren();
  if (active === 'gradient') {
    target.append(gradientTable(moduleData.gradient));
    byId('moduleNote').textContent = '燃料清洁度 0=电、1=天然气/液化气、2=沼气、3=煤/秸秆木材；K=15。';
  } else if (active === 'joint') {
    target.append(jointTable(moduleData.joint));
    byId('moduleNote').textContent = '每个结局一个模型，同时放入自来水与 6 个燃料项；q 按 105 个系数校正。';
  } else if (active === 'interaction') {
    target.append(interactionTable(moduleData.interaction));
    byId('moduleNote').textContent = '按性别、城乡、教育、≥65 岁分层；420 个层间差异检验，未通过 Bonferroni。';
  } else if (active === 'health') {
    target.append(moduleTable(moduleData.health.associations, [
      { label: '暴露项', value: row => row.term },
      { label: 'β（指数 SD）', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p < 0.001 ? '<0.001' : row.p.toFixed(3) },
    ]));
    byId('moduleNote').textContent = '五项 z 分合成（0–100）；n=10,071。';
  } else if (active === 'replication') {
    const rows = [...moduleData.replication.pairs].sort(
      (a, b) => (a.q_2015 ?? 1) - (b.q_2015 ?? 1)).slice(0, 40);
    target.append(moduleTable(rows, [
      { label: '暴露', value: row => row.exposure_concept_id },
      { label: '结局', value: row => row.phenotype_concept_id },
      { label: 'β 2011', value: row => row.beta_2011.toFixed(3) },
      { label: 'β 2015', value: row => row.beta_2015.toFixed(3) },
      { label: 'q 2015', value: row => (row.q_2015 ?? 1) < 0.001 ? '<0.001' : (row.q_2015 ?? 1).toFixed(3) },
      { label: '同向', value: row => row.same_sign ? '是' : '否' },
    ]));
    byId('moduleNote').textContent = `105 项在 2015 可匹配，同向 ${moduleData.replication.same_sign} 项。`;
  } else if (active === 'stability') {
    target.append(moduleTable(moduleData.stability.rows, [
      { label: '暴露对', value: row => row.pair.join(' – ') },
      { label: '2011 ρ', value: row => row.rho['2011'] === undefined ? '—' : row.rho['2011'].toFixed(2) },
      { label: '2013 ρ', value: row => row.rho['2013'] === undefined ? '—' : row.rho['2013'].toFixed(2) },
      { label: '2015 ρ', value: row => row.rho['2015'] === undefined ? '—' : row.rho['2015'].toFixed(2) },
      { label: '方向一致', value: row => row.sign_consistent ? '是' : '否' },
    ]));
    byId('moduleNote').textContent = `${moduleData.stability.edges_in_multiple_waves} 条边出现在 ≥2 个波次，`
      + `${moduleData.stability.edges_in_all_waves} 条三波都有，方向一致率 ${(moduleData.stability.sign_consistent_fraction * 100).toFixed(0)}%。`;
  } else if (active === 'anthropometry') {
    target.append(moduleTable(moduleData.anthropometry.results, [
      { label: '结局', value: row => row.outcome },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '2013 波体测结局。';
  } else if (active === 'agegradient') {
    target.append(moduleTable(moduleData.ageGradient.results, [
      { label: '对照', value: row => row.term },
      { label: '年龄组', value: row => row.band },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '尿酸按基线年龄分组。';
  } else if (active === 'lifestyle') {
    target.append(moduleTable(moduleData.lifestyle.results, [
      { label: '对照', value: row => row.term },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '仅保留从不吸烟且过去一年不饮酒者：燃料—尿酸关联仍显著（固体 −0.244）。';
  } else if (active === 'strata') {
    target.append(moduleTable(moduleData.strata.results, [
      { label: '分层', value: row => row.stratum_set },
      { label: '组', value: row => row.stratum },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = 'BMI 与 eGFR 分层。';
  } else if (active === 'replication2015') {
    target.append(moduleTable(moduleData.replication2015.results, [
      { label: '波次', value: row => row.wave },
      { label: '对照', value: row => row.exposure },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '2015 波，协变量取自 2011 基线。';
  } else if (active === 'anthropometryfull') {
    target.append(moduleTable(moduleData.anthropometryFull.results, [
      { label: '结局', value: row => row.outcome },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'p', value: row => row.p_value < 0.001 ? '<0.001' : row.p_value.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '2013 加 2011 基线城乡/教育后：身高 −0.099、体重 −0.157、BMI −0.133，'
      + '比未调整教育时（−0.138/−0.196/−0.158）普遍减弱，支持部分为社会经济混杂。';
  } else if (active === 'calibration') {
    target.append(moduleTable(moduleData.calibration.families, [
      { label: '家族', value: row => row.family_id },
      { label: '模型', value: row => row.model_id },
      { label: '检验数', value: row => row.tests },
      { label: 'λ', value: row => row.lambda.toFixed(2) },
      { label: 'p<0.05 占比', value: row => (row.share_p_lt_05 * 100).toFixed(0) + '%' },
      { label: '中位 p', value: row => row.median_p.toFixed(3) },
    ]));
    byId('moduleNote').textContent = 'λ 普遍远高于 1：结局相关、家庭社会经济共同因子与家族经过筛选都会抬高 λ；'
      + '这不等于计算错误，但说明本图集是探索性、不可作确证性解读。';
  } else if (active === 'forest') {
    target.append(renderForest(moduleData.forest));
    const gradient = moduleData.forest.gradient;
    byId('moduleNote').textContent = '尿酸相关证据的效应量与区间；梯度项量纲不同，未画入。';
  } else if (active === 'gradient2015') {
    target.append(moduleTable(moduleData.gradient2015.results, [
      { label: '结局', value: row => row.phenotype_concept_id },
      { label: '每等级 β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'q', value: row => row.q_value_by < 0.001 ? '<0.001' : row.q_value_by.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '2015 波同一梯度：尿酸 −0.047（p=0.069），方向与 2011 一致但样本仅 1,553，'
      + '15 项均未过 q<0.05——主要是功效不足，而非方向反转。';
  } else if (active === 'mental') {
    target.append(moduleTable(moduleData.mental.results, [
      { label: '结局', value: row => row.outcome },
      { label: '暴露', value: row => row.exposure },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'q', value: row => row.q_value_by < 0.001 ? '<0.001' : row.q_value_by.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '抑郁（CES-D 0–30）、连续减 7、自评记忆对七类家庭暴露：自来水与天然气方向更好、'
      + '秸秆木材更差；21 项中 8 项过 q<0.05，探索性。';
  } else if (active === 'sleep') {
    target.append(moduleTable(moduleData.sleep.results, [
      { label: '结局', value: row => row.outcome },
      { label: '暴露', value: row => row.exposure },
      { label: row => row.measure === 'OR' ? 'OR' : 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'q', value: row => row.q_value_by < 0.001 ? '<0.001' : row.q_value_by.toFixed(3) },
      { label: 'n', value: row => row.n_model },
    ]));
    byId('moduleNote').textContent = '21 项全部未过 q<0.05（最强为秸秆木材→长睡眠 OR 1.54，q=0.061）。'
      + '这是一个阴性域，说明前两组关联并非"所有结局都关联"。';
  } else if (active === 'trajectory') {
    target.append(moduleTable(moduleData.trajectory.by_wave, [
      { label: '波次', value: row => row.wave },
      { label: '基线年龄', value: row => row.band },
      { label: '自评健康', value: row => row.srh === null ? '—' : row.srh.toFixed(2) },
      { label: '自评记忆', value: row => row.memory === null ? '—' : row.memory.toFixed(2) },
      { label: 'BMI', value: row => row.bmi === null || row.bmi === undefined ? '—' : row.bmi.toFixed(1) },
      { label: 'n', value: row => row.n },
    ]));
    byId('moduleNote').textContent = '按 2011 年龄分层；2018/2020 字段不可比，未纳入。';
  } else {
    target.append(moduleTable(moduleData.solid.results, [
      { label: '结局', value: row => row.phenotype_concept_id },
      { label: 'β', value: row => row.estimate.toFixed(3) },
      { label: '95% CI', value: row => `${row.ci_lower.toFixed(3)} – ${row.ci_upper.toFixed(3)}` },
      { label: 'q', value: row => row.q < 0.001 ? '<0.001' : row.q.toFixed(3) },
      { label: 'n', value: row => row.n },
    ]));
    byId('moduleNote').textContent = '固体燃料（煤/秸秆木材/其他）对 清洁燃料（天然气/液化气/电）；K=15。';
  }
}

document.querySelectorAll('[data-view="modules"]').forEach(button =>
  button.addEventListener('click', () => setTimeout(loadModules, 0)));
const moduleTabs = byId('moduleTabs');
if (moduleTabs) {
  moduleTabs.addEventListener('click', event => {
    const more = event.target.closest('#moduleMore');
    if (more) {
      const expanded = moduleTabs.dataset.expanded === 'true';
      moduleTabs.dataset.expanded = expanded ? 'false' : 'true';
      more.setAttribute('aria-expanded', expanded ? 'false' : 'true');
      more.textContent = expanded ? '更多研究结果' : '收起';
      return;
    }
    const button = event.target.closest('button[data-module]');
    if (!button) return;
    moduleTabs.dataset.active = button.dataset.module;
    moduleTabs.querySelectorAll('button[data-module]').forEach(item => {
      item.setAttribute('aria-current', item === button ? 'page' : 'false');
    });
    renderModules();
  });
}
if (location.hash === '#modules') setTimeout(loadModules, 300);
