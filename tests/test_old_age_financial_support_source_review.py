import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class OldAgeFinancialSupportSourceReviewTests(unittest.TestCase):
    def test_all_wave_mappings_have_questionnaire_categories_and_wave_caveats(self):
        mapping = pd.read_csv(ROOT / "audit/pension_exposure_variable_mapping_v1.csv", dtype=str).fillna("")
        rows = mapping.loc[
            mapping.concept_id.eq("old_age_financial_support_source")
            & mapping.code.str.lower().eq("fn097_w2")
        ].set_index("wave")
        self.assertEqual(set(rows.index), {"2013", "2015", "2018"})
        self.assertTrue(rows.value_labels.str.contains("1=Children; 2=Savings; 3=Pension", case=False).all())
        self.assertTrue(rows.mapping_status.str.contains("questionnaire").all())
        self.assertTrue(rows.caveat.str.contains("not actual support received").all())
        self.assertIn("FN098_w2", rows.loc["2013", "caveat"])
        self.assertIn("denominator is identical", rows.loc["2018", "caveat"])
        self.assertIn("commercial pension insurance", rows.loc["2018", "caveat"].casefold())
        self.assertTrue(rows.value_label_source.str.contains("Questionnaire_extracted.txt").all())

    def test_review_note_excludes_distribution_statistics_and_claims_full_equivalence(self):
        note = (ROOT / "audit/old_age_financial_support_source_review_2026-10-26.md").read_text(encoding="utf-8")
        self.assertIn("frequency counts and percentages are intentionally excluded", note)
        self.assertIn("do not claim full measurement equivalence", note)


if __name__ == "__main__":
    unittest.main()
