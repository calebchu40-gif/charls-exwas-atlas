import csv
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/apply_objective_measurement_protocol_review.py"
spec = importlib.util.spec_from_file_location("objective_protocol_review", MODULE_PATH)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ObjectiveMeasurementProtocolReviewTests(unittest.TestCase):
    def test_official_2011_manual_is_archived_and_extracted(self):
        self.assertTrue((ROOT / "sources_official/CHARLS_2011_Physical_Examination_Questionnaire_official.doc").is_file())
        self.assertTrue((ROOT / review.MANUAL_2011).is_file())
        review.apply()

    def test_crosswalk_keeps_2011_code_difference_and_2015_height_component(self):
        review.apply()
        with review.CSV_PATH.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        qa = next(r for r in rows if r["concept_id"] == "bp_recent_pretest_behavior" and r["wave"] == "2011")
        self.assertIn("LI875", qa["value_semantics"])
        self.assertIn("QA017", qa["value_semantics"])
        self.assertIn("not habitual behavior", qa["caveat"])
        chair11 = next(r for r in rows if r["concept_id"] == "chair_stand_test_chair_setup" and r["wave"] == "2011")
        self.assertIn("LI007", chair11["value_semantics"])
        self.assertIn("module/item-sequence crosswalk reviewed", chair11["mapping_status"])
        self.assertIn("QH005=Times", chair11["value_semantics"])
        self.assertIn("QI002 is the separate respondent standing-height field", chair11["value_semantics"])
        self.assertEqual("cm", chair11["unit"])
        self.assertIn("no response values or Codebook frequencies are inferred", chair11["caveat"])
        chair15 = next(r for r in rows if r["concept_id"] == "chair_stand_test_chair_setup" and r["wave"] == "2015" and r["code"] == "qh006_1")
        self.assertIn("QH006=Other chair route", chair15["caveat"])
        self.assertIn("centimeters", chair15["value_semantics"])


if __name__ == "__main__":
    unittest.main()
