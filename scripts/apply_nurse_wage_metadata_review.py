"""Review the conditional 2015 nurse-wage item as non-exposure context metadata."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE = "2015"
CODE = "db035_w3_2"
QUESTIONNAIRE = "sources_official/CHARLS_2015_Questionnaire_extracted.txt"
CODEBOOK = "sources_official/CHARLS_2015_Codebook_extracted.txt"
FAMILY = "conditional nurse-care wage metadata"
UNIT = "Yuan/month (reported wage last month)"
STATUS = "official questionnaire and Codebook reviewed; amount in Yuan for prior-month nurse wage; conditional on nurse hiring"
NOTE = (
    "DB035_W3_2 records the amount paid to a nurse in the last month, including in-kind value, "
    "only after DB035_W3_1 indicates a nurse was hired; the preceding item separately routes hourly-worker cases. "
    "This is a conditional care-service expense/context measure, not an environmental exposure or health phenotype. "
    "Preserve the route and do not code skipped responses as zero or use it as a default adjustment covariate."
)


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def main() -> None:
    q = (ROOT / QUESTIONNAIRE).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    cb = (ROOT / CODEBOOK).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
    if compact(CODE) not in compact(q) or "howmuchisthetotalwageofnurselastmonth" not in compact(q):
        raise SystemExit("2015 questionnaire does not verify nurse wage item")
    if compact(CODE) not in compact(cb):
        raise SystemExit("2015 Codebook does not identify the nurse wage field")
    q_compact = compact(q)
    route = compact("If DB035_W3_1=1 ask DB035_W3_2-DB035_W3_3")
    if route not in q_compact:
        raise SystemExit("Nurse-hiring route for DB035_W3_2 not verified")
    note = NOTE
    audit = {
        "wave": WAVE,
        "code": CODE,
        "source_field_label": "How Much is The Total Wage of Nurse Last Month",
        "official_sources": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "unit": UNIT,
        "route": "Asked only if DB035_W3_1 indicates a nurse was hired; hourly-worker items use a separate route.",
        "review_status": STATUS,
        "catalog_note": note,
    }
    pd.DataFrame([audit]).to_csv(ROOT / "audit/nurse_wage_metadata_review_2015_v1.csv", index=False, encoding="utf-8-sig")
    catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
    matches = [r for r in catalog if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() == CODE and str(r.get("epcf", "")).lower() == "c"]
    if len(matches) != 1:
        raise SystemExit(f"Expected one C field row; observed {len(matches)}")
    row = matches[0]
    row.update({
        "category": "measurement metadata",
        "subcategory": FAMILY,
        "Candidate.Status": "official questionnaire and Codebook reviewed; conditional care-service expense metadata",
        "Harmonization.Status": note,
        "Review.Flag": "C conditional care-service expense; not an exposure or selected adjustment covariate",
        "Unit": UNIT,
        "Concept.Unit.Candidates": UNIT,
        "Value.Labels": "",
        "Value.Label.Source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "Value.Label.Review": STATUS,
        "value_labels": "",
        "value_label_source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "value_label_review": STATUS,
        "unit": UNIT,
        "candidate_concept_units": UNIT,
        "harmonization_status": note,
    })
    path = ROOT / "site-prototype/dist/catalog.json"
    path.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    csv_path = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
    df = pd.read_csv(csv_path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = df["Source.Wave"].eq(WAVE) & df["Variable.Name"].str.lower().eq(CODE) & df["epcf"].str.lower().eq("c")
    if int(mask.sum()) != 1:
        raise SystemExit(f"Expected one C row in candidate fields; observed {int(mask.sum())}")
    for key, value in row.items():
        if key in df.columns:
            df.loc[mask, key] = value
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print("Reviewed 2015 conditional nurse wage; assigned Yuan/month and retained it as C context metadata.")


if __name__ == "__main__":
    main()
