import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_available_charls_intake_gates import run_available_gates


class AvailableIntakeGatesTests(unittest.TestCase):
    def test_missing_inputs_are_reported_as_skipped_without_reading_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_available_gates(
                root / "Weights.dta", root / "Blood_Data_2015_download", root / "Blood_Data_2015.dta"
            )
        self.assertTrue(result["metadata_only"])
        self.assertFalse(result["respondent_values_read"])
        self.assertEqual(result["wave_2013_weights"]["status"], "skipped_missing_input")
        self.assertEqual(result["wave_2015_blood"]["status"], "skipped_missing_input")

    def test_partial_blood_input_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "download.zip"
            artifact.write_bytes(b"placeholder; gate must not accept incomplete pair")
            result = run_available_gates(root / "Weights.dta", artifact, root / "Blood_Data_2015.dta")
        self.assertEqual(
            result["wave_2015_blood"],
            {"status": "skipped_incomplete_input_set", "download_artifact_present": True, "stata_file_present": False},
        )

    def test_data_under_cloud_sync_path_is_rejected(self):
        with self.assertRaises(ValueError):
            run_available_gates(
                Path("C:/Users/example/OneDrive/CHARLS/Weights.dta"),
                Path("C:/Users/example/OneDrive/CHARLS/Blood.zip"),
                Path("C:/Users/example/OneDrive/CHARLS/Blood.dta"),
            )


if __name__ == "__main__":
    unittest.main()
