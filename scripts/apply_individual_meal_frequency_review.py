"""Apply the questionnaire-backed two-wave usual meal-frequency categories."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {("2011", "da058"), ("2013", "da058")}
LABELS = "1=More than 4 meals per day; 2=4 meals per day; 3=3 meals per day; 4=2 meals per day; 5=1 meal per day; 6=<1 meal per day"
QUESTIONNAIRES = {"2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt", "2013": "CHARLS_2013_Questionnaire_extracted.txt"}


def apply(row: dict, wave: str) -> None:
    source = f"sources_official/{QUESTIONNAIRES[wave]}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"
    status = f"official {wave} questionnaire/Codebook labels reviewed; six ordered self-reported usual meals-per-day categories"
    caveat = "Self-reported usual individual meals per day; an ordinal behavior measure, not dietary quality, nutrient intake, or a laboratory exposure. Only mapped for 2011 and 2013; do not infer coverage or equivalence in later waves. Verify release-specific special values, item eligibility and missingness before modeling."
    row.update({"Value.Labels": LABELS, "Value.Label.Source": source, "Value.Label.Review": status,
                "Concept.Unit.Candidates": "", "Unit": "", "Harmonization.Status": caveat,
                "value_labels": LABELS, "value_label_source": source, "value_label_review": status,
                "candidate_concept_units": "", "harmonization_status": caveat})


def validate() -> None:
    for wave, code in FIELDS:
        for file in (QUESTIONNAIRES[wave], f"CHARLS_{wave}_Codebook_extracted.txt"):
            if code not in (ROOT / "sources_official" / file).read_text(encoding="utf-8", errors="ignore").casefold():
                raise ValueError(f"missing official source field {wave} {code}: {file}")
        qtext = (ROOT / "sources_official" / QUESTIONNAIRES[wave]).read_text(encoding="utf-8", errors="ignore").casefold()
        if "more than 4 meals per day" not in qtext or "<1 meal per day" not in qtext:
            raise ValueError(f"missing response categories in {wave} questionnaire")


def update_csv(path: Path, wave_col: str, code_col: str, mapping: bool = False) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    selected = df.apply(lambda r: (str(r[wave_col]), str(r[code_col]).lower()) in FIELDS, axis=1)
    seen = set(zip(df.loc[selected, wave_col], df.loc[selected, code_col].str.lower()))
    if seen != FIELDS:
        raise ValueError(f"{path}: missing {sorted(FIELDS-seen)}")
    for idx in df.index[selected]:
        row = {}; apply(row, str(df.at[idx, wave_col]))
        if mapping:
            df.at[idx, "code_value_labels"] = row["Value.Labels"]
            df.at[idx, "mapping_status"] = row["Value.Label.Review"]
            df.at[idx, "caveat"] = row["Harmonization.Status"]
        else:
            for k in ("Value.Labels", "Value.Label.Source", "Value.Label.Review", "Concept.Unit.Candidates", "Unit", "Harmonization.Status"):
                if k in df.columns: df.at[idx, k] = row[k]
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(selected.sum())


def update_json(path: Path, wave_key: str, code_key: str) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if rows and "source_fields" in rows[0]: fields = [f for c in rows for f in c["source_fields"]]
    else: fields = rows
    selected = [f for f in fields if (str(f.get(wave_key, "")), str(f.get(code_key, "")).lower()) in FIELDS]
    if not selected: return 0
    seen = {(str(f[wave_key]), str(f[code_key]).lower()) for f in selected}
    if seen != FIELDS: raise ValueError(f"{path}: missing {sorted(FIELDS-seen)}")
    for f in selected:
        row = {}; apply(row, str(f[wave_key]))
        if "source_fields" in rows[0]:
            f.update({"value_labels": LABELS, "value_label_status": row["Value.Label.Review"], "value_label_source": row["Value.Label.Source"], "note": row["Harmonization.Status"]})
        else:
            f.update({k:v for k,v in row.items() if k in ("Value.Labels","Value.Label.Source","Value.Label.Review","Concept.Unit.Candidates","Unit","Harmonization.Status","value_labels","value_label_source","value_label_review","candidate_concept_units","harmonization_status")})
            if wave_key == "wave": f.update({"value_labels":LABELS,"value_label_status":row["Value.Label.Review"],"value_label_source":row["Value.Label.Source"],"mapping_status":row["Value.Label.Review"],"caveat":row["Harmonization.Status"]})
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+"\n" if wave_key=="wave" else json.dumps(rows,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    return len(selected)


def main() -> None:
    validate()
    n=update_csv(ROOT/"audit/charls_atlas_candidate_fields_v0.csv","Source.Wave","Variable.Name")
    n+=update_csv(ROOT/"audit/food_environment_crosswalk_v1.csv","wave","code",True)
    n+=update_json(ROOT/"audit/charls_atlas_candidate_fields_v0.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/catalog.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/catalog_e.json","Source.Wave","Variable.Name")
    n+=update_json(ROOT/"site-prototype/dist/food_environment_v1.json","wave","code")
    print(f"Applied the two-wave individual meal-frequency review to {n} metadata rows; no participant responses or frequencies copied.")


if __name__ == "__main__": main()
