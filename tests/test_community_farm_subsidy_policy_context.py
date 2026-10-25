import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityFarmSubsidyPolicyContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.labels = list(csv.DictReader(stream))
        site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))
        cls.concept = next(item for item in site if item["concept_id"] == "community_farm_subsidy_program")

    def test_fields_preserve_scope_route_and_units(self):
        fields = {r["code"].casefold(): r for r in self.rows if r["concept_id"] == "community_farm_subsidy_program"}
        self.assertEqual(set(fields), {"jg017", "jg018", "jg019", "jg020"})
        self.assertEqual(fields["jg018"]["unit"], "year")
        self.assertEqual(fields["jg019"]["unit"], "households")
        self.assertEqual(fields["jg020"]["unit"], "Yuan/mu")
        for row in fields.values():
            self.assertEqual(row["wave"], "2011")
            self.assertIn("village-only JG017–JG020", row["source_evidence"])
            self.assertIn("analysis eligibility pending", row["mapping_status"])
        site_fields = {f["code"].casefold(): f for f in self.concept["source_fields"]}
        self.assertIn("No response skips JG018–JG020", site_fields["jg017"]["caveat"])
        self.assertIn("not a specific pesticide/fertilizer measure", self.concept["caveat"])
        self.assertIn("Not the sampled household's receipt status", fields["jg019"]["caveat"])

    def test_mapping_uses_official_questionnaire_and_codebook_metadata(self):
        q = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8").casefold()
        cb = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8").casefold()
        for code in ("jg017", "jg018", "jg019", "jg020"):
            self.assertIn(code, q)
            self.assertIn(code, cb)
        self.assertIn("yuan/mu", q)

    def test_yes_no_label_has_no_codebook_frequency(self):
        label = next(r for r in self.labels if r["concept_id"] == "community_farm_subsidy_program" and r["code"].casefold() == "jg017")
        self.assertEqual(label["value_labels"], "1=Yes; 2=No")
        self.assertIn("frequencies omitted", label["value_label_status"])
        self.assertNotIn("Obs", label["value_labels"])


if __name__ == "__main__":
    unittest.main()
