import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Wave5PhysicalActivityDurationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.behavior = read_csv(ROOT / "audit/behavior_exposure_variable_mapping_v1.csv")
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        cls.topic = json.loads((ROOT / "site-prototype/dist/behavior_exposures_v1.json").read_text(encoding="utf-8"))
        cls.pairs = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))

    def test_questionnaire_and_codebook_conflict_is_preserved(self):
        questionnaire = (ROOT / "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt").read_text(encoding="utf-8")
        codebook = (ROOT / "sources_official/CHARLS_2020_Codebook_extracted.txt").read_text(encoding="utf-8")
        self.assertIn("DA035", questionnaire)
        self.assertIn("<30 hours", questionnaire)
        self.assertIn("da035_1_", codebook)
        self.assertIn("<30 Minutes", codebook)
        review = (ROOT / "audit/physical_activity_duration_2020_source_review_2026-10-24.md").read_text(encoding="utf-8")
        self.assertIn("DO NOT ANALYZE", review)
        self.assertIn("skip instructions", review)

    def test_field_mapping_withholds_disputed_labels_and_preserves_other_thresholds(self):
        rows = [row for row in self.behavior if row["wave"] == "2020" and row["concept_id"] == "physical_activity_duration"]
        self.assertEqual(len(rows), 9)
        disputed = [row for row in rows if row["code"].startswith("da035_")]
        self.assertEqual(len(disputed), 3)
        for row in disputed:
            self.assertEqual(row["value_labels"], "")
            self.assertIn("DO NOT ANALYZE", row["value_label_status"])
            self.assertIn("30 hours", row["value_semantics"])
            self.assertIn("30 minutes", row["value_semantics"])
        agreed = [row for row in rows if row["code"].startswith(("da034_", "da036_"))]
        self.assertEqual(len(agreed), 6)
        self.assertTrue(all(row["value_labels"] and "routed components" in row["value_semantics"] for row in agreed))

    def test_catalog_and_topic_keep_conflict_without_frequencies(self):
        rows = [row for row in self.catalog if row["Source.Wave"] == "2020" and row["Variable.Name"].lower().startswith("da035_")]
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["Value.Labels"], "")
            self.assertIn("DO NOT ANALYZE", row["Value.Label.Review"])
            self.assertIn("30 hours", row["Concept.Mapping.Caveat"])
            self.assertIn("30 minutes", row["Concept.Mapping.Caveat"])
            self.assertNotIn("Freq.", row["Concept.Mapping.Caveat"])
        concept = next(item for item in self.topic if item["concept_id"] == "physical_activity_duration")
        fields = [item for item in concept["source_fields"] if item["wave"] == "2020" and item["code"].startswith("da035_")]
        self.assertEqual(len(fields), 3)
        self.assertTrue(all("30 hours" in item["value_semantics"] and "30 minutes" in item["value_semantics"] for item in fields))
        wave = self.pairs["waves"]["2020"]
        pair_concept = next(item for item in wave["exposures"] if item["concept_id"] == "physical_activity_duration")
        pair_fields = [item for item in pair_concept["source_fields"] if item["code"].startswith("da035_")]
        self.assertEqual(len(pair_fields), 3)
        self.assertTrue(all("30 minutes" in item["caveat"] or "30 hours" in item["caveat"] for item in pair_fields))


if __name__ == "__main__":
    unittest.main()
