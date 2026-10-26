from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_public_association_release as release_builder  # noqa: E402
from build_public_association_release import PUBLIC_ROW_FIELDS, build_payload  # noqa: E402
from validate_exwas_result_table import read_schema  # noqa: E402
from validate_public_site_payload import validate_association_payload, validate_payload  # noqa: E402


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

    def test_end_to_end_synthetic_result_review_and_site_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            private = temp_root / "private"
            output_root = temp_root / "repo"
            site = output_root / "site-prototype" / "dist"
            private.mkdir()
            site.mkdir(parents=True)
            (site / "index.html").write_text("<main>synthetic</main>", encoding="utf-8")
            (site / "app.js").write_text("// synthetic", encoding="utf-8")

            fields, required = read_schema()
            row = {field: ("documented" if required[field] == "yes" else "") for field in fields}
            row.update(
                analysis_id="synthetic-e2e-001",
                data_release="synthetic fixture only",
                wave="2011",
                exposure_concept_id="synthetic-exposure",
                phenotype_concept_id="synthetic-phenotype",
                fit_status="blocked_design_verification",
                estimability_review_status="pending",
                source_hash_status="unresolved",
                source_identity_status="unresolved",
                source_manifest_id="",
                weight_status="unresolved",
                psu_status="unresolved",
                stratum_status="unresolved",
                weight_id="",
                psu_id="",
                stratum_id="",
                multiple_testing_family="synthetic_e2e;K=1",
                variance_design="not fit-ready; synthetic end-to-end fixture",
            )
            results_path = private / "synthetic_results.csv"
            with results_path.open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
            digest = hashlib.sha256(results_path.read_bytes()).hexdigest()
            review_path = private / "synthetic_review.csv"
            with review_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=sorted(release_builder.REVIEW_FIELDS))
                writer.writeheader()
                writer.writerow({
                    "analysis_id": row["analysis_id"],
                    "decision": "approved_public_aggregate",
                    "review_record_id": "synthetic-review-v1",
                    "reviewer_reference": "synthetic-reviewer-v1",
                    "reviewed_at": "2026-10-27T10:00:00+08:00",
                    "reviewed_result_sha256": digest,
                })
            output = site / "association_results_v1.json"
            with patch.object(release_builder, "PRIVATE", private), patch.object(release_builder, "ROOT", output_root):
                payload = release_builder.write_release(results_path, review_path, output)
            self.assertEqual(payload["release_status"], "disclosure_reviewed")
            self.assertEqual(validate_payload(site), [])
            public_text = output.read_text(encoding="utf-8")
            self.assertNotIn(digest, public_text)
            self.assertNotIn(str(private), public_text)


if __name__ == "__main__":
    unittest.main()
