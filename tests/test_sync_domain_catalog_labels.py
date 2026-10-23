import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_domain_catalog_labels.py"
SPEC = importlib.util.spec_from_file_location("sync_domain_catalog_labels", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DomainCatalogLabelSyncTests(unittest.TestCase):
    def test_fills_only_blank_fields_from_unique_wave_code_match(self):
        catalog = [{
            "Source.Wave": "2011", "Variable.Name": "da056_s1",
            "Value.Labels": "0=No; 1=Yes", "Value.Label.Source": "official.txt",
            "Value.Label.Review": "officially reviewed",
        }]
        fields = [
            {"wave": "2011", "code": "da056s1", "value_labels": "", "value_label_source": "", "value_label_status": ""},
            {"wave": "2015", "code": "da056s1", "value_labels": ""},
            {"wave": "2011", "code": "da056s1", "value_labels": "local reviewed label"},
        ]
        stats = MODULE.sync(catalog, [{"source_fields": fields}])
        self.assertEqual(stats["filled"], 1)
        self.assertEqual(fields[0]["value_labels"], "0=No; 1=Yes")
        self.assertEqual(fields[0]["value_label_source"], "official.txt")
        self.assertEqual(fields[0]["value_label_status"], "officially reviewed")
        self.assertEqual(fields[1]["value_labels"], "")
        self.assertEqual(fields[2]["value_labels"], "local reviewed label")

    def test_skips_disagreement_and_unreviewed_labels(self):
        catalog = [
            {"Source.Wave": "2011", "Variable.Name": "x1", "Value.Labels": "1=A", "Value.Label.Source": "a", "Value.Label.Review": "reviewed"},
            {"Source.Wave": "2011", "Variable.Name": "x1", "Value.Labels": "1=B", "Value.Label.Source": "b", "Value.Label.Review": "reviewed"},
            {"Source.Wave": "2011", "Variable.Name": "x2", "Value.Labels": "", "Value.Label.Source": "", "Value.Label.Review": "not yet reviewed"},
        ]
        fields = [{"wave": "2011", "code": "x1", "value_labels": ""}, {"wave": "2011", "code": "x2", "value_labels": ""}]
        stats = MODULE.sync(catalog, [{"source_fields": fields}])
        self.assertEqual(stats["ambiguous"], 1)
        self.assertEqual(stats["no_match"], 1)
        self.assertTrue(all(not field["value_labels"] for field in fields))


if __name__ == "__main__":
    unittest.main()
