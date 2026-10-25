"""Map defensible 2011 community-level exposures from the official catalog."""
from pathlib import Path
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"audit"/"raw_variable_catalog_v1.csv"
CONCEPTS={
 "community_water_sources":("Community drinking-water source profile","Community environment","At the end of calendar year 2010, a community informant reported counts of households using each drinking-water source. Sources may overlap; the questionnaire gives no total-household denominator here. These are not an individual's source or a measured contaminant. Single-wave only."),
 "community_cooking_fuel_profile":("Community household cooking-fuel profile","Community environment","At the end of calendar year 2010, a community informant reported counts of households using each fuel source. Categories may overlap; the questionnaire gives no total-household denominator here. Not a person-level fuel dose; single-wave only."),
 "community_winter_heating":("Community winter heating system","Community environment","Community-level availability and fuel type for central winter heating; 2011 only and not an individual residence measure."),
 "community_sanitation_services":("Community sanitation and waste services","Community environment","Sewerage, waste management, toilet infrastructure and public restroom indicators. Community representative report; do not conflate with household toilet fields."),
 "community_industrial_pollution":("Community industrial pollution indicators","Community environment","Three distinct community-level reports: JB018 rates pollution in the village/community; village-only JB019 rates nearby villages/townships; village-only JB027 records distance to the closest industrial pollution site in kilometres, with 0 meaning the site is located in the village. The ratings are subjective ordinal reports, and the distance is not the respondent's home-to-source distance; none is an instrument-measured concentration or individual pollution dose."),
 "community_weather":("Community-reported weather indicators","Community environment","Community-informant estimates for calendar year 2010: lowest/highest temperature in degrees Celsius and rainy/snowy day counts. These are not linked meteorological station observations; preserve each component and verify special values and eligible denominators before analysis."),
 "community_transport_road":("Community road and transport access","Community context","Road type/outage days and distance/count of transport links/stations. Infrastructure/access indicators, not pollutant exposure."),
 "community_electricity":("Community electricity access and reliability","Community environment","Household electricity penetration and annual supply availability/duration; village-level reported metrics."),
 "community_education_profile":("Community adult education composition","Community social context","2011 community-informant estimates of adult education percentages. Each exact-percentage item has a separate category field asked only when the informant does not know the exact number; keep exact and fallback fields distinct and do not combine them until release coding and missingness are validated. Aggregate community context, not an individual's education."),
 "community_water_price":("Community-reported average water price","Community environment","2011 community-reported current average water unit price in RMB yuan per ton; community context, not an individual's household bill."),
 "community_electricity_price":("Community-reported average electricity price","Community environment","2011 community-reported current average electricity unit price in RMB yuan per degree (kWh); community context, not an individual's household bill."),
 "community_road_presence":("Road access through the village/community","Community environment","2011 community-informant Yes/No report of roads passing through the village/community; single-wave context indicator."),
 "community_road_cleanliness":("Community road tidiness","Community environment","2011 community-informant 1-7 ordinal assessment anchored from very dirty to very tidy; subjective road-condition perception, not an environmental sampling measure."),
 "community_observed_socioeconomic_status":("Observed community socioeconomic status","Community social context","2011 interviewer observation on a 1–7 ordinal scale anchored from poor to rich. This is a fieldworker's overall community judgment, not household income or an objective area-level economic statistic."),
 "community_built_form_organization":("Community built-form organization","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from very disorganized to very organized. This is a subjective community-level built-environment proxy, not a standardized urban-form assessment."),
 "community_observed_crowding":("Observed community crowding/sparsity","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from very crowded to very sparse; higher values indicate less perceived crowding. This is not a measured population density."),
 "community_accessibility_observation":("Observed community accessibility for people with disabilities","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from no handicapped access to very convenient. Higher values indicate better perceived access; this is not an audited accessibility standard."),
 "community_primary_school_change":("Primary-school merger or relocation history","Community social context","2011 community-level report of primary-school merger/relocation and prior school count; historical service-access context, not individual schooling."),
 "community_disaster_history":("Recent serious natural-disaster occurrence","Community environment","2011 community-informant report of any serious natural disaster during the prior five years (JI001); No routes to JI003, so JI002 event details have a conditional denominator."),
 "community_sanitation_reconstructed":("Reconstructed community toilet/sewer indicator","Community environment","2011 village-only CAPI item asking whether the village restructured toilet/sewer systems; preserve village-only eligibility and do not infer original derivation from the Codebook variable label."),
 "community_land_use_profile":("Community land area and agricultural land-use profile","Community environment","2011 village-level land area, arable/construction land, land-development and land-lease context. Preserve the distinct reference years, units, V-only eligibility and conditional routes; do not calculate density or percentages without compatible denominators. JA012 is excluded from this concept because its official questionnaire and Codebook descriptions conflict (paddy field versus irrigatable land). These are not an individual's landholding or chemical exposure."),
 "community_main_terrain":("Community main terrain/topography","Community environment","2011 community-reported nominal terrain category (plain, hill, mountainous region, plateau or basin). A coarse area-level descriptor, not a personal exposure dose; do not treat codes as an ordinal scale."),
 "community_agricultural_mechanization":("Community agricultural mechanization context","Community context","2011 community-reported agricultural mechanization share and large-machine rental context. JJ003/004 are conditional; these are not individual occupation, machinery contact, pesticide application or inhaled exposure."),
 "community_fertilizer_seed_inputs":("Community-reported fertilizer and seed input context","Community environment","2011 community informant reports the most commonly used fertilizer name and community-level fertilizer/seed prices. The fertilizer name is open text and does not identify chemical composition or quantify use; prices do not establish individual purchase, handling or exposure."),
 "community_food_prices":("Community-reported food commodity prices","Community food environment","2011 informant-reported current local prices for pork tenderloin, eggs, rice and wheat/flour. These indicate community price context, not what a participant bought, ate, or received nutritionally; retain commodity-specific source fields and units."),
 "community_household_energy_prices":("Community-reported household energy prices","Community environment","2011 informant-reported current local prices for natural gas, bottled LPG and coal. Prices are community context, not household fuel use, fuel mix, combustion or personal pollutant dose; retain distinct units."),
 "community_major_crop_production":("Community major-crop production profile","Community agricultural context","2011 village informant ranks up to three major crops and reports crop-specific planted area, yield per mu, mechanized production, current harvest seasons and historical maximum seasons. Keep crop ranks and unlike measurement units separate; do not sum yields or derive personal pesticide, occupation or dietary exposure."),
 "community_household_amenity_penetration":("Community household communication and appliance penetration","Community socioeconomic context","2011 village-informant estimates of the share of households with fixed telephones, one or more cell phones, televisions, and refrigerators. These are aggregate community percentages, not the sampled household's ownership, use, or an individual's digital exposure; preserve each amenity separately."),
 "community_historical_disaster_epidemic_severity":("Community history of severe disasters and epidemics","Community environment","2011 community informant retrospectively identifies up to three most severe listed natural disasters or epidemics since 1945, with event start/end month and year, deaths/injuries, affected population share, and grain-output decline. Preserve event ranks, dates, event types and impact measures separately; long recall and community-level reporting do not establish a sampled person's direct exposure."),
 "community_reforestation_subsidy_program":("Community reforestation subsidy program context","Community environmental-policy context","2011 village-only report of whether reforestation subsidies were implemented, their start year, the number of village households receiving them in 2010, and the average subsidy standard. These describe a local policy/program and uptake, not forest cover, greenness, ecological restoration success, household receipt linkage, or a personal environmental exposure."),
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
 "community_observed_socioeconomic_status":["jk002"],
 "community_built_form_organization":["jk004"],
 "community_observed_crowding":["jk005"],
 "community_accessibility_observation":["jk006"],
 "community_primary_school_change":["jh015","jh017"],
 "community_disaster_history":["ji001"],
 "community_sanitation_reconstructed":["jb015"],
 "community_land_use_profile":["ja003_1","ja003_2","ja011","ja013","ja014","ja029","ja032","ja033","ja034","ja050"],
 "community_main_terrain":["ja038"],
 "community_agricultural_mechanization":["jj002","jj003","jj004"],
 "community_fertilizer_seed_inputs":["jj006","jj007","jj008","jj009","jj010"],
 "community_food_prices":["jj017","jj018","jj019","jj020"],
 "community_household_energy_prices":["jj021","jj022","jj025"],
 "community_major_crop_production":[*[f"jj001_{i}{suffix}" for i in range(1,4) for suffix in "abcdef"]],
 "community_household_amenity_penetration":["jb023","jb024","jb025","jb026"],
 "community_historical_disaster_epidemic_severity":[f"ji003_{i}{suffix}" for i in range(1,4) for suffix in "abcdefgh"],
 "community_reforestation_subsidy_program":["jg021","jg022","jg023","jg024"],
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
 "community_road_cleanliness","community_observed_socioeconomic_status",
 "community_built_form_organization","community_observed_crowding",
 "community_accessibility_observation","community_disaster_history","community_sanitation_reconstructed",
 "community_land_use_profile","community_main_terrain","community_agricultural_mechanization",
 "community_fertilizer_seed_inputs","community_food_prices","community_household_energy_prices",
 "community_major_crop_production",
 "community_household_amenity_penetration",
 "community_historical_disaster_epidemic_severity",
 "community_reforestation_subsidy_program",
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

def validate_added_source_mappings():
 qpath=ROOT/"sources_official"/"CHARLS_2011_Community_Questionnaire_official_extracted.txt"
 cpath=ROOT/"sources_official"/"CHARLS_2011_Codebook_extracted.txt"
 q=" ".join(qpath.read_text(encoding="utf-8",errors="ignore").casefold().split())
 cb=" ".join(cpath.read_text(encoding="utf-8",errors="ignore").casefold().split())
 codes={code for cid in ("community_land_use_profile","community_main_terrain","community_agricultural_mechanization","community_fertilizer_seed_inputs","community_food_prices","community_household_energy_prices","community_major_crop_production","community_household_amenity_penetration","community_historical_disaster_epidemic_severity","community_reforestation_subsidy_program") for code in MAP[cid]}
 for code in codes:
  code_norm="".join(ch for ch in code.casefold() if ch.isalnum())
  q_norm="".join(ch for ch in q if ch.isalnum())
  cb_norm="".join(ch for ch in cb if ch.isalnum())
  if code_norm not in q_norm or code_norm not in cb_norm:
   raise ValueError(f"Official 2011 community questionnaire/Codebook missing mapped field {code}")
 required_q=(
  "what is the physical area of this village/community",
  "how many of the land is arable land at the end of the year 2010",
  "how much of the land was arable land at the end of 2007",
  "rural construction land at the end of",
  "how much new arable land were added",
  "how many construction land were reduced through village consolidation",
  "percentage of arable land in your village",
  "leased out?",
  "what is the rental price for land each year in your village",
  "what is the average area of house site per person",
  "what is the main terrain/topography of your village /community",
  "what is the percentage of agricultural products on which agricultural machines are used",
  "do you rent big machines",
  "skip to jj006",
  "what is the rental price per day for these big machines",
  "name of the most commonly used fertilizers",
  "price of that fertilizer",
  "price of rice seed",
  "price of rice seedling",
  "price of wheat seed",
  "average unit price for the liji part of pork",
  "average unit price for chicken eggs",
  "average unit price for rice in this village/community",
  "average unit price for flour in this village/community",
  "average unit price for natural gas",
  "average unit price for liquefied petroleum gas",
  "average unit price for coal",
  "please tell me about the three major agricultural products in your village",
  "what is the planting area in 2010",
  "what is the average output per mu",
  "how many seasons do you harvest this crop",
  "what percentage of households in your village has telephone",
  "what percentage of households in your village has one (or more) cell phones",
  "what percentage of households in your village have a tv",
  "what percentage of households in your village has a refrigerator",
  "three most severe natural disaster/epidemics occurred in this village/community since 1945",
  "when did it occur",
  "when did it end",
  "how many people were injured or dead",
  "what was the percentage of people dead or injured",
  "what was the percentage by which grain output went down",
  "does your village have subsidies for reforestation",
  "when did subsidies for reforestation start to be implemented in this village",
  "how many households in this village received subsidies for reforestation in year 2010",
  "what is the average subsidies standard",
 )
 for phrase in required_q:
  if phrase not in q:
   raise ValueError(f"Official 2011 community questionnaire wording missing: {phrase}")
 if "ja012" not in cb or "among arable land, how many is irrigatable" not in cb or "among arable land, how many is paddy field" not in q:
  raise ValueError("JA012 questionnaire/Codebook wording conflict not found")
 for label in ("1 plain","2 hill","3 mountainous region"):
  label_norm="".join(ch for ch in label if ch.isalnum())
  if label_norm not in "".join(ch for ch in q if ch.isalnum()) or label_norm not in "".join(ch for ch in cb if ch.isalnum()):
   raise ValueError(f"JA038 terrain category missing from official source: {label}")
 if "4" not in q or "高原" not in q or "4 plateau" not in cb or "5" not in q or "盆地" not in q or "5 basin" not in cb:
  raise ValueError("JA038 code 4/5 terrain bilingual source anchor not found")

def main():
 validate_added_source_mappings()
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
    elif cid == "community_land_use_profile":
     evidence="CHARLS 2011 Community Questionnaire, Part A pp.2–6 (PDF pp.5–9); V-only land area/use items, reference periods and conditional land-development routes checked against the Codebook. JA012 wording discrepancy is documented separately and is not mapped here."
    elif cid == "community_main_terrain":
     evidence="CHARLS 2011 Community Questionnaire, Part A p.7 (PDF p.10), JA038; nominal answer labels checked against the official Codebook; frequencies omitted."
    elif cid in {"community_agricultural_mechanization","community_fertilizer_seed_inputs"}:
     evidence="CHARLS 2011 Community Questionnaire, Part J, JJ002–JJ010; V-only agricultural production items, branch and stated units checked against official Codebook labels."
    elif cid in {"community_food_prices","community_household_energy_prices"}:
     evidence="CHARLS 2011 Community Questionnaire, Part J pp.38–39 (PDF pp.41–42), commodity-specific current-price prompts and units checked against the official Codebook; no numeric summaries copied."
    elif cid == "community_major_crop_production":
     evidence="CHARLS 2011 Community Questionnaire, Part J p.35 (PDF p.38), JJ001 ranked three-crop table; crop name, 2010 planted area, yield per mu, mechanized-production response and crop-season fields checked against the official Codebook; frequencies omitted."
    elif cid == "community_household_amenity_penetration":
     evidence="CHARLS 2011 Community Questionnaire, Part B p.11 (PDF p.14), JB023–JB026 V-only village household-penetration estimates; 0–100 percent scale checked against the official Codebook."
    elif cid == "community_historical_disaster_epidemic_severity":
     evidence="CHARLS 2011 Community Questionnaire, Part I pp.34–35 (PDF pp.37–38), JI003 retrospective three-event table since 1945; listed disasters/epidemics, event dates and community impact fields checked against the official Codebook."
    elif cid == "community_reforestation_subsidy_program":
     evidence="CHARLS 2011 Community Questionnaire, Part G, village-only JG021–JG024; program route, 2010 household uptake count and stated subsidy unit checked against official Codebook labels; frequencies omitted."
    elif cid.startswith("community_observed_") or cid in {"community_built_form_organization", "community_accessibility_observation"}:
     evidence="CHARLS 2011 Community Questionnaire, Part K interviewer observations; item-specific 1–7 endpoint anchors verified."
    elif is_reviewed:
     evidence="CHARLS 2011 Community Questionnaire, Part A pp.7–8 / Part B pp.10–12; official codebook field label."
    else:
     evidence="CHARLS 2011 official codebook variable label; questionnaire page/routing review remains required for this added candidate"
    if code_l == "jb018":
     evidence="CHARLS 2011 Community Questionnaire, Part B, JB018; response anchors reconciled with the official Codebook; frequencies omitted."
     caveat="Community-informant ordinal report of industrial pollution in this village/community (1=very severe to 4=completely absent); higher codes mean less reported pollution. This is not an instrument-measured concentration or an individual dose."
    elif code_l == "jb019":
     evidence="CHARLS 2011 Community Questionnaire, Part B, village-only CAPI item JB019; response anchors reconciled with the official Codebook; frequencies omitted."
     caveat="Community-informant ordinal report of industrial pollution in nearby villages/townships (1=very severe to 4=completely absent); higher codes mean less reported pollution. Village-only route; not the respondent's residential distance or an instrument-measured concentration."
    elif code_l == "jb027":
     evidence="CHARLS 2011 Community Questionnaire, Part B, village-only CAPI item JB027; stated unit and in-village zero rule reviewed against the official Codebook field."
     caveat="Distance in kilometres from the village to the closest industrial pollution site; questionnaire explicitly says 0 when the site is in the village. Village-only route; not an individual's home-to-source distance, measured concentration, or validated personal dose. Verify release-specific special values and eligible denominator before analysis."
    elif code_l == "ja039_1":
     caveat="Community-informant estimate of the lowest temperature in calendar year 2010, in degrees Celsius. Not linked to a weather station or a respondent's personal temperature exposure; verify release-specific special values before analysis."
    elif code_l == "ja039_2":
     caveat="Community-informant estimate of the highest temperature in calendar year 2010, in degrees Celsius. Not linked to a weather station or a respondent's personal temperature exposure; verify release-specific special values before analysis."
    elif code_l == "ja040":
     caveat="Community-informant estimated count of rainy days in calendar year 2010. Not linked to a weather station; verify release-specific special values and plausible range before analysis."
    elif code_l == "ja041":
     caveat="Community-informant estimated count of snowy days in calendar year 2010. Not linked to a weather station; verify release-specific special values and plausible range before analysis."
    elif code_l == "jg021":
     caveat="Village-only Yes/No report of a reforestation-subsidy program. A No response routes past JG022–JG024; it does not identify ecological conditions or prove that the sampled household received support."
    elif code_l == "jg022":
     unit="year"
     caveat="Year the village began the reforestation-subsidy program, asked only after JG021=Yes. Preserve the route and validate special values in the authorized release."
    elif code_l == "jg023":
     unit="households"
     caveat="Number of village households reported to have received reforestation subsidies in 2010, conditional on the village program route. This is not the sampled household's receipt status or a population-standardized rate."
    elif code_l == "jg024":
     unit="Yuan/mu"
     caveat="Community-reported average reforestation-subsidy standard, conditional on JG021=Yes. The questionnaire states Yuan per mu; do not treat it as an individual's payment or evidence of achieved forest restoration."
    elif code_l in {"ja003_1", "ja003_2"}:
     unit="km²" if code_l == "ja003_1" else "mu"
     caveat="Community boundary area in the unit-specific field; the questionnaire provides separate km² and mu blanks. Keep the source fields distinct until the authorized release confirms how the unit choice is stored; do not sum or double count. This is community area, not household plot size."
    elif code_l == "ja011":
     unit="mu"
     caveat="Village arable-land area at end of 2010, including paddy and dry land; V-only item. Community aggregate, not respondent landholding."
    elif code_l == "ja013":
     unit="mu"
     caveat="Village arable-land area at end of 2007; preserve this earlier reference year separately from the 2010 JA011 measure. V-only community aggregate."
    elif code_l == "ja014":
     unit="mu"
     caveat="Village rural construction-land area at end of 2010; V-only. Do not combine with JA003 total community area or infer individual housing density."
    elif code_l == "ja029":
     unit="mu"
     caveat="New arable-land area added through land development/consolidation since 2005; conditional on the preceding land-development Yes route. Preserve structural skips."
    elif code_l == "ja032":
     unit="mu"
     caveat="Construction-land area reduced through village consolidation since 2005; conditional on the preceding village-consolidation Yes route. Preserve structural skips."
    elif code_l == "ja033":
     unit="percent"
     caveat="Informant's approximate percentage of village arable land subcontracted or leased out; preserve as a community land-use context measure, not an individual tenancy status."
    elif code_l == "ja034":
     unit="Yuan/mu/year"
     caveat="Reported annual land rental price per mu in the village; community market context, not a respondent's land rent or income."
    elif code_l == "ja050":
     unit="mu/person"
     caveat="Reported 2010 average rural house-site area per person in the village; community aggregate, not the sampled respondent's lot size."
    elif code_l == "ja038":
     caveat="Community's main terrain category; nominal, unordered labels. Do not infer elevation, slope, or individual geographic exposure from the category alone."
    elif code_l == "jj002":
     unit="percent"
     caveat="Reported percentage of community agricultural products using agricultural machinery; community production context, not respondent occupational contact or air-pollution dose."
    elif code_l == "jj003":
     caveat="Whether the community rents large agricultural machinery; No routes past the machine-rental price item. Keep the route and do not treat missing JJ004 as zero."
    elif code_l == "jj004":
     unit="Yuan/day"
     caveat="Daily rental price for large agricultural machinery, asked only after JJ003=Yes; community-level production price, not an individual cost or exposure."
    elif code_l == "jj006":
     caveat="Open-text name of one commonly used fertilizer in local agricultural production. It is not a standardized chemical name or measure of application amount; do not infer pesticide or fertilizer exposure from the string alone."
    elif code_l in {"jj007", "jj008", "jj009", "jj010"}:
     unit="Yuan/jin"
     caveat="Community-reported price per jin for the source-specific fertilizer/seed/seedling item; a local agricultural input price, not an individual purchase, use, or absorbed dose."
    elif code_l in {"jj017", "jj018", "jj019", "jj020"}:
     unit="Yuan/jin"
     caveat="Current community-reported commodity price per jin; local food-market context, not respondent purchasing, dietary intake, or nutrient exposure."
    elif code_l == "jj021":
     unit="Yuan/m³"
     caveat="Current community-reported natural-gas price per cubic metre; not evidence of household connection, use, or combustion exposure."
    elif code_l == "jj022":
     unit="Yuan/bottle"
     caveat="Current community-reported bottled LPG price per bottle; bottle size is not specified in this item. Not evidence of household use or combustion exposure."
    elif code_l == "jj025":
     unit="Yuan/jin"
     caveat="Current community-reported coal price per jin; not evidence of household coal use, combustion, or personal pollutant dose."
    elif code_l.startswith("jj001_") and code_l.endswith("a"):
     caveat="Open-text name of the crop in this ranked slot; preserve source rank and do not treat this string as a standardized crop code."
    elif code_l.startswith("jj001_") and code_l.endswith("b"):
     unit="mu"
     caveat="2010 planted area for the crop in this ranked slot; keep crop ranks separate and do not sum until authorized-release coding and overlap are validated."
    elif code_l.startswith("jj001_") and code_l.endswith("c"):
     unit="jin/mu"
     caveat="Informant-reported average yield per mu for the crop in this ranked slot; retain rank and do not combine with planted area to derive production without validation."
    elif code_l.startswith("jj001_") and code_l.endswith("d"):
     caveat="Whether machinery is used for the crop in this ranked slot; nominal Yes/No response, not individual machinery contact or pollution dose."
    elif code_l.startswith("jj001_") and code_l.endswith("e"):
     unit="harvest seasons/year"
     caveat="Current typical number of harvest seasons per year for this crop; keep distinct from its historical maximum and other crop ranks."
    elif code_l.startswith("jj001_") and code_l.endswith("f"):
     unit="harvest seasons/year (historical maximum)"
     caveat="Informant-reported historical maximum harvest seasons per year for this crop; not directly comparable to the current typical seasons field."
    elif code_l in {"jb023","jb024","jb025","jb026"}:
     unit="percent of village households"
     caveat="Community-informant estimate of the share of village households with this amenity (0–100%). Aggregate context, not confirmed ownership or use by the sampled household or individual."
    elif code_l.startswith("ji003_"):
     suffix=code_l[-1]
     unit={"b":"year","c":"month","d":"year","e":"month","f":"people","g":"percent of community population","h":"percent of grain output decline"}.get(suffix,"")
     caveat="Retrospective record for one of the three most severe natural disasters/epidemics reported since 1945; retain event rank, date components and impact fields separately. Community-level long-recall measure, not an individual's verified direct exposure."
    if code_l.startswith(("jb006_", "jb007_")):
     unit="households"
    elif code_l == "jg023":
     unit="households"
    elif code_l == "jg022":
     unit="year"
    elif code_l == "jg024":
     unit="Yuan/mu"
    elif code_l.startswith("jb028_1_") or code_l.startswith("jf002_1_"):
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
    elif code_l == "jb027":
     unit="km"
    elif code_l in {"ja039_1", "ja039_2"}:
     unit="degrees Celsius (°C)"
    elif code_l in {"ja040", "ja041"}:
     unit="days"
    elif code_l == "ja003_1":
     unit="km²"
    elif code_l == "ja003_2":
     unit="mu"
    elif code_l in {"ja011", "ja013", "ja014", "ja029", "ja032"}:
     unit="mu"
    elif code_l == "ja033" or code_l == "jj002":
     unit="percent"
    elif code_l == "ja034":
     unit="Yuan/mu/year"
    elif code_l == "ja050":
     unit="mu/person"
    elif code_l == "jj004":
     unit="Yuan/day"
    elif code_l in {"jj007", "jj008", "jj009", "jj010", "jj017", "jj018", "jj019", "jj020", "jj025"}:
     unit="Yuan/jin"
    elif code_l == "jj021":
     unit="Yuan/m³"
    elif code_l == "jj022":
     unit="Yuan/bottle"
    elif code_l.startswith("jj001_") and code_l.endswith("b"):
     unit="mu"
    elif code_l.startswith("jj001_") and code_l.endswith("c"):
     unit="jin/mu"
    elif code_l.startswith("jj001_") and code_l.endswith("e"):
     unit="harvest seasons/year"
    elif code_l.startswith("jj001_") and code_l.endswith("f"):
     unit="harvest seasons/year (historical maximum)"
    elif code_l in {"jb023","jb024","jb025","jb026"}:
     unit="percent of village households"
    elif code_l.startswith("ji003_"):
     unit={"b":"year","c":"month","d":"year","e":"month","f":"people","g":"percent of community population","h":"percent of grain output decline"}.get(code_l[-1],"")
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
    "note":r.mapping_status,"unit":r.unit,"caveat":r.caveat} for r in fs.itertuples()]})
 (ROOT/"site-prototype"/"dist"/"community_exposures_v1.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"concepts={len(items)}; mappings={len(out)}; all wave=2011; module=Community")
if __name__=="__main__": main()
