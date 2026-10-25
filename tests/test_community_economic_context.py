import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityEconomicContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.labels = {r["code"].lower(): r for r in csv.DictReader(f)}
        cls.site = {x["concept_id"]: x for x in json.loads(
            (ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))}
        cls.codebook = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(
            encoding="utf-8", errors="ignore").casefold()
        cls.questionnaire = " ".join((ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt")
                                      .read_text(encoding="utf-8", errors="ignore").casefold().split())

    def test_community_economic_and_housing_fields_are_distinct_context_candidates(self):
        expected = {
            "community_economic_activity_and_fiscal_context": {"jj011", "jj012", "jj013", "jj014", "jj015", "jj016"},
            "community_housing_market_context": {"jj026", "jj027", "jj028", "jj029", "jj030"},
            "community_formal_credit_access": {"jj031", "jj032"},
        }
        for concept, codes in expected.items():
            rows = [r for r in self.rows if r["concept_id"] == concept]
            self.assertEqual({r["code"].lower() for r in rows}, codes)
            self.assertIn(concept, self.site)
            self.assertTrue(all(r["wave"] == "2011" and any(
                scope in r["caveat"].lower() for scope in ("community", "village")) for r in rows))
            for code in codes:
                self.assertIn(code, self.codebook)

    def test_source_wording_units_and_ordinal_credit_categories_are_preserved(self):
        rows = {r["code"].lower(): r for r in self.rows}
        self.assertIn("total agricultural revenue of this village in 2010", self.questionnaire)
        self.assertIn("average price for a new apartment", self.questionnaire)
        self.assertIn("proportion of farmers who got loans from the formal financial", self.questionnaire)
        self.assertEqual(rows["jj011"]["unit"], "10,000 Yuan")
        self.assertEqual(rows["jj016"]["unit"], "Yuan")
        self.assertEqual(rows["jj026"]["unit"], "Yuan/m²")
        self.assertEqual(rows["jj028"]["unit"], "Yuan/month")
        self.assertEqual(rows["jj031"]["unit"], "percent")
        self.assertIn("1=Very difficult", self.labels["jj032"]["value_labels"])
        self.assertIn("5=Easily", self.labels["jj032"]["value_labels"])
        self.assertIn("frequencies omitted", self.labels["jj032"]["value_label_status"])
        self.assertIn("village-only", rows["jj031"]["caveat"].lower())
        self.assertIn("2010", rows["jj031"]["caveat"].lower())
        self.assertIn("three years earlier", rows["jj032"]["caveat"].lower())


if __name__ == "__main__":
    unittest.main()
