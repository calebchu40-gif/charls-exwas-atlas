"""Build a conservative food-resource and housing-environment field directory.

This is a codebook-catalog crosswalk, not a claim that all fields are comparable
or suitable for causal/association models. It deliberately separates individual
meal frequency, household food expenditure, and housing exposures.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ROOT / "audit" / "raw_variable_catalog_v1.csv"

CONCEPTS = {
    "individual_meal_frequency": ("Individual meal frequency", "Personal behavior",
        "Candidate item described as number/frequency of eating. Verify exact question, recall window, answer units, and respondent eligibility in the official wave questionnaire before treating as comparable."),
    "household_food_expenditure": ("Household food expenditure", "Household food resources",
        "Household expenditure, not an individual's dietary intake or nutrient biomarker. Verify recall period, currency/unit, exclusions, and equivalence across waves; wave 4/5 labels explicitly indicate exclusions."),
    "household_eating_out": ("Household eating-out expenditure", "Household food resources",
        "Household-level eating-out measure, not individual frequency or diet quality. Inspect questionnaire reference period and units by wave before harmonization."),
    "household_meal_size": ("People sharing household meals", "Household context",
        "Household/social context indicator, not dietary exposure. Wording changes between regularly sharing meals and people who ate meals in the past week."),
    "household_food_purchaser": ("Primary household food purchaser", "Household context",
        "Household role/decision context; not an environmental dose or individual food intake."),
    "toilet_access": ("Toilet access and sanitation", "Housing environment",
        "Separate number/distance/type/flushability fields. Do not collapse into one ordinal sanitation score without a prespecified, validated rule."),
    "running_water": ("Running water in residence", "Housing environment",
        "Residence-level water access indicator; distinguish from water source, treatment, and drinking-water quality."),
    "residential_heating": ("Residential heating availability", "Housing environment",
        "Residence-level heating availability; expenditure variables with similar code prefixes are different measures."),
    "heating_energy": ("Main heating energy source", "Housing environment",
        "Nominal fuel/source category; retain wave-specific value labels and never infer an ordered exposure scale."),
    "cooking_fuel_main": ("Main cooking fuel", "Housing environment",
        "Nominal primary cooking fuel; code and response categories change in later waves. See the separate value-label audit; do not treat numeric codes as ordered dose."),
    "air_cleaner": ("Air cleaner in home", "Housing environment",
        "2015-only candidate from the current catalog; availability/presence does not measure use, filtration performance, or ambient/personal PM exposure."),
    "waterworks_treatment": ("Water treated by waterworks", "Housing environment",
        "2020-only candidate in the current catalog; verify the exact questionnaire definition. It is not a direct drinking-water contaminant measurement."),
    "indoor_cleanliness": ("Interviewer-rated household cleanliness", "Indoor environment",
        "Interviewer-observed household condition; not an individual exposure measurement. Preserve the ordinal response and not-applicable category."),
    "indoor_temperature": ("Interviewer-rated indoor temperature", "Indoor environment",
        "Interviewer's categorical observation of household temperature, not a thermometer reading or personal thermal dose."),
    "floor_condition": ("Household floor condition", "Indoor environment",
        "2020-only interviewer observation: covered/flat, concrete, or uneven floor; household condition, not a clinical mobility outcome."),
    "housing_construction_year": ("Year dwelling was built", "Housing environment",
        "2011–2018 fields concern the year the dwelling was built; exact-year and fallback interval responses are separate fields. Do not include 2020 move-in time or impute a single year without a prespecified rule."),
    "residence_move_in_time": ("Time respondent moved into current housing", "Housing environment",
        "2020 asks when the Household Financial Respondent moved into the current housing, not when the building was constructed. Exact calendar year and fallback elapsed-time category are separate response fields; do not treat either as building age or combine without a validated response-format rule."),
    "dwelling_area": ("Dwelling area", "Housing environment",
        "Area wording/variables vary by wave (construction area, house size, usable area); units and target residence must be verified before cross-wave use."),
    "bedroom_count": ("Number of bedrooms", "Housing environment",
        "Household dwelling attribute; not a measure of crowding unless combined with household composition using a declared method."),
    "livingroom_count": ("Number of living rooms", "Housing environment",
        "Household dwelling attribute; room definitions may differ from usable area and bedrooms."),
    "building_structure": ("Building structure type", "Housing environment",
        "Nominal building category; preserve wave-specific value labels and do not assume ordinal levels."),
    "building_stories": ("Building levels and residence floor", "Housing environment",
        "Contains categorical structure/level/current-floor fields; elevator and floor position are separate variables, not one ordered exposure."),
    "elevator_access": ("Elevator availability", "Housing environment/accessibility",
        "Housing/building-level access feature; distinguish availability from actual use and respondent mobility."),
    "home_accessibility": ("Accessibility facilities in residence/building", "Housing environment/accessibility",
        "Presence of listed accessibility facilities; exact checklist and wave wording need value-label review."),
    "entrance_steps": ("Steps to main entrance", "Housing environment/accessibility",
        "Number/category of steps to entrance; may be top-coded or grouped and is not an individual stair-climbing performance test."),
    "electricity_access": ("Electricity in residence", "Housing environment/basic services",
        "Residence-level electricity availability; not household energy consumption or reliability."),
    "bathing_facility": ("In-house shower/bathing facility", "Housing environment/basic services",
        "Nominal categories distinguish centralized hot water, household water heater, or none; retain source categories."),
    "piped_gas_access": ("Coal/natural gas supply to residence", "Housing environment/basic services",
        "Availability of coal/natural-gas supply is not the same as the household's main cooking or heating fuel."),
    "air_cleaner_home": ("Air cleaner present in residence", "Indoor environment",
        "Presence does not measure use, filter condition, ventilation, indoor pollutant concentration, or personal exposure; wave interview mode differs."),
    "tap_water_access": ("Tap water in residence", "Housing environment/basic services",
        "2020 wording is tap-water access; not a direct drinking-water quality or contaminant measurement."),
}

# Explicit code-to-concept mapping; wave-specific codes are preserved as-is.
MAP = {
    "individual_meal_frequency": {2011: ["da058"], 2013: ["da058"]},
    "household_food_expenditure": {2011:["ge006"],2013:["ge006"],2015:["ge006"],2018:["ge006_w4"],2020:["gf006"]},
    "household_eating_out": {2011:["ge007"],2013:["ge007"],2015:["ge007"],2018:["ge007_w4"],2020:["gf009"]},
    "household_meal_size": {2011:["ge004"],2013:["ge004"],2015:["ge004"],2018:["ge004"],2020:["gf004"]},
    "household_food_purchaser": {2011:["ge001","ge002"],2013:["ge001","ge002"],2015:["ge001","ge002"],2018:["ge001","ge002"],2020:["gf002","gf003"]},
    "toilet_access": {2011:["i012_3","i013","i014s1","i014s2","i015"],2013:["i012_3","i013","i014s1","i014s2","i015"],2015:["i012_3","i013","i014s1","i014s2","i015"],2018:["i012_3","i013","i014","i015"],2020:["i011_3","i012","i013","i014"]},
    "running_water": {w:["i017"] for w in [2011,2013,2015,2018]},
    "residential_heating": {2011:["i020"],2013:["i020"],2015:["i020"],2018:["i020"],2020:["i019"]},
    "heating_energy": {2011:["i021"],2013:["i021"],2015:["i021"],2018:["i021_w4"],2020:["i020"]},
    "cooking_fuel_main": {2011:["i022"],2013:["i022"],2015:["i022"],2018:["i022_w4"],2020:["i021"]},
    "air_cleaner": {2015:["i027_w3"]},
    "waterworks_treatment": {2020:["i029"]},
    "indoor_cleanliness": {w:["i025"] for w in [2011,2013,2015,2018,2020]},
    "indoor_temperature": {w:["i026"] for w in [2011,2013,2015,2018,2020]},
    "floor_condition": {2020:["i027"]},
    "housing_construction_year": {2011:["i005","i005_1"],2013:["i005","i005_1"],2015:["i005","i005_1"],2018:["i005","i005_1"]},
    "residence_move_in_time": {2020:["i002","i003"]},
    "dwelling_area": {2011:["i001"],2013:["i001"],2018:["i000_w4_11","i000_w4_12"],2020:["i028"]},
    "bedroom_count": {w:["i012_1"] for w in [2011,2013,2015,2018]} | {2020:["i011_1"]},
    "livingroom_count": {w:["i012_2"] for w in [2011,2013,2015,2018]} | {2020:["i011_2"]},
    "building_structure": {2011:["i004"],2013:["i004"],2015:["i004"],2018:["i004"],2020:["i001"]},
    "building_stories": {2011:["i006","i007","i008"],2013:["i006","i007","i008"],2015:["i006","i007","i008"],2018:["i006","i007","i008"],2020:["i004","i005","i006","i006_1","i006_2"]},
    "elevator_access": {2011:["i009"],2013:["i009"],2015:["i009"],2018:["i009"],2020:["i007"]},
    "home_accessibility": {2011:["i010"],2013:["i010"],2015:["i010"],2018:["i010_w4"],2020:["i009"]},
    "entrance_steps": {2011:["i011"],2013:["i011"],2015:["i011"],2018:["i011"],2020:["i010"]},
    "electricity_access": {2011:["i016"],2013:["i016"],2018:["i016"],2020:["i015"]},
    "bathing_facility": {2011:["i018"],2013:["i018"],2015:["i018"],2018:["i018"],2020:["i017"]},
    "piped_gas_access": {2011:["i019"],2013:["i019"],2015:["i019"],2018:["i019"],2020:["i018"]},
    "air_cleaner_home": {2015:["i027_w3"],2020:["i024"]},
    "tap_water_access": {2020:["i016"]},
}

# Value labels explicitly transcribed from wave codebooks/questionnaires. Empty
# means the variable label is catalogued but its response-value labels still need review.
VALUE_LABELS = {
    # Wave-specific categories copied from the corresponding official CHARLS
    # codebooks. Keep unlike response structures distinct (e.g. 2011/13/15
    # toilet seat checkboxes vs. the single categorical item in 2018/20).
    "running_water": {2011:"1=Yes; 2=No",2013:"1=Yes; 2=No",2015:"1=Yes; 2=No",2018:"1=Yes; 2=No"},
    "residential_heating": {2011:"1=Yes; 2=No",2013:"1=Yes; 2=No",2015:"1=Yes; 2=No",2018:"1=Yes; 2=No",2020:"1=Yes; 2=No (centralized heating wording)"},
    "heating_energy": {
        2011:"1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2013:"1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2015:"1=Solar; 2=Coal; 3=Natural gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2018:"1=Solar; 2=Coal; 3=Natural Gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop Residue/Wood Burning; 7=Other; 8=Heating Provided",
        2020:"1=Solar; 2=Coal; 3=Natural Gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop Residue/Wood Burning; 7=Others; 8=Do not Heating",
    },
    "cooking_fuel_main": {
        2011:"1=Coal; 2=Natural gas; 3=Marsh gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2013:"1=Coal; 2=Natural gas; 3=Marsh gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2015:"1=Coal; 2=Natural gas; 3=Marsh gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop residue/Wood burning; 7=Other",
        2018:"1=Coal; 2=Natural Gas; 3=Marsh Gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop Residue/Wood Burning; 7=Other; 8=Do Not Cook",
        2020:"1=Coal; 2=Natural Gas; 3=Marsh Gas; 4=Liquefied Petroleum Gas; 5=Electric; 6=Crop Residue/Wood Burning; 7=Solar Energy; 8=Others; 9=Do not Cook",
    },
    "piped_gas_access": {2011:"1=Yes; 2=No",2013:"1=Yes; 2=No",2015:"1=Yes; 2=No",2018:"1=Yes; 2=No",2020:"1=Yes; 2=No"},
    "indoor_cleanliness": {
        2011: "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor",
        2013: "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        2015: "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        2018: "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
        2020: "1=Excellent; 2=Very clear; 3=Clear; 4=Fair; 5=Poor; 6=Not applicable",
    },
    "indoor_temperature": {
        2011: "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold",
        2013: "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        2015: "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        2018: "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
        2020: "1=Very hot; 2=Hot; 3=Bearable; 4=Cold; 5=Very cold; 6=Not applicable",
    },
    "floor_condition": {2020: "1=Flat covered; 2=Flat concrete; 3=Uneven"},
    "waterworks_treatment": {2020: "1=Yes; 2=No; 997=Do not know"},
    "tap_water_access": {2020: "1=Yes; 2=No"},
    "electricity_access": {2011:"1=Yes; 2=No",2013:"1=Yes; 2=No",2018:"1=Yes; 2=No",2020:"1=Yes; 2=No"},
    "bathing_facility": {
        2011:"1=Hot water provided; 2=Household water heater; 3=None",
        2013:"1=Hot water provided; 2=Household water heater; 3=None",
        2015:"1=Hot water provided; 2=Household water heater; 3=None",
        2018:"1=Hot water provided; 2=Household water heater; 3=None",
        2020:"1=Unified hot water supply; 2=Water heater; 3=None",
    },
    "air_cleaner_home": {2015:"1=Yes; 2=No",2020:"1=Yes; 2=No"},
}

# Field-level notes are used where a concept expands to unlike source fields;
# a concept-wide value label would wrongly attach toilet response codes to
# toilet counts or distances.
FIELD_VALUE_LABELS = {
    (2011, "i013"): "Continuous distance to nearest toilet; codebook max 1,000 (QA hint, not a validated range).",
    (2013, "i013"): "Continuous distance to nearest toilet; codebook max 1,000 (QA hint, not a validated range).",
    (2015, "i013"): "Continuous distance to nearest toilet; codebook max 2,000 (QA hint, not a validated range).",
    (2018, "i013"): "Continuous distance to nearest toilet; codebook summary includes extreme values; inspect units and raw data before analysis.",
    (2020, "i012"): "Continuous distance to nearest toilet; codebook max 2,000 (QA hint, not a validated range).",
    (2011, "i014s1"): "Separate multi-response toilet type field: 1=Toilet without a seat; no unselected storage code inferred.",
    (2011, "i014s2"): "Separate multi-response toilet type field: 2=Toilet with a seat; no unselected storage code inferred.",
    (2013, "i014s1"): "Separate multi-response toilet type field: 1=Toilet without a seat; no unselected storage code inferred.",
    (2013, "i014s2"): "Separate multi-response toilet type field: 2=Toilet with a seat; no unselected storage code inferred.",
    (2015, "i014s1"): "Separate multi-response toilet type field: 1=Toilet without a seat; no unselected storage code inferred.",
    (2015, "i014s2"): "Separate multi-response toilet type field: 2=Toilet with a seat; no unselected storage code inferred.",
    (2018, "i014"): "1=Without a seat; 2=With a seat.",
    (2020, "i013"): "1=Without a seat; 2=With a seat.",
    **{(wave, code): "1=Yes; 2=No (flushable)." for wave, code in [(2011,"i015"),(2013,"i015"),(2015,"i015"),(2018,"i015"),(2020,"i014")]},
    **{(wave, code): f"Continuous count of toilets in residence; codebook max {top} (QA hint, not a validated range)." for wave,code,top in [(2011,"i012_3",50),(2013,"i012_3",50),(2015,"i012_3",32)]},
    (2018, "i012_3"): "Continuous count of toilets in residence; codebook max 50 (QA hint, not a validated range).",
    (2020, "i011_3"): "Continuous count of toilets in residence; codebook max 46 (QA hint, not a validated range).",
}

def main():
    src = pd.read_csv(FIELDS, dtype=str).fillna("")
    rows=[]
    for cid, by_wave in MAP.items():
        label, domain, caveat = CONCEPTS[cid]
        for wave, codes in by_wave.items():
            for code in codes:
                hit=src[(src["wave"].astype(str)==str(wave)) & (src["variable"].str.lower()==code.lower())]
                if hit.empty:
                    raise ValueError(f"Missing code in catalog: {wave} {code}")
                for _,r in hit.drop_duplicates(["module","variable","variable_label"]).iterrows():
                    rows.append({"concept_id":cid,"concept_label":label,"domain":domain,"wave":wave,
                        "code":code,"module":r["module"],"source_label":r["variable_label"],
                        "code_value_labels":FIELD_VALUE_LABELS.get((wave,code), VALUE_LABELS.get(cid,{}).get(wave,"")),
                        "mapping_status":("2011 codebook/catalog candidate; correct baseline questionnaire is available; field-specific route and units remain under review" if str(wave)=="2011" else "catalog-label candidate; questionnaire review pending"),
                        "caveat":(caveat+" For 2011, the correct baseline household questionnaire is included; verify item-specific wording, recall period, and eligibility before harmonization." if str(wave)=="2011" else caveat)})
    out=pd.DataFrame(rows).drop_duplicates()
    out.to_csv(ROOT/"audit"/"food_environment_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
    concepts=[]
    for cid,(label,domain,caveat) in CONCEPTS.items():
        fields=out[out.concept_id.eq(cid)]
        concepts.append({"concept_id":cid,"label":label,"domain":domain,"caveat":caveat,
            "source_fields":[{"wave":str(r.wave),"code":r.code,"module":r.module,"source_label":r.source_label,"value_labels":r.code_value_labels,"note":r.mapping_status} for r in fields.itertuples()]})
    (ROOT/"site-prototype"/"dist"/"food_environment_v1.json").write_text(json.dumps(concepts,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"concepts={len(concepts)}; field mappings={len(out)}; by wave={out.groupby('wave').size().to_dict()}")

if __name__=="__main__": main()
