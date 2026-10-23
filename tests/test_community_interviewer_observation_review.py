import csv
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityInterviewerObservationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questionnaire = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.crosswalk = list(csv.DictReader(io.StringIO((ROOT / "audit/community_exposure_crosswalk_v1.csv").read_text(encoding="utf-8-sig"))))
        cls.overrides = list(csv.DictReader(io.StringIO((ROOT / "audit/community_questionnaire_label_overrides_v1.csv").read_text(encoding="utf-8-sig"))))
        cls.site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))

    def test_four_interviewer_observations_have_explicit_community_scope(self):
        expected = {
            "jk002": "community_observed_socioeconomic_status",
            "jk004": "community_built_form_organization",
            "jk005": "community_observed_crowding",
            "jk006": "community_accessibility_observation",
        }
        for code, concept_id in expected.items():
            row = next(r for r in self.crosswalk if r["code"] == code)
            self.assertEqual(row["concept_id"], concept_id)
            self.assertIn("Part K interviewer observations", row["source_evidence"])
            self.assertEqual(row["wave"], "2011")

    def test_questionnaire_anchors_and_scope_are_preserved(self):
        for anchor in ("jk002. social economic status", "jk004. the construction structure", "jk005. the degree of crowdness", "jk006. the degree of community handicapped access"):
            self.assertIn(anchor, self.questionnaire.lower())
        by_code = {r["code"]: r for r in self.overrides}
        self.assertIn("2–6=intermediate", by_code["jk005"]["value_labels"])
        self.assertIn("higher codes indicate less perceived crowding", by_code["jk005"]["rationale"])
        self.assertIn("higher codes indicate better perceived accessibility", by_code["jk006"]["rationale"])

    def test_site_keeps_items_as_separate_ordinal_concepts(self):
        concepts = {item["concept_id"]: item for item in self.site}
        for concept_id in ("community_observed_socioeconomic_status", "community_built_form_organization", "community_observed_crowding", "community_accessibility_observation"):
            item = concepts[concept_id]
            self.assertEqual(len(item["source_fields"]), 1)
            self.assertEqual(item["source_fields"][0]["wave"], "2011")
            self.assertIn("interviewer observation", item["caveat"])


if __name__ == "__main__":
    unittest.main()
