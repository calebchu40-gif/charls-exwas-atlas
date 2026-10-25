import csv
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CommunityPartDEnterpriseWageReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def read_csv(path):
            with (ROOT/path).open(encoding="utf-8-sig",newline="") as f:
                return list(csv.DictReader(f))
        cls.raw=read_csv(Path("audit/raw_variable_catalog_v1.csv"))
        cls.crosswalk=read_csv(Path("audit/community_exposure_crosswalk_v1.csv"))
        cls.overrides=read_csv(Path("audit/catalog_role_override_review_v1.csv"))
        cls.questionnaire=(ROOT/"sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.codebook=(ROOT/"sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        cls.audit=(ROOT/"audit/community_part_d_enterprise_wage_review_2026-10-26.md").read_text(encoding="utf-8")
        cls.site=json.loads((ROOT/"site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))

    def test_all_substantive_fields_are_mapped_and_informant_role_is_c_only(self):
        inventory={r["variable"].lower() for r in self.raw if r["wave"]=="2011" and r["module"]=="community" and r["variable"].lower().startswith("jd")}
        mapped={r["code"].lower() for r in self.crosswalk if r.get("wave")=="2011" and r.get("code","").lower().startswith("jd")}
        c_only={r["code"].lower() for r in self.overrides if r["wave"]=="2011" and r["keep_role"].lower()=="c"}
        self.assertEqual(len(inventory),18)
        self.assertEqual(len(mapped),17)
        self.assertEqual(inventory,mapped|{"jd014"})
        self.assertIn("jd014",c_only)
        self.assertEqual(sum(1 for r in self.overrides if r["wave"]=="2011" and r["code"].lower()=="jd014" and r["metadata_type"]=="community_part_d_informant_role"),1)

    def test_source_mappings_keep_2010_context_units_and_aggregate_scope(self):
        rows={r["code"].lower():r for r in self.crosswalk if r.get("wave")=="2011"}
        self.assertEqual(rows["jd001"]["unit"],"households")
        self.assertEqual(rows["jd003"]["unit"],"firms")
        self.assertEqual(rows["jd005"]["unit"],"persons")
        self.assertEqual(rows["jd007_1"]["unit"],"Yuan/day")
        self.assertEqual(rows["jd007_2"]["unit"],"Yuan/month")
        self.assertEqual(rows["jd009"]["unit"],"days/month")
        self.assertEqual(rows["jd010"]["unit"],"Yuan/day")
        self.assertEqual(rows["jd012"]["unit"],"Yuan/month")
        for code in rows:
            if code.startswith("jd") and code!="jd014":
                self.assertIn("Community-informant aggregate/estimate",rows[code]["caveat"])
                self.assertIn("Part D",rows[code]["source_evidence"])
        self.assertIn("at least eight employees",self.audit)
        self.assertIn("What was the average salary of male employees",self.questionnaire)
        self.assertIn("jd007 1",self.codebook.lower())

    def test_product_slots_stay_nominal_and_names_and_phones_are_excluded(self):
        rows={r["code"].lower():r for r in self.crosswalk if r.get("wave")=="2011"}
        for code in ("jd004s1","jd004s2","jd004s3","jd004s4"):
            self.assertEqual(rows[code]["unit"],"")
            self.assertIn("slot/value encoding",rows[code]["caveat"])
        all_source_codes={f["code"].lower() for item in self.site for f in item["source_fields"]}
        self.assertNotIn("jd013",all_source_codes)
        self.assertNotIn("jd015",all_source_codes)
        self.assertIn("JD013",self.audit)
        self.assertIn("JD015",self.audit)

if __name__=="__main__": unittest.main()
