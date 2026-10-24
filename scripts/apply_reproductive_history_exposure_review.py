"""Promote source-verified reproductive timing components to E candidates."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAPPING = AUDIT / "reproductive_history_exposure_crosswalk_v1.csv"
FIELD_CSV = AUDIT / "charls_atlas_candidate_fields_v0.csv"
FIELD_COLUMNS = [
    "Variable.Name", "Variable.Description", "Data.File.Name", "Data.File.Description",
    "Begin.Year", "EndYear", "Component", "Use.Constraints", "epcf", "category",
    "subcategory", "Source.Wave", "Source.Archive", "Candidate.Status",
    "Harmonization.Status", "Review.Flag", "Value.Labels", "Value.Label.Source",
    "Value.Label.Review", "Concept.Unit.Candidates", "Unit", "Concept.ID.Candidates",
    "Concept.Alias.IDs", "Concept.Label.Candidates", "Concept.Mapping.Source",
    "Concept.Mapping.Status", "Concept.Mapping.Caveat", "Concept.Mapping.Collision",
    "Concept.Mapping.Relationship",
]
JSON_ALIAS_FIELDS = (
    "candidate_concept_ids", "candidate_concept_labels", "candidate_concept_units",
    "concept_mapping_sources", "concept_mapping_statuses", "concept_mapping_caveats",
    "concept_mapping_collision", "concept_mapping_relationship", "Source.Review.Files",
    "value_labels", "value_label_source", "value_label_review", "harmonization_status",
)

LABELS = {
    "age_at_menarche": "初潮年龄",
    "age_at_menopause": "绝经年龄",
}
SOURCE_FILES = {
    "2011": ("CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "CHARLS_2011_Codebook_extracted.txt"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", "CHARLS_2013_Codebook_extracted.txt"),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt", "CHARLS_2015_Codebook_extracted.txt"),
    "2018": ("CHARLS_2018_Questionnaire_extracted.txt", "CHARLS_2018_Codebook_extracted.txt"),
}


def load_mapping() -> pd.DataFrame:
    mapping = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    expected = {
        (wave, code)
        for wave in SOURCE_FILES
        for code in ("da026_2", "da028_2")
    }
    actual = {(str(r.wave), str(r.code).lower()) for r in mapping.itertuples(index=False)}
    if actual != expected or len(mapping) != len(expected):
        raise SystemExit(f"unexpected reproductive-history mapping set: {sorted(actual)}")
    return mapping


def reviewed_values(row: dict[str, str]) -> dict[str, str]:
    concept = row["concept_id"]
    label = row["concept_label"]
    wave = row["wave"]
    code = row["code"].lower()
    files = SOURCE_FILES[wave]
    source = "; ".join(f"sources_official/{name}" for name in files)
    caveat = row["caveat"]
    status = row["mapping_status"]
    return {
        "epcf": "e",
        "category": "life-course and reproductive history",
        "subcategory": "reproductive timing",
        "Candidate.Status": "Source-reviewed life-course exposure candidate; female-only routed age component; not a covariate or adjustment recommendation",
        "Harmonization.Status": "Wave-specific recalled age component in years; *_1 calendar-year component remains separate and is never converted; route and age/year choice restrict the observed denominator; cross-wave comparability and analysis eligibility are not approved",
        "Review.Flag": "Candidate E only; female and wave-specific route. For age at menopause retain the DA027 yes-branch; preserve the age/year component and special responses; never infer values from skips or report association results",
        "Concept.ID.Candidates": concept,
        "Concept.Label.Candidates": label,
        "Concept.Unit.Candidates": "years",
        "Concept.Mapping.Source": "audit/reproductive_history_exposure_crosswalk_v1.csv",
        "Concept.Mapping.Status": status,
        "Concept.Mapping.Caveat": caveat,
        "Concept.Mapping.Collision": "",
        "Concept.Mapping.Relationship": "",
        "Value.Labels": "",
        "Value.Label.Source": source,
        "Value.Label.Review": "Official questionnaire and Codebook identify the age-response component and unit; no response frequencies copied",
        "value_labels": "",
        "value_label_source": source,
        "value_label_review": "Official questionnaire and Codebook identify the age-response component and unit; no response frequencies copied",
        "harmonization_status": "Wave-specific recalled age component in years; *_1 calendar-year component remains separate and is never converted; route and age/year choice restrict the observed denominator; cross-wave comparability and analysis eligibility are not approved",
    }


def transform_records(records: list[dict[str, str]], mapping: pd.DataFrame) -> list[dict[str, str]]:
    targets = {(str(r.wave), str(r.code).lower()): r._asdict() for r in mapping.itertuples(index=False)}
    seen: set[tuple[str, str]] = set()
    for item in records:
        key = (str(item.get("Source.Wave", "")), str(item.get("Variable.Name", "")).lower())
        if key not in targets:
            continue
        if key in seen:
            raise SystemExit(f"duplicate source field row: {key}")
        seen.add(key)
        if str(item.get("epcf", "")).lower() not in {"c", "e"}:
            raise SystemExit(f"unexpected source role for {key}: {item.get('epcf')}")
        row = targets[key]
        if str(item.get("epcf", "")).lower() == "e" and str(item.get("Concept.ID.Candidates", "")) not in {"", row["concept_id"]}:
            raise SystemExit(f"conflicting exposure concept for {key}")
        values = reviewed_values(row)
        for field, value in values.items():
            item[field] = value
        item["category"] = values["category"]
        item["subcategory"] = values["subcategory"]
    if seen != set(targets):
        raise SystemExit(f"missing reproductive source rows: {sorted(set(targets) - seen)}")
    return records


def update_csv(path: Path, mapping: pd.DataFrame) -> int:
    data = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    records = transform_records(data.to_dict(orient="records"), mapping)
    result = pd.DataFrame(records).reindex(columns=FIELD_COLUMNS)
    result.to_csv(path, index=False, encoding="utf-8-sig")
    return len(mapping)


def update_json(path: Path, mapping: pd.DataFrame, *, strip_aliases: bool = False) -> int:
    records = json.loads(path.read_text(encoding="utf-8"))
    records = transform_records(records, mapping)
    fields_to_strip = JSON_ALIAS_FIELDS if strip_aliases else ("Source.Review.Files",)
    for record in records:
        for field in fields_to_strip:
            record.pop(field, None)
    path.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(mapping)


def main() -> None:
    mapping = load_mapping()
    count = 0
    for path, strip_aliases in (
        (FIELD_CSV, False),
        (AUDIT / "charls_atlas_candidate_fields_v0.json", True),
        (ROOT / "site-prototype/dist/catalog.json", False),
        (ROOT / "site-prototype/dist/catalog_e.json", False),
    ):
        if path.suffix == ".csv":
            count += update_csv(path, mapping)
        else:
            count += update_json(path, mapping, strip_aliases=strip_aliases)
    print(f"Reviewed {count} wave-field reproductive timing exposure candidates; no respondent data used.")


if __name__ == "__main__":
    main()
