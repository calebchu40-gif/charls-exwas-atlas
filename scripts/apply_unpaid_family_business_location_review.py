"""Review unpaid family-business workplace location fields (2011-2018)."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv';INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv';SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
CONCEPT='unpaid_family_business_location_2011_2018';REVIEW='audit/unpaid_family_business_location_review_2026-10-25.md'
FILES={
 '2011':('CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province'),
 '2013':('CHARLS_2013_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 '2015':('CHARLS_2015_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 '2018':('CHARLS_2018_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Other village/community in the permanent address's county/city/district; 3=Other domestic location; 4=Abroad"),
}
CODE='fh013';UNIT='wave-specific nominal location category; no address or distance measure'
STATUS=f'official wave-specific questionnaire/Codebook categories and unpaid-family-business route reviewed; interviewer special code, re-interview carry-forward, eligible denominator and person linkage require QA; see {REVIEW}'
CAVEAT=('Self-reported broad location category for unpaid family-business work, a work-context candidate rather than an environmental dose or personal exposure. Keep wave-specific categories and the unpaid-family-work route separate. '
        '2011 instructs interviewers to enter 0 for no fixed address; that instruction is not an additional location category and requires released-data coding verification. Later-wave re-interview branches may skip details when the same business carries forward. Fine-grained place-name/address fields are excluded from public metadata. Confirm eligible denominator, special values and person linkage before analysis.')

def norm(p):return re.sub(r'\s+',' ',p.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 for w,(filename,labels) in FILES.items():
  q=norm(ROOT/'sources_official'/filename);cb=(ROOT/'sources_official'/f'CHARLS_{w}_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').casefold()
  if 'fh013' not in cb or 'fh013' not in q or 'where is this company or workplace' not in q:raise ValueError(f'{w} official FH013 source missing')
  if w=='2011' and 'mark 0 if there is no fixed address' not in q:raise ValueError('2011 no-fixed-address instruction missing')
  if w=='2018' and not all(x in q for x in ('same as the permanent address','4. abroad')):raise ValueError('2018 FH013 categories missing')

def main():
 validate();expected={(w,CONCEPT,CODE) for w in FILES}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected:continue
  w=k[0];r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' Address/place-name subfields are excluded from the public catalogue.';r['unit']=UNIT;r['caveat']=CAVEAT;seen.add(k)
 if seen!=expected:raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected:continue
  r['Mapping.Status']=STATUS;r['Caveat']=CAVEAT;r['Unit']=UNIT;r['Value.Labels']=FILES[k[0]][1];r['Value.Semantics']='official location categories; no address text or frequencies';indexed.add(k)
 if indexed!=expected:raise ValueError(f'E/P index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8'));found=set()
 for item in data:
  if item.get('concept_id')!=CONCEPT:continue
  item['caveat']=CAVEAT
  for fld in item.get('source_fields',[]):
   k=(str(fld.get('wave','')),item['concept_id'],str(fld.get('code','')).lower())
   if k not in expected:continue
   w=k[0];note=STATUS+(' 2011 interviewer code 0 for no fixed address requires release-level validation.' if w=='2011' else '')
   fld.update({'mapping_status':STATUS,'note':note,'caveat':CAVEAT,'unit':UNIT,'value_labels':FILES[w][1],
    'value_label_status':'Official questionnaire/Codebook categories reviewed; address text and frequencies omitted',
    'value_label_source':f"sources_official/{FILES[w][0]}; sources_official/CHARLS_{w}_Codebook_extracted.txt"});found.add(k)
 if found!=expected:raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'Reviewed and synchronized {len(expected)} unpaid-family business location fields.')

if __name__=='__main__':main()
