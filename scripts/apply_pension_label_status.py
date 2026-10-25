"""Synchronize explicit official pension response labels with source status."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "audit/pension_exposure_variable_mapping_v1.csv"
STALE_STATUS = "candidate from official variable metadata; questionnaire wording/value codes and route review pending"
REVIEWED_STATUS = (
    "official response labels reviewed; preserve source-specific response/option semantics; "
    "route, authorized-release coding and analysis eligibility remain to be validated"
)


def apply_status(mapping: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    stale = mapping["mapping_status"].eq(STALE_STATUS)
    reviewed = mapping["value_label_status"].str.contains(
        r"official (?:codebook response labels reviewed|selected-option label)",
        case=False,
        regex=True,
    )
    evidence = stale & reviewed & mapping["value_labels"].ne("")
    count = int(evidence.sum())
    target = evidence | mapping["mapping_status"].eq(REVIEWED_STATUS)
    if count not in (0, 23) or int(target.sum()) != 23:
        raise ValueError(f"Expected 23 stale pension rows with explicit labels; found {count} (total target {int(target.sum())})")
    result = mapping.copy()
    result.loc[target, "mapping_status"] = REVIEWED_STATUS
    return result, 23


def main() -> None:
    mapping = pd.read_csv(MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    updated, count = apply_status(mapping)
    updated.to_csv(MAPPING_PATH, index=False, encoding="utf-8-sig")
    print(f"Updated official response-label status for {count} pension fields; route/release-coding/analysis QA remains pending")


if __name__ == "__main__":
    main()
