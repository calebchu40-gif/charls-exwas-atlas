"""Build the wave-specific residential settlement-context lookup."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
OUT = AUDIT / "residential_settlement_exposure_crosswalk_v1.csv"

wave_specs = {
    "2015": {
        "code": "bb001_w3_2", "module": "Demographic_Background",
        "label": "Was It Village or City/Town",
        "labels": "1=Main city zone; 2=Combination zone between urban and rural areas; 3=Town center; 4=Zhenxiang area; 5=Special area; 6=Township central; 7=Village",
        "questionnaire": "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
        "route": "The field describes the respondent's stated current/permanent address; preserve all seven wave-specific categories.",
        "archive": "CHARLS2015r.zip",
    },
    "2018": {
        "code": "bb001_w3_2", "module": "Demographic_Background",
        "label": "Type of Residential Address / Was Your Address in Village or City/Town",
        "labels": "1=City/town center; 2=Combination zone between urban and rural areas; 3=Village; 4=Special area",
        "questionnaire": "sources_official/CHARLS_2018_Questionnaire_extracted.txt",
        "route": "The 2018 questionnaire asks the BB001-BB005 section of new interviewees (XRType=2); it is not a universal repeated measure among returners.",
        "archive": "CHARLS2018r.zip",
    },
    "2020": {
        "code": "ba008", "module": "Demographic_Background",
        "label": "Was It Village or City/Town",
        "labels": "1=City/town center; 2=Combination zone between urban and rural areas/Zhenxiang area; 3=Village; 4=Special area",
        "questionnaire": "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
        "route": "The questionnaire ties this item to the respondent's residential-address question (BA006/BA007); retain the source address/time frame and do not infer ambient environmental quality.",
        "archive": "CHARLS2020r.zip",
    },
}

raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
rows = []
for wave, spec in wave_specs.items():
    source = raw[(raw.wave == wave) & (raw.variable.str.lower() == spec["code"].lower())]
    if source.empty:
        raise SystemExit(f"No source catalog match: {wave} {spec['code']}")
    questionnaire_text = (ROOT / spec["questionnaire"].replace("/", "\\")).read_text(encoding="utf-8", errors="ignore").lower()
    code = spec["code"].lower()
    if code not in questionnaire_text and code.upper().lower() not in questionnaire_text:
        raise SystemExit(f"Official questionnaire item not found: {wave} {code}")
    codebook = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    rows.append({
        "wave": wave, "code": spec["code"],
        "concept_id": "residential_settlement_type",
        "concept_label": "居住地址城乡/聚落类别",
        "domain": "social determinants", "module": spec["module"],
        "source_label": spec["label"], "value_labels": spec["labels"],
        "value_label_status": "official wave questionnaire and codebook categories reviewed; frequencies omitted",
        "value_label_source": f"{spec['questionnaire']}; {codebook}",
        "mapping_status": "wave-specific residential settlement-context candidate; item and response categories reviewed",
        "construct": "Categorical settlement context of the respondent's residential address",
        "value_semantics": "nominal/ordered-by-definition only within wave; codes and category boundaries differ across waves",
        "caveat": "This is residence context, not hukou registration type and not a measured environmental pollutant. " + spec["route"] + " Do not harmonize by numeric code; define any urban/rural collapse before analysis and report its rationale.",
        "source_archive": f"{spec['archive']}; {spec['questionnaire']}; {codebook}",
        "questionnaire_source": spec["questionnaire"],
    })
df = pd.DataFrame(rows)
if df.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate residential-settlement wave/code rows")
df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Wrote {len(df)} wave-field rows for {df.concept_id.nunique()} residential-context concept")
