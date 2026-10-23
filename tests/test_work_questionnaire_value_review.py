import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


class WorkQuestionnaireValueReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pd.read_csv(
            ROOT / "audit" / "work_exposure_value_labels_v1.csv",
            dtype=str,
            encoding="utf-8-sig",
        ).fillna("")

    def row(self, code):
        rows = self.rows[(self.rows["wave"] == "2011") & (self.rows["code"].str.lower() == code)]
        self.assertEqual(len(rows), 1, code)
        return rows.iloc[0]

    def test_unnumbered_questionnaire_options_do_not_claim_numeric_codes(self):
        for code in ("fi004", "fi008", "fl001", "fl013"):
            row = self.row(code)
            self.assertIn("numeric answer codes unverified", row["value_labels"])
            self.assertIn("DO NOT ANALYZE", row["value_label_status"])

    def test_numbered_workplace_categories_retain_release_coding_caveat(self):
        row = self.row("fl004")
        self.assertIn("1=This village/community", row["value_labels"])
        self.assertIn("0 when no fixed address", row["value_labels"])
        self.assertIn("release coding unverified", row["value_labels"])

    def test_continuous_measure_notes_include_documented_units_or_ranges(self):
        expected = {
            "fi009": "Yuan per month",
            "fi012": "0-120 years",
            "fl008": "0-168",
            "fl009": "999997",
            "fl022_1": "Yuan",
            "fl022_2": "0-120 years",
            "fm051": "0-50 persons",
        }
        for code, text in expected.items():
            row = self.row(code)
            self.assertIn(text, row["value_labels"], code)
            self.assertIn("not categorical answer labels", row["value_label_status"], code)

    def test_employer_status_uses_questionnaire_wording_but_keeps_codes_unverified(self):
        row = self.row("fl007")
        self.assertIn("Yes; No", row["value_labels"])
        self.assertIn("numeric value codes not verified", row["value_label_status"])


if __name__ == "__main__":
    unittest.main()
