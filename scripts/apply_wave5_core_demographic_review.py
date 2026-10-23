"""Apply source-backed CHARLS Wave 5 age and gender metadata to C catalogue rows.

Only public questionnaire/Codebook descriptions are used. No respondent values
are read by this script. The fields remain covariate candidates, not an approved
adjustment set.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WAVE = "2020"
QUESTIONNAIRE = "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt"
CODEBOOK = "sources_official/CHARLS_2020_Codebook_extracted.txt"
FIELDS = {
    "xrage": {
        "labels": "",
        "review": "officially reviewed: 2020 questionnaire auxiliary formula checked; continuous derived age; no categorical labels",
        "note": "CHARLS CAPI-derived age: if ZRBirthYear is missing or XRType=2 (new interview), XRAge=2020−BA003_1; if XRType=1 (reinterview) and ZRBirthYear is present, XRAge=2020−ZRBirthYear. This is a year-difference algorithm, not exact age at interview month/day. Candidate covariate only; retain source route and verify release/version and eligible sample before modeling.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "xrgender": {
        "labels": "1=Male; 2=Female",
        "review": "Wave 5 official questionnaire formula checked; prior-wave source semantics are audited separately",
        "note": "CHARLS CAPI-derived confirmed gender: when ZRGender is present and equals interviewer record BA001, take BA001; when they disagree, use respondent reconfirmation BA002; when ZRGender is missing, take BA001. BA001/BA002 use 1=Male and 2=Female. This Wave 5 derivation is not automatically equivalent to the Wave 1–4 Harmonized CHARLS cross-module consistency rule.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "ba001": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire response categories checked; interviewer-recorded current gender input",
        "note": "Interviewer-recorded current gender input to the released XRGender derivation. Do not substitute this input for the derived field without reconciling the prior-wave gender and current confirmation route.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "ba002": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire response categories checked; conditional current gender reconfirmation input",
        "note": "Conditional reconfirmation input used by the official XRGender formula when prior-wave ZRGender is present and differs from interviewer-recorded BA001. It is not asked/used as a universal standalone gender measure.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "zrgender": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire auxiliary definition and Codebook field checked; prior-wave gender preload",
        "note": "Prior-wave gender preload. The official XRGender formula compares it with BA001 and uses BA002 to reconfirm when they disagree; it is not a current-wave answer by itself.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "xr18gender": {
        "labels": "male=Male; female=Female",
        "review": "officially reviewed: questionnaire auxiliary definition checked; string-derived 2018 gender reference",
        "note": "Derived from ZRGender by the official questionnaire auxiliary definition; this represents the 2018 registered gender reference, not the current 2020 confirmed-gender field.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
    "xr20gender": {
        "labels": "male=Male; female=Female",
        "review": "officially reviewed: questionnaire auxiliary definition checked; string recode of interviewer input",
        "note": "String recode of BA001 (1=male, 2=female); an intermediate/derived field rather than a separate respondent report.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
    },
}


def update_json(path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for row in rows:
        code = str(row.get("Variable.Name", "")).lower()
        if row.get("Source.Wave") != WAVE or row.get("epcf", "").lower() != "c" or code not in FIELDS:
            continue
        meta = FIELDS[code]
        row.update({
            "Value.Labels": meta["labels"], "value_labels": meta["labels"],
            "Value.Label.Source": meta["source"], "value_label_source": meta["source"],
            "Value.Label.Review": meta["review"], "value_label_review": meta["review"],
            "Harmonization.Status": meta["note"], "harmonization_status": meta["note"],
            "Review.Flag": "C metadata; source-backed age/gender definition; covariate use remains estimand-specific and unapproved",
        })
        changed += 1
    path.write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return changed


def update_csv(path: Path) -> int:
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    if "Source.Wave" not in df or "Variable.Name" not in df or "epcf" not in df:
        return 0
    mask = df["Source.Wave"].eq(WAVE) & df["epcf"].str.lower().eq("c") & df["Variable.Name"].str.lower().isin(FIELDS)
    for idx in df.index[mask]:
        meta = FIELDS[df.at[idx, "Variable.Name"].lower()]
        for col, val in {
            "Value.Labels": meta["labels"], "Value.Label.Source": meta["source"],
            "Value.Label.Review": meta["review"], "Harmonization.Status": meta["note"],
            "Review.Flag": "C metadata; source-backed age/gender definition; covariate use remains estimand-specific and unapproved",
        }.items():
            if col in df.columns:
                df.at[idx, col] = val
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(mask.sum())


def main() -> None:
    for rel in (QUESTIONNAIRE, CODEBOOK):
        if not (ROOT / rel).exists():
            raise SystemExit(f"Missing source: {rel}")
    targets = [ROOT / "audit/charls_atlas_candidate_fields_v0.csv", ROOT / "audit/charls_atlas_candidate_fields_v0.json", ROOT / "site-prototype/dist/catalog.json", ROOT / "site-prototype/dist/catalog_c.json"]
    total = 0
    for path in targets:
        n = update_json(path) if path.suffix == ".json" else update_csv(path)
        print(f"{path.relative_to(ROOT)}: updated {n} rows")
        total += n
    if total < len(FIELDS):
        raise SystemExit(f"Expected at least {len(FIELDS)} matching rows, updated {total}")
    print(f"Updated {total} wave-specific metadata rows; no participant data read.")


if __name__ == "__main__":
    main()
