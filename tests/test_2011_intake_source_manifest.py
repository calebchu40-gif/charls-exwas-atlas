import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_2011_pilot_intake_metadata import (  # noqa: E402
    ROLE_DOCUMENTS,
    ROLE_URLS,
    evaluate_source_manifest,
    refresh_manifest_after_file_change,
)


class IntakeSourceManifestTests(unittest.TestCase):
    def setUp(self):
        self.files = {
            role: {
                "status": "metadata_read",
                "file_name": f"{role}.dta" if role != "wave1_all_data" else "wave1.zip",
                "local_sha256": (str(index + 1) * 64),
            }
            for index, role in enumerate(ROLE_URLS)
        }
        self.manifest = {
            "source_manifest_id": "charls2011-synthetic-v1",
            "source_identity_review": {
                "status": "verified_official_source",
                "reviewed_at": "2026-10-26",
                "reviewer_note": "Synthetic review fixture; no participant data.",
            },
            "required_files": [
                {
                    "role": role,
                    "official_document": ROLE_DOCUMENTS[role],
                    "source_page": ROLE_URLS[role],
                    "original_filename": self.files[role]["file_name"],
                    "official_title": f"Synthetic title for {role}",
                    "downloaded_at": "2026-10-26",
                    "identity_review_status": "verified_official_source",
                    "reviewed_local_sha256": self.files[role]["local_sha256"],
                }
                for role in ROLE_URLS
            ],
        }

    def test_verified_identity_and_private_hash_evidence_are_distinct(self):
        result = evaluate_source_manifest(self.manifest, self.files)
        self.assertEqual(result["source_identity_status"], "verified_official_source")
        self.assertEqual(result["source_hash_status"], "private_local_sha256_recorded")
        self.assertEqual(result["source_manifest_id"], "charls2011-synthetic-v1")
        self.assertEqual(result["source_identity_review_errors"], [])

    def test_changed_received_file_hash_reopens_identity_gate(self):
        self.files["blood"]["local_sha256"] = "f" * 64
        result = evaluate_source_manifest(self.manifest, self.files)
        self.assertEqual(result["source_identity_status"], "unresolved")
        self.assertTrue(any("SHA-256 does not match" in e for e in result["source_identity_review_errors"]))

    def test_missing_official_file_stays_pending_and_does_not_claim_hash(self):
        self.files["psu"]["status"] = "missing_or_ambiguous"
        result = evaluate_source_manifest(self.manifest, self.files)
        self.assertEqual(result["source_identity_status"], "unavailable_pending_authorized_file")
        self.assertEqual(result["source_hash_status"], "unavailable_pending_authorized_file")

    def test_private_paths_are_not_valid_manifest_ids(self):
        self.manifest["source_manifest_id"] = r"C:\private\manifest.json"
        result = evaluate_source_manifest(self.manifest, self.files)
        self.assertEqual(result["source_identity_status"], "unresolved")
        self.assertEqual(result["source_manifest_id"], "")

    def test_changed_source_bytes_rotate_manifest_id_and_reopen_review(self):
        manifest = dict(self.manifest)
        manifest["required_files"] = [dict(row) for row in self.manifest["required_files"]]
        manifest["last_preflight_local_sha256"] = {
            role: self.files[role]["local_sha256"] for role in ROLE_URLS
        }
        changed_files = {role: dict(row) for role, row in self.files.items()}
        changed_files["weight"]["local_sha256"] = "e" * 64
        updated, rotated = refresh_manifest_after_file_change(manifest, changed_files)
        self.assertTrue(rotated)
        self.assertNotEqual(updated["source_manifest_id"], self.manifest["source_manifest_id"])
        self.assertEqual(updated["source_identity_review"]["status"], "unresolved")
        changed_role = next(x for x in updated["required_files"] if x["role"] == "weight")
        self.assertIsNone(changed_role["reviewed_local_sha256"])

    def test_initial_hash_capture_does_not_claim_source_identity(self):
        manifest = dict(self.manifest)
        manifest["source_identity_review"] = dict(self.manifest["source_identity_review"])
        manifest["source_identity_review"]["status"] = "unresolved"
        manifest.pop("last_preflight_local_sha256", None)
        updated, rotated = refresh_manifest_after_file_change(manifest, self.files)
        self.assertFalse(rotated)
        self.assertEqual(updated["source_identity_review"]["status"], "unresolved")
        self.assertEqual(len(updated["last_preflight_local_sha256"]), 4)


if __name__ == "__main__":
    unittest.main()
