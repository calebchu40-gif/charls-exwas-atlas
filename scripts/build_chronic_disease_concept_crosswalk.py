from pathlib import Path
import re, json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'audit'
# Index wording checked against official wave questionnaires. 2020 inserted Parkinson's disease at 13.
legacy=[
('hypertension_diagnosis','医生诊断高血压','Hypertension'),
('dyslipidemia_diagnosis','医生诊断血脂异常','Dyslipidemia'),
('diabetes_high_blood_sugar_diagnosis','医生诊断糖尿病或高血糖','Diabetes or high blood sugar'),
('cancer_diagnosis','医生诊断癌症或恶性肿瘤','Cancer or malignant tumor'),
('chronic_lung_disease_diagnosis','医生诊断慢性肺病','Chronic lung diseases'),
('liver_disease_diagnosis','医生诊断肝病','Liver disease'),
('heart_disease_diagnosis','医生诊断心脏病','Heart attack/coronary heart disease/other heart problems'),
('stroke_diagnosis','医生诊断中风','Stroke'),
('kidney_disease_diagnosis','医生诊断肾病','Kidney disease'),
('digestive_disease_diagnosis','医生诊断胃或其他消化系统疾病','Stomach or other digestive disease'),
('emotional_psychiatric_diagnosis','医生诊断情绪/神经/精神问题','Emotional, nervous, or psychiatric problems'),
('memory_related_disease_diagnosis','医生诊断记忆相关疾病','Memory-related disease'),
('parkinsons_diagnosis','医生诊断帕金森病','Parkinson\'s disease'),
('arthritis_rheumatism_diagnosis','医生诊断关节炎或风湿病','Arthritis or rheumatism'),
('asthma_diagnosis','医生诊断哮喘','Asthma'),
]
# Legacy index 13/14 were arthritis/asthma through 2018; 2020 inserts Parkinson at index 13.
concepts=[]
for idx,(cid,zh,en) in enumerate(legacy,1):
    legacy_idx=idx if idx<=12 else (None if idx==13 else idx-1)
    idx2020=idx
    if idx>=13: idx2020=idx
    if idx==13: legacy_idx=None
    if idx==14: legacy_idx=13
    if idx==15: legacy_idx=14
    caveat=''
    status='not automatically harmonized; questionnaire routing, concept wording and interview type require review'
    if cid=='memory_related_disease_diagnosis':
        caveat='2018 index 12 wording includes Parkinson’s disease as an example; 2020 memory-related disease is index 12 and Parkinson’s disease is a separate index 13.'
    if cid=='parkinsons_diagnosis':
        caveat='2020 has a separate Parkinson’s disease item at index 13; 2018 includes it in the wording/examples for memory-related disease; 2011/2013/2015 have no separate Parkinson’s item.'
        status='separate diagnosis item only in 2020; earlier waves do not provide an equivalent standalone phenotype'
    if cid in {'arthritis_rheumatism_diagnosis','asthma_diagnosis'}:
        caveat='Legacy index 13/14 through 2018; 2020 indices 14/15 because Parkinson’s disease was inserted at index 13.'
    concepts.append({
      'Concept.ID':cid,'Concept.Label.zh':zh,'Concept.Label.en':en,
      '2011_2018.Question.Index':legacy_idx if legacy_idx else '',
      '2020.Question.Index':idx2020,
      '2011_2018.Source.Pattern': f'da007_{legacy_idx}_' if legacy_idx else '',
      '2013_2015.Returner.Confirm.Pattern': f'da007_w2_1_{legacy_idx}_' if legacy_idx else '',
      '2013_2015.Returner.Interval.Diagnosis.Pattern': f'da007_w2_2_{legacy_idx}_' if legacy_idx else '',
      '2020.Source.Pattern':f'da003_{idx}_',
      '2018.Label.Caveat':caveat,
      'Crosswave.Status':status,
      'Primary.Source':'Official CHARLS questionnaires: 2013, 2015, 2018, 2020; see variable mapping audit'
    })

# Prostate illness is an explicit male-only item outside the indexed DA007
# disease list. Keep it separate from prostate cancer site/history.
concepts.append({
    'Concept.ID':'prostate_illness_diagnosis',
    'Concept.Label.zh':'医生诊断前列腺疾病（不含前列腺癌）',
    'Concept.Label.en':'Physician-diagnosed prostate illness (excluding prostate cancer)',
    '2011_2018.Question.Index':'sex-specific item', '2020.Question.Index':'',
    '2011_2018.Source.Pattern':'da029',
  '2013_2015.Returner.Confirm.Pattern':'da029_w2_1 (prior awareness)',
    '2013_2015.Returner.Interval.Diagnosis.Pattern':'da029_w4',
    '2020.Source.Pattern':'',
    '2018.Label.Caveat':'Male respondents only; routing differs for new and returning respondents. The item explicitly excludes prostate cancer. No equivalent standalone item was found in 2020.',
    'Crosswave.Status':'sex-specific candidate; preserve new-respondent diagnosis, returner prior awareness and since-last-wave diagnosis as separate roles',
    'Primary.Source':'Official CHARLS 2011, 2013, 2015, 2018 questionnaires and codebooks; see variable-level mapping audit'
})

legacy_to_cid={i+1:legacy[i][0] for i in range(12)}
legacy_to_cid.update({13:legacy[13][0],14:legacy[14][0]})

cat=pd.read_csv(AUDIT/'raw_variable_catalog_v1.csv',dtype=str,encoding='utf-8-sig').fillna('')
cat=cat[cat.wave.isin(['2011','2013','2015','2018','2020'])]
rows=[]
for r in cat.itertuples(index=False):
    wave=str(r.wave); code=str(r.variable).strip(); lo=code.lower()
    idx=None; role=None; cid=None
    if wave=='2020':
        m=re.fullmatch(r'da003_(\d+)_',lo)
        if m: idx=int(m.group(1)); role='current_wave_doctor_diagnosis'
    else:
        m=re.fullmatch(r'da007_(\d+)_',lo)
        if m: idx=int(m.group(1)); role='doctor_diagnosis_item'
        m=re.fullmatch(r'da007_w2_1_(\d+)_',lo)
        if m and wave in {'2013','2015'}: idx=int(m.group(1)); role='returner_prior_condition_confirmation'
        m=re.fullmatch(r'da007_w2_2_(\d+)_',lo)
        if m and wave in {'2013','2015'}: idx=int(m.group(1)); role='returner_interval_new_diagnosis'
        m=re.fullmatch(r'zda007_(\d+)_',lo)
        if m and wave in {'2013','2015'}: idx=int(m.group(1)); role='prior_wave_physician_diagnosis_preload'
    if idx is None: continue
    if role=='current_wave_doctor_diagnosis':
        if 1<=idx<=15: cid=legacy[idx-1][0]
    else:
        # 2011-2018 legacy code order has 14 conditions, index 12 includes Parkinson only in 2018 wording.
        if 1<=idx<=14: cid=legacy_to_cid.get(idx)
    if not cid: continue
    concept=next(c for c in concepts if c['Concept.ID']==cid)
    rows.append({
      'Source.Wave':wave,'Source.Variable':code,'Source.Label':str(r.variable_label),
      'Source.Module':str(r.module),'Mapping.Role':role,'Concept.ID':cid,
      'Concept.Label.zh':concept['Concept.Label.zh'],
      'Question.Index':idx,
      'Mapping.Status':('official prior-wave preload field; return-interview routing and missing-state semantics retained' if role=='prior_wave_physician_diagnosis_preload' else 'official questionnaire index crosswalk; derivation/routing not yet finalized'),
      'Caveat':concept['2018.Label.Caveat'] if wave=='2018' else '',
      'Source.Archive':str(r.source),
      'Value.Labels':{
          'doctor_diagnosis_item':'1=Yes; 2=No',
          'current_wave_doctor_diagnosis':'1=Yes; 2=No',
          'returner_prior_condition_confirmation':'1=Agree; 2=Disagree',
          'returner_interval_new_diagnosis':'1=Yes; 2=No',
          'prior_wave_physician_diagnosis_preload':('1=Yes; 2=No' if wave=='2013' else '1=Yes')
      }[role],
      'Official.Source':'CHARLS official wave codebook and questionnaire; valid response codes only; route/nonresponse must remain distinct'
    })

# DA009_i is the response-format flag for the accompanying diagnosis/knowledge
# time: official questionnaires/codebooks define 1=Year and 2=Age. It is a
# companion interpretation field, never a standalone disease outcome.
for r in cat.itertuples(index=False):
    wave=str(r.wave); code=str(r.variable).strip(); lo=code.lower()
    m=re.fullmatch(r'da009_(\d+)_',lo)
    if wave not in {'2011','2013','2015','2018'} or not m:
        continue
    idx=int(m.group(1)); cid=legacy_to_cid.get(idx)
    if not cid: continue
    concept=next(c for c in concepts if c['Concept.ID']==cid)
    doc=("sources_official/CHARLS_2011_Codebook_extracted.txt; sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; item DA009"
         if wave=='2011' else f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt; sources_official/CHARLS_{wave}_Codebook_extracted.txt")
    rows.append({
      'Source.Wave':wave,'Source.Variable':code,'Source.Label':str(r.variable_label),
      'Source.Module':str(r.module),'Mapping.Role':'diagnosis_time_response_format_metadata','Concept.ID':cid,
      'Concept.Label.zh':concept['Concept.Label.zh'],'Question.Index':idx,
      'Mapping.Status':'companion response-format metadata; 1=Year, 2=Age; do not treat as a standalone outcome',
      'Caveat':'DA009 asks when the condition was first diagnosed or first known by the respondent. This field selects the unit for its companion year/age response; it is not a diagnosis date or biological onset measure.',
      'Source.Archive':str(r.source),'Value.Labels':'1=Year; 2=Age','Official.Source':doc
    })

# Explicit prostate illness fields are outside DA007's numbered list. The
# baseline/new-respondent status, returner fields and time components remain
# distinct; this does not make the field eligible for every respondent.
prostate_roles={
    'da029':'doctor_diagnosis_item',
    'da029_w2_1':'returner_prior_condition_awareness',
    'da029_w4':'returner_interval_new_diagnosis',
    'da030':'diagnosis_time_response_format_metadata',
    'da030_1':'diagnosis_time_year_component',
    'da030_2':'diagnosis_time_age_component',
    'zda030':'prior_wave_diagnosis_time_response_format_metadata',
}
for r in cat.itertuples(index=False):
    wave=str(r.wave); code=str(r.variable).strip(); role=prostate_roles.get(code.lower())
    if wave not in {'2011','2013','2015','2018'} or role is None: continue
    if role=='returner_interval_new_diagnosis' and wave!='2018': continue
    if role=='returner_prior_condition_confirmation' and wave=='2011': continue
    if role=='prior_wave_diagnosis_time_response_format_metadata' and wave!='2018': continue
    if role=='diagnosis_time_response_format_metadata' and wave=='2011': continue
    labels={
      'doctor_diagnosis_item':'1=Yes; 2=No',
      'returner_prior_condition_awareness':'1=Yes; 2=No; 3=Don’t know',
      'returner_interval_new_diagnosis':'1=Yes; 2=No',
      'diagnosis_time_response_format_metadata':'1=Year; 2=Age',
      'prior_wave_diagnosis_time_response_format_metadata':'1=Year; 2=Age',
      'diagnosis_time_year_component':'','diagnosis_time_age_component':''
    }[role]
    rows.append({
      'Source.Wave':wave,'Source.Variable':code,'Source.Label':str(r.variable_label),
      'Source.Module':str(r.module),'Mapping.Role':role,
      'Concept.ID':'prostate_illness_diagnosis',
      'Concept.Label.zh':'医生诊断前列腺疾病（不含前列腺癌）',
      'Question.Index':'sex-specific',
      'Mapping.Status':'male-only, wave-routed prostate illness; DA029 explicitly excludes prostate cancer',
      'Caveat':'DA029 explicitly excludes prostate cancer. New-respondent diagnosis, prior awareness, since-last-wave diagnosis and year/age response components have distinct routes. Do not infer No from skips or missingness; 2020 has no equivalent standalone item.',
      'Source.Archive':str(r.source),'Value.Labels':labels,
      'Official.Source':f"sources_official/{'CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt' if wave == '2011' else f'CHARLS_{wave}_Questionnaire_English_extracted.txt' if wave == '2020' else f'CHARLS_{wave}_Questionnaire_extracted.txt'}; official codebook DA029/DA030"
    })

cross=pd.DataFrame(concepts)
cross.to_csv(AUDIT/'chronic_disease_concept_crosswalk_v2.csv',index=False,encoding='utf-8-sig')
varmap=pd.DataFrame(rows)
varmap['_module_priority']=~varmap['Source.Module'].str.contains('health_status',case=False,na=False)
varmap=(varmap.sort_values(['_module_priority','Source.Wave','Source.Variable'],kind='stable')
        .drop_duplicates(['Source.Wave','Source.Variable','Concept.ID','Mapping.Role'])
        .drop(columns='_module_priority')
        .sort_values(['Source.Wave','Mapping.Role','Question.Index']))
format_rows=varmap[varmap['Mapping.Role'].eq('diagnosis_time_response_format_metadata') & varmap['Source.Variable'].str.lower().str.startswith('da009_')]
prior_rows=varmap[varmap['Mapping.Role'].eq('prior_wave_physician_diagnosis_preload')]
assert len(format_rows)==56 and set(format_rows['Value.Labels'])=={'1=Year; 2=Age'}
assert len(prior_rows)==28
prostate_rows=varmap[varmap['Concept.ID'].eq('prostate_illness_diagnosis')]
assert len(prostate_rows)==20, len(prostate_rows)
varmap.to_csv(AUDIT/'chronic_disease_concept_variable_mapping_v2.csv',index=False,encoding='utf-8-sig')
# Site uses only this non-participant metadata JSON.
site=[]
for c in concepts:
    aliases=varmap[varmap['Concept.ID'].eq(c['Concept.ID'])]
    source_codes=[]
    for _,a in aliases.iterrows():
        qidx=a['Question.Index']
        try: qidx=int(qidx)
        except (TypeError,ValueError): qidx=str(qidx)
        source_codes.append({'wave':a['Source.Wave'],'code':a['Source.Variable'],'role':a['Mapping.Role'],
                             'source_label':a['Source.Label'],'value_labels':a['Value.Labels'],
                             'question_index':qidx})
    site.append({'concept_id':c['Concept.ID'],'label':c['Concept.Label.zh'],'label_en':c['Concept.Label.en'],
                 'legacy_index':c['2011_2018.Question.Index'],'wave2020_index':c['2020.Question.Index'],
                 'source_fields':source_codes,'status':c['Crosswave.Status'],'caveat':c['2018.Label.Caveat']})
(AUDIT/'chronic_disease_concepts_v2.json').write_text(json.dumps(site,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(ROOT/'site-prototype'/'dist'/'chronic_disease_concepts_v2.json').write_text(json.dumps(site,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print('concepts',len(cross),'observed variable mappings',len(varmap))
print(varmap.groupby(['Source.Wave','Mapping.Role']).size().to_string())
print('missing legacy codes by wave')
for wave in ['2011','2013','2015','2018']:
    got=set(varmap[(varmap['Source.Wave']==wave)&varmap['Mapping.Role'].eq('doctor_diagnosis_item')]['Question.Index'])
    print(wave,'missing',[i for i in range(1,15) if i not in got])
print('2020 missing',[i for i in range(1,16) if i not in set(varmap[(varmap['Source.Wave']=='2020')]['Question.Index'])])

