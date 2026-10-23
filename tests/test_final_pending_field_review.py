import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FinalPendingFieldReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        cls.by_key = {(r["Source.Wave"], r["Variable.Name"].lower()): r for r in cls.rows}

    def test_no_generic_pending_e_value_label_reviews_remain(self):
        pending = [r for r in self.rows if r.get("Value.Label.Review", "").strip().lower() == "not yet reviewed"]
        self.assertEqual(pending, [])

    def test_continuous_household_amounts_have_units_and_no_categories(self):
        for code in ("ge010_4", "ge010_6", "ge010_7"):
            row = self.by_key[("2011", code)]
            self.assertIn("Yuan", row["Unit"])
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("numeric summary", row["Value.Label.Review"])

    def test_rental_status_codes_are_wave_specific_and_sourced(self):
        for key in (("2018", "ha064"), ("2020", "ge014")):
            row = self.by_key[key]
            for label in ("1=Yes", "2=No", "997=", "999="):
                self.assertIn(label, row["Value.Labels"])
            self.assertIn("official", row["Value.Label.Source"])

    def test_conflict_and_analysis_locks_are_preserved(self):
        gf015 = self.by_key[("2020", "gf015_s4")]
        gf016 = self.by_key[("2020", "gf016_s8")]
        self.assertIn("0=No; 4=Yes", gf015["Value.Labels"])
        self.assertIn("DO NOT ANALYZE", gf015["Harmonization.Status"])
        self.assertIn("DO NOT ANALYZE", gf016["Harmonization.Status"])
        self.assertIn("conflict", gf016["Value.Label.Review"])
        self.assertEqual(gf016["Value.Labels"], "")

    def test_occupation_classifications_are_not_response_categories(self):
        for code in ("fh015_gb", "fh015_isco"):
            row = self.by_key[("2011", code)]
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("classification code", row["Value.Label.Review"])


if __name__ == "__main__":
    unittest.main()
