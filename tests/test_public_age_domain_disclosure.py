from pathlib import Path
import unittest


class PublicAgeDomainDisclosureTests(unittest.TestCase):
    def test_method_panel_distinguishes_crosssection_flag_from_age_domain(self):
        html = (Path(__file__).resolve().parents[1] / "site-prototype" / "dist" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("主要受访者及其配偶都会接受访谈", html)
        self.assertIn("Wave 4 个体横截面权重覆盖这两类记录", html)
        self.assertIn("crosssection 标记不能单独解释为每条记录年龄均≥45岁", html)
        self.assertIn("预先确定目标年龄域并说明配偶记录的处理", html)


if __name__ == "__main__":
    unittest.main()
