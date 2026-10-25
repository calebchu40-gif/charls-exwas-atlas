"""Reflect completed Codebook label review for 2018 housing-owner slots."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "audit/housing_exposure_variable_mapping_v1.csv"
REVIEW_PATHS = (
    ROOT / "audit/housing_owner_relation_value_label_review_v1.csv",
    ROOT / "audit/housing_current_owner_relation_labels_2018_v1.csv",
)
REVIEWED_STATUS = (
    "official Codebook response labels reviewed; preserve exact slot-specific categories; "
    "authorized-release route, special codes, household/individual linkage and analysis eligibility still require QA"
)


def apply_status(mapping: pd.DataFrame, reviews: list[pd.DataFrame]) -> tuple[pd.DataFrame, int]:
    """Update only the exact reviewed 2018 fields; fail closed on coverage drift."""
    reviewed = pd.concat(reviews, ignore_index=True)
    keys = set(zip(reviewed["wave"].astype(str), reviewed["code"].str.lower()))
    target = mapping["concept_id"].isin(
        ["household_property_owner_relation_slots", "current_home_owner_relation"]
    ) & mapping["wave"].astype(str).eq("2018")
    target_keys = set(zip(mapping.loc[target, "wave"].astype(str), mapping.loc[target, "code"].str.lower()))
    if len(reviewed) != 224 or len(keys) != 224 or keys != target_keys:
        raise ValueError(f"Reviewed owner-label coverage mismatch: reviews={len(reviewed)}, unique={len(keys)}, targets={len(target_keys)}")
    result = mapping.copy()
    result.loc[target, "mapping_status"] = REVIEWED_STATUS
    return result, int(target.sum())


def main() -> None:
    mapping = pd.read_csv(MAPPING_PATH, dtype=str, encoding="utf-8-sig").fillna("")
    reviews = [pd.read_csv(path, dtype=str, encoding="utf-8-sig").fillna("") for path in REVIEW_PATHS]
    updated, count = apply_status(mapping, reviews)
    updated.to_csv(MAPPING_PATH, index=False, encoding="utf-8-sig")
    print(f"Updated reviewed response-label status for {count} 2018 housing-owner fields; release/route/analysis QA remains pending")


if __name__ == "__main__":
    main()
