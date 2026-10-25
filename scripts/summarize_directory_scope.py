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
# This block is regenerated on every metadata finalization. Remove any copy
# left by an earlier run before locating/rebuilding the statistics section.
lines=[line for line in lines if not (
    line.lstrip().startswith('<p class="stats-note">') and '去重后共有' in line
)]
e_only=len(e_ids-p_ids); p_only=len(p_ids-e_ids); dual=len(e_ids&p_ids)
indices=[i for i,line in enumerate(lines) if line.lstrip().startswith('<div class="stats"')]
if len(indices)!=1: raise SystemExit('Expected exactly one stats block; refusing to overwrite unexpected HTML')
start=indices[0]; indent=len(lines[start])-len(lines[start].lstrip())
end=next((i for i in range(start+1,len(lines)) if lines[i].strip()=='</div>' and len(lines[i])-len(lines[i].lstrip())==indent),None)
if end is None: raise SystemExit('Could not locate stats block closing tag; refusing to overwrite unexpected HTML')
new=[
    ' '*indent+'<div class="stats" aria-label="目录进度">',
    ' '*(indent+2)+f'<div class="stat"><b>{len(e_ids):,}</b><span>暴露候选概念</span></div>',
    ' '*(indent+2)+f'<div class="stat"><b>{len(p_ids):,}</b><span>表型候选概念</span></div>',
    ' '*(indent+2)+'<div class="stat"><b>5</b><span>调查波次：2011–2020</span></div>',
    ' '*(indent+2)+'<div class="stat"><b>0</b><span>正式关联模型</span></div>',
    ' '*indent+'</div>',
    ' '*indent+f'<p class="stats-note">五轮常规主调查去重后共有 {len(concept_ids):,} 个 E/P 候选概念，其中 {len(e_ids & p_ids)} 个同时承担暴露与表型角色；{rows:,} 条概念—源字段映射是目录对应关系，不是样本量或关联结果。2014生命历程特殊调查单独展示，不计入上述五波统计。E 是广义解释变量候选，涵盖社区/住房、饮食与行为、社会经济/工作/保障，也包含内部血液生物标志物；{len(e_ids):,} 不代表环境化学物数量。</p>',
]
lines=lines[:start]+new+lines[end+1:]
html.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'candidate_concept_ids':len(concept_ids),'exposures':len(e_ids),'phenotypes':len(p_ids),'concept_source_rows':rows},ensure_ascii=False))
