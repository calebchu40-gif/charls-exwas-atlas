import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import apply_wave5_core_demographic_review as review


class Wave5CoreDemographicReviewTests(unittest.TestCase):
    def test_age_rule_retains_reinterview_and_new_interview_routes(self):
        note = review.FIELDS["xrage"]["note"]
        self.assertIn("ZRBirthYear is missing or XRType=2", note)
        self.assertIn("XRType=1", note)
        self.assertIn("year-difference algorithm", note)

    def test_gender_formula_inputs_are_not_mislabeled_as_final_covariates(self):
        self.assertIn("use respondent reconfirmation BA002", review.FIELDS["xrgender"]["note"])
        self.assertIn("Conditional reconfirmation", review.FIELDS["ba002"]["note"])
        self.assertIn("prior-wave gender preload", review.FIELDS["zrgender"]["note"].lower())
        self.assertIn("unapproved", "C metadata; source-backed age/gender definition; covariate use remains estimand-specific and unapproved")

    def test_age_target_and_interview_language_remain_measurement_metadata(self):
        self.assertIn("target age", review.FIELDS["xfagepossibility"]["note"])
        self.assertEqual(review.FIELDS["xfagepossibility"]["category"], "measurement metadata")
        self.assertEqual(review.FIELDS["xfagepossibility"]["unit"], "years")
        self.assertIn("not the respondent’s native language", review.FIELDS["dc030"]["note"])
        self.assertIn("not respondent age", review.FIELDS["xfagepossibility"]["review_flag"])
        self.assertIn("not respondent native language", review.FIELDS["dc030"]["review_flag"])
        self.assertNotIn("age/gender definition", review.FIELDS["dc030"]["review_flag"])
        self.assertEqual(review.FIELDS["xfagepossibility"]["subcategory"], "subjective life-expectancy target age")
        self.assertEqual(review.FIELDS["dc030"]["subcategory"], "interview language")

    def test_wave5_catalog_status_is_field_specific_and_does_not_promote_intermediates(self):
        self.assertIn("age derivation reviewed", review.FIELDS["xrage"]["candidate_status"])
        self.assertIn("conditional gender reconfirmation", review.FIELDS["ba002"]["candidate_status"])
        self.assertIn("intermediate gender recode", review.FIELDS["xr20gender"]["candidate_status"])
        self.assertIn("not observed survival", review.FIELDS["xfagepossibility"]["candidate_status"])
        self.assertEqual(review.FIELDS["xrage"]["subcategory"], "respondent age derivation")

    def test_json_update_is_wave_and_role_scoped(self):
        rows = [
            {"Source.Wave": "2020", "Variable.Name": "xrage", "epcf": "c", "Value.Label.Review": "not yet reviewed"},
            {"Source.Wave": "2018", "Variable.Name": "xrage", "epcf": "c", "Value.Label.Review": "leave me"},
            {"Source.Wave": "2020", "Variable.Name": "xrage", "epcf": "e", "Value.Label.Review": "leave me too"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            self.assertEqual(review.update_json(path), 1)
            result = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("CAPI-derived age", result[0]["Harmonization.Status"])
        self.assertEqual(result[1]["Value.Label.Review"], "leave me")
        self.assertEqual(result[2]["Value.Label.Review"], "leave me too")


if __name__ == "__main__":
    unittest.main()

