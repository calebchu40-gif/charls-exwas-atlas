"""Guard the public Git index against licensed CHARLS data and local QA outputs."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTECTED_DATA_SUFFIXES = {
    ".dta", ".sav", ".sas7bdat", ".rds", ".rdata", ".parquet", ".feather",
    ".por", ".xpt", ".dbf", ".sqlite", ".sqlite3", ".mdb", ".accdb",
}
PRIVATE_QA_MARKERS = (
    "pairwise_complete_n", "pairwise_availability", "complete_n",
    "raw_response_counts", "sample_counts", "qa_outputs",
)


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [path for path in result.stdout.decode("utf-8").split("\0") if path]


class RepositoryPrivacyInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = tracked_paths()

    def test_no_licensed_respondent_data_files_are_tracked(self):
        unsafe = [path for path in self.paths if Path(path).suffix.casefold() in PROTECTED_DATA_SUFFIXES]
        self.assertEqual([], unsafe, f"Protected respondent-data formats are tracked: {unsafe}")

    def test_private_pairwise_and_qa_count_outputs_are_not_tracked(self):
        unsafe = [
            path for path in self.paths
            if any(marker in path.casefold() for marker in PRIVATE_QA_MARKERS)
        ]
        self.assertEqual([], unsafe, f"Private/local QA outputs are tracked: {unsafe}")


if __name__ == "__main__":
    unittest.main()
