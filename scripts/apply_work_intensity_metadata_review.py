"""Review employed-work days/week and hours/day metadata, retaining wave rules."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv'; INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv'; SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
REVIEW='audit/employed_work_intensity_review_2026-10-25.md'
FILES={
 '2011':('CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt','fe002','fe003'),
 '2013':('CHARLS_2013_Questionnaire_extracted.txt','fe002','fe003'),
 '2015':('CHARLS_2015_Questionnaire_extracted.txt','fe002','fe003'),
 '2018':('CHARLS_2018_Questionnaire_extracted.txt','fe002','fe003'),
 '2020':('CHARLS_2020_Questionnaire_English_extracted.txt','fc026','fc027'),
}
CONCEPTS={'employed_days_per_week':(1,'days per week'),'employed_hours_per_day':(2,'hours per working day')}
STATUS=f'official wave-specific questionnaire/Codebook numeric measure, unit and applicable work rule reviewed; authorized-release storage and eligible denominator require QA; see {REVIEW}'
BASE_CAVEAT=('Past-year average for wage-employment work, not a direct environmental exposure or validated measure of physical workload. Keep days/week separate from hours/working day; these marginal averages do not identify daily schedules, intensity, unpaid work or occupation. '
             'The item belongs to the wage-employment workplace route; dispatch and payor references may vary. Confirm current/last-year employment eligibility, special values and person linkage in the authorized release. Cross-wave equality of units does not establish measurement equivalence.')

def field_caveat(concept,wave):
 text=BASE_CAVEAT
 if concept=='employed_days_per_week' and wave=='2018':text+=' Irregular weekly days may be derived from annual working days divided by working months and four; retain this stated derivation context.'
 if concept=='employed_days_per_week' and wave=='2020':text+=' Weeks with paid vacations and fully paid sick leave are excluded; when work is fewer than four days per month and the average is below one day per week, interviewers are instructed to enter 1.'
 return text

def norm(p):return re.sub(r'\s+',' ',p.read_text(encoding='utf-8',errors='ignore').casefold())
def validate():
 for wave,(qfile,days,hours) in FILES.items():
  q=norm(ROOT/'sources_official'/qfile);cb=(ROOT/'sources_official'/f'CHARLS_{wave}_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').casefold()
  for code,unit in ((days,'days a week'),(hours,'hours did')):
   if code not in cb:raise ValueError(f'{wave} Codebook field {code} missing')
   pos=q.find(code)
   if pos<0:raise ValueError(f'{wave} questionnaire field {code} missing')
   section=q[pos:pos+900]
   if unit not in section:raise ValueError(f'{wave} {code} unit/question wording missing')
  if wave=='2018' and 'working days in a week can be imputed' not in q:raise ValueError('2018 irregular-day conversion note missing')
  if wave=='2020':
   if 'weeks exclude paid vacations and sick leave fully paid' not in q:raise ValueError('2020 days/week paid leave exclusion missing')
   if 'less than four days per month' not in q:raise ValueError('2020 low-frequency workday interviewer instruction missing')

def main():
 validate();expected={(wave,cid,FILES[wave][idx]) for cid,(idx,unit) in CONCEPTS.items() for wave in FILES}
 caveats={cid:BASE_CAVEAT+(' Hours exclude meal breaks and include paid or unpaid overtime where specified.' if cid=='employed_hours_per_day' else '') for cid in CONCEPTS}
 with AUDIT.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 seen=set()
 for r in rows:
  k=(r['wave'],r['concept_id'],r['code'].lower())
  if k not in expected:continue
  idx=CONCEPTS[k[1]][0];r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' No categorical response labels are fabricated for numeric inputs.';r['unit']=CONCEPTS[k[1]][1];r['caveat']=field_caveat(k[1],k[0]);seen.add(k)
 if seen!=expected:raise ValueError(f'Domain crosswalk mismatch: {expected-seen}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 indexed=set()
 for r in irows:
  k=(r['Wave'],r['Concept.ID'],r['Source.Code'].lower())
  if k not in expected:continue
  cid=k[1];r['Mapping.Status']=STATUS;r['Caveat']=field_caveat(cid,k[0]);r['Unit']=CONCEPTS[cid][1];r['Value.Labels']='';r['Value.Semantics']='continuous numeric response; units and special survey rules reviewed; no categories inferred';indexed.add(k)
 if indexed!=expected:raise ValueError(f'E/P index mismatch: {expected-indexed}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8'));found=set()
 for item in data:
  cid=item.get('concept_id')
  if cid not in CONCEPTS:continue
  item['caveat']=caveats[cid]
  for fld in item.get('source_fields',[]):
   k=(str(fld.get('wave','')),cid,str(fld.get('code','')).lower())
   if k not in expected:continue
   wave=k[0];idx=CONCEPTS[cid][0]
   fld.update({'mapping_status':STATUS,'note':STATUS,'caveat':field_caveat(cid,wave),'unit':CONCEPTS[cid][1],'value_labels':'',
    'value_label_status':'continuous numeric input; no categorical labels assigned',
    'value_label_source':f"sources_official/{FILES[wave][0]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"});found.add(k)
 if found!=expected:raise ValueError(f'Site payload mismatch: {expected-found}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(f'Reviewed and synchronized {len(expected)} employed-work intensity fields.')

if __name__=='__main__':main()
