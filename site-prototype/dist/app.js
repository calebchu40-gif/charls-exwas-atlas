// The catalog contains public variable metadata. No CHARLS association results have been fitted.

const byId = id => document.getElementById(id);
const deferredViewLoaders = new Map();
function deferJson(url, viewId) {
  let resolveData, rejectData;
  const promise = new Promise((resolve, reject) => { resolveData = resolve; rejectData = reject; });
  let started = false;
  deferredViewLoaders.set(viewId, () => {
    if (started) return;
    started = true;
    const statusIds = {chronicConcepts:'diseaseCount',verifiedCodes:'codeCount',functionalConcepts:'functionCount',healthWorkLimitations:'workLimitCount',moodConcepts:'moodCount',cognitionConcepts:'cognitionCount',behaviorExposures:'behaviorCount',healthSymptoms:'symptomCount',foodEnvironment:'foodEnvCount',workExposures:'workCount',communityExposures:'communityCount',socialExposures:'socialCount',healthcareAccess:'healthcareCount',bloodBiomarkers:'bloodCount',objectiveMeasures:'objectiveCount',lifeHistoryExposures:'lifeHistoryCount',disabilityHistory:'disabilityCount',cancerSites:'cancerCount',housingCatalog:'housingCount',householdRentalIncome:'rentalIncomeCount',householdCovidEconomics:'covidEconomicCount'};
    const status = statusIds[viewId] && byId(statusIds[viewId]);
    if (status) status.textContent = '正在载入目录…';
    fetch(url, {cache:'no-cache'}).then(response => {
      if (!response.ok) throw new Error(`${url} HTTP ${response.status}`);
      return response.json();
    }).then(resolveData, rejectData);
  });
  return promise;
}

const diseaseLoaded=deferJson('./chronic_disease_concepts_v2.json?v=2','chronicConcepts');
const verifiedCodesLoaded=deferJson('./verified_code_examples_v1.json?v=1','verifiedCodes');
const functionalConceptsLoaded=deferJson('./functional_concepts_v1.json?v=2','functionalConcepts');
const healthWorkLimitationsLoaded=deferJson('./health_work_limitations_v1.json?v=1','healthWorkLimitations');
const moodItemsLoaded=deferJson('./mood_items_v1.json?v=2','moodConcepts');
const cognitionItemsLoaded=deferJson('./cognition_items_v1.json?v=2','cognitionConcepts');
const behaviorExposuresLoaded=deferJson('./behavior_exposures_v1.json?v=4','behaviorExposures');
const healthSymptomsLoaded=deferJson('./health_symptoms_v1.json?v=3','healthSymptoms');
const foodEnvironmentLoaded=deferJson('./food_environment_v1.json?v=4','foodEnvironment');
const workExposuresLoaded=deferJson('./work_exposures_v1.json?v=3','workExposures');
const communityExposuresLoaded=deferJson('./community_exposures_v1.json?v=4','communityExposures');
const socialExposuresLoaded=deferJson('./social_exposures_v1.json?v=4','socialExposures');
const healthcareAccessLoaded=deferJson('./healthcare_access_v1.json?v=3','healthcareAccess');
const bloodBiomarkersLoaded=deferJson('./blood_biomarkers_v1.json?v=3','bloodBiomarkers');
let candidatePairExplorerLoaded;
const objectiveMeasurementsLoaded=deferJson('./objective_measurements_v1.json?v=4','objectiveMeasures');
const lifeHistoryLoaded=deferJson('./life_history_exposures_v1.json?v=1','lifeHistoryExposures');
const catalogLoaded = {};

function showView(id) {
  document.querySelectorAll('.view').forEach(el => { el.hidden = el.id !== id; });
  document.querySelectorAll('.viewnav button').forEach(btn => {
    if (btn.dataset.view === id) btn.setAttribute('aria-current','page');
    else btn.removeAttribute('aria-current');
  });
  deferredViewLoaders.get(id)?.();
  if (id === 'exposures' || id === 'groups') loadCatalog('e');
  if (id === 'phenotypes') loadCatalog('p');
  if (id === 'metadata') loadCatalog('c');
  if (id === 'candidatePairExplorer') loadCandidatePairExplorer();
}
document.querySelectorAll('.viewnav button').forEach(btn => btn.addEventListener('click', () => showView(btn.dataset.view)));
document.querySelectorAll('.overview-view [data-view]').forEach(btn => btn.addEventListener('click', () => showView(btn.dataset.view)));

function renderCandidatePairExplorer(data){
 const design=byId('candidatePairDesign').value;
 const wave=byId('candidatePairWave').value;
 const longitudinal=design==='baseline-community';
 const entry=longitudinal?data.baseline_community_to_followup[wave]:data.waves[wave];
 const exposureItems=longitudinal?data.baseline_community_exposures:entry.exposures;
 const phenotypeItems=longitudinal?data.waves[wave].phenotypes.filter(x=>entry.phenotype_concept_ids.includes(x.concept_id)):entry.phenotypes;
 const exposureInput=byId('candidateExposure'),phenotypeInput=byId('candidatePhenotype');
 const exposureList=byId('candidateExposureOptions'),phenotypeList=byId('candidatePhenotypeOptions');
 const display=x=>`${x.label} [${x.concept_id}]`;
 const fill=(list,items)=>{list.replaceChildren();for(const x of items){const o=document.createElement('option');o.value=display(x);list.append(o)}};
 fill(exposureList,exposureItems);fill(phenotypeList,phenotypeItems);
 const eMap=new Map(exposureItems.map(x=>[display(x),x])),pMap=new Map(phenotypeItems.map(x=>[display(x),x]));
 if(!eMap.has(exposureInput.value))exposureInput.value='';
 if(!pMap.has(phenotypeInput.value))phenotypeInput.value='';
 byId('candidateExposureHeading').textContent=longitudinal?'2011基线社区暴露源字段':'暴露源字段';
 byId('candidatePhenotypeHeading').textContent=longitudinal?`${wave}随访表型源字段`:'表型源字段';
 byId('candidatePairStatus').textContent=longitudinal?`2011基线社区：${entry.exposure_count}个暴露概念 × ${entry.followup_wave}波：${entry.phenotype_count}个表型概念，形成${entry.candidate_pair_count.toLocaleString()}个目录候选组合。官方指南说明社区ID可与前序波次对应，但此处没有匹配任何个体记录。`: `${wave}波：${entry.exposure_count}个暴露概念 × ${entry.phenotype_count}个表型概念，形成${entry.candidate_pair_count.toLocaleString()}个不同概念的目录候选组合。该数字不是人数或分析样本量。`;
 byId('candidatePairLongitudinalNote').hidden=!longitudinal;
 const warning=byId('candidatePairWarning'),e=eMap.get(exposureInput.value),p=pMap.get(phenotypeInput.value);
 warning.hidden=true;warning.textContent='';
 const showFields=(container,item)=>{container.replaceChildren();if(!item){const msg=document.createElement('p');msg.textContent='请选择一个已列出的概念。';container.append(msg);return}for(const f of item.source_fields){const row=document.createElement('div');row.className='pair-field';const code=document.createElement('strong');code.textContent=f.code;row.append(code);const detail=document.createElement('span');detail.textContent=` · ${f.label||'官方标签待核'} · ${f.module||'模块待核'}${f.unit?` · 单位：${f.unit}`:''}`;row.append(detail);const note=document.createElement('div');note.textContent=[f.value_labels,f.value_semantics,f.mapping_status,f.caveat].filter(Boolean).join('；');if(note.textContent)row.append(note);container.append(row)}};
 showFields(byId('candidateExposureFields'),e);showFields(byId('candidatePhenotypeFields'),p);
 if(e&&p&&e.concept_id===p.concept_id){warning.hidden=false;warning.textContent='同一概念不能与自身配对；请选择另一个表型或暴露候选。'}
}
function loadCandidatePairExplorer(){
 if(candidatePairExplorerLoaded)return candidatePairExplorerLoaded;
 byId('candidatePairStatus').textContent='正在载入候选配对索引…';
 candidatePairExplorerLoaded=fetch('./candidate_pair_explorer_v1.json?v=5',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(`candidate pair explorer HTTP ${r.status}`);return r.json()}).then(data=>{renderCandidatePairExplorer(data);['candidatePairDesign','candidatePairWave','candidateExposure','candidatePhenotype'].forEach(id=>byId(id).addEventListener(id==='candidateExposure'||id==='candidatePhenotype'?'input':'change',()=>{if(byId('candidatePairDesign').value==='baseline-community'&&byId('candidatePairWave').value==='2011')byId('candidatePairWave').value='2013';renderCandidatePairExplorer(data)}));return data}).catch(err=>{byId('candidatePairStatus').textContent=`候选配对目录载入失败：${err.message}`;return null});
 return candidatePairExplorerLoaded;
}

function renderAssociations() {
  byId('rows').replaceChildren();
  byId('empty').hidden=false;
  byId('count').textContent='0 条已审查的真实关联结果';
}

function addOptions(select, values) {
  for (const value of values) {const option=document.createElement('option');option.value=value;option.textContent=select.id==='cCategory'?({'automated covariate search hit':'自动关键词命中（协变量未选定）','covariate candidate':'协变量备选字段（未选入模型）','measurement metadata':'测量/调查设计元数据','source-detail metadata':'来源字段细节','source-reviewed chronic-disease timing metadata':'已审阅的慢性病时间元数据','source-mapped candidate context':'已映射的候选背景字段'}[value]||value):value;select.append(option)}
}
const C_SUBCATEGORY_LABELS={"community mortality and unstandardized cause-of-death metadata":"社区死亡及未标准化死因元数据","community Part B unstructured other-specify text":"社区问卷B部分非结构化其他说明文本","community Part B questionnaire informant role":"社区问卷B部分信息人身份","Part F community questionnaire informant role; source conflict":"社区问卷F部分信息人身份（来源冲突）","unresolved JA042 community leadership slot":"未核实的社区干部职位槽位","community-questionnaire informant role":"社区问卷信息人身份角色","child education questionnaire/Codebook source conflict":"子女教育问卷与代码本来源冲突","2011 proxy interview and Section E assistance context":"2011代理访谈与E部分协助记录","2018 employer pension contribution amount/share unit selector":"2018雇主养老金缴费金额/比例单位选择器","2018 respondent pension contribution amount/share unit selector":"2018受访者养老金缴费金额/比例单位选择器","2020 CAPI-derived work-day formula under review":"2020 CAPI派生工作日公式，待核验","2020 current-employer start-date verification flag":"2020当前雇主起始日期核验标记","2020 pandemic work-module selection flag":"2020疫情期工作模块选择标记","CAPI-derived survey-home linkage flag":"CAPI派生的调查访谈地址关联标记","age/calendar-year response-format selector":"年龄/日历年份回答格式选择器","beer quantity unit selector":"啤酒数量单位选择器","birth-date source and age derivation metadata":"出生日期来源与年龄推算元数据","blood pressure recent pretest conditions":"血压测量前近期行为条件","chair setup for repeated chair-stand test":"重复坐站测试的座椅设置","checklist none-option coding":"清单题“均无”选项编码","cognitive word-list form and stimulus metadata":"认知词表版本与刺激材料元数据","cognitive-test administration and nonresponse metadata":"认知测验实施与未应答元数据","cognitive-test instrument-use metadata":"认知测验工具使用元数据","commercial-pension expected claim timing format selector":"城镇职工养老金预计领取时间格式选择器","current home market-value response unit selector":"现住房市场价值回答单位选择器","current residence total-price versus unit-price selector by slot":"现住房总价/单位面积价格格式选择器（分槽位）","defined-contribution pension account balance last-check date component":"缴费确定型养老金账户余额最近核对日期组成项","detailed hukou/residential geography components":"户口/居住地详细地理信息组成项","detailed respondent residential address fields":"受访者详细居住地址字段","early-exit pension reduction amount/percentage selector":"提前领取养老金扣减金额/比例选择器","formal-schooling history exposure overlap":"正规教育经历暴露重叠字段","household electricity access exposure overlap":"住宅电力可及性暴露重叠字段","residential settlement context exposure overlap":"居住地聚落环境暴露重叠字段","historical hukou/location context exposure overlap":"历史户籍/居住地语境暴露重叠字段","social participation/care exposure overlap":"社会参与/照护暴露重叠字段","recent hukou change exposure overlap; conditional context candidate":"近期户籍变更暴露重叠；条件性背景候选","exact C/E field overlap; metadata only":"精确 C/E 同字段重叠；仅目录元数据","exact C/P field overlap; metadata only":"精确 C/P 同字段重叠；仅目录元数据","partner/social context exposure overlap":"伴侣与社会背景暴露重叠字段","expected formal-retirement benefit amount/percentage selector":"预计正式退休待遇金额/比例选择器","expected pension benefit amount format selector":"预计养老金待遇金额格式选择器","expected pension benefit amount-unit selector":"预计养老金待遇金额单位选择器","expected pension benefit unit/form selector":"预计养老金待遇单位/形式选择器","expected pension receipt age-versus-years response selector":"预计养老金领取时间按年龄/年数回答选择器","expected pension receipt time format selector":"预计养老金领取时间格式选择器","expected retirement pension benefit format selector":"预计退休养老金待遇格式选择器","expected supplementary pension benefit timing response selector":"预计补充养老金待遇时间回答选择器","firm supplementary pension expected-benefit form selector":"单位补充养老金预计待遇形式选择器","fixed age/calendar-year component-type marker":"年龄/日历年份组成部分类型标记","household debt unfolding-bracket response metadata":"家庭债务逐步追问区间回答元数据","household financial respondent source":"家庭财务回答者来源","money-management helper relationship option slots":"管理钱财帮助者关系选项槽位","household income response-format selectors":"家庭收入回答格式选择器","household income/expenditure respondent source":"家庭收入/支出回答者来源","household property total-price versus unit-price response-format selector":"家庭房产总价/单位面积价格格式选择器","housing rental amount applicability/response-format selector":"住房租金金额适用性/回答格式选择器","hypothetical health anchoring vignettes":"假设健康情境锚定题","inactive fixed-capital legacy/format fields":"未启用的固定资产旧版/格式字段","inactive household lending and debt legacy fields":"未启用的家庭借贷与债务旧版字段","inactive legacy questionnaire slots with no observations":"未启用且无观测记录的旧问卷槽位","individual transfer-income amount unit selector":"个人转移收入金额单位选择器","interview assistance / proxy response context":"访谈协助/代理回答情况","interview language":"访谈语言","invalid extra disability slot with no Yes category":"无“Yes”类别的无效额外残障槽位","keyword discovery only; not a reviewed covariate or adjustment recommendation":"关键词命中线索；字段定义/协变量资格需分别审核，不是调整建议","knee-height measurement agreement and instruction comprehension":"膝高测量同意与说明理解情况","land-requisition pension expected-benefit amount-format selector":"被征地农民养老金预计待遇金额格式选择器","life-course timing unit selectors":"生命历程时间单位选择器","life-insurance contribution payment-period selector":"人寿保险缴费周期选择器","life-insurance expected claim timing format selector":"人寿保险预计领取时间格式选择器","life-insurance expected-benefit amount-format selector":"人寿保险预计待遇金额格式选择器","life-insurance other-type open text":"人寿保险“其他类型”开放文本","linked child-roster selection identifiers":"关联子女名册选择标识","other-pension expected claim timing format selector":"其他养老金预计领取时间格式选择器","pension amount response-format selector or unfolding-bracket bound":"养老金金额回答格式选择器或逐步追问区间边界","pension child-roster payer selection slots":"子女名册中的养老金缴费者选择槽位","personal wage deduction scope and response-unit selectors":"个人工资扣除范围与回答单位选择器","personal wage-deduction response unit and applicability selector":"个人工资扣除回答单位及适用性选择器","physical-activity randomized-module assignment marker":"身体活动随机模块分配标记","prior-interview response-history routing flags":"既往访谈回答历史与跳转标记","prior-wave demographic preload and correction route":"前一波次人口学信息预载与更正路径","prior-wave demographic record verification and response routing":"前一波次人口学记录核验与回答路径","prior-wave diagnosis-time answer-history flags":"前一波次诊断时间回答历史标记","prior-wave diagnosis-time preload values":"前一波次诊断时间预载年龄值（非当前波协变量）","condition or event timing metadata":"疾病或事件时间元数据","residential geography and migration metadata":"居住地与迁居元数据","conditional nurse-care wage metadata":"条件性护工/护士费用元数据","prior-wave reproductive-history preload values":"前一波次生殖史预载年龄值（非当前波暴露/结局）","prior-wave gender route flag":"前一波次性别信息路由标记","hukou life-course exposure overlap; estimand-specific context candidate":"户口生命历程暴露重叠；按估计目标判断的背景候选","marital-history exposure overlap; estimand-specific context candidate":"婚姻史暴露重叠；按估计目标判断的背景候选","marriage-history source availability and route metadata":"婚姻史字段发布状态与问卷路由元数据","adult-education duration exposure overlap; route-specific context candidate":"成人教育年限暴露重叠；保留波次路由的背景候选","respondent gender source and derivation metadata":"受访者性别来源与派生元数据","property-sale proceeds use-category selector slot":"房产出售所得用途类别选择槽位","property-roster location; field meaning reviewed; not respondent residence or an adjustment recommendation":"已核验的房产名册位置；字段含义已审；不是受访者住所或协变量调整建议","respondent age derivation":"受访者年龄派生","confirmed gender derivation":"确认性别派生","interviewer-recorded gender input":"访员记录的性别输入","conditional gender reconfirmation input":"条件性性别再确认输入","prior-wave gender preload":"前一波次性别预载","prior-wave gender reference":"前一波次性别参考值","interviewer gender recode":"访员性别字段重编码","residential-history context":"居住史背景信息","residential-history field identity conflict":"居住史字段身份冲突","current-residence context":"当前住所背景","household mortgage payment measure":"家庭住房按揭月供指标","past-year alcohol threshold and route":"过去一年饮酒阈值与问卷路径","retrospective alcohol history and route":"既往饮酒史与问卷路径","prior-wave alcohol history carry-forward metadata":"前一波饮酒史沿用元数据","alcohol beverage-type selector":"饮酒类型选择元数据","reported diagnosis/knowledge age metadata":"自报诊断/知悉年龄元数据","adult-education participation option slot":"成人教育参与形式选项字段","adult-education credential response metadata":"成人教育证书/学位回答元数据","adult-education highest-credential response metadata":"成人教育最高学历回答元数据","province-level pension-source work-unit location metadata":"省级养老金来源单位地点元数据","questionnaire inserted activity-type labels":"问卷新增活动类型标签","resident-pension supplementary repayment currency selector":"城乡居民养老金补缴金额币种选择器","retirement/receding work-unit geographic linkage components":"退休/原工作单位地理关联组成项","rural pension contribution frequency selector":"农村养老金缴费频率选择器","smoking cessation age/calendar-year response-format selector; component labels conflict":"戒烟年龄/日历年份回答格式选择器；组成项标签存在冲突","social-pension expected-benefit form selector":"社会养老金预计待遇形式选择器","social-pension supplementary repayment currency selector":"社会养老金补缴金额币种选择器","stroke recurrence timing response format":"卒中复发时间回答格式","subjective life-expectancy target age":"主观预期寿命题的目标年龄","subjective life-expectancy target-age metadata":"主观预期寿命题的目标年龄元数据","unlisted chronic-disease index placeholder":"未列明慢性病的索引占位字段","unresolved questionnaire and Codebook field identity conflict":"问卷与代码本字段身份冲突，尚未解决","unresolved release-field identity/data-type discrepancy":"发行字段身份/数据类型差异，尚未解决","unstructured other-specify response text":"未结构化的“其他，请说明”回答文本","unstructured other-use response text":"未结构化的“其他用途”回答文本","respondent age field; source definition and derivation context":"受访者年龄字段；来源定义与推算背景","ever lived outside permanent county/city for over six months; wave-specific branch":"曾在现居县/市以外居住超过六个月；波次分支不同","ever lived outside permanent county/city/district for over six months; wave-specific branch":"曾在现居县/市/区以外居住超过六个月；波次分支不同","cumulative years outside permanent county/city after BB007 yes; keep separate from months":"BB007回答是后的累计离县/市年数；与月数分开","cumulative months outside permanent county/city after BB007 yes; keep separate from years":"BB007回答是后的累计离县/市月数；与年数分开","ever lived outside permanent county/city for over six months; alternate BB001 branch":"曾在现居县/市以外居住超过六个月；BB001另一问卷分支","ever lived outside permanent county/city/district for over six months; alternate BB001 branch":"曾在现居县/市/区以外居住超过六个月；BB001另一问卷分支","cumulative years outside permanent area after BB009 yes; keep separate from months":"BB009回答是后的累计离开居住地年数；与月数分开","cumulative months outside permanent area after BB009 yes; keep separate from years":"BB009回答是后的累计离开居住地月数；与年数分开","calendar year first lived in permanent county/city/district; distinct from village entry":"首次在常住县/市/区居住年份；与村/社区年份区分","calendar year first lived in village/community; distinct from county entry":"首次在村/社区居住年份；与县/市/区年份区分","unsupported prior-wave disease-awareness slots":"前一波次疾病知晓情况槽位，当前不支持","date of death components":"去世日期组成项","mortality date calendar interpretation":"死亡日期历法解释元数据","proxy-reported death expectedness":"代理报告的死亡预期性","final illness-to-death interval":"末次疾病至死亡间隔"};
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
    let valueStatus=x.concept_mapping_statuses?.startsWith('official questionnaire response menu reviewed; CodeBook response-category table omits questionnaire option 2')?'\u5b98\u65b9\u95ee\u5377\u83dc\u5355\u5df2\u6838\uff1bCodeBook\u7c7b\u522b\u8868\u672a\u5217\u5b63\u5ea6\u9009\u9879\uff0c\u5206\u6790\u524d\u6838\u5bf9\u83b7\u51c6\u53d1\u884c\u7248':x.value_label_review?.startsWith('official 2011 questionnaire/Codebook threshold categories transcribed; no response frequencies shown')?'\u5b98\u65b9\u9608\u503c\u7c7b\u522b\u5df2\u6838\uff1bCodebook\u672a\u5217\u7c7b\u522b\u4e0d\u63a8\u65ad\uff0c\u91d1\u989d\u548c\u5e8f\u5217\u4ecd\u9501\u5b9a':x.value_label_review==='conflict'?'编码标签冲突，需人工复核':x.value_label_review?.startsWith('candidate; questionnaire and Codebook labels reviewed; validate routes and eligible denominator in approved data')?'官方问卷和代码本类别已核；发行数据编码、路由及适用人群/分母仍待核':x.value_label_review?.startsWith('official selector code reviewed;')?'官方格式选择器；仅用于解释后续年龄/日历年字段，不是吸烟或饮酒暴露':x.value_label_review?.startsWith('full questionnaire menu transcribed without frequencies; 2011 codebook omits FL014')?'问卷菜单已转录；代码本字段/类别不完整，发行版编码和先前未工作路由待核':x.value_label_review?.startsWith('official questionnaire categories; frequencies omitted; FC020 multiple-job main-work route')?'官方问卷类别；需区分多工作主要工作与单一非农工作路线':x.value_label_review?.includes('official questionnaire')&&x.value_label_review?.includes('frequencies omitted')?'官方问卷类别已核/转录；按波次题意和路由解释，未使用代码本频数':x.value_label_review?.startsWith('official selected-option label; checkbox slot')?'官方复选框选项；未选中或空白不解释为No':x.value_label_review?.startsWith('official questionnaire checkbox menu and codebook slot coding')?'官方问卷复选框选项；路由外或未选中记录不推断为No':x.value_label_review?.startsWith('official 2011 Codebook selected-option category transcribed; frequencies omitted')||x.value_label_review?.startsWith('official 2013 Codebook selected-option category transcribed; frequencies omitted')||x.value_label_review?.startsWith('official 2015 Codebook selected-option category transcribed; frequencies omitted')?'官方代码本仅列被选选项类别；未选存储及路由分母未核，暂不可分析':x.value_label_review?.startsWith('official 2018 Codebook response categories transcribed; frequencies omitted')?'2018官方代码本类别已转录；频数已省略；保留问卷路由；发行版编码及适用分母待验证':x.value_label_review?.startsWith('official wave codebook category verified; selected option only')?'官方代码本类别已核；仅代表选中项，未选中存储码未知':x.value_label_review?.startsWith('official codebook response labels; prior-wave self-awareness/preload route retained')?'官方类别已核；自知疾病/既往波次预加载，按原问卷路由解释':x.value_label_review?.startsWith('continuous measure metadata available')?'连续测量字段；单位与测量范围见变量说明':x.value_label_review?.startsWith('continuous count measure')?'连续计数测量；保留每个15秒区间和正确/总数区别；代码本摘要不定义有效范围':x.value_label_review?.startsWith('continuous recorded response')?'连续原始作答；代码本极端值需用授权数据核验后再定范围或评分':x.value_label_review?.startsWith('numeric/time unit metadata available')?'数量或时间单位已登记；无离散值标签，详见概念交叉表':x.value_label_review?.startsWith('audited measurement component')?'客观测量组成字段；按交叉表派生概念':x.value_label_review?.startsWith('official Codebook extraction exposes only a partial response-code set')?'官方代码本仅显示部分类别；不推断缺失编码':x.value_label_review==='officially reviewed'?'官方值标签已核验':x.value_label_review&&x.value_label_review!=='not yet reviewed'?x.value_label_review:'官方值标签待逐项核验';
    if (x.value_label_review?.startsWith('official codebook field located; continuous/count or no categorical labels')) valueStatus='官方代码本已找到该字段但未列离散类别；数值/计数含义、单位和路由仍需结合问卷核对';
    if (x.value_label_review?.startsWith('official response label not located or title match insufficient')) valueStatus='已检索的官方代码本未定位到可确认的答案类别，或题目标题匹配不足；需逐波回查，不推断类别或缺失编码';
    if (x.value_label_review==='codebook field located; continuous/open response or no categorical labels') valueStatus='官方代码本已找到该字段；它是连续/开放回答或未列离散类别，不虚构答案标签；单位和题目路由仍需核对';
    if (x.value_label_review==='official codebook category labels not located') valueStatus='已检索的官方代码本中未找到该字段的类别标签；这不代表没有类别，问卷菜单、单位、路由和发行版编码仍待核对';
    if (x.value_label_review?.startsWith('official Codebook lists numeric summary; no categorical response menu in this entry')) valueStatus='官方代码本为该字段列出数值摘要，未列分类菜单；单位、特殊值和路由仍需结合问卷核对';
    if (x.value_label_review?.startsWith('official Codebook response categories transcribed; frequencies omitted; cross-wave question scope and release coding pending')) valueStatus='官方代码本类别已转录且已省略频数；跨波题意、发行版编码和适用分母仍待核对';
    if (x.value_label_review?.startsWith('DO NOT ANALYZE; questionnaire:')) valueStatus='⚠ 问卷与Codebook编码冲突，已锁定不可分析；'+x.value_label_review;
    const relationStratified=x.concept_mapping_relationship?.startsWith('relationship_stratified_parent_record_measure:');
    const candidateStatus=x['Candidate.Status']||'C类来源/测量元数据';
    const conceptDisplay=role==='c'?(candidateStatus==='automated discovery; questionnaire/codebook review required'?'自动发现纳入候选目录；逐字段核验状态见来源与值标签列':candidateStatus==='official questionnaire and Codebook reviewed; prior-wave diagnosis-time preload metadata'?'官方问卷与代码本已核；前波诊断时间预载元数据':candidateStatus==='official questionnaire and Codebook reviewed; prior-wave reproductive-history preload metadata'?'官方问卷与代码本已核；前波生殖史预载元数据':candidateStatus):[x.candidate_concept_ids||'待归属稳定概念',x.candidate_concept_alias_ids?`别名：${x.candidate_concept_alias_ids}`:'',x.concept_mapping_collision&&!relationStratified?'⚠ 构念重叠待按关系审查':'',x['Review.Flag']?.includes('DO NOT ANALYZE')?'\u26a0 DO NOT ANALYZE':''].filter(Boolean).join('；');
    const metadataNote=role==='c'?(x.concept_mapping_caveats||x['Review.Flag']||'请回查来源问卷/代码本'):'';
    const metadataReview=x.value_label_review?.startsWith('official selector code reviewed;')?valueStatus:x.value_label_review?.startsWith('official questionnaire and Codebook reviewed; continuous prior-wave diagnosis-age value')?'官方问卷与代码本已确认：前波诊断/知悉年龄数值；不是当前波结局或通用调整变量':x['Value.Label.Review']==='not yet reviewed'?'官方值标签/编码尚未逐项核验；连续变量可能没有离散类别标签':x['Value.Label.Review']==='officially reviewed'?'官方值标签已核验':x['Value.Label.Review'];
    const metadataSemantics=role==='c'?([x.value_labels,metadataReview].filter(Boolean).join('；')||'测量/设计元数据'):'';
    const harmonizationNote=x.harmonization_status?.startsWith('continuous internal biomarker/clinical or physical measure')?'内部生理/临床测量，属于表型候选，不是外源环境暴露；跨波尚未统一':'';
    const labelDisplay=role==='c'?metadataSemantics:[x.value_labels||valueStatus,x.value_labels&&valueStatus!=='官方值标签已核验'?valueStatus:'',harmonizationNote].filter(Boolean).join('；');
    const categoryDisplay=role==='c'?({'automated covariate search hit':'自动关键词命中（协变量未选定）','covariate candidate':'协变量备选字段（未选入模型）','measurement metadata':'测量/调查设计元数据'}[x.category]||x.category):({'social wellbeing':'社会关系与主观幸福感','health and symptoms':'健康与症状'}[x.category]||x.category);
    const subcategoryDisplay=role==='c'?(C_SUBCATEGORY_LABELS[x.subcategory]||x.subcategory):({'marital relationship satisfaction':'婚姻关系满意度','life satisfaction':'总体生活满意度','health satisfaction':'健康满意度','relationship with children satisfaction':'与子女关系满意度','subjective life expectancy':'主观预期寿命可能性'}[x.subcategory]||x.subcategory);
    const displayValues=[x['Variable.Name'],conceptDisplay,categoryDisplay+' · '+subcategoryDisplay,x['Variable.Description'],x.waves,x.source_modules,role==='c'?metadataNote:(x.candidate_concept_units||'未登记单位/分类构成'),labelDisplay];
    for(const [i,value] of displayValues.entries()){
      const td=document.createElement('td');td.textContent=value;tr.append(td)
      if(i===1)td.title=role==='c'?'C类角色判定：'+(x['Candidate.Status']||'来源/测量元数据')+'；处理边界：'+(x['Harmonization.Status']||'不进入E/P关联矩阵')+'；审核：'+(x['Review.Flag']||'回查对应波次的官方问卷/代码本')+'；官方来源：'+(x['Value.Label.Source']||'见项目官方来源清单'):'候选概念：'+(x.candidate_concept_labels||'待核')+'；原始别名ID：'+(x.candidate_concept_alias_ids||'无')+'；关系：'+(x.concept_mapping_relationship||'无额外重叠')+'；映射状态：'+(x.concept_mapping_statuses||'待核')+'；解释与路由：'+(x.concept_mapping_caveats||'未登记')+'；来源表：'+(x.concept_mapping_sources||'待核')
      if(i===2&&role==='c')td.title='原始分类说明：'+x.subcategory
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

function loadCatalog(role){
  if(catalogLoaded[role])return catalogLoaded[role];
  const prefix={e:'e',p:'p',c:'c'}[role],countId={e:'eCount',p:'pCount',c:'cCount'}[role];
  byId(countId).textContent='正在载入字段目录…';
  catalogLoaded[role]=fetch(`./catalog_${role}.json?v=1`,{cache:'no-cache'}).then(r=>{
    if(!r.ok)throw new Error(`catalog_${role}.json HTTP ${r.status}`);
    return r.json();
  }).then(all=>{
    renderCatalog(all,role,prefix);
    const controls={e:['eSearch','eCategory','eWave'],p:['pSearch','pCategory','pWave'],c:['cSearch','cCategory','cWave']}[role];
    controls.forEach(id=>byId(id).addEventListener('input',()=>renderCatalog(all,role,prefix)));
    if(role==='e')renderGroups(all);
    return all;
  }).catch(err=>{
    byId(countId).textContent=`候选目录载入失败：${err.message}`;
    return null;
  });
  return catalogLoaded[role];
}
renderBrowseCards('phenotypeBrowse','p');renderBrowseCards('exposureBrowse','e');
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
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_labels} ${field.value_semantics} ${field.value_label_status} ${field.unit||''} ${field.source_evidence||''} ${field.note||''} ${field.source_document||''} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('foodEnvRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,field.value_labels||'值标签待核',[field.value_label_status,field.value_label_source,field.note,field.source_document,concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
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
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.domain} ${field.code} ${field.source_label} ${field.module} ${field.value_labels} ${field.value_label_status} ${field.unit||''} ${field.source_evidence||''} ${field.caveat||''} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('communityRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,concept.domain,field.code,field.wave,field.module,field.source_label,field.unit||'—',field.value_labels||field.value_label_status,[field.value_label_source,field.source_evidence,field.value_label_status,field.caveat,concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v||'—';tr.append(td)}body.append(tr)}
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
 const matches=items.filter(x=>(!wave||x.wave===wave)&&(!term||`${x.concept_id} ${x.concept_label} ${x.domain} ${x.variables} ${x.source_field_labels||''} ${x.module} ${x.value_semantics} ${x.source_status} ${x.source_document} ${x.codebook_presence||''} ${x.source_caveat||''}`.toLocaleLowerCase().includes(term)));
 const body=byId('objectiveRows');body.replaceChildren();
 for(const x of matches){const tr=document.createElement('tr');for(const v of [x.concept_id,x.concept_label,x.domain,x.variables,x.source_field_labels||'Codebook字段标签未提取',x.wave,x.module,x.value_semantics,[x.source_status,x.codebook_presence,x.source_caveat,x.source_document].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('objectiveCount').textContent=`筛选命中 ${matches.length} 条波次—概念映射，涉及 ${new Set(matches.map(x=>x.concept_id)).size} 个候选测量概念；同一概念下多个读数不是多个指标。`;
}
objectiveMeasurementsLoaded.then(items=>{renderObjectiveMeasurements(items);['objectiveSearch','objectiveWave'].forEach(id=>byId(id).addEventListener('input',()=>renderObjectiveMeasurements(items)));document.querySelector('[data-view="objectiveMeasures"]').addEventListener('click',()=>renderObjectiveMeasurements(items))}).catch(err=>{byId('objectiveCount').textContent=`客观测量目录载入失败：${err.message}`});


const disabilityHistoryLoaded=deferJson('./disability_history_v1.json?v=1','disabilityHistory');
function renderDisabilityHistory(items){
 const term=byId('disabilitySearch').value.trim().toLocaleLowerCase(),wave=byId('disabilityWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.label_en} ${field.code} ${field.field_role} ${field.source_label} ${field.value_labels} ${field.value_label_status} ${field.caveat} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('disabilityRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,`${concept.label} (${concept.label_en})`,field.wave,field.code,field.field_role,field.source_label,`${field.value_labels||field.value_label_status}；${field.value_label_source}；${field.caveat||concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('disabilityCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 类残疾史；字段数不等于独立结局数。`;
}
disabilityHistoryLoaded.then(items=>{renderDisabilityHistory(items);['disabilitySearch','disabilityWave'].forEach(id=>byId(id).addEventListener('input',()=>renderDisabilityHistory(items)));document.querySelector('[data-view="disabilityHistory"]').addEventListener('click',()=>renderDisabilityHistory(items))}).catch(err=>{byId('disabilityCount').textContent=`残疾史目录载入失败：${err.message}`});

const cancerSitesLoaded=deferJson('./cancer_sites_v1.json?v=1','cancerSites');
function renderCancerSites(items){
 const term=byId('cancerSearch').value.trim().toLocaleLowerCase(),wave=byId('cancerWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${concept.site} ${field.code} ${field.source_label} ${field.value_labels} ${field.module} ${field.value_label_source} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('cancerRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.site,field.wave,field.code,field.source_label,field.value_labels||'该字段未观察到可核实的部位选项标签',`${field.value_label_status}；来源：${field.value_label_source}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('cancerCount').textContent=`筛选命中 ${matches.length} 条波次—源字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个癌症部位概念；标签中不含频数。`;
}
cancerSitesLoaded.then(items=>{renderCancerSites(items);['cancerSearch','cancerWave'].forEach(id=>byId(id).addEventListener('input',()=>renderCancerSites(items)));document.querySelector('[data-view="cancerSites"]').addEventListener('click',()=>renderCancerSites(items))}).catch(err=>{byId('cancerCount').textContent=`癌症部位目录载入失败：${err.message}`});

const housingCatalogLoaded=deferJson('./housing_catalog_v1.json?v=2','housingCatalog');
function renderHousingCatalog(items){
 const term=byId('housingSearch').value.trim().toLocaleLowerCase(),wave=byId('housingWave').value;
 const matches=items.filter(x=>(!wave||x.wave===wave)&&(!term||`${x.concept_id} ${x.concept_label} ${x.code} ${x.source_label} ${x.module} ${x.unit||''} ${x.value_labels} ${x.caveat}`.toLocaleLowerCase().includes(term)));
 const body=byId('housingRows');body.replaceChildren();
 for(const x of matches.slice(0,150)){const tr=document.createElement('tr');for(const v of [x.code,x.concept_label,x.wave,x.module,x.source_label,x.unit||"—",x.value_labels||x.value_label_status,[x.mapping_status,x.value_label_status,x.value_label_source,x.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v;tr.append(td)}body.append(tr)}
 byId('housingCount').textContent=`筛选命中 ${matches.length} 条波次—字段映射，当前展示 ${Math.min(matches.length,150)} 条，涉及 ${new Set(matches.map(x=>x.concept_id)).size} 个候选概念；值码只在对应波次解释。`;
}
housingCatalogLoaded.then(items=>{renderHousingCatalog(items);['housingSearch','housingWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHousingCatalog(items)));document.querySelector('[data-view="housingCatalog"]').addEventListener('click',()=>renderHousingCatalog(items))}).catch(err=>{byId('housingCount').textContent=`住房编码目录载入失败：${err.message}`});

const householdRentalIncomeLoaded=deferJson('./household_other_asset_rental_income_v1.json?v=1','householdRentalIncome');
function renderHouseholdRentalIncome(items){
 const term=byId('rentalIncomeSearch').value.trim().toLocaleLowerCase(),wave=byId('rentalIncomeWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.value_labels} ${field.unit} ${field.mapping_status} ${field.source_document} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('rentalIncomeRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.wave,field.code,field.module,field.source_label,field.value_labels||field.unit,`${field.mapping_status}；${field.source_document}；${concept.caveat}`]){const td=document.createElement('td');td.textContent=v||'—';tr.append(td)}body.append(tr)}
 byId('rentalIncomeCount').textContent=`筛选命中 ${matches.length} 条波次—字段映射，涉及 ${new Set(matches.map(x=>x.concept.concept_id)).size} 个候选概念；不代表有效样本数或可直接合并的指标。`;
}
householdRentalIncomeLoaded.then(items=>{renderHouseholdRentalIncome(items);['rentalIncomeSearch','rentalIncomeWave'].forEach(id=>byId(id).addEventListener('input',()=>renderHouseholdRentalIncome(items)));document.querySelector('[data-view="householdRentalIncome"]').addEventListener('click',()=>renderHouseholdRentalIncome(items))}).catch(err=>{byId('rentalIncomeCount').textContent=`家庭资产租赁收入目录载入失败：${err.message}`});

const householdCovidEconomicsLoaded=deferJson('./household_covid_economic_v1.json?v=1','householdCovidEconomics');
function renderHouseholdCovidEconomics(items){
 const term=byId('covidEconomicSearch').value.trim().toLocaleLowerCase(),wave=byId('covidEconomicWave').value,matches=[];
 for(const concept of items)for(const field of concept.source_fields){if(wave&&field.wave!==wave)continue;if(term&&!`${concept.concept_id} ${concept.label} ${field.code} ${field.source_label} ${field.value_labels} ${field.unit} ${field.mapping_status} ${field.source_document} ${concept.caveat}`.toLocaleLowerCase().includes(term))continue;matches.push({concept,field})}
 const body=byId('covidEconomicRows');body.replaceChildren();
 for(const {concept,field} of matches){const tr=document.createElement('tr');for(const v of [concept.concept_id,concept.label,field.wave,field.code,field.module,field.source_label,field.value_labels||field.unit,[field.mapping_status,field.source_document,concept.caveat].filter(Boolean).join('；')]){const td=document.createElement('td');td.textContent=v||'—';tr.append(td)}body.append(tr)}
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
