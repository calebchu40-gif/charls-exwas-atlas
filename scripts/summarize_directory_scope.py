"""Count the full E/P concept-source index and refresh prototype KPI cards."""
from pathlib import Path
from datetime import date
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
master=pd.read_csv(ROOT/'audit/ep_concept_source_crosswalk_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
role_sets=master['Role'].str.split(',').apply(lambda xs:{x.strip() for x in xs})
ep=master[[bool(x & {'e','p'}) for x in role_sets]].copy()
e_ids=set(ep.loc[ep['Role'].str.contains('e'),'Concept.ID'])
p_ids=set(ep.loc[ep['Role'].str.contains('p'),'Concept.ID'])
concept_ids=e_ids|p_ids
rows=len(ep)
domains=[]
for source, group in ep.groupby('Source.File'):
    domains.append({'file':source,'mapping_rows':len(group),'concept_ids':group['Concept.ID'].nunique()})
summary={'as_of':date.today().isoformat(),'crosswalk_files':len(domains),'candidate_concept_ids':len(concept_ids),
         'exposure_concept_ids_including_dual':len(e_ids),'phenotype_concept_ids_including_dual':len(p_ids),
         'wave_field_mapping_rows':rows,'includes':'all E/P candidate rows from ep_concept_source_crosswalk_v1.csv',
         'excludes':'C-only measurement eligibility rows; verified_code_examples_v1.csv is a separate multiwave lookup',
         'domains':domains}
(ROOT/'audit/directory_scope_counts_v1.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
html=ROOT/'site-prototype/dist/index.html'; lines=html.read_text(encoding='utf-8').splitlines()
e_only=len(e_ids-p_ids); p_only=len(p_ids-e_ids); dual=len(e_ids&p_ids)
new=f'<div class="stats" aria-label="项目当前进展"><div class="stat"><b>{len(concept_ids)}</b><span>去重候选 E/P Concept ID</span></div><div class="stat"><b>{len(e_ids)} / {len(p_ids)}</b><span>E / P 角色概念；另有{dual}个双角色（去重{len(concept_ids)}）</span></div><div class="stat"><b>5</b><span>已整理波次（2011–2020）</span></div><div class="stat"><b>{rows:,}</b><span>E/P概念—源字段映射；含波次/槽位</span></div><div class="stat"><b>0</b><span>正式关联模型已拟合</span></div></div>'
indices=[i for i,line in enumerate(lines) if line.lstrip().startswith('<div class="stats" aria-label="项目当前进展">')]
if len(indices)!=1: raise SystemExit('Expected exactly one KPI line; refusing to overwrite unexpected HTML')
lines[indices[0]]='    '+new
html.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'candidate_concept_ids':len(concept_ids),'exposures':len(e_ids),'phenotypes':len(p_ids),'concept_source_rows':rows},ensure_ascii=False))
