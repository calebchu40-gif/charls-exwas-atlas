"""Review last-job workplace location, preserving questionnaire/Codebook conflicts."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv';INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv';SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
CONCEPT='last_job_workplace_location_2011_2018';REVIEW='audit/last_job_workplace_location_review_2026-10-25.md';CODE='fl004'
FILES={
 '2011':('CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','1=This village/community; 2=Other village/community in this county/city; 3=Another county/city in this province; 4=Another province'),
 '2013':('CHARLS_2013_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 '2015':('CHARLS_2015_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Another village/neighborhood in permanent address's county/city/district; 3=Other; 4=Abroad"),
 '2018':('CHARLS_2018_Questionnaire_extracted.txt',"1=Same as permanent address; 2=Other village/community in the permanent address's county/city/district; 3=Other domestic location; 4=Abroad"),
}
BASE=('Retrospective self-reported location category for the most recent job. This is coarse historical geographic context, not commute distance, a geocoded address, measured pollution or personal dose. '
      'Keep wave-specific categories and prior-job eligibility routes separate; questionnaire place-name fields are excluded from public metadata. Confirm special values, field storage, prior-job route and eligible denominator in the authorized release.')
STATUSES={
 '2011':f'DO NOT ANALYZE; official questionnaire prints location categories and interviewer code 0 for no fixed address, but the 2011 Codebook does not resolve released-data coding; see {REVIEW}',
 '2013':f'questionnaire/Codebook menu discrepancy: official questionnaire includes 4=Abroad but the Codebook category table omits it; candidate pending authorized-release code validation; see {REVIEW}',
 '2015':f'official 2015 questionnaire and Codebook categories reviewed; release storage, prior-job eligibility and denominator still require QA; see {REVIEW}',
 '2018':f'questionnaire/Codebook menu discrepancy: official questionnaire includes 4=Abroad but the Codebook category table omits it; candidate pending authorized-release code validation; see {REVIEW}',
}

def norm(path):return re.sub(r'\s+',' ',path.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 qtexts={w:norm(ROOT/'sources_official'/qf) for w,(qf,_) in FILES.items()}
 ctexts={w:(ROOT/'sources_official'/f'CHARLS_{w}_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').lower() for w in FILES}
 for w,q in qtexts.items():
  if 'where was the job located' not in q or CODE not in q:raise ValueError(f'{w} FL004 questionnaire item missing')
  if w=='2011' and 'mark 0 if there is no fixed address' not in q:raise ValueError('2011 FL004 no-fixed-address instruction missing')
  if w in {'2013','2015','2018'} and '4. abroad' not in q[q.find('fl004 where was the job located'):q.find('fl004 where was the job located')+1000]:raise ValueError(f'{w} questionnaire Abroad option missing')
 if re.search(r'\bfl004\b',ctexts['2011'],flags=re.IGNORECASE|re.ASCII):raise ValueError('2011 Codebook unexpectedly contains an exact FL004 field; manual review required')
 for w in ('2013','2015','2018'):
  if 'fl004' not in ctexts[w]:raise ValueError(f'{w} Codebook FL004 heading missing')
 if '4 abroad' not in ctexts['2015']:raise ValueError('2015 Codebook Abroad category missing')
 for w in ('2013','2018'):
  i=ctexts[w].find('fl004')
  if '4 abroad' in ctexts[w][i:i+500]:raise ValueError(f'{w} expected Codebook omission of Abroad did not reproduce')

def main():
 validate();expected={(w,CONCEPT,CODE) for w in FILES}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected:continue
  w=k[0];r['mapping_status']=STATUSES[w];r['questionnaire_review']=STATUSES[w]+' Numeric questionnaire options do not establish released-data value coding.';r['unit']='wave-specific retrospective nominal location category';r['caveat']=BASE+(' 2011 code 0 is an interviewer instruction for no fixed address, not an extra location category.' if w=='2011' else ' Codebook omits the questionnaire Abroad option; retain the discrepancy until release-level validation.' if w in {'2013','2018'} else ' 2015 questionnaire and Codebook both list the Abroad category.');seen.add(k)
 if seen!=expected:raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected:continue
  w=k[0];r['Mapping.Status']=STATUSES[w];r['Caveat']=BASE+(' 2011 numeric coding and no-fixed-address code 0 remain unresolved.' if w=='2011' else ' Codebook omits questionnaire option 4=Abroad; verify released coding.' if w in {'2013','2018'} else ' 2015 question and Codebook menus agree.');r['Unit']='wave-specific retrospective nominal location category';r['Value.Labels']=FILES[w][1];r['Value.Semantics']='official questionnaire menu; wave-specific Codebook completeness and released coding noted in Mapping.Status';indexed.add(k)
 if indexed!=expected:raise ValueError(f'E/P index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8'));found=set()
 for item in data:
  if item.get('concept_id')!=CONCEPT:continue
  item['caveat']=BASE+' 2011 coding and 2013/2018 Codebook category omissions remain flagged; do not infer harmonized released values.'
  for fld in item.get('source_fields',[]):
   w=str(fld.get('wave',''));k=(w,CONCEPT,str(fld.get('code','')).lower())
   if k not in expected:continue
   source_status=('Questionnaire categories; Codebook source absent, numeric released coding unverified' if w=='2011' else 'Questionnaire menu includes Abroad; Codebook response-category table omits option 4' if w in {'2013','2018'} else 'Questionnaire and Codebook category menus agree; frequencies omitted')
   fld.update({'mapping_status':STATUSES[w],'note':STATUSES[w],'caveat':BASE+(' 2011 interviewer code 0 is not a location category; released coding unresolved.' if w=='2011' else ' Codebook omits Abroad; preserve the option-menu discrepancy.' if w in {'2013','2018'} else ''),'unit':'wave-specific retrospective nominal location category','value_labels':FILES[w][1],'value_label_status':source_status,'value_label_source':f"sources_official/{FILES[w][0]}"+(f"; sources_official/CHARLS_{w}_Codebook_extracted.txt" if w!='2011' else '')});found.add(k)
 if found!=expected:raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Reviewed four last-job location fields; retained 2011 lock and 2013/2018 Codebook omissions.')

if __name__=='__main__':main()
