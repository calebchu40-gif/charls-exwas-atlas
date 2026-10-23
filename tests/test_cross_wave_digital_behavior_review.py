import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CrossWaveDigitalBehaviorReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "social_exposure_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.digital = [row for row in cls.rows if row["domain"] == "internet and digital technology use"]

    def test_legacy_internet_activity_is_kept_distinct_from_direct_screening(self):
        rows = [row for row in self.digital if row["concept_id"] == "internet_use_social_activity"]
        self.assertEqual({row["wave"] for row in rows}, {"2011", "2013", "2015", "2018"})
        self.assertEqual(len(rows), 4)
        self.assertTrue(all("past-month activity checklist" in row["source_label"] for row in rows))
        self.assertTrue(all(not row["value_labels"] for row in rows if row["wave"] != "2018"))
        self.assertTrue(all("do not infer No" in row["value_semantics"] for row in rows if row["wave"] != "2018"))

    def test_2018_followups_have_verified_values_and_routes(self):
        rows = [row for row in self.digital if row["wave"] == "2018"]
        by_code = {row["code"].lower(): row for row in rows}
        self.assertEqual(len(by_code), len(rows))
        for code in ["da056_w3_s1", "da056_w4_1_s1", "da056_w4_2", "da056_w4_3"]:
            self.assertIn(code, by_code)
            self.assertIn("frequencies omitted", by_code[code]["value_label_status"])
            self.assertIn("DA056=10", by_code[code]["value_label_status"])
        self.assertEqual(by_code["da056_w3_s1"]["value_labels"], "0=No; 1=Desktop computer (selected option)")
        self.assertEqual(by_code["da056_w4_2"]["value_labels"], "1=Yes; 2=No")
        self.assertEqual(by_code["da056_w4_4"]["concept_id"], "wechat_moments_posting")
        self.assertIn("conditional on WeChat use", by_code["da056_w4_4"]["value_label_status"])

    def test_wave_2015_device_values_are_not_assumed_from_codebook_option_numbers(self):
        rows = [row for row in self.digital if row["wave"] == "2015" and row["concept_id"].startswith("internet_device_")]
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(row["value_labels"] == "" for row in rows))
        self.assertTrue(all("storage is unresolved" in row["value_label_status"] for row in rows))


if __name__ == "__main__":
    unittest.main()
