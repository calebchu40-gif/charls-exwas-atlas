"""Apply questionnaire-backed housing area and timing metadata to public catalogs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    ("2011", "i001"): ("square metres", "2011 construction area of the respondent's residence; main-respondent housing module. Questionnaire soft-checks values below 10 or above 500; this is not a validated exclusion range."),
    ("2013", "i001"): ("square metres", "2013 construction area of the respondent's residence; main-respondent housing module. Questionnaire soft-checks values below 10 or above 500; this is not a validated exclusion range."),
    ("2020", "i028"): ("square metres", "2020 size of the Household Financial Respondent's house. Questionnaire permits positive real values and applies a soft check for values outside 10–500; this is not a validated exclusion range."),
    ("2011", "i005"): ("calendar year", "2011 year the current house was built; if unclear, the questionnaire offers the separate interval field i005_1. Preserve exact year and interval response separately."),
    ("2013", "i005"): ("calendar year", "2013 exact year the current house was built; if unclear, the questionnaire offers the separate interval field i005_1. Preserve exact year and interval response separately."),
    ("2015", "i005"): ("calendar year", "2015 year the current house was built; if unclear, the questionnaire offers the separate interval field i005_1. Preserve exact year and interval response separately."),
    ("2018", "i005"): ("calendar year", "2018 year the currently occupied house was built; if unclear, the questionnaire offers the separate interval field i005_1. Preserve exact year and interval response separately."),
    ("2020", "i002"): ("calendar year", "2020 year the Household Financial Respondent moved into current housing, not the building construction year. The questionnaire specifies 1900–2020 and instructs interviewers to enter -1 when the respondent cannot answer; validate release-specific storage and special values before analysis."),
}
SOURCE = "; ".join([
    "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2013_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
    "wave-specific CHARLS Codebook extracts",
])


def review_status(wave: str, code: str, unit: str) -> str:
    if wave == "2020" and code.lower() == "i002":
        return "official 2020 questionnaire identifies respondent move-in calendar year; no discrete labels; questionnaire -1 unknown code requires authorized-release validation"
    return f"official {wave} questionnaire identifies continuous numeric {unit} measure; no discrete labels; Codebook extrema are not valid-range evidence; verify release special values and eligibility"


def update(row: dict, wave: str, code: str) -> None:
    unit, note = FIELDS[(wave, code.lower())]
    status = review_status(wave, code, unit)
    row["Concept.Unit.Candidates"] = unit
    row["Value.Labels"] = ""
    row["Value.Label.Review"] = status
    row["Value.Label.Source"] = SOURCE
    row["Harmonization.Status"] = note + " Do not infer eligible sample or valid range from Codebook summaries; verify authorized release metadata before modeling."
    row["candidate_concept_units"] = unit
    row["value_labels"] = ""
    row["value_label_review"] = status
    row["value_label_source"] = SOURCE
    row["harmonization_status"] = row["Harmonization.Status"]


def patch_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and wave_key == "wave" and isinstance(rows[0].get("source_fields"), list):
        selected = [
            field for concept in rows for field in concept.get("source_fields", [])
            if (str(field.get(wave_key, "")), str(field.get(code_key, "")).lower()) in FIELDS
        ]
        seen = {(str(field[wave_key]), str(field[code_key]).lower()) for field in selected}
        if not set(FIELDS).issubset(seen):
            raise ValueError(f"{path}: missing reviewed housing fields {sorted(set(FIELDS)-seen)}")
        for field in selected:
            wave, code = str(field[wave_key]), str(field[code_key]).lower()
            unit, note = FIELDS[(wave, code)]
            status = "official questionnaire unit/measurement identity reviewed; special values and sample eligibility require authorized-release QA"
            if (wave, code) == ("2020", "i002"):
                status += "; see audit/housing_context_source_review_2026-10-24.md"
            field["unit"] = unit
            field["mapping_status"] = status
            if (wave, code) != ("2020", "i002") or not field.get("note"):
                field["note"] = status
            field["caveat"] = note + " Do not infer eligible sample or valid range from Codebook summaries; verify authorized release metadata before modeling."
            field["value_label_status"] = review_status(wave, code, unit)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(selected)
    if not rows or wave_key not in rows[0]:
        return 0
    selected = [r for r in rows if (str(r.get(wave_key, "")), str(r.get(code_key, "")).lower()) in FIELDS]
    seen = {(str(r[wave_key]), str(r[code_key]).lower()) for r in selected}
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing reviewed housing fields {sorted(set(FIELDS)-seen)}")
    for row in selected:
        wave, code = str(row[wave_key]), str(row[code_key]).lower()
        update(row, wave, code)
        if wave_key == "wave":
            row["unit"] = FIELDS[(wave, code)][0]
            row["mapping_status"] = "official questionnaire unit/measurement identity reviewed; special values and sample eligibility require authorized-release QA"
            if (wave, code) == ("2020", "i002"):
                row["mapping_status"] += "; see audit/housing_context_source_review_2026-10-24.md"
            if "note" in row and (wave, code) != ("2020", "i002"):
                row["note"] = row["mapping_status"]
            row["caveat"] = FIELDS[(wave, code)][1]
            row["value_label_status"] = review_status(wave, code, FIELDS[(wave, code)][0])
    pretty_json = wave_key == "wave" and path.name != "housing_catalog_v1.json"
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if pretty_json else json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(text, encoding="utf-8")
    return len(selected)


def patch_csv(path: Path) -> int:
    import pandas as pd
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, "Source.Wave"], df.loc[selected, "Variable.Name"].str.lower()))
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing reviewed housing fields {sorted(set(FIELDS)-seen)}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        update(row, str(row["Source.Wave"]), str(row["Variable.Name"]).lower())
        for key in ("Concept.Unit.Candidates", "Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status"):
            if key in df.columns:
                df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def patch_food_crosswalk_csv(path: Path) -> int:
    import pandas as pd
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["wave"]), str(r["code"]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, "wave"], df.loc[selected, "code"].str.lower()))
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing reviewed housing fields {sorted(set(FIELDS)-seen)}")
    for idx in df.index[selected]:
        wave, code = str(df.at[idx, "wave"]), str(df.at[idx, "code"]).lower()
        unit, note = FIELDS[(wave, code)]
        df.at[idx, "mapping_status"] = review_status(wave, code, unit)
        if (wave, code) == ("2020", "i002"):
            df.at[idx, "mapping_status"] += "; see audit/housing_context_source_review_2026-10-24.md"
        df.at[idx, "caveat"] = note + " Do not infer eligible sample or valid range from Codebook summaries; verify authorized release metadata before modeling."
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def validate_sources() -> None:
    source_paths = list((ROOT / "sources_official").glob("CHARLS_*Questionnaire*extracted.txt"))
    texts = {p.name: p.read_text(encoding="utf-8", errors="ignore").casefold() for p in source_paths}
    expected = {
        "2011": ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "construction area", "m2"),
        "2013": ("CHARLS_2013_Questionnaire_extracted.txt", "construction area", "m2"),
        "2020": ("CHARLS_2020_Questionnaire_English_extracted.txt", "square meter", "move into this housing"),
    }
    for wave, (filename, *phrases) in expected.items():
        text = texts[filename]
        for phrase in phrases:
            if phrase.casefold() not in text:
                raise ValueError(f"Official {wave} questionnaire evidence missing: {phrase}")
    for wave in ("2011", "2013", "2015", "2018"):
        source_name = "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt" if wave == "2011" else f"CHARLS_{wave}_Questionnaire_extracted.txt"
        if "when was this house built" not in texts[source_name]:
            raise ValueError(f"Official {wave} questionnaire lacks construction-year wording")


def main() -> None:
    validate_sources()
    counts = [
        patch_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv"),
        patch_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json", "Source.Wave", "Variable.Name"),
        patch_json(ROOT / "site-prototype/dist/catalog.json", "Source.Wave", "Variable.Name"),
        patch_json(ROOT / "site-prototype/dist/catalog_e.json", "Source.Wave", "Variable.Name"),
        patch_food_crosswalk_csv(ROOT / "audit/food_environment_crosswalk_v1.csv"),
        patch_json(ROOT / "site-prototype/dist/food_environment_v1.json", "wave", "code"),
    ]
    print(f"Applied area/year measurement review to {sum(counts)} metadata rows; no participant values or frequencies included.")


if __name__ == "__main__":
    main()
