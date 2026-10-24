"""Review household-farm and paid-farm location context fields."""
from __future__ import annotations
import csv, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv'; INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv'; SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
REVIEW='audit/agricultural_workplace_context_review_2026-10-25.md'
FILES={
 ('household_agricultural_workplace_location_2011_2018','2011'):('fc012','CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province'),
 ('household_agricultural_workplace_location_2011_2018','2013'):('fc012','CHARLS_2013_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 ('household_agricultural_workplace_location_2011_2018','2015'):('fc012','CHARLS_2015_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 ('household_agricultural_workplace_location_2011_2018','2018'):('fc012','CHARLS_2018_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Other village/community in the permanent address's county/city/district; 3=Other domestic location"),
 ('household_agricultural_workplace_location_2020','2020'):('fb001','CHARLS_2020_Questionnaire_English_extracted.txt','1=Same village/community as current residence; 2=Other village/community in same county/district; 3=Other county/district; 4=Hong Kong, Macao, Taiwan, or abroad; 999=Refuse to answer'),
 ('paid_agricultural_workplace_location_2011_2013','2011'):('fc003','CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province'),
 ('paid_agricultural_workplace_location_2011_2013','2013'):('fc003','CHARLS_2013_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other"),
}
STATUS=f'official wave-specific questionnaire/Codebook categories and work route reviewed; release storage, eligible denominator and person linkage require QA; see {REVIEW}'
CAVEAT=('Coarse self-reported location of household agricultural work or paid work for another farm, according to the distinct concept and route shown for each field. Not a measured environmental concentration, personal dose, commute distance, or validated geocode. '
        'Keep household-farm, paid-farm and wave-specific categories separate. The questionnaire may contain place-name text fields; they are excluded from public metadata. Confirm route, eligible denominator, special values, release identity and person linkage before analysis.')

def norm(p): return re.sub(r'\s+',' ',p.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 for (concept,wave),(code,filename,labels) in FILES.items():
  q=norm(ROOT/'sources_official'/filename); cb=norm(ROOT/'sources_official'/f'CHARLS_{wave}_Codebook_extracted.txt')
  if code not in q or code not in cb: raise ValueError(f'Missing official {wave} source field {code}')
  prompt='where is your workplace' if concept=='paid_agricultural_workplace_location_2011_2013' else ('where is your workplace most of the time' if wave=='2018' else 'where is your workplace for most time' if wave!='2020' else 'where is [xrname]')
  if prompt not in q: raise ValueError(f'Missing {wave} work-location prompt for {code}')
  if wave=='2011' and 'mark 0 if there is no fixed address' not in q: raise ValueError('2011 no-fixed-address instruction missing')
  if wave=='2020' and ('999. refuse' not in q or 'hong kong, macao, taiwan' not in q): raise ValueError('2020 special response categories missing')

def main():
 validate(); expected={(w,cid,vals[0].lower()) for (cid,w),vals in FILES.items()}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f); cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected: continue
  r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' Fine-grained address/place-name subfields are excluded from public output.';r['caveat']=CAVEAT;seen.add(k)
 if seen!=expected: raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f: wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected: continue
  r['Mapping.Status']=STATUS;r['Caveat']=CAVEAT;r['Value.Labels']=FILES[(k[1],k[0])][2];r['Value.Semantics']='official questionnaire/Codebook categories; frequencies and address text omitted';indexed.add(k)
 if indexed!=expected: raise ValueError(f'E/P index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f: wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8')); found=set()
 for item in data:
  if (item.get('concept_id'),) not in {(concept,) for wave,concept,code in expected}: continue
  item['caveat']=CAVEAT
  for field in item.get('source_fields',[]):
   k=(str(field.get('wave','')),item['concept_id'],str(field.get('code','')).lower())
   if k not in expected: continue
   field.update({'mapping_status':STATUS,'note':STATUS,'caveat':CAVEAT,'value_labels':FILES[(k[1],k[0])][2],
    'value_label_status':'Official questionnaire/Codebook categories reviewed; frequencies and address text omitted',
    'value_label_source':f"sources_official/{FILES[(k[1],k[0])][1]}; sources_official/CHARLS_{k[0]}_Codebook_extracted.txt"})
   if k[0]=='2011': field['note'] += ' Interviewer code 0 for no fixed address requires release-level validation.'
   if k[0]=='2020': field['note'] += ' Refusal code 999 is retained separately.'
   found.add(k)
 if found!=expected: raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'Reviewed and synchronized {len(expected)} agricultural workplace location fields.')

if __name__=='__main__': main()
