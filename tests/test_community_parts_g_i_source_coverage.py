import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CommunityPartsGIcoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def rows(path):
            with (ROOT / path).open(encoding="utf-8-sig", newline="") as stream:
                return list(csv.DictReader(stream))

        cls.inventory = rows("audit/community_field_inventory_2011_v1.csv")
        cls.crosswalk = rows("audit/community_exposure_crosswalk_v1.csv")
        cls.overrides = rows("audit/catalog_role_override_review_v1.csv")

    def test_every_jg_ji_inventory_field_has_an_explicit_disposition(self):
        module_fields = {
            row["variable"].casefold()
            for row in self.inventory
            if row["variable"].casefold().startswith(("jg", "ji"))
        }
        mapped = {row["code"].casefold() for row in self.crosswalk}
        c_only = {
            row["code"].casefold()
            for row in self.overrides
            if row["wave"] == "2011" and row["keep_role"].casefold() == "c"
        }
        self.assertEqual(len(module_fields), 123)
        self.assertEqual(module_fields - mapped, {"jg008", "jg042", "ji002_other"})
        self.assertTrue(module_fields <= mapped | c_only)
        self.assertEqual(len(module_fields & mapped), 120)

    def test_conflicted_items_are_c_metadata_not_exposures(self):
        overrides = {
            row["code"].casefold(): row
            for row in self.overrides
            if row["wave"] == "2011"
        }
        self.assertEqual(overrides["jg008"]["keep_role"], "c")
        self.assertEqual(overrides["jg008"]["metadata_type"], "community_part_g_amount_source_conflict")
        self.assertEqual(overrides["jg042"]["keep_role"], "c")
        self.assertEqual(overrides["jg042"]["metadata_type"], "community_part_g_informant_identity")
        self.assertEqual(overrides["ji002_other"]["keep_role"], "c")
        self.assertNotIn("jg008", {row["code"].casefold() for row in self.crosswalk})
        self.assertNotIn("jg042", {row["code"].casefold() for row in self.crosswalk})
        self.assertNotIn("ji002_other", {row["code"].casefold() for row in self.crosswalk})

    def test_source_documents_support_the_recorded_conflicts(self):
        questionnaire = (ROOT / "sources_official/CHARLS_2011_Community_Questionnaire_official_extracted.txt").read_text(encoding="utf-8").casefold()
        codebook = (ROOT / "audit/CHARLS_2011_Codebook_extracted.txt").read_text(encoding="utf-8").casefold()
        self.assertIn("skip to jg008", questionnaire)
        self.assertIn("平均失业补助标准", questionnaire)
        self.assertIn("jg042. respondent identity for part g", questionnaire)
        self.assertIn("jg042 : respondent identity for part d", codebook)
        self.assertIn("other", questionnaire)
        self.assertIn("disasters", questionnaire)


if __name__ == "__main__":
    unittest.main()
