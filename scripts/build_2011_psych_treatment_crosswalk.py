"""Add 2011 DA020 treatment options to the existing treatment concept.

Uses official variable metadata/question wording only; no respondent records
or codebook frequencies are used.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
labels = {
    "da020s1": "Receiving psychiatric or psychological treatment",
    "da020s2": "Taking antidepressants",
    "da020s3": "Taking tranquilizers or sleeping pills",
    "da020s4": "None of the above",
}
raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str,
                  encoding="utf-8-sig").fillna("")
raw = raw[(raw.wave == "2011") & raw.variable.str.lower().isin(labels)]
by_code = {r.variable.lower(): r for r in raw.itertuples(index=False)}
missing = sorted(set(labels) - set(by_code))
if missing:
    raise SystemExit(f"missing 2011 DA020 metadata: {missing}")

rows = []
for code, response in labels.items():
    rec = by_code[code]
    option = int(code[-1])
    rows.append({
        "wave": "2011", "code": code,
        "concept_id": "reported_treatment_emotional_psychiatric",
        "concept_label": "自报情绪/神经/精神问题治疗方式",
        "domain": "chronic disease ancillary", "module": rec.module,
        "source_label": rec.variable_label, "source_item": "DA020 multi-select",
        "construct": "Current reported treatment for emotional, nervous, or psychiatric problems",
        "unit": "categorical multi-select",
        "value_labels": (
            f"{option}={response} (selected option; unselected storage code not inferred)"
            if code == "da020s2" else f"{option}={response}"
        ),
        "value_semantics": f"Selected option {option} represents: {response}. The item is about current treatment, not a diagnosis.",
        "mapping_status": "2011 questionnaire and CodeBook response label reviewed; mapped to existing treatment concept",
        "caveat": "DA020 asks about current treatment and allows multiple selections. Do not treat treatment as evidence of physician-diagnosed disease. An unselected/blank slot is not automatically No; option 4 is the explicit 'None of the above' response.",
        "source_archive": rec.source,
        "official_source": "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt; sources_official/CHARLS_2011_Codebook_extracted.txt",
    })
out = AUDIT / "psych_treatment_2011_crosswalk_v1.csv"
pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
print(f"2011 DA020 treatment options reviewed={len(rows)}; new E/P mappings=2 (da020s3/s4)")
