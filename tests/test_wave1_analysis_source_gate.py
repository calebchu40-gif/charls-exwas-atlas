import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from project_paths import PRIVATE_ROOT  # noqa: E402
from require_verified_wave1_frame import require_verified_wave1_frame  # noqa: E402


class Wave1AnalysisSourceGateTests(unittest.TestCase):
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
