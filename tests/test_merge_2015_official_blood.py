import hashlib
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.merge_2015_official_blood import (
    BLOOD_FIELDS,
    merge_blood_tables,
    validate_prepared_provenance,
)


class Wave3BloodMergeTests(unittest.TestCase):
    @staticmethod
    def blood_fixture(ids):
        data = {"id": ids}
        data.update({field: [1.0] * len(ids) for field in BLOOD_FIELDS})
        return pd.DataFrame(data)

    def test_left_merge_preserves_frame_and_crosssection_flag(self):
        prepared = pd.DataFrame({"ID": ["001", "002"], "crosssection": [1, 0], "exposure": [3, 4]})
        blood = self.blood_fixture(["001"])
        merged, qa = merge_blood_tables(prepared, blood)

        self.assertEqual(len(merged), len(prepared))
        self.assertEqual(merged["ID"].tolist(), ["001", "002"])
        self.assertEqual(merged["crosssection"].tolist(), [1, 0])
        self.assertEqual(merged.loc[0, "bl_wbc"], 1.0)
        self.assertTrue(pd.isna(merged.loc[1, "bl_wbc"]))
        self.assertEqual(qa["row_expansion"], False)
        self.assertIn("cross-sectional only", qa["blood_weight_scope"])

    def test_blood_respondent_missing_from_prepared_frame_fails(self):
        prepared = pd.DataFrame({"ID": ["001"], "crosssection": [1]})
        with self.assertRaisesRegex(ValueError, "IDs absent"):
            merge_blood_tables(prepared, self.blood_fixture(["999"]))

    def test_duplicate_ids_fail_closed(self):
        prepared = pd.DataFrame({"ID": ["001", "001"], "crosssection": [1, 1]})
        with self.assertRaisesRegex(ValueError, "must be complete and unique"):
            merge_blood_tables(prepared, self.blood_fixture(["001"]))

    def test_crosssection_flag_is_required(self):
        prepared = pd.DataFrame({"ID": ["001"]})
        with self.assertRaisesRegex(ValueError, "crosssection"):
            merge_blood_tables(prepared, self.blood_fixture(["001"]))

    def test_prepared_table_must_match_archive_and_output_hash_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / "CHARLS2015r.zip"
            prepared = root / "prepared.dta"
            archive.write_bytes(b"official archive fixture")
            prepared.write_bytes(b"prepared table fixture")
            source_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
            output_hash = hashlib.sha256(prepared.read_bytes()).hexdigest()
            record = {
                "source_archive": {"bytes": archive.stat().st_size, "sha256": source_hash},
                "prepared_output": {"filename": prepared.name, "bytes": prepared.stat().st_size,
                                    "sha256": output_hash},
            }
            validate_prepared_provenance(record, prepared, archive)
            archive.write_bytes(b"changed archive")
            with self.assertRaisesRegex(ValueError, "source archive"):
                validate_prepared_provenance(record, prepared, archive)


if __name__ == "__main__":
    unittest.main()
