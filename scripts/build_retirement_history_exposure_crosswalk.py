"""Add official-questionnaire mappings for CHARLS retirement and post-retirement history."""
from pathlib import Path
import json
import re
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
raw=pd.read_csv(AUDIT/'raw_variable_catalog_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
CONCEPTS={
 'retirement_processed_last_interview':('Retirement or receding processed by last interview','Retirement transition','2018 preload/transition flag; do not interpret as a current-wave general retirement state.'),
 'retirement_processing_unit_relation':('Work unit that processed retirement or receding','Retirement context','Conditional on a retirement/receding history; distinguish current, prior and other work unit routes.'),
 'retirement_processing_unit_type':('Type of retirement-processing work unit','Retirement context','Asked conditionally when the current/last work-unit preload is unavailable or not applicable; response categories are wave-specific.'),
 'retirement_processing_unit_location_relation':('Location relation of retirement-processing work unit','Retirement context','Retains only the broad coded relation to the respondent’s residence. Free-text city/county/village subfields are excluded from this index.'),
 'receding_from_position_timing':('Timing of receding from position','Retirement transition','Year and month are separate components of a conditional reported event. Month 0 can mean not recalled; preserve route and special values.'),
 'receding_from_position_reason':('Main reason for receding from position','Retirement transition','Conditional on receding rather than retirement; reason choices and codes vary by wave, retain source labels.'),
 'pre_receding_monthly_salary':('Salary before receding from position','Retirement resources','2011 questionnaire specifies yuan per month; inspect wave label and unit before pooling. Min/max unfolding brackets are interval components, not separate measures.'),
 'severance_payment_receipt':('Receipt of payment for leaving a job','Retirement resources','Conditional on a retirement/receding route. Not equivalent to pension receipt.'),
 'severance_compensation_amount':('Compensation amount for leaving a job','Retirement resources','Asked only after eligible severance route; keep amount and unfolding bracket components linked.'),
 'pension_receipt_after_job_exit':('Current pension receipt after retirement or receding','Retirement resources','2011 item is route-specific to retirement/receding and should not replace the general pension module.'),
 'pension_benefit_start_date_components':('Pension benefit receipt start date components','Retirement resources','Reported year/month when pension benefits began; retain components, and month 0 means not remembered rather than January.'),
 'retirement_type':('Type of retirement or receding','Retirement transition','Normal, early, internal retirement and receding procedures are distinct; retain source categories.'),
 'retirement_worker_or_cadre_status':('Worker or cadre status at retirement','Retirement context','Retrospective report at the retirement event; do not treat as current occupation.'),
 'revolutionary_retiree_status':('Ordinary or revolutionary retiree category','Retirement context','Historical category present only in early waves; preserve exact wave scope.'),
 'formal_retirement_timing':('Timing of formal retirement','Retirement transition','Reported year/month of completed formal retirement; returned-respondent confirmation fields have a distinct route but refer to the same event. Month 0 may mean not recalled.'),
 'early_retirement_reason':('Reason for early retirement','Retirement transition','Conditional on the early-retirement route; response categories remain wave-specific.'),
 'pre_retirement_salary':('Salary before retirement','Retirement resources','Salary amount before formal/early retirement; units and wave-specific unfolding brackets require codebook review.'),
 'retirement_benefit_type':('Benefit received at retirement','Retirement resources','Retrospective benefit item; retain its reported form and route, separate from monthly pension amount.'),
 'retirement_pension_benefit_source':('Source of pension benefit at retirement','Retirement resources','2011 retirement routes use different source-question formats; preserve route-specific coding. For FM019 checkbox slots, unselected storage is not assumed to mean No.'),
 'pension_benefit_amount_at_retirement':('Pension benefit amount at retirement','Retirement resources','Reported amount when retirement occurred; distinct from the current monthly amount and conditional on the formal/early retirement route.'),
 'current_pension_monthly_amount':('Current monthly pension benefit amount','Retirement resources','Current reported monthly amount including subsidy; conditional on FM010=Yes and the formal/early retirement route in 2011.'),
 'retirement_monthly_pension_amount':('Monthly pension amount at retirement','Retirement resources','Keep monthly benefit amount distinct from retirement-time benefit type and expected future pension.'),
 'eligible_service_years_at_retirement':('Eligible service years at retirement','Retirement context','Retrospective reported service-years measure; retirement subtype and route vary.'),
 'internal_retirement_timing':('Timing of internal retirement','Retirement transition','Conditional on internal-retirement category; year/month are components; month 0 may indicate recall uncertainty.'),
 'internal_retirement_reason':('Reason for internal retirement','Retirement transition','Conditional historical self-report; answer codes must be retained by wave.'),
 'pre_internal_retirement_salary':('Salary before internal retirement','Retirement resources','Reported salary before internal retirement; units/range and interval response must be checked by wave.'),
 'internal_retirement_wage':('Wage when internal retirement was processed','Retirement resources','Separate reported wage at processing from pre-internal-retirement salary; inspect unit and response branch.'),
 'planned_formal_retirement_timing':('Expected timing of future formal retirement','Retirement transition','Expected future date, not observed retirement event; do not merge with completed-retirement date.'),
 'formal_retirement_status_since_prior_wave':('Formal retirement completed since the prior interview','Retirement transition','Returner preload/status field for respondents previously internally retired; route-limited.'),
 'expected_formal_retirement_benefit_amount_or_ratio':('Expected formal-retirement benefit amount or salary ratio','Retirement resources','Original response may combine amount and percentage; do not infer units from a bracket component.'),
 'expected_formal_retirement_benefit_monthly_amount':('Expected monthly formal-retirement benefit amount','Retirement resources','2011 FM038_1 directly records Yuan/month; linked FM039 interval components remain unit-ambiguous because the FM038 selector is absent on bracket rows. Do not combine bounds with reported amounts or salary percentages until resolved.'),
 'expected_formal_retirement_benefit_salary_ratio':('Expected formal-retirement benefit as salary percentage','Retirement resources','2011 percentage component; retain as a proportion/percent, not currency.'),
 'eligible_service_years_for_retirement':('Eligible service years for retirement calculation','Retirement context','Retrospective/predicted eligible service years; distinguish years at retirement from years currently accrued.'),
 'current_eligible_service_years':('Eligible service or contribution years currently accrued','Retirement context','Reported current service/insurance-contribution years; not equivalent to years at the future retirement date.'),
 'spouse_present_at_retirement':('Whether respondent had a spouse at retirement','Family context at retirement','Retrospective family context at the reported retirement event; not current marital status.'),
 'respondent_health_at_retirement':('Respondent-reported health at retirement','Family context at retirement','Retrospective self-rated health at retirement; not a contemporaneous clinical phenotype.'),
 'spouse_retired_before_respondent':('Whether spouse had retired before respondent','Family context at retirement','Retrospective household context at the retirement event; not current spouse status.'),
 'spouse_work_at_respondent_retirement':('Spouse economic activity at respondent retirement','Family context at retirement','Retrospective spouse activity; preserve response categories and conditional route.'),
 'spouse_health_at_respondent_retirement':('Spouse health at respondent retirement','Family context at retirement','Retrospective report about spouse; not respondent’s own phenotype.'),
 'father_alive_at_retirement':('Whether father was alive at respondent retirement','Family context at retirement','Retrospective family context, asked conditionally by wave and route.'),
 'father_health_at_retirement':('Father health at respondent retirement','Family context at retirement','Retrospective report about parent health; not respondent phenotype.'),
 'mother_alive_at_retirement':('Whether mother was alive at respondent retirement','Family context at retirement','Retrospective family context, asked conditionally by wave and route.'),
 'mother_health_at_retirement':('Mother health at respondent retirement','Family context at retirement','Retrospective report about parent health; not respondent phenotype.'),
 'young_grandchildren_at_retirement':('Number of grandchildren under age six at retirement','Family context at retirement','Retrospective count at the reported retirement event; not current household roster count.'),
 'work_after_retirement':('Work after retirement or receding','Post-retirement work','Includes farm, wage, self-employment and unpaid family-business work under the questionnaire definition; not voluntary activity or housework.'),
 'work_in_last_two_years_after_retirement':('Work during the last two years after retirement','Post-retirement work','Distinct recall period from ever working after retirement; keep as its own wave-specific item.'),
 'time_to_resume_work_after_retirement':('Time from retirement to resuming work','Post-retirement work','2018 questionnaire specifies years; earlier-wave wording/units require review. Keep raw source units.'),
 'paid_pastime_work_current':('Current paid pastime work after retirement','Post-retirement work','Questionnaire distinguishes paid pastime/recreational work from unpaid volunteering; wave-specific route.'),
 'pastime_work_occupation_code_gb':('Pastime job occupation code (GB)','Post-retirement work','2011 only; preserve classification version and review detailed code categories before public release.'),
 'pastime_work_occupation_code_isco':('Pastime job occupation code (ISCO)','Post-retirement work','2011 only; keep separate from GB classification and review detailed categories before public release.'),
 'pastime_work_industry_code':('Pastime job industry code','Post-retirement work','2011 only; preserve classification version and review detailed categories before public release.'),
 'pastime_work_start_timing':('Start timing of current pastime work','Post-retirement work','Year/month components describe a reported job start; month 0 may indicate not recalled.'),
 'pastime_work_days_per_week':('Days per week in pastime work','Post-retirement work','Questionnaire specifies an average weekly count; value range and eligible route require review.'),
 'pastime_work_hours_per_week':('Hours per week in pastime work','Post-retirement work','Questionnaire specifies average hours/week; retain as weekly hours and review route.'),
 'pastime_work_monthly_income':('Monthly income from pastime work','Post-retirement work','Questionnaire specifies yuan/month; special values and unfolding brackets must be checked.'),
}
# Exact source codes are listed by questionnaire item. Component fields and
# unfolding brackets are attached to the parent construct with explicit notes.
MAP={
 'fm000_w4':'retirement_processed_last_interview','fm001':'retirement_processing_unit_relation','fm003':'retirement_processing_unit_type','fm004':'retirement_processing_unit_location_relation',
 'fm005_1':'receding_from_position_timing','fm005_2':'receding_from_position_timing','fm006':'receding_from_position_reason','fm007':'pre_receding_monthly_salary','fm008':'severance_payment_receipt','fm009':'severance_compensation_amount','fm010':'pension_receipt_after_job_exit','fm018_1':'pension_benefit_start_date_components','fm018_2':'pension_benefit_start_date_components','fm019s1':'retirement_pension_benefit_source','fm019s2':'retirement_pension_benefit_source','fm019s3':'retirement_pension_benefit_source','fm019s4':'retirement_pension_benefit_source','fm019s5':'retirement_pension_benefit_source','fm020':'pension_benefit_amount_at_retirement','fm021_a':'pension_benefit_amount_at_retirement','fm021_b':'pension_benefit_amount_at_retirement','fm022':'current_pension_monthly_amount','fm023_a':'current_pension_monthly_amount','fm023_b':'current_pension_monthly_amount','fm032_a':'pension_benefit_amount_at_retirement','fm032_b':'pension_benefit_amount_at_retirement','fm033':'retirement_pension_benefit_source','fm034':'current_pension_monthly_amount','fm035_a':'current_pension_monthly_amount','fm035_b':'current_pension_monthly_amount','fm038_1':'expected_formal_retirement_benefit_monthly_amount','fm038_2':'expected_formal_retirement_benefit_salary_ratio','fm039_a':'expected_formal_retirement_benefit_monthly_amount','fm039_b':'expected_formal_retirement_benefit_monthly_amount',
 'fm011':'retirement_type','fm012':'retirement_worker_or_cadre_status','fm013':'revolutionary_retiree_status','fm014_1':'formal_retirement_timing','fm014_2':'formal_retirement_timing','fm015':'early_retirement_reason','fm016':'pre_retirement_salary',
 'fm024':'eligible_service_years_at_retirement',
 'fm025_1':'internal_retirement_timing','fm025_2':'internal_retirement_timing','fm026':'internal_retirement_reason','fm027':'pre_internal_retirement_salary','fm028':'internal_retirement_wage','fm029_a':'internal_retirement_wage','fm029_b':'internal_retirement_wage',
 'fm030_1':'formal_retirement_timing','fm030_2':'formal_retirement_timing','fm036':'eligible_service_years_for_retirement','fm037_1':'planned_formal_retirement_timing','fm037_2':'planned_formal_retirement_timing','fm037_w2':'formal_retirement_status_since_prior_wave','fm038_w2_1':'formal_retirement_timing','fm038_w2_1_1':'formal_retirement_timing','fm038_w2_1_2':'formal_retirement_timing','fm038_w2_2':'formal_retirement_timing','fm040':'eligible_service_years_for_retirement','fm040_w2':'eligible_service_years_for_retirement','fm041':'current_eligible_service_years',
 'fm042':'spouse_present_at_retirement','fm043':'respondent_health_at_retirement','fm044':'spouse_retired_before_respondent','fm045':'spouse_work_at_respondent_retirement','fm046':'spouse_health_at_respondent_retirement','fm047':'father_alive_at_retirement','fm048':'father_health_at_retirement','fm049':'mother_alive_at_retirement','fm050':'mother_health_at_retirement','fm051':'young_grandchildren_at_retirement',
 'fm052':'work_after_retirement','fm052_w2':'work_in_last_two_years_after_retirement','fm053':'time_to_resume_work_after_retirement','fm054':'paid_pastime_work_current','fm055_gb':'pastime_work_occupation_code_gb','fm055_isco':'pastime_work_occupation_code_isco','fm055_indc':'pastime_work_industry_code','fm056_1':'pastime_work_start_timing','fm056_2':'pastime_work_start_timing','fm057':'pastime_work_days_per_week','fm058':'pastime_work_hours_per_week','fm059':'pastime_work_monthly_income',
}
# Unfolding brackets are stored as intervals and stay attached to the amount concept.
BRACKET_PARENT={'fm007':'pre_receding_monthly_salary','fm009':'severance_compensation_amount','fm016':'pre_retirement_salary','fm017':'pre_retirement_salary','fm020':'pension_benefit_amount_at_retirement','fm022':'current_pension_monthly_amount','fm027':'pre_internal_retirement_salary','fm028':'internal_retirement_wage','fm029':'internal_retirement_wage','fm059':'pastime_work_monthly_income'}
DOCS={
 '2011':'sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt',
 '2013':'sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt',
 '2015':'sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt',
 '2018':'sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt',
}
UNITS={
 'fm005_1':'calendar year','fm005_2':'calendar month','fm007':'yuan/month (2011 questionnaire); wave review required','fm020':'yuan/month at retirement, including subsidy (2011 questionnaire)','fm022':'yuan/month current pension, including subsidy (2011 questionnaire)','fm031':'yuan/month at formal retirement (2011 questionnaire)','fm034':'yuan/month current pension (2011 questionnaire; FM011=3 route)','fm038_1':'yuan/month expected in first year of formal retirement','fm038_2':'percent of pre-retirement salary',
 'fm014_1':'calendar year','fm014_2':'calendar month','fm018_1':'calendar year','fm018_2':'calendar month; 0=not remembered','fm025_1':'calendar year','fm025_2':'calendar month',
 'fm030_1':'calendar year','fm030_2':'calendar month','fm037_1':'expected calendar year','fm037_2':'expected calendar month',
 'fm038_w2_1':'calendar year','fm038_w2_1_1':'calendar year','fm038_w2_1_2':'calendar month','fm038_w2_2':'calendar month',
 'fm038_1':'yuan/month (2011 questionnaire)','fm038_2':'percent (2011 questionnaire)','fm024':'eligible service years',
 'fm036':'eligible service years','fm040':'eligible service/contribution years','fm040_w2':'eligible service/contribution years','fm041':'eligible service/contribution years',
 'fm053':'years (2018 questionnaire); earlier waves need review','fm057':'days/week','fm058':'hours/week','fm059':'yuan/month',
}
SPECIAL_STATUS={
}
def main():
 rows=[]
 for rec in raw.itertuples(index=False):
  wave=str(rec.wave); code=str(rec.variable).lower()
  if wave not in DOCS or not code.startswith('fm'): continue
  cid=MAP.get(code)
  if cid is None:
   # Link interval endpoints to their exact parent amount fields without counting as new concepts.
   m=re.match(r'(fm\d{3})',code)
   if m and m.group(1) in BRACKET_PARENT and re.search(r'bracket|min|max',code+' '+str(rec.variable_label),re.I): cid=BRACKET_PARENT[m.group(1)]
  if not cid: continue
  label,domain,caveat=CONCEPTS[cid]
  note='Official questionnaire section FM001–FM059 located; route applies to retirement/receding respondents or wave-specific returners. See review note for exact item scope.'
  status='official variable metadata mapped; questionnaire item family located; conditional route and analysis denominator require review'
  if code == 'fm010':
   note='2011 Baseline Household Questionnaire explicitly asks current pension receipt after confirming processed retirement/receding history (FB011=1 or FB012=1); response is 1=Yes, 2=No. This is not general pension enrollment or a whole-cohort pension measure.'
   status='2011 official questionnaire and Codebook field identity and Yes/No labels verified; conditional retirement/receding denominator retained'
  if code in {'fm038_1','fm038_2'}:
   note='2011 FM038 is asked for respondents with FM011=4 who have not yet completed formal retirement; record first-year expected benefit as either yuan/month (fm038_1) or percent of pre-retirement salary (fm038_2). Keep the two response units separate; the FM038 parent field may encode answer format and requires separate review.'
   status='2011 questionnaire field identity and units verified; conditional future-retirement route retained; parent response-format field remains under review'
  if code in {'fm031','fm032_a','fm032_b'}:
   note='2011 FM011=3 internal-then-formal retirement route. FM031 is explicitly marked No Observations in the Codebook. Controlled local QA confirms FM032 endpoints are paired strings on the FM011=3 route (8 pairs), while the Codebook maximum includes 99,999,996; do not infer a point amount or special-code meaning.'
   status='DO NOT ANALYZE: FM031 has no Codebook observations; FM032 paired bracket endpoints and special-value meaning remain unresolved'
  if code == 'fm033':
   note='2011 FM033 is a single-category pension-source item in the FM011=3 internal-then-formal retirement route. The questionnaire lists Government, Work unit, Social insurance agency, Commercial insurance company, and Other. The Codebook documents observed codes 6=Government, 7=Work unit, 8=Social insurance agency, and 10=Other; controlled local QA confirms all nonblank responses are on the FM011=3 route and use only those four documented codes (125 responses among 126 route-eligible records). The commercial-insurance option has no observed category in the Codebook; do not infer its code or publish a label for an unobserved value. Blank response remains missing.'
   status='2011 questionnaire route and all observed response codes verified; retain route-specific categorical candidate; one questionnaire option has no Codebook observations'
  if code in {'fm034','fm035_a','fm035_b'}:
   note='2011 FM011=3 internal-then-formal retirement route. FM034 asks current monthly pension in Yuan; FM035 is its nonresponse/recall unfolding component. Controlled local QA confirms the two FM035 endpoints are paired strings (2 pairs) on the FM011=3 route, with lower endpoint 0 and upper endpoint 99,999,996, matching the Codebook special/extreme value. Do not derive a numeric amount or infer special-code meaning.'
   if code in {'fm035_a','fm035_b'}: status='DO NOT ANALYZE: paired FM035 bracket endpoints and special-value meaning remain unresolved'
   else: status='2011 questionnaire field identity and yuan/month unit verified; FM011=3 route retained'
  if code in {'fm039_a','fm039_b'}:
   note='2011 questionnaire routes FM037–FM040 to the FM011=4 future-retirement route (or wave-specific returners). FM038 records either Yuan/month or salary percent; FM039 asks an unfolding bracket in Yuan when unwilling/unsure, but the local authorized table has empty FM038 unit selectors on bracket rows. Both bounds are stored as strings and the upper endpoint includes the Codebook extreme value 99,999,996. Keep the candidate link but do not analyze until the bracket unit branch and special-value meaning are confirmed.'
   status='DO NOT ANALYZE; bracket endpoints and extreme code confirmed, but FM038 unit branch and special-value meaning remain unresolved'
  if code in {'fm019s1','fm019s2','fm019s3','fm019s4','fm019s5'}:
   note='2011 FM019 is a choose-all-that-apply pension-benefit-source item. Official question text includes the FM011 normal/early-retirement route and the FM010 current-pension route. Local authorized-table QA confirms selected option-code strings and empty-string nonselections, but some selections fall outside the apparent questionnaire routes; empty strings also conflate unselected and not-asked. Do not infer a binary No or eligible denominator.'
   status='DO NOT ANALYZE; option-code storage confirmed, but route discrepancy and eligible denominator remain unresolved; see audit/pension_2011_fm019_checkbox_storage_review_2026-10-22.md'
  if re.search(r'bracket|min|max',code): note+=' Interval unfolding component of the parent amount; not a separate indicator or point amount.'
  if code in {'fm019s1','fm019s2','fm019s3','fm019s4','fm019s5'}: note+=' The released local prepared table stores the selected option code as a string and uses an empty string otherwise; empty values remain ambiguous between unselected and not-asked.'
  if code.startswith('fm004_'): continue
  if code in SPECIAL_STATUS: continue
  if code in {'fm055_gb','fm055_isco','fm055_indc'}:
   note='2011 questionnaire FM055 asks the respondent to describe the specific paid pastime job in open text; the public index excludes the free-text response. The 2011 Codebook lists separate GB occupation, ISCO occupation, and industry child fields, but does not identify the coding-standard edition or provide a verified category lookup here. CHARLS Wave 4 User Guide describes GB six-digit occupation and two-digit industry coding for a specified set of work-module items and says Wave 4 continued Wave 3 procedures; FM055 is not among the listed items, so those procedures cannot be assumed for this field. Keep the three coded fields separate; classification version, category lookup, and small-cell disclosure review are unresolved. Codebook frequencies are not published.'
   status='candidate only; 2011 FM055 classification edition and lookup unverified; DO NOT ANALYZE until verified'
  unit=UNITS.get(code,'')
  if re.search(r'bracket|min|max',code): unit+='; unfolding interval component' if unit else 'unfolding interval component'
  rows.append({'concept_id':cid,'concept_label':label,'domain':domain,'wave':wave,'code':code,'module':rec.module,'source_label':rec.variable_label,'unit':unit,'source_document':DOCS[wave],'mapping_status':status,'questionnaire_review':note,'caveat':caveat})
 out=pd.DataFrame(rows).drop_duplicates(['wave','code','concept_id'])
 base=pd.read_csv(AUDIT/'work_exposure_crosswalk_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
 # Keep the concept caveat synchronized for the already-existing FM039 rows.
 fm039_mask=base['code'].astype(str).str.lower().isin({'fm039_a','fm039_b'}) & base['wave'].astype(str).eq('2011')
 base.loc[fm039_mask,'caveat']=CONCEPTS['expected_formal_retirement_benefit_monthly_amount'][2]
 # Keep the existing work-history table intact and add only new item mappings.
 merged=pd.concat([base,out],ignore_index=True).drop_duplicates(['wave','code','concept_id'])
 # Explicitly refresh the three existing FM055 rows, whose source review was
 # strengthened after their initial crosswalk entry was created.
 for code in {'fm055_gb','fm055_isco','fm055_indc'}:
  source=out[(out.wave.eq('2011')) & out.code.str.lower().eq(code)]
  target=(merged.wave.eq('2011')) & merged.code.str.lower().eq(code)
  if len(source)==1 and target.sum()==1:
   for column in ['mapping_status','questionnaire_review','caveat','unit']:
    merged.loc[target,column]=source.iloc[0][column]
 merged.to_csv(AUDIT/'work_exposure_crosswalk_v1.csv',index=False,encoding='utf-8-sig')
 items=[]
 for cid,(label,domain,caveat) in CONCEPTS.items():
  fs=out[out.concept_id.eq(cid)]
  if fs.empty: continue
  items.append({'concept_id':cid,'label':label,'domain':domain,'caveat':caveat,'source_fields':[{'wave':str(r.wave),'code':r.code,'module':r.module,'source_label':r.source_label,'unit':r.unit,'source_document':r.source_document,'mapping_status':r.mapping_status,'note':r.questionnaire_review} for r in fs.itertuples()]})
 path=ROOT/'site-prototype'/'dist'/'work_exposures_v1.json'
 old=json.loads(path.read_text(encoding='utf-8'))
 byid={r['concept_id']:r for r in old}
 review_ids={
  'pastime_work_occupation_code_gb',
  'pastime_work_occupation_code_isco',
  'pastime_work_industry_code',
 }
 for item in items:
  # Refresh only the FM055 concepts whose audited status changed. Other
  # retirement concepts may carry downstream reviews that are not encoded in
  # this source builder and must remain intact.
  if item['concept_id'] in review_ids or item['concept_id'] not in byid:
   byid[item['concept_id']]=item
 path.write_text(json.dumps(list(byid.values()),ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'retirement concepts={len(items)}; mappings={len(out)}; waves={out.groupby("wave").size().to_dict()}')
if __name__=='__main__': main()
