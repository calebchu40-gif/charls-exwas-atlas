"""Apply wave-specific CHARLS toilet-type and toilet-distance review."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
Q = {
    "2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
    "2013": "CHARLS_2013_Questionnaire_extracted.txt",
    "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    "2018": "CHARLS_2018_Questionnaire_extracted.txt",
    "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
}
CB = {w: f"CHARLS_{w}_Codebook_extracted.txt" for w in Q}
FIELDS = {}
for wave, code in [(w, "i013") for w in ("2011", "2013", "2015")] + [("2018", "i013"), ("2020", "i012")]:
    FIELDS[(wave, code)] = ("distance", "", "Nearest toilet distance is a numeric measure in meters. Questionnaire soft checks are interviewer prompts, not valid-range cutoffs; Codebook extrema, including implausible extremes, are not analytic thresholds.")
for wave, code, label in [
    ("2011", "i014s1", "1=Toilet without a seat"), ("2011", "i014s2", "2=Toilet with a seat"),
    ("2013", "i014s1", "1=Toilet without a seat"), ("2013", "i014s2", "2=Toilet with a seat"),
    ("2015", "i014s1", "1=Toilet without a seat"), ("2015", "i014s2", "2=Toilet with a seat"),
    ("2018", "i014", "1=Toilet without a seat; 2=Toilet with a seat"),
    ("2020", "i013", "1=Toilet without a seat; 2=Toilet with a seat"),
]:
    FIELDS[(wave, code)] = ("type", label, "Toilet type is a household sanitation/access characteristic, not a pollutant dose. In 2011–2015 the Codebook represents the response as separate option-specific fields; the questionnaire presents a single type question. Do not infer that a missing/zero option-specific field means the alternative category without authorized-release storage validation. 2018/2020 use a single categorical item; 2018 explicitly instructs selecting the seated toilet if both are present.")


def apply(row: dict, wave: str, code: str) -> None:
    kind, labels, detail = FIELDS[(wave, code.lower())]
    unit = "meters" if kind == "distance" else ""
    source = f"sources_official/{Q[wave]}; sources_official/{CB[wave]}"
    status = f"official {wave} questionnaire/Codebook review: numeric distance in meters, no discrete labels" if kind == "distance" else f"official {wave} questionnaire/Codebook category wording reviewed; preserve wave-specific storage representation"
    caveat = detail + " Verify release-specific special values, routes, measurement object, and missingness before modeling; cross-wave equivalence is not established."
    row.update({
        "Value.Labels": labels, "Value.Label.Source": source, "Value.Label.Review": status,
        "Concept.Unit.Candidates": unit, "Unit": unit, "Harmonization.Status": caveat,
        "value_labels": labels, "value_label_source": source, "value_label_review": status,
        "candidate_concept_units": unit, "harmonization_status": caveat,
    })


def validate_sources() -> None:
    for wave, code in FIELDS:
        qtext = (ROOT / "sources_official" / Q[wave]).read_text(encoding="utf-8", errors="ignore").casefold()
        cbtext = (ROOT / "sources_official" / CB[wave]).read_text(encoding="utf-8", errors="ignore").casefold()
        questionnaire_code = "i014" if code in ("i014s1", "i014s2") else code
        if questionnaire_code not in qtext or code not in cbtext:
            raise ValueError(f"official questionnaire/Codebook missing {wave} {code}")


def update_csv(path: Path, wave_col: str, code_col: str, mapping: bool = False) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r[wave_col]), str(r[code_col]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, wave_col], df.loc[selected, code_col].str.lower()))
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for idx in df.index[selected]:
        row = df.loc[idx].to_dict()
        apply(row, str(row[wave_col]), str(row[code_col]).lower())
        if mapping:
            df.at[idx, "code_value_labels"] = row["Value.Labels"]
            df.at[idx, "mapping_status"] = row["Value.Label.Review"]
            df.at[idx, "caveat"] = row["Harmonization.Status"]
        else:
            for key in ("Value.Labels", "Value.Label.Source", "Value.Label.Review", "Concept.Unit.Candidates", "Unit", "Harmonization.Status"):
                if key in df.columns:
                    df.at[idx, key] = row[key]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and "source_fields" in rows[0]:
        fields = [f for c in rows for f in c["source_fields"]]
    else:
        fields = rows
    selected = [f for f in fields if (str(f.get(wave_key, "")), str(f.get(code_key, "")).lower()) in FIELDS]
    seen = {(str(f[wave_key]), str(f[code_key]).lower()) for f in selected}
    if not seen:
        return 0
    if seen != set(FIELDS):
        raise ValueError(f"{path}: missing {sorted(set(FIELDS)-seen)}")
    for f in selected:
        row = {}
        apply(row, str(f[wave_key]), str(f[code_key]).lower())
        if "source_fields" in rows[0]:
            f.update({"value_labels": row["Value.Labels"], "value_label_status": row["Value.Label.Review"], "value_label_source": row["Value.Label.Source"], "unit": row["Unit"], "note": row["Harmonization.Status"]})
        else:
            f.update({k: v for k, v in row.items() if k in ("Value.Labels", "Value.Label.Source", "Value.Label.Review", "Concept.Unit.Candidates", "Unit", "Harmonization.Status", "value_labels", "value_label_source", "value_label_review", "candidate_concept_units", "harmonization_status")})
            if wave_key == "wave":
                f.update({"unit": row["Unit"], "value_labels": row["Value.Labels"], "value_label_status": row["Value.Label.Review"], "value_label_source": row["Value.Label.Source"], "mapping_status": row["Value.Label.Review"], "caveat": row["Harmonization.Status"]})
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n" if wave_key == "wave" else json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(selected)


def main() -> None:
    validate_sources()
    count = update_csv(ROOT / "audit/charls_atlas_candidate_fields_v0.csv", "Source.Wave", "Variable.Name")
    count += update_csv(ROOT / "audit/food_environment_crosswalk_v1.csv", "wave", "code", mapping=True)
    count += update_json(ROOT / "audit/charls_atlas_candidate_fields_v0.json", "Source.Wave", "Variable.Name")
    count += update_json(ROOT / "site-prototype/dist/catalog.json", "Source.Wave", "Variable.Name")
    count += update_json(ROOT / "site-prototype/dist/catalog_e.json", "Source.Wave", "Variable.Name")
    count += update_json(ROOT / "site-prototype/dist/food_environment_v1.json", "wave", "code")
    print(f"Applied toilet type/distance review to {count} metadata rows; no participant responses, frequencies or extrema copied.")


if __name__ == "__main__":
    main()
