"""Build candidate housing, dwelling-quality, and property-asset mappings."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
food = pd.read_csv(AUDIT / "food_environment_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
cooking = pd.read_csv(AUDIT / "cooking_fuel_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
known = {(str(r.wave), str(r.code).lower()) for r in food.itertuples(index=False)}
known |= {(str(r.wave), str(r.raw_variable).lower()) for r in cooking.itertuples(index=False)}

DWELLING = {
    "i001": ("dwelling_construction_area", "住宅建筑面积"),
    "i002": ("dwelling_housing_land_area", "住宅占地面积"),
    "i003": ("dwelling_business_use", "住宅是否兼作经营场所"),
    "i004": ("dwelling_structure_type", "住宅建筑结构类型"),
    "i005": ("dwelling_construction_year", "住宅建成年份"),
    "i005_1": ("dwelling_construction_period_category", "住宅建成年代区间"),
    "i006": ("dwelling_story_count_category", "住宅楼层数类别"),
    "i007": ("dwelling_independent_or_compound", "住宅独立/合院类型"),
    "i008": ("dwelling_floor_location", "住宅所在楼层"),
    "i009": ("dwelling_elevator_access", "住宅是否有电梯"),
    "i010": ("dwelling_accessibility_facility", "住宅无障碍设施"),
    "i010_w4": ("dwelling_accessibility_facility", "住宅无障碍设施"),
    "i011": ("dwelling_entrance_steps", "住宅入口台阶数"),
    "i012_1": ("dwelling_bedroom_count", "住宅卧室数量"),
    "i012_2": ("dwelling_livingroom_count", "住宅客厅数量"),
    "i012_3": ("dwelling_toilet_count", "住宅卫生间数量"),
    "i012_4": ("dwelling_kitchen_count", "住宅厨房数量"),
    "i012_5": ("dwelling_balcony_count", "住宅阳台数量"),
    "i013": ("dwelling_nearest_toilet_distance", "住宅至最近卫生间距离"),
    "i014": ("dwelling_toilet_type", "住宅卫生间类型"),
    "i014s1": ("dwelling_toilet_type", "住宅卫生间类型"),
    "i014s2": ("dwelling_toilet_type", "住宅卫生间类型"),
    "i015": ("dwelling_flushable_toilet", "住宅卫生间是否可冲水"),
    "i016": ("dwelling_electricity_access", "住宅是否有电"),
    "i017": ("dwelling_running_water_access", "住宅是否有自来水"),
    "i018": ("dwelling_shower_bath_access", "住宅是否有室内淋浴/浴室"),
    "i019": ("dwelling_gas_supply", "住宅是否有煤气/天然气"),
    "i020": ("dwelling_heating_access", "住宅是否有供暖"),
    "i021": ("dwelling_heating_energy_source", "住宅供暖能源来源"),
    "i021_w4": ("dwelling_heating_energy_source", "住宅供暖能源来源"),
    "i022": ("cooking_fuel_main", "家庭主要烹饪燃料"),
    "i022_w4": ("cooking_fuel_main", "家庭主要烹饪燃料"),
    "i023": ("dwelling_telephone_access", "住宅是否有电话"),
    "i024": ("dwelling_broadband_access", "住宅是否有宽带网络"),
    "i025": ("dwelling_cleanliness_perception", "家庭环境整洁度自评"),
    "i026": ("dwelling_indoor_temperature_perception", "家庭室内温度自评"),
    "i027_w3": ("dwelling_air_cleaner_access", "住宅是否有空气净化器"),
}
ZH = {
    "cooking_fuel_main": "家庭主要烹饪燃料",
    "dwelling_urban_rural_context": "现居住地城乡属性",
    "dwelling_house_type": "当前住宅类型",
    "current_home_owner_relation": "当前住宅所有者关系类别",
    "current_home_owner_share": "当前住宅所有权比例（关系类别）",
    "current_home_usable_area": "当前住宅可用面积",
    "current_home_total_area": "当前住宅面积",
    "current_home_rent_paid": "当前住宅租金支出",
    "current_home_market_rent": "当前住宅市场租金估值",
    "current_home_total_value": "当前住宅总价值估值",
    "current_home_unit_value": "当前住宅单位价值估值",
    "current_home_year_acquired": "取得当前住宅年份",
    "current_home_purchase_amount": "取得当前住宅支付金额",
    "household_property_count": "家庭名下住房数量",
    "household_property_owner_relation_slots": "家庭住房所有者关系/住房槽位记录",
    "household_property_owner_share_slots": "家庭住房所有权比例/成员槽位记录",
    "household_property_value_measure_type": "家庭住房价值总额/单位值类型",
    "household_property_total_value_by_slot": "家庭各住房总价值估值（住房槽位）",
    "household_property_unit_value_by_slot": "家庭各住房单位价值估值（住房槽位）",
    "household_property_rented_out_by_slot": "家庭各住房是否出租（住房槽位）",
    "household_property_rent_by_slot": "家庭各住房租金（住房槽位）",
    "household_property_market_rent_by_slot": "家庭各住房市场租金估值（住房槽位）",
    "current_home_market_total_value_2013_2015": "\u5f53\u524d\u5c45\u4f4f\u623f\u5c4b\u5e02\u573a\u4ef7\u503c\uff1a\u603b\u4ef7\uff08\u4fdd\u7559\u69fd\u4f4d\uff09",
    "current_home_market_unit_value_2013_2015": "\u5f53\u524d\u5c45\u4f4f\u623f\u5c4b\u5e02\u573a\u4ef7\u503c\uff1a\u5355\u4f4d\u9762\u79ef\u4ef7\uff08\u4fdd\u7559\u69fd\u4f4d\uff09",
    "house_acquisition_building_outlay_2011": "\u5bb6\u5ead\u8d2d\u4e70\u3001\u5efa\u9020\u6216\u6362\u53d6\u4f4f\u623f\u652f\u51fa\uff082011\uff09",
    "house_own_money_spent_acquisition_2013_2015": "\u4f4f\u6237\u81ea\u6709\u8d44\u91d1\u8d2d\u5efa\u4f4f\u623f\u652f\u51fa\uff082013/2015\uff09",
    "new_house_own_money_purchase_outlay_2011": "\\u65b0\\u4f4f\\u623f\\u81ea\\u6709\\u8d44\\u91d1\\u652f\\u51fa\\uff082011\\uff09",
    "demolition_compensation_old_house_market_value_2011": "\\u62c6\\u8fc1\\u8865\\u507f\\u60c5\\u5f62\\u4e2d\\u65e7\\u623f\\u5e02\\u573a\\u4ef7\\uff082011\\uff09",
    "demolition_compensation_new_house_total_value_2011": "\\u62c6\\u8fc1\\u8865\\u507f\\u65b0\\u623f\\u5e02\\u573a\\u603b\\u4ef7\\uff082011\\uff09",
    "demolition_compensation_new_house_unit_value_2011": "\\u62c6\\u8fc1\\u8865\\u507f\\u65b0\\u623f\\u5e02\\u573a\\u5355\\u4f4d\\u9762\\u79ef\\u4ef7\\uff082011\\uff09",
    "demolition_compensation_old_house_market_value_household_2011": "\\u5bb6\\u6237\\u623f\\u4ea7\\u62c6\\u8fc1\\u65f6\\u65e7\\u623f\\u5e02\\u573a\\u4ef7\\uff082011\\uff09",
    "housing_property_renovation_event_outlay_2011": "\\u5bb6\\u6237\\u623f\\u4ea7\\u88c5\\u4fee\\u4e8b\\u4ef6\\u652f\\u51fa\\uff082011\\uff09",
    "new_house_own_money_purchase_outlay_2013": "\u65b0\u8d2d\u4f4f\u623f\u81ea\u6709\u8d44\u91d1\u652f\u51fa\uff082013\uff09",
    "demolition_compensation_old_house_market_value_2013": "\u62c6\u8fc1\u8865\u507f\u60c5\u5f62\u4e2d\u65e7\u623f\u5e02\u573a\u4ef7\uff082013\uff09",
    "demolition_compensation_new_house_total_value_2013": "\u62c6\u8fc1\u8865\u507f\u65b0\u623f\u5e02\u573a\u603b\u4ef7\uff082013\uff09",
    "demolition_compensation_new_house_unit_value_2013": "\u62c6\u8fc1\u8865\u507f\u65b0\u623f\u5e02\u573a\u5355\u4f4d\u9762\u79ef\u4ef7\uff082013\uff09",
}

CURRENT_HOME_MEASURE_UNITS = {
    "current_home_rent_paid": "Yuan/month",
    "current_home_market_rent": "Yuan/month",
    "current_home_total_value": "10,000 Yuan",
    "current_home_unit_value": "1,000 Yuan/square metre",
    "current_home_year_acquired": "calendar year",
    "current_home_purchase_amount": "10,000 Yuan",
}

def classify(rec):
    wave, code, label, module = str(rec.wave), str(rec.variable).lower(), str(rec.variable_label), str(rec.module).lower()
    # 2018 preload values refer to the last interview and are not same-wave outcomes.
    # Bracket endpoints are metadata used for interval responses, not observed values.
    if code.startswith("z") or re.search(r"(?:__|_)(?:min|max)$", code) or re.search(r"\b(?:min|max) bracket\b", label, re.I):
        return None
    if wave in {"2011", "2013", "2015", "2018"}:
        if wave == "2011" and re.fullmatch(r"ha047_[12]_", code):
            cid = "demolition_compensation_old_house_market_value_household_2011"
            return cid, ZH[cid], "old house market value at demolition-compensation event, household property slot", "Household housing-history loop in the 2011 household questionnaire; HA047 follows the acquisition route and HA046 event timing. Keep property slots separate and distinguish this household instrument from the 2011 baseline respondent housing-history HA022 field. Questionnaire reporting unit is 10,000 Yuan; stored scale and the sparse Codebook summary format for slot 2 require release-dictionary verification. Preserve route and special values."
        if wave == "2011" and re.fullmatch(r"ha049_[1-3]_", code):
            cid = "housing_property_renovation_event_outlay_2011"
            return cid, ZH[cid], "housing-property decorating/renovating event outlay by household property slot", "2011 household questionnaire asks expenditure for this property and HA050 records the year of the greatest renovation if more than once; this is not past-year HA025 expenditure. Preserve property slot and event year; do not sum slots or merge with annual renovation spending. Questionnaire unit is Yuan; stored scale and special codes require release-dictionary verification."
        if wave == "2011" and code == "ha018":
            cid = "new_house_own_money_purchase_outlay_2011"
            return cid, ZH[cid], "conditional own-money outlay on acquired residence", "2011 baseline retrospective housing-history item, not annual spending. HA018 asks own money spent on this housing; retain HA016 acquisition route and HA017 acquisition year. Some acquisition routes skip the amount. Questionnaire reporting unit is 10,000 Yuan; 2011 Codebook summary values show a scale that needs official release-dictionary verification before numerical use. Preserve special values and bracket/missing semantics."
        if wave == "2011" and code == "ha022":
            cid = "demolition_compensation_old_house_market_value_2011"
            return cid, ZH[cid], "old house value under demolition-compensation route", "Asked only when HA016=8 (house received as compensation for demolition); market value of old house at that event, not current residence value. Questionnaire reporting unit is 10,000 Yuan; 2011 Codebook summary values require stored-value scale verification. Preserve route, event reference and special values."
        if wave == "2011" and code == "ha023_1":
            cid = "demolition_compensation_new_house_total_value_2011"
            return cid, ZH[cid], "new house value under demolition-compensation route", "Conditional 2011 market value of the new house at the demolition-compensation event; total price in questionnaire reporting units of 10,000 Yuan. Keep distinct from old-house value and unit-area price. Stored-value scale requires official release-dictionary verification."
        if wave == "2011" and code == "ha023_2":
            cid = "demolition_compensation_new_house_unit_value_2011"
            return cid, ZH[cid], "new house value under demolition-compensation route", "Conditional 2011 market value of the new house at the demolition-compensation event; unit price in questionnaire reporting units of 1,000 Yuan per square meter. Keep distinct from old-house value and total price. Stored-value scale requires official release-dictionary verification."
        if wave == "2013" and code == "ha018":
            cid = "new_house_own_money_purchase_outlay_2013"
            return cid, ZH[cid], "conditional own-money outlay on newly acquired residence", "2013 retrospective housing-history item, not annual spending. HA018 asks own money spent on the housing; retain HA016 acquisition route and HA017 purchase/build year. Some acquisition paths skip the amount. Questionnaire reporting unit is 10,000 Yuan; stored-value scale requires official release-dictionary verification. Preserve special values and bracket/missing semantics."
        if wave == "2013" and code == "ha022":
            cid = "demolition_compensation_old_house_market_value_2013"
            return cid, ZH[cid], "old house value under demolition-compensation route", "Asked only when HA016=8 (house received as demolition compensation); this is the market value of the old house at that event, not current residence value. Questionnaire reporting unit is 10,000 Yuan; preserve the route, event reference and special values. Stored-value scale requires official release-dictionary verification."
        if wave == "2013" and code == "ha023_1":
            cid = "demolition_compensation_new_house_total_value_2013"
            return cid, ZH[cid], "new house value under demolition-compensation route", "Conditional 2013 value of the new house received after demolition compensation; total price in questionnaire reporting units of 10,000 Yuan. Keep distinct from old-house value and unit-area price; preserve HA016=8 route and event reference. Stored-value scale requires official release-dictionary verification."
        if wave == "2013" and code == "ha023_2":
            cid = "demolition_compensation_new_house_unit_value_2013"
            return cid, ZH[cid], "new house value under demolition-compensation route", "Conditional 2013 value of the new house received after demolition compensation; unit price in questionnaire reporting units of 1,000 Yuan per square meter. Keep distinct from old-house value and total price; preserve HA016=8 route and event reference. Stored-value scale requires official release-dictionary verification."
        if wave == "2011" and re.fullmatch(r"ha043_[1-3]_", code):
            cid = "house_acquisition_building_outlay_2011"
            return cid, ZH[cid], "household house acquisition/building outlay", "2011 questionnaire asks how much the household spent to buy/build/exchange this house; retain the numbered source slot and household-level respondent scope. Questionnaire reporting unit is 10,000 Yuan. Do not combine with later own-money wording or sum slots into net worth. Preserve the bracket route and special values; underlying stored-value scale needs official release-dictionary verification."
        if wave in {"2013", "2015"} and re.fullmatch(r"ha043_[1-4]_", code):
            cid = "house_own_money_spent_acquisition_2013_2015"
            return cid, ZH[cid], "household house acquisition/building outlay", "2013/2015 questionnaire asks how much of the respondent's own money was spent on the house, including loan-financed spending; retain the numbered source slot and household-level respondent scope. Questionnaire reporting unit is 10,000 Yuan. Keep separate from the differently worded 2011 item and do not sum slots. Preserve bracket routing and special values; underlying stored-value scale needs official release-dictionary verification."
        if wave in {"2013", "2015"} and re.fullmatch(r"ha034_1_[1-4]_", code):
            cid = "current_home_market_total_value_2013_2015"
            return cid, ZH[cid], "current respondent/spouse residence total market value", "Reported total price in 10,000 Yuan. The questionnaire asks about the respondent/spouse residence when an eligible household member lives there; retain the numbered source slot and household-level respondent scope. Do not combine with unit-area prices or sum slots into household net worth. Preserve unfolding-bracket routing and special values."
        if wave in {"2013", "2015"} and re.fullmatch(r"ha034_2_[1-4]_", code):
            cid = "current_home_market_unit_value_2013_2015"
            return cid, ZH[cid], "current respondent/spouse residence unit market value", "Reported unit price in 1,000 Yuan per square meter. The questionnaire asks about the respondent/spouse residence when an eligible household member lives there; retain the numbered source slot and household-level respondent scope. Do not combine with total prices or sum slots. Preserve unfolding-bracket routing and special values."
        if code in DWELLING and module in {"housing_characteristics", "housing"}:
            cid, zh = DWELLING[code]
            return cid, zh, "dwelling condition/amenity", "Single-residence or household dwelling field. Verify wave-specific response labels, eligibility, missing codes and whether fields describe the same dwelling before pooling."
        if wave == "2018" and code == "i000_w4_2":
            cid = "dwelling_urban_rural_context"
        elif wave == "2018" and code == "i000_w4_3":
            cid = "dwelling_house_type"
        elif wave == "2018" and re.match(r"i000_w4_4_s(?!999$)\d+", code):
            cid = "current_home_owner_relation"
        elif wave == "2018" and code.startswith("i000_w4_4_") and re.search(r"percent", label, re.I):
            cid = "current_home_owner_share"
        elif wave == "2018" and code == "i000_w4_11": cid = "current_home_usable_area"
        elif wave == "2018" and code == "i000_w4_12": cid = "current_home_total_area"
        elif wave == "2018" and code == "i000_w4_13": cid = "current_home_rent_paid"
        elif wave == "2018" and code == "i000_w4_14": cid = "current_home_market_rent"
        elif wave == "2018" and code == "i000_w4_15_1": cid = "current_home_total_value"
        elif wave == "2018" and code == "i000_w4_15_2": cid = "current_home_unit_value"
        elif wave == "2018" and code == "i000_w4_16": cid = "current_home_year_acquired"
        elif wave == "2018" and code == "i000_w4_17": cid = "current_home_purchase_amount"
        elif wave == "2018" and code == "ha000_w4_0": cid = "household_property_count"
        elif wave == "2018" and code.startswith(("ha000_w4_", "ha001_w4_", "ha034_w4_")) and re.search(r"percent .*own|share of .*house prop", label, re.I):
            cid = "household_property_owner_share_slots"
        elif wave == "2018" and code.startswith("ha000_w4_") and re.search(r"own(?:s)? house", label, re.I) and not re.search(r"none of the above|refused|percent", label, re.I):
            cid = "household_property_owner_relation_slots"
        elif wave == "2018" and re.match(r"ha004_w4_\d+_1_", code): cid = "household_property_total_value_by_slot"
        elif wave == "2018" and re.match(r"ha004_w4_\d+_2_", code): cid = "household_property_unit_value_by_slot"
        elif wave == "2018" and re.match(r"ha004_w4_\d+_?$", code): cid = "household_property_value_measure_type"
        elif wave == "2018" and re.fullmatch(r"ha005_w4_\d+_", code): cid = "household_property_rented_out_by_slot"
        elif wave == "2018" and re.fullmatch(r"ha006_w4_\d+_", code): cid = "household_property_rent_by_slot"
        elif wave == "2018" and re.fullmatch(r"ha007_w4_\d+_", code): cid = "household_property_market_rent_by_slot"
        else:
            return None
        return cid, ZH[cid], "housing/property candidate", "2018 housing roster fields may repeat by property and household-member relationship. Slots are components, not independent exposures; do not sum values or equate respondent ownership with household ownership without a prespecified derivation. Confirm units, route and special codes."
    return None

rows = []
for rec in raw.itertuples(index=False):
    wave, code = str(rec.wave), str(rec.variable)
    if wave not in {"2011", "2013", "2015", "2018"}:
        continue
    result = classify(rec)
    if not result or (wave, code.lower()) in known:
        continue
    concept, label, construct, caveat = result
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": "housing and built environment", "module": rec.module,
        "source_label": rec.variable_label,
        "unit": "% of the specific house's property rights" if concept in {"household_property_owner_share_slots", "current_home_owner_share"} else (CURRENT_HOME_MEASURE_UNITS.get(concept, "Yuan (questionnaire reporting unit)" if concept == "housing_property_renovation_event_outlay_2011" else ("10,000 Yuan (questionnaire reporting unit)" if concept in {"house_acquisition_building_outlay_2011", "house_own_money_spent_acquisition_2013_2015", "new_house_own_money_purchase_outlay_2011", "demolition_compensation_old_house_market_value_2011", "demolition_compensation_new_house_total_value_2011", "new_house_own_money_purchase_outlay_2013", "demolition_compensation_old_house_market_value_2013", "demolition_compensation_new_house_total_value_2013", "current_home_market_total_value_2013_2015"} else ("1,000 Yuan/m2 (questionnaire reporting unit)" if concept in {"demolition_compensation_new_house_unit_value_2011", "demolition_compensation_new_house_unit_value_2013", "current_home_market_unit_value_2013_2015"} else "")))),
        "mapping_status": "official 2018 questionnaire defines a continuous percentage share; route and house/member-slot interpretation reviewed" if concept in {"household_property_owner_share_slots", "current_home_owner_share"} else ("official 2018 questionnaire confirms numeric response unit; special values, route and release coding still require review" if concept in CURRENT_HOME_MEASURE_UNITS else "candidate mapped from official wave-variable metadata; response labels, routing and comparability review required"),
        "construct": construct, "caveat": ("Official 2018 HA&I questionnaire asks what percentage of a specific house's property rights belongs to each listed family-member slot. This is a continuous percent response, not a categorical value label. Fields repeat by house/person and follow roster-dependent routes; preserve slot identity and denominators, do not sum across incompatible or missing slots, and do not infer respondent-level ownership without a prespecified derivation. The questionnaire instructs interviewers to enter 100% for the 'Other' case when the house is unrelated to the respondent/spouse or listed relatives/friends. Confirm special codes and route eligibility in the authorized release before analysis." if concept in {"household_property_owner_share_slots", "current_home_owner_share"} else ("Official 2018 questionnaire unit is " + CURRENT_HOME_MEASURE_UNITS[concept] + ". Retain the exact current-home measure and ownership/eligibility route. Do not combine the total-price and unit-price forms or derive one from the other without a validated area and response-format selector. Codebook summary extrema are not valid-range evidence; preserve special/missing values and confirm route, denominator and release coding in authorized data before analysis." if concept in CURRENT_HOME_MEASURE_UNITS else caveat)),
        "source_archive": f"{rec.source}; official wave questionnaire/codebook",
    })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "housing_exposure_variable_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["construct", "concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"), source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "housing_exposure_concept_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"housing mappings={len(out)}; concepts={out.concept_id.nunique()}; constructs={out.construct.nunique()}")
