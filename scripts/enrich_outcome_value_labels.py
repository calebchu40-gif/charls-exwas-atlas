"""Add explicitly reviewed CHARLS outcome codebook labels to generated mappings.
Uses official extracted codebooks and public metadata only; no respondent data.
"""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CODEBOOK=lambda w:f'CHARLS_{w}_Codebook_extracted.txt'

def labels_self_health(w,code):
    if w=='2011' and code=='da001': return '1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor'
    if w=='2011' and code in {'da002','da079'}: return '1=Very good; 2=Good; 3=Fair; 4=Poor; 5=Very poor'
    if w in {'2013','2015'} and code=='da001': return '1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor'
    if w in {'2013','2015'} and code in {'da002','da079'}: return '1=Very good; 2=Good; 3=Fair; 4=Poor; 5=Very poor'
    if w=='2018' and code=='da002': return '1=Very good; 2=Good; 3=Fair; 4=Poor; 5=Very poor'
    if w=='2020' and code=='da001': return '1=Very good; 2=Good; 3=Fair; 4=Poor; 5=Very poor; 997=Don’t know'
    return ''

def labels_self_health_alt(w,code):
    if w in {'2011','2013','2015'} and code=='da080':
        return '1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor'
    return ''

health=pd.read_csv(ROOT/'audit/health_symptom_variable_mapping_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
hjson=ROOT/'site-prototype/dist/health_symptoms_v1.json'; hdata=json.loads(hjson.read_text(encoding='utf-8'))
health_rules=[]
for row in health.to_dict('records'):
    cid,w,code=row['concept_id'],row['wave'],row['code']; lab=''; status='not yet reviewed against full response value labels'
    if cid=='self_rated_health':
        lab=labels_self_health(w,code)
        if w=='2011' and code=='da079': status='response scale verified in official questionnaire; Codebook variable-title conflict retained for review' 
    elif cid=='self_rated_health_alt_scale':
        lab=labels_self_health_alt(w,code)
    elif cid=='health_change' and (w,code) in {('2013','da002_w2_1'),('2015','da002_w2_1'),('2018','da002_w2_1')}:
        lab='1=Better; 2=About the same; 3=Worse'
    elif cid=='chest_pain_symptoms' and w in {'2011','2013'} and code in {'da003','da004'}:
        lab='1=Yes; 2=No'
    elif cid.startswith('codebook_only_sleep_severity_item_') and w=='2011' and code in {'de010','de011','de012'}:
        lab='1=None; 2=Mild; 3=Moderate; 4=Severe; 5=Extreme'
    elif cid in {'who_bodily_pain_severity','who_sleep_difficulty_severity','who_mobility_problem_severity','who_concentration_memory_difficulty','who_breathlessness_severity','who_low_mood_severity'} and w=='2011' and code in {'de001','de002','de003','de004','de005','de006'}:
        lab='1=None; 2=Mild; 3=Moderate; 4=Severe; 5=Extreme'
    elif cid in {'affect_sad_yesterday','affect_lonely_yesterday'} and w=='2013' and code in {'wb06','wb08'}:
        lab='1=Not at all; 2=A little; 3=Somewhat; 4=Quite a bit; 5=Very'
    elif cid=='chewing_difficulty_solid_foods' and w=='2018' and code=='da040_w4_2':
        lab='1=Yes; 2=No; 3=Not Applicable'
    elif cid.startswith('infectious_history_') and w=='2011' and code.startswith('da044s'):
        infection_labels={'1':'Tuberculosis','2':'Hepatitis B','3':'Malaria','4':'Influenza','5':'Rabies','6':'Schistosomiasis','7':'AIDS patients and infectious ones','8':'Encephalitis B','9':'Dysentery','10':'Measles','11':'Brucellosis','12':'Gonorrhea','13':'Syphilis','14':'Others, please specify'}
        n=code.removeprefix('da044s')
        if n in infection_labels: lab=f'{n}={infection_labels[n]} (selected category; unselected/missing code not inferred)'
    elif cid=='pain_presence' and (w,code) in {('2011','da041'),('2015','da041')}:
        lab='1=Yes; 2=No'
    elif cid in {'pain_presence','pain_intensity','pain_yesterday'} and (w,code)==('2013','wb16'):
        lab='1=None; 2=A little; 3=Some; 4=Quite a bit; 5=A lot'
    elif cid=='pain_location' and code.startswith('da042s') and w in {'2011','2013','2015'}:
        site={'1':'Head (Headache)','2':'Shoulder','3':'Arm','4':'Wrist','5':'Fingers','6':'Chest','7':'Stomach (Stomachache)','8':'Back','9':'Waist','10':'Buttocks','11':'Leg','12':'Knees','13':'Ankle','14':'Toes','15':'Neck','16':'Other'}
        n=code.removeprefix('da042s')
        if n in site: lab=f'{n}={site[n]} (selected option; unselected/missing storage code not inferred)'
    elif cid=='pain_location' and ((w=='2018' and code.startswith('da042_s')) or (w=='2020' and code.startswith('da028_s'))):
        site={'1':'Head (Headache)','2':'Shoulder','3':'Arm','4':'Wrist','5':'Fingers','6':'Chest','7':'Stomach (Stomachache)','8':'Back','9':'Waist','10':'Buttocks','11':'Leg','12':'Knees','13':'Ankle','14':'Toes','15':'Neck','16':'Other, please specify'}
        n=code.rsplit('s',1)[-1]
        if n in site: lab=f'0=No; {n}={site[n]}'
    elif cid=='pain_management_measures':
        n=code.rsplit('s',1)[-1]
        options={'1':'Taking Chinese traditional medicine','2':'Taking Western modern medicine','3':'Acupuncture treatment','4':'Professional massage therapy','5':'Other, please specify','6':'None'}
        if n in options:
            lab=(f'0=No; {n}={options[n]}' if w=='2018' else f'{n}={options[n]} (selected option; unselected/missing storage code not inferred)')
    elif cid=='other_important_medical_condition' and code=='da045':
        lab='1=Yes; 2=No'
    elif cid=='pain_presence' and (w,code) in {('2018','da041_w4'),('2020','da027')}:
        lab='1=None; 2=A little; 3=Somewhat; 4=Quite a bit; 5=Very'
    elif cid=='pain_intensity' and (w,code)==('2011','da043'):
        lab='1=Mild; 2=Moderate; 3=Severe'
    elif cid=='pain_intensity' and (w,code)==('2013','wb16'):
        lab='1=None; 2=A little; 3=Some; 4=Quite a bit; 5=A lot'
    elif cid=='pain_intensity' and (w,code) in {('2018','da041_w4'),('2020','da027')}:
        lab='1=None; 2=A little; 3=Somewhat; 4=Quite a bit; 5=Very'
    elif cid in {'vision_distance','vision_near','hearing_quality'} and w in {'2011','2013','2015','2018'}:
        lab='1=Excellent; 2=Very good; 3=Good; 4=Fair; 5=Poor'
        if w in {'2018'} and cid in {'vision_distance','vision_near','hearing_quality'}: lab+='; 997=Don’t know'
    elif cid=='hearing_aid' and (w,code) in {('2011','da038'),('2013','da038'),('2013','zda038'),('2015','da038'),('2015','zda038'),('2018','da038_w4')}:
        lab='1=Yes; 2=No'
    if lab:
        status='official codebook response labels reviewed; routing/special codes noted where documented'
        if cid.startswith('codebook_only_sleep_severity_item_'): status='official codebook response labels reviewed; exact questionnaire item identity unresolved; DO NOT ANALYZE'
        if (w,code)==('2011','da079'): status='official questionnaire response scale verified; Codebook variable-title conflict retained; confirm released data dictionary before analysis'
        if cid=='pain_location' and w in {'2011','2013','2015'}: status+='; positive selected option only, nonselection storage code not inferred'
        if cid=='pain_management_measures' and w in {'2013','2015'}: status+='; positive selected option only, unselected/missing storage code not inferred'
        if cid=='hearing_aid' and code.startswith('zda'): status+='; prior-wave preload/return-interview route, not a new current-wave answer'
        source=(f'sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/{CODEBOOK(w)}' if (w,code)==('2011','da079') else f'sources_official/{CODEBOOK(w)}')
    else: source=''
    health.loc[(health.concept_id==cid)&(health.wave==w)&(health.code==code),'value_labels']=lab
    health.loc[(health.concept_id==cid)&(health.wave==w)&(health.code==code),'value_label_status']=status
    health.loc[(health.concept_id==cid)&(health.wave==w)&(health.code==code),'value_label_source']=source
    health_rules.append(((cid,w,code),lab,status,source))
for c in hdata:
    for f in c['source_fields']:
        key=(c['concept_id'],f['wave'],f['code'])
        found=next((x for x in health_rules if x[0]==key),None)
        if found: f['value_labels'],f['value_label_status'],f['value_label_source']=found[1:]
        else: f.update(value_labels='',value_label_status='not yet reviewed against full response value labels',value_label_source='')
health.to_csv(ROOT/'audit/health_symptom_variable_mapping_v1.csv',index=False,encoding='utf-8-sig')
hjson.write_text(json.dumps(hdata,ensure_ascii=False,indent=2),encoding='utf-8')

# Function limitation items share a four-category response scale in official codebooks.
func=pd.read_csv(ROOT/'audit/functional_concept_variable_mapping_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
fjson=ROOT/'site-prototype/dist/functional_concepts_v1.json'; fdata=json.loads(fjson.read_text(encoding='utf-8'))
func_labels='1=No, I don’t have any difficulty; 2=I have difficulty but can still do it; 3=I have difficulty and need help; 4=I cannot do it'
func_map=[]
for row in func.to_dict('records'):
    wave=row['wave']; lab=func_labels if wave in {'2011','2013','2015','2018','2020'} else ''
    source=f'sources_official/{CODEBOOK(wave)}' if lab else ''
    mask=(func.concept_id==row['concept_id'])&(func.wave==wave)&(func.code==row['code'])
    func.loc[mask,'value_labels']=lab
    func.loc[mask,'value_label_status']='official codebook response labels reviewed; item routing/derived scale remain separate' if lab else 'pending'
    func.loc[mask,'value_label_source']=source
    func_map.append(((row['concept_id'],wave,row['code']),lab,source))
for c in fdata:
    for f in c['source_fields']:
        x=next((x for x in func_map if x[0]==(c['concept_id'],f['wave'],f['code'])),None)
        if x: f.update(value_labels=x[1],value_label_status='official codebook response labels reviewed; item routing/derived scale remain separate',value_label_source=x[2])
func.to_csv(ROOT/'audit/functional_concept_variable_mapping_v1.csv',index=False,encoding='utf-8-sig')
fjson.write_text(json.dumps(fdata,ensure_ascii=False,indent=2),encoding='utf-8')

# CES-D item frequency labels: 2018/2020 special-response codes differ from earlier waves.
mood=pd.read_csv(ROOT/'audit/mood_item_variable_mapping_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
mjson=ROOT/'site-prototype/dist/mood_items_v1.json'; mdata=json.loads(mjson.read_text(encoding='utf-8'))
for i,row in mood.iterrows():
    w=row['wave']; lab='1=Rarely or none (<1 day); 2=Some or a little (1–2 days); 3=Occasionally or a moderate amount (3–4 days); 4=Most or all of the time (5–7 days)'
    if w=='2018': lab='1=Rarely or none (<1 day); 2=Some or a little (1–2 days); 3=Occasionally or a moderate amount (3–4 days); 4=Most of the time (5–7 days); 8=Don’t know; 9=Refused'
    elif w=='2020': lab='1=Rarely or none (<1 day); 2=Some or a little (1–2 days); 3=Occasionally or a moderate amount (3–4 days); 4=Most of the time (5–7 days); 997=Don’t know; 999=Refused'
    mood.loc[i,'value_labels']=lab
    mood.loc[i,'value_label_status']='official codebook item response labels reviewed; no scale score derived'
    mood.loc[i,'value_label_source']=f'sources_official/{CODEBOOK(w)}'
mood.to_csv(ROOT/'audit/mood_item_variable_mapping_v1.csv',index=False,encoding='utf-8-sig')
mmap={(r['concept_id'],r['wave'],r['code']):(r['value_labels'],r['value_label_status'],r['value_label_source']) for r in mood.to_dict('records')}
for c in mdata:
    for f in c['source_fields']:
        lab,status,source=mmap[(c['concept_id'],f['wave'],f['code'])]
        f.update(value_labels=lab,value_label_status=status,value_label_source=source)
mjson.write_text(json.dumps(mdata,ensure_ascii=False,indent=2),encoding='utf-8')
print('health labels',int((health.value_labels!='').sum()),'/',len(health),'functional labels',int((func.value_labels!='').sum()),'/',len(func),'mood labels',int((mood.value_labels!='').sum()),'/',len(mood))
