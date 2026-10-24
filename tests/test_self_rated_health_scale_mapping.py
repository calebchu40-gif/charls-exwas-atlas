import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SelfRatedHealthScaleMappingTests(unittest.TestCase):
    def test_early_wave_fields_are_grouped_by_response_scale(self):
        with (ROOT / "audit/health_symptom_variable_mapping_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            rows = list(csv.DictReader(stream))
        by_key = {(r["wave"], r["code"].lower()): r for r in rows}

        for wave in ("2011", "2013", "2015"):
            for code in ("da001", "da080"):
                row = by_key[(wave, code)]
                self.assertEqual(row["concept_id"], "self_rated_health_excellent_poor")
                self.assertIn("1=Excellent", row["value_labels"])
            for code in ("da002", "da079"):
                row = by_key[(wave, code)]
                self.assertEqual(row["concept_id"], "self_rated_health_very_good_very_poor")
                self.assertIn("1=Very good", row["value_labels"])

    def test_later_wave_self_rated_health_uses_very_good_scale(self):
        with (ROOT / "audit/health_symptom_variable_mapping_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            rows = list(csv.DictReader(stream))
        by_key = {(r["wave"], r["code"].lower()): r for r in rows}
        for key in (("2018", "da002"), ("2020", "da001")):
            row = by_key[key]
            self.assertEqual(row["concept_id"], "self_rated_health_very_good_very_poor")
            self.assertIn("1=Very good", row["value_labels"])


if __name__ == "__main__":
    unittest.main()
