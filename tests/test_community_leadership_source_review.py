import csv
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CommunityLeadershipSourceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"audit/community_field_inventory_2011_v1.csv").open(encoding="utf-8-sig",newline="") as f:
            cls.raw=list(csv.DictReader(f))
        with (ROOT/"audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig",newline="") as f:
            cls.crosswalk=list(csv.DictReader(f))
        with (ROOT/"audit/catalog_role_override_review_v1.csv").open(encoding="utf-8-sig",newline="") as f:
            cls.overrides=list(csv.DictReader(f))
        cls.questionnaire=(ROOT/"sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.review=(ROOT/"audit/community_part_a_leadership_profile_source_review_2026-10-26.md").read_text(encoding="utf-8")
        cls.catalog=json.loads((ROOT/"site-prototype/dist/catalog_e.json").read_text(encoding="utf-8"))

    def test_every_ja042_inventory_field_has_candidate_or_explicit_hold(self):
        inventory={r["variable"].lower() for r in self.raw if r["wave"]=="2011" and r["module"]=="community" and r["variable"].lower().startswith("ja042")}
        mapped={r["code"].lower() for r in self.crosswalk if r.get("wave")=="2011" and r.get("code","").lower().startswith("ja042")}
        held={r["code"].lower() for r in self.overrides if r.get("wave")=="2011" and r.get("keep_role","").lower()=="c" and r.get("code","").lower().startswith("ja042")}
        self.assertEqual(len(inventory),14)
        self.assertEqual(len(mapped),12)
        self.assertEqual(held,{"ja042_2_5_","ja042_3_5_"})
        self.assertEqual(inventory,mapped|held)
        self.assertFalse(mapped&held)

    def test_four_named_roles_and_scope_are_source_documented(self):
        for term in ("community director","village head","village secretary","village accountant"):
            self.assertIn(term.lower(),self.questionnaire.lower())
            self.assertIn(term.lower(),self.review.lower())
        self.assertIn("c only",self.questionnaire.lower())
        self.assertIn("v only",self.questionnaire.lower())
        self.assertIn("community-only",self.review.lower())
        self.assertIn("village-only",self.review.lower())
        self.assertIn("fifth title",self.review.lower())
        self.assertIn("not participant education",self.review.lower())

    def test_questionnaire_education_categories_are_consistent_across_roles(self):
        rows={r["Variable.Name"].lower():r for r in self.catalog if r.get("Source.Wave")=="2011"}
        expected="1=Primary school; 2=Junior high school; 3=High school; 4=Middle professional school; 5=Advanced professional school; 6=University and above; 7=Illiterate"
        for i in range(1,5):
            row=rows[f"ja042_1_{i}_"]
            self.assertEqual(row["Value.Labels"],expected)
            self.assertIn("official questionnaire response categories",row["Value.Label.Review"])
            self.assertIn("CHARLS_2011_Community_Questionnaire",row["Value.Label.Source"])

    def test_candidate_concepts_keep_education_age_and_tenure_separate(self):
        rows={r["code"].lower():r for r in self.crosswalk if r.get("wave")=="2011"}
        for i,concept in enumerate(("community_director_education_profile","community_village_head_education_profile","community_village_secretary_education_profile","community_village_accountant_education_profile"),1):
            self.assertEqual(rows[f"ja042_1_{i}_"]["concept_id"],concept)
        self.assertEqual({rows[f"ja042_2_{i}_"]["concept_id"] for i in range(1,5)},{"community_local_leader_age_profile"})
        self.assertEqual({rows[f"ja042_3_{i}_"]["concept_id"] for i in range(1,5)},{"community_local_leader_tenure_profile"})
        self.assertIn("not participant age",rows["ja042_2_1_"]["caveat"].lower())
        self.assertEqual(rows["ja042_2_1_"]["unit"],"years of age")
        self.assertEqual(rows["ja042_3_1_"]["unit"],"years in position")

if __name__=="__main__":
    unittest.main()
