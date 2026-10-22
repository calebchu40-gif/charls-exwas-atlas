"""Correct audited 2011 household-questionnaire citations before catalog builds."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
BAD = "sources_official/CHARLS_2011_Questionnaire_extracted.txt"
GOOD = "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"

# These audited 2011 records are all from the baseline household questionnaire.
TARGETS = {
    "assistive_device_phenotype_crosswalk_v1.csv": {"code": {f"db029s{i}" for i in range(1, 8)}},
    "measurement_protocol_crosswalk_v1.csv": {"code": {"hd012"}},
}

changed = 0
for name, selectors in TARGETS.items():
    path = AUDIT / name
    frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = frame.get("wave", pd.Series(index=frame.index, dtype=str)).astype(str).eq("2011")
    for column, values in selectors.items():
        mask &= frame[column].astype(str).str.lower().isin({v.lower() for v in values})
    for column in frame.columns:
        if any(token in column.lower() for token in ("source", "document", "questionnaire")):
            old = frame.loc[mask, column].str.count(BAD).sum()
            frame.loc[mask, column] = frame.loc[mask, column].str.replace(BAD, GOOD, regex=False)
            changed += int(old)
    frame.to_csv(path, index=False, encoding="utf-8-sig")
print(f"corrected audited 2011 source-path occurrences={changed}")
