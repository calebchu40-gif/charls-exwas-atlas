import csv
import json
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "site-prototype" / "dist"


class ValueLabelCoverageSummaryTests(unittest.TestCase):
    def test_coverage_csv_matches_final_role_shards(self):
        expected = defaultdict(lambda: {"rows": 0, "fields": set(), "labels": 0})
        for role in ("e", "p"):
            rows = json.loads((DIST / f"catalog_{role}.json").read_text(encoding="utf-8"))
            for row in rows:
                key = (role, row.get("category", ""), row.get("subcategory", ""))
                bucket = expected[key]
                bucket["rows"] += 1
                bucket["fields"].add((row.get("Source.Wave", ""), row.get("Variable.Name", "").lower()))
                bucket["labels"] += bool(str(row.get("Value.Labels", "")).strip())

        with (ROOT / "audit/charls_ep_catalog_value_label_coverage_v1.csv").open(encoding="utf-8-sig", newline="") as handle:
            actual = {
                (row["epcf"], row["category"], row["subcategory"]): (
                    int(row["field_category_rows"]),
                    int(row["distinct_wave_fields"]),
                    int(row["rows_with_reviewed_labels"]),
                )
                for row in csv.DictReader(handle)
            }
        wanted = {key: (value["rows"], len(value["fields"]), value["labels"]) for key, value in expected.items()}
        self.assertEqual(actual, wanted)

    def test_markdown_generic_pending_counts_match_final_catalogues(self):
        counts = {}
        for role in ("e", "p", "c"):
            rows = json.loads((DIST / f"catalog_{role}.json").read_text(encoding="utf-8"))
            counts[role] = sum(row.get("Value.Label.Review", "").strip().lower() == "not yet reviewed" for row in rows)
        report = (ROOT / "audit/charls_ep_catalog_value_label_coverage_v1.md").read_text(encoding="utf-8")
        self.assertIn(f"E/P中精确状态为`not yet reviewed`的目录行：{counts['e'] + counts['p']:,}；C目录对应行：{counts['c']:,}", report)
        self.assertRegex(report, r"读取最终网站角色分片`catalog_e\.json`、`catalog_p\.json`和`catalog_c\.json`")


if __name__ == "__main__":
    unittest.main()
