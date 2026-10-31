"""Tests for the MIT-licensed official lunar lookup.

The lookup table is CHARLS's own published ``lunar2solar.mmat`` (MIT). No
third-party conversion library is imported here, and no participant data is
read.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lunar_lookup import (  # noqa: E402
    DEFAULT_MMAT,
    OFFICIAL_MMAT_SHA256,
    LunarLookupError,
    OfficialLunarLookup,
)

HAVE_TABLE = DEFAULT_MMAT.is_file()


@unittest.skipUnless(HAVE_TABLE, "official lunar table is not present in this checkout")
class OfficialLunarLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lookup = OfficialLunarLookup()

    def test_table_identity_and_shape(self):
        self.assertEqual(self.lookup.sha256, OFFICIAL_MMAT_SHA256)
        self.assertEqual(self.lookup.counts, {"total": 51470, "ordinary": 49949, "leap": 1521})

    def test_known_conversions(self):
        self.assertEqual(self.lookup.to_solar(1900, 1, 1), "19000131")
        self.assertEqual(self.lookup.to_solar(1900, 8, 1, leap=True), "19000924")
        self.assertEqual(self.lookup.to_solar(1976, 8, 8, leap=True), "19761001")
        self.assertEqual(self.lookup.from_solar(1976, 10, 1).lunar, "19760808")
        self.assertTrue(self.lookup.from_solar(1976, 10, 1).leap)

    def test_leap_and_ordinary_months_are_distinct(self):
        ordinary = self.lookup.to_solar(1900, 8, 1, leap=False)
        leap = self.lookup.to_solar(1900, 8, 1, leap=True)
        self.assertIsNotNone(ordinary)
        self.assertIsNotNone(leap)
        self.assertNotEqual(ordinary, leap)

    def test_full_table_round_trips(self):
        mismatches = 0
        checked = 0
        for row in self.lookup.iter_solar():
            year, month, day = int(row.lunar[:4]), int(row.lunar[4:6]), int(row.lunar[6:8])
            converted = self.lookup.to_solar(year, month, day, row.leap)
            checked += 1
            if converted != row.solar:
                mismatches += 1
        self.assertEqual(checked, 51470)
        self.assertEqual(mismatches, 0)

    def test_unknown_and_out_of_domain_keys_return_none(self):
        self.assertIsNone(self.lookup.to_solar(1899, 12, 1))
        self.assertIsNone(self.lookup.to_solar(1900, 13, 1))
        self.assertIsNone(self.lookup.to_solar(1900, 1, 31))
        self.assertIsNone(self.lookup.from_solar(1801, 1, 1))

    def test_altered_table_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "altered.mmat"
            shutil.copyfile(DEFAULT_MMAT, copy)
            data = bytearray(copy.read_bytes())
            data[-1] ^= 0xFF
            copy.write_bytes(data)
            with self.assertRaises(LunarLookupError):
                OfficialLunarLookup(path=copy)

    def test_missing_table_is_rejected(self):
        with self.assertRaises(LunarLookupError):
            OfficialLunarLookup(path=Path(tempfile.gettempdir()) / "does-not-exist.mmat")


if __name__ == "__main__":
    unittest.main()
