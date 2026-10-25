import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "apply_2011_chronic_treatment_storage_review",
    ROOT / "scripts/apply_2011_chronic_treatment_storage_review.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ChronicTreatmentStorageReviewTests(unittest.TestCase):
    def test_exact_32_2011_fields_are_targeted(self):
        codes = {f"da010_{disease}_s{option}" for disease in MODULE.DISEASES for option in MODULE.OPTIONS}
        self.assertEqual(codes, MODULE.EXPECTED)
        self.assertTrue(all(MODULE.is_target("2011", code) for code in codes))
        self.assertFalse(MODULE.is_target("2013", "da010_2_s4"))
        self.assertFalse(MODULE.is_target("2011", "da010_1_s1"))

    def test_site_review_preserves_lock_and_is_idempotent(self):
        row = {"Review.Flag": f"preserve existing review flag; {MODULE.NOTE}", "Concept.Mapping.Caveat": "existing route caveat"}
        MODULE.apply_site_row(row)
        once = dict(row)
        MODULE.apply_site_row(row)
        self.assertEqual(row, once)
        self.assertNotIn("DO NOT ANALYZE", row.get("Candidate.Status", ""))
        self.assertIn("DO NOT ANALYZE", row["Value.Label.Review"])
        self.assertIn("unselected storage", row["Value.Label.Review"])
        self.assertEqual(row["Review.Flag"], "preserve existing review flag")
        self.assertIn(MODULE.NOTE, row["Concept.Mapping.Caveat"])

    def test_field_json_review_uses_same_wave_specific_status(self):
        row = {
            "Review.Flag": "preserve this review flag",
            "Concept.Mapping.Caveat": "existing route caveat",
        }
        MODULE.apply_site_row(row)
        self.assertEqual(row["Review.Flag"], "preserve this review flag")
        self.assertIn("unselected storage", row["Value.Label.Review"])
        self.assertIn("DO NOT ANALYZE", row["Concept.Mapping.Status"])


if __name__ == "__main__":
    unittest.main()
