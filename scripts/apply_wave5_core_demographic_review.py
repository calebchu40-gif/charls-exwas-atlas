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
        "candidate_status": "C metadata; official age derivation reviewed; adjustment eligibility remains estimand-specific and unapproved",
        "review_flag": "C candidate age metadata; retain interview-route and age-reference caveats; not automatically selected for adjustment",
        "category": "source-reviewed demographic metadata",
        "subcategory": "respondent age derivation",
    },
    "xrgender": {
        "labels": "1=Male; 2=Female",
        "review": "Wave 5 official questionnaire formula checked; prior-wave source semantics are audited separately",
        "note": "CHARLS CAPI-derived confirmed gender: when ZRGender is present and equals interviewer record BA001, take BA001; when they disagree, use respondent reconfirmation BA002; when ZRGender is missing, take BA001. BA001/BA002 use 1=Male and 2=Female. This Wave 5 derivation is not automatically equivalent to the Wave 1–4 Harmonized CHARLS cross-module consistency rule.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official gender derivation reviewed; adjustment eligibility remains estimand-specific and unapproved",
        "review_flag": "C candidate gender metadata; derived current value is wave-specific; not automatically selected for adjustment",
        "category": "source-reviewed demographic metadata",
        "subcategory": "confirmed gender derivation",
    },
    "ba001": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire response categories checked; interviewer-recorded current gender input",
        "note": "Interviewer-recorded current gender input to the released XRGender derivation. Do not substitute this input for the derived field without reconciling the prior-wave gender and current confirmation route.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official gender input reviewed; distinguish interviewer report from derived current gender",
        "review_flag": "C gender-source metadata; interviewer input is not a substitute for the official derived field",
        "category": "source-reviewed demographic metadata",
        "subcategory": "interviewer-recorded gender input",
    },
    "ba002": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire response categories checked; conditional current gender reconfirmation input",
        "note": "Conditional reconfirmation input used by the official XRGender formula when prior-wave ZRGender is present and differs from interviewer-recorded BA001. It is not asked/used as a universal standalone gender measure.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official conditional gender reconfirmation reviewed; not a universal standalone measure",
        "review_flag": "C gender-source metadata; conditional reconfirmation input, not a universal adjustment variable",
        "category": "source-reviewed demographic metadata",
        "subcategory": "conditional gender reconfirmation input",
    },
    "zrgender": {
        "labels": "1=Male; 2=Female",
        "review": "officially reviewed: questionnaire auxiliary definition and Codebook field checked; prior-wave gender preload",
        "note": "Prior-wave gender preload. The official XRGender formula compares it with BA001 and uses BA002 to reconfirm when they disagree; it is not a current-wave answer by itself.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official prior-wave gender preload reviewed; not a current-wave response by itself",
        "review_flag": "C gender-source metadata; prior-wave preload, not a current-wave response",
        "category": "source-reviewed demographic metadata",
        "subcategory": "prior-wave gender preload",
    },
    "xr18gender": {
        "labels": "male=Male; female=Female",
        "review": "officially reviewed: questionnaire auxiliary definition checked; string-derived 2018 gender reference",
        "note": "Derived from ZRGender by the official questionnaire auxiliary definition; this represents the 2018 registered gender reference, not the current 2020 confirmed-gender field.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official 2018 gender reference derivation reviewed; distinct from current 2020 gender",
        "review_flag": "C gender-reference metadata; 2018 value is not the current 2020 confirmed-gender field",
        "category": "source-reviewed demographic metadata",
        "subcategory": "prior-wave gender reference",
    },
    "xr20gender": {
        "labels": "male=Male; female=Female",
        "review": "officially reviewed: questionnaire auxiliary definition checked; string recode of interviewer input",
        "note": "String recode of BA001 (1=male, 2=female); an intermediate/derived field rather than a separate respondent report.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "candidate_status": "C metadata; official intermediate gender recode reviewed; not a separate respondent report",
        "review_flag": "C gender-derivation metadata; intermediate recode, not a separate respondent report",
        "category": "source-reviewed demographic metadata",
        "subcategory": "interviewer gender recode",
    },
    "xfagepossibility": {
        "labels": "",
        "review": "officially reviewed: questionnaire auxiliary formula checked; age-threshold target, not respondent age or observed survival",
        "note": "CAPI-generated target age used in the 2020 DA029 subjective life-expectancy question. It is set by XRAge bands (<65→75; 65–69→80; 70–74→85; 75–79→90; 80–84→95; 85–89→100; 90–94→105; 95–99→110; ≥100→115). This is question-vignette metadata, not an independently reported expectation, a clinical outcome, or a routine covariate. Interpret DA029 responses together with this age-specific threshold; do not treat thresholds as identical across respondents.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "category": "measurement metadata",
        "subcategory": "subjective life-expectancy target age",
        "unit": "years",
        "candidate_status": "C measurement metadata; subjective life-expectancy target age; not observed survival or an adjustment covariate",
        "review_flag": "C question-vignette metadata; age threshold is not respondent age, survival, or a routine covariate",
    },
    "dc030": {
        "labels": "1=Mandarin; 2=Local dialect; 3=Other dialect, please specify",
        "review": "officially reviewed: 2020 interviewer-observation categories checked against questionnaire and Codebook",
        "note": "Interviewer-observed language used during the interview. This describes interview language, not the respondent’s native language or an environmental exposure. It may be relevant to measurement context; do not recommend it automatically as an adjustment covariate.",
        "source": f"{QUESTIONNAIRE}; {CODEBOOK}",
        "category": "measurement metadata",
        "subcategory": "interview language",
        "candidate_status": "C measurement metadata; interviewer-observed interview language; not respondent native language or a default covariate",
        "review_flag": "C interview-context metadata; interviewer-observed language, not respondent native language or an automatic adjustment variable",
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
            "Candidate.Status": meta.get("candidate_status", row.get("Candidate.Status", "")),
            "Review.Flag": meta.get("review_flag", "C metadata; source-backed demographic definition; adjustment use remains estimand-specific and unapproved"),
        })
        if "category" in meta:
            row["category"] = meta["category"]
            row["subcategory"] = meta["subcategory"]
        if "unit" in meta:
            row["Unit"] = meta["unit"]
            row["Concept.Unit.Candidates"] = meta["unit"]
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
            "Candidate.Status": meta.get("candidate_status", df.at[idx, "Candidate.Status"] if "Candidate.Status" in df else ""),
            "Review.Flag": meta.get("review_flag", "C metadata; source-backed demographic definition; adjustment use remains estimand-specific and unapproved"),
            "category": meta.get("category", df.at[idx, "category"] if "category" in df else ""),
            "subcategory": meta.get("subcategory", df.at[idx, "subcategory"] if "subcategory" in df else ""),
            "Unit": meta.get("unit", df.at[idx, "Unit"] if "Unit" in df else ""),
            "Concept.Unit.Candidates": meta.get("unit", df.at[idx, "Concept.Unit.Candidates"] if "Concept.Unit.Candidates" in df else ""),
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
