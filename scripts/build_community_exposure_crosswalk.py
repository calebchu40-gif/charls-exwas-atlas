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
 "community_population_hukou_profile":("Community population and household-registration profile","Community social context","Community-informant aggregate counts from 2009–2010. Preserve each residence-duration, local/nonlocal hukou, person/household count and reference year separately; source denominators are not interchangeable, so do not derive rates or totals without validating the official release. These are community context, not the sampled participant's residence or hukou."),
 "community_short_term_migrant_population":("Community short-term migrant population","Community migration context","Community-informant count of people living in the village/community for less than half a year at the end of 2010. This is not a CHARLS respondent's migration history; do not combine with the more-than-half-year resident or hukou counts without confirming mutually exclusive definitions and denominators."),
 "community_age_sex_structure":("Community age and sex composition","Community social context","2011 community-informant counts of adults aged 16+, people aged 65+, and people aged 80+, with separate reported male counts. Preserve nested age thresholds and reference population; do not sum the 65+ and 80+ counts or derive individual age/sex values."),
 "community_never_married_over40_population":("Community count of never-married people aged over 40","Community social context","2011 community-informant count for the questionnaire's over-40 never-married group and a separate male count. The English/Chinese item wording and informant-reported aggregate do not identify any participant's marital status; preserve the published item definition pending release validation."),
 "community_ethnic_minority_household_profile":("Community ethnic-minority presence and household counts","Community social context","2011 community-informant report of whether minority groups are present, how many groups, and household counts for the largest, second-largest and remaining groups. The counts have no population denominator and must not be summed into a percentage without release-level validation. Minority names are open text and are excluded from E/P display."),
 "community_water_price":("Community-reported average water price","Community environment","2011 community-reported current average water unit price in RMB yuan per ton; community context, not an individual's household bill."),
 "community_electricity_price":("Community-reported average electricity price","Community environment","2011 community-reported current average electricity unit price in RMB yuan per degree (kWh); community context, not an individual's household bill."),
 "community_road_presence":("Road access through the village/community","Community environment","2011 community-informant Yes/No report of roads passing through the village/community; single-wave context indicator."),
 "community_road_cleanliness":("Community road tidiness","Community environment","2011 community-informant 1-7 ordinal assessment anchored from very dirty to very tidy; subjective road-condition perception, not an environmental sampling measure."),
 "community_observed_socioeconomic_status":("Observed community socioeconomic status","Community social context","2011 interviewer observation on a 1–7 ordinal scale anchored from poor to rich. This is a fieldworker's overall community judgment, not household income or an objective area-level economic statistic."),
 "community_built_form_organization":("Community built-form organization","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from very disorganized to very organized. This is a subjective community-level built-environment proxy, not a standardized urban-form assessment."),
 "community_observed_crowding":("Observed community crowding/sparsity","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from very crowded to very sparse; higher values indicate less perceived crowding. This is not a measured population density."),
 "community_accessibility_observation":("Observed community accessibility for people with disabilities","Community environment","2011 interviewer observation on a 1–7 ordinal scale anchored from no handicapped access to very convenient. Higher values indicate better perceived access; this is not an audited accessibility standard."),
 "community_primary_school_change":("Primary-school merger or relocation history","Community social context","2011 community-level report of primary-school merger/relocation, reported year and prior school count; historical service-access context, not an individual's schooling history."),
 "community_land_institutional_transition_history":("Community land-institutional transition history","Community social and policy context","2011 retrospective report by 2–3 older community-history informants of village-level institutional dates and land-allocation/subcontracting policy transitions. Retain each event and year separately; V-only routing and recall limitations apply. Not an individual's land tenure or household landholding."),
 "community_sent_down_youth_migration_history":("Sent-down youth migration to the community","Community migration history","2011 retrospective community-history informant report of counts, timing and origin of rusticated youth; multiple older informants were asked to recall village history. This is not the respondent's own migration or cohort-member exposure; preserve counts, years and origin as distinct components."),
 "community_barefoot_doctor_capacity_history":("Historical barefoot-doctor availability","Community healthcare history","Community-history informants' retrospective estimate of the number of barefoot doctors in the village during the 1970s. This is a recalled community workforce count, not individual care use or current service availability."),
 "community_military_service_history":("Community military-service counts by historical period","Community social history","Community-history informants report counts of residents who joined the army across questionnaire-defined years/periods. Counts have no population denominator and are not individual military service histories."),
 "community_university_admission_history":("Community university-admission counts by historical period","Community social history","Community-history informants report counts of residents admitted to university across questionnaire-defined years/periods. Counts have no population denominator and are not individual educational attainment."),
 "community_family_planning_policy_history":("Community family-planning policy history","Community policy context","Retrospective community-history report of policy start, Han/minority policy categories, policy changes and the 1970s 'late, sparse, few' policy. Preserve historical and current-policy items separately; this is not an individual's fertility, reproductive history, or policy exposure duration."),
 "community_unplanned_birth_penalty_policy_history":("Community unplanned-birth penalty policy history","Community policy context","Retrospective report of whether/when a village-level penalty policy existed and reported initial/subsequent penalty amounts. Preserve conditional routes and year/amount slots; this is not an individual's fine or reproductive history."),
 "community_identity_card_rollout_history":("Community identity-card rollout timing","Community modernization context","Community-history informants' recalled years when residents began receiving first- and second-generation national identity cards. This is a community-level administrative modernization marker, not an individual's verified identity-document history."),
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
 "community_farm_subsidy_program":("Community agricultural subsidy program context","Community agricultural-policy context","2011 village-only report of whether agricultural subsidies were implemented, their start year, the number of village households receiving subsidies in 2010, and the average standard per mu. The questionnaire names grain direct payments, improved-seed subsidies, farm-machinery purchase subsidies and comprehensive agricultural-input subsidies as examples. This is broad local policy context, not a specific pesticide/fertilizer measure, household receipt linkage or individual exposure."),
 "community_unemployment_subsidy_program":("Community unemployment subsidy program context","Community social-policy context","2011 community-informant report of whether unemployment subsidies existed, when they began, the number of people receiving them in 2010, and the average monthly standard. These are community-level program and uptake measures; they do not establish sampled-household receipt or individual income."),
 "community_minimum_living_allowance_program":("Community minimum living allowance context","Community social-policy context","2011 community-informant report of whether minimum living allowance existed, its start year, and the number of people receiving it in 2010. The JG008 amount prompt appears to carry an unemployment-subsidy wording conflict and is excluded from this concept pending source resolution. These fields describe local social protection coverage, not sampled-household eligibility, receipt, or individual income."),
 "community_single_child_reward_program":("Community single-child family reward program context","Community social-policy context","2011 community-informant report of whether the community provided rewards to parents of a single child, the start year, number of recipient households in 2010, and monthly standard. This does not establish sampled-household eligibility or receipt, nor individual fertility history."),
 "community_pension_65plus_program":("Community pension subsidy for adults over 65 context","Community social-policy context","2011 community-informant report of the over-65 pension subsidy program, its start year, 2010 recipient count and monthly standard. It is distinct from the over-80 subsidy and named rural pension systems; it does not establish sampled-person eligibility or receipt."),
 "community_pension_80plus_subsidy_program":("Community subsidy for adults over 80 context","Community social-policy context","2011 community-informant report of the over-80 subsidy program, its start year, 2010 recipient count and monthly standard. Preserve the age-specific program as separate from the over-65 pension and named rural pension systems; it is not an individual's receipt status."),
 "community_nrps_program":("Community New Rural Pension System context","Community social-policy context","2011 village-only report of whether the New Rural Pension System (NRPS) was implemented, its start year, 2010 recipient count and monthly standard. Keep distinct from the Old Rural Pension System; do not infer individual enrollment, contribution or receipt."),
 "community_orps_program":("Community Old Rural Pension System context","Community social-policy context","2011 village-only report of whether the Old Rural Pension System (ORPS) was implemented, its start year, 2010 recipient count and monthly standard. Keep distinct from NRPS and age-targeted subsidy programs; do not infer individual enrollment, contribution or receipt."),
 "community_other_subsidy_program_roster":("Other community subsidy program roster","Community social-policy context","2011 community-informant roster of other poverty-related subsidy programs, with up to five emitted response/name/start/count/standard slots. Field suffixes and nested name fields are preserved exactly; the flattened questionnaire/Codebook do not fully document slot-to-name linkage, so verify field pairing and repeat behavior in the authorized release before analysis. Open-text program names are not standardized policy categories. These are community reports, not household receipt or individual income."),
 "community_urban_resident_medical_insurance_context":("Community urban-resident medical insurance program context","Community healthcare policy","2011 community-reported availability, start year, cumulative annual household participation counts (2005–2010), and annual premium for urban resident medical insurance handled through the community. The questionnaire conditions follow-ups on JF010 option 1; preserve the selection route and source year for each cumulative count. These are community aggregates, not sampled-household enrollment or individual premium/coverage."),
 "community_rural_cooperative_medical_insurance_context":("Community rural cooperative medical insurance program context","Community healthcare policy","2011 community-reported availability, start year, cumulative annual household participation counts (2003–2010), and annual premium for the New Rural Cooperative Medical Insurance program. The questionnaire conditions follow-ups on JF010 option 2; preserve the selection route and source year for each cumulative count. These are community aggregates, not sampled-household enrollment or individual premium/coverage."),
 "community_eldercare_center_context":("Community-based elderly care center context","Community healthcare and social-care access","2011 community-informant report of community-based elderly care center availability (CAPI community-only), area, number of older users, listed services, annual user fee and funding source. JB030 No routes past the center details; preserve that denominator. These are community-level service context measures, not participant-level service use or quality."),
 "community_home_eldercare_context":("Village/home-based elder-care context","Community healthcare and social-care access","2011 community/village-level elder-care context: share of households employing a live-in caregiver for an older person (JB036), and village-only home-based elder-care service station availability and number served (JB037–JB038). Keep the community and village routes distinct; these are contextual reports, not individual caregiving exposure or service receipt."),
 "community_economic_activity_and_fiscal_context":("Community economic activity and fiscal context","Community socioeconomic context","2010 community/village-informant reports of agricultural and industrial revenue, village public expenditure, total village income, net investment, and per-capita net income. Preserve the distinct constructs, reporting units, reference year, and village-only routes; these are aggregate contextual candidates, not household income or audited accounts."),
 "community_housing_market_context":("Community housing-market context","Community socioeconomic context","2011 informant estimates of new/used apartment price, two-bedroom monthly rent, share of households renting out a home, and share living in market-purchased commercial housing. These are community-level contextual measures, not the sampled household's property value, rent, or housing tenure; preserve distinct units and validate special values."),
 "community_formal_credit_access":("Community formal-credit access context","Community socioeconomic context","2010 village-level share of farmers obtaining formal-institution loans and an ordinal community report of household borrowing difficulty relative to three years earlier. Keep percentage and ordinal response separate; these do not establish an individual household's credit access or debt."),
 "community_agricultural_machinery_supply_origin":("Community agricultural machinery supply origin","Community agricultural context","2011 village-only informant report of where rented large agricultural machinery is sourced: locally, elsewhere in the province, or another province. Asked only on the rented-machinery route; this is a contextual service-supply indicator, not personal machinery use, pesticide exposure, or ambient pollution."),
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
 "community_population_hukou_profile":["jc001","jc002","jc003","jc003_1","jc004","jc004_1","jc005","jc005_1","jc007","jc008"],
 "community_short_term_migrant_population":["jc006"],
 "community_age_sex_structure":["jc009","jc009_1","jc010","jc010_1","jc011","jc011_1"],
 "community_never_married_over40_population":["jc012","jc012_1"],
 "community_ethnic_minority_household_profile":["jc013","jc013_1","jc015","jc017","jc018"],
 "community_water_price":["jj023"],
 "community_electricity_price":["jj024"],
 "community_road_presence":["jk001"],
 "community_road_cleanliness":["jk003"],
 "community_observed_socioeconomic_status":["jk002"],
 "community_built_form_organization":["jk004"],
 "community_observed_crowding":["jk005"],
 "community_accessibility_observation":["jk006"],
 "community_primary_school_change":["jh015","jh016","jh017"],
 "community_land_institutional_transition_history":["jh003","jh004","jh005","jh006","jh007","jh008","jh008_1"],
 "community_sent_down_youth_migration_history":["jh009","jh010","jh011","jh012","jh013","jh013_1","jh013_2"],
 "community_barefoot_doctor_capacity_history":["jh014"],
 "community_military_service_history":[*[f"jh018_1_{i}_" for i in range(1,12)]],
 "community_university_admission_history":[*[f"jh018_2_{i}_" for i in range(1,12)]],
 "community_family_planning_policy_history":["jh019","jh020","jh021","jh022","jh023","jh024","jh025","jh030"],
 "community_unplanned_birth_penalty_policy_history":["jh026","jh026_1","jh027","jh028",*[f"jh029a_{i}_" for i in range(1,4)],*[f"jh029b_{i}_" for i in range(1,4)]],
 "community_identity_card_rollout_history":["jh032","jh033"],
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
 "community_farm_subsidy_program":["jg017","jg018","jg019","jg020"],
 "community_unemployment_subsidy_program":["jg001","jg002","jg003","jg004"],
 "community_minimum_living_allowance_program":["jg005","jg006","jg007"],
 "community_single_child_reward_program":["jg013","jg014","jg015","jg016"],
 "community_pension_65plus_program":["jg025","jg026","jg027","jg028"],
 "community_pension_80plus_subsidy_program":["jg029","jg030","jg031","jg032"],
 "community_nrps_program":["jg033","jg034","jg035","jg036"],
 "community_orps_program":["jg037","jg038","jg039","jg040"],
 "community_other_subsidy_program_roster":[*[f"jg009_{i}_" for i in range(1,6)],*[f"jg009_1_{i}_" for i in range(1,6)],*[f"jg010_{i}_" for i in range(1,6)],*[f"jg011_{i}_" for i in range(1,6)],*[f"jg012_{i}_" for i in range(1,6)]],
 "community_urban_resident_medical_insurance_context":["jf010s1","jf011",*[f"jf012_{i}" for i in range(1,7)],"jf013"],
 "community_rural_cooperative_medical_insurance_context":["jf010s2","jf014",*[f"jf015_{i}" for i in range(1,9)],"jf016"],
 "community_eldercare_center_context":["jb030","jb031","jb032","jb033s1","jb033s2","jb033s3","jb033s4","jb034","jb035"],
 "community_home_eldercare_context":["jb036","jb037","jb038"],
 "community_economic_activity_and_fiscal_context":["jj011","jj012","jj013","jj014","jj015","jj016"],
 "community_housing_market_context":["jj026","jj027","jj028","jj029","jj030"],
 "community_formal_credit_access":["jj031","jj032"],
 "community_agricultural_machinery_supply_origin":["jj005"],
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
 "community_population_hukou_profile","community_short_term_migrant_population","community_age_sex_structure",
 "community_never_married_over40_population","community_ethnic_minority_household_profile",
 "community_road_cleanliness","community_observed_socioeconomic_status",
 "community_built_form_organization","community_observed_crowding",
 "community_accessibility_observation","community_disaster_history","community_sanitation_reconstructed",
 "community_primary_school_change","community_land_institutional_transition_history",
 "community_sent_down_youth_migration_history","community_barefoot_doctor_capacity_history",
 "community_military_service_history","community_university_admission_history",
 "community_family_planning_policy_history","community_unplanned_birth_penalty_policy_history",
 "community_identity_card_rollout_history",
 "community_land_use_profile","community_main_terrain","community_agricultural_mechanization",
 "community_fertilizer_seed_inputs","community_food_prices","community_household_energy_prices",
 "community_major_crop_production",
 "community_household_amenity_penetration",
 "community_historical_disaster_epidemic_severity",
 "community_reforestation_subsidy_program",
 "community_farm_subsidy_program",
 "community_unemployment_subsidy_program",
 "community_minimum_living_allowance_program",
 "community_single_child_reward_program",
 "community_pension_65plus_program","community_pension_80plus_subsidy_program",
 "community_nrps_program","community_orps_program",
 "community_other_subsidy_program_roster",
 "community_urban_resident_medical_insurance_context","community_rural_cooperative_medical_insurance_context",
 "community_eldercare_center_context","community_home_eldercare_context",
 "community_economic_activity_and_fiscal_context","community_housing_market_context","community_formal_credit_access",
 "community_agricultural_machinery_supply_origin",
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
 other_subsidy_codes=set(MAP["community_other_subsidy_program_roster"])
 insurance_codes=set(MAP["community_urban_resident_medical_insurance_context"]+MAP["community_rural_cooperative_medical_insurance_context"])
 codes={code for cid in ("community_land_use_profile","community_main_terrain","community_agricultural_mechanization","community_fertilizer_seed_inputs","community_food_prices","community_household_energy_prices","community_major_crop_production","community_household_amenity_penetration","community_historical_disaster_epidemic_severity","community_reforestation_subsidy_program","community_farm_subsidy_program","community_unemployment_subsidy_program","community_minimum_living_allowance_program","community_single_child_reward_program","community_pension_65plus_program","community_pension_80plus_subsidy_program","community_nrps_program","community_orps_program","community_eldercare_center_context","community_home_eldercare_context","community_economic_activity_and_fiscal_context","community_housing_market_context","community_formal_credit_access","community_agricultural_machinery_supply_origin","community_primary_school_change","community_land_institutional_transition_history","community_sent_down_youth_migration_history","community_barefoot_doctor_capacity_history","community_military_service_history","community_university_admission_history","community_family_planning_policy_history","community_unplanned_birth_penalty_policy_history","community_identity_card_rollout_history") for code in MAP[cid]}
 codes.update(code for cid in ("community_population_hukou_profile","community_short_term_migrant_population","community_age_sex_structure","community_never_married_over40_population","community_ethnic_minority_household_profile") for code in MAP[cid])
 for code in codes:
  code_norm="".join(ch for ch in code.casefold() if ch.isalnum())
  q_norm="".join(ch for ch in q if ch.isalnum())
  cb_norm="".join(ch for ch in cb if ch.isalnum())
  questionnaire_code = code.split("s", 1)[0] if code.lower().startswith("jb033s") else code
  questionnaire_code_norm="".join(ch for ch in questionnaire_code.casefold() if ch.isalnum())
  if questionnaire_code_norm not in q_norm or code_norm not in cb_norm:
   raise ValueError(f"Official 2011 community questionnaire/Codebook missing mapped field {code}")
 for code in other_subsidy_codes:
  code_norm="".join(ch for ch in code.casefold() if ch.isalnum())
  cb_norm="".join(ch for ch in cb if ch.isalnum())
  if code_norm not in cb_norm:
   raise ValueError(f"Official 2011 Codebook missing slot-indexed other-subsidy field {code}")
 cb_norm="".join(ch for ch in cb if ch.isalnum())
 for code in insurance_codes:
  code_norm="".join(ch for ch in code.casefold() if ch.isalnum())
  if code_norm not in cb_norm:
   raise ValueError(f"Official 2011 Codebook missing community insurance field {code}")
 if "does your village/community have other subsidies" not in q or "for every answer in jg009_1" not in q:
  raise ValueError("Official questionnaire's other-subsidy prompt/repeat instruction missing")
 if ("which of the following types of insurance are provided through the community" not in q
     or "if chosen, answer jf011 - jf013" not in q or "if chosen, answer jf014 - jf016" not in q
     or "how many households in your village/community participated in urban resident medical insurance" not in q
     or "how many households in your village/community participated in rural cooperative medical insurance" not in q):
  raise ValueError("Official questionnaire's community health-insurance routes or participation items missing")
 q_alnum="".join(ch for ch in q if ch.isalnum())
 if any(phrase not in q_alnum for phrase in (
     "doesyourcommunityhavecommunitybasedelderlycarecenter",
     "skiptojb036",
     "whatservicesareprovidedcircleallthatapply",
     "howmucheachelderneedtopayforit",
     "percentageofhouseholdsthathirenanny",
     "doesyourvillagehaveafamilybasedeldercarecenter",
     "howmanypersonsareserved")):
  raise ValueError("Official questionnaire's elder-care items/routes missing")
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
  "does your village have farm subsidies",
  "when did farm subsidies start to be implemented in this village",
  "how many households in this village received farm subsidies in year 2010",
  "does your village/community have unemployment subsidies",
  "how many people in this village/community re ceived unemployment subsidies in year 2010",
  "does your village/community have minimum living allowance",
  "does your village/community have subsidies for being parents of single child",
  "does your village/community issue pension to persons older than 65",
  "does your village/community have subsidy for persons older than 80",
  "does your village have the new rural pension system",
  "does your village have the old rural pension system",
  "skip to jg029",
  "skip to jg033",
  "skip to jg036",
  "2010",
  "yuan/month",
  "square meters",
  "persons",
  "yuan/year",
  "percentage of households",
 )
 for phrase in required_q:
  phrase_norm="".join(ch for ch in phrase if ch.isalnum())
  q_norm="".join(ch for ch in q if ch.isalnum())
  if phrase_norm not in q_norm:
   raise ValueError(f"Official 2011 community questionnaire wording missing: {phrase}")
 if "ja012" not in cb or "among arable land, how many is irrigatable" not in cb or "among arable land, how many is paddy field" not in q:
  raise ValueError("JA012 questionnaire/Codebook wording conflict not found")
 for label in ("1 plain","2 hill","3 mountainous region"):
  label_norm="".join(ch for ch in label if ch.isalnum())
  if label_norm not in "".join(ch for ch in q if ch.isalnum()) or label_norm not in "".join(ch for ch in cb if ch.isalnum()):
   raise ValueError(f"JA038 terrain category missing from official source: {label}")
 if "4" not in q or "高原" not in q or "4 plateau" not in cb or "5" not in q or "盆地" not in q or "5 basin" not in cb:
  raise ValueError("JA038 code 4/5 terrain bilingual source anchor not found")
 q_alnum="".join(ch for ch in q if ch.isalnum())
 if any(term not in q_alnum for term in ("whatwasthetotalpopulationwholiveinyourvillagecommunityformorethanhalfayear",
      "howmanyofthemhavenonagriculturehukou","totalmigrantpopulationwholivelessthanhalfayear",
      "totalnumberofpopulationaged65andover","bachelorsagedabove40whohaveneverbeenmarried",
      "doesyourvillagecommunityhaveminorities","whichminorityhasthelargestpopulation")):
  raise ValueError("Official community population/hukou/minority questionnaire prompts missing")

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
    unit = ""
    if code_l.startswith("jb028_"):
     evidence="CHARLS 2011 Community Questionnaire, Part B p.10 (PDF p.13), JB028 facility table; corresponding codebook field label."
    elif cid in {"community_urban_resident_medical_insurance_context","community_rural_cooperative_medical_insurance_context"}:
     evidence="CHARLS 2011 Community Questionnaire, Part F, JF010 multiple-selection routes and program-specific JF011–JF016 follow-ups; start year, year-indexed cumulative household counts, and annual premium checked against official Codebook labels; frequencies omitted."
    elif cid in {"community_eldercare_center_context","community_home_eldercare_context"}:
     evidence="CHARLS 2011 Community Questionnaire, Part B pp.13–14 (PDF pp.16–17), JB030–JB038; community-only versus village-only routing, JB030 No-skip, listed services and units checked against official Codebook; frequencies omitted."
    elif cid in {"community_economic_activity_and_fiscal_context","community_housing_market_context","community_formal_credit_access"}:
     evidence="CHARLS 2011 Community Questionnaire, Part J pp.35–37 (PDF pp.38–40), JJ011–JJ032; reference year, village-only routes, aggregate units, and ordinal loan-difficulty wording checked against official Codebook; descriptive frequencies and extrema omitted."
    elif cid in {"community_population_hukou_profile","community_short_term_migrant_population","community_age_sex_structure","community_never_married_over40_population","community_ethnic_minority_household_profile"}:
     evidence="CHARLS 2011 Community Questionnaire, Part C pp.14–15 (PDF pp.17–18), JC001–JC018; community population/employment informant route, 2009/2010 reference periods, person-versus-household counts, age thresholds, hukou/residence definitions, minority skip route and official Codebook field labels reviewed; Codebook frequencies omitted."
    elif cid in {"community_primary_school_change","community_land_institutional_transition_history","community_sent_down_youth_migration_history","community_barefoot_doctor_capacity_history","community_military_service_history","community_university_admission_history","community_family_planning_policy_history","community_unplanned_birth_penalty_policy_history","community_identity_card_rollout_history"}:
     evidence="CHARLS 2011 Community Questionnaire, Part H pp.28–34 (PDF pp.31–37); retrospective community-history informant route, item-specific V-only scope, year bands, count units and skip logic reviewed against official Codebook field labels; frequencies and descriptive summaries omitted."
    elif cid == "community_agricultural_machinery_supply_origin":
     evidence="CHARLS 2011 Community Questionnaire, Part J p.35 (PDF p.38), JJ003–JJ005; village-only rented-machinery route, local/provincial origin categories, and conditional county/province text fields checked against official Codebook; frequencies omitted."
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
    elif cid == "community_farm_subsidy_program":
     evidence="CHARLS 2011 Community Questionnaire, Part G, village-only JG017–JG020; subsidy examples, No-skip route, 2010 household uptake count and stated per-mu unit checked against official Codebook labels; frequencies omitted."
    elif cid == "community_unemployment_subsidy_program":
     evidence="CHARLS 2011 Community Questionnaire, Part G, JG001–JG004; community-program prompt, 2010 person count and monthly subsidy unit checked against official Codebook labels; frequencies omitted."
    elif cid == "community_minimum_living_allowance_program":
     evidence="CHARLS 2011 Community Questionnaire, Part G, JG005–JG007; No-skip destination and 2010 person count checked against official Codebook labels. JG008's amount identity conflict is excluded; frequencies omitted."
    elif cid == "community_single_child_reward_program":
     evidence="CHARLS 2011 Community Questionnaire, Part G, JG013–JG016; No-skip route, 2010 recipient-household count and monthly standard checked against official Codebook labels; frequencies omitted."
    elif cid in {"community_pension_65plus_program","community_pension_80plus_subsidy_program","community_nrps_program","community_orps_program"}:
     evidence="CHARLS 2011 Community Questionnaire, Part G, JG025–JG040; age-specific subsidy and named rural-pension program routes, 2010 recipient counts, monthly units, and V-only flags checked against official Codebook labels; frequencies omitted."
    elif cid == "community_other_subsidy_program_roster":
     evidence="CHARLS 2011 Community Questionnaire, Part G, JG009–JG012 repeat instruction and slot-indexed Codebook fields; open-text names and emitted indices retained as written, 2010 recipient unit and monthly standard checked; slot linkage requires authorized-release validation; frequencies omitted."
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
    elif code_l == "jg001":
     caveat="Community-level Yes/No report of unemployment subsidies. Following items record program start, 2010 recipient count and monthly standard; do not infer a personal benefit or income from the community response."
    elif code_l == "jg002":
     unit="year"
     caveat="Year community unemployment subsidies began; preserve source routing and validate special values in the authorized release."
    elif code_l == "jg003":
     unit="persons"
     caveat="Number of people in the community reported to have received unemployment subsidies in 2010; this is not a count of sampled respondents or a linked individual receipt measure."
    elif code_l == "jg004":
     unit="Yuan/month"
     caveat="Community-reported average monthly unemployment-subsidy standard; not a sampled respondent's income or benefit amount."
    elif code_l == "jg005":
     caveat="Community-level Yes/No report of a minimum living allowance program. The official questionnaire says No skips to JG008; preserve this route rather than imputing JG006–JG007."
    elif code_l == "jg006":
     unit="year"
     caveat="Year the community minimum living allowance began; conditional route must be checked against the official JG005 response and authorized release."
    elif code_l == "jg007":
     unit="persons"
     caveat="Number of community members reported to have received minimum living allowance in 2010; not a linked sampled-person receipt status."
    elif code_l == "jg008":
     unit="Yuan/month"
    elif code_l == "jg013":
     caveat="Community-level Yes/No report of rewards for parents of a single child. A No response skips to JG017; this is not an individual's fertility history or household receipt measure."
    elif code_l == "jg014":
     unit="year"
     caveat="Year the community single-child-parent reward began; asked on the JG013 Yes route. Preserve the route and validate special values in the authorized release."
    elif code_l == "jg015":
     unit="households"
     caveat="Number of households reported to have received the single-child-parent reward in 2010; not a linked sampled-household receipt status."
    elif code_l == "jg016":
     unit="Yuan/month"
     caveat="Community-reported average monthly single-child-parent reward standard; not the sampled household's actual benefit."
    elif code_l == "jg017":
     caveat="Village-only Yes/No report of an agricultural-subsidy program, with examples including grain direct payments, improved seeds, machinery purchases and agricultural inputs. A No response skips JG018–JG020. This broad policy report does not establish a specific subsidy, household receipt, fertilizer/pesticide use or individual exposure."
    elif code_l == "jg018":
     unit="year"
     caveat="Year the village agricultural-subsidy program began, asked only after JG017=Yes. Preserve the route and validate special values in the authorized release."
    elif code_l == "jg019":
     unit="households"
     caveat="Number of village households reported to have received agricultural subsidies in 2010, conditional on JG017=Yes. Not the sampled household's receipt status or a population-standardized rate."
    elif code_l == "jg020":
     unit="Yuan/mu"
     caveat="Community-reported average agricultural-subsidy standard per mu, conditional on JG017=Yes. Do not treat it as an individual's payment or a chemical-use/exposure measure."
    elif code_l == "jg025":
     caveat="Community-level Yes/No report of a pension subsidy for persons older than 65. No routes to JG029; this is not an individual's age eligibility or receipt status."
    elif code_l == "jg026":
     unit="year"
     caveat="Year the community began the over-65 pension subsidy policy, conditional on JG025=Yes. Preserve the route and validate release-specific special values."
    elif code_l == "jg027":
     unit="persons"
     caveat="Number of persons older than 65 reported to have received this community pension subsidy in 2010; not linked to sampled respondents."
    elif code_l == "jg028":
     unit="Yuan/month"
     caveat="Community-reported average monthly over-65 pension subsidy standard; not an individual's benefit amount."
    elif code_l == "jg029":
     caveat="Community-level Yes/No report of a subsidy for persons older than 80. No routes to JG033; keep distinct from the over-65 pension and rural pension systems."
    elif code_l == "jg030":
     unit="year"
     caveat="Year the community began the over-80 subsidy, conditional on JG029=Yes. Preserve the route and validate release-specific special values."
    elif code_l == "jg031":
     unit="persons"
     caveat="Number of persons older than 80 reported to have received this subsidy in 2010; not linked to sampled respondents."
    elif code_l == "jg032":
     unit="Yuan/month"
     caveat="Community-reported average monthly over-80 subsidy standard; not an individual's benefit amount."
    elif code_l == "jg033":
     caveat="Village-only Yes/No report of New Rural Pension System implementation. The questionnaire routes No to JG036, which skips JG034–JG035; preserve this unusual route and do not interpret the later standard as proof of NRPS enrollment or receipt."
    elif code_l == "jg034":
     unit="year"
     caveat="Year the village began the New Rural Pension System, asked on the JG033=Yes route. Village-only; verify the route in the authorized release."
    elif code_l == "jg035":
     unit="persons"
     caveat="Number of persons reported to have received pension through NRPS in 2010, conditional on village program route; not linked to sampled respondents."
    elif code_l == "jg036":
     unit="Yuan/month"
     caveat="Community-reported average monthly subsidy standard. The questionnaire routes JG033=No directly here, so item applicability is ambiguous; preserve separately and do not assume it measures NRPS recipients only."
    elif code_l == "jg037":
     caveat="Village-only Yes/No report of Old Rural Pension System implementation. Keep distinct from NRPS and age-targeted subsidy programs; it does not establish individual enrollment or receipt."
    elif code_l == "jg038":
     unit="year"
     caveat="Year the village began the Old Rural Pension System, conditional on JG037=Yes. Village-only; verify the route in the authorized release."
    elif code_l == "jg039":
     unit="persons"
     caveat="Number of persons reported to have received pension through ORPS in 2010, conditional on village program route; not linked to sampled respondents."
    elif code_l == "jg040":
     unit="Yuan/month"
     caveat="Community-reported average monthly ORPS subsidy standard, conditional on village program route; not an individual's benefit amount."
    elif code_l.startswith("jg009_"):
     caveat="Slot-indexed response or open-text name field in the 2011 other community poverty-subsidy roster. The questionnaire says No routes to JG013; preserve the exact suffix and verify repeat/name-field linkage against the authorized release. Do not infer a standardized program type."
    elif code_l.startswith("jg010_"):
     caveat="Slot-indexed start year for a community-reported other subsidy. The flattened source does not establish which open-text name slot it pairs with; verify repeat linkage and route in the authorized release."
    elif code_l.startswith("jg011_"):
     caveat="Slot-indexed count of households reported to have received an other community subsidy in 2010. Verify which name/program slot it pairs with; not linked to sampled households."
    elif code_l.startswith("jg012_"):
     caveat="Slot-indexed average monthly standard for an other community subsidy. Verify which open-text name/program slot it pairs with; not an individual's benefit amount."
    elif code_l in {"jf010s1", "jf010s2"}:
     caveat="Community-level multiple-selection insurance channel. Urban-resident insurance follow-ups JF011–JF013 apply only to option 1; rural cooperative insurance follow-ups JF014–JF016 apply only to option 2. Preserve selected-option storage and do not infer household or individual enrollment."
    elif code_l == "jf011":
     unit="year"
     caveat="Year the community began providing urban resident medical insurance, asked only when JF010 option 1 is selected. Community policy timing, not an individual's enrollment start."
    elif code_l.startswith("jf012_"):
     unit="households"
     caveat="Community-reported cumulative household participation count in urban resident medical insurance for the year named by the source suffix (2005–2010). Conditional on JF010 option 1; preserve each year separately and do not treat as sampled-household enrollment."
    elif code_l == "jf013":
     unit="Yuan/year"
     caveat="Community-reported annual urban resident medical-insurance premium, conditional on JF010 option 1. Not the sampled participant's premium or benefit."
    elif code_l == "jf014":
     unit="year"
     caveat="Year the community began New Rural Cooperative Medical Insurance, asked only when JF010 option 2 is selected. Community policy timing, not an individual's enrollment start."
    elif code_l.startswith("jf015_"):
     unit="households"
     caveat="Community-reported cumulative household participation count in rural cooperative medical insurance for the year named by the source suffix (2003–2010). Conditional on JF010 option 2; preserve each year separately and do not treat as sampled-household enrollment."
    elif code_l == "jf016":
     unit="Yuan/year"
     caveat="Community-reported annual rural cooperative medical-insurance premium, conditional on JF010 option 2. Not the sampled participant's premium or benefit."
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
     caveat="2011 village-informant estimate of the share of households with fixed telephones, one or more cell phones, televisions, and refrigerators. These are aggregate community percentages, not confirmed ownership or use by the sampled household or individual; preserve each amenity separately."
    elif code_l in {"jh003","jh004","jh005","jh007","jh008","jh008_1","jh010","jh012","jh016","jh019","jh023","jh026_1","jh032","jh033"} or code_l.startswith("jh029a_"):
     unit="year"
    elif code_l in {"jh009","jh011","jh014"} or code_l.startswith("jh018_"):
     unit="people"
    elif code_l == "jh027" or code_l.startswith("jh029b_"):
     unit="Yuan"
    elif code_l.startswith("ji003_"):
     suffix=code_l[-1]
     unit={"b":"year","c":"month","d":"year","e":"month","f":"people","g":"percent of community population","h":"percent of grain output decline"}.get(suffix,"")
     caveat="Retrospective record for one of the three most severe natural disasters/epidemics reported since 1945; retain event rank, date components and impact fields separately. Community-level long-recall measure, not an individual's verified direct exposure."
    if code_l.startswith(("jh018_1_","jh018_2_")):
     period_index=int(code_l.split("_")[2])
     period_labels={1:"2010",2:"2009",3:"2008",4:"2007",5:"2006",6:"2000–2005",7:"1996–2000",8:"1990–1995",9:"1986–1990",10:"1981–1985",11:"1977–1980"}
     caveat += f" Source slot {period_index} corresponds to questionnaire period {period_labels.get(period_index, 'unresolved')}; do not pool periods or divide by an unverified population denominator."
    if code_l.startswith(("jb006_", "jb007_")):
     unit="households"
    elif code_l == "jg023":
     unit="households"
    elif code_l == "jg022":
     unit="year"
    elif code_l == "jg024":
     unit="Yuan/mu"
    elif code_l == "jg018":
     unit="year"
    elif code_l == "jg019":
     unit="households"
    elif code_l == "jg020":
     unit="Yuan/mu"
    elif code_l.startswith("jg010_"):
     unit="year"
    elif code_l.startswith("jg011_"):
     unit="households"
    elif code_l.startswith("jg012_"):
     unit="Yuan/month"
    elif code_l in {"jf011", "jf014"}:
     unit="year"
    elif code_l.startswith(("jf012_", "jf015_")):
     unit="households"
    elif code_l in {"jf013", "jf016"}:
     unit="Yuan/year"
    elif code_l in {"jg026", "jg030", "jg034", "jg038"}:
     unit="year"
    elif code_l in {"jg027", "jg031", "jg035", "jg039"}:
     unit="persons"
    elif code_l in {"jg028", "jg032", "jg036", "jg040"}:
     unit="Yuan/month"
    elif code_l in {"jg002", "jg006", "jg014"}:
     unit="year"
    elif code_l in {"jg003", "jg007"}:
     unit="persons"
    elif code_l in {"jg004", "jg008", "jg016"}:
     unit="Yuan/month"
    elif code_l == "jg015":
     unit="households"
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
    elif code_l in {"jc001","jc002","jc003","jc004","jc005","jc006","jc007","jc008","jc009","jc009_1","jc010","jc010_1","jc011","jc011_1","jc012","jc012_1","jc013_1"}:
     unit="people"
    elif code_l in {"jc003_1","jc004_1","jc005_1","jc015","jc017","jc018"}:
     unit="households"
    elif code_l in {"jc019","jc020","jc021","jc022","jc023","jc024"}:
     unit="percent of community adults"
    elif code_l in {"jc019_1","jc020_1","jc021_1","jc022_1","jc023_1","jc024_1"}:
     unit="percent bracket (fallback category)"
    elif code_l == "jj023":
     unit="RMB yuan/ton"
    elif code_l == "jj024":
     unit="RMB yuan/kWh"
    elif code_l == "jb031":
     unit="square meters"
    elif code_l in {"jb032", "jb038"}:
     unit="persons"
    elif code_l == "jb034":
     unit="Yuan/year"
    elif code_l == "jb036":
     unit="percent of community households"
    elif code_l in {"jj011","jj012"}:
     unit="10,000 Yuan"
    elif code_l in {"jj013","jj014","jj015","jj016","jj026","jj027"}:
     unit="Yuan" if code_l in {"jj013","jj014","jj015","jj016"} else "Yuan/m²"
    elif code_l == "jj028":
     unit="Yuan/month"
    elif code_l in {"jj029","jj030","jj031"}:
     unit="percent"
    if cid == "community_population_hukou_profile":
     details={
      "jc001":"2010 year-end usual residents living in the community for more than half a year",
      "jc002":"people among JC001 with non-agricultural household registration",
      "jc003":"2010 usual residents with local household registration",
      "jc003_1":"households associated with the JC003 local-hukou count",
      "jc004":"2010 usual residents without local household registration",
      "jc004_1":"households associated with the JC004 nonlocal-hukou count",
      "jc005":"2010 people with local household registration who did not live locally for more than half a year",
      "jc005_1":"households associated with the JC005 nonresident local-hukou count",
      "jc007":"2009 year-end usual residents living locally for more than half a year",
      "jc008":"people among JC007 with local household registration",
     }
     caveat=f"Community-informant aggregate count: {details[code_l]}. Reference year and residence/hukou definition are field-specific. Person and household counts are not interchangeable; do not infer respondent hukou or derive rates without validating denominator consistency and authorized-release special values."
    elif cid == "community_short_term_migrant_population":
     caveat="Community-informant count of people living locally for less than half a year at 2010 year-end. This is distinct from JC001's more-than-half-year resident population and is not a sampled participant's migration history; do not combine counts without validation."
    elif cid == "community_age_sex_structure":
     details={"jc009":"people aged 16 and over","jc009_1":"male count within the JC009 adult population","jc010":"people aged 65 and over","jc010_1":"male count within the JC010 65+ population","jc011":"people aged 80 and over","jc011_1":"male count within the JC011 80+ population"}
     caveat=f"Community-informant aggregate count: {details[code_l]}. Preserve the nested age threshold and separate sex count; do not sum 65+ and 80+ groups or interpret as participant-level demographic data."
    elif cid == "community_never_married_over40_population":
     caveat="Community-informant count for the questionnaire's never-married population aged over 40 and a separate male count, as labelled in the official source. This aggregate item does not establish any sampled participant's marital status; verify release coding and denominator before analysis."
    elif cid == "community_ethnic_minority_household_profile":
     details={"jc013":"whether any ethnic-minority groups are reported in the community","jc013_1":"number of different minority groups, asked after a Yes response","jc015":"households in the largest minority group","jc017":"households in the second-largest minority group","jc018":"households in all other minority groups"}
     caveat=f"Community-informant aggregate: {details[code_l]}. JC014/JC016 minority names are open text and excluded from E/P; JC013=No routes to JC019, so downstream blanks are structural rather than No. Do not sum household counts or infer individual ethnicity."
    elif cid == "community_eldercare_center_context":
     if code_l == "jb030": caveat="Community-only CAPI item reporting whether a community-based elderly care center exists. No routes to JB036, skipping JB031–JB035; structural absence is not zero or a negative response. Community aggregate, not individual service use."
     elif code_l in {"jb031", "jb032"}: caveat=f"Conditional community-level {('center area in square meters' if code_l == 'jb031' else 'number of older people using the center')}, asked only after JB030=Yes; preserve the route and validate special values in the authorized release."
     elif code_l.startswith("jb033s"): caveat="Separate multiple-response service slot for a community-based elderly care center (health care, entertainment activities, exercise equipment, or other). Slots are distinct; do not treat their numeric suffixes as an ordinal score. Conditional on JB030=Yes."
     elif code_l == "jb034": caveat="Annual fee per older user of the community-based center, in Yuan/year; the questionnaire explicitly instructs 0 when services are free. Conditional on JB030=Yes; validate special values in the authorized release."
     elif code_l == "jb035": caveat="Reported funding source(s) for establishing/running the community center. Preserve official nominal categories and conditional JB030=Yes route; this is not a participant's benefit or household expenditure."
    elif cid == "community_home_eldercare_context":
     if code_l == "jb036": caveat="Community-informant estimate of the percentage of households employing a live-in nanny to care for an older person; aggregate context, not respondent household status. Verify scale and special values in the authorized release."
     elif code_l == "jb037": caveat="Village-only Yes/No report of a family-based elder-care service station. No routes to JB039; village/community service availability, not individual receipt."
     elif code_l == "jb038": caveat="Number of older people served by the village family-based elder-care station, conditional on JB037=Yes; preserve route and validate special values in the authorized release."
    elif cid == "community_economic_activity_and_fiscal_context":
     economic_notes={
      "jj011":"2010 village-only total agricultural revenue, in ten-thousand Yuan",
      "jj012":"2010 village/community total industrial revenue, in ten-thousand Yuan",
      "jj013":"2010 village-only public expenditure, including public facilities and welfare, in Yuan",
      "jj014":"2010 village-only total village income, including government fiscal transfers, village-run enterprise income and raised funds; explicitly excludes residents' household income",
      "jj015":"2010 village-only total net investment, in Yuan",
      "jj016":"2010 village/community per-capita net income, in Yuan",
     }
     caveat=f"Community-informant aggregate: {economic_notes[code_l]}. Retain the distinct construct and confirm scale/special values in the authorized release; do not interpret as the respondent's or household's own income/wealth."
    elif cid == "community_housing_market_context":
     housing_notes={
      "jj026":"local average new-apartment price per square metre",
      "jj027":"local average used-apartment price per square metre",
      "jj028":"local average monthly rent for a two-bedroom apartment",
      "jj029":"estimated share of households that rent out their home",
      "jj030":"estimated share living in commercial housing bought through the market",
     }
     caveat=f"Community-informant housing-market estimate: {housing_notes[code_l]}. This is not the sampled household's property value, rent, purchase or tenure; preserve the item unit and verify scale/special values in the authorized release."
    elif cid == "community_formal_credit_access":
     caveat="Village-only informant report; JJ031 is the 2010 proportion of farmers receiving formal-institution loans, while JJ032 is an ordinal comparison of household loan access with three years earlier. The questionnaire's English lender wording and Chinese credit-cooperative wording differ; retain both and verify release-specific interpretation. Neither measures the sampled household's loan or debt."
    elif cid == "community_agricultural_machinery_supply_origin":
     caveat="Village-only report, conditional on JJ003=Yes (large machinery is rented); JJ005 distinguishes machinery sourced within the county/city, elsewhere in the province, or from another province. JJ005_1/JJ005_2 are route-specific open text/locality details, not standardized geography codes; preserve the source category and verify release linkage. This is community service-supply context, not individual use or chemical exposure."
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
