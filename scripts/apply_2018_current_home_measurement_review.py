"""Apply audited Wave 4 current-home measurement metadata to field catalogs.

This updates public metadata only. It does not read participant-level data or
publish observed values, frequencies, or Codebook summary statistics.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WAVE = "2018"
CODES = {"i000_w4_4_1", "i000_w4_4_3", "i000_w4_4_6", "i000_w4_4_7", "i000_w4_4_8"}
SHARE_CODES = set(CODES)
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
MEASURES = {
    "i000_w4_11": {
        "unit": "square metres",
        "note": "2018 usable floor area; asked on the route where the respondent/spouse does not own property rights to the current home. Keep separate from i000_w4_12, which has a different ownership route and area wording.",
    },
    "i000_w4_12": {
        "unit": "square metres",
        "note": "2018 floor area of current home; asked on the respondent/spouse ownership route. Keep separate from i000_w4_11 (usable area on the no-ownership route); cross-wave or within-wave substitution is not approved.",
    },
    "i000_w4_13": {
        "unit": "Yuan/month",
        "note": "2018 monthly rent paid. Questionnaire interviewer instructions allow 0 when no rent is payable, while the CAPI may trigger unfolding brackets when the entered value is 0; do not interpret 0 without route and bracket-field review.",
    },
    "i000_w4_14": {
        "unit": "Yuan/month",
        "note": "2018 estimated market rent per month. It is distinct from rent actually paid; CAPI unfolding-bracket fields are interval metadata, not point estimates. Preserve route and special values.",
    },
    "i000_w4_15_1": {
        "unit": "10,000 Yuan",
        "note": "2018 current-home market total-price form. Keep separate from the alternative unit-price response i000_w4_15_2; do not convert or combine without a validated area and format selector.",
    },
    "i000_w4_15_2": {
        "unit": "1,000 Yuan/square metre",
        "note": "2018 current-home market unit-price form. Keep separate from the alternative total-price response i000_w4_15_1; do not convert or combine without a validated area and format selector.",
    },
    "i000_w4_16": {
        "unit": "calendar year",
        "note": "2018 year the current home was acquired or built; a calendar-year field, not a duration or age. Preserve special/missing values and confirm allowable years in authorized data.",
    },
    "i000_w4_17": {
        "unit": "10,000 Yuan",
        "note": "2018 amount spent to acquire or build the current home, in questionnaire reporting units. Historical acquisition amount is not current market value; preserve route and special/missing values.",
    },
}
REVIEW_CODES = SHARE_CODES | set(MEASURES)


def update_field(row: dict) -> None:
    code = str(row.get("Variable.Name", "")).lower()
    if code in MEASURES:
        unit = MEASURES[code]["unit"]
        note = MEASURES[code]["note"]
        row["Concept.Unit.Candidates"] = unit
        row["Value.Labels"] = ""
        row["Value.Label.Review"] = (
            f"official 2018 questionnaire identifies continuous numeric measure ({unit}); no discrete labels; "
            "Codebook summary extrema are not valid-range evidence; verify special values and route"
        )
        row["Value.Label.Source"] = SOURCE
        row["Harmonization.Status"] = (
            f"{note} Codebook summary extrema do not define a valid range; analyze only after authorized-release QA."
        )
        row["candidate_concept_units"] = unit
        row["value_labels"] = ""
        row["value_label_review"] = row["Value.Label.Review"]
        row["value_label_source"] = SOURCE
        row["harmonization_status"] = row["Harmonization.Status"]
        return
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
    selected = df["Source.Wave"].astype(str).eq(WAVE) & df["Variable.Name"].str.lower().isin(REVIEW_CODES)
    found = set(df.loc[selected, "Variable.Name"].str.lower())
    if found != REVIEW_CODES:
        raise ValueError(f"{path}: expected all reviewed Wave 4 home fields; found {sorted(found)}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        update_field(row)
        for key in ["Concept.Unit.Candidates", "Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status"]:
            df.at[idx, key] = row[key]
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
    selected = [r for r in rows if str(r.get("Source.Wave", "")) == WAVE and str(r.get("Variable.Name", "")).lower() in REVIEW_CODES]
    found = {str(r["Variable.Name"]).lower() for r in selected}
    if found != REVIEW_CODES:
        raise ValueError(f"{path}: expected all reviewed Wave 4 home fields; found {sorted(found)}")
    for row in selected:
        update_field(row)
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def update_housing_json(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    selected = [r for r in rows if str(r.get("wave", "")) == WAVE and str(r.get("code", "")).lower() in REVIEW_CODES]
    found = {str(r["code"]).lower() for r in selected}
    if found != REVIEW_CODES:
        raise ValueError(f"{path}: expected all reviewed Wave 4 housing fields; found {sorted(found)}")
    for row in selected:
        code = str(row["code"]).lower()
        if code in MEASURES:
            row["unit"] = MEASURES[code]["unit"]
            row["mapping_status"] = "official 2018 questionnaire identifies continuous numeric measure/unit; route and special values still require authorized-release QA"
            row["caveat"] = MEASURES[code]["note"] + " Codebook summary extrema are not valid-range evidence."
        else:
            row["unit"] = UNIT
            row["mapping_status"] = "official 2018 questionnaire identifies continuous percent share; routes and special values still require authorized-release QA"
            row["caveat"] = HARMONIZATION
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(selected)


def validate_official_sources() -> None:
    questionnaire = (ROOT / "sources_official/CHARLS_2018_Questionnaire_extracted.txt").read_bytes().decode("utf-8", errors="ignore").casefold()
    codebook = (ROOT / "sources_official/CHARLS_2018_Codebook_extracted.txt").read_text(encoding="utf-8", errors="ignore")
    for code in REVIEW_CODES:
        if code.casefold() not in questionnaire:
            raise ValueError(f"Official 2018 questionnaire does not contain reviewed field {code}")
        if not any(line.casefold().startswith(code.casefold() + ":") for line in codebook.splitlines()):
            raise ValueError(f"Official 2018 Codebook heading not found for {code}")
    unit_checks = {
        "i000_w4_11": "square metres",
        "i000_w4_12": "square meters",
        "i000_w4_13": "yuan/month",
        "i000_w4_14": "yuan/month",
        "i000_w4_15_1": "10,000 yuan",
        "i000_w4_15_2": "1,000 yuan/square meter",
        "i000_w4_16": "year",
        "i000_w4_17": "10,000 yuan",
    }
    for code, unit_phrase in unit_checks.items():
        starts = [match.start() for match in re.finditer(re.escape(code.casefold()), questionnaire)]
        # Require the unit near an occurrence of the exact field; this avoids
        # a prior route mention being mistaken for the question definition.
        if not any(unit_phrase in questionnaire[start:start + 900] for start in starts):
            raise ValueError(f"Official questionnaire unit text not found near {code}: {unit_phrase}")


def main() -> None:
    validate_official_sources()
    mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    selected = mapping.loc[mapping["wave"].eq(WAVE) & mapping["code"].str.lower().isin(SHARE_CODES)]
    if set(selected["code"].str.lower()) != SHARE_CODES or not selected["unit"].eq(UNIT).all():
        raise ValueError("Housing crosswalk does not contain the reviewed percent unit for exactly the five ownership-share fields")
    measure_rows = mapping.loc[mapping["wave"].eq(WAVE) & mapping["code"].str.lower().isin(set(MEASURES))]
    expected_mapped = set(MEASURES) - {"i000_w4_11", "i000_w4_12"}
    if set(measure_rows["code"].str.lower()) != expected_mapped:
        raise ValueError(f"Housing mapping does not contain the six reviewed numeric housing fields: {sorted(set(measure_rows['code'].str.lower()))}")
    for row in measure_rows.itertuples(index=False):
        if row.unit != MEASURES[str(row.code).lower()]["unit"]:
            raise ValueError(f"Unit mismatch in housing mapping for {row.code}: {row.unit}")
    results = [
        update_field_catalog_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv"),
        update_field_catalog_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json"),
        update_field_catalog_json(ROOT / "site-prototype/dist/catalog.json"),
        update_field_catalog_json(ROOT / "site-prototype/dist/catalog_e.json"),
        update_housing_json(ROOT / "site-prototype/dist/housing_catalog_v1.json"),
    ]
    applied = [count for count in results if count is not None]
    if any(count < len(REVIEW_CODES) for count in applied):
        raise ValueError(f"One or more field-level outputs are missing reviewed fields: {results}")
    print(f"Applied audited Wave 4 housing measurement metadata to {sum(applied)} field rows across {len(REVIEW_CODES)} variables; no values or frequencies included.")


if __name__ == "__main__":
    main()
