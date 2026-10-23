"""Apply reviewed Wave 5 digital-behavior and life-expectancy metadata.

Uses public CHARLS questionnaire and Codebook metadata only. No respondent
records or Codebook frequency tables are used or published.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE = "2020"
DIGITAL_CODES = {
    "da040", "da041_s1", "da041_s2", "da041_s3", "da041_s4", "da041_s5",
    "da042_s1", "da042_s2", "da042_s3", "da042_s4", "da042_s5", "da042_s6",
    "da043", "da044", "da045",
}
BEHAVIOR_MAP = ROOT / "audit/behavior_exposure_variable_mapping_v1.csv"
HEALTH_MAP = ROOT / "audit/health_symptom_variable_mapping_v1.csv"


def read_mapping(path: Path) -> dict[str, dict[str, str]]:
    frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    return {row["code"].lower(): row for row in frame.to_dict(orient="records") if row.get("wave") == WAVE}


def update_rows(rows: list[dict]) -> tuple[list[dict], int, int]:
    behavior = read_mapping(BEHAVIOR_MAP)
    health = read_mapping(HEALTH_MAP)
    reviewed = 0
    removed = 0
    kept = []
    for row in rows:
        code = str(row.get("Variable.Name", "")).lower()
        wave = str(row.get("Source.Wave", row.get("Begin.Year", "")))
        role = str(row.get("epcf", "")).lower()
        if wave == WAVE and code == "da042_s5" and role == "c":
            # This exact field is a routed DA042 internet activity, now mapped
            # as E. Remove only the auto-keyword C duplicate.
            removed += 1
            continue
        mapping = behavior.get(code) if wave == WAVE and role == "e" and code in DIGITAL_CODES else None
        if mapping:
            note = mapping.get("note", "")
            labels = mapping.get("value_labels", "")
            source = mapping.get("value_label_source", "")
            review = "2020 official questionnaire and Codebook wording/response categories reviewed; frequencies excluded; routed missingness retained"
            row.update({
                "category": "behavior",
                "subcategory": "internet and digital technology use",
                "Value.Labels": labels,
                "value_labels": labels,
                "Value.Label.Source": source,
                "value_label_source": source,
                "Value.Label.Review": review,
                "value_label_review": review,
                "Harmonization.Status": note,
                "harmonization_status": note,
                "Review.Flag": "E candidate; source wording and route reviewed; not an approved causal exposure or analysis variable",
            })
            reviewed += 1
        elif wave == WAVE and code == "da029" and code in health and role == "p":
            mapping = health[code]
            note = mapping.get("note", "")
            labels = mapping.get("value_labels", "")
            source = mapping.get("value_label_source", "")
            review = "2020 official questionnaire and Codebook ordinal categories reviewed; frequencies excluded; interpretation depends on the respondent-specific target age"
            row.update({
                "Value.Labels": labels,
                "value_labels": labels,
                "Value.Label.Source": source,
                "value_label_source": source,
                "Value.Label.Review": review,
                "value_label_review": review,
                "Harmonization.Status": note,
                "harmonization_status": note,
                "Review.Flag": "P candidate; subjective expectation with age-specific target; not observed survival or a clinical endpoint",
            })
            reviewed += 1
        kept.append(row)
    return kept, reviewed, removed


def main() -> None:
    for path in (BEHAVIOR_MAP, HEALTH_MAP,
                 ROOT / "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
                 ROOT / "sources_official/CHARLS_2020_Codebook_extracted.txt"):
        if not path.exists():
            raise SystemExit(f"Missing source: {path.relative_to(ROOT)}")
    targets = [ROOT / "audit/charls_atlas_candidate_fields_v0.csv",
               ROOT / "audit/charls_atlas_candidate_fields_v0.json"]
    total_reviewed = total_removed = 0
    for path in targets:
        if path.suffix == ".json":
            rows = json.loads(path.read_text(encoding="utf-8"))
            rows, reviewed, removed = update_rows(rows)
            path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        else:
            frame = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            rows, reviewed, removed = update_rows(frame.to_dict(orient="records"))
            pd.DataFrame(rows, columns=frame.columns).to_csv(path, index=False, encoding="utf-8-sig")
        print(f"{path.relative_to(ROOT)}: reviewed {reviewed}; removed exact E/C duplicate {removed}")
        total_reviewed += reviewed
        total_removed += removed
    if total_reviewed < 16 or total_removed < 1:
        raise SystemExit(f"Expected 15 E fields plus 1 P field and one C duplicate; got reviewed={total_reviewed}, removed={total_removed}")
    print("Wave 5 digital/subjective-expectancy metadata applied; no respondent values or frequencies used.")


if __name__ == "__main__":
    main()
