import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ResidentialHistoryBB003ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_wave = {r["Source.Wave"]: r for r in rows if r["Variable.Name"].lower() == "bb003"}

    def test_four_wave_specific_records_exist_without_response_categories(self):
        self.assertEqual(set(self.by_wave), {"2011", "2013", "2015", "2018"})
        for row in self.by_wave.values():
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("statistics omitted", row["Value.Label.Review"])
            self.assertIn("BB005", row["Harmonization.Status"])

    def test_2015_route_and_2018_new_interview_restriction_are_explicit(self):
        self.assertIn("BB001_W3 is not 1 or XRType=NEWIW", self.by_wave["2015"]["Harmonization.Status"])
        self.assertIn("XRType=2", self.by_wave["2018"]["Harmonization.Status"])

    def test_2018_reference_is_distinguished_from_earlier_waves(self):
        self.assertIn("current address BB001_W3", self.by_wave["2018"]["Harmonization.Status"])
        self.assertIn("permanent address's county/city/district", self.by_wave["2011"]["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
