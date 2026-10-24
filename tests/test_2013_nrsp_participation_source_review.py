import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPT = "new_rural_social_pension_participation"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class Wave2NewRuralSocialPensionReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exposure = read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv")
        cls.participation = read_csv(ROOT / "audit/pension_participation_crosswalk_v1.csv")
        cls.index = read_csv(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        cls.pairs = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))

    def test_official_questionnaire_and_codebook_route_checks_are_documented(self):
        review = (ROOT / "audit/new_rural_social_pension_2013_source_review_2026-10-24.md").read_text(encoding="utf-8")
        self.assertIn("1=Yes", review)
        self.assertIn("2=No", review)
        self.assertIn("FN071_W2", review)
        self.assertIn("FN070_W2", review)
        self.assertIn("not claim cross-wave measurement equivalence", review)

    def test_pension_domain_crosswalks_keep_one_exact_wave_two_row(self):
        rows = [r for r in self.exposure if r["wave"] == "2013" and r["code"].lower() == "fn069_w2" and r["concept_id"] == CONCEPT]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["value_labels"], "1=Yes; 2=No")
        self.assertIn("FN071_W2", row["value_semantics"])
        self.assertIn("FN070_W2", row["value_semantics"])
        self.assertIn("cross-wave measurement equivalence", row["caveat"])
        self.assertIn("CHARLS_2013_Questionnaire_extracted.txt", row["official_source"])
        self.assertIn("CHARLS_2013_Codebook_extracted.txt", row["official_source"])
        part = [r for r in self.participation if r["wave"] == "2013" and r["code"].lower() == "fn069_w2" and r["concept_id"] == CONCEPT]
        self.assertEqual(len(part), 1)
        self.assertEqual(part[0]["mapping_status"], row["mapping_status"])

    def test_review_reaches_catalog_index_and_pair_browser_without_frequency_data(self):
        rows = [r for r in self.catalog if r["Source.Wave"] == "2013" and r["Variable.Name"].lower() == "fn069_w2"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Value.Labels"], "1=Yes; 2=No")
        self.assertIn(CONCEPT, rows[0]["candidate_concept_ids"])
        # The general harmonization status remains a family-level caution;
        # the reviewed, exact route belongs in the concept mapping caveat.
        self.assertIn("FN071_W2", rows[0]["concept_mapping_caveats"])
        self.assertIn("FN070_W2", rows[0]["concept_mapping_caveats"])
        mappings = [r for r in self.index if r["Wave"] == "2013" and r["Source.Code"].lower() == "fn069_w2" and r["Concept.ID"] == CONCEPT]
        self.assertEqual(len(mappings), 1)
        self.assertIn("FN071_W2", mappings[0]["Caveat"])
        wave = self.pairs["waves"]["2013"]
        concept = next(x for x in wave["exposures"] if x["concept_id"] == CONCEPT)
        self.assertTrue(any(field["code"].lower() == "fn069_w2" for field in concept["source_fields"]))
        labels = rows[0]["Value.Labels"]
        self.assertNotIn("%", labels)
        self.assertNotIn("OBS", labels)


if __name__ == "__main__":
    unittest.main()
