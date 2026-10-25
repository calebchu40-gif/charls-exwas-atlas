import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityEldercareContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.rows = list(csv.DictReader(f))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.labels = {r["code"].lower(): r for r in csv.DictReader(f)}
        cls.site = {x["concept_id"]: x for x in json.loads(
            (ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))}
        cls.codebook = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(
            encoding="utf-8", errors="ignore"
        ).casefold()

    def test_all_candidate_fields_exist_in_raw_inventory_and_site(self):
        expected = {
            "community_eldercare_center_context": {"jb030", "jb031", "jb032", "jb033s1", "jb033s2", "jb033s3", "jb033s4", "jb034", "jb035"},
            "community_home_eldercare_context": {"jb036", "jb037", "jb038"},
        }
        for concept, codes in expected.items():
            rows = [r for r in self.rows if r["concept_id"] == concept]
            self.assertEqual({r["code"].lower() for r in rows}, codes)
            self.assertIn(concept, self.site)
            for row in rows:
                self.assertEqual(row["wave"], "2011")
                # The raw-field inventory is a local, ignored build artifact. CI
                # verifies these codes against the committed official Codebook.
                self.assertIn(row["code"].lower(), self.codebook)
                self.assertIn("analysis eligibility pending", row["mapping_status"])
                self.assertTrue(any(scope in row["caveat"].lower() for scope in ("community", "village", "aggregate")))

    def test_distinct_routes_units_and_official_categories_are_preserved(self):
        rows = {r["code"].lower(): r for r in self.rows}
        self.assertIn("community-only", rows["jb030"]["caveat"].lower())
        self.assertIn("skip", rows["jb030"]["caveat"].lower())
        self.assertIn("village-only", rows["jb037"]["caveat"].lower())
        self.assertEqual(rows["jb031"]["unit"], "square meters")
        self.assertEqual(rows["jb032"]["unit"], "persons")
        self.assertEqual(rows["jb034"]["unit"], "Yuan/year")
        self.assertEqual(rows["jb036"]["unit"], "percent of community households")
        self.assertIn("1=Health care", self.labels["jb033s1"]["value_labels"])
        self.assertIn("1=Yes; 2=No", self.labels["jb037"]["value_labels"])
        q = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8").casefold()
        self.assertIn("does your community have communi ty-based elderly care center", q)
        self.assertIn("skip to jb036", q)
        self.assertIn("does your village have a fam ily-based elder-care center", q)


if __name__ == "__main__":
    unittest.main()
