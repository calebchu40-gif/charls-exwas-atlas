"""Review individual transfer-income source option coding by wave."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
MAPPING = AUDIT / "individual_transfer_income_crosswalk_v1.csv"


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def field_code(wave: str, code: str) -> int:
    if wave in {"2011", "2013", "2015"}:
        return int(re.search(r"s(\d+)$", code.lower()).group(1))
    return int(re.search(r"s(\d+)$", code.lower()).group(1))


def sources(wave: str) -> str:
    qname = {
        "2011": "CHARLS_2011_Baseline_Questionnaire_official_extracted.txt",
        "2013": "CHARLS_2013_Questionnaire_extracted.txt",
        "2015": "CHARLS_2015_Questionnaire_extracted.txt",
        "2018": "CHARLS_2018_Questionnaire_extracted.txt",
        "2020": "CHARLS_2020_Questionnaire_English_extracted.txt",
    }[wave]
    return f"sources_official/{qname}; sources_official/CHARLS_{wave}_Codebook_extracted.txt"


def main() -> None:
    frame = pd.read_csv(MAPPING, dtype=str, encoding="utf-8-sig").fillna("")
    for column in ("value_label_status", "value_label_source", "value_semantics"):
        if column not in frame:
            frame[column] = ""
    target_mask = frame["wave"].isin({"2011", "2013", "2015", "2018", "2020"}) & frame["concept_id"].eq("individual_transfer_income_source_receipt")
    target = frame.loc[target_mask].copy()
    expected = {"2011": 10, "2013": 10, "2015": 10, "2018": 10, "2020": 10}
    actual = target.groupby("wave").size().to_dict()
    if actual != expected:
        raise SystemExit(f"Expected 10 individual transfer source fields per wave; found {actual}")

    for idx, row in target.iterrows():
        wave, code = row["wave"], row["code"].lower()
        option = field_code(wave, code)
        qpath = ROOT / sources(wave).split("; ")[0]
        cpath = ROOT / "sources_official" / f"CHARLS_{wave}_Codebook_extracted.txt"
        qtext = qpath.read_text(encoding="utf-8", errors="replace")
        codebook = cpath.read_text(encoding="utf-8", errors="replace")
        if compact(code) not in compact(codebook):
            raise SystemExit(f"Codebook does not identify {wave}/{code}")
        qlower = qtext.lower()
        stem = "ga003" if wave in {"2011", "2013", "2015"} else ("ga003_w4" if wave == "2018" else "ga005")
        if stem not in qlower or not re.search(r"check all that apply|select all that apply", qlower):
            raise SystemExit(f"Expected official multi-select transfer-income prompt missing: {wave}/{code}")

        if wave in {"2018", "2020"}:
            pattern = re.compile(rf"(?im)^\s*{re.escape(code)}\s*:\s*(.*?)(?=^\s*[a-z][a-z0-9_]*\s*:|\Z)", re.S)
            match = pattern.search(codebook)
            if not match or not re.search(r"\b0\s+No\b", match.group(1)) or not re.search(rf"\b{option}\s+Yes\b", match.group(1)):
                raise SystemExit(f"Expected explicit 0=No and {option}=Yes labels missing: {wave}/{code}")
            status = "official questionnaire/Codebook response categories reviewed; frequencies omitted; option-specific Yes code verified"
            labels = f"0=No; {option}=Yes"
            extra = "The official Codebook explicitly gives 0=No and this item's option-number=Yes. This is an individual past-year transfer-income source indicator, not an amount. Preserve the wave-specific source item; do not treat the mutually exclusive 'None of the above' option as a receipt source. No frequency data copied."
            if wave == "2020":
                extra += " The 2020 questionnaire explicitly includes individual COVID-19 pandemic subsidies in transfer income."
        else:
            status = "official questionnaire and Codebook option identity reviewed; participant-level No/unselected storage and denominator unresolved; no response-value labels assigned"
            labels = ""
            extra = "The questionnaire defines a past-year check-all-that-apply individual-income source item. The Codebook identifies the affirmative option text but does not establish a safe participant-level 0=No value, how unselected slots are stored, or the eligible denominator. Do not infer No from blank or missing values; verify against the authorized release before analysis."
        row["value_label_status"] = status
        row["value_label_source"] = sources(wave)
        row["value_labels"] = labels
        row["value_semantics"] = extra
        row["mapping_status"] = status
        caveat = row["caveat"]
        while extra in caveat:
            caveat = caveat.replace(extra, "")
        caveat = re.sub(r"\s*;\s*", "; ", caveat).strip(" ;")
        row["caveat"] = (caveat + "; " + extra).strip("; ")
        frame.loc[idx, row.index] = row

    frame.to_csv(MAPPING, index=False, encoding="utf-8-sig")
    print("Reviewed 50 individual transfer-income source fields across five waves; early-wave storage uncertainty preserved; no Codebook frequencies copied.")


if __name__ == "__main__":
    main()
