"""Build a wave-specific health insurance and healthcare-use field directory."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
src=pd.read_csv(ROOT/'audit/raw_variable_catalog_v1.csv',dtype=str).fillna('')
concepts=[
 ('health_insurance_type_status','Health insurance type/status (wave-specific)','Healthcare access / socioeconomic context','Insurance instrument and coding change by wave. 2015 ea001_w3_2_* only indicates continued coverage for plans reported in the previous wave; it is not a complete current-plan inventory. 2020 ba017 is one categorical type field. Do not sum overlapping plan types without checking coding.'),
 ('insurance_history_2015','Validation and between-wave insurance history (2015)','Healthcare access / socioeconomic context','2015-only follow-up fields for prior-wave insurance: verify the previous-wave record and whether the respondent held the preloaded insurance at any time between interviews. The between-wave item is not current-at-interview coverage.'),
 ('outpatient_use','Outpatient care use (recent recall)','Healthcare utilization','Recent-use measure wording/recall varies: hospital last month, past four weeks, and 2018 accept outpatient care. 2020 main respondent module lacks a directly matched routine outpatient-use field in the current catalog; exit interviews describe deceased respondents and are excluded from this living-respondent series.'),
 ('outpatient_visits_by_facility','Outpatient visits by facility type','Healthcare utilization','Counts are facility-specific slots conditional on selected/visited provider types. Facility categories and recall windows may differ by wave. Do not treat blank slots as zero without routing rules.'),
 ('inpatient_use_past_year','Inpatient care in past year','Healthcare utilization','Self-reported inpatient-care occurrence over the past year in 2011–2018. Check same-condition follow-up wording and non-response codes by wave.'),
 ('inpatient_count_past_year','Number of inpatient episodes past year','Healthcare utilization','Count fields are conditional on inpatient-care reporting; preserve special values and routing; not equivalent to nights in hospital.'),
 ('hospital_nights_last_stay','Nights in hospital at last inpatient stay','Healthcare utilization','Duration of the last stay, not total annual inpatient days. Interpret alongside admission and exit date fields; availability is conditional on hospitalization.'),
 ('pandemic_delayed_care','Delayed or unmet medical care during the COVID-19 period (2020)','Healthcare access / pandemic disruption','2020-only retrospective item asking whether needed medical, including dental, care was delayed or not obtained because of the pandemic. Not a general access measure and not comparable to routine utilization without a specific estimand.'),
 ('pandemic_delayed_care_service_type','Types of care delayed or not obtained during the COVID-19 period (2020)','Healthcare access / pandemic disruption','Six separate select-all-that-apply service indicators, asked only after DA009=Yes. Preserve the item-specific selection code and conditional denominator; do not treat unasked fields as No.'),
 ('pandemic_outpatient_visit_reason','Reasons for outpatient care during the COVID-19 period (2020)','Healthcare access / pandemic disruption','Three select-all-that-apply reason indicators for outpatient care; asked for respondents reporting delayed/not obtained outpatient service (DA010 outpatient-service item). Conditional and pandemic-specific.'),
 ('pandemic_delayed_care_reason','Reasons for delaying or not obtaining care during the COVID-19 period (2020)','Healthcare access / pandemic disruption','Five select-all-that-apply reason indicators, asked only after DA009=Yes. Conditional and pandemic-specific; retain each reason separately.'),
]
def keep(cid,w,v):
 v=v.lower()
 if cid=='health_insurance_type_status':
  return ((w in ['2011','2013'] and v.startswith('ea001s')) or
          (w=='2015' and v.startswith('ea001_w3_2_')) or
          (w=='2018' and v.startswith('ea001_w4_s')) or
          (w=='2020' and v=='ba017'))
 if cid=='insurance_history_2015': return w=='2015' and (v.startswith('ea001_w3_1_') or v.startswith('ea001_w3_3_'))
 if cid=='outpatient_use': return w in ['2011','2013','2015','2018'] and v=='ed001'
 if cid=='outpatient_visits_by_facility': return w in ['2011','2013','2015','2018'] and __import__('re').fullmatch(r'ed005_\d+_',v) is not None
 if cid=='inpatient_use_past_year': return w in ['2011','2013','2015','2018'] and v=='ee003'
 if cid=='inpatient_count_past_year': return w in ['2011','2013','2015','2018'] and v=='ee004'
 if cid=='hospital_nights_last_stay': return w in ['2011','2013','2015','2018'] and v=='ee016'
 if cid=='pandemic_delayed_care': return w=='2020' and v=='da009'
 if cid=='pandemic_delayed_care_service_type': return w=='2020' and __import__('re').fullmatch(r'da010_s[1-6]',v) is not None
 if cid=='pandemic_outpatient_visit_reason': return w=='2020' and __import__('re').fullmatch(r'da011_s[1-3]',v) is not None
 if cid=='pandemic_delayed_care_reason': return w=='2020' and __import__('re').fullmatch(r'da012_s[1-5]',v) is not None
 return False
def semantics(cid,w):
 if w=='2011':
  refs={'health_insurance_type_status':'EA001 is a multi-select current health-insurance policy-holder/primary-beneficiary list; keep selected plan indicators separate.',
        'outpatient_use':'ED001 asks about outpatient care during the last month, including facility visits and home visits by a health worker/doctor; ED002 adds a separate recent-illness route.',
        'outpatient_visits_by_facility':'ED004 selects facility types visited for outpatient treatment in the last 4 weeks; ED005 asks visit counts in the last month for each selected facility. ED006 is conditional on total ED005 >1.',
        'inpatient_use_past_year':'EE003 asks whether inpatient care was received in the past year; No skips to EF001.',
        'inpatient_count_past_year':'EE004 asks the number of inpatient-care episodes in the past year; one episode skips to EE007.',
        'hospital_nights_last_stay':'EE016 asks nights hospitalized for the most recent stay; it is not annual inpatient nights.'}
  return refs.get(cid,'2011 codebook/catalog candidate; check the baseline questionnaire route before analysis.')
 if cid=='health_insurance_type_status' and w=='2011': return '2011 EA001 is a multi-select plan list; no-insurance cannot be selected with another plan. Retain original plan indicators.'
 if cid=='health_insurance_type_status' and w=='2013': return '2013 EA001 is a multi-select primary-beneficiary plan list; no-insurance cannot be selected with a specific plan. Keep plan categories separate.'
 if cid=='health_insurance_type_status' and w=='2015': return 'EA001_W3_2_* only asks whether the respondent still held each plan preloaded from the prior wave; it does not enumerate all current plans.'
 if cid=='insurance_history_2015': return 'EA001_W3_1_* checks whether prior-wave preloaded insurance was correctly reported; EA001_W3_3_* asks whether the respondent held that preloaded plan at any time between interviews. Neither alone is a complete current coverage measure.'
 if cid=='health_insurance_type_status' and w=='2020': return 'BA017 categories: 1 urban employee; 2 urban/rural resident; 3 urban resident; 4 new cooperative medical; 5 government medical; 6 other. Single category (not multi-select); IWER may consult children/village cadres if respondent does not know.'
 if cid=='outpatient_use' and w in ['2011','2013','2015','2018']: return 'Questionnaire: in the last month, visited a public/private hospital, public health center, clinic, or health worker/doctor practice, or received a home visit for outpatient care; 2018 explicitly excludes physical examination. Yes=1, No=2 in 2011–2015 and 2018 codebook; eligibility/routing differs.'
 if cid=='inpatient_use_past_year' and w in ['2011','2013','2015','2018']: return 'Questionnaire: received inpatient care during the past year. Yes=1, No=2 in codebooks; no routes onward. 2011–2018 Part II interviewer instruction prohibits proxy responses.'
 if cid=='outpatient_visits_by_facility': return 'Facility-specific visit count slot; slot suffix must be interpreted with same-wave ed004 provider-type categories.'
 if cid in ['inpatient_use_past_year','inpatient_count_past_year']: return 'Past-year inpatient care/episode count; preserve codebook special values and route-conditioned missingness.'
 if cid=='hospital_nights_last_stay': return 'Nights at the last inpatient stay; duration of last stay only, not annual total.'
 if cid=='pandemic_delayed_care': return '2020 DA009: whether needed medical (including dental) care was delayed/not obtained because of COVID-19 impact; 1=Yes, 2=No. Pandemic-specific, 2020 only.'
 if cid=='pandemic_delayed_care_service_type': return '2020 DA010 select-all-that-apply service type, conditional on DA009=Yes. Item-specific code equals the selected option; 0=No and suffix code=Yes for the corresponding service. Do not infer No from structural missingness.'
 if cid=='pandemic_outpatient_visit_reason': return '2020 DA011 select-all-that-apply reasons for outpatient care; conditional on reporting delayed/not obtained outpatient care. 0=No; option-number code=Yes. Keep separate from DA012 delay reasons.'
 if cid=='pandemic_delayed_care_reason': return '2020 DA012 select-all-that-apply reasons for delaying/not obtaining care; conditional on DA009=Yes. 0=No; option-number code=Yes. Keep separate from service types and outpatient-care reasons.'
 return 'See source label; verify exact wave wording, recall interval, value labels and routing in official questionnaire/codebook.'
def question_ref(cid,w):
 if w=='2011':
  pages={'health_insurance_type_status':'Word p.97, EA001', 'outpatient_use':'Word p.100, ED001–ED002',
         'outpatient_visits_by_facility':'Word p.100, ED004–ED006',
         'inpatient_use_past_year':'Word p.105, EE003', 'inpatient_count_past_year':'Word p.105, EE004',
         'hospital_nights_last_stay':'Word p.107, EE016'}
  return 'sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc; '+pages.get(cid,'see question ID in the official baseline questionnaire')
 if w=='2013':
  if cid=='health_insurance_type_status': return '2013 Questionnaire, p.110 (Part I Medical Insurance; primary beneficiary, select all that apply).'
  if cid=='outpatient_use' or cid=='outpatient_visits_by_facility': return '2013 Questionnaire, pp.116–118 (outpatient recent-month use and provider-specific counts).'
  if cid=='inpatient_use_past_year' or cid=='inpatient_count_past_year': return '2013 Questionnaire, pp.121–122 (past-year inpatient occurrence and episode count); Part II excludes proxy responses.'
  return '2013 Questionnaire, pp.122–124 (last-stay details including nights); Part II excludes proxy responses.'
 if w=='2015':
  if cid=='health_insurance_type_status' or cid=='insurance_history_2015': return '2015 Questionnaire, pp.100–101 (preload confirmation/current continuation/between-wave coverage branches).'
  if cid=='outpatient_use' or cid=='outpatient_visits_by_facility': return '2015 Questionnaire, pp.104–106 (past-month outpatient use and provider-specific counts).'
  if cid=='inpatient_use_past_year' or cid=='inpatient_count_past_year': return '2015 Questionnaire, pp.108–110 (past-year inpatient occurrence and episode count); Part II excludes proxy responses.'
  return '2015 Questionnaire, pp.110–112 (last-stay details including nights); Part II excludes proxy responses.'
 if w=='2018':
  if cid=='health_insurance_type_status': return '2018 Questionnaire, pp.150–152 (current insurance, select all that apply).'
  if cid=='outpatient_use' or cid=='outpatient_visits_by_facility': return '2018 Questionnaire, pp.154–156 (last-month outpatient use, excludes physical examinations; facility categories reference last 4 weeks).'
  if cid=='inpatient_use_past_year' or cid=='inpatient_count_past_year': return '2018 Questionnaire, pp.156–157 (past-year inpatient occurrence and episode count); Part II excludes proxy responses.'
  return '2018 Questionnaire, pp.157–158 (last-stay details including nights); Part II excludes proxy responses.'
 if w=='2020' and cid=='health_insurance_type_status': return '2020 English Questionnaire, p.11, BA017; six plan categories; interviewer may consult family/village cadres if unknown.'
 if w=='2020' and cid.startswith('pandemic_'): return '2020 English Questionnaire, pp.29–30, DA009–DA012; value codes checked against CHARLS 2020 Codebook.'
 return 'Official questionnaire page not yet confirmed.'
rows=[]
for cid,label,domain,caveat in concepts:
 for _,r in src.iterrows():
  if keep(cid,r.wave,r.variable):
   rows.append(dict(concept_id=cid,concept_label=label,domain=domain,wave=r.wave,code=r.variable,module=r.module,source_label=r.variable_label,mapping_status='Codebook/catalog candidate; wave-specific wording/routing review required',value_semantics=semantics(cid,r.wave),questionnaire_reference=question_ref(cid,r.wave),caveat=caveat))
out=pd.DataFrame(rows).drop_duplicates()
out.to_csv(ROOT/'audit/healthcare_access_crosswalk_v1.csv',index=False,encoding='utf-8-sig')
items=[]
for cid,label,domain,caveat in concepts:
 fields=out[out.concept_id.eq(cid)]
 items.append(dict(concept_id=cid,label=label,domain=domain,caveat=caveat,source_fields=[dict(wave=str(x.wave),code=x.code,module=x.module,source_label=x.source_label,note=x.mapping_status,value_semantics=x.value_semantics,questionnaire_reference=x.questionnaire_reference) for x in fields.itertuples()]))
(ROOT/'site-prototype/dist/healthcare_access_v1.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'concepts={len(items)} field mappings={len(out)} by concept={out.groupby("concept_id").size().to_dict()} by wave={out.groupby("wave").size().to_dict()}')
