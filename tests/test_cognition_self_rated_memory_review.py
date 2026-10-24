import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"2011": "dc004", "2013": "dc004", "2015": "dc004", "2018": "dc004", "2020": "dc006"}


class SelfRatedMemoryReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/cognition_item_variable_mapping_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.mapping = list(csv.DictReader(stream))
        cls.topic = next(x for x in json.loads((ROOT / "site-prototype/dist/cognition_items_v1.json").read_text(encoding="utf-8")) if x["concept_id"] == "cog_subjective_memory")
        with (ROOT / "audit/charls_atlas_candidate_fields_v0.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.catalog = list(csv.DictReader(stream))

    def test_five_wave_codes_and_direction_are_source_reviewed(self):
        rows = [x for x in self.mapping if x["concept_id"] == "cog_subjective_memory"]
        self.assertEqual({x["wave"]: x["code"].lower() for x in rows}, TARGETS)
        for row in rows:
            self.assertIn("1–5 ordinal direction reviewed", row["mapping_status"])
            self.assertIn("1=Excellent", row["value_labels"])
            self.assertIn("5=Poor", row["value_labels"])
            self.assertIn("require authorized-release dictionary QA", row["value_label_status"])
        self.assertIn("997=Don't Know", next(x for x in rows if x["wave"] == "2020")["value_labels"])

    def test_topic_and_field_catalog_keep_non_analysis_caveat(self):
        self.assertIn("not an objective memory-test score", self.topic["caveat"])
        self.assertEqual(len(self.topic["source_fields"]), 5)
        rows = [x for x in self.catalog if x["Concept.ID.Candidates"] == "cog_subjective_memory"]
        self.assertEqual({x["Source.Wave"]: x["Variable.Name"].lower() for x in rows}, TARGETS)
        self.assertTrue(all("not an objective memory-test score" in x["Harmonization.Status"] for x in rows))


if __name__ == "__main__":
    unittest.main()
