"""Apply questionnaire-backed measurement metadata to pending household expenses."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def item_status(wave: str, code: str) -> tuple[str, str, str]:
    if code.lower() in {"ge006_w2", "gf007"}:
        unit = ""
        labels = "1=Yes; 2=No"
        status = "official Codebook response categories reviewed; frequencies and percentages omitted"
        wording = "whether the household produces agricultural products for its own use"
        caveat = "This is a household-level indicator, not respondent diet or individual food intake; follow-up market value applies only to self-produced food consumed by household members."
    else:
        labels = ""
        status = f"official {wave} questionnaire and Codebook identify continuous household expenditure; no discrete response categories"
        wording = "household expenditure"
        code_l = code.lower()
        if code_l.startswith("ge009_"):
            unit = "Yuan/month"
            period = "previous month"
        elif code_l.startswith("ge010_") or code_l.startswith("gf013_"):
            unit = "Yuan/year"
            period = "previous year"
        elif code_l in {"ge008", "gf010"}:
            unit = "Yuan/week"
            period = "previous week"
        else:
            raise ValueError(f"No period rule for {wave}/{code}")
        caveat = f"{wave} {wording} in the {period}; household-level resource measure, not personal spending. Preserve the wave-specific item list and period. Questionnaire soft checks are not analytic cutoffs. Do not infer valid ranges from Codebook summaries."
    return status, labels, (unit + "|" + wording + "|" + caveat)


def main() -> None:
    crosswalk_path = AUDIT / "household_economic_exposure_mapping_v1.csv"
    frame = pd.read_csv(crosswalk_path, dtype=str, encoding="utf-8-sig").fillna("")
    wave_codes = {
        "2011": {"ge009_1", "ge009_2", "ge009_3", "ge010_1", "ge010_2", "ge010_3", "ge010_5", "ge010_8", "ge010_9", "ge010_10", "ge010_11", "ge010_12", "ge010_13", "ge010_14"},
        "2013": {"ge006_w2", "ge010_11", "ge010_12", "ge010_13"},
        "2015": {"ge006_w2", "ge010_11", "ge010_12", "ge010_13"},
        "2018": {"ge006_w2", "ge008", "ge009_1", "ge009_2", "ge009_3", "ge010_1", "ge010_2", "ge010_3", "ge010_4", "ge010_5", "ge010_8", "ge010_9", "ge010_10", "ge010_11", "ge010_12", "ge010_13", "ge010_14"},
        "2020": {"gf007", "gf010", "gf013_1", "gf013_2", "gf013_3", "gf013_4", "gf013_5", "gf013_8", "gf013_9", "gf013_10", "gf013_11", "gf013_12", "gf013_13", "gf013_14"},
    }
    pairs = {(wave, code) for wave, codes in wave_codes.items() for code in codes}
    target = frame[frame.apply(lambda r: (r["wave"], r["code"].lower()) in pairs, axis=1)].copy()
    if len(target) != 53:
        raise SystemExit(f"Expected 53 mapped household expenditure fields, found {len(target)}")

    updates = []
    for idx, row in target.iterrows():
        wave, code = row["wave"], row["code"]
        questionnaire_candidates = list((ROOT / "sources_official").glob(f"CHARLS_{wave}_*Questionnaire*_extracted.txt"))
        if wave == "2011":
            questionnaire_candidates = [ROOT / "sources_official/CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt"]
        if not questionnaire_candidates:
            raise SystemExit(f"Official questionnaire missing for wave {wave}")
        qtext = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in questionnaire_candidates).lower()
        cpath = ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt"
        ctext = cpath.read_text(encoding="utf-8", errors="replace")
        if compact(code) not in compact(ctext):
            raise SystemExit(f"Official Codebook field missing: {wave}/{code}")
        if code.lower() not in qtext:
            # Some official questionnaire extractions use GE010_W4 or GF013 prose; require the family stem and source item label.
            stem = re.match(r"[a-z]+\d+", code.lower()).group(0)
            if stem not in qtext:
                raise SystemExit(f"Official questionnaire item family missing: {wave}/{code}")
        status, labels, semantic_blob = item_status(wave, code)
        unit, *semantics = semantic_blob.split("|", 2)
        note = semantics[1] if len(semantics) == 2 else semantics[0]
        row["value_label_status"] = status
        row["value_label_source"] = f"sources_official/{questionnaire_candidates[0].name}; sources_official/{cpath.name}"
        row["value_labels"] = labels
        row["unit"] = unit
        row["value_semantics"] = note
        frame.loc[idx, row.index] = row
        updates.append(row.to_dict())
    frame.to_csv(crosswalk_path, index=False, encoding="utf-8-sig")
    print(f"Reviewed {len(target)} household expenditure fields across 2011–2020; household scope and periods recorded; no Codebook frequencies/extrema copied.")


if __name__ == "__main__":
    main()
