from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_public_association_release import PUBLIC_ROW_FIELDS, build_payload  # noqa: E402
from validate_public_site_payload import validate_association_payload  # noqa: E402


class PublicAssociationReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = []
        self.reviews = {}
        for index in (1, 2):
            analysis_id = f"synthetic-{index}"
            row = {field: "" for field in PUBLIC_ROW_FIELDS}
            row.update(
                analysis_id=analysis_id,
                wave="2011",
                exposure_concept_id=f"exposure-{index}",
                phenotype_concept_id=f"phenotype-{index}",
                model_id="M1",
                fit_status="inestimable",
                multiple_testing_family="synthetic_main;K=2",
            )
            self.rows.append(row)
            self.reviews[analysis_id] = {
                "analysis_id": analysis_id,
                "decision": "approved_public_aggregate",
                "review_record_id": "review-record-1",
                "reviewer_reference": "methods-reviewer-1",
                "reviewed_at": "2026-10-27T10:00:00+08:00",
                "reviewed_result_sha256": "a" * 64,
            }

    def test_complete_approved_family_builds_minimal_payload(self) -> None:
        payload = build_payload(self.rows, self.reviews, "a" * 64, "2026-10-27T10:00:00+08:00")
        self.assertEqual(payload["release_status"], "disclosure_reviewed")
        self.assertEqual(payload["families"][0]["family_size"], 2)
        self.assertEqual(len(payload["families"][0]["rows"]), 2)
        self.assertNotIn("multiple_testing_family", payload["families"][0]["rows"][0])
        self.assertEqual(validate_association_payload(payload), [])

    def test_any_withheld_hypothesis_withholds_the_whole_family(self) -> None:
        self.reviews["synthetic-2"]["decision"] = "withheld"
        with self.assertRaisesRegex(ValueError, "no complete multiplicity family"):
            build_payload(self.rows, self.reviews, "a" * 64)

    def test_reviews_must_cover_exactly_all_analysis_rows(self) -> None:
        self.reviews.pop("synthetic-2")
        with self.assertRaisesRegex(ValueError, "cover exactly every result row"):
            build_payload(self.rows, self.reviews, "a" * 64)

    def test_review_must_match_the_exact_result_file_hash(self) -> None:
        with self.assertRaisesRegex(ValueError, "does not match the exact result file"):
            build_payload(self.rows, self.reviews, "b" * 64)

    def test_family_declared_size_must_be_consistent_and_complete(self) -> None:
        self.rows[1]["multiple_testing_family"] = "synthetic_main;K=3"
        with self.assertRaisesRegex(ValueError, "inconsistent declared K"):
            build_payload(self.rows, self.reviews, "a" * 64)

    def test_public_payload_rejects_private_or_nonallowlisted_fields(self) -> None:
        payload = build_payload(self.rows, self.reviews, "a" * 64)
        payload["families"][0]["rows"][0]["local_sha256"] = "private"
        errors = validate_association_payload(payload)
        self.assertTrue(any("non-allowlisted fields" in error for error in errors))

    def test_public_payload_rejects_incomplete_family(self) -> None:
        payload = build_payload(self.rows, self.reviews, "a" * 64)
        payload["families"][0]["rows"].pop()
        errors = validate_association_payload(payload)
        self.assertTrue(any("complete declared K" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
