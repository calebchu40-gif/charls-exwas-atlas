import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_public_site_payload import RESULT_ROW_FIELDS, validate_payload


class PublicSitePayloadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "index.html").write_text("<main>Atlas</main>", encoding="utf-8")
        (self.root / "app.js").write_text("console.log('Atlas');", encoding="utf-8")
        (self.root / "catalog.json").write_text(json.dumps({"rows": []}), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_accepts_browser_assets_and_valid_json(self):
        (self.root / "styles.css").write_text("body {}", encoding="utf-8")
        (self.root / ".nojekyll").write_text("", encoding="utf-8")
        self.assertEqual(validate_payload(self.root), [])

    def test_rejects_common_microdata_and_archive_formats_case_insensitively(self):
        for name in ("respondents.DTA", "lab.sas7bdat", "survey.XPT", "private.RData", "backup.ZIP", "records.xlsx"):
            (self.root / name).write_bytes(b"restricted")
        errors = validate_payload(self.root)
        self.assertEqual(len(errors), 6)
        self.assertTrue(all("Unexpected non-site file type" in error for error in errors))

    def test_rejects_unknown_file_types_and_invalid_json(self):
        (self.root / "payload.bin").write_bytes(b"unknown")
        (self.root / "broken.json").write_text("{", encoding="utf-8")
        errors = validate_payload(self.root)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("Unexpected non-site file type" in error for error in errors))
        self.assertTrue(any("Invalid JSON catalog" in error for error in errors))

    def test_requires_entry_point_files(self):
        (self.root / "index.html").unlink()
        errors = validate_payload(self.root)
        self.assertTrue(any("Required site file" in error and "index.html" in error for error in errors))

    def test_accepts_complete_reviewed_association_family(self):
        row = {field: "" for field in RESULT_ROW_FIELDS}
        row.update(
            analysis_id="synthetic-001", wave="2011", exposure_concept_id="e1",
            phenotype_concept_id="p1", model_id="M1", fit_status="inestimable",
            disclosure_status="approved_public_aggregate",
        )
        payload = {
            "schema_version": 1,
            "release_status": "disclosure_reviewed",
            "generated_at": "2026-10-27T10:00:00+08:00",
            "families": [{"family_id": "synthetic_main", "family_size": 1, "rows": [row]}],
        }
        (self.root / "association_results_v1.json").write_text(json.dumps(payload), encoding="utf-8")
        self.assertEqual(validate_payload(self.root), [])

    def test_rejects_private_fields_in_association_family(self):
        row = {field: "" for field in RESULT_ROW_FIELDS}
        row.update(
            analysis_id="synthetic-001", wave="2011", exposure_concept_id="e1",
            phenotype_concept_id="p1", model_id="M1", fit_status="inestimable",
            disclosure_status="approved_public_aggregate", private_file_path="C:/private/data.dta",
        )
        payload = {
            "schema_version": 1,
            "release_status": "disclosure_reviewed",
            "generated_at": "2026-10-27T10:00:00+08:00",
            "families": [{"family_id": "synthetic_main", "family_size": 1, "rows": [row]}],
        }
        (self.root / "association_results_v1.json").write_text(json.dumps(payload), encoding="utf-8")
        errors = validate_payload(self.root)
        self.assertTrue(any("non-allowlisted fields" in error for error in errors))

    def test_rejects_incomplete_association_family(self):
        row = {field: "" for field in RESULT_ROW_FIELDS}
        row.update(
            analysis_id="synthetic-001", wave="2011", exposure_concept_id="e1",
            phenotype_concept_id="p1", model_id="M1", fit_status="inestimable",
            disclosure_status="approved_public_aggregate",
        )
        payload = {
            "schema_version": 1,
            "release_status": "disclosure_reviewed",
            "generated_at": "2026-10-27T10:00:00+08:00",
            "families": [{"family_id": "synthetic_main", "family_size": 2, "rows": [row]}],
        }
        (self.root / "association_results_v1.json").write_text(json.dumps(payload), encoding="utf-8")
        errors = validate_payload(self.root)
        self.assertTrue(any("complete declared K" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
