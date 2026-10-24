"""Audit 2018 housing-owner relation response labels without using counts."""
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
rows = mapping.loc[mapping.concept_id.eq("household_property_owner_relation_slots"), ["wave", "code"]].drop_duplicates()
codebook = (ROOT / "sources_official/CHARLS_2018_Codebook_extracted.txt").read_text(encoding="utf-8", errors="ignore")
starts = list(re.finditer(r"(?m)^([^\n]+):\s*(.*?)\s*$", codebook))
blocks = {}
for i, match in enumerate(starts):
    code = match.group(1).strip().lower()
    if code not in set(rows.code.str.lower()):
        continue
    body = codebook[match.end():starts[i + 1].start() if i + 1 < len(starts) else len(codebook)]
    # Extract only official category text; never copy Freq. or % columns/counts.
    labels = {value: label for value, label in re.findall(
        r"(?m)^\s*(\d+)\s+(Do Not Own|Own)\s*$", body
    )}
    blocks[code] = labels

out = []
for row in rows.itertuples(index=False):
    labels = blocks.get(str(row.code).lower(), {})
    out.append({
        "wave": row.wave, "code": row.code,
        "value_labels": "; ".join(f"{value}={labels[value]}" for value in sorted(labels, key=int)),
        "value_label_status": "official Codebook listed ownership labels transcribed; frequencies omitted; unlisted categories not inferred",
        "value_label_source": "sources_official/CHARLS_2018_Codebook_extracted.txt",
    })
result = pd.DataFrame(out)
if len(result) != len(rows) or result.code.nunique() != len(rows) or len(blocks) != len(rows):
    raise SystemExit(f"owner-relation field coverage mismatch: rows={len(rows)}, parsed={len(blocks)}")
result.to_csv(ROOT / "audit/housing_owner_relation_value_label_review_v1.csv", index=False, encoding="utf-8-sig")
print(f"2018 owner-relation fields={len(result)}; fields with listed labels={result.value_labels.ne('').sum()}; frequencies omitted; unlisted categories not inferred")
