import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Wave4HousingRosterContextReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_code = {r["Variable.Name"].lower(): r for r in cls.rows if r["Source.Wave"] == "2018"}
        cls.series = json.loads((ROOT / "audit/charls_atlas_candidate_series_v0.json").read_text(encoding="utf-8"))
        cls.series_by_code = {r["Variable.Name"].lower(): r for r in cls.series if r["waves"] == "2018"}

    def test_property_roster_labels_and_scope_are_explicit(self):
        expected = {f"ha025_w4_{i}_" for i in range(1, 12)}
        rows = {code: self.by_code[code] for code in expected}
        for row in rows.values():
            self.assertEqual(row["epcf"], "c")
            self.assertIn("4=Special regions", row["Value.Labels"])
            self.assertIn("property roster position", row["Harmonization.Status"])
            self.assertIn("not automatically the respondent's current residence", row["Harmonization.Status"])
            self.assertNotRegex(row["Value.Labels"], r"\b\d{1,3},\d{3}\b|\b\d{2,}\.\d{1,2}\b")
            self.assertEqual(self.series_by_code[row["Variable.Name"].lower()]["value_labels"], row["Value.Labels"])

    def test_mortgage_payment_is_continuous_household_measure(self):
        row = self.by_code["ha057_w3"]
        self.assertEqual(row["Value.Labels"], "")
        self.assertEqual(row["Concept.Unit.Candidates"], "10,000 Yuan/month")
        self.assertIn("excludes properties whose mortgage is paid off", row["Harmonization.Status"])
        self.assertIn("not an individual income", row["Harmonization.Status"])


if __name__ == "__main__":
    unittest.main()
