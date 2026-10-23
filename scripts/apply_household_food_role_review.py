"""Apply questionnaire-backed food-purchaser and shared-meal metadata."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVES = {
    "2011": ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "ge001", "ge002", "ge004"),
    "2013": ("CHARLS_2013_Questionnaire_extracted.txt", "ge001", "ge002", "ge004"),
    "2015": ("CHARLS_2015_Questionnaire_extracted.txt", "ge001", "ge002", "ge004"),
    "2018": ("CHARLS_2018_Questionnaire_extracted.txt", "ge001", "ge002", "ge004"),
    "2020": ("CHARLS_2020_Questionnaire_English_extracted.txt", "gf002", "gf003", "gf004"),
}
FIELDS = {(wave, code): kind for wave, (_, yes, who, count) in WAVES.items()
          for code, kind in ((yes, "yes_no"), (who, "roster"), (count, "count"))}
SOURCE = "; ".join(f"sources_official/{v[0]}" for v in WAVES.values())


def apply(row: dict, wave: str, code: str) -> None:
    kind = FIELDS[(wave, code.lower())]
    source_file = f"sources_official/{WAVES[wave][0]}"
    if kind == "yes_no":
        labels = "1=Yes; 2=No"
        status = f"official {wave} questionnaire and Codebook identify respondent-as-primary-food-purchaser Yes/No; household-role item, not a dietary measure"
        unit = ""
        detail = "Ask whether the respondent is the household's primary food purchaser; 'Yes' routes past the roster selector. Household decision-role context only."
    elif kind == "roster":
        labels = ""
        status = f"official {wave} questionnaire identifies primary food purchaser through wave-specific household roster/other-person selector; dynamic identity choices are not fixed value labels"
        unit = ""
        detail = "Roster-dependent identity/role selector. Choice ranges and roster construction differ by wave; do not harmonize numeric codes as the same person or publish respondent names. Household-role context only."
    else:
        labels = ""
        status = f"official {wave} questionnaire identifies a numeric household person count; continuous count measure, no discrete category labels"
        unit = "persons"
        detail = "Counts household members who usually ate meals together during the past week, excluding guests. Treat as household context, not an individual's dietary frequency; interviewer soft checks are prompts, not analytic cutoffs. Confirm release-specific special values and household linkage before modeling."
    row.update({
        "Value.Labels": labels,
        "Value.Label.Source": source_file,
        "Value.Label.Review": status,
        "Concept.Unit.Candidates": unit,
        "Unit": unit,
        "Harmonization.Status": detail,
        "value_labels": labels,
        "value_label_source": source_file,
        "value_label_review": status,
        "candidate_concept_units": unit,
        "harmonization_status": detail,
    })


def validate_sources() -> None:
    for wave, (name, yes, who, count) in WAVES.items():
        text = (ROOT / "sources_official" / name).read_text(encoding="utf-8", errors="ignore").casefold()
        for code in (yes, who, count):
            if code.casefold() not in text:
                raise ValueError(f"Questionnaire source lacks {wave} {code}")
        if "primary person" not in text or "purchas" not in text:
            raise ValueError(f"Questionnaire source lacks purchaser wording for {wave}")


def update_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r["Source.Wave"]), str(r["Variable.Name"]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, "Source.Wave"], df.loc[selected, "Variable.Name"].str.lower()))
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}; unexpected {sorted(seen-set(FIELDS))}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        apply(row, str(row["Source.Wave"]), str(row["Variable.Name"]).lower())
        for key in ("Value.Labels", "Value.Label.Source", "Value.Label.Review", "Concept.Unit.Candidates", "Unit", "Harmonization.Status"):
            df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and "source_fields" in rows[0]:
        found = set()
        for concept in rows:
            for row in concept["source_fields"]:
                key = (str(row.get("wave", "")), str(row.get("code", "")).lower())
                if key not in FIELDS:
                    continue
                found.add(key)
                proxy = {}
                apply(proxy, *key)
                row.update({
                    "value_labels": proxy["Value.Labels"],
                    "value_label_status": proxy["Value.Label.Review"],
                    "value_label_source": proxy["Value.Label.Source"],
                    "unit": proxy["Unit"],
                    "note": proxy["Harmonization.Status"],
                })
        if found != set(FIELDS):
            raise ValueError(f"{path}: missing {sorted(set(FIELDS)-found)}")
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return len(found)
    if not rows or wave_key not in rows[0]:
        return 0
    selected = [r for r in rows if (str(r.get(wave_key, "")), str(r.get(code_key, "")).lower()) in FIELDS]
    seen = {(str(r[wave_key]), str(r[code_key]).lower()) for r in selected}
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for row in selected:
        wave, code = str(row[wave_key]), str(row[code_key]).lower()
        apply(row, wave, code)
        if wave_key == "wave":
            row["unit"] = FIELDS[(wave, code)] == "count" and "persons" or ""
            row["value_label_status"] = row["Value.Label.Review"]
            row["mapping_status"] = row["Value.Label.Review"]
            row["caveat"] = row["Harmonization.Status"]
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if wave_key == "wave" else json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    path.write_text(payload, encoding="utf-8")
    return len(selected)


def main() -> None:
    validate_sources()
    paths = [
        (ROOT / "audit/charls_atlas_candidate_fields_v0.csv", "csv"),
        (ROOT / "audit/food_environment_crosswalk_v1.csv", "csv"),
        (ROOT / "audit/charls_atlas_candidate_fields_v0.json", "source"),
        (ROOT / "site-prototype/dist/catalog.json", "source"),
        (ROOT / "site-prototype/dist/catalog_e.json", "source"),
        (ROOT / "site-prototype/dist/food_environment_v1.json", "food"),
    ]
    count = 0
    for path, kind in paths:
        if kind == "csv" and path.name == "food_environment_crosswalk_v1.csv":
            df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
            selected = df.apply(lambda r: (str(r["wave"]), str(r["code"]).lower()) in FIELDS, axis=1)
            seen = set(zip(df.loc[selected, "wave"], df.loc[selected, "code"].str.lower()))
            if seen != set(FIELDS):
                raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
            for idx in df.index[selected]:
                row = df.loc[idx].to_dict()
                apply(row, str(row["wave"]), str(row["code"]).lower())
                df.at[idx, "code_value_labels"] = row["Value.Labels"]
                df.at[idx, "mapping_status"] = row["Value.Label.Review"]
                df.at[idx, "caveat"] = row["Harmonization.Status"]
            df.to_csv(path, index=False, encoding="utf-8-sig")
            count += int(selected.sum())
        else:
            count += update_csv(path) if kind == "csv" else update_json(path, "wave", "code") if kind == "food" else update_json(path, "Source.Wave", "Variable.Name")
    print(f"Applied questionnaire-backed household food-role/meal-count metadata to {count} field rows; participant data and frequencies were not used.")


if __name__ == "__main__":
    main()
