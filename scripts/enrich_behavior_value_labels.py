"""Attach verified smoking/alcohol codebook labels to behavior field mappings."""
from pathlib import Path
import json,re
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BOOK=lambda w:f'sources_official/CHARLS_{w}_Codebook_extracted.txt'
QUESTIONNAIRE={
 '2011':('CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt',{}),
 '2013':('CHARLS_2013_Questionnaire_extracted.txt',{'da066':3227,'da049':3029,'da050':3033,'da073':3282,'da075':3296,'da075_1':3296,'da075_2':3296,'da077':3311}),
 '2015':('CHARLS_2015_Questionnaire_extracted.txt',{'da049':2429,'da050':2433,'da073':2684,'da075':2698,'da075_1':2698,'da075_2':2698,'da077':2713}),
 '2018':('CHARLS_2018_Questionnaire_extracted.txt',{'da049':2941,'da050':2945,'da073':3158,'da075':3173,'da075_1':3173,'da075_2':3173,'da077':3189}),
 '2020':('CHARLS_2020_Questionnaire_English_extracted.txt',{'da030':1100,'da031':1104}),
}
def questionnaire_source(w,c):
    if c=='da064':
        filename={'2011':'CHARLS_2011_Baseline_Household_Questionnaire.doc','2013':'CHARLS_2013_Questionnaire_extracted.txt','2015':'CHARLS_2015_Questionnaire_extracted.txt'}.get(w,'')
        if filename: return f'sources_official/{filename}; DA064 (price per pack of 20 cigarettes; prompt specifies reference-time rather than current price)'
    if w=='2011':
        pages={'da058':'Word p.73','da060':'Word p.73','da061':'Word p.74','da064':'Word p.74','da067':'Word p.74','da073':'Word p.75','da075':'Word p.76','da075_1':'Word p.76','da075_2':'Word p.76'}
        page=pages.get(c,'question page not yet indexed')
        return f'sources_official/CHARLS_2011_Baseline_Household_Questionnaire.doc; {c.upper()}, {page}'
    filename,lines=QUESTIONNAIRE[w]
    line=lines.get(c)
    return f'sources_official/{filename}:L{line}' if line else ''
frequency='1=Once a month; 2=2–3 times a month; 3=Once a week; 4=2–3 times a week; 5=4–6 times a week; 6=Once a day; 7=Twice a day; 8=More than twice a day'
products='1=Smoking a pipe; 2=Smoking self-rolled cigarettes; 3=Filtered cigarette; 4=Unfiltered cigarette; 5=Cigar; 6=Water cigarettes'
def code(cid,w,c):
    if cid=='smoking_status':
        if c in {'da059','da046'}: return '1=Yes; 2=No'
        if (w,c) in {('2011','da061'),('2013','da061'),('2018','da061')}: return '1=Still smoking; 2=Quit'
        if (w,c)==('2015','da061'): return '1=Still smoking; 2=Quit; 3=Never smoked'
        if (w,c) in {('2015','da061_w3'),('2018','da061_w4'),('2020','da047')}: return '1=Still smoking; 2=Quit; 3=Never smoked'
    if cid=='smoking_product':
        if (w,c) in {('2011','da060'),('2018','da060'),('2020','da048')}: return products
        if w=='2015' and re.fullmatch(r'da060s[1-6]',c):
            names={1:'Pipe',2:'Self-rolled cigarettes',3:'Filtered cigarette',4:'Unfiltered cigarette',5:'Cigar',6:'Water cigarettes'}
            return f'{c[-1]}={names[int(c[-1])]} (selected option; nonselection code not inferred)'
    if cid=='smoking_dependence' and c=='da066' and w in {'2011','2013'}:
        return '1=Within 5 minutes; 2=Within 6–30 minutes; 3=Within 31–60 minutes; 4=More than 1 hour'
    if cid=='smoking_quantity' and c in {'da063','da050_1','da050_2'}:
        return None
    if cid=='cigarette_price_per_pack' and c=='da064':
        return None
    if cid=='smoking_initiation_cessation' and c=='da065':
        return ('1=Age; 2=Year' if w in {'2011','2013','2015'} else
                '1=Year; 2=Age' if w=='2018' else None)
    if cid=='smoking_initiation_cessation' and c in {'da062','da049'} and w in {'2013','2015','2018','2020'}:
        return '1=Year; 2=Age' if w=='2018' else '1=Age; 2=Year'
    if cid=='alcohol_recent' and c in {'da067','da051'}:
        return '1=Drink more than once a month; 2=Drink but less than once a month; 3=None of these'
    if cid=='alcohol_history' and c=='da069':
        return '1=Never had a drink; 2=Used to drink less than once a month; 3=Used to drink more than once a month'
    if cid=='alcohol_morning_drink' and c=='da078' and w in {'2011','2013'}:
        return '1=Yes; 2=No'
    if cid=='alcohol_prior_wave_frequency' and w=='2018' and c=='zda069':
        return '1=Never; 2=Less than once a month; 3=More than once a month (prior-wave preload)'
    if cid=='smoking_prior_wave_status' and c=='zda059' and w in {'2013','2015'}:
        return '1=Yes; 2=No (prior-interview preload)'
    if cid in {'smoking_prior_wave_ever','smoking_last_interview_status'} and c=='zsmoke':
        return '1=Yes (positive prior-interview preload only; absence is not inferred as No)'
    if cid=='alcohol_type':
        if w=='2018' and re.fullmatch(r'da068_s[123]',c):
            n=int(c[-1]); cat={1:'Liquor, including white liquor/whisky/others',2:'Beer',3:'Wine or rice wine'}[n]
            return f'0=No; {n}={cat}'
        if w in {'2011','2013','2015'} and re.fullmatch(r'da068s[123]',c):
            n=int(c[-1]); cat={1:'Liquor, including white liquor/whisky/others',2:'Beer',3:'Wine or rice wine'}[n]
            return f'{n}={cat} (selected option; nonselection code not inferred)'
    if cid=='alcohol_frequency_amount' and ((w in {'2011','2013','2015','2018'} and c in {'da072','da074','da076'}) or (w=='2020' and c=='da052')):
        return frequency
    if cid=='alcohol_frequency_amount' and w in {'2011','2013','2015','2018'} and c=='da075':
        return '1=Bottles; 2=Mugs (beer serving unit selection)'
    if cid=='physical_activity_occurrence':
        return '1=Yes; 2=No'
    if cid=='physical_activity_purpose' and c in {'da051_1_1_','da051_1_2_','da051_1_3_','da037_1_','da037_2_','da037_3_'}:
        return {
            '2015':'1=Job Demands; 2=Entertainments; 3=Exercise; 4=Other',
            '2018':'1=Job Demands; 2=Entertainment; 3=Exercise; 4=Other',
            '2020':'1=Job Demands; 2=Entertainment; 3=Exercise; 4=Others, Please Specify',
        }.get(w)
    if cid=='physical_activity_days':
        return '1–7=Number of days in the past week; days asked only on the activity route'
    if cid=='physical_activity_duration':
        if c.startswith('da053_'): return '1=<2 hours; 2=≥2 hours'
        if c.startswith('da054_'): return '1=<30 minutes; 2=≥30 minutes'
        if c.startswith('da055_') or c.startswith('da036_'): return '1=<4 hours; 2=≥4 hours'
        if c.startswith('da034_'): return '1=<2 hours; 2=≥2 hours'
        if c.startswith('da035_'): return '1=<30 minutes; 2=≥30 minutes'
    if cid=='alcohol_start_stop' and w in {'2011','2013','2015','2018'} and c in {'da070','da071'}:
        return '1=Age; 2=Year' if w=='2011' else '1=Year; 2=Age'
    return None

p=ROOT/'audit/behavior_exposure_variable_mapping_v1.csv'; d=pd.read_csv(p,dtype=str,encoding='utf-8-sig').fillna('')
for col in ['value_labels','value_label_status','value_label_source','value_semantics','questionnaire_source']:
    if col not in d.columns: d[col]=''
for i,r in d.iterrows():
    cid,w,c=r['concept_id'],r['wave'],r['code']; lab=code(cid,w,c)
    if cid=='smoking_initiation_cessation' and w=='2011' and c in {'da062s1','da062s2'}:
        marker='1=Age' if c=='da062s1' else '2=Year'
        d.loc[i,'value_labels']=marker
        d.loc[i,'value_label_status']='official component-type marker reviewed; Codebook lists a fixed Age/Year marker, not the respondent’s cessation time'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='C metadata marker for the adjacent continuous DA062 age/year response fields; not an exposure or a respondent-reported cessation age/year.'
        d.loc[i,'mapping_status']='C metadata; fixed component-type marker only; the respondent’s continuous cessation time is stored separately in da062_1 or da062_2'
        d.loc[i,'questionnaire_source']='sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; DA062 specifies age in da062_1 or calendar year in da062_2 and does not describe an s1/s2 response'
        continue
    if cid=='smoking_initiation_cessation' and w=='2018' and c in {'da062_1','da062_2'}:
        d.loc[i,'value_labels']=''
        d.loc[i,'value_label_status']='DO NOT ANALYZE; official 2018 Questionnaire and Codebook assign opposite age/year meanings to the component'
        d.loc[i,'value_label_source']='sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3089-L3090; sources_official/CHARLS_2018_Codebook_extracted.txt:L43140-L43158'
        d.loc[i,'value_semantics']='Questionnaire: DA062_1=Age, DA062_2=Year; Codebook: DA062_1=Year, DA062_2=Age. Preserve unresolved source conflict.'
        d.loc[i,'questionnaire_source']='sources_official/CHARLS_2018_Questionnaire_extracted.txt:L3089-L3090'
        d.loc[i,'mapping_status']='DO NOT ANALYZE; official 2018 Questionnaire and Codebook assign opposite age/year meanings to this component'
        continue
    if lab is not None:
        d.loc[i,'value_labels']=lab
        d.loc[i,'value_label_status']='official codebook response labels reviewed; routing/measurement definition retained separately'
        d.loc[i,'value_label_source']=BOOK(w)
        if cid=='smoking_initiation_cessation' and c in {'da065','da062','da049'}:
            d.loc[i,'value_label_status']='official selector code reviewed; selects whether the following component is age or calendar year, with order changing in 2018'
            d.loc[i,'value_semantics']='Selector only; interpret paired cessation/initiation component fields using wave-specific code order. Do not analyze as an ordinal exposure.'
            if c in {'da062','da049'}:
                d.loc[i,'mapping_status']='C metadata; smoking-cessation age/year response-format selector; use only to interpret its paired time component'
                if w=='2018':
                    d.loc[i,'value_label_status']='official selector code reviewed; Codebook selector options retained; child component identities conflict with the official questionnaire'
                    d.loc[i,'mapping_status']='C metadata; selector options are Codebook-labeled, but child age/year component identities conflict with the official questionnaire'
        if cid=='alcohol_start_stop' and c in {'da070','da071'}:
            d.loc[i,'value_label_status']='official selector code reviewed; component order differs in 2011 versus 2013–2018'
            d.loc[i,'value_semantics']='Selector only; paired fields encode age/year according to the wave-specific selector labels. Not an ordinal exposure.'
        if cid=='smoking_dependence' or (cid=='alcohol_frequency_amount' and c=='da075'): d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
        if cid=='physical_activity_purpose':
            d.loc[i,'value_label_status']='official codebook response labels reviewed; frequencies omitted; descriptive purpose only, not activity dose'
            d.loc[i,'value_semantics']='Purpose of intensive/moderate/light physical activity; descriptive category, not activity occurrence, frequency, duration, or dose. Preserve the wave-specific codebook wording and questionnaire route.'
    elif cid=='smoking_quantity' and c in {'da063','da050_1','da050_2'}:
        d.loc[i,'value_label_status']='continuous count, not a categorical code; daily cigarette count; 2020 current and pre-quit values are separate'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='daily cigarette count; inspect raw special/missing codes before analysis'
    elif cid=='cigarette_price_per_pack' and c=='da064':
        d.loc[i,'value_label_status']='continuous monetary amount, not a categorical code; self-reported price for 20 cigarettes at respondent-specific current/pre-quit reference time'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='Currency: Chinese Yuan per pack of 20 cigarettes, as asked in the questionnaire. Historical/pre-quit reference may apply; not a current market price. Conditional smoker/quit-history routing means missingness is not population-wide absence.'
        d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
    elif cid=='smoking_initiation_cessation' and c=='da065':
        d.loc[i,'value_label_status']='official selector code reviewed; selects whether the following component is age or calendar year, with order changing in 2018'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='Selector only; interpret paired component fields using wave-specific code order. Do not analyze as an ordinal exposure.'
    elif cid=='smoking_initiation_cessation' and re.fullmatch(r'(?:da062|da065|da049)(?:_|s)[12]',c):
        age_component=(c.endswith('1') if w in {'2011','2013','2015'} else c.endswith('2')) if w!='2020' else c.endswith('1')
        d.loc[i,'value_label_status']='continuous component, not a categorical code; component unit reviewed against wave-specific official codebook'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='Age in years' if age_component else 'Calendar year'
    elif cid=='alcohol_start_stop' and c in {'da070','da071'}:
        d.loc[i,'value_label_status']='official selector code reviewed; component order differs in 2011 versus 2013–2018'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='Selector only; paired fields encode age/year according to the wave-specific selector labels. Not an ordinal exposure.'
    elif cid=='alcohol_start_stop' and re.fullmatch(r'da07[01](?:_|s)[12]',c):
        age_component=c.endswith('2')
        d.loc[i,'value_label_status']='continuous component, not a categorical code; component unit reviewed against wave-specific official codebook'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='Age in years' if age_component else 'Calendar year'
    elif cid in {'smoking_prior_wave_ever','smoking_last_interview_status'} and c=='zsmoke':
        d.loc[i,'value_label_status']='official codebook positive preload label reviewed; non-preloaded values are not interpreted as No'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']='prior-interview smoking status preload; codebook exposes positive preload only; do not infer a negative response from absence'
    elif cid=='alcohol_frequency_amount' and c in {'da073','da075_1','da075_2','da077'}:
        unit={'da073':'liang of liquor; questionnaire defines 1 liang as 50 ml','da075_1':'number of beer bottles; questionnaire defines 1 bottle as 2.5 mugs and 1 mug as 220 ml','da075_2':'number of beer mugs; questionnaire defines 1 mug as 220 ml','da077':'liang of wine/rice wine; questionnaire defines 1 liang as 50 ml'}[c]
        d.loc[i,'value_label_status']='continuous beverage quantity, not a categorical code; last drinking event in past year; inspect out-of-range/special values and do not convert to ethanol grams without alcohol-strength assumptions'
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'value_semantics']=unit+'; recalls the most recent drinking event in the past year; beverage amounts/frequency are distinct; no grams of ethanol derived'
        d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
    elif cid=='smoking_dependence' and c=='da066':
        d.loc[i,'value_label_source']=BOOK(w)
        d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
    elif cid=='sleep_duration' and c in {'da049','da030'}:
        d.loc[i,'value_label_status']='continuous measure, not a categorical code; past-month average sleep hours per night; inspect special/missing codes'
        d.loc[i,'value_label_source']=BOOK(w)
        if w=='2020': sem='Continuous real hours/night for past-month actual sleep; valid range 0-24; -1 explicitly means unable to answer.'
        else: sem='Continuous real hours/night for past-month actual sleep; questionnaire range 0-24; released-file special codes still require verification.'
        d.loc[i,'value_semantics']=sem
        d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
    elif cid=='daytime_nap' and c in {'da050','da031'}:
        d.loc[i,'value_label_status']='continuous measure, not a categorical code; nap duration appears in minutes; inspect special/missing codes'
        d.loc[i,'value_label_source']=BOOK(w)
        if w=='2020': sem='Continuous integer minutes after lunch in past month; non-napper=0; -1 explicitly means unable to answer; questionnaire range 0-300.'
        elif w=='2018': sem='Continuous minutes after lunch in past month; non-napper=0; codebook summary maximum 999 conflicts with questionnaire/context and remains unresolved.'
        else: sem='Continuous minutes after lunch in past month; non-napper=0; codebook summary maximum 180; released-file special codes still require verification.'
        d.loc[i,'value_semantics']=sem
        d.loc[i,'questionnaire_source']=questionnaire_source(w,c)
    else:
        d.loc[i,'value_label_status']='not yet reviewed against full response value labels'
# Keep concepts/fields and add the labels to the website JSON in matching order.
d.to_csv(p,index=False,encoding='utf-8-sig')
jp=ROOT/'site-prototype/dist/behavior_exposures_v1.json'; concepts=json.loads(jp.read_text(encoding='utf-8'))
lookup={(r['concept_id'],r['wave'],r['code']):r for r in d.to_dict('records')}
for concept in concepts:
    for f in concept['source_fields']:
        r=lookup[(concept['concept_id'],f['wave'],f['code'])]
        f.update(value_labels=r['value_labels'],value_label_status=r['value_label_status'],value_label_source=r['value_label_source'],value_semantics=r['value_semantics'],questionnaire_source=r['questionnaire_source'])
jp.write_text(json.dumps(concepts,ensure_ascii=False,indent=2),encoding='utf-8')
print('behavior mappings',len(d),'explicit codebook label rows',int((d.value_labels!='').sum()),'continuous quantity/measure rows',int(d.value_label_status.str.startswith(('continuous count','continuous measure','continuous beverage quantity')).sum()))
print(d[d.value_labels!=''].groupby('concept_id').size().to_string())
print(d[d.value_label_status.str.startswith(('continuous count','continuous measure'))].groupby('concept_id').size().to_string())


