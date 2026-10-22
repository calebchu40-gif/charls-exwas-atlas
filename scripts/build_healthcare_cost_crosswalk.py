"""Add official-questionnaire candidate fields for healthcare expenditures.

This inventory records field identity only. It never reads respondent-level data or
uses Codebook frequency tables as analysis results.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'audit/raw_variable_catalog_v1.csv'
out_csv = ROOT / 'audit/healthcare_access_crosswalk_v1.csv'
out_json = ROOT / 'site-prototype/dist/healthcare_access_v1.json'
raw = pd.read_csv(source, dtype=str).fillna('')
base = pd.read_csv(out_csv, dtype=str).fillna('')

specs = [
 ('healthcare_cost_annual_premium','Annual out-of-pocket health-insurance premium by plan','Healthcare expenditure phenotype','2011–2015 plan-slot fields. Keep each insurance plan separate; annual nominal amounts are not inflation-adjusted or summed. Eligibility depends on the corresponding insurance plan and premium route.','annual premium amount; nominal currency/year; exact unit and special codes pending', lambda w,c: w in {'2011','2013','2015'} and c.startswith('ea006_')),
 ('healthcare_cost_outpatient_total','Outpatient treatment cost','Healthcare expenditure phenotype','Wave-specific outpatient cost item. 2011 and 2015/2018 refer to a visit; 2013 ED006 refers to costs across visits in its recall period. Do not pool without reconstructing visit period and denominator. Bracket Min/Max fields are response bounds, not independent outcomes.','nominal amount; recall interval and visit aggregation vary by wave', lambda w,c: (w=='2011' and c=='ed023_1') or (w=='2013' and c in {'ed006_1','ed006_bracketbracket_min','ed006_bracketbracket_max'}) or (w=='2015' and c=='ed023_1') or (w=='2018' and c in {'ed023_w4_1','ed023_w4_min','ed023_w4_max'})),
 ('healthcare_cost_outpatient_oop','Outpatient out-of-pocket treatment cost','Healthcare expenditure phenotype','2013 ED007 reports self-paid cost across outpatient visits; 2015 ED024_1 reports out-of-pocket cost at the last outpatient visit. Different recall/aggregation; bracket endpoints remain bounds and must not be treated as exact amounts.','nominal amount; denominator and recall differ by wave', lambda w,c: (w=='2011' and c=='ed024_1') or (w=='2013' and c in {'ed024','ed024_bracketbracket_min','ed024_bracketbracket_max'}) or (w=='2015' and c=='ed024_1') or (w=='2018' and c in {'ed024_1','ed024_min','ed024_max'})),
 ('healthcare_cost_outpatient_medicine_oop','Out-of-pocket medicine cost for outpatient care','Healthcare expenditure phenotype','Medicine-specific out-of-pocket cost. The question position and recall period differ across waves; preserve the official item route. 2013 bracket endpoints are not exact values.','nominal amount; medication-only; wave-specific recall', lambda w,c: (w=='2011' and c=='ed027_1') or (w=='2013' and c in {'ed027','ed027_bracketbracket_min','ed027_bracketbracket_max'}) or (w=='2015' and c=='ed027_1')),
 ('healthcare_cost_inpatient_total','Inpatient medical-care total cost','Healthcare expenditure phenotype','2011–2015 items summarize cost of inpatient care over the past-year module; 2018 Codebook has a total inpatient-cost item. Confirm route, hospitalization count, missing/special values, and whether each release stores all-stay or referenced-stay cost before harmonizing. Bracket bounds are not exact amounts.','nominal amount; annual module or wave-specific inpatient reference', lambda w,c: (w=='2011' and c=='ee005_1') or (w=='2013' and c in {'ee005_1','ee005_bracketbracket_min','ee005_bracketbracket_max'}) or (w=='2015' and c in {'ee005_1','ee005_1_bracket_min','ee005_1_bracket_max'}) or (w=='2018' and c in {'ee005_w4_1','ee005_w4_min','ee005_w4_max'})),
 ('healthcare_cost_inpatient_annual_oop','Out-of-pocket part of past-year inpatient-care cost','Healthcare expenditure phenotype','Past-year self-paid portion of inpatient care, available in Codebook/catalog for 2011, 2013, 2015 and 2018. Keep separate from last-stay OOP items; preserve amount/bounds and annual reference.','nominal amount; past-year inpatient care; route conditional', lambda w,c: (w=='2011' and c=='ee006_1') or (w=='2013' and c in {'ee006_1','ee006_bracketbracket_min','ee006_bracketbracket_max'}) or (w=='2015' and c in {'ee006_1','ee006_1_bracket_min','ee006_1_bracket_max'}) or (w=='2018' and c in {'ee006_1','ee006_min','ee006_max'})),
 ('healthcare_cost_inpatient_last_stay_total','Total medical cost at last inpatient hospitalization','Healthcare expenditure phenotype','Cost of the referenced/last inpatient stay, distinct from past-year all-hospitalization total. Some waves use range brackets; endpoints are not exact amounts. Preserve the route and the specific hospitalization reference.','nominal amount; referenced hospitalization; route conditional', lambda w,c: (w=='2011' and c=='ee024_1') or (w=='2013' and c in {'ee024_1','ee024_bracketbracket_min','ee024_bracketbracket_max'}) or (w=='2015' and c=='ee024_1') or (w=='2018' and c in {'ee024_w4_1','ee024_w4_min','ee024_w4_max'})),
 ('healthcare_cost_inpatient_last_stay_oop','Out-of-pocket cost for inpatient hospitalization','Healthcare expenditure phenotype','Reported out-of-pocket cost for hospitalization. The 2011/2013/2015 items are conditional on the inpatient route; 2015 wording includes paid/will-pay. Do not combine with total cost or medication-only cost.','nominal amount; last-stay or wave-specific hospital cost; route conditional', lambda w,c: (w in {'2011','2013','2015'} and c=='ee027_1') or (w=='2018' and c in {'ee027_1','ee027_min','ee027_max'})),
 ('healthcare_cost_inpatient_medicine_oop','Out-of-pocket medicine cost for inpatient care','Healthcare expenditure phenotype','Medicine-only cost at inpatient care. Preserve the separate medication route and wave-specific reference stay; do not combine with total inpatient out-of-pocket cost.','nominal amount; medicine-only; route conditional', lambda w,c: w in {'2011','2013','2015'} and c=='ee030_1'),
 ('healthcare_cost_inpatient_nonmedical','Transport, food and accommodation cost related to inpatient care','Healthcare expenditure phenotype','Ancillary travel, food and accommodation expenses for patient/relatives, distinct from medical charges and out-of-pocket treatment cost. Route is conditional on the inpatient module.','nominal amount; nonmedical ancillary costs; route conditional', lambda w,c: w in {'2011','2013','2015'} and c=='ee026_1'),
 ('healthcare_cost_outpatient_transport','Transportation cost to outpatient facility','Healthcare expenditure phenotype','Transportation expenditure associated with the outpatient visit; preserve each wave’s visit reference and route. Not a medical treatment charge.','nominal amount; transport cost; reference visit varies by wave', lambda w,c: w in {'2011','2013','2015'} and c=='ed015'),
]


def route_note(cid,wave,code):
    notes={
      'healthcare_cost_annual_premium':'EA006 asks yearly out-of-pocket premium for each insurance plan slot, including main and supplemental premiums; retain plan-specific fields and route to the reported insurance plan.',
      'healthcare_cost_outpatient_total':{
        '2011':'ED023 records total cost of the referenced outpatient visit, including treatment and medication; explicit no-cost response is separate.',
        '2013':'ED006 asks total cost across visits to the selected facility during the past month and is routed only when the sum of ED005 visits exceeds one; do not equate with a single visit.',
        '2015':'ED023_1 records total cost of the last outpatient visit, including treatment and medication; keep the no-cost gate separate.',
        '2018':'ED023_W4 records total cost of the referenced outpatient visit; keep bracket fields and no-cost route distinct.'},
      'healthcare_cost_outpatient_oop':'ED024 asks the respondent-paid amount after insurance reimbursement, conditional on a cost at the referenced visit; this is distinct from gross visit cost.',
      'healthcare_cost_outpatient_medicine_oop':'ED027 is conditional on medicine/prescription route; “no prescription” and “did not fill” are not zero medication cost.',
      'healthcare_cost_inpatient_total':'EE005 asks past-year cost of inpatient care, limited to fees paid to the hospital; preserve any no-cost branch and the annual inpatient route.',
      'healthcare_cost_inpatient_annual_oop':'EE006 asks the self-paid portion after the past-year inpatient cost route; do not treat the amount as total cost.',
      'healthcare_cost_inpatient_last_stay_total':'EE024 asks total medical cost of the referenced/most recent hospitalization; excludes hired-nurse wages and family travel/accommodation, while including hospital/ward fees.',
      'healthcare_cost_inpatient_last_stay_oop':'EE027 asks the amount paid or expected to be paid out of pocket for the referenced hospitalization; preserve paid/will-pay wording and conditional route.',
      'healthcare_cost_inpatient_medicine_oop':'EE030 asks medicine-specific out-of-pocket payment during the referenced hospitalization; it follows medication route and is distinct from EE029 total medication cost.',
      'healthcare_cost_inpatient_nonmedical':'EE026 covers transportation, food and accommodation for the patient/relatives, separate from hospital medical fees. Read-only inspection of the original 2011 baseline DOC confirms that the printed response placeholder is EP026_1 even though the item is EE026; the official CodeBook labels the amount field EE026 1 and the project catalog normalizes it as ee026_1. Treat EP026_1 as a questionnaire placeholder typo, preserve the CodeBook field identity, and verify actual release-file storage before analysis.',
      'healthcare_cost_outpatient_transport':'ED015 records one-way transport cost to the facility (including fuel) and is skipped under the ED014=1 route; retain that eligibility condition.'}
    value=notes.get(cid,'')
    if isinstance(value,dict): value=value.get(wave,'')
    return (' Questionnaire review: '+value) if value else ''

new=[]
for cid,label,domain,caveat,semantics,selector in specs:
    for r in raw.to_dict('records'):
        wave,code=r['wave'],r['variable'].lower()
        if selector(wave,code):
            if wave == '2011':
                questionnaire='sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc'
                pages='Word pp.97–99 (EA insurance premiums)' if code.startswith('ea006') else 'Word pp.100–103 (ED outpatient costs)' if code.startswith('ed') else 'Word pp.105–107 (EE inpatient costs)'
            elif wave == '2013':
                questionnaire='sources_official/CHARLS_2013_Questionnaire.pdf'
                pages='pp.110–112 (EA insurance premiums)' if code.startswith('ea006') else 'pp.116–120 (ED outpatient costs)' if code.startswith('ed') else 'pp.121–124 (EE inpatient costs)'
            elif wave == '2015':
                questionnaire='sources_official/CHARLS_2015_Questionnaire.pdf'
                pages='pp.100–103 (EA insurance premiums)' if code.startswith('ea006') else 'pp.104–108 (ED outpatient costs)' if code.startswith('ed') else 'pp.108–112 (EE inpatient costs)'
            else:
                questionnaire='sources_official/CHARLS_2018_Questionnaire.pdf'
                pages='pp.150–152 (EA insurance)' if code.startswith('ea') else 'pp.154–156 (ED outpatient costs)' if code.startswith('ed') else 'pp.156–158 (EE inpatient costs)'
            qref=f'{questionnaire}, {pages}; Codebook field {code}.'
            new.append(dict(concept_id=cid,concept_label=label,domain=domain,wave=wave,code=code,module=r['module'],source_label=r['variable_label'],mapping_status='Candidate field identified in official wave Codebook/catalog; questionnaire routing, special codes, measurement units and release storage require field-level review; not analysis-ready',catalog_role='p',value_semantics=semantics+route_note(cid,wave,code),questionnaire_reference=qref,caveat=caveat,value_labels='',value_label_status='continuous monetary response; special/missing codes and release storage not yet validated',value_label_source=f'sources_official/CHARLS_{wave}_Codebook_extracted.txt'))

newdf=pd.DataFrame(new).drop_duplicates(subset=['concept_id','wave','code'])
base=base[~base.concept_id.isin([s[0] for s in specs])]
combined=pd.concat([base,newdf],ignore_index=True).fillna('')
combined.to_csv(out_csv,index=False,encoding='utf-8-sig')
items=json.loads(out_json.read_text(encoding='utf-8'))
cost_ids={spec[0] for spec in specs}
items=[item for item in items if item.get('concept_id') not in cost_ids]
for cid,label,domain,caveat,*_ in specs:
 fields=newdf[newdf.concept_id.eq(cid)]
 items.append(dict(concept_id=cid,label=label,domain=domain,caveat=caveat,source_fields=[dict(wave=str(r.wave),code=r.code,module=r.module,source_label=r.source_label,note=r.mapping_status,value_semantics=r.value_semantics,questionnaire_reference=r.questionnaire_reference,value_labels='',value_label_status=r.value_label_status,value_label_source=r.value_label_source) for r in fields.itertuples()]))
out_csv.write_text(combined.to_csv(index=False),encoding='utf-8-sig')
out_json.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'healthcare expenditure concepts={len(specs)} mappings={len(newdf)} by wave={newdf.groupby("wave").size().to_dict()}')
