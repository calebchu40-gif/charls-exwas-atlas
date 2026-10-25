import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityReforestationPolicyContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.label_rows = list(csv.DictReader(stream))
        site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))
        cls.concept = next(item for item in site if item["concept_id"] == "community_reforestation_subsidy_program")

    def test_all_four_wave1_fields_are_mapped_with_correct_units_and_scope(self):
        fields = {row["code"].casefold(): row for row in self.rows if row["concept_id"] == "community_reforestation_subsidy_program"}
        self.assertEqual(set(fields), {"jg021", "jg022", "jg023", "jg024"})
        self.assertEqual(fields["jg022"]["unit"], "year")
        self.assertEqual(fields["jg023"]["unit"], "households")
        self.assertEqual(fields["jg024"]["unit"], "Yuan/mu")
        for row in fields.values():
            self.assertEqual(row["wave"], "2011")
            self.assertIn("village-only JG021–JG024", row["source_evidence"])
            self.assertIn("analysis eligibility pending", row["mapping_status"])
        self.assertIn("not forest cover", self.concept["caveat"])
        site_fields = {item["code"].casefold(): item for item in self.concept["source_fields"]}
        self.assertIn("No response routes past JG022–JG024", site_fields["jg021"]["caveat"])
        self.assertIn("not the sampled household's receipt status", site_fields["jg023"]["caveat"])

    def test_mapping_is_anchored_in_both_official_sources(self):
        questionnaire = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        codebook = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        for code, phrase in (("JG021", "subsidies for reforestation"), ("JG022", "subsidies for reforestation"),
                             ("JG023", "how many households in this village received subsidies for reforestation"),
                             ("JG024", "average subsidies standard")):
            with self.subTest(code=code):
                self.assertIn(code, questionnaire)
                self.assertIn(phrase, questionnaire.casefold())
                self.assertIn(code.casefold(), codebook.casefold())

    def test_no_codebook_frequency_or_summary_statistics_are_exposed(self):
        for row in self.rows:
            if row["concept_id"] == "community_reforestation_subsidy_program":
                self.assertNotIn("Freq.", row["source_evidence"])
                self.assertNotIn("Mean", row["source_evidence"])
                self.assertNotIn("OBS", row["source_evidence"])
        labels = next(row for row in self.label_rows if row["concept_id"] == "community_reforestation_subsidy_program" and row["code"].casefold() == "jg021")
        self.assertEqual(labels["value_labels"], "1=Yes; 2=No")
        self.assertIn("frequencies omitted", labels["value_label_status"])
        self.assertNotIn("114", labels["value_labels"])


if __name__ == "__main__":
    unittest.main()
