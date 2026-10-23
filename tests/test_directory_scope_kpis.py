import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DirectoryScopeKpiTests(unittest.TestCase):
    def test_homepage_reports_exposure_and_phenotype_counts_separately(self):
        scope = json.loads((ROOT / "audit/directory_scope_counts_v1.json").read_text(encoding="utf-8"))
        html = (ROOT / "site-prototype/dist/index.html").read_text(encoding="utf-8")
        match = re.search(r'<div class="stats"[^>]*>(.*?)</div>\s*<p class="stats-note">(.*?)</p>', html, re.S)
        self.assertIsNotNone(match)
        cards = re.findall(r'<div class="stat"><b>([^<]+)</b><span>([^<]+)</span></div>', match.group(1))
        self.assertEqual(
            cards,
            [
                (f"{scope['exposure_concept_ids_including_dual']:,}", "暴露候选概念"),
                (f"{scope['phenotype_concept_ids_including_dual']:,}", "表型候选概念"),
                ("5", "调查波次：2011–2020"),
                ("0", "正式关联模型"),
            ],
        )
        unique = scope["candidate_concept_ids"]
        dual = scope["exposure_concept_ids_including_dual"] + scope["phenotype_concept_ids_including_dual"] - unique
        self.assertIn(f"{unique:,} 个 E/P 候选概念", match.group(2))
        self.assertIn(f"{dual} 个同时承担暴露与表型角色", match.group(2))
        self.assertIn(f"{scope['wave_field_mapping_rows']:,} 条概念—源字段映射", match.group(2))
        self.assertIn("不是样本量或关联结果", match.group(2))


if __name__ == "__main__":
    unittest.main()
