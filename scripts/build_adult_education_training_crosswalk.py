"""Map adult education and vocational-training source fields as E candidates.

This is a metadata-only, evidence-preserving crosswalk. It does not read
respondent records or infer unselected multi-response options.
"""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

DOMAIN = "education and social position"
OPTIONS = {
    1: "None",
    2: "TV University",
    3: "Night School",
    4: "Zikao (self-taught examination)",
    5: "Correspondence / distance learning",
    6: "Literacy course",
    7: "Accelerated education course",
    8: "Other",
}
DOC = {
    "2011": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
    "2018": "sources_official/CHARLS_2018_Questionnaire_extracted.txt; sources_official/CHARLS_2018_Codebook_extracted.txt",
}

SPECS = {
    "adult_education_program_participation": {
        "label": "成人教育参与形式（按问卷多选与访谈路径）",
        "codes": {
            "2011": [f"bd007s{i}" for i in range(1, 9)],
            "2013": [f"bd007s{i}" for i in range(1, 9)] + [f"bd007_w2_1s{i}" for i in range(1, 9)],
            "2015": [f"bd007_w2_1s{i}" for i in range(1, 9)],
            "2018": [f"bd007_w4_1_s{i}" for i in range(1, 9)] + [f"bd007_w2_1_s{i}" for i in range(1, 9)],
        },
        "unit": "multi-response option",
        "period": "ever or since the prior interview, depending on wave and interview route",
        "response": "option-specific source field; see the per-wave value-label note",
        "caveat": "Adult-education formats are a multi-response question. Wave 1 and selected returner/new-interview routes ask ever/current participation, while update routes ask since the prior interview. Option slots are components of one construct, not separate exposure concepts. Unselected/blank slots are not inferred as No. In 2018, retain XRType/ZFRedu routing and the distinct BD007_W4_1 versus BD007_W2_1 forms.",
    },
    "adult_education_duration_years": {
        "label": "成人教育学习年限（年）",
        "codes": {"2011": ["bd008"], "2013": ["bd008", "bd008_w2_1"], "2015": ["bd008_w2_1"], "2018": ["bd008_w2_1", "bd008_w4_1"]},
        "unit": "years",
        "period": "lifetime or since prior interview, depending on source question and route",
        "response": "continuous duration; retain original field and route",
        "caveat": "The unit is years. Baseline/ever items and since-last-interview update items have different time windows. In 2018 the W2_1 and W4_1 source forms follow different interview/education-update routes; do not combine their raw values without an explicit harmonization rule.",
    },
    "adult_education_degree_received": {
        "label": "成人教育是否获得文凭/学位",
        "codes": {"2011": ["bd009"], "2013": ["bd009", "bd009_w2_1"], "2015": ["bd009_w2_1"], "2018": ["bd009_w2_1", "bd009_w4_1"]},
        "unit": "binary response (official codes retained per wave)",
        "period": "ever or since prior interview, depending on source question and route",
        "response": "1=Yes; 2=No where specified by the official codebook",
        "caveat": "The indicator is conditional on adult-education participation and follows different ever/since-last-interview routes. Preserve structural skips; do not convert skipped questions to No. Reconcile the 2018 XRType/ZFRedu branch before deriving one current status.",
    },
    "adult_education_highest_credential": {
        "label": "成人教育最高学历/文凭类别",
        "codes": {"2011": ["bd011"], "2013": ["bd011"], "2015": ["bd011"], "2018": ["bd011", "bd011_w4"]},
        "unit": "ordinal/categorical credential; original categories retained",
        "period": "highest attained credential or route-specific update credential",
        "response": "Official categories include vocational school, two/three-year college, four-year college, and other; verify each wave's code labels before harmonizing.",
        "caveat": "Do not conflate adult-education credentials with the separate highest general schooling item. The 2018 BD011 and BD011_W4 forms have different interview routes/time scopes; no cross-wave recode is asserted.",
    },
    "vocational_training_participation": {
        "label": "职业技术培训参与",
        "codes": {"2015": ["bd012"], "2018": ["bd012", "bd012_w4"]},
        "unit": "binary response (official codes retained per wave)",
        "period": "since prior interview or ever, depending on interview route",
        "response": "1=Yes; 2=No in the official codebook",
        "caveat": "2015 BD012 asks about training since ZIWTime. In 2018, BD012 and BD012_W4 reflect different reinterview/new-interview routes. Keep route, target denominator, and time window; do not infer No from a skipped follow-up.",
    },
    "vocational_training_episode_count": {
        "label": "职业技术培训参加次数",
        "codes": {"2015": ["bd013"], "2018": ["bd013", "bd013_w4"]},
        "unit": "times",
        "period": "since prior interview or route-defined reference period",
        "response": "continuous count; preserve source units and special values",
        "caveat": "The count is asked conditionally after training participation. 2018 BD013/BD013_W4 have route-specific reference periods. Codebook summary statistics are metadata only and must not be treated as participant-level values.",
    },
    "vocational_training_duration_months": {
        "label": "职业技术培训累计时长（月）",
        "codes": {"2018": ["bd014", "bd014_w4"]},
        "unit": "months",
        "period": "route-defined period in the 2018 questionnaire",
        "response": "continuous duration in months",
        "caveat": "2018 questionnaire/codebook defines BD014 and BD014_W4 duration in months. The 2015 BD014 is documented as a string variable with a different/unclear unit in its codebook; it is intentionally excluded pending source-format and unit reconciliation.",
    },
    "vocational_certificate_attained": {
        "label": "职业培训后是否获得职业证书",
        "codes": {"2018": ["bd015_w4"]},
        "unit": "binary response (official codes retained)",
        "period": "since prior interview for the routed 2018 form",
        "response": "1=Yes; 2=No",
        "caveat": "Single-wave candidate. The question follows vocational-training participation; retain its conditional denominator and verify disclosure-safe summaries before publication.",
    },
}

rows = []
for concept_id, spec in SPECS.items():
    for wave, codes in spec["codes"].items():
        for code in codes:
            found = raw[(raw.wave == wave) & raw.variable.str.lower().eq(code.lower())]
            if found.empty:
                raise SystemExit(f"Source field missing from official metadata: {wave} {code}")
            for rec in found.itertuples(index=False):
                option_match = re.search(r"s([1-8])$", code.lower()) if concept_id == "adult_education_program_participation" else None
                if option_match:
                    option = int(option_match.group(1))
                    if wave == "2018":
                        value_labels = f"0=No; {option}={OPTIONS[option]} (official codebook labels)"
                    else:
                        value_labels = f"{option}={OPTIONS[option]} (option category; unselected is not inferred as No)"
                elif concept_id in {"adult_education_degree_received", "vocational_training_participation", "vocational_certificate_attained"}:
                    value_labels = "1=Yes; 2=No (official value labels; route and special missing codes require wave-level review)"
                elif concept_id == "adult_education_highest_credential":
                    value_labels = "1=Vocational school; 2=Two/three-year college or associate degree; 3=Four-year college or bachelor's degree; 4=Other (official questionnaire categories; verify exact wave-specific codebook labels)"
                elif concept_id in {"adult_education_duration_years", "vocational_training_episode_count", "vocational_training_duration_months"}:
                    value_labels = ""
                else:
                    value_labels = ""
                rows.append({
                    "wave": wave,
                    "code": code,
                    "concept_id": concept_id,
                    "concept_label": spec["label"],
                    "domain": "sociodemographic and social context",
                    "module": rec.module,
                    "source_label": rec.variable_label,
                    "unit": spec["unit"],
                    "value_labels": value_labels,
                    "value_semantics": f"{spec['period']}; {spec['response']}",
                    "mapping_status": "candidate exposure mapping; official questionnaire/codebook field identified; route, denominator and value review required",
                    "construct": spec["period"],
                    "caveat": spec["caveat"],
                    "source_archive": f"{rec.source}; {DOC[wave]}",
                })

out = pd.DataFrame(rows).drop_duplicates(["wave", "code", "concept_id"])
out.to_csv(AUDIT / "adult_education_training_exposure_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
summary = (out.groupby(["concept_id", "concept_label"], dropna=False)
           .agg(waves=("wave", lambda x: ",".join(sorted(set(x)))),
                source_fields=("code", "size"),
                source_codes=("code", lambda x: ";".join(sorted(set(x)))))
           .reset_index())
summary.to_csv(AUDIT / "adult_education_training_exposure_summary_v1.csv", index=False, encoding="utf-8-sig")
print(f"adult education/training candidate concepts={out.concept_id.nunique()} mappings={len(out)}")
print(out.groupby("concept_id").size().to_string())
