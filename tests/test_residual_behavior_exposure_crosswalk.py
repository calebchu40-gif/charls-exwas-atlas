import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ResidualBehaviorExposureCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "audit" / "residual_behavior_exposure_crosswalk_v1.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.sleep = {
            row["code"].lower(): row
            for row in cls.rows
            if row["concept_id"] == "previous_day_sleep_schedule"
        }

    def test_sleep_timing_is_limited_to_the_2013_previous_day_recall(self):
        self.assertEqual(len(self.sleep), 10)
        self.assertTrue(all(row["wave"] == "2013" for row in self.sleep.values()))
        self.assertTrue(all("yesterday" in row["value_semantics"] for row in self.sleep.values()))
        self.assertTrue(all("not usual sleep timing" in row["caveat"] for row in self.sleep.values()))
        self.assertTrue(all("no established temporal direction" in row["caveat"] for row in self.sleep.values()))

    def test_split_time_components_preserve_am_and_pm_rows(self):
        for code in ("wb03", "wb04"):
            self.assertEqual(self.sleep[code]["value_labels"], "1=AM; 2=PM (official codebook response codes)")
            for suffix in ("_1", "_2"):
                self.assertIn("AM-row", self.sleep[code + suffix]["value_labels"])
            for suffix in ("_3", "_4"):
                self.assertIn("PM-row", self.sleep[code + suffix]["value_labels"])
        self.assertTrue(all("verify release storage" in row["value_labels"] for code, row in self.sleep.items() if code not in {"wb03", "wb04"}))
        self.assertTrue(all("verify released-file storage" in row["caveat"] for row in self.sleep.values()))

    def test_public_wave_catalog_receives_the_component_notes(self):
        path = ROOT / "site-prototype" / "dist" / "catalog_e.json"
        with path.open(encoding="utf-8") as stream:
            public_rows = __import__("json").load(stream)
        public_sleep = {
            row["Variable.Name"].lower(): row
            for row in public_rows
            if "previous_day_sleep_schedule" in row.get("candidate_concept_ids", "")
        }
        self.assertEqual(set(public_sleep), set(self.sleep))
        self.assertIn("AM-row component", public_sleep["wb03_1"]["Value.Labels"])
        self.assertIn("PM-row component", public_sleep["wb03_3"]["Value.Labels"])
        self.assertIn("verify released-file storage", public_sleep["wb03_1"]["harmonization_status"])


if __name__ == "__main__":
    unittest.main()
