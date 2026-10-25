import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunitySocialPolicyContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "audit/community_exposure_crosswalk_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))
        with (ROOT / "audit/community_exposure_value_labels_v1.csv").open(encoding="utf-8-sig", newline="") as stream:
            cls.label_rows = list(csv.DictReader(stream))
        site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))
        cls.concepts = {x["concept_id"]: x for x in site}

    def test_program_fields_keep_units_and_distinct_recipient_units(self):
        expected = {
            "community_unemployment_subsidy_program": {"jg001", "jg002", "jg003", "jg004"},
            "community_minimum_living_allowance_program": {"jg005", "jg006", "jg007"},
            "community_single_child_reward_program": {"jg013", "jg014", "jg015", "jg016"},
            "community_pension_65plus_program": {"jg025", "jg026", "jg027", "jg028"},
            "community_pension_80plus_subsidy_program": {"jg029", "jg030", "jg031", "jg032"},
            "community_nrps_program": {"jg033", "jg034", "jg035", "jg036"},
            "community_orps_program": {"jg037", "jg038", "jg039", "jg040"},
        }
        for cid, codes in expected.items():
            rows = {r["code"].casefold(): r for r in self.rows if r["concept_id"] == cid}
            self.assertEqual(set(rows), codes)
            self.assertIn(cid, self.concepts)
            for row in rows.values():
                self.assertEqual(row["wave"], "2011")
                self.assertIn("analysis eligibility pending", row["mapping_status"])
        units = {r["code"].casefold(): r["unit"] for r in self.rows}
        self.assertEqual(units["jg002"], "year")
        self.assertEqual(units["jg003"], "persons")
        self.assertEqual(units["jg004"], "Yuan/month")
        self.assertEqual(units["jg006"], "year")
        self.assertEqual(units["jg007"], "persons")
        self.assertEqual(units["jg014"], "year")
        self.assertEqual(units["jg015"], "households")
        self.assertEqual(units["jg016"], "Yuan/month")
        self.assertEqual(units["jg026"], "year")
        self.assertEqual(units["jg027"], "persons")
        self.assertEqual(units["jg028"], "Yuan/month")
        self.assertEqual(units["jg030"], "year")
        self.assertEqual(units["jg031"], "persons")
        self.assertEqual(units["jg032"], "Yuan/month")
        self.assertEqual(units["jg034"], "year")
        self.assertEqual(units["jg035"], "persons")
        self.assertEqual(units["jg036"], "Yuan/month")
        self.assertEqual(units["jg038"], "year")
        self.assertEqual(units["jg039"], "persons")
        self.assertEqual(units["jg040"], "Yuan/month")
        count_status = next(r for r in self.label_rows if r["code"].casefold() == "jg015")
        self.assertIn("continuous household count", count_status["value_label_status"])

    def test_routes_and_jg008_wording_conflict_are_preserved(self):
        all_mapped = {r["code"].casefold() for r in self.rows}
        self.assertNotIn("jg008", all_mapped)
        min_allowance = self.concepts["community_minimum_living_allowance_program"]
        self.assertIn("JG008 amount prompt appears to carry an unemployment-subsidy wording conflict", min_allowance["caveat"])
        field = next(r for r in self.rows if r["code"].casefold() == "jg005")
        self.assertIn("No skips to JG008", field["caveat"])
        single = self.concepts["community_single_child_reward_program"]
        single_fields = {x["code"].casefold(): x for x in single["source_fields"]}
        self.assertIn("No response skips to JG017", single_fields["jg013"]["caveat"])
        nrps = {x["code"].casefold(): x for x in self.concepts["community_nrps_program"]["source_fields"]}
        self.assertIn("routes No to JG036", nrps["jg033"]["caveat"])
        self.assertIn("applicability is ambiguous", nrps["jg036"]["caveat"])

    def test_official_source_presence_and_frequencies_omitted(self):
        q = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8").casefold()
        cb = (ROOT / "sources_official/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8").casefold()
        for code in ("jg001", "jg002", "jg003", "jg004", "jg005", "jg006", "jg007", "jg008", "jg013", "jg014", "jg015", "jg016", *[f"jg{i:03d}" for i in range(25, 41)]):
            with self.subTest(code=code):
                self.assertIn(code, q)
                self.assertIn(code, cb)
        for row in self.rows:
            if row["concept_id"].startswith("community_") and row["code"].casefold().startswith(("jg001", "jg002", "jg003", "jg004", "jg005", "jg006", "jg007", "jg013", "jg014", "jg015", "jg016", *[f"jg{i:03d}" for i in range(25, 41)])):
                self.assertNotIn("Freq.", row["source_evidence"])
                self.assertNotIn("Mean", row["source_evidence"])


if __name__ == "__main__":
    unittest.main()
