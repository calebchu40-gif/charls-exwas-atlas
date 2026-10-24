"""Classify 2013 reproductive-history preload fields as historical metadata."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CATALOG = ROOT / "site-prototype/dist/catalog.json"
OUTPUT = AUDIT / "reproductive_history_preload_metadata_crosswalk_v1.csv"
TARGETS = {
    "zda026_2": "menarche age at prior interview",
    "zda028_2": "menopause age at prior interview",
}
QUESTIONNAIRE = "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
CODEBOOK = "sources_official/CHARLS_2013_Codebook_extracted.txt"
REVIEW_STATUS = (
    "2013 official questionnaire and Codebook reviewed; prior-interview age field stored as string; "
    "no categorical labels or respondent data used"
)
NOTE = (
    "Prior-interview reproductive-history preload, not a newly measured 2013 exposure or phenotype. "
    "The Codebook identifies the _2 component as age but records it as a string; preserve it as "
    "historical source metadata and verify field identity, parsing, linkage, and special values in "
    "the authorized release before any longitudinal use. Do not infer values for routed skips."
)


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def source_records() -> list[dict[str, str]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected = [
        row for row in catalog
        if str(row.get("epcf", "")).lower() == "c"
        and str(row.get("Source.Wave", "")) == "2013"
        and str(row.get("Variable.Name", "")).lower() in TARGETS
    ]
    found = {str(row["Variable.Name"]).lower() for row in selected}
    if found != set(TARGETS) or len(selected) != len(TARGETS):
        raise SystemExit(f"Expected exactly C-only preload fields {sorted(TARGETS)}; got {sorted(found)}")

    questionnaire = (ROOT / QUESTIONNAIRE).read_text(encoding="utf-8", errors="replace")
    codebook = (ROOT / CODEBOOK).read_text(encoding="utf-8", errors="replace")
    q = compact(questionnaire)
    if "zda026beganmenarchetime" not in q or "zda028timeofmenopause" not in q:
        raise SystemExit("Questionnaire does not identify both prior-interview reproductive preloads")
    if "zda027ifda027yeszda027yesrhadstartedmenopauseatrs" not in q:
        raise SystemExit("Questionnaire prior-interview menopause context not verified")

    result = []
    for row in selected:
        code = str(row["Variable.Name"]).lower()
        # The Codebook calls each field Age and documents its storage as a
        # string; numeric extrema and frequencies are deliberately not copied.
        code_pattern = re.compile(rf"{re.escape(code)}\s*:?\s*(?:the age of menarche occured|age|the age of menopause)", re.I)
        if not code_pattern.search(codebook):
            raise SystemExit(f"Codebook does not identify {code} as an age field")
        result.append({
            "wave": "2013",
            "code": code,
            "metadata_family": TARGETS[code],
            "official_sources": f"{QUESTIONNAIRE}; {CODEBOOK}",
            "source_field_label": str(row.get("Variable.Description", "")),
            "review_status": REVIEW_STATUS,
            "value_labels": "",
            "catalog_note": NOTE,
        })
    return sorted(result, key=lambda row: row["code"])


def propagate(records: list[dict[str, str]]) -> None:
    targets = {(r["wave"], r["code"]): r for r in records}
    for rel in (
        "audit/charls_atlas_candidate_fields_v0.csv",
        "audit/charls_atlas_candidate_fields_v0.json",
        "site-prototype/dist/catalog.json",
    ):
        path = ROOT / rel
        if not path.exists():
            continue
        updated = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for (wave, code), item in targets.items():
                mask = (
                    df["Source.Wave"].eq(wave)
                    & df["Variable.Name"].str.lower().eq(code)
                    & df["epcf"].str.lower().eq("c")
                )
                if mask.any():
                    df.loc[mask, "category"] = "measurement metadata"
                    df.loc[mask, "subcategory"] = "prior-wave reproductive-history preload values"
                    df.loc[mask, "Candidate.Status"] = "official questionnaire and Codebook reviewed; prior-wave reproductive-history preload metadata"
                    df.loc[mask, "Harmonization.Status"] = NOTE
                    df.loc[mask, "Review.Flag"] = NOTE
                    df.loc[mask, "Value.Labels"] = ""
                    df.loc[mask, "Value.Label.Source"] = item["official_sources"]
                    df.loc[mask, "Value.Label.Review"] = REVIEW_STATUS
                    updated += int(mask.sum())
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} fields in {rel}; updated {updated}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                if key not in targets or str(row.get("epcf", "")).lower() != "c":
                    continue
                item = targets[key]
                row.update({
                    "category": "measurement metadata",
                    "subcategory": "prior-wave reproductive-history preload values",
                    "Candidate.Status": "official questionnaire and Codebook reviewed; prior-wave reproductive-history preload metadata",
                    "Harmonization.Status": NOTE,
                    "Review.Flag": NOTE,
                    "Value.Labels": "",
                    "Value.Label.Source": item["official_sources"],
                    "Value.Label.Review": REVIEW_STATUS,
                    "value_labels": "",
                    "value_label_source": item["official_sources"],
                    "value_label_review": REVIEW_STATUS,
                    "harmonization_status": NOTE,
                })
                updated += 1
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} fields in {rel}; updated {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Reviewed {len(records)} prior-wave reproductive-history fields; retained C-only metadata and no labels.")


if __name__ == "__main__":
    propagate(source_records())
