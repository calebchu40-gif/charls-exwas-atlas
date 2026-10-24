import importlib.util
import csv
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_balance_measurement_source_review.py"
spec = importlib.util.spec_from_file_location("balance_measurement_source_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class BalanceMeasurementSourceReviewTests(unittest.TestCase):
    def test_official_questionnaire_anchors_exist_for_all_waves(self):
        self.assertEqual(set(review.verify_sources()), {"2011", "2013", "2015"})

    def test_age_graded_full_tandem_protocol_and_separate_routes_are_documented(self):
        semantics, caveat, _ = review.source_note("2015", "balance_full_tandem")
        self.assertIn("30 seconds for age 70 or older", semantics)
        self.assertIn("60 seconds for younger participants", semantics)
        self.assertIn("993", semantics)
        self.assertIn("999", semantics)
        self.assertIn("do not assign zero to unasked", caveat)

    def test_2011_item_identity_is_not_asserted(self):
        self.assertIn("LI* item identifiers", review.source_note("2011", "balance_semi_tandem")[1])
        self.assertIn("unverified", review.source_note("2011", "balance_semi_tandem")[1])

    def test_all_nine_concept_wave_records_are_reviewed(self):
        with (ROOT / "audit/objective_measurement_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        target = [r for r in rows if r["concept_id"] in review.CONCEPTS]
        self.assertEqual(len(target), 9)
        self.assertTrue(all("candidate phenotype only" in r["source_status"] for r in target))
        self.assertTrue(all("do not assign zero to unasked" in r["source_caveat"] for r in target))


if __name__ == "__main__":
    unittest.main()
