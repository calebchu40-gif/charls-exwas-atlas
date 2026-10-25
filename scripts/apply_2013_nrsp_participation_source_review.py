"""Review the 2013 current New Rural Social Pension participation item.

Metadata-only. Checks the official questionnaire and Codebook wording/codes;
does not import response frequencies or read respondent-level data.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
CONCEPT = "new_rural_social_pension_participation"
WAVE = "2013"
CODE = "fn069_w2"
QUESTIONNAIRE = ROOT / "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
CODEBOOK = ROOT / "sources_official/CHARLS_2013_Codebook_extracted.txt"
QUESTION_SOURCE = "sources_official/CHARLS_2013_Questionnaire_extracted.txt"
CODEBOOK_SOURCE = "sources_official/CHARLS_2013_Codebook_extracted.txt"
OFFICIAL_SOURCE = f"{QUESTION_SOURCE}; {CODEBOOK_SOURCE}"
STATUS = "official 2013 questionnaire and Codebook item wording, Yes/No response codes and route reviewed; candidate mapping"
LABELS = "1=Yes; 2=No"
CAVEAT = (
    "2013 asks current participation in New Rural Social Pension Insurance. Yes routes to FN071_W2 for first-coverage month/year; No routes to FN070_W2 multi-select non-participation reasons. Preserve this gate and its eligible denominator; skipped reason slots are not negative responses. Keep separate from receiving a pension, the preloaded prior-wave pension-plan roster, contribution/payment amounts, benefit receipt/amount, and other pension schemes. A common concept ID with 2011 does not establish cross-wave measurement equivalence. Confirm authorized-release field identity, special/missing codes, and target population before analysis."
)


def validate_sources() -> None:
    qtext = re.sub(r"[\s-]+", " ", QUESTIONNAIRE.read_text(encoding="utf-8", errors="ignore").casefold())
    ctext = re.sub(r"\s+", " ", CODEBOOK.read_text(encoding="utf-8", errors="ignore").casefold())
    qstart = qtext.find("fn069_w2 do you currently")
    if qstart < 0:
        raise ValueError("2013 questionnaire FN069_W2 not found")
    qblock = qtext[qstart:qstart + 1200]
    for phrase in ("currently participate in the new rural social pension insurance", "skip to fn071_w2", "fn070_w2"):
        if phrase not in qblock:
            raise ValueError(f"2013 questionnaire route check failed: {phrase}")
    cstart = ctext.find("fn069_w2")
    if cstart < 0:
        raise ValueError("2013 Codebook FN069_W2 not found")
    cblock = ctext[cstart:ctext.find("•", cstart + 1) if "•" in ctext[cstart + 1:] else cstart + 600]
    for phrase in ("1 yes", "2 no"):
        if phrase not in cblock:
            raise ValueError(f"2013 Codebook response-code check failed: {phrase}")


def update_pension_exposure() -> int:
    path = AUDIT / "pension_exposure_variable_mapping_v1.csv"
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = (
        df.wave.astype(str).eq(WAVE)
        & df.code.astype(str).str.lower().eq(CODE)
        & df.concept_id.astype(str).eq(CONCEPT)
    )
    if int(mask.sum()) != 1:
        raise ValueError(f"Expected exactly one pension source row for {WAVE}/{CODE}/{CONCEPT}; found {int(mask.sum())}")
    idx = df.index[mask][0]
    df.loc[idx, "mapping_status"] = STATUS
    df.loc[idx, "value_label_status"] = "official 2013 Codebook Yes/No response codes reviewed; frequencies omitted"
    df.loc[idx, "value_labels"] = LABELS
    df.loc[idx, "source_item"] = "FN069_W2"
    df.loc[idx, "value_semantics"] = "1=Yes; 2=No. Yes routes to FN071_W2; No routes to FN070_W2 non-participation reasons."
    df.loc[idx, "caveat"] = CAVEAT
    df.loc[idx, "source_archive"] = "CHARLS2013_Dataset.zip"
    df.loc[idx, "official_source"] = OFFICIAL_SOURCE
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(mask.sum())


def update_participation_crosswalk() -> int:
    path = AUDIT / "pension_participation_crosswalk_v1.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        rows = list(reader)
    matches = [r for r in rows if (r.get("wave"), r.get("code", "").lower(), r.get("concept_id")) == (WAVE, CODE, CONCEPT)]
    if len(matches) > 1:
        raise ValueError(f"Duplicate 2013 NRSP participation crosswalk rows: {len(matches)}")
    raw = pd.read_csv(AUDIT / "raw_variable_catalog_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
    found = raw[(raw.wave.astype(str) == WAVE) & (raw.variable.astype(str).str.lower() == CODE)]
    if len(found) != 1:
        raise ValueError(f"Expected one raw field record for {WAVE}/{CODE}; found {len(found)}")
    source = found.iloc[0]
    row = {
        "wave": WAVE,
        "code": CODE,
        "concept_id": CONCEPT,
        "concept_label": "新型农村社会养老保险当前参保",
        "domain": "social protection",
        "module": source.get("module", ""),
        "source_label": source.get("variable_label", ""),
        "source_item": "FN069_W2",
        "construct": "Current participation in New Rural Social Pension Insurance",
        "unit": "categorical",
        "value_labels": LABELS,
        "value_semantics": "1=Yes; 2=No. Yes routes to FN071_W2; No routes to FN070_W2 non-participation reasons.",
        "mapping_status": STATUS,
        "caveat": CAVEAT,
        "source_archive": source.get("source", "CHARLS2013_Dataset.zip"),
        "official_source": OFFICIAL_SOURCE,
    }
    if matches:
        rows[rows.index(matches[0])] = row
    else:
        rows.append(row)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return 1


def update_codebook_label_audit() -> int:
    path = AUDIT / "pension_codebook_value_labels_v1.csv"
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("")
    mask = df.wave.astype(str).eq(WAVE) & df.code.astype(str).str.lower().eq(CODE)
    if int(mask.sum()) != 1:
        raise ValueError(f"Expected one codebook label-audit row for {WAVE}/{CODE}; found {int(mask.sum())}")
    df.loc[mask, "value_label_status"] = "official 2013 Codebook Yes/No response codes reviewed; frequencies omitted"
    df.loc[mask, "value_labels"] = LABELS
    df.loc[mask, "value_label_source"] = OFFICIAL_SOURCE
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return int(mask.sum())


def main() -> None:
    validate_sources()
    updated = update_pension_exposure() + update_participation_crosswalk() + update_codebook_label_audit()
    print(f"Reviewed 2013 {CODE.upper()} current NRSP participation route and Yes/No labels; updated {updated} metadata mappings; no frequencies or respondent records used.")


if __name__ == "__main__":
    main()
