import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class AlcoholHistorySourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = read_csv(ROOT / "audit/behavior_exposure_variable_mapping_v1.csv")
        cls.catalog = json.loads((ROOT / "site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))
        cls.topic = json.loads((ROOT / "site-prototype/dist/behavior_exposures_v1.json").read_text(encoding="utf-8"))
        cls.pairs = json.loads((ROOT / "site-prototype/dist/candidate_pair_explorer_v1.json").read_text(encoding="utf-8"))
        cls.review = (ROOT / "audit/alcohol_history_source_review_2026-10-25.md").read_text(encoding="utf-8")

    def test_official_questions_and_codebooks_support_wave_specific_labels_and_routes(self):
        cases = {
            "2011": ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "CHARLS_2011_Codebook_extracted.txt"),
            "2013": ("CHARLS_2013_Questionnaire_extracted.txt", "CHARLS_2013_Codebook_extracted.txt"),
            "2015": ("CHARLS_2015_Questionnaire_extracted.txt", "CHARLS_2015_Codebook_extracted.txt"),
            "2018": ("CHARLS_2018_Questionnaire_extracted.txt", "CHARLS_2018_Codebook_extracted.txt"),
        }
        for questionnaire, codebook in cases.values():
            q = (ROOT / "sources_official" / questionnaire).read_text(encoding="utf-8", errors="replace").lower()
            cb = (ROOT / "sources_official" / codebook).read_text(encoding="utf-8", errors="replace").lower()
            self.assertIn("da069", q)
            self.assertIn("never had a drink", q)
            self.assertIn("used to drink less than once a month", q)
            self.assertIn("used to drink more than once a month", q)
            self.assertIn("da069", cb)
            self.assertIn("never had a drink", cb)
            self.assertIn("used to drink less than once a month", cb)
            self.assertIn("used to drink more than once a month", cb)
        self.assertIn("ZDA069", self.review)
        self.assertIn("not current past-year drinking", self.review)
        self.assertIn("routes past the later drinking-history questions", self.review)

    def test_morning_drink_scope_is_only_the_documented_2011_2013_route(self):
        for questionnaire, codebook in [
            ("CHARLS_2011_Baseline_Household_Questionnaire_extracted.txt", "CHARLS_2011_Codebook_extracted.txt"),
            ("CHARLS_2013_Questionnaire_extracted.txt", "CHARLS_2013_Codebook_extracted.txt"),
        ]:
            q = (ROOT / "sources_official" / questionnaire).read_text(encoding="utf-8", errors="replace").lower()
            cb = (ROOT / "sources_official" / codebook).read_text(encoding="utf-8", errors="replace").lower()
            self.assertIn("da078", q)
            self.assertIn("in the last year", q)
            self.assertIn("steady your", q)
            self.assertIn("da078", cb)
            self.assertIn("taking a drink first thing", cb)
        self.assertIn("not a population-wide item", self.review)
        self.assertIn("not extended to unlisted waves", self.review)

    def test_reviewed_labels_and_caveats_reach_catalog_and_pair_browser(self):
        histories = [r for r in self.mapping if r["concept_id"] == "alcohol_history"]
        self.assertEqual({r["wave"] for r in histories}, {"2011", "2013", "2015", "2018"})
        history_labels = "1=Never had a drink; 2=Used to drink less than once a month; 3=Used to drink more than once a month"
        for r in histories:
            self.assertEqual(r["value_labels"], history_labels)
            self.assertIn("prior-wave carry-forward", r["value_label_status"])
            self.assertIn("not current past-year drinking", r["value_semantics"])
            self.assertIn("ZDA069", r["note"])
            self.assertNotIn("Freq.", r["value_label_source"])

        mornings = [r for r in self.mapping if r["concept_id"] == "alcohol_morning_drink"]
        self.assertEqual({r["wave"] for r in mornings}, {"2011", "2013"})
        for r in mornings:
            self.assertEqual(r["value_labels"], "1=Yes; 2=No")
            self.assertIn("conditional DA069 route", r["value_label_status"])
            self.assertIn("does not have a population-wide denominator", r["value_semantics"])

        catalog_rows = [r for r in self.catalog if r["Variable.Name"].lower() == "da069"]
        self.assertEqual({r["Source.Wave"] for r in catalog_rows}, {"2011", "2013", "2015", "2018"})
        self.assertTrue(all(r["Value.Labels"] == history_labels and r["Value.Label.Review"] == "officially reviewed" for r in catalog_rows))
        topic_history = next(c for c in self.topic if c["concept_id"] == "alcohol_history")
        self.assertTrue(all("not current past-year drinking" in f["value_semantics"] for f in topic_history["source_fields"]))
        wave = self.pairs["waves"]["2018"]
        pair_history = next(c for c in wave["exposures"] if c["concept_id"] == "alcohol_history")
        self.assertTrue(all("ZDA069" in f["caveat"] for f in pair_history["source_fields"]))
        pair_morning = next(c for c in self.pairs["waves"]["2013"]["exposures"] if c["concept_id"] == "alcohol_morning_drink")
        self.assertTrue(all("not a population-wide Yes/No prevalence field" in f["caveat"] for f in pair_morning["source_fields"]))
        self.assertNotIn("Freq.", json.dumps([catalog_rows, pair_history, pair_morning], ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
