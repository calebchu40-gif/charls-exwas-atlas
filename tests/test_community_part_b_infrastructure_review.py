import csv
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class CommunityPartBInfrastructureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT/"audit/raw_variable_catalog_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.raw=list(csv.DictReader(f))
        with (ROOT/"audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.crosswalk=list(csv.DictReader(f))
        with (ROOT/"audit/catalog_role_override_review_v1.csv").open(encoding="utf-8-sig",newline="") as f: cls.overrides=list(csv.DictReader(f))
        cls.questionnaire=(ROOT/"sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8")
        cls.codebook=(ROOT/"sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8")
        cls.audit=(ROOT/"audit/community_part_b_infrastructure_timing_review_2026-10-26.md").read_text(encoding="utf-8")
        cls.site=json.loads((ROOT/"site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))

    def test_every_raw_part_b_field_has_candidate_or_c_only_disposition(self):
        inventory={r["variable"].lower() for r in self.raw if r["wave"]=="2011" and r["module"]=="community" and r["variable"].lower().startswith("jb")}
        mapped={r["code"].lower() for r in self.crosswalk if r.get("wave")=="2011" and r.get("code","").lower().startswith("jb")}
        held={r["code"].lower() for r in self.overrides if r.get("wave")=="2011" and r.get("keep_role","").lower()=="c" and r.get("code","").lower().startswith("jb")}
        self.assertEqual(len(inventory),127)
        self.assertEqual(len(mapped),122)
        self.assertEqual(held,{"jb009_1","jb013_1","jb033_1","jb035_1","jb040"})
        self.assertEqual(inventory,mapped|held)

    def test_three_historical_infrastructure_years_are_distinct_candidates(self):
        rows={r["code"].lower():r for r in self.crosswalk if r.get("wave")=="2011"}
        expected={"jb011":"community_sewer_system_start_year","jb016":"community_sanitation_reconstruction_year","jb022":"community_electricity_first_available_year"}
        for code,cid in expected.items():
            self.assertEqual(rows[code]["concept_id"],cid)
            self.assertEqual(rows[code]["unit"],"calendar year")
            self.assertIn(code,self.codebook.lower())
        self.assertIn("skip to jb012",self.questionnaire.lower())
        self.assertIn("capi: v only",self.questionnaire.lower())

    def test_all_jb029_facility_slots_are_mapped_with_route_caveats(self):
        rows=[r for r in self.crosswalk if r.get("wave")=="2011" and r.get("code","").lower().startswith("jb029_")]
        self.assertEqual(len(rows),42)
        for index in range(1,15):
            codes={f"jb029_{part}_{index}_" for part in (1,2,3) if any(r["code"].lower()==f"jb029_{part}_{index}_" for r in rows)}
            self.assertEqual(codes,{f"jb029_1_{index}_",f"jb029_2_{index}_",f"jb029_3_{index}_"})
        self.assertIn("Who initiated this",self.questionnaire)
        self.assertIn("Who funded this",self.questionnaire)
        self.assertIn("structural",self.audit.lower())
        self.assertFalse(any(f["code"].lower().startswith("jb029_") for item in self.site for f in item["source_fields"] if "respondent" in f.get("caveat","").lower()))

    def test_open_text_and_informant_fields_remain_c_only(self):
        c_rows=[r for r in self.overrides if r.get("wave")=="2011" and r.get("keep_role","").lower()=="c"]
        c_codes={r["code"].lower() for r in c_rows}
        self.assertTrue({"jb009_1","jb013_1","jb033_1","jb035_1","jb040"}.issubset(c_codes))
        for code in ("jb009_1","jb013_1","jb033_1","jb035_1"):
            row=next(r for r in c_rows if r["code"].lower()==code)
            self.assertEqual(row["metadata_type"],"community_part_b_open_text_metadata")
        self.assertIn("direct identifiers",self.audit.lower())
        self.assertIn("response text is not published",self.audit.lower())

if __name__=="__main__": unittest.main()
