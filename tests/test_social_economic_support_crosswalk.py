import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SocialEconomicSupportCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/social_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.rows = list(csv.DictReader(handle))
        with (ROOT / "audit/raw_variable_catalog_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.raw = {(r["wave"], r["variable"].lower(), r["module"].lower()) for r in csv.DictReader(handle)}
        cls.support = [r for r in cls.rows if r["concept_id"].startswith("economic_support_")]

    def test_six_distinct_transfer_directions_and_relationship_groups_are_kept(self):
        concepts = {r["concept_id"] for r in self.support}
        self.assertEqual(concepts, {
            "economic_support_received_parents",
            "economic_support_received_parents_in_law",
            "economic_support_received_children",
            "economic_support_provided_parents",
            "economic_support_provided_parents_in_law",
            "economic_support_provided_children",
        })

    def test_every_mapped_field_exists_in_wave_specific_raw_catalog(self):
        for row in self.support:
            self.assertIn((row["wave"], row["code"].lower(), row["module"].lower()), self.raw)
            self.assertIn("Questionnaire_extracted.txt", row["questionnaire_source"])
            self.assertIn("Codebook_extracted.txt", row["value_label_source"])

    def test_no_later_wave_inlaw_equivalence_is_inferred(self):
        for row in self.support:
            if row["concept_id"].endswith("parents_in_law"):
                self.assertIn(row["wave"], {"2011", "2013"})

    def test_amount_and_2011_source_discrepancies_remain_explicit(self):
        for row in self.support:
            self.assertIn("Bracket min/max follow-ups are ranges", row["value_semantics"])
        baseline = [r for r in self.support if r["wave"] == "2011"]
        self.assertTrue(baseline)
        self.assertTrue(all("discrep" in r["caveat"].lower() for r in baseline))


if __name__ == "__main__":
    unittest.main()
