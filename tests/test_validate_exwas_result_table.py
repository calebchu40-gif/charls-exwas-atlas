import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_exwas_result_table import read_schema, validate_rows  # noqa: E402


class ResultTableValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fields, cls.required = read_schema()

    def base_row(self):
        row = {field: "" for field in self.fields}
        for field in self.fields:
            if self.required[field] == "yes":
                row[field] = "documented"
        row.update(
            analysis_id="synthetic-001",
            multiple_testing_family="synthetic_main;K=1",
            fit_status="blocked_design_verification",
            estimability_review_status="pending",
            weight_status="unresolved",
            psu_status="unresolved",
            stratum_status="unresolved",
            source_hash_status="private_local_sha256_recorded",
            source_identity_status="verified_official_source",
            source_manifest_id="synthetic-manifest-v1",
            variance_design="not fit-ready; synthetic validation fixture",
        )
        return row

    def test_blocked_result_has_no_effect_estimates(self):
        errors = validate_rows([self.base_row()], self.fields, self.required)
        self.assertEqual(errors, [])

    def test_blocked_result_cannot_contain_effect_estimate(self):
        row = self.base_row()
        row["estimate"] = "0.2"
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("unless fit_status=success" in error for error in errors))

    def test_inestimable_row_rejects_finite_iteration_coefficient_and_nan_uncertainty(self):
        row = self.base_row()
        row.update(
            fit_status="inestimable",
            estimate="27.2",
            standard_error="nan",
            ci_lower="nan",
            ci_upper="nan",
            p_value="nan",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("standard_error must be finite" in error for error in errors))
        self.assertTrue(any("estimate fields must be blank unless fit_status=success" in error for error in errors))

    def test_sample_flow_and_probability_bounds_are_enforced(self):
        row = self.base_row()
        row.update(n_eligible="10", n_interview="8", p_value="1.4")
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("n_eligible cannot exceed n_interview" in error for error in errors))
        self.assertTrue(any("p_value must be between 0 and 1" in error for error in errors))

    def test_design_verified_success_row_passes(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="CHARLS synthetic release; release_id=synthetic-v1",
            software_versions="python=synthetic; commit=" + "b" * 40,
            weight_status="verified_used",
            weight_id="synthetic_weight",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="verified_used",
            stratum_id="synthetic_stratum",
            variance_design="synthetic design-based variance fixture",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_interview="100",
            n_eligible="90",
            n_exposure_valid="85",
            n_phenotype_valid="80",
            n_pair_complete="75",
            n_model="70",
        )
        self.assertEqual(validate_rows([row], self.fields, self.required), [])
        row["source_identity_status"] = "unresolved"
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("independently verified official source identity" in e for e in errors))

    def test_success_requires_private_source_hash_evidence_and_code_commit(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="CHARLS synthetic release; release_id=synthetic-v1",
            source_hash_status="unavailable_pending_authorized_file",
            source_identity_status="unresolved",
            source_manifest_id="",
            software_versions="python=synthetic",
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="approximate method: synthetic Taylor; limitation: synthetic strata only",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("source hash verification recorded" in e for e in errors))
        self.assertTrue(any("independently verified official source identity" in e for e in errors))
        self.assertTrue(any("source_manifest_id" in e for e in errors))
        self.assertTrue(any("requires a code commit" in e for e in errors))

    def test_success_rejects_a_path_instead_of_an_opaque_manifest_id(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            source_manifest_id="C:\\private\\manifest.json",
            software_versions="python=synthetic; commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="approximate method: synthetic Taylor; limitation: synthetic strata only",
            estimate="0.1", standard_error="0.05", ci_lower="0.002", ci_upper="0.198",
            p_value="0.04", q_value_by="0.04", p_bonferroni="0.04", n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("opaque source_manifest_id" in e for e in errors))

    def test_success_rejects_unverified_or_not_applicable_design_choices(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="not_applicable",
            psu_status="not_applicable",
            stratum_status="not_released",
            variance_design="Taylor linearization",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("verified weight choice" in e for e in errors))
        self.assertTrue(any("verified PSU" in e for e in errors))
        self.assertTrue(any("approximate method:" in e for e in errors))

    def test_success_with_verified_unweighted_and_unreleased_stratum_needs_approximation(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="Taylor linearization",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("approximate method:" in e for e in errors))
        self.assertTrue(any("limitation:" in e for e in errors))

    def test_unreleased_stratum_approximation_requires_limitation_text(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="approximate method: synthetic Taylor",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("limitation:" in e for e in errors))

    def test_unreleased_stratum_accepts_explicit_chinese_method_and_limitation_labels(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="近似方法：合成Taylor线性化；局限：未体现官方隐式方差分层",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_model="70",
        )
        self.assertEqual(validate_rows([row], self.fields, self.required), [])

    def test_family_size_includes_unestimable_hypotheses_and_adjustments_are_checked(self):
        success = self.base_row()
        success.update(
            analysis_id="synthetic-success",
            multiple_testing_family="synthetic_full;K=2",
            fit_status="success",
            estimability_review_status="reviewed_pass",
            estimability_review_id="synthetic-review-v1",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="approximate method: synthetic Taylor; limitation: synthetic strata only",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.01",
            q_value_by="0.03",
            p_bonferroni="0.02",
            n_model="70",
        )
        inestimable = self.base_row()
        inestimable.update(
            analysis_id="synthetic-inestimable",
            multiple_testing_family="synthetic_full;K=2",
            fit_status="inestimable",
        )
        self.assertEqual(validate_rows([success, inestimable], self.fields, self.required), [])

        success["q_value_by"] = "0.02"
        errors = validate_rows([success, inestimable], self.fields, self.required)
        self.assertTrue(any("q_value_by does not match" in e for e in errors))

    def test_family_row_count_must_match_declared_k(self):
        first = self.base_row()
        first["analysis_id"] = "synthetic-a"
        first["multiple_testing_family"] = "synthetic_full;K=3"
        second = self.base_row()
        second["analysis_id"] = "synthetic-b"
        second["multiple_testing_family"] = "synthetic_full;K=3"
        errors = validate_rows([first, second], self.fields, self.required)
        self.assertTrue(any("contains 2 rows but declares K=3" in e for e in errors))

    def test_success_requires_pair_level_estimability_review(self):
        row = self.base_row()
        row.update(
            fit_status="success",
            data_release="synthetic; release_id=synthetic-v1",
            software_versions="commit=" + "b" * 40,
            weight_status="verified_unweighted",
            psu_status="verified_used",
            psu_id="synthetic_psu",
            stratum_status="not_released",
            variance_design="approximate method: synthetic Taylor; limitation: synthetic strata only",
            estimate="0.1",
            standard_error="0.05",
            ci_lower="0.002",
            ci_upper="0.198",
            p_value="0.04",
            q_value_by="0.04",
            p_bonferroni="0.04",
            n_model="70",
        )
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("estimability_review_status=reviewed_pass" in e for e in errors))
        self.assertTrue(any("requires estimability_review_id" in e for e in errors))
        row["estimability_review_status"] = "reviewed_pass"
        row["estimability_review_id"] = "synthetic-rule-v1:pair-001"
        self.assertEqual(validate_rows([row], self.fields, self.required), [])

    def test_reviewed_pass_requires_reference_and_cannot_conflict_with_inestimable_fit(self):
        row = self.base_row()
        row.update(fit_status="inestimable", estimability_review_status="reviewed_pass")
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("reviewed_pass requires estimability_review_id" in e for e in errors))
        self.assertTrue(any("inestimable fit cannot have estimability_review_status=reviewed_pass" in e for e in errors))
        row["estimability_review_id"] = "synthetic-rule-v1:pair-001"
        errors = validate_rows([row], self.fields, self.required)
        self.assertTrue(any("inestimable fit cannot have estimability_review_status=reviewed_pass" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
