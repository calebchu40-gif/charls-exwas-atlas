"""Apply the audited Wave 4 current-home ownership-share metadata to field catalogs.

This updates public metadata only. It does not read participant-level data or
publish observed values, frequencies, or Codebook summary statistics.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WAVE = "2018"
CODES = {"i000_w4_4_1", "i000_w4_4_3", "i000_w4_4_6", "i000_w4_4_7", "i000_w4_4_8"}
UNIT = "% of the specific house's property rights"
STATUS = (
    "official 2018 questionnaire confirms continuous percentage share; no discrete labels; "
    "Codebook summary extrema are not valid-range evidence; verify route and special values"
)
SOURCE = (
    "sources_official/CHARLS_2018_Questionnaire_extracted.txt; "
    "sources_official/CHARLS_2018_Codebook_extracted.txt"
)
HARMONIZATION = (
    "2018 current-home ownership share by listed relationship slot, reported as percent; "
    "continuous numeric measure, not a categorical label. Preserve each slot and the "
    "question's multi-response/household route; do not sum across slots or infer respondent "
    "ownership. Valid range, special values, eligible denominator, and missing-slot semantics "
    "require authorized-release QA before analysis. Codebook summary extrema do not define a valid range."
)


def update_field(row: dict) -> None:
    row["Concept.Unit.Candidates"] = UNIT
    row["Value.Labels"] = ""
    row["Value.Label.Review"] = STATUS
    row["Value.Label.Source"] = SOURCE
    row["Harmonization.Status"] = HARMONIZATION
    # Keep the lower-case aliases in the audit JSON synchronized where present.
    row["candidate_concept_units"] = UNIT
    row["value_labels"] = ""
    row["value_label_review"] = STATUS
    row["value_label_source"] = SOURCE
    row["harmonization_status"] = HARMONIZATION


def update_field_catalog_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df["Source.Wave"].astype(str).eq(WAVE) & df["Variable.Name"].str.lower().isin(CODES)
    found = set(df.loc[selected, "Variable.Name"].str.lower())
    if found != CODES:
        raise ValueError(f"{path}: expected exactly the five reviewed Wave 4 fields; found {sorted(found)}")
    df.loc[selected, "Concept.Unit.Candidates"] = UNIT
    df.loc[selected, "Value.Labels"] = ""
    df.loc[selected, "Value.Label.Review"] = STATUS
    df.loc[selected, "Value.Label.Source"] = SOURCE
    df.loc[selected, "Harmonization.Status"] = HARMONIZATION
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_field_catalog_json(path: Path) -> int | None:
    rows = json.loads(path.read_text(encoding="utf-8"))
    # Some internal concept-summary exports do not carry wave-level field
    # identity. Leave those summaries untouched; the field-level catalogs are
    # updated below and are the files consumed by the interactive lookup.
    if rows and "Source.Wave" not in rows[0]:
        print(f"Skipped non-wave-level summary: {path.relative_to(ROOT)}")
        return None
    selected = [r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() in CODES]
    found = {str(r["Variable.Name"]).lower() for r in selected}
    if found != CODES:
        raise ValueError(f"{path}: expected all five reviewed Wave 4 fields; found {sorted(found)}")
    for row in selected:
        update_field(row)
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def update_housing_json(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    selected = [r for r in rows if str(r.get("wave", "")) == WAVE and str(r.get("code", "")).lower() in CODES]
    found = {str(r["code"]).lower() for r in selected}
    if found != CODES:
        raise ValueError(f"{path}: expected all five reviewed Wave 4 housing fields; found {sorted(found)}")
    for row in selected:
        row["unit"] = UNIT
        row["mapping_status"] = "official 2018 questionnaire identifies continuous percent share; routes and special values still require authorized-release QA"
        row["caveat"] = HARMONIZATION
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(selected)


def main() -> None:
    mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    selected = mapping.loc[mapping["wave"].eq(WAVE) & mapping["code"].str.lower().isin(CODES)]
    if set(selected["code"].str.lower()) != CODES or not selected["unit"].eq(UNIT).all():
        raise ValueError("Housing crosswalk does not contain the reviewed percent unit for exactly the five fields")
    results = [
        update_field_catalog_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv"),
        update_field_catalog_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json"),
        update_field_catalog_json(ROOT / "site-prototype/dist/catalog.json"),
        update_field_catalog_json(ROOT / "site-prototype/dist/catalog_e.json"),
        update_housing_json(ROOT / "site-prototype/dist/housing_catalog_v1.json"),
    ]
    applied = [count for count in results if count is not None]
    if any(count < len(CODES) for count in applied):
        raise ValueError(f"One or more field-level outputs are missing reviewed fields: {results}")
    print(f"Applied audited Wave 4 continuous ownership-share metadata to {sum(applied)} field rows; no values or frequencies included.")


if __name__ == "__main__":
    main()
