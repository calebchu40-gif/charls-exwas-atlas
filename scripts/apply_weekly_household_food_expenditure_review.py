"""Apply questionnaire-backed weekly household food-spending metadata."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    ("2011", "ge006"): "2011 past-week household food consumption amount; questionnaire explicitly includes purchased and own-produced food consumed and excludes eating out, alcohol and tobacco.",
    ("2013", "ge006"): "2013 past-week household food spending; own-produced food market value is captured in a separate conditional field. Do not assume it is included in cash expenditure.",
    ("2015", "ge006"): "2015 past-week household food spending; own-produced food market value is captured in a separate conditional field. Do not assume it is included in cash expenditure.",
    ("2018", "ge006_w4"): "2018 past-week household food spending; excludes eating out, alcohol, tobacco and banquet/wedding spending. Own-produced food value is separate.",
    ("2020", "gf006"): "2020 past-week household food spending; excludes banquets/weddings, eating out, alcohol and tobacco. Own-produced food value is separate.",
    ("2011", "ge007"): "2011 past-week household eating-out spending; retain its questionnaire scope and do not assume banquet/wedding exclusions.",
    ("2013", "ge007"): "2013 past-week household eating-out spending; retain its questionnaire scope and do not assume banquet/wedding exclusions.",
    ("2015", "ge007"): "2015 past-week household eating-out spending; retain its questionnaire scope and do not assume banquet/wedding exclusions.",
    ("2018", "ge007_w4"): "2018 past-week household eating-out spending; questionnaire explicitly excludes banquets/weddings.",
    ("2020", "gf009"): "2020 past-week household members' eating-out spending; questionnaire explicitly excludes banquets/weddings.",
}
SOURCE = "; ".join([
    "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2013_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2015_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2018_Questionnaire_extracted.txt",
    "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt",
])
SOURCE_FIELD = {
    "2011": "CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}


def apply(row: dict, wave: str, code: str) -> None:
    note = FIELDS[(wave, code.lower())]
    status = f"official {wave} questionnaire identifies a past-week household Yuan amount; continuous measure with no discrete labels; check release-specific special values"
    caveat = note + " Household aggregate is not individual dietary intake or nutrient exposure. Wave definitions and own-production treatment differ; do not assume cross-wave equivalence. Questionnaire soft checks are prompts, not validated exclusions. Verify eligible sample, special values, missingness and household/respondent linkage in authorized-release QA before modeling."
    row.update({
        "Concept.Unit.Candidates": "Yuan/week", "Value.Labels": "", "Value.Label.Review": status,
        "Value.Label.Source": SOURCE, "Harmonization.Status": caveat,
        "candidate_concept_units": "Yuan/week", "value_labels": "", "value_label_review": status,
        "value_label_source": SOURCE, "harmonization_status": caveat,
    })


def validate_sources() -> None:
    for wave, code in FIELDS:
        path = ROOT / "sources_official" / SOURCE_FIELD[wave]
        text = path.read_text(encoding="utf-8", errors="ignore").casefold()
        if code.casefold() not in text:
            raise ValueError(f"Questionnaire source lacks {wave} {code}")
        if "past week" not in text and "past week" not in text.replace("\u2011", "-"):
            raise ValueError(f"Questionnaire source lacks weekly recall language for {wave} {code}")


def update_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, "Source.Wave"], df.loc[selected, "Variable.Name"].str.lower()))
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing fields {sorted(set(FIELDS)-seen)}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        apply(row, str(row["Source.Wave"]), str(row["Variable.Name"]).lower())
        for key in ("Concept.Unit.Candidates", "Value.Labels", "Value.Label.Review", "Value.Label.Source", "Harmonization.Status"):
            if key in df.columns:
                df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not rows or wave_key not in rows[0]:
        return 0
    selected = [r for r in rows if (str(r.get(wave_key, "")), str(r.get(code_key, "")).lower()) in FIELDS]
    seen = {(str(r[wave_key]), str(r[code_key]).lower()) for r in selected}
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing fields {sorted(set(FIELDS)-seen)}")
    for row in selected:
        wave, code = str(row[wave_key]), str(row[code_key]).lower()
        apply(row, wave, code)
        if wave_key == "wave":
            row["unit"] = "Yuan/week"
            row["mapping_status"] = "official questionnaire confirms weekly household Yuan amount; cross-wave construct comparability remains unapproved"
            row["caveat"] = FIELDS[(wave, code)] + " Not individual dietary intake; own-production treatment and exclusions vary by wave. Verify route, special values, missingness and household/respondent linkage before analysis."
            row["value_label_status"] = row["Value.Label.Review"]
    output = json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if wave_key == "wave" else json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(output, encoding="utf-8")
    return len(selected)


def update_domain_crosswalk(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(
        lambda r: (str(r["wave"]), str(r["code"]).lower()) in FIELDS,
        axis=1,
    )
    seen = set(zip(df.loc[selected, "wave"], df.loc[selected, "code"].str.lower()))
    if not set(FIELDS).issubset(seen):
        raise ValueError(f"{path}: missing reviewed food-spending mappings {sorted(set(FIELDS)-seen)}")
    for idx in df.index[selected]:
        wave = str(df.at[idx, "wave"])
        code = str(df.at[idx, "code"]).lower()
        df.at[idx, "mapping_status"] = (
            f"official {wave} questionnaire wording, past-week Yuan unit and household target reviewed; "
            "cross-wave construct comparability not approved; see "
            "audit/household_food_expenditure_measure_review_2026-10-23.md"
        )
        df.at[idx, "caveat"] = (
            FIELDS[(wave, code)] + " Household aggregate, not individual dietary intake or nutrient exposure. "
            "Own-production treatment and exclusions vary by wave; do not assume cross-wave equivalence. "
            "Questionnaire soft checks are prompts, not validated exclusions. Verify route, special values, "
            "missingness and household/respondent linkage before analysis."
        )
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def main() -> None:
    validate_sources()
    counts = [
        update_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv"),
        update_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/catalog.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/catalog_e.json", "Source.Wave", "Variable.Name"),
        update_json(ROOT / "site-prototype/dist/food_environment_v1.json", "wave", "code"),
        update_domain_crosswalk(ROOT / "audit/food_environment_crosswalk_v1.csv"),
    ]
    print(f"Applied weekly household food-spending metadata to {sum(counts)} field rows; no participant values or frequencies included.")


if __name__ == "__main__":
    main()
