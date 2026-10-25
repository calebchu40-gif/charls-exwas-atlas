"""Synchronize chronic-disease ancillary labels already transcribed from official sources."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "audit/chronic_disease_ancillary_variable_mapping_v1.csv"
STALE_STATUS = "official variable metadata mapped; item-level value labels/routing review pending"
REVIEWED_STATUS = (
    "official response categories reviewed/transcribed from wave-specific questionnaire/Codebook; "
    "retain source-specific route and time frame; release coding, routed denominator and analysis eligibility require QA"
)


def apply_status(mapping: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    stale = mapping["mapping_status"].eq(STALE_STATUS)
    reviewed_evidence = mapping["value_label_status"].str.contains(
        r"official .*?(?:response labels reviewed|response categories transcribed|response options|selected-option category transcribed)",
        case=False,
        regex=True,
    ) & mapping["value_label_status"].ne(STALE_STATUS)
    target = (stale & reviewed_evidence & mapping["value_labels"].ne("")) | mapping["mapping_status"].eq(REVIEWED_STATUS)
    count = int(target.sum())
    if count != 83:
        raise ValueError(f"Expected 83 stale rows with explicit reviewed labels; found {count}")
    result = mapping.copy()
    result.loc[target, "mapping_status"] = REVIEWED_STATUS
    return result, count


def main() -> None:
    mapping = pd.read_csv(MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    updated, count = apply_status(mapping)
    updated.to_csv(MAPPING_PATH, index=False, encoding="utf-8-sig")
    print(f"Updated response-label status for {count} chronic-disease ancillary fields; release coding/denominator/analysis QA remains pending")


if __name__ == "__main__":
    main()
