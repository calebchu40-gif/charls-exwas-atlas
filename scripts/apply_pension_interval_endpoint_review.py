"""Review pension contribution/benefit interval endpoints without treating them as point values."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "audit/pension_exposure_variable_mapping_v1.csv"
TARGETS = {
    "2011": {"fn005_a", "fn005_b", "fn008_a", "fn008_b", "fn014_a", "fn014_b", "fn019_a", "fn019_b", "fn023_a", "fn023_b", "fn037_a", "fn037_b"},
    "2013": {"fn035_w2_bracketbracket_min", "fn035_w2_bracketbracket_max"},
    "2015": {"fn035_w2_bracket_min", "fn035_w2_bracket_max"},
}


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def source_files(wave: str) -> tuple[str, str]:
    questionnaire = {
        "2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
        "2013": "CHARLS_2013_Questionnaire_extracted.txt",
        "2015": "CHARLS_2015_Questionnaire_extracted.txt",
    }[wave]
    return questionnaire, f"CHARLS_{wave}_Codebook_extracted.txt"


def main() -> None:
    frame = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    for column in ("value_label_status", "value_label_source", "value_labels", "value_semantics", "unit"):
        if column not in frame:
            frame[column] = ""
    pairset = {(wave, code) for wave, codes in TARGETS.items() for code in codes}
    selected_mask = frame.apply(lambda row: (row["wave"], row["code"].lower()) in pairset, axis=1)
    selected = frame.loc[selected_mask].copy()
    counts = selected.groupby("wave").size().to_dict()
    if counts != {"2011": 12, "2013": 2, "2015": 2}:
        raise SystemExit(f"Expected pension interval endpoints by wave {{2011:12, 2013:2, 2015:2}}; found {counts}")

    updates = []
    for idx, row in selected.iterrows():
        wave, code, label = row["wave"], row["code"].lower(), row["source_label"].lower()
        qname, cbname = source_files(wave)
        qpath, cbpath = ROOT / "sources_official" / qname, ROOT / "sources_official" / cbname
        questionnaire = qpath.read_text(encoding="utf-8", errors="replace")
        codebook = cbpath.read_text(encoding="utf-8", errors="replace")
        if compact(code) not in compact(codebook):
            raise SystemExit(f"Official Codebook endpoint field missing: {wave}/{code}")
        stem = re.match(r"[a-z]+\d+", code).group(0)
        if stem not in questionnaire.lower():
            raise SystemExit(f"Official questionnaire item missing: {wave}/{code}")
        source = f"sources_official/{qname}; sources_official/{cbname}"
        if wave == "2013":
            unit = "CNY/month bracket endpoint; Codebook stores endpoint as string"
            status = "official questionnaire/Codebook identify a conditional bracket endpoint; Codebook explicitly says string; no discrete response categories"
            note = "Lower/upper bound of the conditional monthly contribution-amount bracket; the 2013 Codebook explicitly identifies these endpoint fields as string variables. Preserve as string and keep the paired endpoint and questionnaire route; do not coerce, midpoint-impute, or interpret as an observed contribution amount. Verify release storage and special codes before analysis."
        elif wave == "2015":
            unit = "CNY/month bracket endpoint"
            status = "official questionnaire/Codebook identify a conditional bracket endpoint; Codebook provides numeric summaries but no discrete response categories"
            note = "Lower/upper bound of the conditional monthly contribution-amount bracket. The Codebook summary is not a response-category menu or validation of a usable range; keep the endpoints paired and conditional, and verify release storage, special values, and denominator before analysis. Do not infer cutoffs from summary extrema or midpoint-impute."
        else:
            unit = "CNY/month interval bound; not a point estimate"
            status = "official questionnaire/Codebook identify a pension bracket endpoint; no discrete response categories"
            if "fn037" in code:
                note = "Lower/upper endpoint for an expected monthly benefit amount under the conditional defined-contribution-plan route. It is not a point estimate; preserve both endpoints and route, and do not combine with current pension benefit fields. Codebook summary extrema are not analytic cutoffs. Verify release storage, special codes, and denominator before analysis."
            else:
                note = "Lower/upper endpoint for a conditional monthly pension benefit/contribution amount under its item-specific pension-plan route. It is not a point estimate; preserve both endpoints and route, and do not combine distinct plan measures. Verify release storage, special codes, and denominator before analysis. Codebook summaries are not analytic cutoffs."
        row["value_label_status"] = status
        row["value_label_source"] = source
        row["value_labels"] = ""
        row["unit"] = unit
        row["value_semantics"] = note
        row["mapping_status"] = status
        caveat = row["caveat"]
        while note in caveat:
            caveat = caveat.replace(note, "")
        caveat = re.sub(r"\s*;\s*", "; ", caveat).strip(" ;")
        row["caveat"] = (caveat + "; " + note).strip("; ")
        frame.loc[idx, row.index] = row
        updates.append(row.to_dict())
    frame.to_csv(MAPPING, index=False, encoding="utf-8-sig")
    print("Reviewed 16 pension bracket endpoints in 2011/2013/2015; pair, route, and string/numeric-source caveats retained; no summary extrema copied.")


if __name__ == "__main__":
    main()
