// Special analyses: fuel gradient, jointly adjusted household model and effect
// modification. Each tab renders one aggregate JSON produced overnight.

const moduleData = { gradient: null, joint: null, interaction: null, health: null, solid: null };

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
    const [gradient, joint, interaction, health, solid] = await Promise.all([
      fetch('./fuel_gradient_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./joint_household_model_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./effect_modification_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./health_index_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
      fetch('./solid_fuel_blood_v1.json?v=1', { cache: 'no-cache' }).then(r => r.json()),
    ]);
    moduleData.gradient = gradient;
    moduleData.joint = joint;
    moduleData.interaction = interaction;
    moduleData.health = health;
    moduleData.solid = solid;
    renderModules();
  } catch (error) {
    byId('moduleBody').textContent = `专项分析载入失败：${error.message}`;
  }
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
    byId('moduleNote').textContent = '健康指数 = 收缩压、BMI、连续减 7、自评健康、自评记忆 五项 z 分均值（0–100）；n=10,071。';
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
    const button = event.target.closest('button[data-module]');
    if (!button) return;
    moduleTabs.dataset.active = button.dataset.module;
    moduleTabs.querySelectorAll('button').forEach(item => {
      item.setAttribute('aria-current', item === button ? 'page' : 'false');
    });
    renderModules();
  });
}
if (location.hash === '#modules') setTimeout(loadModules, 300);
