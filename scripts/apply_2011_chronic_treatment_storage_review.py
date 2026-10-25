"""Propagate the local aggregate-only 2011 DA010 storage review to metadata."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISEASES = ("2", "5", "6", "7", "9", "10", "12", "13")
OPTIONS = ("1", "2", "3", "4")
EXPECTED = {f"da010_{disease}_s{option}" for disease in DISEASES for option in OPTIONS}
MAPPING = ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv"
SOURCE_INDEX = ROOT / "audit/ep_concept_source_crosswalk_v1.csv"
CANDIDATE_FIELDS = ROOT / "audit/charls_atlas_candidate_fields_v0.csv"
SITE_CATALOG = ROOT / "site-prototype/dist/catalog.json"
QUESTIONNAIRE = ROOT / "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"
CODEBOOK = ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt"

STATUS = (
    "official 2011 Codebook selected-option category transcribed; local aggregate-only QA "
    "corroborates selected code; unselected storage and blank semantics, plus routed denominator, unresolved; DO NOT ANALYZE"
)
MAPPING_STATUS = (
    "official 2011 Codebook item/option identity and selected code corroborated by local aggregate-only QA; "
    "response/route denominator unresolved; DO NOT ANALYZE"
)
HARMONIZATION = (
    "Selected response code matches the official Codebook option index in local aggregate-only QA; "
    "preserve disease item, wave, response slot, and route; cross-wave harmonization not approved"
)
NOTE = (
    "Local aggregate-only QA checks nonmissing response codes against the official Codebook option index. "
    "It does not establish whether blank means unselected or skipped, define the routed denominator, "
    "or approve analysis. Do not infer No from an empty slot."
)
LEGACY_NOTE = (
    "Local aggregate-only QA checks nonmissing response codes against the official Codebook option index. "
    "It does not establish whether blank means unselected or skipped, define the routed denominator, "
    "or approve analysis. Do not infer No from an empty slot; DO NOT ANALYZE."
)


def is_target(wave: object, code: object) -> bool:
    return str(wave) == "2011" and str(code).strip().lower() in EXPECTED


def validate_sources() -> None:
    questionnaire = QUESTIONNAIRE.read_text(encoding="utf-8", errors="replace").casefold()
    codebook = CODEBOOK.read_text(encoding="utf-8", errors="replace").casefold()
    for anchor in ("da010. are you now taking", "check all that apply", "none of the above"):
        if anchor not in questionnaire:
            raise ValueError(f"Official 2011 baseline questionnaire is missing DA010 anchor: {anchor}")
    for disease in DISEASES:
        for option in OPTIONS:
            code = f"da010 {disease} s{option}"
            if code not in codebook:
                raise ValueError(f"Official 2011 Codebook is missing reviewed field {code}")


def update_csv(path: Path, wave_column: str, code_column: str, updates: dict[str, str]) -> int:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = list(reader.fieldnames or []), list(reader)
    matches = [row for row in rows if is_target(row.get(wave_column), row.get(code_column))]
    observed = {str(row.get(code_column, "")).strip().lower() for row in matches}
    if observed != EXPECTED:
        raise ValueError(f"{path.name}: expected exactly 32 reviewed fields, found {len(observed)}")
    for row in matches:
        for key, value in updates.items():
            if key.casefold() == "caveat":
                existing = str(row.get(key, "")).strip()
                existing = existing.replace(LEGACY_NOTE, "").strip(" ;")
                if NOTE not in existing:
                    row[key] = f"{existing}; {NOTE}" if existing else NOTE
            elif key.casefold() == "review.flag":
                existing = str(row.get(key, "")).strip()
                row[key] = existing.replace(LEGACY_NOTE, "").replace(NOTE, "").strip(" ;")
            else:
                row[key] = value
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(matches)


def update_site_catalog(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    matches = [row for row in rows if is_target(row.get("Source.Wave"), row.get("Variable.Name"))]
    observed = {str(row.get("Variable.Name", "")).strip().lower() for row in matches}
    if observed != EXPECTED:
        raise ValueError(f"{path.name}: expected exactly 32 reviewed site rows, found {len(observed)}")
    for row in matches:
        apply_site_row(row)
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(matches)


def apply_site_row(row: dict[str, str]) -> None:
    if "Review.Flag" in row:
        row["Review.Flag"] = str(row.get("Review.Flag", "")).replace(LEGACY_NOTE, "").replace(NOTE, "").strip(" ;")
    row["Harmonization.Status"] = HARMONIZATION
    row["Value.Label.Review"] = STATUS
    row["Concept.Mapping.Status"] = MAPPING_STATUS
    for key in ("Concept.Mapping.Caveat",):
        existing = str(row.get(key, "")).strip()
        existing = existing.replace(LEGACY_NOTE, "").strip(" ;")
        if NOTE not in existing:
            row[key] = f"{existing}; {NOTE}" if existing else NOTE


def main() -> None:
    validate_sources()
    counts = {
        "ancillary_mapping": update_csv(
            MAPPING, "wave", "code",
            {"mapping_status": MAPPING_STATUS, "value_label_status": STATUS, "caveat": NOTE},
        ),
        "concept_source_index": update_csv(
            SOURCE_INDEX, "Wave", "Source.Code",
            {"Mapping.Status": MAPPING_STATUS, "Caveat": NOTE},
        ),
        "candidate_field_catalog": update_csv(
            CANDIDATE_FIELDS, "Source.Wave", "Variable.Name",
            {"Harmonization.Status": HARMONIZATION, "Value.Label.Review": STATUS,
             "Concept.Mapping.Status": MAPPING_STATUS,
             "Concept.Mapping.Caveat": NOTE, "Review.Flag": ""},
        ),
        "site_catalog": update_site_catalog(SITE_CATALOG),
    }
    if set(counts.values()) != {32}:
        raise ValueError(f"Unexpected reviewed-field synchronization counts: {counts}")
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
