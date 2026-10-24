"""Build the source-reviewed childhood residential-setting candidate mapping."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
RAW = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")

wave, code = "2013", "bb006"
matches = RAW[(RAW.wave == wave) & RAW.variable.str.lower().eq(code)]
if matches.empty:
    raise SystemExit("Missing official 2013 source field: 2013/bb006")

questionnaire_path = ROOT / "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
questionnaire = questionnaire_path.read_bytes().replace(b"\x00", b"").decode("utf-8", errors="replace")
item_start = questionnaire.lower().find("bb006 where did you mainly live before you were 16 years old")
if item_start < 0:
    raise SystemExit("Official 2013 questionnaire BB006 question not found")
item_text = questionnaire[item_start:item_start + 1100]
if "1. Village" not in item_text or "2. City/Town" not in item_text:
    raise SystemExit("Official 2013 questionnaire BB006 categories differ from the reviewed mapping")
normalized_questionnaire = re.sub(r"\s+", " ", questionnaire).lower()
if "if xrtype = reiw and bb006 in the last wave is not missing" not in normalized_questionnaire:
    raise SystemExit("Official 2013 BB006 carry-forward/reinterview route not found")

codebook_path = ROOT / "sources_official/CHARLS_2013_Codebook_extracted.txt"
codebook = codebook_path.read_text(encoding="utf-8", errors="replace")
codebook_start = codebook.lower().find("bb006 : where did you live before 16 years old")
if codebook_start < 0 or "1 Village" not in codebook[codebook_start:codebook_start + 300] or "2 City/Town" not in codebook[codebook_start:codebook_start + 300]:
    raise SystemExit("Official 2013 Codebook BB006 labels do not match the reviewed mapping")

source = matches.iloc[0]
questionnaire_rel = "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
codebook_rel = "sources_official/CHARLS_2013_Codebook_extracted.txt"
row = {
    "wave": wave,
    "code": code,
    "concept_id": "childhood_residential_setting_before_16_2013",
    "concept_label": "16岁前主要居住地城乡属性（2013）",
    "domain": "early-life and family socioeconomic context",
    "subcategory": "childhood residential setting",
    "module": source.module,
    "source_label": "Where did You Live Before 16 Years Old",
    "mapping_status": "single-wave candidate; 2013 questionnaire and Codebook agree on the item and category labels; cross-wave harmonization is not established",
    "unit": "respondent-reported childhood residential setting before age 16",
    "value_labels": "1=Village; 2=City/Town",
    "value_label_status": "official 2013 questionnaire and Codebook categories reviewed; frequencies omitted",
    "value_label_source": f"{questionnaire_rel}; {codebook_rel}",
    "construct": "Self-reported predominant residential setting before age 16; preserve source wave and respondent-reported time frame",
    "value_semantics": "categorical nominal response; the source asks village versus city/town; do not derive ambient pollution, exact residence, or duration",
    "caveat": (
        "The 2013 questionnaire and Codebook agree that 1=Village and 2=City/Town. "
        "The 2011 questionnaire gives the same labels, but the 2011 Codebook reverses them; the 2011 source conflict is documented separately and its field is deliberately not mapped here. "
        "In 2013, returning respondents skip the question when BB006 is already present in the prior wave, so the stored value may be carried forward rather than newly elicited in 2013. "
        "Treat this as a single-wave search candidate only; do not combine 2011/2013 codes or interpret categories as measured pollution."
    ),
    "source_archive": f"{source.source}; {questionnaire_rel}; {codebook_rel}",
}
out = pd.DataFrame([row])
if out.duplicated(["wave", "code"]).any():
    raise SystemExit("Duplicate wave/code in childhood residential-context crosswalk")
out.to_csv(AUDIT / "childhood_residential_context_crosswalk_v1.csv", index=False, encoding="utf-8-sig")
print("Wrote 1 source-reviewed 2013 childhood residential-setting candidate; 2011 conflict remains excluded")
