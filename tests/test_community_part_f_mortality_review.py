import csv
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CommunityPartFMortalityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"audit/community_field_inventory_2011_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.raw=list(csv.DictReader(f))
        with (ROOT/"audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.crosswalk=list(csv.DictReader(f))
        with (ROOT/"audit/catalog_role_override_review_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.overrides=list(csv.DictReader(f))
        cls.questionnaire=(ROOT/"sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.codebook=(ROOT/"audit/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        cls.audit=(ROOT/"audit/community_part_f_mortality_source_review_2026-10-26.md").read_text(encoding="utf-8")
        cls.site=json.loads((ROOT/"site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))

    def test_all_inventory_mortality_fields_are_candidate_or_c_only(self):
        inventory={r["variable"].lower() for r in self.raw if r["wave"]=="2011" and r["module"]=="community" and (r["variable"].lower().startswith("jf017") or r["variable"].lower().startswith("jf018") or r["variable"].lower()=="jf020")}
        mapped={r["code"].lower() for r in self.crosswalk if r.get("wave")=="2011" and r.get("code","").lower().startswith(("jf017","jf018"))}
        held={r["code"].lower() for r in self.overrides if r.get("wave")=="2011" and r.get("keep_role","").lower()=="c" and (r.get("code","").lower().startswith("jf018") or r.get("code","").lower()=="jf020")}
        self.assertEqual(len(inventory),9)
        self.assertEqual(mapped,{"jf017_1","jf017_2"})
        self.assertEqual(held,{"jf018_1_1_","jf018_1_2_","jf018_1_3_","jf018_2_1_","jf018_2_2_","jf018_2_3_","jf020"})
        self.assertEqual(inventory,mapped|held)
        self.assertFalse(mapped&held)

    def test_candidate_definitions_preserve_aggregate_denominators_and_time(self):
        rows={r["code"].lower():r for r in self.crosswalk if r.get("wave")=="2011"}
        self.assertEqual(rows["jf017_1"]["concept_id"],"community_total_deaths_3y")
        self.assertEqual(rows["jf017_2"]["concept_id"],"community_suicide_deaths_3y")
        for code in ("jf017_1","jf017_2"):
            self.assertEqual(rows[code]["unit"],"persons")
            self.assertIn("since 2008",rows[code]["caveat"].lower())
            self.assertIn("no population denominator",rows[code]["caveat"].lower())
        self.assertIn("past three years(since 2008)",self.questionnaire.lower())

    def test_open_text_cause_slots_and_informant_conflict_are_not_exposures(self):
        c_codes={r["code"].lower() for r in self.overrides if r.get("keep_role","").lower()=="c"}
        self.assertTrue({"jf018_1_1_","jf018_1_2_","jf018_1_3_","jf018_2_1_","jf018_2_2_","jf018_2_3_","jf020"}.issubset(c_codes))
        self.assertIn("no text response is published",self.audit.lower())
        self.assertIn("questionnaire calls it part f",self.audit.lower())
        self.assertIn("codebook field label says",self.audit.lower())
        self.assertIn("part d",self.codebook.lower())
        concepts={item["concept_id"] for item in self.site}
        self.assertIn("community_total_deaths_3y",concepts)
        self.assertIn("community_suicide_deaths_3y",concepts)
        self.assertNotIn("jf018_1_1_",{f["code"].lower() for item in self.site for f in item["source_fields"]})

if __name__=="__main__": unittest.main()
