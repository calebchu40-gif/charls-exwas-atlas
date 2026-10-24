"""Build child-level hukou/location-history context candidates from reviewed sources."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

SOURCES = {
    "2013": "sources_official/CHARLS_2013_Questionnaire_extracted.txt; sources_official/CHARLS_2013_Codebook_extracted.txt",
    "2015": "sources_official/CHARLS_2015_Questionnaire_extracted.txt; sources_official/CHARLS_2015_Codebook_extracted.txt",
}
LINKAGE = (
    "The official raw inventory lists this code in the wave's Child module and lists ID, childID, and "
    "HHmemberID in that module. The extracted questionnaires/Codebooks document corresponding Childn "
    "family-information slots, but do not provide a one-to-one crosswalk from each slot to the Child "
    "record field. Treat the item/label association as a metadata candidate; verify field identity, "
    "coding, respondent joins, and missing-link semantics in the authorized release. This is a "
    "child-level social-context measure, not an individual environmental dose. Children are clustered "
    "within respondents; any analysis must preserve its estimand and account for that dependence. "
    "Codebook frequencies are omitted."
)

# Response categories reproduce the official questionnaire/Codebook category labels only. Frequencies,
# extrema, and summary statistics are intentionally not included. Wave-specific menus stay separate.
SPECS = [
    ("2013", "cb056", "offspring_hukou_location_matches_residence_2013", "子女户口所在地是否与居住地相同（2013）", "Hukou location same as place of residence", "1=Yes; 2=No", "binary response; see questionnaire route", "The Yes route skips to the birth-location branch; retain item routing and do not interpret a skipped follow-up as a negative response."),
    ("2013", "cb057", "offspring_current_hukou_location", "子女当前户口所在地类别（2013/2015）", "Current hukou location of child", "1=This household; 2=His/her birthplace; 3=Respondent's permanent-address village/neighborhood; 4=Another village/neighborhood in respondent's permanent-address county/city/district; 5=Other county/city/district; 6=Other", "categorical location context; not geocoded", "Location wording is wave-specific; the 2015 menu uses a different label for option 6. Do not publish address write-ins or derive precise geography."),
    ("2015", "cb057", "offspring_current_hukou_location", "子女当前户口所在地类别（2013/2015）", "Current hukou place of child", "1=This household; 2=His/her birthplace; 3=Respondent's permanent-address village/neighborhood; 4=Another village/neighborhood in respondent's permanent-address county/city/district; 5=Other; 6=Abroad", "categorical location context; not geocoded", "The response menu differs from 2013 and must remain wave-specific. Do not publish address write-ins or derive precise geography."),
    ("2013", "cb081", "offspring_birthplace_location_2013", "子女出生地类别（2013）", "Birth place of child", "1=Respondent's permanent-address village/neighborhood; 2=Another village/neighborhood in respondent's permanent-address county/city/district; 3=Other county/city/district; 4=Abroad", "categorical location context; not geocoded", "This is a coarse birthplace category, not a geographic identifier; keep separate from the 2015 birthplace menu."),
    ("2015", "cb081", "offspring_birthplace_location_2015", "子女出生地类别（2015）", "Location where child was born", "1=His/her birthplace; 2=Respondent's birthplace; 3=Respondent's permanent-address village/neighborhood; 4=Another village/neighborhood in respondent's permanent-address county/city/district; 5=Other", "categorical location context; not geocoded", "The 2015 response menu differs from 2013; retain as a wave-specific concept and do not infer geocoded location."),
    ("2013", "cb082", "offspring_current_hukou_same_as_first_2013", "子女当前户口与首次户口是否相同（2013）", "Hukou status is same as his/her first hukou", "1=Yes; 2=No", "binary life-course context", "Status/location history is self/proxy reported as asked in the questionnaire; do not infer exact migration events from this item alone."),
    ("2013", "cb083", "offspring_hukou_change_type_2013", "子女户口状态或所在地变化类型（2013）", "Changing of hukou status/location", "1=Both hukou status and location have changed; 2=Only hukou status has changed; 3=Only hukou location has changed", "categorical life-course context", "Preserve the three distinct change categories; this item does not establish timing or causal exposure."),
    ("2013", "cb084", "offspring_first_hukou_status_2013", "子女首次户口性质（2013）", "First hukou status of child", "1=Agricultural hukou; 2=Non-agricultural hukou", "categorical hukou context", "Keep the historical first-status measure distinct from current hukou status."),
    ("2013", "cb085", "offspring_first_hukou_location_2013", "子女首次户口所在地类别（2013）", "First hukou location of child", "1=Respondent's permanent-address village/neighborhood; 2=Another village/neighborhood in respondent's permanent-address city/county; 3=Other county/city/district", "categorical location context; not geocoded", "The source is a coarse category; do not publish address write-ins or derive precise geography."),
    ("2013", "cb055_w2_1", "offspring_hukou_status_before_unified_residency", "子女户口统一登记前户口性质（2013/2015）", "Hukou status before Unified Residency", "1=Agricultural hukou; 2=Non-agricultural hukou; 3=Does not have hukou", "categorical hukou context", "Asked only on the unified-residency route; preserve eligibility and do not treat a skipped item as absence of hukou."),
    ("2015", "cb055_w2_1", "offspring_hukou_status_before_unified_residency", "子女户口统一登记前户口性质（2013/2015）", "Hukou status prior to Unified Residency", "1=Agricultural hukou; 2=Non-agricultural hukou; 3=Does not have hukou", "categorical hukou context", "Asked only when the current hukou response routes to the unified-residency follow-up; preserve eligibility and wave-specific routing."),
    ("2013", "cb055_w2_2", "offspring_year_of_unified_residency_hukou", "子女户口统一登记年份（2013/2015）", "Year of having Unified Residency Hukou", "", "calendar year; numeric", "Asked only on the unified-residency route. Verify numeric storage, special codes, and allowed year bounds in the authorized release; do not apply Codebook extrema as validity limits."),
    ("2015", "cb055_w2_2", "offspring_year_of_unified_residency_hukou", "子女户口统一登记年份（2013/2015）", "Year child had the Unified Residency", "", "calendar year; numeric", "Asked only on the unified-residency route. Verify numeric storage, special codes, and allowed year bounds in the authorized release; do not apply Codebook extrema as validity limits."),
]

rows = []
for wave, code, concept_id, label, source_label, value_labels, unit, caveat in SPECS:
    found = RAW[(RAW.wave == wave) & RAW.module.str.lower().eq("child") & RAW.variable.str.lower().eq(code)]
    if found.empty:
        raise SystemExit(f"Missing official raw-catalog Child field: {wave}/{code}")
    rec = found.iloc[0]
    rows.append({
        "wave": wave, "code": code, "concept_id": concept_id, "concept_label": label,
        "domain": "family and intergenerational context", "subcategory": "child hukou and location history",
        "module": "Child", "source_label": source_label,
        "mapping_status": "official raw inventory field; same-stem questionnaire/Codebook item candidate; exact record-field crosswalk and release coding validation pending",
        "unit": f"linked child record (ID + childID); {unit}", "value_labels": value_labels,
        "value_label_status": (
            "official questionnaire/Codebook slot categories reviewed; frequencies omitted; exact Child-field coding alignment requires authorized-release validation"
            if value_labels else "continuous year item reviewed in questionnaire/Codebook context; special-value and storage validation required"
        ),
        "value_label_source": SOURCES[wave],
        "construct": f"{label}; retain ID and childID linkage and wave-specific response coding.",
        "value_semantics": "child-level hukou/residential-history context linked to a CHARLS respondent; not an individual environmental exposure dose",
        "caveat": f"{caveat} {LINKAGE}", "source_archive": f"{rec.source}; official questionnaire/Codebook context",
    })

out = pd.DataFrame(rows)
if out.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate child-hukou wave/code")
out.to_csv(AUDIT / "child_hukou_lifecourse_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print(f"child hukou/location-history candidate mappings={len(out)}; concepts={out.concept_id.nunique()}; frequencies excluded")
