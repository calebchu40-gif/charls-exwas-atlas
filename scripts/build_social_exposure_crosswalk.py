"""Build a conservative social participation and intergenerational contact directory."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
src=pd.read_csv(ROOT/'audit/raw_variable_catalog_v1.csv',dtype=str).fillna('')
concepts=[
 ('social_participation','Social participation activities','Social relationships / activity','Participation checklist items differ by wave. Activity slots are not fully semantically aligned; 2020 uses xsoctype_* and does not expose frequency in this code family. Preserve item-level fields; do not create an unvalidated social-isolation score.'),
 ('social_activity_frequency','Frequency of social activities','Social relationships / activity','2011 fields are tied to fixed activity types; 2013–2018 suffixes are positional among selected DA056 activities and require within-wave linkage.'),
 ('parent_visits','Visits with non-co-resident parents','Intergenerational contact','Parent roster slots and parent definitions vary by wave (biological/step/in-law and spouse routing). Wave 4 labels refer to non-co-resident parents. This is contact frequency, not perceived support.'),
 ('child_visits','Visits with children','Intergenerational contact','Child-indexed frequency fields; child roster size and co-residence/eligibility affect availability. Wave 4 also has separate co-residence duration fields; those are not visit frequency.'),
 ('child_contact','Contact with children','Intergenerational contact','Child-indexed contact frequency fields; mode/recall definition should be checked by questionnaire. Do not merge with in-person visits.'),
 ('formal_caregiver_current','Volunteer/facility caregiver among current helpers','Care support','Conditional on functional limitations and the CHARLS helper roster. 2011 checklist and 2013 task/helper-slot fields have different storage structures; retain wave, task, slot, and original code. The 2011 codebook reports no observations for db022s38; 2013 helper-category fields are sparse in the codebook summaries. Do not assume adequate modeling power. These are not population-wide access or service-use measures.'),
 ('informal_help_eating','Informal help with eating','Care support','2013/2015/2018 yes/no item asked only after a reported eating difficulty; not general caregiver access or a population-wide measure. Preserve the eligible denominator and structural skips; no 2020 equivalent mapped.'),
 ('informal_help_household_chores','Informal help with household chores','Care support','2013/2015/2018 item follows household-chore difficulty. In 2013/2015, official questionnaire wording says help with household chores while the codebook variable label says help preparing hot meals; retain a source-conflict warning and do not analyze those waves until the field-label discrepancy is resolved. 2018 wording is aligned; the measure remains conditional.'),
 ('informal_help_meal_preparation','Informal help preparing hot meals','Care support','2013/2015/2018 yes/no item follows difficulty preparing hot meals; 2013/2018 questionnaires also route nursing-home residents away from the follow-up. Not population-wide meal support; preserve functional-difficulty and residence eligibility, and do not infer no help from a skip. No 2020 equivalent mapped.'),
 ('formal_caregiver_days','Days helped by volunteer/facility caregiver in prior month','Care support','2011 only: DB023_38_ records days in the last month for the volunteer helper category, conditional on the respondent having a listed helper. The 2011 codebook summary has one observed record; treat as a lookup candidate, not evidence of adequate analytic coverage. Preserve the original count and skip/missing codes; no cross-wave equivalence established.'),
 ('formal_care_expected_future','Expected volunteer/facility help in future','Perceived future care support','2011/2013 future-helper roster category. This is an expectation about potential future help, not current receipt or guaranteed service access; preserve wave-specific wording and response coding.'),
]
rules={
 'social_participation':lambda w,v: (w in ['2011','2013','2015','2018'] and v.lower().startswith('da056')) or (w=='2020' and v.lower().startswith('xsoctype_')),
 'social_activity_frequency':lambda w,v: w in ['2011','2013','2015','2018'] and v.lower().startswith('da057_'),
 'parent_visits':lambda w,v: v.lower().startswith('cd002') and w in ['2011','2013','2015','2018'] and not ('w2' in v.lower()),
 'child_visits':lambda w,v: v.lower().startswith('cd003') and w in ['2011','2013','2015','2018'] and '_w4_' not in v.lower(),
 'child_contact':lambda w,v: v.lower().startswith('cd004') and w in ['2011','2013','2015','2018'],
 'formal_caregiver_current':lambda w,v: (w=='2011' and v.lower()=='db022s38') or (w=='2013' and v.lower().startswith('db022_w2_') and v.lower().endswith('_s64')),
 'formal_caregiver_days':lambda w,v: w=='2011' and v.lower()=='db023_38_',
 'formal_care_expected_future':lambda w,v: w in ['2011','2013'] and v.lower()=='db031s37',
 'informal_help_eating':lambda w,v: w in ['2013','2015','2018'] and v.lower()=='db012_w2',
 'informal_help_household_chores':lambda w,v: w in ['2013','2015','2018'] and v.lower()=='db016_w2',
 'informal_help_meal_preparation':lambda w,v: w in ['2013','2015','2018'] and v.lower()=='db017_w2',
}
rows=[]
def value_note(cid,wave):
 if cid=='social_participation':
  if wave=='2018': return '官方代码本：0=No；正值表示对应活动项目（如 da056_s1：1=Interacted With Friends）。具体答案槽及特殊缺失仍需按代码本解析。'
  if wave=='2020': return '官方代码本将 xsoctype_* 标为字符串变量；保留字符串答案，不能假定为数值0/1。'
  return '代码本列出活动类型/槽位；当前未逐波确认未选中、未提及和特殊缺失的存储码，不作二元重编码。'
 if cid=='social_activity_frequency':
  if wave=='2011': return '官方代码本值标签：1=Almost daily；2=Almost every week；3=Less often。该波字段按固定活动类型提问（如朋友交往），不与后续波次的位置槽位直接等同。'
  return '官方代码本值标签：1=Almost Daily；2=Almost Every Week；3=Not Regularly。2013–2018后缀序号指DA056所选活动的顺序槽位，须与相同访谈的活动排列对应。'
 if cid in {'child_visits','child_contact'}:
  return '官方代码本有序类别：1=Almost every day；2=2-3 times a week；3=Once a week；4=Every two weeks；5=Once a month；6=Once every three months；7=Once every six months；8=Once a year；9=Almost never；10=Other。保留类别，不当作等距连续量。'
 if cid=='formal_caregiver_current':
  return '官方问卷/代码本标注志愿者或机构人员为照护者名册中的一个类别。2011为是否经常帮助的单项字段（代码本显示无观察值）；2013为按ADL/IADL任务及帮助者槽位展开的类别字段，代码本汇总提示稀疏。值编码及未问/跳题状态需按各波代码本解析；先检查原始数据实际覆盖与分母，再决定是否可建模。'
 if cid=='formal_caregiver_days':
  return '官方问卷：过去一个月志愿者帮助的天数（0–31）；仅在帮助者名册相关条件下询问。代码本汇总仅见1条观察记录，不能据此认为有足够分析样本；先核原始覆盖。保留原始计数及特殊缺失码。'
 if cid=='formal_care_expected_future':
  return '官方问卷将志愿者/机构人员列为未来可能帮助者类别；此题属于未来帮助者名册，不等同当前照护。保留逐波原始编码。'
 if cid in {'informal_help_eating','informal_help_household_chores','informal_help_meal_preparation'}:
  condition={'informal_help_eating':'仅在报告进食困难者中追问是否有人帮助进食', 'informal_help_household_chores':'仅在报告家务困难者中追问是否有人帮助做家务', 'informal_help_meal_preparation':'仅在报告备餐困难者中追问是否有人帮助准备热餐'}[cid]
  if cid=='informal_help_meal_preparation' and wave in {'2013','2018'}:
   condition += '；问卷还规定养老院居住者跳过该帮助题'
  return f'官方值标签：1=Yes；2=No。{condition}；缺失或未问不能编码为No；不是全体样本的照护覆盖率。'
 return '该波代码标签仍需逐字段回查；保留原码及名册槽位，不进行跨波重编码。'

def value_labels(cid,wave):
 if cid in {'informal_help_eating','informal_help_household_chores','informal_help_meal_preparation'}:
  return '1=Yes; 2=No'
 return ''

for cid,label,domain,caveat in concepts:
 for _,r in src.iterrows():
  if rules[cid](r.wave,r.variable):
   if cid=='informal_help_household_chores' and r.wave in {'2013','2015'}:
    status='Official questionnaire/codebook yes-no response categories reviewed; questionnaire item wording conflicts with codebook variable label; candidate mapping only; DO NOT ANALYZE until source version/field alias is reconciled'
   elif cid=='formal_caregiver_current' and r.wave=='2011':
    status='2011 baseline questionnaire helper-list category and route reviewed; Codebook reports no observations; candidate metadata only'
   elif cid=='formal_caregiver_days' and r.wave=='2011':
    status='2011 baseline questionnaire helper-roster route and 1–31 days unit reviewed; Codebook summary reports one observation; candidate only'
   elif cid=='formal_care_expected_future' and r.wave=='2011':
    status='2011 baseline questionnaire future-helper route and category reviewed; candidate only'
   elif cid in {'informal_help_eating','informal_help_meal_preparation','informal_help_household_chores'}:
    status='Official questionnaire/codebook yes-no response categories reviewed; conditional care-support candidate; preserve route and eligible denominator'
   else:
    status='Official codebook response labels reviewed; preserve original category and routing' if cid in {'social_activity_frequency','child_visits','child_contact'} or (cid=='social_participation' and r.wave in {'2018','2020'}) else 'Codebook/catalog label candidate; item-level questionnaire and value-label review required'
   questionnaire_source=(f'sources_official/CHARLS_{r.wave}_Questionnaire_extracted.txt; {r.variable.upper()}' if cid.startswith('informal_help_') else 'sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; DB022/DB023/DB030/DB031' if r.wave=='2011' and cid in {'formal_caregiver_current','formal_caregiver_days','formal_care_expected_future'} else '')
   value_label_source=(f'sources_official/CHARLS_{r.wave}_Codebook_extracted.txt' if cid.startswith('informal_help_') else 'sources_official/CHARLS_2011_Codebook_extracted.txt' if r.wave=='2011' and cid in {'formal_caregiver_current','formal_caregiver_days','formal_care_expected_future'} else '')
   if cid=='social_participation' and r.wave=='2020':
    questionnaire_source='sources_official/CHARLS_2020_Questionnaire_English_extracted.txt'
    value_label_source='sources_official/CHARLS_2020_Codebook_extracted.txt'
   rows.append(dict(concept_id=cid,concept_label=label,domain=domain,wave=r.wave,code=r.variable,module=r.module,source_label=r.variable_label,mapping_status=status,value_labels=value_labels(cid,r.wave),value_semantics=value_note(cid,r.wave),questionnaire_source=questionnaire_source,value_label_source=value_label_source,caveat=caveat))
out=pd.DataFrame(rows).drop_duplicates()
out.to_csv(ROOT/'audit/social_exposure_crosswalk_v1.csv',index=False,encoding='utf-8-sig')
items=[]
for cid,label,domain,caveat in concepts:
 fields=out[out.concept_id.eq(cid)]
 items.append(dict(concept_id=cid,label=label,domain=domain,caveat=caveat,source_fields=[dict(wave=str(x.wave),code=x.code,module=x.module,source_label=x.source_label,note=x.mapping_status,value_labels=x.value_labels,value_semantics=x.value_semantics,questionnaire_source=x.questionnaire_source,value_label_source=x.value_label_source) for x in fields.itertuples()]))
(ROOT/'site-prototype/dist/social_exposures_v1.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'concepts={len(items)} field mappings={len(out)} by concept={out.groupby("concept_id").size().to_dict()} by wave={out.groupby("wave").size().to_dict()}')


