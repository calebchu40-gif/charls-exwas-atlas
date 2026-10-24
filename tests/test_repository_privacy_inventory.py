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
    "raw_response_counts", "sample_counts", "qa_outputs", "value_counts",
    "candidate_adjustment_coverage", "cooking_fuel_crosswalk",
)
PUBLIC_AGGREGATE = "audit/covariate_candidate_availability_v1.csv"
PUBLIC_AGGREGATE_COLUMNS = {
    "wave", "concept_id", "source_variables", "status", "respondent_n",
    "n_raw_available", "n_constructed_candidate", "candidate_min",
    "candidate_median", "candidate_max", "definition_note",
}


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
            if path.casefold().startswith("audit/")
            and any(marker in path.casefold() for marker in PRIVATE_QA_MARKERS)
        ]
        self.assertEqual([], unsafe, f"Private/local QA outputs are tracked: {unsafe}")

    def test_published_covariate_readiness_summary_is_aggregate_only(self):
        path = ROOT / PUBLIC_AGGREGATE
        self.assertTrue(path.is_file())
        import csv
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            self.assertEqual(PUBLIC_AGGREGATE_COLUMNS, set(reader.fieldnames or []))
            rows = list(reader)

        self.assertTrue(rows)
        # Any observed-value summaries are restricted to the explicitly
        # provisional year-difference age candidate; raw category counts stay private.
        summary_rows = [row for row in rows if row["candidate_min"] or row["candidate_median"] or row["candidate_max"]]
        self.assertTrue(summary_rows)
        self.assertTrue(all(
            row["concept_id"] == "age_reported_or_derived"
            and row["status"] == "year_difference_candidate_not_final_age"
            for row in summary_rows
        ))
        self.assertFalse(any(
            column.casefold() in {"id", "person_id", "respondent_id", "householdid", "communityid"}
            for column in (reader.fieldnames or [])
        ))


if __name__ == "__main__":
    unittest.main()
