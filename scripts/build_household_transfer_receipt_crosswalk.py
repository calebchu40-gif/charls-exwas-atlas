"""Map household transfer-source selection fields, distinct from their amounts."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
specs = {
    "gd003s1": ("household_societal_donation_source_selected_2011_2015", "家户过去一年是否勾选社会捐助来源", "1=Donations from the society"),
    "gd003s2": ("household_land_seizure_compensation_source_selected_2011_2015", "家户过去一年是否勾选征地补偿来源", "2=Compensation for land seizure"),
    "gd003s3": ("household_house_demolition_compensation_source_selected_2011_2015", "家户过去一年是否勾选住房拆迁补偿来源", "3=Compensation to pulling down house/apartment"),
}
rows=[]
for wave in ["2011", "2013", "2015"]:
    for code,(concept,label,value_labels) in specs.items():
        hit=raw[(raw.wave==wave)&raw.variable.str.lower().eq(code)]
        if len(hit)!=1: raise ValueError(f"Expected one {wave} {code}, got {len(hit)}")
        src=hit.iloc[0]
        questionnaire={"2011":"CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt"}[wave]
        rows.append({"wave":wave,"code":code,"concept_id":concept,"concept_label":label,
            "domain":"household transfers and compensation","module":src.module,"source_label":src.variable_label,
            "mapping_status":"official questionnaire and Codebook identify the option and selected category code; missing/nonselection storage remains unverified",
            "construct":"household past-year income-source selection; a categorical checklist marker, not an amount",
            "unit":"selected source option code; do not derive No from blank without release-file verification",
            "value_labels":value_labels,"value_label_status":"official questionnaire/Codebook option label reviewed; frequencies omitted",
            "value_label_source":f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            "source_document":f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
            "caveat":"GD003 is a household past-year check-all-that-apply item, followed by separate amount fields gd003_1/_2/_3. This source marker is not the amount. Preserve the official selection code and missingness; do not convert blanks to No until authorized release storage is verified. gd003s4 is the shared None option and is not a source-specific exposure. Household-level measure; do not assign to an individual.",
            "source_archive":src.source})
out=pd.DataFrame(rows)
out.to_csv(AUDIT/"household_transfer_receipt_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
print(f"household transfer source-selection mappings={len(out)}; concepts={out.concept_id.nunique()}")

none_rows=[]
for wave in ["2011", "2013", "2015"]:
    code="gd003s4"
    hit=raw[(raw.wave==wave)&raw.variable.str.lower().eq(code)]
    if len(hit)!=1: raise ValueError(f"Expected one {wave} {code}, got {len(hit)}")
    src=hit.iloc[0]
    questionnaire={"2011":"CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt","2013":"CHARLS_2013_Questionnaire_extracted.txt","2015":"CHARLS_2015_Questionnaire_extracted.txt"}[wave]
    none_rows.append({"wave":wave,"code":code,"concept_id":"household_transfer_compensation_none_option_metadata_2011_2015",
        "concept_label":"家户捐助/补偿清单的None选项元数据","domain":"measurement metadata",
        "subcategory":"checklist none-option coding","module":src.module,"source_label":src.variable_label,
        "mapping_status":"official questionnaire and Codebook identify the shared None option; metadata only",
        "unit":"check-all-that-apply checklist option code","value_labels":"4=None",
        "value_label_status":"official questionnaire/Codebook option label reviewed; frequencies omitted",
        "value_label_source":f"sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "source_document":f"sources_official/{questionnaire}; sources_official/CHARLS_{wave}_Codebook_extracted.txt",
        "caveat":"This shared None option is not a source-specific exposure and is not an independent response for each transfer category. Preserve as checklist metadata; do not substitute it for all source-specific fields or infer source-level No from blank values.",
        "source_archive":src.source})
pd.DataFrame(none_rows).to_csv(AUDIT/"household_transfer_none_option_crosswalk_v1.csv",index=False,encoding="utf-8-sig")
