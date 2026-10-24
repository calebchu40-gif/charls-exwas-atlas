"""Review written labor contract status across five current-work waves."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv'; INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv'; SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
CONCEPT='written_labor_contract'; REVIEW='audit/written_labor_contract_review_2026-10-25.md'
FIELDS={
 '2011':('fd020','CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','did you receive a labor contract','1=Yes; 2=No'),
 '2013':('fd020','CHARLS_2013_Questionnaire_extracted.txt','did you receive a labor contract','1=Yes; 2=No'),
 '2015':('fd020','CHARLS_2015_Questionnaire_extracted.txt','did you receive a labor contract','1=Yes; 2=No'),
 '2018':('fd020','CHARLS_2018_Questionnaire_extracted.txt','did you receive a labor contract','1=Yes; 2=No'),
 '2020':('fc016','CHARLS_2020_Questionnaire_English_extracted.txt','sign a labor contract in written form','1=Yes; 2=No'),
}
UNIT='binary self-report; written labor contract status (1=Yes, 2=No)'
STATUS=f'official wave-specific questionnaire/Codebook item wording, Yes/No codes and applicable route reviewed; payor reference, release storage and eligible denominator require QA; see {REVIEW}'
CAVEAT=('Self-reported written labor-contract status in the current-work module; it is not a direct environmental exposure and does not measure contract duration, quality, labor rights or overall job security. '
        'In 2011–2015, the item refers to the current workplace or labor-dispatch company; the 2018 CAPI instruction assigns the referent to the dispatch company for dispatched workers and to the wage-paying person for workers hired by an individual. '
        'Preserve these route-specific referents. A No response skips contract-detail questions; do not treat those downstream structural skips as missing contract-status responses. Verify current-worker eligibility, special values and field storage in the authorized release.')

def norm(p):return re.sub(r'\s+',' ',p.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 for w,(code,qfile,prompt,labels) in FIELDS.items():
  q=norm(ROOT/'sources_official'/qfile); cb=(ROOT/'sources_official'/f'CHARLS_{w}_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').casefold()
  if prompt not in q or code not in cb:raise ValueError(f'Official {w} contract item missing')
  item=q[q.find(prompt):q.find(prompt)+600]
  if 'yes' not in item:raise ValueError(f'{w} Yes response missing')
  if 'no' not in item:raise ValueError(f'{w} No response missing')
 if 'dispatch company' not in norm(ROOT/'sources_official'/'CHARLS_2018_Questionnaire_extracted.txt'):
  raise ValueError('2018 dispatch-company referent note missing')

def main():
 validate(); expected={(w,CONCEPT,c.lower()) for w,(c,*_) in FIELDS.items()}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected:continue
  w=k[0];r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' 2018 CAPI payor-referent distinction retained; follow-up skips are not used to recode the status item.';r['caveat']=CAVEAT + (' The 2011 questionnaire prints Yes/No without numeric display codes; numeric coding is taken from the Codebook and must be confirmed in the authorized release.' if w=='2011' else '');r['unit']=UNIT;seen.add(k)
 if seen!=expected:raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected:continue
  r['Mapping.Status']=STATUS;r['Caveat']=CAVEAT;r['Unit']=UNIT;r['Value.Labels']=FIELDS[k[0]][3];r['Value.Semantics']='binary Yes/No response; wave-specific contract referent retained';indexed.add(k)
 if indexed!=expected:raise ValueError(f'E/P index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8'));found=set()
 for item in data:
  if item.get('concept_id')!=CONCEPT:continue
  item['caveat']=CAVEAT
  for fld in item.get('source_fields',[]):
   k=(str(fld.get('wave','')),item['concept_id'],str(fld.get('code','')).lower())
   if k not in expected:continue
   w=k[0];extra=' The 2011 questionnaire prints Yes/No without numeric display codes; confirm the Codebook coding in the authorized release.' if w=='2011' else ''
   fld.update({'mapping_status':STATUS,'note':STATUS+extra,'caveat':CAVEAT+extra,'unit':UNIT,'value_labels':FIELDS[w][3],
    'value_label_status':'Official questionnaire/Codebook Yes/No response categories reviewed; frequencies omitted',
    'value_label_source':f"sources_official/{FIELDS[w][1]}; sources_official/CHARLS_{w}_Codebook_extracted.txt"});found.add(k)
 if found!=expected:raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'Reviewed and synchronized {len(expected)} written-contract fields.')

if __name__=='__main__':main()
