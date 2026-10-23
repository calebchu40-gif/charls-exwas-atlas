import json
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class CommunityEducationFallbackReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crosswalk = pd.read_csv(ROOT / "audit/community_exposure_crosswalk_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
        cls.labels = pd.read_csv(ROOT / "audit/community_exposure_value_labels_v1.csv", dtype=str, encoding="utf-8-sig").fillna("")
        cls.site = json.loads((ROOT / "site-prototype/dist/community_exposures_v1.json").read_text(encoding="utf-8"))

    def test_all_exact_and_conditional_fallback_fields_are_separate(self):
        education = self.crosswalk[self.crosswalk["concept_id"] == "community_education_profile"]
        expected = {f"jc0{i:02d}" for i in range(19, 25)} | {f"jc0{i:02d}_1" for i in range(19, 25)}
        self.assertEqual(set(education["code"].str.lower()), expected)
        self.assertEqual(len(education), 12)
        self.assertEqual(set(education.loc[education["code"].str.endswith("_1"), "unit"]), {"percent bracket (fallback category)"})
        self.assertEqual(set(education.loc[~education["code"].str.endswith("_1"), "unit"]), {"percent of community adults"})
        self.assertTrue(education["caveat"].str.contains("do not combine", case=False).all())

    def test_questionnaire_menus_include_categories_missing_from_codebook_counts(self):
        expected = {
            "jc019_1": "1=0-20%; 2=20-40%; 3=40-60%; 4=60-80%; 5=80-100%",
            "jc020_1": "1=0-10%; 2=10-20%; 3=20-30%; 4=30-40%; 5=>40%",
            "jc021_1": "1=0-10%; 2=10-20%; 3=20-30%; 4=30-40%; 5=>40%",
            "jc022_1": "1=0-10%; 2=10-20%; 3=20-30%; 4=30-40%; 5=>40%",
            "jc023_1": "1=None; 2=0-1%; 3=1-5%; 4=5-10%; 5=10-15%; 6=>15%",
            "jc024_1": "1=None; 2=0-1%; 3=1-5%; 4=5-10%; 5=>10%",
        }
        for code, labels in expected.items():
            row = self.labels[(self.labels["wave"] == "2011") & (self.labels["code"].str.lower() == code)]
            self.assertEqual(len(row), 1, code)
            self.assertEqual(row.iloc[0]["value_labels"], labels)
            self.assertIn("asked only when exact percentage is unknown", row.iloc[0]["value_label_status"])
            self.assertIn("frequencies omitted", row.iloc[0]["value_label_status"])

    def test_other_questionnaire_only_community_mappings_are_reviewed(self):
        reviewed_codes = {"jc020", "jc021", "jc022", "jc023", "jc024", "jj023", "jj024", "jk001", "jk003", "ji001", "jb015"}
        rows = self.crosswalk[self.crosswalk["code"].str.lower().isin(reviewed_codes)]
        self.assertEqual(set(rows["code"].str.lower()), reviewed_codes)
        self.assertTrue(rows["mapping_status"].str.startswith("official questionnaire slot/route").all())
        by_code = rows.set_index(rows["code"].str.lower())
        self.assertEqual(by_code.loc["jj023", "unit"], "RMB yuan/ton")
        self.assertEqual(by_code.loc["jj024", "unit"], "RMB yuan/kWh")
        self.assertIn("village-only", by_code.loc["jb015", "caveat"])

    def test_public_community_site_has_fallback_fields(self):
        concept = next(item for item in self.site if item["concept_id"] == "community_education_profile")
        fields = {field["code"]: field for field in concept["source_fields"]}
        self.assertIn("jc019_1", fields)
        self.assertIn("jc024_1", fields)
        self.assertIn("fallback category", fields["jc019_1"]["unit"])


if __name__ == "__main__":
    unittest.main()
