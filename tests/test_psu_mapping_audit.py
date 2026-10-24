import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_charls_psu_mapping import normalize_codes, read_psu_map_candidate


class PsuMappingAuditTests(unittest.TestCase):
    def test_normalizes_community_keys_without_changing_text_codes(self):
        values = pd.Series([" 001.0", "", None, "A02"])
        result = normalize_codes(values)
        self.assertEqual(result.iloc[0], "001")
        self.assertTrue(result.iloc[1:3].isna().all())
        self.assertEqual(result.iloc[3], "A02")

    def test_rejects_duplicate_community_keys(self):
        mapping = pd.DataFrame({
            "communityID": ["001", "001"],
            "province": ["p", "p"], "city": ["c", "c"],
            "urban_nbs": [1, 1], "areatype": [1, 1],
        })
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "psu.dta"
            with patch("audit_charls_psu_mapping.pyreadstat.read_dta", return_value=(mapping, None)):
                with self.assertRaisesRegex(ValueError, "one nonmissing row per communityID"):
                    read_psu_map_candidate(path)


if __name__ == "__main__":
    unittest.main()
