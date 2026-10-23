import unittest
import json
from pathlib import Path

from scripts.site_catalog_shards import ROLES, rows_for_role
from scripts.build_ep_atlas_metadata import FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS

ROOT = Path(__file__).resolve().parents[1]


class SiteCatalogShardTests(unittest.TestCase):
    def test_role_filter_keeps_dual_role_rows_in_both_catalogs(self):
        records = [
            {"Variable.Name": "e_only", "epcf": "e"},
            {"Variable.Name": "dual", "epcf": "e,p"},
            {"Variable.Name": "reverse_dual", "epcf": "p, e"},
            {"Variable.Name": "p_only", "epcf": "p"},
            {"Variable.Name": "metadata", "epcf": "c"},
        ]
        self.assertEqual(
            [row["Variable.Name"] for row in rows_for_role(records, "e")],
            ["e_only", "dual", "reverse_dual"],
        )
        self.assertEqual(
            [row["Variable.Name"] for row in rows_for_role(records, "p")],
            ["dual", "reverse_dual", "p_only"],
        )
        self.assertEqual(
            [row["Variable.Name"] for row in rows_for_role(records, "c")],
            ["metadata"],
        )

    def test_rejects_unknown_catalog_role(self):
        with self.assertRaises(ValueError):
            rows_for_role([], "x")

    def test_generated_site_role_shards_match_master_catalog(self):
        master = json.loads((ROOT / "site-prototype/dist/catalog.json").read_text(encoding="utf-8"))
        key = lambda row: (row.get("Source.Wave"), row.get("Variable.Name", "").lower(), row.get("epcf"), row.get("category"), row.get("subcategory"))
        for role in ROLES:
            shard = json.loads((ROOT / f"site-prototype/dist/catalog_{role}.json").read_text(encoding="utf-8"))
            expected = rows_for_role(master, role)
            self.assertEqual([key(row) for row in shard], [key(row) for row in expected])
            for row in shard:
                self.assertEqual(row["waves"], row["Source.Wave"])
                self.assertEqual(row["value_labels"], row["Value.Labels"])

    def test_both_metadata_pipelines_rebuild_role_shards_after_all_catalog_edits(self):
        self.assertEqual(FINALIZATION_PIPELINE_SCRIPTS[-1], "site_catalog_shards.py")
        self.assertEqual(FULL_PIPELINE_SCRIPTS[-1], "site_catalog_shards.py")
        for pipeline in (FINALIZATION_PIPELINE_SCRIPTS, FULL_PIPELINE_SCRIPTS):
            self.assertLess(pipeline.index("refresh_candidate_series_review_status.py"), len(pipeline) - 1)


if __name__ == "__main__":
    unittest.main()
