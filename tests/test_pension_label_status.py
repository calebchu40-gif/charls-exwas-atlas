import importlib.util
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "apply_pension_label_status",
    ROOT / "scripts/apply_pension_label_status.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PensionLabelStatusTests(unittest.TestCase):
    def test_only_explicitly_labeled_rows_advance(self):
        mapping = pd.read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        original_locked = int(mapping.mapping_status.str.contains("DO NOT ANALYZE").sum())
        updated, count = MODULE.apply_status(mapping)
        self.assertGreater(count, 0)
        changed = updated.mapping_status.eq(MODULE.REVIEWED_STATUS)
        self.assertEqual(int(changed.sum()), count)
        self.assertTrue(updated.loc[changed, "value_labels"].ne("").all())
        self.assertTrue(updated.loc[changed, "mapping_status"].str.contains("analysis eligibility remain to be validated").all())
        self.assertEqual(original_locked, int(updated.mapping_status.str.contains("DO NOT ANALYZE").sum()))
        self.assertFalse(updated.loc[~changed, "mapping_status"].eq(MODULE.REVIEWED_STATUS).any())

    def test_status_application_is_idempotent(self):
        mapping = pd.read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        reviews, _ = MODULE.apply_status(mapping)
        repeated, _ = MODULE.apply_status(reviews)
        self.assertTrue(reviews.equals(repeated))


if __name__ == "__main__":
    unittest.main()
