import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityHistorySourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.crosswalk = list(csv.DictReader(f))
        with (ROOT / "audit/community_field_inventory_2011_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.raw = list(csv.DictReader(f))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.labels = list(csv.DictReader(f))
        with (ROOT / "audit/community_questionnaire_label_overrides_v1.csv").open(encoding="utf-8-sig", newline="") as f:
            cls.overrides = list(csv.DictReader(f))
        cls.review = (ROOT / "audit/community_part_h_source_coverage_review_2026-10-26.md").read_text(encoding="utf-8")

    def test_all_reviewed_part_h_codes_have_a_disposition(self):
        inventory = {
            r["variable"].lower() for r in self.raw
            if r.get("module", "").lower() == "community"
            and r.get("wave") == "2011"
            and r.get("variable", "").lower().startswith("jh")
        }
        mapped = {r["code"].lower() for r in self.crosswalk if r.get("wave") == "2011" and r.get("code", "").lower().startswith("jh")}
        self.assertEqual(len(inventory), 75)
        self.assertEqual(len(mapped), 60)
        self.assertTrue(mapped <= inventory)
        self.assertEqual(len(inventory - mapped), 15)
        for code in ("jh001_1", "jh031"):
            self.assertIn(code.upper(), self.review)
        self.assertIn("JH002_1_*", self.review)

    def test_history_maps_keep_community_level_scope_and_period_slots(self):
        by_code = {r["code"].lower(): r for r in self.crosswalk if r.get("wave") == "2011"}
        expected = {
            "jh003": "community_land_institutional_transition_history",
            "jh009": "community_sent_down_youth_migration_history",
            "jh014": "community_barefoot_doctor_capacity_history",
            "jh016": "community_primary_school_change",
            "jh018_1_1_": "community_military_service_history",
            "jh018_2_11_": "community_university_admission_history",
            "jh019": "community_family_planning_policy_history",
            "jh029b_3_": "community_unplanned_birth_penalty_policy_history",
            "jh033": "community_identity_card_rollout_history",
        }
        for code, concept_id in expected.items():
            self.assertEqual(by_code[code]["concept_id"], concept_id)
            self.assertIn("Part H", by_code[code]["source_evidence"])
            self.assertIn("not ", by_code[code]["caveat"].lower())
        self.assertIn("questionnaire period 2010", by_code["jh018_1_1_"]["caveat"])
        self.assertEqual(by_code["jh018_1_1_"]["unit"], "people")

    def test_conditional_year_is_reviewed_as_numeric_not_category(self):
        row = next(r for r in self.labels if r["wave"] == "2011" and r["code"].lower() == "jh026_1")
        self.assertEqual(row["value_labels"], "")
        self.assertIn("continuous numeric year", row["value_label_status"])
        override = next(r for r in self.overrides if r["wave"] == "2011" and r["code"].lower() == "jh026_1")
        self.assertIn("JH026=Yes", override["rationale"])


if __name__ == "__main__":
    unittest.main()
