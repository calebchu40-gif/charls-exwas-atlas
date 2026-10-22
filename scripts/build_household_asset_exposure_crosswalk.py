"""Map official household durable-asset ownership and current-value items."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
ASSETS = {
    1: ("automobile", "汽车"), 2: ("electric_bicycle", "电动自行车"),
    3: ("motorcycle", "摩托车"), 4: ("refrigerator", "冰箱/冰柜"),
    5: ("washing_machine", "洗衣机"), 6: ("television", "电视机"),
    7: ("computer", "电脑"), 8: ("stereo_system", "组合音响"),
    9: ("video_camera", "摄像机"), 10: ("camera", "照相机"),
    11: ("air_conditioner", "空调"), 12: ("mobile_phone", "手机"),
    13: ("furniture", "值钱家具"), 14: ("music_instrument", "高档乐器"),
    15: ("valuable_decorations", "贵重装饰物"),
    16: ("precious_metals", "珠宝及贵重金属"),
    17: ("antiques_art", "古董、字画及艺术品"),
    18: ("air_purifier", "空气净化器"),
}
rows = []
for rec in raw.itertuples(index=False):
    wave, code = str(rec.wave), str(rec.variable).lower()
    if wave not in {"2011", "2013", "2015", "2018"} or "household_income" not in str(rec.module).lower():
        continue
    legacy_match = re.fullmatch(r"ha065s(\d+)", code)
    wave4_match = re.fullmatch(r"ha065_s(\d+)", code)
    legacy_value = re.fullmatch(r"ha065_1_(\d+)_", code)
    wave4_value = re.fullmatch(r"ha065_(\d+)", code) if wave == "2018" else None
    match = legacy_match or wave4_match
    value = legacy_value or wave4_value
    current_home_value = re.fullmatch(r"ha011_([12])", code) if wave in {"2013", "2015"} else None
    none_code = 19 if wave4_match else 18
    if current_home_value:
        component = int(current_home_value.group(1))
        concept = ("household_current_primary_residence_total_market_value" if component == 1
                   else "household_current_primary_residence_unit_market_value")
        label = ("家庭当前主要住房市场总价" if component == 1 else "家庭当前主要住房单位面积市场价格")
        construct = ("reported current total market value of primary residence" if component == 1
                     else "reported current unit-area market value of primary residence")
        unit = "10,000 Yuan" if component == 1 else "1,000 Yuan/m2"
        value_labels = ""
        caveat = ("Household-level estimate for the current home or a similar nearby housing unit; the questionnaire's HA011 selector routes total-price versus unit-price answers. "
                  "Conditional housing eligibility applies (2015 HA007=3 skips this item); preserve route and special missing values. Do not convert or combine the two alternative units without a prespecified rule, and do not interpret as respondent-specific ownership or wealth.")
    elif match and int(match.group(1)) == none_code:
        concept = "household_durable_asset_none_reported"
        label = "家户耐用品清单回答为以上皆无"
        construct = "explicit none-of-listed-assets response"
        value_labels = (f"0=No; {none_code}=Yes (official wave-specific response codes)"
                        if wave4_match else "18=None option selected (official category; unselected is not automatically No)")
        unit = "categorical response code" if wave4_match else "categorical selected-option code"
        caveat = "Explicit none option in the household durable-asset item. Do not infer from missing or unselected fields. This is household-level, not respondent ownership."
    elif match and int(match.group(1)) in ASSETS:
        item = int(match.group(1)); slug, zh = ASSETS[item]
        concept = f"household_owns_{slug}"
        label = f"家户是否拥有：{zh}"
        construct = "household asset ownership response"
        value_labels = (f"0=No; {item}=Yes (official 2018 response codes)"
                        if wave4_match else f"{item}={zh} (official selected-option label; unselected or absent is not automatically No)")
        unit = "categorical response code" if wave4_match else "categorical selected-option code"
        caveat = "Household respondent reports whether a household asset is owned. This does not establish ownership by the CHARLS respondent/spouse; preserve wave-specific response codes and missingness."
    elif value and int(value.group(1)) in ASSETS and (int(value.group(1)) <= 17 or wave == "2018"):
        item = int(value.group(1)); slug, zh = ASSETS[item]
        concept = f"household_current_value_{slug}"
        label = f"家户{zh}当前估值"
        construct = "reported current value of household durable asset"
        value_labels = ""
        unit = "Yuan"
        caveat = "Household-level current value in Yuan, asked for the listed item when applicable/owned. Preserve wave-specific eligibility, special missing values, and zero values; do not interpret as respondent-owned wealth or infer absent value as zero."
    else:
        continue
    rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": "income, wealth, and material resources", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "candidate; household asset item linked to official questionnaire/codebook; analysis eligibility pending",
        "construct": construct, "unit": unit, "value_labels": value_labels,
        "value_label_status": ("official questionnaire/codebook response labels reviewed; frequencies omitted; wave-specific"
                               if value_labels else "continuous value item; unit verified, categorical labels not applicable"),
        "value_label_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt; audit/CHARLS_2018_Codebook_extracted.txt",
        "caveat": caveat, "source_archive": rec.source,
    })

# Fixed capital assets are a separate questionnaire construct from the HA065
# household durable-goods list above. Keep the respondent/ownership scope
# explicit: it changes across waves, and 2018 asks only about the couple's
# owned share when property is jointly held with others.
LEGACY_FIXED_ASSETS = {
    1: ("tractor", "拖拉机"), 2: ("thresher", "脱粒机"),
    3: ("tractor_tools", "机引农具"), 4: ("water_pump", "抽水机/水泵"),
    5: ("processing_equipment", "加工机械"),
}
WAVE4_FIXED_ASSETS = {
    1: ("tractor", "拖拉机"), 2: ("thresher", "脱粒机"),
    3: ("harvester", "收割机"), 4: ("water_pump", "抽水机/水泵"),
    5: ("processing_equipment", "加工机械"), 6: ("seeder", "播种机"),
    7: ("agricultural_aircraft", "农用飞机"),
}
raw_index = {(str(x.wave), str(x.variable).lower()): x for x in raw.itertuples(index=False)}
fixed_rows = []
for (wave, code), rec in raw_index.items():
    if wave not in {"2011", "2013", "2015", "2018"} or "household_income" not in str(rec.module).lower():
        continue
    legacy_own = re.fullmatch(r"ha066s([1-6])", code)
    wave4_own = re.fullmatch(r"ha066_w4_s([1-8])", code) if wave == "2018" else None
    legacy_value = re.fullmatch(r"ha066_1_(\d+)_", code) if wave != "2018" else None
    wave4_value = re.fullmatch(r"ha066_w4_(\d+)", code) if wave == "2018" else None
    if legacy_own or wave4_own:
        item = int((legacy_own or wave4_own).group(1))
        none_code = 8 if wave == "2018" else 6
        if item == none_code:
            concept = "household_fixed_agricultural_assets_none_reported" if wave in {"2011", "2013"} else ("respondent_spouse_fixed_agricultural_assets_none_reported" if wave == "2015" else "respondent_spouse_owned_share_fixed_agricultural_assets_none_reported")
            label = "农用固定资产清单回答为以上皆无"
            construct = "explicit none-of-listed-fixed-capital-assets response"
            value_labels = (f"0=No; {none_code}=Yes" if wave == "2018" else "6=None option selected; unselected is not automatically No")
            scope = "household" if wave in {"2011", "2013"} else "main respondent and spouse" if wave == "2015" else "main respondent and spouse's owned share"
            label = f"{scope}农用固定资产清单回答为以上皆无"
        else:
            slug, zh = (WAVE4_FIXED_ASSETS if wave == "2018" else LEGACY_FIXED_ASSETS)[item]
            scope_tag = "household" if wave in {"2011", "2013"} else "respondent_spouse" if wave == "2015" else "respondent_spouse_owned_share"
            concept = f"{scope_tag}_owns_fixed_agricultural_asset_{slug}"
            label = f"{scope}是否拥有农用固定资产：{zh}"
            construct = "fixed-capital agricultural asset ownership response"
            value_labels = (f"0=No; {item}=Yes" if wave == "2018" else f"{item}={zh} selected; unselected or absent is not automatically No")
        unit = "categorical response code" if wave == "2018" else "categorical selected-option code"
        caveat = (f"Ownership scope: {scope}. Preserve wave-specific response codes and missingness. A blank/unselected multi-select field is not automatically No; the 2018 instrument records only the main respondent/spouse owned share for jointly held assets.")
    elif legacy_value or wave4_value:
        item = int((legacy_value or wave4_value).group(1))
        asset_items = WAVE4_FIXED_ASSETS if wave == "2018" else LEGACY_FIXED_ASSETS
        if item not in asset_items:
            continue
        slug, zh = asset_items[item]
        if wave == "2018":
            scope_tag, scope = "respondent_spouse_owned_share", "主要受访者及配偶所拥有的产权份额"
        elif wave == "2015":
            scope_tag, scope = "respondent_spouse", "受访者和配偶"
        else:
            scope_tag, scope = "household", "家户"
        concept = f"{scope_tag}_current_value_fixed_agricultural_asset_{slug}"
        label = f"{scope}农用固定资产当前估值：{zh}"
        construct = "reported current value of fixed-capital agricultural asset"
        unit = "10,000 Yuan" if wave == "2018" and item == 7 else "Yuan"
        value_labels = ""
        caveat = (f"Reported current value for {scope}; the 2018 questionnaire explicitly limits values to the main respondent/spouse owned share where an asset is shared. Preserve item-specific eligibility, special missingness and zero values; do not infer non-ownership from absent value or sum categories as total wealth.")
    elif code == "ha067" or code == "ha067_w4":
        scope_tag, scope = (("respondent_spouse_nonagricultural", "主要受访者及配偶") if wave == "2018" else
                            ("household", "家户"))
        concept = f"{scope_tag}_other_fixed_capital_current_value"
        label = f"{scope}其他生产/经营固定资本当前估值"
        construct = "reported current value of other fixed-capital assets used in household production or self-employment"
        unit = "Yuan"
        value_labels = ""
        caveat = ("The questionnaire says not to double-count fixed assets listed in HA066. In 2018 the item is explicitly non-agricultural and includes business property such as shops, factories and warehouses, and refers to the main respondent/spouse. Preserve scope and missingness; do not sum with other asset measures as net wealth.")
    elif code in {"ha068", "ha068_1"}:
        if wave in {"2011", "2013"}:
            scope_tag, scope = "household", "家户"
        else:
            scope_tag, scope = "respondent_spouse", "受访者及配偶"
        is_status = code == "ha068"
        concept = f"{scope_tag}_other_durable_or_fixed_assets_500_yuan_plus" + ("_status" if is_status else "_current_value")
        label = f"{scope}其他500元及以上耐用品或固定资产" + ("是否拥有" if is_status else "当前估值")
        construct = "reported other durable/fixed asset eligibility status" if is_status else "reported current value of other durable/fixed assets"
        unit = "categorical response code" if is_status else "Yuan"
        value_labels = ("1=Yes; 2=No; 997=Don't know; 999=Refused" if wave == "2018" else "1=Yes; 2=No") if is_status else ""
        caveat = (f"The item concerns other assets worth at least 500 Yuan and is conditional on the relevant positive route for the value field. Target scope: {scope}. Do not infer zero value from No, missing, Don't know, or refusal; preserve official special codes and wave-specific eligibility.")
    else:
        continue
    source_doc = {
        "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
        "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
        "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
        "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
    }[wave]
    fixed_rows.append({
        "wave": wave, "code": code, "concept_id": concept, "concept_label": label,
        "domain": "income, wealth, and material resources", "module": rec.module,
        "source_label": rec.variable_label,
        "mapping_status": "candidate; fixed-capital asset identity, scope, and questionnaire wording reviewed; analysis eligibility pending",
        "construct": construct, "unit": unit, "value_labels": value_labels,
        "value_label_status": ("official questionnaire/codebook response labels reviewed; frequencies omitted; wave-specific" if value_labels else "continuous value item; unit verified in official questionnaire; categorical labels not applicable"),
        "value_label_source": source_doc, "caveat": caveat, "source_archive": rec.source,
    })
rows.extend(fixed_rows)
out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "household_asset_exposure_mapping_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["construct", "concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))), source_fields=("code", "size"), source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "household_asset_exposure_concept_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"household durable asset mappings={len(out)}; concepts={out.concept_id.nunique()}; ownership/value/none rows={out.construct.str.contains('ownership|none').sum()}/{out.construct.str.contains('value').sum()}/{out.construct.str.contains('none').sum()}")
