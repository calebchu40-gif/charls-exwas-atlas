import importlib.util
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "apply_housing_owner_relation_label_status",
    ROOT / "scripts/apply_housing_owner_relation_label_status.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HousingOwnerRelationStatusTests(unittest.TestCase):
    def test_only_exactly_reviewed_2018_owner_fields_advance_status(self):
        mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        reviews = [
            pd.read_csv(path, dtype=str).fillna("")
            for path in MODULE.REVIEW_PATHS
        ]
        updated, count = MODULE.apply_status(mapping, reviews)
        self.assertEqual(count, 224)
        target = updated.concept_id.isin([
            "household_property_owner_relation_slots", "current_home_owner_relation"
        ]) & updated.wave.astype(str).eq("2018")
        self.assertEqual(int(target.sum()), 224)
        self.assertTrue(updated.loc[target, "mapping_status"].eq(MODULE.REVIEWED_STATUS).all())
        self.assertTrue(updated.loc[target, "mapping_status"].str.contains("analysis eligibility still require QA").all())
        self.assertTrue(updated.loc[target, "caveat"].str.contains("special codes", case=False).all())
        untouched = updated.loc[~target]
        original = mapping.loc[~target]
        self.assertTrue(untouched["mapping_status"].reset_index(drop=True).equals(original["mapping_status"].reset_index(drop=True)))

    def test_status_application_is_idempotent(self):
        mapping = pd.read_csv(ROOT / "audit/housing_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        reviews = [pd.read_csv(path, dtype=str).fillna("") for path in MODULE.REVIEW_PATHS]
        once, _ = MODULE.apply_status(mapping, reviews)
        twice, _ = MODULE.apply_status(once, reviews)
        self.assertTrue(once.equals(twice))


if __name__ == "__main__":
    unittest.main()
