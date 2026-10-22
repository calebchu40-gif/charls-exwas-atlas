// The catalog contains public variable metadata. No CHARLS association results have been fitted.

const byId = id => document.getElementById(id);
const diseaseLoaded = fetch('./chronic_disease_concepts_v2.json?v=2', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`disease catalog HTTP ${r.status}`);return r.json()});
const verifiedCodesLoaded = fetch('./verified_code_examples_v1.json?v=1', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`verified codes HTTP ${r.status}`);return r.json()});
const functionalConceptsLoaded = fetch('./functional_concepts_v1.json?v=2', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`functional concepts HTTP ${r.status}`);return r.json()});
const healthWorkLimitationsLoaded = fetch('./health_work_limitations_v1.json?v=1', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`health/work limitations HTTP ${r.status}`);return r.json()});
const moodItemsLoaded = fetch('./mood_items_v1.json?v=2', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`mood items HTTP ${r.status}`);return r.json()});
const cognitionItemsLoaded = fetch('./cognition_items_v1.json?v=1', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`cognition items HTTP ${r.status}`);return r.json()});
const behaviorExposuresLoaded = fetch('./behavior_exposures_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`behavior exposures HTTP ${r.status}`);return r.json()});
const healthSymptomsLoaded = fetch('./health_symptoms_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`health symptoms HTTP ${r.status}`);return r.json()});
const foodEnvironmentLoaded = fetch('./food_environment_v1.json?v=2', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`food/environment HTTP ${r.status}`);return r.json()});
const workExposuresLoaded = fetch('./work_exposures_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`work exposures HTTP ${r.status}`);return r.json()});
const communityExposuresLoaded = fetch('./community_exposures_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`community exposures HTTP ${r.status}`);return r.json()});
const socialExposuresLoaded = fetch('./social_exposures_v1.json?v=2', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`social exposures HTTP ${r.status}`);return r.json()});
const healthcareAccessLoaded = fetch('./healthcare_access_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`healthcare access HTTP ${r.status}`);return r.json()});
const bloodBiomarkersLoaded = fetch('./blood_biomarkers_v1.json?v=3', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`blood biomarkers HTTP ${r.status}`);return r.json()});
const candidatePairExplorerLoaded = fetch('./candidate_pair_explorer_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`candidate pair explorer HTTP ${r.status}`);return r.json()});
const objectiveMeasurementsLoaded = fetch('./objective_measurements_v1.json?v=1', {cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`objective measurements HTTP ${r.status}`);return r.json()});
const lifeHistoryLoaded=fetch('./life_history_exposures_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`Life History HTTP ${r.status}`);return r.json()});
const catalogLoaded = fetch('./catalog.json?v=11', {cache:'no-store'}).then(r => {
  if (!r.ok) throw new Error(`catalog.json HTTP ${r.status}`);
  return r.json();
});

function showView(id) {
  document.querySelectorAll('.view').forEach(el => { el.hidden = el.id !== id; });
  document.querySelectorAll('.viewnav button').forEach(btn => {
    if (btn.dataset.view === id) btn.setAttribute('aria-current','page');
    else btn.removeAttribute('aria-current');
  });
}
document.querySelectorAll('.viewnav button').forEach(btn => btn.addEventListener('click', () => showView(btn.dataset.view)));
document.querySelectorAll('.overview-view [data-view]').forEach(btn => btn.addEventListener('click', () => showView(btn.dataset.view)));

function renderCandidatePairExplorer(data){
 const wave=byId('candidatePairWave').value,entry=data.waves[wave];
 const exposureInput=byId('candidateExposure'),phenotypeInput=byId('candidatePhenotype');
 const exposureList=byId('candidateExposureOptions'),phenotypeList=byId('candidatePhenotypeOptions');
 const display=x=>`${x.label} [${x.concept_id}]`;
 const fill=(list,items)=>{list.replaceChildren();for(const x of items){const o=document.createElement('option');o.value=display(x);list.append(o)}};
 fill(exposureList,entry.exposures);fill(phenotypeList,entry.phenotypes);
 const eMap=new Map(entry.exposures.map(x=>[display(x),x])),pMap=new Map(entry.phenotypes.map(x=>[display(x),x]));
 if(!eMap.has(exposureInput.value))exposureInput.value='';
 if(!pMap.has(phenotypeInput.value))phenotypeInput.value='';
 byId('candidatePairStatus').textContent=`${wave}波：${entry.exposure_count}个暴露概念 × ${entry.phenotype_count}个表型概念，形成${entry.candidate_pair_count.toLocaleString()}个不同概念的目录候选组合。该数字不是人数或分析样本量。`;
 const warning=byId('candidatePairWarning'),e=eMap.get(exposureInput.value),p=pMap.get(phenotypeInput.value);
 warning.hidden=true;warning.textContent='';
 const showFields=(container,item)=>{container.replaceChildren();if(!item){const msg=document.createElement('p');msg.textContent='请选择一个已列出的概念。';container.append(msg);return}for(const f of item.source_fields){const row=document.createElement('div');row.className='pair-field';const code=document.createElement('strong');code.textContent=f.code;row.append(code);const detail=document.createElement('span');detail.textContent=` · ${f.label||'官方标签待核'} · ${f.module||'模块待核'}${f.unit?` · 单位：${f.unit}`:''}`;row.append(detail);const note=document.createElement('div');note.textContent=[f.value_labels,f.value_semantics,f.mapping_status,f.caveat].filter(Boolean).join('；');if(note.textContent)row.append(note);container.append(row)}};
 showFields(byId('candidateExposureFields'),e);showFields(byId('candidatePhenotypeFields'),p);
 if(e&&p&&e.concept_id===p.concept_id){warning.hidden=false;warning.textContent='同一概念不能与自身配对；请选择另一个表型或暴露候选。'}
}
candidatePairExplorerLoaded.then(data=>{renderCandidatePairExplorer(data);['candidatePairWave','candidateExposure','candidatePhenotype'].forEach(id=>byId(id).addEventListener(id==='candidatePairWave'?'change':'input',()=>renderCandidatePairExplorer(data)));document.querySelector('[data-view="candidatePairExplorer"]').addEventListener('click',()=>renderCandidatePairExplorer(data))}).catch(err=>{byId('candidatePairStatus').textContent=`候选配对目录载入失败：${err.message}`});

function renderAssociations() {
  byId('rows').replaceChildren();
  byId('empty').hidden=false;
  byId('count').textContent='0 条已审查的真实关联结果';
}

function addOptions(select, values) {
  for (const value of values) {const option=document.createElement('option');option.value=value;option.textContent=select.id==='cCategory'?({'covariate candidate':'协变量候选','measurement metadata':'测量/设计元数据'}[value]||value):value;select.append(option)}
}
function renderCatalog(all, role, prefix) {
  const records=all.filter(x=>x.epcf.split(',').includes(role));
  const cats=[...new Set(records.map(x=>x.category))].sort((a,b)=>a.localeCompare(b,'zh-CN'));
  const categorySelect=byId(`${prefix}Category`);
  if(categorySelect.options.length===1)addOptions(categorySelect,cats);
  const term=byId(`${prefix}Search`).value.trim().toLocaleLowerCase();
  const cat=categorySelect.value, wave=byId(`${prefix}Wave`).value;
  const matched=records.filter(x=>{const searchable=[x['Variable.Name'],x.candidate_concept_ids,x.candidate_concept_alias_ids,x.candidate_concept_labels,x.candidate_concept_units,x['Variable.Description'],x.category,x.subcategory,x.source_modules,x.value_labels,x.harmonization_status,x.concept_mapping_caveats,x.concept_mapping_collision,x.concept_mapping_relationship].join(' ').toLocaleLowerCase();return (!term||searchable.includes(term))&&(!cat||x.category===cat)&&(!wave||x.waves.split(',').includes(wave))})
    .sort((a,b)=>String(a['Variable.Name']).localeCompare(String(b['Variable.Name']))||String(a.category).localeCompare(String(b.category)));
  const body=byId(`${prefix}Rows`); body.replaceChildren();
  for(const x of matched.slice(0,100)){
    const tr=document.createElement('tr');
    let valueStatus=x.concept_mapping_statuses?.startsWith('official questionnaire response menu reviewed; CodeBook response-category table omits questionnaire option 2')?'\u5b98\u65b9\u95ee\u5377\u83dc\u5355\u5df2\u6838\uff1bCodeBook\u7c7b\u522b\u8868\u672a\u5217\u5b63\u5ea6\u9009\u9879\uff0c\u5206\u6790\u524d\u6838\u5bf9\u83b7\u51c6\u53d1\u884c\u7248':x.value_label_review?.startsWith('official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown')?'\u5b98\u65b9\u9608\u503c\u7c7b\u522b\u5df2\u6838\uff1bCodebook\u672a\u5217\u7c7b\u522b\u4e0d\u63a8\u65ad\uff0c\u91d1\u989d\u548c\u5e8f\u5217\u4ecd\u9501\u5b9a':x.value_label_review==='conflict'?'编码标签冲突，需人工复核':x.value_label_review?.startsWith('candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data')?'官方问卷和代码本类别已核；发行数据编码、路由及适用人群/分母仍待核':x.value_label_review?.startsWith('official selector code reviewed;')?'官方格式选择器；仅用于解释后续年龄/日历年字段，不是吸烟或饮酒暴露':x.value_label_review?.startsWith('full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014')?'问卷菜单已转录；代码本字段/类别不完整，发行版编码和先前未工作路由待核':x.value_label_review?.startsWith('official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route')?'官方问卷类别；需区分多工作主要工作与单一非农工作路线':x.value_label_review?.includes('official questionnaire')&&x.value_label_review?.includes('frequencies omitted')?'官方问卷类别已核/转录；按波次题意和路由解释，未使用代码本频数':x.value_label_review?.startsWith('official selected-option label; checkbox slot')?'官方复选框选项；未选中或空白不解释为No':x.value_label_review?.startsWith('official questionnaire checkbox menu and codebook slot coding')?'官方问卷复选框选项；路由外或未选中记录不推断为No':x.value_label_review?.startsWith('official wave codebook category verified; selected option only')?'官方代码本类别已核；仅代表选中项，未选中存储码未知':x.value_label_review?.startsWith('official codebook response labels; prior-wave self-awareness/preload route retained')?'官方类别已核；自知疾病/既往波次预加载，按原问卷路由解释':x.value_label_review?.startsWith('continuous measure metadata available')?'连续测量字段；单位与测量范围见变量说明':x.value_label_review?.startsWith('continuous count measure')?'连续计数测量；保留每个15秒区间和正确/总数区别；代码本摘要不定义有效范围':x.value_label_review?.startsWith('continuous recorded response')?'连续原始作答；代码本极端值需用授权数据核验后再定范围或评分':x.value_label_review?.startsWith('numeric/time unit metadata available')?'数量或时间单位已登记；无离散值标签，详见概念交叉表':x.value_label_review?.startsWith('audited measurement component')?'客观测量组成字段；按交叉表派生概念':x.value_label_review?.startsWith('official Codebook extraction exposes only a partial response-code set')?'官方代码本仅显示部分类别；不推断缺失编码':x.value_label_review==='officially reviewed'?'官方值标签已核验':x.value_label_review&&x.value_label_review!=='not yet reviewed'?x.value_label_review:'官方值标签待逐项核验';
    if (x.value_label_review?.startsWith('DO NOT ANALYZE; questionnaire:')) valueStatus='⚠ 问卷与Codebook编码冲突，已锁定不可分析；'+x.value_label_review;
    const relationStratified=x.concept_mapping_relationship?.startsWith('relationship_stratified_parent_record_measure:');
    const candidateStatus=x['Candidate.Status']||'C类来源/测量元数据';
    const conceptDisplay=role==='c'?(candidateStatus==='automated discovery; questionnaire/codebook review required'?'自动发现候选；官方问卷/代码本尚待核验':candidateStatus):[x.candidate_concept_ids||'待归属稳定概念',x.candidate_concept_alias_ids?`别名：${x.candidate_concept_alias_ids}`:'',x.concept_mapping_collision&&!relationStratified?'⚠ 构念重叠待按关系审查':'',x['Review.Flag']?.includes('DO NOT ANALYZE')?'\u26a0 DO NOT ANALYZE':''].filter(Boolean).join('；');
    const metadataNote=role==='c'?(x.concept_mapping_caveats||x['Review.Flag']||'请回查来源问卷/代码本'):'';
    const metadataReview=x.value_label_review?.startsWith('official selector code reviewed;')?valueStatus:x['Value.Label.Review']==='not yet reviewed'?'官方值标签/编码尚未逐项核验；连续变量可能没有离散类别标签':x['Value.Label.Review']==='officially reviewed'?'官方值标签已核验':x['Value.Label.Review'];
    const metadataSemantics=role==='c'?([x.value_labels,metadataReview].filter(Boolean).join('；')||'测量/设计元数据'):'';
    const harmonizationNote=x.harmonization_status?.startsWith('continuous internal biomarker/clinical or physical measure')?'内部生理/临床测量，属于表型候选，不是外源环境暴露；跨波尚未统一':'';
    const labelDisplay=role==='c'?metadataSemantics:[x.value_labels||valueStatus,x.value_labels&&valueStatus!=='官方值标签已核验'?valueStatus:'',harmonizationNote].filter(Boolean).join('；');
    const categoryDisplay=role==='c'?({'covariate candidate':'协变量候选','measurement metadata':'测量/设计元数据'}[x.category]||x.category):x.category;
    const displayValues=[x['Variable.Name'],conceptDisplay,categoryDisplay+' · '+x.subcategory,x['Variable.Description'],x.waves,x.source_modules,role==='c'?metadataNote:(x.candidate_concept_units||'未登记单位/分类构成'),labelDisplay];
    for(const [i,value] of displayValues.entries()){
      const td=document.createElement('td');td.textContent=value;tr.append(td)
      if(i===1)td.title=role==='c'?'C类角色判定：'+(x['Candidate.Status']||'来源/测量元数据')+'；处理边界：'+(x['Harmonization.Status']||'不进入E/P关联矩阵')+'；审核：'+(x['Review.Flag']||'回查对应波次的官方问卷/代码本')+'；官方来源：'+(x['Value.Label.Source']||'见项目官方来源清单'):'候选概念：'+(x.candidate_concept_labels||'待核')+'；原始别名ID：'+(x.candidate_concept_alias_ids||'无')+'；关系：'+(x.concept_mapping_relationship||'无额外重叠')+'；映射状态：'+(x.concept_mapping_statuses||'待核')+'；解释与路由：'+(x.concept_mapping_caveats||'未登记')+'；来源表：'+(x.concept_mapping_sources||'待核')
      if(i===6&&x.concept_mapping_sources)td.title='单位来源：'+x.concept_mapping_sources
      if(i===7&&x.value_label_source)td.title='答案标签来源：'+x.value_label_source
    }
    body.append(tr);
  }
  byId(`${prefix}Count`).textContent=`筛选命中 ${matched.length.toLocaleString()} 条逐波字段—类别记录；当前展示 ${Math.min(100,matched.length)} 条。此数不是最终指标数。`;
}

function renderGroups(all) {
  const exposures=all.filter(x=>x.epcf.split(',').includes('e'));
  const grouped=new Map();
  for(const x of exposures){const k=x.category;grouped.set(k,(grouped.get(k)||0)+1)}
  const grid=byId('groupGrid');grid.replaceChildren();
  for(const [category,n] of [...grouped].sort((a,b)=>a[0].localeCompare(b[0],'zh-CN'))){
    const card=document.createElement('div');card.className='group-card';
    const title=document.createElement('b');title.textContent=category;
    const count=document.createElement('span');count.textContent=`${n.toLocaleString()} 条宽口径候选编码—类别记录（不是已确认暴露指标）`;
    card.append(title,count);grid.append(card);
  }
}
function renderBrowseCards(containerId,role){
  const root=byId(containerId);root.replaceChildren();
  const card=document.createElement('div');card.className='group-card';
  const title=document.createElement('b');title.textContent='真实关联结果尚未生成';
  const meta=document.createElement('span');meta.textContent='当前目录记录的是CHARLS字段、波次、答案编码和候选概念。完成分析资格、调查设计和统计审查后，才会接入关联结果。';
  const btn=document.createElement('button');btn.type='button';btn.className='clear';btn.style.marginTop='12px';btn.textContent=role==='p'?'查看表型候选目录':'查看暴露候选目录';
  btn.addEventListener('click',()=>showView(role==='p'?'phenotypes':'exposures'));
  card.append(title,meta,btn);root.append(card);
}

catalogLoaded.then(all=>{
  renderCatalog(all,'e','e');renderCatalog(all,'p','p');renderCatalog(all,'c','c');renderGroups(all);
  ['eSearch','eCategory','eWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCatalog(all,'e','e')));
  ['pSearch','pCategory','pWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCatalog(all,'p','p')));
  ['cSearch','cCategory','cWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCatalog(all,'c','c')));
  document.querySelector('[data-view="exposures"]').addEventListener('click',()=>renderCatalog(all,'e','e'));
  document.querySelector('[data-view="phenotypes"]').addEventListener('click',()=>renderCatalog(all,'p','p'));
  document.querySelector('[data-view="metadata"]').addEventListener('click',()=>renderCatalog(all,'c','c'));
  renderBrowseCards('phenotypeBrowse','p');renderBrowseCards('exposureBrowse','e');
}).catch(err=>{
  for(const id of ['eCount','pCount'])byId(id).textContent=`候选目录载入失败：${err.message}`;
});
renderAssociations();


function renderDiseaseConcepts(items){
 const term=byId('diseaseSearch').value.trim().toLocaleLowerCase(), wave=byId('diseaseWave').value;
 const shown=items.filter(x=>{const fields=x.source_fields.filter(f=>!wave||f.wave===wave);return (!wave||fields.length>0)&&(!term||`${x.concept_id} ${x.label} ${x.label_en} ${fields.map(f=>f.code).join(' ')}`.toLocaleLowerCase().includes(term))}).sort((a,b)=>String(a.legacy_index||99).localeCompare(String(b.legacy_index||99),undefined,{numeric:true}));
 const body=byId('diseaseRows');body.replaceChildren();
 for(const x of shown){const tr=document.createElement('tr');const fields=x.source_fields.filter(f=>!wave||f.wave===wave);const values=[...new Set(fields.map(f=>`${f.role}: ${f.value_labels||'待核'}`))].join('；');for(const v of [x.concept_id,x.label,x.legacy_index||'未单列',x.wave2020_index,fields.map(f=>`${f.wave}: ${f.code} (${f.role})`).join(' · ')||'当前波次未匹配源字段',values||'当前波次暂无字段',x.caveat||x.status]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('diseaseCount').textContent=`当前显示 ${shown.length} / ${items.length} 个疾病概念；源字段映射不是最终分析状态定义。`;
}
diseaseLoaded.then(items=>{renderDiseaseConcepts(items);['diseaseSearch','diseaseWave'].forEach(id=>byId(id).addEventListener('input',()=>renderDiseaseConcepts(items)));document.querySelector('[data-view="chronicConcepts"]').addEventListener('click',()=>renderDiseaseConcepts(items))}).catch(err=>{byId('diseaseCount').textContent=`慢病概念目录载入失败：${err.message}`});

function renderVerifiedCodes(items){
 const term=byId('codeSearch').value.trim().toLocaleLowerCase(), wave=byId('codeWave').value;
 const shown=items.filter(x=>(!wave||x.waves.split(',').includes(wave))&&(!term||`${x.code} ${x.concept} ${x.source_labels} ${x.modules}`.toLocaleLowerCase().includes(term)));
 const body=byId('codeRows');body.replaceChildren();
 for(const x of shown){const tr=document.createElement('tr');for(const v of [x.code,x.concept,x.waves,x.modules,x.source_labels,`${x.mapping_status}；${x.note}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('codeCount').textContent=`筛选命中 ${shown.length} 条源字段映射；按指标名、CHARLS编码或官方标签检索。`;
}
verifiedCodesLoaded.then(items=>{renderVerifiedCodes(items);['codeSearch','codeWave'].forEach(id=>byId(id).addEventListener('input',()=>renderVerifiedCodes(items)));document.querySelector('[data-view="verifiedCodes"]').addEventListener('click',()=>renderVerifiedCodes(items))}).catch(err=>{byId('codeCount').textContent=`官方编码目录载入失败：${err.message}`});

function renderFunctionalConcepts(items){
 const term=byId('functionSearch').value.trim().toLocaleLowerCase(),wave=byId('functionWave').value;
 const matches=[];
 for(const concept of items){for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}}
 const body=byId('functionRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.source_label,[field.value_labels,field.value_label_status,field.value_label_source,field.note||concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('functionCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个候选概念；不是最终指标数。`;
}
functionalConceptsLoaded.then(items=>{renderFunctionalConcepts(items);['functionSearch','functionWave'].forEach(id=>byId(id).addEventListener('input',()=>renderFunctionalConcepts(items)));document.querySelector('[data-view="functionalConcepts"]').addEventListener('click',()=>renderFunctionalConcepts(items))}).catch(err=>{byId('functionCount').textContent=`功能概念目录载入失败：${err.message}`});

function renderMoodItems(items){
 const term=byId('moodSearch').value.trim().toLocaleLowerCase(),wave=byId('moodWave').value,matches=[];
 for(const concept of items){for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.module}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}}
 const body=byId('moodRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.code,field.wave,field.module,field.source_label,[field.value_labels,field.value_label_status,field.value_label_source,field.note||concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('moodCount').textContent=`筛选命中 ${matches.length} 条条目—波次候选映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个概念；未计算量表总分。`;
}
moodItemsLoaded.then(items=>{renderMoodItems(items);['moodSearch','moodWave'].forEach(id=>byId(id).addEventListener('input',()=>renderMoodItems(items)));document.querySelector('[data-view="moodConcepts"]').addEventListener('click',()=>renderMoodItems(items))}).catch(err=>{byId('moodCount').textContent=`情绪条目目录载入失败：${err.message}`});

function renderCognitionItems(items){
 const term=byId('cognitionSearch').value.trim().toLocaleLowerCase(),wave=byId('cognitionWave').value,matches=[];
 for(const concept of items){for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.module} ${field.value_labels||''} ${field.value_semantics||''}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}}
 const body=byId('cognitionRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label||'本地代码本未提供字段标签',[field.value_labels,field.value_semantics,field.value_label_status,field.value_label_source,field.questionnaire_source,field.note,concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 const labeled=matches.filter(x=>Boolean(x.field.value_labels)).length;
 byId('cognitionCount').textContent=`筛选命中 ${matches.length} 条问卷语义—字段映射，其中 ${labeled} 条显示官方值类别或连续作答语义；涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个认知概念，未计算认知量表总分。`;
}
cognitionItemsLoaded.then(items=>{renderCognitionItems(items);['cognitionSearch','cognitionWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCognitionItems(items)));document.querySelector('[data-view="cognitionConcepts"]').addEventListener('click',()=>renderCognitionItems(items))}).catch(err=>{byId('cognitionCount').textContent=`认知目录载入失败：${err.message}`});

function renderBehaviorExposures(items){
 const term=byId('behaviorSearch').value.trim().toLocaleLowerCase(),wave=byId('behaviorWave').value,matches=[];
 for(const concept of items){for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_semantics||''} ${field.questionnaire_source||''}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}}
 const body=byId('behaviorRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,[field.value_labels,field.value_semantics,field.value_label_status,field.questionnaire_source,field.value_label_source,field.note||concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('behaviorCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个行为暴露概念；字段数不等于独立暴露指标数。`;
}
behaviorExposuresLoaded.then(items=>{renderBehaviorExposures(items);['behaviorSearch','behaviorWave'].forEach(id=>byId(id).addEventListener('input',()=>renderBehaviorExposures(items)));document.querySelector('[data-view="behaviorExposures"]').addEventListener('click',()=>renderBehaviorExposures(items))}).catch(err=>{byId('behaviorCount').textContent=`行为暴露目录载入失败：${err.message}`});

function renderHealthSymptoms(items){
 const term=byId('symptomSearch').value.trim().toLocaleLowerCase(),wave=byId('symptomWave').value,matches=[];
 for(const concept of items){for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_semantics||''} ${field.questionnaire_source||''}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}}
 const body=byId('symptomRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,[field.value_labels,field.value_label_status,field.value_label_source,field.note||concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('symptomCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个健康/症状表型概念；拆分身体部位字段不等于独立结局。`;
}
healthSymptomsLoaded.then(items=>{renderHealthSymptoms(items);['symptomSearch','symptomWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHealthSymptoms(items)));document.querySelector('[data-view="healthSymptoms"]').addEventListener('click',()=>renderHealthSymptoms(items))}).catch(err=>{byId('symptomCount').textContent=`健康症状目录载入失败：${err.message}`});

function renderFoodEnvironment(items){
 const term=byId('foodEnvSearch').value.trim().toLocaleLowerCase(),wave=byId('foodEnvWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_labels} ${field.value_semantics} ${field.value_label_status} ${field.unit||''} ${field.source_evidence||''} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('foodEnvRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,field.value_labels||'值标签待核',concept.caveat]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('foodEnvCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个概念；字段映射数不是独立指标数。`;
}
foodEnvironmentLoaded.then(items=>{renderFoodEnvironment(items);['foodEnvSearch','foodEnvWave'].forEach(id=>byId(id).addEventListener('input',()=>renderFoodEnvironment(items)));document.querySelector('[data-view="foodEnvironment"]').addEventListener('click',()=>renderFoodEnvironment(items))}).catch(err=>{byId('foodEnvCount').textContent=`饮食/环境目录载入失败：${err.message}`});

function renderWorkExposures(items){
 const term=byId('workSearch').value.trim().toLocaleLowerCase(),wave=byId('workWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.unit||''} ${field.value_labels} ${field.value_label_status} ${field.mapping_status||''} ${field.source_document||''} ${field.note} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('workRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,field.unit||'—',field.value_labels||field.value_label_status,`${field.mapping_status||''}；${field.source_document||field.value_label_source||'来源待定位'}；${field.value_label_status}；${field.note}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 const labeled=matches.filter(x=>Boolean(x.field.value_labels)).length;
 byId('workCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个概念；${labeled} 条显示代码本类别/选项标签。频数已排除；多选槽位未选不等于“否”。`;
}
workExposuresLoaded.then(items=>{renderWorkExposures(items);['workSearch','workWave'].forEach(id=>byId(id).addEventListener('input',()=>renderWorkExposures(items)));document.querySelector('[data-view="workExposures"]').addEventListener('click',()=>renderWorkExposures(items))}).catch(err=>{byId('workCount').textContent=`工作暴露目录载入失败：${err.message}`});

function renderCommunityExposures(items){
 const term=byId('communitySearch').value.trim().toLocaleLowerCase(),wave=byId('communityWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_labels} ${field.value_label_status} ${field.unit||''} ${field.source_evidence||''} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('communityRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,field.unit||'—',field.value_labels||field.value_label_status,`${field.value_label_source||'来源待定位'}；${field.source_evidence||'问卷/代码本来源待定位'}；${field.value_label_status}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 const labeled=matches.filter(x=>Boolean(x.field.value_labels)).length;
 byId('communityCount').textContent=`筛选命中 ${matches.length} 条问卷字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个社区层概念；其中 ${labeled} 条显示代码本类别标签，全部为2011年。`;
}
communityExposuresLoaded.then(items=>{renderCommunityExposures(items);['communitySearch','communityWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCommunityExposures(items)));document.querySelector('[data-view="communityExposures"]').addEventListener('click',()=>renderCommunityExposures(items))}).catch(err=>{byId('communityCount').textContent=`社区环境目录载入失败：${err.message}`});

function renderSocialExposures(items){
 const term=byId('socialSearch').value.trim().toLocaleLowerCase(),wave=byId('socialWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_labels||''} ${field.value_semantics||''} ${field.questionnaire_source||''} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('socialRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,[field.value_labels?`官方值标签：${field.value_labels}`:'',field.note,field.value_semantics,field.questionnaire_source,field.value_label_source,concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('socialCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个社会关系候选概念；家庭成员索引字段不是独立概念数。`;
}
socialExposuresLoaded.then(items=>{renderSocialExposures(items);['socialSearch','socialWave'].forEach(id=>byId(id).addEventListener('input',()=>renderSocialExposures(items)));document.querySelector('[data-view="socialExposures"]').addEventListener('click',()=>renderSocialExposures(items))}).catch(err=>{byId('socialCount').textContent=`社交/家庭联系目录载入失败：${err.message}`});

function renderHealthcareAccess(items){
 const term=byId('healthcareSearch').value.trim().toLocaleLowerCase(),wave=byId('healthcareWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('healthcareRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,`${field.value_labels?`官方值标签：${field.value_labels}；`:''}${field.value_label_status||'值标签审查状态待核'}；${field.value_semantics||'值语义待逐波核实'}；来源：${field.value_label_source||'代码本来源待定位'}；${field.questionnaire_reference||'题目页码待核'}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('healthcareCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个医保、医疗利用与费用候选概念组；字段行数不是独立结局/暴露数。`;
}
healthcareAccessLoaded.then(items=>{renderHealthcareAccess(items);['healthcareSearch','healthcareWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHealthcareAccess(items)));document.querySelector('[data-view="healthcareAccess"]').addEventListener('click',()=>renderHealthcareAccess(items))}).catch(err=>{byId('healthcareCount').textContent=`医保、医疗利用与费用目录载入失败：${err.message}`});

function renderBloodBiomarkers(items){
 const term=byId('bloodSearch').value.trim().toLocaleLowerCase(),wave=byId('bloodWave').value;
 const matches=items.filter(x=>(!wave||x.wave===wave)&&(!term||`${x.concept_id} ${x.concept_label} ${x.domain} ${x.variable} ${x.module} ${x.value_semantics} ${x.cross_wave_comparability||''} ${x.role_boundary||''} ${x.source_status} ${x.assay_method||''} ${x.assay_metadata_status||''} ${x.assay_metadata_source||''}`.toLocaleLowerCase().includes(term)));
 const body=byId('bloodRows');body.replaceChildren();
 for(const x of matches){const assay=[x.assay_method&&`方法：${x.assay_method}`,x.within_assay_cv&&`批内CV：${x.within_assay_cv}`,x.between_assay_cv&&`批间CV：${x.between_assay_cv}`,x.guide_reported_detection_range&&`指南所列检测范围：${x.guide_reported_detection_range}`,x.assay_metadata_status,`来源：${x.assay_metadata_source||'未提供'}`].filter(Boolean).join('；');const tr=document.createElement('tr');for(const v of [x.concept_id,x.concept_label,x.domain,x.variable,x.wave,x.module,x.unit,`${x.value_semantics} ${x.collection_scope} ${x.cross_wave_comparability||''} ${x.role_boundary||''}`,`${x.weight_field}；${x.source_status}`,assay,x.source_unit_text||x.unit]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('bloodCount').textContent=`筛选命中 ${matches.length} 条波次—字段映射，覆盖 ${new Set(matches.filter(x=>x.concept_id!=='blood_collection_metadata').map(x=>x.concept_id)).size} 个实验室分析物概念；波次字段行数不等于独立指标数。`;
}
bloodBiomarkersLoaded.then(items=>{renderBloodBiomarkers(items);['bloodSearch','bloodWave'].forEach(id=>byId(id).addEventListener('input',()=>renderBloodBiomarkers(items)));document.querySelector('[data-view="bloodBiomarkers"]').addEventListener('click',()=>renderBloodBiomarkers(items))}).catch(err=>{byId('bloodCount').textContent=`血液生物标志物目录载入失败：${err.message}`});

function renderObjectiveMeasurements(items){
 const term=byId('objectiveSearch').value.trim().toLocaleLowerCase(),wave=byId('objectiveWave').value;
 const matches=items.filter(x=>(!wave||x.wave===wave)&&(!term||`${x.concept_id} ${x.concept_label} ${x.domain} ${x.variables} ${x.module} ${x.value_semantics}`.toLocaleLowerCase().includes(term)));
 const body=byId('objectiveRows');body.replaceChildren();
 for(const x of matches){const tr=document.createElement('tr');for(const v of [x.concept_id,x.concept_label,x.domain,x.variables,x.wave,x.module,x.value_semantics,x.source_status]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('objectiveCount').textContent=`筛选命中 ${matches.length} 条波次—概念映射，涉及 ${new Set(matches.map(x=>x.concept_id)).size} 个候选测量概念；同一概念下多个读数不是多个指标。`;
}
objectiveMeasurementsLoaded.then(items=>{renderObjectiveMeasurements(items);['objectiveSearch','objectiveWave'].forEach(id=>byId(id).addEventListener('input',()=>renderObjectiveMeasurements(items)));document.querySelector('[data-view="objectiveMeasures"]').addEventListener('click',()=>renderObjectiveMeasurements(items))}).catch(err=>{byId('objectiveCount').textContent=`客观测量目录载入失败：${err.message}`});


const disabilityHistoryLoaded=fetch('./disability_history_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`disability history HTTP ${r.status}`);return r.json()});
function renderDisabilityHistory(items){
 const term=byId('disabilitySearch').value.trim().toLocaleLowerCase(),wave=byId('disabilityWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.label_en} ${field.code} ${field.field_role} ${field.source_label} ${field.value_labels} ${field.value_label_status} ${field.caveat} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('disabilityRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,`${concept.label} (${concept.label_en})`,field.wave,field.code,field.field_role,field.source_label,`${field.value_labels||field.value_label_status}；${field.value_label_source}；${field.caveat||concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('disabilityCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 类残疾史；字段数不等于独立结局数。`;
}
disabilityHistoryLoaded.then(items=>{renderDisabilityHistory(items);['disabilitySearch','disabilityWave'].forEach(id=>byId(id).addEventListener('input',()=>renderDisabilityHistory(items)));document.querySelector('[data-view="disabilityHistory"]').addEventListener('click',()=>renderDisabilityHistory(items))}).catch(err=>{byId('disabilityCount').textContent=`残疾史目录载入失败：${err.message}`});

const cancerSitesLoaded=fetch('./cancer_sites_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`cancer sites HTTP ${r.status}`);return r.json()});
function renderCancerSites(items){
 const term=byId('cancerSearch').value.trim().toLocaleLowerCase(),wave=byId('cancerWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.site} ${field.code} ${field.source_label} ${field.value_labels} ${field.module} ${field.value_label_source} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('cancerRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.site,field.wave,field.code,field.source_label,field.value_labels||'该字段未观察到可核实的部位选项标签',`${field.value_label_status}；来源：${field.value_label_source}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('cancerCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个癌症部位概念；标签中不含频数。`;
}
cancerSitesLoaded.then(items=>{renderCancerSites(items);['cancerSearch','cancerWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCancerSites(items)));document.querySelector('[data-view="cancerSites"]').addEventListener('click',()=>renderCancerSites(items))}).catch(err=>{byId('cancerCount').textContent=`癌症部位目录载入失败：${err.message}`});

const housingCatalogLoaded=fetch('./housing_catalog_v1.json?v=2',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`housing catalog HTTP ${r.status}`);return r.json()});
function renderHousingCatalog(items){
 const term=byId('housingSearch').value.trim().toLocaleLowerCase(),wave=byId('housingWave').value;
 const matches=items.filter(x=>(!wave||x.wave===wave)&&(!term||`${x.concept_id} ${x.concept_label} ${x.code} ${x.source_label} ${x.module} ${x.unit||''} ${x.value_labels} ${x.caveat}`.toLocaleLowerCase().includes(term)));
 const body=byId('housingRows');body.replaceChildren();
 for(const x of matches.slice(0,150)){const tr=document.createElement('tr');for(const v of [x.code,x.concept_label,x.wave,x.module,x.source_label,x.unit||"—",x.value_labels||x.value_label_status,x.caveat]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('housingCount').textContent=`筛选命中 ${matches.length} 条波次—字段映射，当前展示 ${Math.min(matches.length,150)} 条，涉及 ${new Set(matches.map(x=>x.concept_id)).size} 个候选概念；值码只在对应波次解释。`;
}
housingCatalogLoaded.then(items=>{renderHousingCatalog(items);['housingSearch','housingWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHousingCatalog(items)));document.querySelector('[data-view="housingCatalog"]').addEventListener('click',()=>renderHousingCatalog(items))}).catch(err=>{byId('housingCount').textContent=`住房编码目录载入失败：${err.message}`});

const householdRentalIncomeLoaded=fetch('./household_other_asset_rental_income_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`household rental income HTTP ${r.status}`);return r.json()});
function renderHouseholdRentalIncome(items){
 const term=byId('rentalIncomeSearch').value.trim().toLocaleLowerCase(),wave=byId('rentalIncomeWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.value_labels} ${field.unit} ${field.mapping_status} ${field.source_document} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('rentalIncomeRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.wave,field.code,field.module,field.source_label,field.value_labels||field.unit,`${field.mapping_status}；${field.source_document}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v||'—';tr.append(td)}body.append(tr)}
 byId('rentalIncomeCount').textContent=`筛选命中 ${matches.length} 条波次—字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个候选概念；不代表有效样本数或可直接合并的指标。`;
}
householdRentalIncomeLoaded.then(items=>{renderHouseholdRentalIncome(items);['rentalIncomeSearch','rentalIncomeWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHouseholdRentalIncome(items)));document.querySelector('[data-view="householdRentalIncome"]').addEventListener('click',()=>renderHouseholdRentalIncome(items))}).catch(err=>{byId('rentalIncomeCount').textContent=`家庭资产租赁收入目录载入失败：${err.message}`});

const householdCovidEconomicsLoaded=fetch('./household_covid_economic_v1.json?v=1',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`household COVID economics HTTP ${r.status}`);return r.json()});
function renderHouseholdCovidEconomics(items){
 const term=byId('covidEconomicSearch').value.trim().toLocaleLowerCase(),wave=byId('covidEconomicWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.value_labels} ${field.unit} ${field.mapping_status} ${field.source_document} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('covidEconomicRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.wave,field.code,field.module,field.source_label,field.value_labels||field.unit,`${field.mapping_status}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v||'—';tr.append(td)}body.append(tr)}
 byId('covidEconomicCount').textContent=`筛选命中 ${matches.length} 条源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个候选概念；不代表有效样本数、跨波可比指标或正式关联结果。`;
}
householdCovidEconomicsLoaded.then(items=>{renderHouseholdCovidEconomics(items);['covidEconomicSearch','covidEconomicWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHouseholdCovidEconomics(items)));document.querySelector('[data-view="householdCovidEconomics"]').addEventListener('click',()=>renderHouseholdCovidEconomics(items))}).catch(err=>{byId('covidEconomicCount').textContent=`疫情期间家庭经济目录载入失败：${err.message}`});

function renderHealthWorkLimitations(items){
 const term=byId('workLimitSearch').value.trim().toLocaleLowerCase(),wave=byId('workLimitWave').value;
 const matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.value_labels} ${field.note}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('workLimitRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.code,field.wave,field.source_label,field.value_labels,`${field.value_semantics}；${field.note}；来源：${field.value_label_source}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('workLimitCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个候选概念；不是最终指标数。`;
}
healthWorkLimitationsLoaded.then(items=>{renderHealthWorkLimitations(items);['workLimitSearch','workLimitWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHealthWorkLimitations(items)));document.querySelector('[data-view="healthWorkLimitations"]').addEventListener('click',()=>renderHealthWorkLimitations(items))}).catch(err=>{byId('workLimitCount').textContent=`健康相关工作/家务目录载入失败：${err.message}`});

function renderLifeHistory(items){
 const q=byId('lifeHistorySearch').value.trim().toLowerCase(), role=byId('lifeHistoryRole').value, body=byId('lifeHistoryRows'); body.replaceChildren();
 const filtered=items.filter(g=>(!role||g.role===role)&&(!q||[g.concept_id,g.label,g.domain,g.question,g.unit,g.values,g.caveat,...g.source_fields.flatMap(x=>[x.code,x.module,x.codebook_label])].join(' ').toLowerCase().includes(q)));
 let n=0; for(const g of filtered) for(const x of g.source_fields){n++;const tr=document.createElement('tr');const cells=[g.concept_id,g.label,g.role.toUpperCase(),g.domain,x.code+' · 2014',x.module+' / '+x.codebook_label,g.question,g.unit+'; '+g.values,g.caveat];for(const value of cells){const td=document.createElement('td');td.textContent=value;tr.append(td)}body.append(tr)}
 byId('lifeHistoryCount').textContent=`显示 ${n} 条字段映射，涉及 ${filtered.length} 个概念组；字段行数不等于独立暴露数量。`;
}
lifeHistoryLoaded.then(items=>{renderLifeHistory(items);['lifeHistorySearch','lifeHistoryRole'].forEach(id=>byId(id).addEventListener('input',()=>renderLifeHistory(items)));document.querySelector('[data-view="lifeHistoryExposures"]').addEventListener('click',()=>renderLifeHistory(items))}).catch(err=>{byId('lifeHistoryCount').textContent=`生命历程候选目录载入失败：${err.message}`});
