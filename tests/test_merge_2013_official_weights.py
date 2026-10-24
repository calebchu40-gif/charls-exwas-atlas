import sys
import hashlib
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from merge_2013_official_weights import (  # noqa: E402
    EXPECTED_OFFICIAL_WEIGHTS_SHA1,
    merge_official_weights,
    verify_official_weights_sha1,
)


class OfficialWeightMergeTests(unittest.TestCase):
    def setUp(self):
        self.prepared = pd.DataFrame({"ID": ["001", "002"], "age": [60, 72],
                                      "INDV_weight": [1.0, 2.0]})
        self.weights = pd.DataFrame({"ID": ["001", "002"], "crosssection": [1, 0],
                                     "longitudinal": [0, 1], "INDV_weight": [1.0, 2.0],
                                     "Biomarker_weight": [0.5, 0.6]})

    def test_adds_flags_keeps_order_and_reports_aggregates(self):
        merged, labels, qa = merge_official_weights(self.prepared, self.weights)
        self.assertEqual(merged["ID"].tolist(), ["001", "002"])
        self.assertEqual(merged["crosssection"].tolist(), [1, 0])
        self.assertEqual(merged["longitudinal"].tolist(), [0, 1])
        self.assertEqual(merged["INDV_weight"].tolist(), [1.0, 2.0])
        self.assertEqual(qa["match_rate"], 1.0)
        self.assertNotIn("001", str(qa))
        self.assertNotIn("002", str(qa))

    def test_missing_required_flags_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "missing required flags"):
            merge_official_weights(self.prepared, self.weights.drop(columns="crosssection"))

    def test_duplicate_or_missing_ids_fail_closed(self):
        duplicate = pd.concat([self.weights, self.weights.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "unique"):
            merge_official_weights(self.prepared, duplicate)
        missing = self.weights.copy()
        missing.loc[0, "ID"] = None
        with self.assertRaisesRegex(ValueError, "nonmissing and unique"):
            merge_official_weights(self.prepared, missing)

    def test_existing_weight_conflict_fails_closed(self):
        conflicting = self.weights.copy()
        conflicting.loc[0, "INDV_weight"] = 88.0
        with self.assertRaisesRegex(ValueError, "values conflict"):
            merge_official_weights(self.prepared, conflicting)

    def test_equal_weight_values_with_integer_float_storage_are_accepted(self):
        mixed_storage = self.weights.copy()
        mixed_storage["INDV_weight"] = [1, 2]
        merged, _, _ = merge_official_weights(self.prepared, mixed_storage)
        self.assertEqual(merged["INDV_weight"].tolist(), [1.0, 2.0])

    def test_incomplete_coverage_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Not all prepared respondents matched"):
            merge_official_weights(self.prepared, self.weights.iloc[[0]])

    def test_official_weight_intake_requires_matching_release_hash(self):
        self.assertEqual(EXPECTED_OFFICIAL_WEIGHTS_SHA1, "22c4fc89df2e55fa8faf051e88830eebe0e035c0")
        payload = b"synthetic test file; not CHARLS data"
        expected = hashlib.sha1(payload).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Weights.dta"
            path.write_bytes(payload)
            self.assertEqual(verify_official_weights_sha1(path, expected), expected)
            with self.assertRaisesRegex(ValueError, "does not match the official"):
                verify_official_weights_sha1(path, "0" * 40)


if __name__ == "__main__":
    unittest.main()
