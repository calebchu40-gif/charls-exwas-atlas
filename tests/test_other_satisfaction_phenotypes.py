import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OtherSatisfactionPhenotypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit" / "other_satisfaction_phenotypes_crosswalk_v1.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.crosswalk = list(csv.DictReader(stream))
        with (ROOT / "audit" / "charls_atlas_candidate_fields_v0.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            cls.catalog = list(csv.DictReader(stream))

    def test_distinct_concepts_keep_official_wave_coverage(self):
        expected = {
            "life_satisfaction": {"2011", "2013", "2015", "2018"},
            "health_satisfaction": {"2015", "2018"},
            "children_relationship_satisfaction": {"2015", "2018"},
        }
        for concept, waves in expected.items():
            rows = [r for r in self.crosswalk if r["concept_id"] == concept]
            self.assertEqual({r["wave"] for r in rows}, waves)
            self.assertTrue(all(r["code"] for r in rows))
            candidate_rows = [
                r for r in self.catalog
                if r["Concept.ID.Candidates"] == concept and r["epcf"] == "p"
            ]
            self.assertEqual({r["Source.Wave"] for r in candidate_rows}, waves)
            self.assertTrue(all(r["category"] == "social wellbeing" for r in candidate_rows))

    def test_life_and_health_satisfaction_keep_five_ordered_labels(self):
        for row in self.crosswalk:
            if row["concept_id"] in {"life_satisfaction", "health_satisfaction"}:
                self.assertIn("1=Completely satisfied", row["value_labels"])
                self.assertIn("5=Not at all satisfied", row["value_labels"])
                self.assertIn("no frequencies copied", row["value_label_status"])

    def test_child_relationship_item_preserves_route_and_nonordinal_status(self):
        rows = [r for r in self.crosswalk if r["concept_id"] == "children_relationship_satisfaction"]
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIn("在世子女", row["caveat"])
            self.assertIn("6=No child now", row["value_labels"])
            self.assertIn("separate non-ordinal status", row["value_labels"])
        for wave in ("2015", "2018"):
            questionnaire = (ROOT / "sources_official" / f"CHARLS_{wave}_Questionnaire_extracted.txt").read_text(
                encoding="utf-8", errors="replace"
            )
            self.assertIn("DC044_W3", questionnaire)
            self.assertIn("6. No child now", questionnaire)


if __name__ == "__main__":
    unittest.main()
