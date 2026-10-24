import csv
import hashlib
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

    def test_authoritative_chinese_sources_resolve_translation_and_route(self):
        questionnaire = (ROOT / "sources_official/CHARLS_2020_Questionnaire_Chinese_extracted.txt").read_text(encoding="utf-8")
        english = (ROOT / "sources_official/CHARLS_2020_Questionnaire_English_extracted.txt").read_text(encoding="utf-8")
        codebook = (ROOT / "sources_official/CHARLS_2020_Codebook_extracted.txt").read_text(encoding="utf-8")
        review = (ROOT / "audit/physical_activity_duration_2020_source_review_2026-10-24.md").read_text(encoding="utf-8")
        self.assertIn("DA035", questionnaire)
        self.assertIn("<30 分钟", questionnaire)
        self.assertIn(">=30 分", questionnaire)
        self.assertIn("<30 hours", english)
        self.assertIn("<30 Minutes", codebook)
        self.assertIn("DA034` response `<2 hours` routes to `DA035`", review)
        self.assertIn("English questionnaire prints “30 hours”", review)
        expected = {
            "CHARLS_2020_Questionnaire_Chinese.pdf": "307FB0F902E76FD08E07222324A4CE5FA24FEC99",
            "CHARLS_2020_Flowchart_Chinese.pdf": "83DA535E9542AD6974FF3474B7FE0FCDED0ED0BD",
        }
        for filename, sha1 in expected.items():
            digest = hashlib.sha1((ROOT / "sources_official" / filename).read_bytes()).hexdigest().upper()
            self.assertEqual(digest, sha1)

    def test_all_three_da035_fields_have_reviewed_codebook_labels_and_release_qa_caveat(self):
        rows = [row for row in self.behavior if row["wave"] == "2020" and row["concept_id"] == "physical_activity_duration"]
        self.assertEqual(len(rows), 9)
        disputed = [row for row in rows if row["code"].startswith("da035_")]
        self.assertEqual(len(disputed), 3)
        for row in disputed:
            self.assertEqual(row["value_labels"], "1=<30 minutes; 2=≥30 minutes")
            self.assertIn("translation discrepancy resolved", row["value_label_status"])
            self.assertIn("authorized-file QA", row["value_label_status"])
            self.assertIn("conditional denominator", row["note"])
            self.assertIn("CHARLS_2020_Questionnaire_Chinese.pdf", row["value_label_source"])
            self.assertNotIn("DO NOT ANALYZE", row["value_label_status"])
            self.assertNotIn("frequency", row["value_label_source"].lower())
        self.assertTrue(all("DA034" in row["value_semantics"] and "DA036" in row["value_semantics"] for row in rows))

    def test_public_catalog_and_browsers_show_labels_and_conditional_route_without_frequencies(self):
        rows = [row for row in self.catalog if row["Source.Wave"] == "2020" and row["Variable.Name"].lower().startswith("da035_")]
        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertEqual(row["Value.Labels"], "1=<30 minutes; 2=≥30 minutes")
            self.assertEqual(row["Value.Label.Review"], "officially reviewed")
            self.assertIn("DA034<2 hours", row["Concept.Mapping.Caveat"])
            self.assertNotIn("Freq.", row["Concept.Mapping.Caveat"])
        concept = next(item for item in self.topic if item["concept_id"] == "physical_activity_duration")
        fields = [item for item in concept["source_fields"] if item["wave"] == "2020" and item["code"].startswith("da035_")]
        self.assertEqual(len(fields), 3)
        self.assertTrue(all("30 minutes" in item["value_semantics"] for item in fields))
        self.assertTrue(all("DA034<2 hours" in item["value_semantics"] for item in fields))
        wave = self.pairs["waves"]["2020"]
        pair_concept = next(item for item in wave["exposures"] if item["concept_id"] == "physical_activity_duration")
        pair_fields = [item for item in pair_concept["source_fields"] if item["code"].startswith("da035_")]
        self.assertEqual(len(pair_fields), 3)
        self.assertTrue(all("30 minutes" in item["caveat"] and "DA034<2 hours" in item["caveat"] for item in pair_fields))
        self.assertNotIn("DO NOT ANALYZE", json.dumps([rows, fields, pair_fields], ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
