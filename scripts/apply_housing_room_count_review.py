"""Apply official-source measurement metadata for household room/toilet counts."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE_FIELDS = {
    "2011": {"i012_1": "bedroom", "i012_2": "living-room", "i012_3": "toilet"},
    "2013": {"i012_1": "bedroom", "i012_2": "living-room", "i012_3": "toilet"},
    "2015": {"i012_1": "bedroom", "i012_2": "living-room", "i012_3": "toilet"},
    "2018": {"i012_1": "bedroom", "i012_2": "living-room", "i012_3": "toilet"},
    "2020": {"i011_1": "bedroom", "i011_2": "living-room", "i011_3": "toilet"},
}
SOURCE = "; ".join(f"sources_official/CHARLS_{wave}_{suffix}_extracted.txt" for wave, suffix in [
    ("2011", "Baseline_Household_Questionnaire"), ("2013", "Questionnaire"),
    ("2015", "Questionnaire"), ("2018", "Questionnaire"),
]) + "; sources_official/CHARLS_2020_Questionnaire_English_extracted.txt; wave-specific CHARLS Codebook extracts"


def metadata(wave: str, code: str, measure: str) -> tuple[str, str, str]:
    label = {"bedroom": "bedroom", "living-room": "living-room", "toilet": "toilet"}[measure]
    subject = "the Household Financial Respondent's house" if wave == "2020" else "the respondent household's residence"
    soft_check = "The questionnaire has a soft check above 20; this is not a validated exclusion threshold." if wave != "2020" else "The questionnaire specifies a nonnegative integer response and a soft check above 20; this is not a validated exclusion threshold."
    review = f"official {wave} questionnaire and Codebook identify a numeric {label} count; no discrete labels; Codebook extrema are not valid-range evidence; verify release-specific special values"
    harmonization = (f"{wave} {label} count for {subject}; household/residence-level measure, not an individual dose. {soft_check} "
                     "Retain wave-specific field and residence wording; do not assume cross-wave equivalence or form a crowding score without a prespecified household-composition denominator. "
                     "Confirm special values, eligible sample, missingness, and linkage in authorized-release QA before analysis.")
    return "count", review, harmonization


def update(row: dict, wave: str, code: str) -> None:
    measure = WAVE_FIELDS[wave][code.lower()]
    unit, review, harmonization = metadata(wave, code, measure)
    row["Concept.Unit.Candidates"] = unit
    row["Value.Labels"] = ""
    row["Value.Label.Review"] = review
    row["Value.Label.Source"] = SOURCE
    row["Harmonization.Status"] = harmonization
    for key, val in [("candidate_concept_units", unit), ("value_labels", ""), ("value_label_review", review),
                     ("value_label_source", SOURCE), ("harmonization_status", harmonization)]:
        if key in row or key != "candidate_concept_units":
            row[key] = val


def validate_sources() -> None:
    suffixes = {"2011": "Baseline_Household_Questionnaire", "2013": "Questionnaire", "2015": "Questionnaire", "2018": "Questionnaire", "2020": "Questionnaire_English"}
    for wave, fields in WAVE_FIELDS.items():
        questionnaire = ROOT / f"sources_official/CHARLS_{wave}_{suffixes[wave]}_extracted.txt"
        codebook = ROOT / f"sources_official/CHARLS_{wave}_Codebook_extracted.txt"
        qtext = questionnaire.read_text(encoding="utf-8", errors="ignore").casefold()
        ctext = codebook.read_text(encoding="utf-8", errors="ignore").casefold()
        for code in fields:
            if re.sub(r"[^a-z0-9]", "", code.casefold()) not in re.sub(r"[^a-z0-9]", "", qtext):
                raise ValueError(f"Questionnaire source lacks {wave} {code}")
            if re.sub(r"[^a-z0-9]", "", code.casefold()) not in re.sub(r"[^a-z0-9]", "", ctext):
                raise ValueError(f"Codebook source lacks {wave} {code}")
        if wave == "2020" and "financialresp" not in qtext:
            raise ValueError("2020 questionnaire source lacks the Household Financial Respondent reference")


def update_csv(path: Path, wave_col: str, code_col: str) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: str(r[wave_col]) in WAVE_FIELDS and str(r[code_col]).lower() in WAVE_FIELDS[str(r[wave_col])], axis=1)
    found = {(str(r[wave_col]), str(r[code_col]).lower()) for _, r in df[selected].iterrows()}
    expected = {(w, c) for w, fields in WAVE_FIELDS.items() for c in fields}
    if not expected.issubset(found):
        raise ValueError(f"{path}: missing expected reviewed fields: {sorted(expected-found)}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        update(row, str(row[wave_col]), str(row[code_col]))
        for key in ["Concept.Unit.Candidates", "Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status"]:
            if key in df.columns:
                df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_food_crosswalk_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: str(r["wave"]) in WAVE_FIELDS and str(r["code"]).lower() in WAVE_FIELDS[str(r["wave"])], axis=1)
    found = {(str(r["wave"]), str(r["code"]).lower()) for _, r in df[selected].iterrows()}
    expected = {(w, c) for w, fields in WAVE_FIELDS.items() for c in fields}
    if not expected.issubset(found):
        raise ValueError(f"{path}: missing expected reviewed fields: {sorted(expected-found)}")
    for idx in df.index[selected]:
        wave, code = str(df.at[idx, "wave"]), str(df.at[idx, "code"]).lower()
        measure = WAVE_FIELDS[wave][code]
        _, review, harmonization = metadata(wave, code, measure)
        df.at[idx, "mapping_status"] = f"official {wave} questionnaire and Codebook confirm numeric count; special values and sample eligibility require authorized-release QA"
        df.at[idx, "caveat"] = harmonization
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and wave_key == "wave" and isinstance(rows[0].get("source_fields"), list):
        selected = [
            field for concept in rows for field in concept.get("source_fields", [])
            if str(field.get(wave_key, "")) in WAVE_FIELDS
            and str(field.get(code_key, "")).lower() in WAVE_FIELDS.get(str(field.get(wave_key, "")), {})
        ]
        found = {(str(field[wave_key]), str(field[code_key]).lower()) for field in selected}
        expected = {(w, c) for w, fields in WAVE_FIELDS.items() for c in fields}
        if not expected.issubset(found):
            raise ValueError(f"{path}: missing expected reviewed fields: {sorted(expected-found)}")
        for field in selected:
            wave, code = str(field[wave_key]), str(field[code_key]).lower()
            measure = WAVE_FIELDS[wave][code]
            _, review, harmonization = metadata(wave, code, measure)
            field["unit"] = "count"
            field["mapping_status"] = f"official {wave} questionnaire and Codebook confirm numeric count; special values and sample eligibility require authorized-release QA"
            field["note"] = field["mapping_status"]
            field["caveat"] = harmonization
            field["value_label_status"] = review
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(selected)
    if not rows or wave_key not in rows[0]:
        return 0
    selected = [r for r in rows if str(r.get(wave_key, "")) in WAVE_FIELDS and str(r.get(code_key, "")).lower() in WAVE_FIELDS.get(str(r.get(wave_key, "")), {})]
    found = {(str(r[wave_key]), str(r[code_key]).lower()) for r in selected}
    expected = {(w, c) for w, fields in WAVE_FIELDS.items() for c in fields}
    if not expected.issubset(found):
        raise ValueError(f"{path}: missing expected reviewed fields: {sorted(expected-found)}")
    for row in selected:
        update(row, str(row[wave_key]), str(row[code_key]))
        if wave_key == "wave":
            wave, code = str(row[wave_key]), str(row[code_key]).lower()
            _, review, harmonization = metadata(wave, code, WAVE_FIELDS[wave][code])
            row["unit"] = "count"
            row["mapping_status"] = f"official {wave} questionnaire and Codebook confirm numeric count; special values and sample eligibility require authorized-release QA"
            row["caveat"] = harmonization
            row["value_label_status"] = review
            if "note" in row:
                row["note"] = row["mapping_status"]
    pretty_json = wave_key == "wave" and path.name != "housing_catalog_v1.json"
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if pretty_json else json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    return len(selected)


def main() -> None:
    validate_sources()
    outputs = [
        update_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv", "Source.Wave", "Variable.Name"),
        update_food_crosswalk_csv(ROOT / "audit/food_environment_crosswalk_v1.csv"),
        update_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/catalog.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/catalog_e.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/food_environment_v1.json", "wave", "code"),
        update_json(ROOT / "site-prototype/dist/housing_catalog_v1.json", "wave", "code"),
    ]
    print(f"Applied official numeric count metadata to {sum(outputs)} field rows; no participant values or frequencies included.")


if __name__ == "__main__":
    main()
