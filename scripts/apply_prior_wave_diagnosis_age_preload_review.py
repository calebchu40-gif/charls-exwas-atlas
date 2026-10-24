"""Reclassify 2013/2015 ZDA009 age fields as prior-wave preload metadata."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CATALOG = ROOT / "site-prototype/dist/catalog.json"
OUTPUT = AUDIT / "prior_wave_diagnosis_age_preload_crosswalk_v1.csv"
TARGETS = {"2013": 19, "2015": 14}
FAMILY = "prior-wave diagnosis-time preload values"
SUBCATEGORY = FAMILY
REVIEW_STATUS = (
    "official questionnaire and Codebook reviewed; continuous prior-wave diagnosis-age value; "
    "no discrete labels; authorized-release storage and prior-wave linkage require validation"
)
NOTE = (
    "Preloaded age component of the prior-interview answer to when the indexed condition was first "
    "diagnosed or known. This is historical source metadata, not a current-wave phenotype or an "
    "automatic adjustment covariate. Preserve the wave-specific disease slot; verify respondent "
    "linkage, special codes, and storage in the authorized release before any longitudinal use."
)


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def source_records() -> list[dict[str, str]]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected = [
        row for row in catalog
        if str(row.get("epcf", "")).lower() == "c"
        and str(row.get("Source.Wave", "")) in TARGETS
        and re.fullmatch(r"zda009_2(?:_\d+_)?", str(row.get("Variable.Name", "")).lower())
        and str(row.get("category", "")) == "automated covariate search hit"
    ]
    counts = {wave: sum(row.get("Source.Wave") == wave for row in selected) for wave in TARGETS}
    if counts != TARGETS:
        raise SystemExit(f"Expected prior-wave ZDA009 age-field counts {TARGETS}; observed {counts}")

    result = []
    for row in selected:
        wave = str(row["Source.Wave"])
        code = str(row["Variable.Name"]).lower()
        codebook_rel = f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        questionnaire_rel = f"sources_official/CHARLS_{wave}_Questionnaire_extracted.txt"
        codebook = (ROOT / codebook_rel).read_text(encoding="utf-8", errors="replace")
        questionnaire = (ROOT / questionnaire_rel).read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        if compact(code + "Age") not in compact(codebook):
            raise SystemExit(f"Codebook does not support {wave}/{code} as Age")
        q = compact(questionnaire)
        if "zda009" not in q or "whenwastheconditionfirstdiagnosedorknownbyyourself" not in q or "ziwtime" not in q:
            raise SystemExit(f"Questionnaire preload prompt/context not verified for {wave}/{code}")
        result.append({
            "wave": wave,
            "code": code,
            "metadata_family": FAMILY,
            "official_sources": f"{questionnaire_rel}; {codebook_rel}",
            "source_field_label": str(row.get("Variable.Description", "")),
            "review_status": REVIEW_STATUS,
            "value_labels": "",
            "catalog_note": NOTE,
        })
    return sorted(result, key=lambda row: (row["wave"], row["code"]))


def update_row(row: dict[str, object], item: dict[str, str]) -> None:
    row["category"] = "measurement metadata"
    row["subcategory"] = SUBCATEGORY
    row["Candidate.Status"] = "official questionnaire and Codebook reviewed; prior-wave diagnosis-time preload metadata"
    row["Harmonization.Status"] = NOTE
    row["Review.Flag"] = NOTE
    row["Value.Labels"] = ""
    row["Value.Label.Source"] = item["official_sources"]
    row["Value.Label.Review"] = REVIEW_STATUS
    row["value_labels"] = ""
    row["harmonization_status"] = NOTE
    row["value_label_source"] = item["official_sources"]
    row["value_label_review"] = REVIEW_STATUS


def propagate(records: list[dict[str, str]]) -> None:
    targets = {(r["wave"], r["code"]): r for r in records}
    for rel in ("audit/charls_atlas_candidate_fields_v0.csv", "audit/charls_atlas_candidate_fields_v0.json", "site-prototype/dist/catalog.json"):
        path = ROOT / rel
        if not path.exists():
            continue
        updated = 0
        if path.suffix == ".csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            for (wave, code), item in targets.items():
                mask = (df["Source.Wave"].eq(wave) & df["Variable.Name"].str.lower().eq(code) & df["epcf"].str.lower().eq("c"))
                if mask.any():
                    df.loc[mask, "category"] = "measurement metadata"
                    df.loc[mask, "subcategory"] = SUBCATEGORY
                    df.loc[mask, "Candidate.Status"] = "official questionnaire and Codebook reviewed; prior-wave diagnosis-time preload metadata"
                    df.loc[mask, "Harmonization.Status"] = NOTE
                    df.loc[mask, "Review.Flag"] = NOTE
                    df.loc[mask, "Value.Labels"] = ""
                    df.loc[mask, "Value.Label.Source"] = item["official_sources"]
                    df.loc[mask, "Value.Label.Review"] = REVIEW_STATUS
                    updated += int(mask.sum())
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} C fields in {rel}; updated {updated}")
            df.to_csv(path, index=False, encoding="utf-8-sig")
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
            for row in data:
                key = (str(row.get("Source.Wave", "")), str(row.get("Variable.Name", "")).lower())
                if key in targets and str(row.get("epcf", "")).lower() == "c":
                    update_row(row, targets[key])
                    updated += 1
            if updated != len(targets):
                raise SystemExit(f"Expected {len(targets)} C fields in {rel}; updated {updated}")
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"Reviewed and reclassified {len(records)} prior-wave diagnosis-age fields; kept C-only with no value labels.")


if __name__ == "__main__":
    propagate(source_records())
