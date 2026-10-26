import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_2011_pilot_intake_metadata import ROLE_DOCUMENTS, ROLE_URLS  # noqa: E402
from project_paths import PRIVATE_ROOT  # noqa: E402
from prepare_charls_wave_tables import sha256_file  # noqa: E402
from require_verified_wave1_frame import require_verified_wave1_frame  # noqa: E402


class Wave1AnalysisSourceGateTests(unittest.TestCase):
    def test_synthetic_fully_reviewed_frame_passes_provenance_only(self):
        PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave1_analysis_gate_", dir=PRIVATE_ROOT) as temp:
            root = Path(temp)
            incoming = root / "incoming_2011_official"
            prepared = root / "derived_wave_tables"
            incoming.mkdir()
            prepared.mkdir()
            demo_dta = root / "synthetic_module.dta"
            pyreadstat.write_dta(pd.DataFrame({"ID": [1]}), str(demo_dta))
            all_data = incoming / "all_data.zip"
            with zipfile.ZipFile(all_data, "w") as archive:
                archive.write(demo_dta, "synthetic_module.dta")

            filenames = {
                "wave1_all_data": "all_data.zip",
                "psu": "PSU.dta", "weight": "Weight.dta", "blood": "Blood.dta",
            }
            source_inputs = {
                "all_data_archive": {
                    "filename": filenames["wave1_all_data"],
                    "bytes": all_data.stat().st_size,
                    "sha256": sha256_file(all_data),
                }
            }
            entries = []
            for role in ("psu", "weight", "blood"):
                path = incoming / filenames[role]
                pyreadstat.write_dta(pd.DataFrame({"ID": [1]}), str(path))
                source_inputs[role] = {
                    "filename": path.name, "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            for role in ROLE_URLS:
                item = source_inputs["all_data_archive" if role == "wave1_all_data" else role]
                entries.append({
                    "role": role, "official_document": ROLE_DOCUMENTS[role],
                    "source_page": ROLE_URLS[role], "original_filename": item["filename"],
                    "official_title": f"Synthetic fixture {role}",
                    "downloaded_at": "2026-10-27",
                    "identity_review_status": "verified_official_source",
                    "reviewed_local_sha256": item["sha256"],
                })
            intake = incoming / "intake_manifest.json"
            manifest_id = "charls2011-synthetic-gate"
            intake.write_text(json.dumps({
                "source_manifest_id": manifest_id,
                "source_identity_review": {
                    "status": "verified_official_source",
                    "reviewed_at": "2026-10-27",
                    "reviewer_note": "Synthetic code-path fixture only.",
                },
                "required_files": entries,
            }), encoding="utf-8")

            table = prepared / "CHARLS_wave2011_person_analytic.dta"
            pyreadstat.write_dta(pd.DataFrame({"ID": [1]}), str(table))
            (prepared / "prepared_data_manifest.json").write_text(json.dumps({
                "waves": [{
                    "wave": "2011", "source_review": {
                        "source_identity_status": "verified_official_source",
                        "source_manifest_id": manifest_id,
                    },
                    "source_inputs": source_inputs,
                    "prepared_output": {
                        "filename": table.name, "bytes": table.stat().st_size,
                        "sha256": sha256_file(table),
                    },
                }]
            }), encoding="utf-8")

            result = require_verified_wave1_frame(root)
            self.assertEqual(result["source_identity_status"], "verified_official_source")
            self.assertEqual(result["survey_design_status"], "still_requires_independent_review")

    def test_legacy_prepared_manifest_cannot_run_association_model(self):
        PRIVATE_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave1_analysis_gate_", dir=PRIVATE_ROOT) as temp:
            root = Path(temp)
            incoming = root / "incoming_2011_official"
            prepared = root / "derived_wave_tables"
            incoming.mkdir()
            prepared.mkdir()
            (incoming / "intake_manifest.json").write_text(json.dumps({
                "source_manifest_id": "charls2011-synthetic-v1",
                "source_identity_review": {"status": "verified_official_source"},
                "required_files": [],
            }), encoding="utf-8")
            (prepared / "prepared_data_manifest.json").write_text(json.dumps({
                "waves": [{"wave": "2011", "rows": 17705,
                           "output": "CHARLS_wave2011_person_analytic.dta"}]
            }), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "predates source-review provenance"):
                require_verified_wave1_frame(root)

    def test_analysis_gate_rejects_workspace_outside_protected_root(self):
        outside = Path(tempfile.gettempdir()) / "not_the_charls_private_root"
        with self.assertRaisesRegex(ValueError, "outside protected storage"):
            require_verified_wave1_frame(outside)


if __name__ == "__main__":
    unittest.main()
