"""Review 2020 employer-location metadata and correct an unrelated unit label."""
from __future__ import annotations
import csv,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; AUDIT=ROOT/'audit/work_exposure_crosswalk_v1.csv'; INDEX=ROOT/'audit/ep_concept_source_crosswalk_v1.csv'; SITE=ROOT/'site-prototype/dist/work_exposures_v1.json'
CONCEPT='current_workplace_location_relative_to_residence_2020'; CODE='fc004'; WAVE='2020'; REVIEW='audit/current_employer_location_2020_review_2026-10-25.md'
QFILE='CHARLS_2020_Questionnaire_English_extracted.txt'; UNIT='wave-specific nominal workplace location category; not a distance measure'
LABELS='1=Same village/community as current residence; 2=Other village/community in same county/district; 3=Other county/district; 4=Hong Kong, Macao, Taiwan, or abroad; 999=Refuse to answer'
STATUS=f'official 2020 questionnaire/Codebook wording, response labels and current-employer route reviewed; release storage, eligible denominator and person linkage require QA; see {REVIEW}'
CAVEAT=('2020 FC004 asks where the current employer is located, among respondents routed to the employer module. This is coarse self-reported geographic context, not commute distance or measured pollution. '
        'The instrument has conditional place-name fields; they are excluded from public metadata and must not be geocoded without a separate privacy/data-use review. Preserve nominal response categories and 999 refusal separately; verify exact release storage, route, denominator and linkage before analysis.')

def main():
 q=re.sub(r'\s+',' ',(ROOT/'sources_official'/QFILE).read_text(encoding='utf-8',errors='ignore').casefold())
 cb=(ROOT/'sources_official'/'CHARLS_2020_Codebook_extracted.txt').read_text(encoding='utf-8',errors='ignore').casefold()
 for phrase in ('fc004 where is','999. refuse','hong kong, macao, taiwan'):
  if phrase not in q: raise ValueError(f'Missing official questionnaire anchor: {phrase}')
 if CODE not in cb: raise ValueError('2020 Codebook field missing')
 with AUDIT.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f);cols,rows=rd.fieldnames or [],list(rd)
 hit=0
 for r in rows:
  if (r['concept_id'],r['wave'],r['code'].lower())!=(CONCEPT,WAVE,CODE):continue
  r['mapping_status']=STATUS;r['questionnaire_review']=STATUS+' Employer place-name fields are not included in public output.';r['unit']=UNIT;r['caveat']=CAVEAT;hit+=1
 if hit!=1:raise ValueError(f'Expected one domain field, found {hit}')
 with AUDIT.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');wr.writeheader();wr.writerows(rows)
 with INDEX.open(encoding='utf-8-sig',newline='') as f:rd=csv.DictReader(f);icols,irows=rd.fieldnames or [],list(rd)
 hits=0
 for r in irows:
  if (r['Concept.ID'],r['Wave'],r['Source.Code'].lower())!=(CONCEPT,WAVE,CODE):continue
  r['Mapping.Status']=STATUS;r['Caveat']=CAVEAT;r['Unit']=UNIT;r['Value.Labels']=LABELS;r['Value.Semantics']='official 2020 response categories; 999 refusal retained; frequencies omitted';hits+=1
 if hits!=1:raise ValueError(f'Expected one index row, found {hits}')
 with INDEX.open('w',encoding='utf-8-sig',newline='') as f:wr=csv.DictWriter(f,fieldnames=icols,lineterminator='\n');wr.writeheader();wr.writerows(irows)
 data=json.loads(SITE.read_text(encoding='utf-8'));hits=0
 for item in data:
  if item.get('concept_id')!=CONCEPT:continue
  item['caveat']=CAVEAT
  for field in item.get('source_fields',[]):
   if (str(field.get('wave')),str(field.get('code','')).lower())!=(WAVE,CODE):continue
   field.update({'mapping_status':STATUS,'note':STATUS,'caveat':CAVEAT,'unit':UNIT,'value_labels':LABELS,'value_label_status':'Official questionnaire/Codebook categories reviewed; refusal retained, frequencies and address text omitted','value_label_source':f'sources_official/{QFILE}; sources_official/CHARLS_2020_Codebook_extracted.txt'});hits+=1
 if hits!=1:raise ValueError(f'Expected one site field, found {hits}')
 SITE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Reviewed 2020 current employer location and corrected its unit metadata.')

if __name__=='__main__':main()
