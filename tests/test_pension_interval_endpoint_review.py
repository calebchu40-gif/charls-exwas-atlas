import csv
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENDPOINTS = {
    "2011": {"fn005_a", "fn005_b", "fn008_a", "fn008_b", "fn014_a", "fn014_b", "fn019_a", "fn019_b", "fn023_a", "fn023_b", "fn037_a", "fn037_b"},
    "2013": {"fn035_w2_bracketbracket_min", "fn035_w2_bracketbracket_max"},
    "2015": {"fn035_w2_bracket_min", "fn035_w2_bracket_max"},
}


class PensionIntervalEndpointReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.fields = list(csv.DictReader(handle))
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_sixteen_source_fields_are_reviewed_as_interval_endpoints(self):
        expected = {(wave, code) for wave, codes in ENDPOINTS.items() for code in codes}
        rows = [r for r in self.fields if (r.get("Source.Wave"), r.get("Variable.Name", "").lower()) in expected]
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertIn("not a point estimate", row["Candidate.Status"])
            self.assertEqual(row["Value.Labels"], "")
            self.assertTrue(any(term in row["Unit"] for term in ("interval endpoint", "interval bound", "bracket endpoint")))
            self.assertIn("CHARLS_", row["Value.Label.Source"])

    def test_2013_string_and_2015_summary_are_not_misrepresented_as_categories(self):
        rows = [r for r in self.catalog if r.get("Source.Wave") in {"2013", "2015"} and r.get("Variable.Name", "").lower() in ENDPOINTS[r.get("Source.Wave", "")]]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("bracket endpoint", row["Value.Label.Review"])
            self.assertTrue(any(term in row["Harmonization.Status"] for term in ("string", "summary")))

    def test_no_2011_summary_extrema_are_treated_as_valid_ranges(self):
        rows = [r for r in self.catalog if r.get("Source.Wave") == "2011" and r.get("Variable.Name", "").lower() in ENDPOINTS["2011"]]
        self.assertEqual(len(rows), 12)
        self.assertTrue(all("not analytic cutoffs" in r["Harmonization.Status"] for r in rows))


if __name__ == "__main__":
    unittest.main()
