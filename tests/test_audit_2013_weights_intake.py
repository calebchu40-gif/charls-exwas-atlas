import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_2013_weights_intake import audit_weights_header  # noqa: E402


class Wave2WeightsIntakeTests(unittest.TestCase):
    def test_hash_and_header_pass_without_reading_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "Weights.dta"
            pyreadstat.write_dta(
                pd.DataFrame({
                    "ID": ["synthetic-id"],
                    "crosssection": [1],
                    "longitudinal": [0],
                    "INDV_weight": [1.0],
                }),
                str(source),
            )
            expected = hashlib.sha1(source.read_bytes()).hexdigest()
            result = audit_weights_header(source, expected_sha1=expected)
            self.assertTrue(result["metadata_only"])
            self.assertFalse(result["respondent_values_read"])
            self.assertEqual(result["required_fields_present"], 3)
            self.assertEqual(result["weight_field_names"], ["INDV_weight"])
            self.assertNotIn("synthetic-id", str(result))

    def test_rejects_wrong_artifact_hash_before_metadata_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "Weights.dta"
            source.write_bytes(b"not an official file")
            with self.assertRaisesRegex(ValueError, "does not match the official"):
                audit_weights_header(source)

    def test_rejects_wrong_release_schema_even_when_hash_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "Weights.dta"
            pyreadstat.write_dta(
                pd.DataFrame({"ID": ["synthetic-id"], "INDV_weight": [1.0]}),
                str(source),
            )
            expected = hashlib.sha1(source.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "missing required fields"):
                audit_weights_header(source, expected_sha1=expected)


if __name__ == "__main__":
    unittest.main()
