"""Map defensible 2011 community-level exposures from the official catalog."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"audit"/"raw_variable_catalog_v1.csv"
CONCEPTS={
 "community_water_sources":("Community drinking-water source profile","Community environment","2011 village/community counts of households using each drinking-water source (not an individual's source or a measured contaminant). Community respondent and denominator must be verified; single-wave only."),
 "community_cooking_fuel_profile":("Community household cooking-fuel profile","Community environment","2011 community-level counts by household fuel category. Not a person-level fuel dose; source categories and denominator require questionnaire/codebook review."),
 "community_winter_heating":("Community winter heating system","Community environment","Community-level availability and fuel type for central winter heating; 2011 only and not an individual residence measure."),
 "community_sanitation_services":("Community sanitation and waste services","Community environment","Sewerage, waste management, toilet infrastructure and public restroom indicators. Community representative report; do not conflate with household toilet fields."),
 "community_industrial_pollution":("Community industrial pollution indicators","Community environment","Includes subjective community ratings for local/nearby industrial pollution and village-level distance to nearest source; not instrument-measured concentration. Some items are village-respondent-only."),
 "community_weather":("Community-reported weather indicators","Community environment","Reported prior calendar-year highest/lowest temperature and rainy/snowy days. These are community-report estimates, not linked meteorological station data."),
 "community_transport_road":("Community road and transport access","Community context","Road type/outage days and distance/count of transport links/stations. Infrastructure/access indicators, not pollutant exposure."),
 "community_electricity":("Community electricity access and reliability","Community environment","Household electricity penetration and annual supply availability/duration; village-level reported metrics."),
 "community_education_profile":("Community adult education composition","Community social context","2011 community-informant estimates of adult education percentages. Each exact-percentage item has a separate category field asked only when the informant does not know the exact number; keep exact and fallback fields distinct and do not combine them until release coding and missingness are validated. Aggregate community context, not an individual's education."),
 "community_water_price":("Community-reported average water price","Community environment","2011 community-reported current average water unit price in RMB yuan per ton; community context, not an individual's household bill."),
 "community_electricity_price":("Community-reported average electricity price","Community environment","2011 community-reported current average electricity unit price in RMB yuan per degree (kWh); community context, not an individual's household bill."),
 "community_road_presence":("Road access through the village/community","Community environment","2011 community-informant Yes/No report of roads passing through the village/community; single-wave context indicator."),
 "community_road_cleanliness":("Community road tidiness","Community environment","2011 community-informant 1-7 ordinal assessment anchored from very dirty to very tidy; subjective road-condition perception, not an environmental sampling measure."),
 "community_primary_school_change":("Primary-school merger or relocation history","Community social context","2011 community-level report of primary-school merger/relocation and prior school count; historical service-access context, not individual schooling."),
 "community_disaster_history":("Recent serious natural-disaster occurrence","Community environment","2011 community-informant report of any serious natural disaster during the prior five years (JI001); No routes to JI003, so JI002 event details have a conditional denominator."),
 "community_sanitation_reconstructed":("Reconstructed community toilet/sewer indicator","Community environment","2011 village-only CAPI item asking whether the village restructured toilet/sewer systems; preserve village-only eligibility and do not infer original derivation from the Codebook variable label."),
}
MAP={
 "community_water_sources":["jb006_1","jb006_2","jb006_3","jb006_4","jb006_5","jb006_6","jb006_7","jb006_8"],
 "community_cooking_fuel_profile":["jb007_1","jb007_2","jb007_3","jb007_4","jb007_5","jb007_6"],
 "community_winter_heating":["jb008","jb009s1","jb009s2","jb009s3","jb009s4"],
 "community_sanitation_services":["jb010","jb012","jb013","jb014"],
 "community_industrial_pollution":["jb018","jb019","jb027"],
 "community_weather":["ja039_1","ja039_2","ja040","ja041"],
 "community_transport_road":["jb001","jb002","jb003","jb004","jb005"],
 "community_electricity":["jb017","jb020","jb021"],
 "community_education_profile":["jc019","jc019_1","jc020","jc020_1","jc021","jc021_1","jc022","jc022_1","jc023","jc023_1","jc024","jc024_1"],
 "community_water_price":["jj023"],
 "community_electricity_price":["jj024"],
 "community_road_presence":["jk001"],
 "community_road_cleanliness":["jk003"],
 "community_primary_school_change":["jh015","jh017"],
 "community_disaster_history":["ji001"],
 "community_sanitation_reconstructed":["jb015"],
}

# The 2011 Community Questionnaire pages 10, 21–22, and 32–33 explicitly
# identify the facility slots and routes that were missing from the original
# codebook-only triage. Keep each facility/type as a candidate concept and
# preserve conditional response components as source fields.
FACILITIES = [
 (1,"kindergarten","Kindergartens"), (2,"primary_school","Primary schools"),
 (3,"junior_middle_school","Junior middle schools"), (4,"senior_high_school","Senior high schools"),
 (5,"post_office","Post offices"), (6,"library","Libraries"),
 (7,"police_station","Police stations"), (8,"bank","Banks"),
 (9,"theatre","Theatres"), (10,"nursing_home","Nursing homes"),
 (11,"convenience_store","Convenience stores"), (12,"farmers_market","Farmers' markets"),
 (13,"supermarket","Supermarkets"),
]
HEALTH_FACILITIES = [
 (1,"general_hospital","General hospital"), (2,"specialized_hospital","Specialized hospital"),
 (3,"chinese_medicine_hospital","Chinese medicine hospital"), (4,"nearby_pharmacy","Nearby pharmacy"),
 (5,"community_health_center","Community health care center"), (6,"community_medical_post","Community health care medical post"),
 (7,"township_health_clinic","Township health clinic/hospital"), (8,"village_medical_post","Village medical post"),
]
for idx, slug, label in FACILITIES:
 for measure, title, unit in (("count","count","facilities"),("distance","distance from community office","km")):
  cid=f"community_{slug}_{measure}"
  CONCEPTS[cid]=(f"{label} in community ({title})","Community infrastructure",
   ("2011 community-informant report of the number of facilities in the village/community. "
    "This is a community count, not an individual's access measure.") if measure=="count" else
   ("2011 distance from the village/community office to the most commonly used facility of this type; "
    "the questionnaire records 0 when the facility is in the community. Not distance from a respondent's home."))
  MAP[cid]=[f"jb028_1_{idx}_" if measure=="count" else f"jb028_2_{idx}_"]

for idx, slug, label in HEALTH_FACILITIES:
 cid=f"community_{slug}_availability_and_count"
 CONCEPTS[cid]=(f"Community availability/count: {label}","Community healthcare access",
  "2011 community informant may select this facility type as commonly used by residents, then reports whether the community has it and gives a count if present. A blank/unselected JF001 option is not confirmed No; JF002 count is conditional. These are community-level reports, not individual use.")
 MAP[cid]=[f"jf001s{idx}",f"jf002_{idx}_",f"jf002_1_{idx}_"]
 cid=f"community_{slug}_public_private"
 CONCEPTS[cid]=(f"Community care facility type: {label} (public/private)","Community healthcare access",
  "2011 public/private type for a facility type selected in JF001. Conditional on the community health-informant route; not an individual-level care outcome.")
 MAP[cid]=[f"jf004_{idx}_"]
 cid=f"community_{slug}_distance_to_office"
 CONCEPTS[cid]=(f"Community care facility: {label} distance to office","Community healthcare access",
  "2011 one-way distance from the community office to this commonly used facility, in kilometres; 0 means the facility is in the community. Conditional on the JF001 facility route.")
 MAP[cid]=[f"jf006_{idx}_"]
 cid=f"community_{slug}_main_transport"
 CONCEPTS[cid]=(f"Community care facility: {label} main transport","Community healthcare access",
  "2011 community-informant report of the usual transport mode to this facility. Nominal categories; do not treat numeric codes as an ordered exposure.")
 MAP[cid]=[f"jf007_{idx}_"]
 cid=f"community_{slug}_oneway_travel_time"
 CONCEPTS[cid]=(f"Community care facility: {label} one-way travel time","Community healthcare access",
  "2011 travel time by the reported main transport mode, stored in separate hour and minute fields. Preserve both source components and route; do not assume either component alone is total minutes.")
 MAP[cid]=[f"jf008_1_{idx}_",f"jf008_2_{idx}_"]
 cid=f"community_{slug}_oneway_travel_cost"
 CONCEPTS[cid]=(f"Community care facility: {label} one-way travel cost","Community healthcare access",
  "2011 average one-way transportation cost including fuel, reported in RMB yuan. Community-informant measure, conditional on JF001 facility route.")
 MAP[cid]=[f"jf009_{idx}_"]

for idx, slug, label in HEALTH_FACILITIES[:3]:
 cid=f"community_{slug}_facility_level"
 CONCEPTS[cid]=(f"Community care facility: {label} level","Community healthcare access",
  "2011 facility-level category for general, specialized, and Chinese-medicine hospitals only, as specified by the questionnaire. Conditional on JF001 selection.")
 MAP[cid]=[f"jf005_{idx}_"]

DISASTERS = [(1,"flood","Flood"),(2,"drought","Drought"),(3,"fire","Fire"),
 (4,"earthquake","Earthquake"),(5,"typhoon","Typhoon"),(6,"snow_storm","Snow storm"),
 (7,"other_natural_disaster","Other natural disaster")]
for idx, slug, label in DISASTERS:
 cid=f"community_{slug}_history_5y"
 CONCEPTS[cid]=(f"Community {label.lower()} history (past five years)","Community environment",
  "2011 community-informant report: occurrence, number of times, year/month of the most severe event, and people injured or dead in that event. Asked after the JI001 serious-disaster route; keep components and denominator distinct. Open-text description of 'other' is not included.")
 MAP[cid]=[f"ji002_a_{idx}_",f"ji002_b_{idx}_",f"ji002_c_{idx}_",f"ji002_d_{idx}_",f"ji002_e_{idx}_"]

QUESTIONNAIRE_REVIEWED = {
 "community_water_sources","community_cooking_fuel_profile","community_winter_heating",
 "community_sanitation_services","community_industrial_pollution","community_weather",
 "community_transport_road","community_electricity","community_education_profile",
 "community_water_price","community_electricity_price","community_road_presence",
 "community_road_cleanliness","community_disaster_history","community_sanitation_reconstructed",
 *[cid for cid in CONCEPTS if cid.startswith("community_kindergarten_") or
    cid.startswith("community_primary_school_") or cid.startswith("community_junior_middle_school_") or
    cid.startswith("community_senior_high_school_") or cid.startswith("community_post_office_") or
    cid.startswith("community_library_") or cid.startswith("community_police_station_") or
    cid.startswith("community_bank_") or cid.startswith("community_theatre_") or
    cid.startswith("community_nursing_home_") or cid.startswith("community_convenience_store_") or
    cid.startswith("community_farmers_market_") or cid.startswith("community_supermarket_") or
    cid.startswith("community_general_hospital_") or cid.startswith("community_specialized_hospital_") or
    cid.startswith("community_chinese_medicine_hospital_") or cid.startswith("community_nearby_pharmacy_") or
    cid.startswith("community_community_health_center_") or cid.startswith("community_community_medical_post_") or
    cid.startswith("community_township_health_clinic_") or cid.startswith("community_village_medical_post_") or
    cid.startswith("community_flood_history_") or cid.startswith("community_drought_history_") or
    cid.startswith("community_fire_history_") or cid.startswith("community_earthquake_history_") or
    cid.startswith("community_typhoon_history_") or cid.startswith("community_snow_storm_history_") or
    cid.startswith("community_other_natural_disaster_history_")]
}

def main():
 src=pd.read_csv(CAT,dtype=str,encoding="utf-8-sig").fillna(""); rows=[]
 for cid,codes in MAP.items():
  label,domain,caveat=CONCEPTS[cid]
  for code in codes:
   hit=src[(src.wave.astype(str)=="2011") & src.variable.str.lower().eq(code.lower()) & src.module.str.lower().eq("community")]
   if hit.empty: raise ValueError(f"Community variable not found: {code}")
   for r in hit.drop_duplicates(["module","variable","variable_label"]).itertuples():
    is_reviewed = cid in QUESTIONNAIRE_REVIEWED
    code_l = code.lower()
    if code_l.startswith("jb028_"):
     evidence="CHARLS 2011 Community Questionnaire, Part B p.10 (PDF p.13), JB028 facility table; corresponding codebook field label."
    elif code_l.startswith("jf"):
     evidence="CHARLS 2011 Community Questionnaire, Part F pp.21–22 (PDF pp.24–25), JF001–JF009 route; corresponding codebook field label."
    elif code_l.startswith("ji002_"):
     evidence="CHARLS 2011 Community Questionnaire, Part I pp.32–33 (PDF pp.35–36), JI001–JI002 route; corresponding codebook field label."
    elif cid == "community_education_profile":
     evidence="CHARLS 2011 Community Questionnaire, Part C p.16 (PDF p.19), JC019-JC024; exact percentage fields and conditional _1 bracket fields verified."
    elif is_reviewed:
     evidence="CHARLS 2011 Community Questionnaire, Part A pp.7–8 / Part B pp.10–12; official codebook field label."
    else:
     evidence="CHARLS 2011 official codebook variable label; questionnaire page/routing review remains required for this added candidate"
    if code_l.startswith("jb028_1_") or code_l.startswith("jf002_1_"):
     unit="facilities"
    elif code_l.startswith(("jb028_2_","jf006_")):
     unit="km"
    elif code_l.startswith("jf008_1_"):
     unit="hours"
    elif code_l.startswith("jf008_2_"):
     unit="minutes"
    elif code_l.startswith("jf009_"):
     unit="RMB yuan"
    elif code_l.startswith("ji002_b_"):
     unit="events"
    elif code_l.startswith("ji002_c_"):
     unit="year"
    elif code_l.startswith("ji002_d_"):
     unit="month"
    elif code_l.startswith("ji002_e_"):
     unit="people injured or dead"
    elif code_l in {"jc019","jc020","jc021","jc022","jc023","jc024"}:
     unit="percent of community adults"
    elif code_l in {"jc019_1","jc020_1","jc021_1","jc022_1","jc023_1","jc024_1"}:
     unit="percent bracket (fallback category)"
    elif code_l == "jj023":
     unit="RMB yuan/ton"
    elif code_l == "jj024":
     unit="RMB yuan/kWh"
    else:
     unit=""
    rows.append({"concept_id":cid,"concept_label":label,"domain":domain,"wave":2011,
     "code":code,"module":r.module,"source_label":r.variable_label,
     "source_evidence":evidence,
     "mapping_status":"official questionnaire slot/route and codebook label reviewed; candidate, analysis eligibility pending" if is_reviewed else "official codebook label located; candidate pending questionnaire/valid-code review",
     "caveat":caveat,"unit":unit})
 out=pd.DataFrame(rows).drop_duplicates()
 out.to_csv(ROOT/"audit"/"community_exposure_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
 items=[]
 for cid,(label,domain,caveat) in CONCEPTS.items():
  fs=out[out.concept_id.eq(cid)]
  items.append({"concept_id":cid,"label":label,"domain":domain,"caveat":caveat,
   "source_fields":[{"wave":str(r.wave),"code":r.code,"module":r.module,
    "source_label":r.source_label,"source_evidence":r.source_evidence,
    "note":r.mapping_status,"unit":r.unit} for r in fs.itertuples()]})
 (ROOT/"site-prototype"/"dist"/"community_exposures_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"concepts={len(items)}; mappings={len(out)}; all wave=2011; module=Community")
if __name__=="__main__": main()
