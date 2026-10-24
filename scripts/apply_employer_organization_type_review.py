"""Review current-employer organization type fields across CHARLS waves."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv'; INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv'; SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
CONCEPT='current_employer_organization_type'; REVIEW='audit/current_employer_organization_type_review_2026-10-25.md'
FIELDS={
 '2011':('fd002','CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','1=Government department; 2=Public institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Farmer; 7=Individual household; 8=Other'),
 '2013':('fd002','CHARLS_2013_Questionnaire_extracted.txt','1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Farmer; 7=Individual household; 8=Other'),
 '2015':('fd002','CHARLS_2015_Questionnaire_extracted.txt','1=Government; 2=Institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Farmer; 7=Individual household; 8=Other'),
 '2018':('fd002','CHARLS_2018_Questionnaire_extracted.txt','1=Government; 2=Public institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Farmer; 7=Individual household; 8=Other'),
 '2020':('fc002','CHARLS_2020_Questionnaire_English_extracted.txt','1=Government; 2=Public institution; 3=NGO; 4=Firm; 5=Individual firm; 6=Farmer; 7=Individual household; 8=Other; 997=Do not know'),
}
UNIT='nominal current-employer organization category; no inherent order'
STATUS=f'official wave-specific questionnaire/Codebook category wording and employment route reviewed; released storage, re-interview carry-forward, eligible denominator and person linkage require QA; see {REVIEW}'
CAVEAT=('Current employer/work-unit type, retained as a nominal work and socioeconomic context measure. Categories have no inherent order and are not an environmental dose. '
        'Questionnaire wording and coding vary slightly by wave. Re-interview routing can skip employer-detail questions when the same workplace is carried forward; distinguish valid preloaded values, structural skips and missingness in the authorized release. '
        'Confirm eligible current-worker denominator and person linkage before use; do not treat missing or skipped as “no.”')

def norm(p):return re.sub(r'\s+',' ',p.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 for w,(code,qfile,labels) in FIELDS.items():
  q=norm(ROOT/'sources_official'/qfile); cb=(ROOT/'sources_official'/f'CHARLS_{w}_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').casefold()
  if code not in cb:raise ValueError(f'{w} Codebook field {code} missing')
  prompt='what is the type of [ xrname]' if w=='2020' else 'what is the type of your workplace' if w=='2018' else 'do you work for a government organization'
  if prompt not in q:raise ValueError(f'{w} official employer type prompt missing')
  for label in ('government','ngo','farmer','individual household'):
   if label not in q:raise ValueError(f'{w} official response menu missing {label}')
  if w=='2020' and '997. don’t know' not in q and '997. don\u2019t know' not in q:
   if '997.' not in q or 'don' not in q[q.find('997.'):q.find('997.')+80]:raise ValueError('2020 don’t know category not found')

def main():
 validate(); expected={(w,CONCEPT,c.lower()) for w,(c,_,_) in FIELDS.items()}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected:continue
  w=k[0];r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' Categories remain nominal; wave-specific employer carry-forward and skips are not coded as absence.';r['caveat']=CAVEAT;r['unit']=UNIT;seen.add(k)
 if seen!=expected:raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected:continue
  r['Mapping.Status']=STATUS;r['Caveat']=CAVEAT;r['Unit']=UNIT;r['Value.Labels']=FIELDS[k[0]][2];r['Value.Semantics']='official nominal response categories; 2020 code 997 means do not know; frequencies omitted';indexed.add(k)
 if indexed!=expected:raise ValueError(f'E/P source-index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8')); found=set()
 for item in data:
  if item.get('concept_id')!=CONCEPT:continue
  item['caveat']=CAVEAT
  for fld in item.get('source_fields',[]):
   k=(str(fld.get('wave','')),item['concept_id'],str(fld.get('code','')).lower())
   if k not in expected:continue
   w=k[0];fld.update({'mapping_status':STATUS,'note':STATUS,'caveat':CAVEAT,'unit':UNIT,'value_labels':FIELDS[w][2],
    'value_label_status':'Official wave-specific questionnaire/Codebook categories reviewed; frequencies omitted',
    'value_label_source':f"sources_official/{FIELDS[w][1]}; sources_official/CHARLS_{w}_Codebook_extracted.txt"});found.add(k)
 if found!=expected:raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'Reviewed and synchronized {len(expected)} current-employer organization fields.')

if __name__=='__main__':main()
