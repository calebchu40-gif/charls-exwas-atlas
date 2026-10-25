import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResidentialHistoryBB004ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_wave = {r["Source.Wave"]: r for r in rows if r["Variable.Name"].lower() == "bb004"}

    def test_2011_conflict_withholds_labels_and_locks_field(self):
        row = self.by_wave["2011"]
        self.assertEqual(row["Value.Labels"], "")
        self.assertIn("identity conflict", row["Value.Label.Review"])
        self.assertIn("HOLD FOR SOURCE VALIDATION", row["Review.Flag"])
        self.assertIn("HOLD FOR SOURCE VALIDATION", row["Candidate.Status"])
        self.assertEqual(row["subcategory"], "residential-history field identity conflict")
        self.assertIn("same county/city", row["Harmonization.Status"])
        self.assertNotIn("DO NOT ANALYZE", row["Harmonization.Status"])

    def test_later_wave_labels_are_wave_specific_and_routed(self):
        for wave in ("2013", "2015", "2018"):
            row = self.by_wave[wave]
            self.assertEqual(row["Value.Labels"], "1=Yes; 2=No")
            self.assertIn("conditional", row["Harmonization.Status"])
            self.assertIn("not current neighborhood quality", row["Harmonization.Status"])
            self.assertIn("question reviewed", row["Candidate.Status"])
            self.assertEqual(row["subcategory"], "residential-history context")
            self.assertNotIn("Freq.", row["Harmonization.Status"])


class ResidentialHistoryBB005ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_wave = {r["Source.Wave"]: r for r in rows if r["Variable.Name"].lower() == "bb005"}

    def test_four_wave_specific_calendar_year_records_are_present(self):
        self.assertEqual(set(self.by_wave), {"2011", "2013", "2015", "2018"})
        for row in self.by_wave.values():
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("statistics omitted", row["Value.Label.Review"])
            self.assertIn("route", row["Harmonization.Status"].lower())

    def test_2018_new_interview_and_address_reference_are_preserved(self):
        note = self.by_wave["2018"]["Harmonization.Status"]
        self.assertIn("XRType=2", note)
        self.assertIn("BB001_W3", note)
        self.assertIn("permanent-address wording", note)

    def test_2011_codebook_label_is_not_overstated(self):
        row = self.by_wave["2011"]
        self.assertEqual(row["Variable.Description"], "Year")
        self.assertIn("Codebook heading is only 'Year'", row["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
