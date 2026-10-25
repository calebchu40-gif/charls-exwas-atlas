import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class PensionReceiptDateReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv")
        cls.crosswalk = read_csv(ROOT / "audit/ep_concept_source_crosswalk_v1.csv")
        cls.labels = read_csv(ROOT / "audit/pension_codebook_value_labels_v1.csv")
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_review_has_exact_wave_counts_and_keeps_release_caveats(self):
        rows = [r for r in self.mapping if r["concept_id"] == "pension_benefit_start_date_components" and r["wave"] in {"2013", "2018"}]
        self.assertEqual({w: sum(r["wave"] == w for r in rows) for w in ("2013", "2018")}, {"2013": 22, "2018": 14})
        locked = {(r["wave"], r["code"].lower()): r for r in rows if r["mapping_status"].startswith("DO NOT ANALYZE")}
        self.assertEqual(set(locked), {("2013", "fn081_w2_2"), ("2013", "fn095_w2_1"), ("2013", "fn095_w2_2")})
        self.assertIn("repeats the year subfield identifier", locked[("2013", "fn081_w2_2")]["mapping_status"])
        self.assertIn("No Observations", locked[("2013", "fn095_w2_1")]["mapping_status"])
        self.assertIn("month not remembered", next(r for r in rows if r["wave"] == "2013" and r["code"].lower() == "fn041_w2_2")["unit"])

    def test_source_review_is_synced_to_public_crosswalk_and_catalog(self):
        key = ("2013", "fn081_w2_2")
        mapping = next(r for r in self.mapping if (r["wave"], r["code"].lower()) == key)
        source = next(r for r in self.crosswalk if (r["Wave"], r["Source.Code"].lower()) == key and r["Concept.ID"] == "pension_benefit_start_date_components")
        self.assertEqual(source["Mapping.Status"], mapping["mapping_status"])
        self.assertIn("do not relabel from inference", source["Caveat"])
        catalog = next(r for r in self.catalog if r["Source.Wave"] == key[0] and r["Variable.Name"].lower() == key[1])
        self.assertIn("pension_benefit_start_date_components", catalog["candidate_concept_ids"])
        self.assertIn("FN081", catalog["concept_mapping_caveats"].upper())

    def test_codebook_label_audit_matches_review_without_frequencies(self):
        rows = [r for r in self.labels if r["wave"] == "2013" and r["code"].lower() in {"fn081_w2_2", "fn095_w2_1", "fn095_w2_2"}]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all("DO NOT ANALYZE" in r["value_label_status"] for r in rows))
        self.assertTrue(all("%" not in r["value_labels"] for r in rows))

    def test_2018_fn003_month_is_questionnaire_only_in_public_crosswalk(self):
        questionnaire = (ROOT / "sources_official/CHARLS_2018_Questionnaire_extracted.txt").read_text(encoding="utf-8", errors="replace")
        codebook = (ROOT / "sources_official/CHARLS_2018_Codebook_extracted.txt").read_text(encoding="utf-8", errors="replace")
        self.assertIn("FN003_W2_2", questionnaire)
        self.assertNotIn("fn003_w2_2", codebook.lower())
        fields = {
            r["code"].lower()
            for r in self.mapping
            if r["wave"] == "2018"
            and r["concept_id"] == "pension_benefit_start_date_components"
            and "fn003_w2" in r["code"].lower()
        }
        self.assertEqual(fields, {f"fn003_w2_1_{i}_" for i in range(1, 5)})


if __name__ == "__main__":
    unittest.main()
