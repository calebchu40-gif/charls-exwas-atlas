import json
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Wave4HousingRosterContextReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((ROOT / "site-prototype/dist/catalog_c.json").read_text(encoding="utf-8"))
        cls.by_code = {r["Variable.Name"].lower(): r for r in cls.rows if r["Source.Wave"] == "2018"}
        cls.main_catalog = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
        with (ROOT / "audit/housing_exposure_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.housing_map = list(csv.DictReader(stream))
        with (ROOT / "audit/ep_concept_source_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.concept_map = list(csv.DictReader(stream))
        cls.series = json.loads((ROOT / "audit/charls_atlas_candidate_series_v0.json").read_text(encoding="utf-8"))
        cls.series_by_code = {r["Variable.Name"].lower(): r for r in cls.series if r["waves"] == "2018"}

    def test_property_roster_labels_and_scope_are_explicit(self):
        expected = {f"ha025_w4_{i}_" for i in range(1, 12)}
        rows = {code: self.by_code[code] for code in expected}
        for row in rows.values():
            self.assertEqual(row["epcf"], "c")
            self.assertEqual(row["category"], "source-reviewed context metadata")
            self.assertIn("property-roster location", row["subcategory"])
            self.assertIn("field-level meaning reviewed", row["Candidate.Status"])
            self.assertNotIn("automated keyword discovery only", row["Candidate.Status"])
            self.assertIn("4=Special regions", row["Value.Labels"])
            self.assertIn("property roster position", row["Harmonization.Status"])
            self.assertIn("not automatically the respondent's current residence", row["Harmonization.Status"])
            self.assertNotRegex(row["Value.Labels"], r"\b\d{1,3},\d{3}\b|\b\d{2,}\.\d{1,2}\b")
            self.assertEqual(self.series_by_code[row["Variable.Name"].lower()]["value_labels"], row["Value.Labels"])
            self.assertEqual(self.series_by_code[row["Variable.Name"].lower()]["category"], row["category"])
            self.assertEqual(self.series_by_code[row["Variable.Name"].lower()]["subcategory"], row["subcategory"])

    def test_mortgage_payment_is_continuous_household_measure(self):
        row = self.by_code["ha057_w3"]
        self.assertEqual(row["Value.Labels"], "")
        self.assertEqual(row["Concept.Unit.Candidates"], "10,000 Yuan/month")
        self.assertIn("excludes properties whose mortgage is paid off", row["Harmonization.Status"])
        self.assertIn("not an individual income", row["Harmonization.Status"])

    def test_current_residence_is_distinct_from_property_roster_location(self):
        rows = [r for r in self.main_catalog if r["Source.Wave"] == "2018" and r["Variable.Name"].lower() == "i000_w4_2"]
        self.assertEqual({r["epcf"] for r in rows}, {"e", "c"})
        for row in rows:
            self.assertIn("main respondent's currently occupied house", row["Harmonization.Status"])
            self.assertIn("distinct from HA025_W4[i]", row["Harmonization.Status"])
            self.assertIn("4=Special zone", row["Value.Labels"])
        exposure = next(r for r in rows if r["epcf"] == "e")
        self.assertEqual(exposure["Concept.Mapping.Status"].startswith("official 2018 questionnaire and Codebook reviewed"), True)
        housing = next(r for r in self.housing_map if r["wave"] == "2018" and r["code"] == "i000_w4_2")
        self.assertIn("currently occupied residence", housing["construct"])
        self.assertNotIn("roster fields may repeat", housing["caveat"])
        concept = next(r for r in self.concept_map if r["Wave"] == "2018" and r["Source.Code"] == "i000_w4_2")
        self.assertIn("distinct from HA025_W4[i]", concept["Caveat"])


if __name__ == "__main__":
    unittest.main()
