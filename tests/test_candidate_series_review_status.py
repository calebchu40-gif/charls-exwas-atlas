import unittest

from scripts.refresh_candidate_series_review_status import find_source_rows


class CandidateSeriesReviewStatusTests(unittest.TestCase):
    def test_legacy_series_subcategory_falls_back_by_exact_role_code_and_module(self):
        series = {"epcf": "c", "category": "automated covariate search hit",
                  "subcategory": "keyword discovery only", "Variable.Name": "ba000_w2_3",
                  "source_modules": "Demographic_Background"}
        fields = [
            {"epcf": "c", "category": "automated covariate search hit",
             "subcategory": "respondent gender source and derivation metadata",
             "Variable.Name": "ba000_w2_3", "Data.File.Name": "Demographic_Background"},
            {"epcf": "p", "category": "other", "subcategory": "different",
             "Variable.Name": "ba000_w2_3", "Data.File.Name": "Demographic_Background"},
            {"epcf": "c", "category": "other", "subcategory": "different",
             "Variable.Name": "ba000_w2_3", "Data.File.Name": "Other_Module"},
        ]
        indexed = {}
        self.assertEqual(find_source_rows(series, fields, indexed), [fields[0]])


if __name__ == "__main__":
    unittest.main()
