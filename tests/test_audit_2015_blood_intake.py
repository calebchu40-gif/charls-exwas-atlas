import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_2015_blood_intake import (
    EXPECTED_OFFICIAL_BLOOD_SHA1,
    REQUIRED_FIELDS,
    inspect_stata_metadata,
    verify_official_artifact_sha1,
)


class Blood2015IntakeTests(unittest.TestCase):
    def test_official_sha1_is_pinned_and_verifier_fails_closed(self):
        self.assertEqual(EXPECTED_OFFICIAL_BLOOD_SHA1, "de5b1d80e9b72d61b690dff19b191f50f21ee8c5")
        payload = b"synthetic test artifact; not CHARLS data"
        expected = hashlib.sha1(payload).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "artifact.bin"
            path.write_bytes(payload)
            self.assertEqual(verify_official_artifact_sha1(path, expected), expected)
            with self.assertRaisesRegex(ValueError, "does not match the official"):
                verify_official_artifact_sha1(path, "0" * 40)

    def test_metadata_gate_requires_all_official_fields_and_expected_release_rows(self):
        frame = pd.DataFrame({name: [0, 1] for name in REQUIRED_FIELDS})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic_blood.dta"
            pyreadstat.write_dta(frame, str(path))
            result = inspect_stata_metadata(path, expected_rows=2)
            self.assertTrue(result["metadata_only"])
            self.assertFalse(result["respondent_values_read"])
            self.assertEqual(result["row_count_from_stata_header"], 2)
            self.assertEqual(result["required_fields_present"], len(REQUIRED_FIELDS))
            with self.assertRaisesRegex(ValueError, "row count does not match"):
                inspect_stata_metadata(path, expected_rows=13_420)

            incomplete = frame.drop(columns="bl_cysc")
            pyreadstat.write_dta(incomplete, str(path))
            with self.assertRaisesRegex(ValueError, "missing required official fields"):
                inspect_stata_metadata(path, expected_rows=2)


if __name__ == "__main__":
    unittest.main()
