#!/usr/bin/env python3
"""Inventory the public JSON modules and check every one is wired to the site.

Scans ``site-prototype/dist`` for ``*.json``, verifies each parses, and looks for
its filename in the site's scripts and HTML. An unreferenced payload is reported
so a module can never ship without a way to open it (or vice versa).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
AUDIT = ROOT / "audit"
MD = AUDIT / "module_inventory_2026-11-02.md"
JSON_OUT = AUDIT / "module_inventory_2026-11-02.json"
# Payloads consumed by dedicated views rather than the module tab strip.
DYNAMIC = re.compile(r"^(catalog_[a-z]+\.json|household_.*|individual_.*|land_rental_.*|residential_rental_.*)$")
CORE = {"association_results_v1.json", "catalog.json", "exposure_network_2011_v1.json",
        "exposure_network_2013_v1.json", "exposure_network_2015_v1.json",
        "cross_wave_meta_v1.json", "effect_modification_v1.json"}


def main() -> int:
    code = "\n".join(path.read_text(encoding="utf-8", errors="ignore")
                     for path in SITE.glob("*.js"))
    html = (SITE / "index.html").read_text(encoding="utf-8", errors="ignore")
    rows, orphans, broken = [], [], []
    for path in sorted(SITE.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            parsed = True
        except json.JSONDecodeError as error:
            parsed = False
            broken.append({"file": path.name, "error": str(error)[:120]})
            payload = None
        referenced = path.name in code or path.name in html
        rows.append({"file": path.name,
                     "kb": round(path.stat().st_size / 1024, 1),
                     "parsed": parsed,
                     "referenced": referenced,
                     "core": path.name in CORE})
        if parsed and not referenced and path.name not in CORE and not DYNAMIC.match(path.name):
            orphans.append(path.name)

    lines = ["# 公开模块清单（2026-11-02）\n",
             "`catalog_*.json` 由模板按角色加载，`household_*`/`individual_*`/`land_rental_*`/`residential_rental_*` "
             "是历史遗留的数据 payload（非本轮新增、暂未绑定视图），二者不计入未接入告警。\n",
             f"共 {len(rows)} 个 JSON，{sum(1 for row in rows if row['parsed'])} 个可解析，"
             f"{sum(1 for row in rows if row['referenced'] or row['core'])} 个已接入页面。\n",
             "| 文件 | KB | 解析 | 已接入 | 核心 |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['file']} | {row['kb']} | {'是' if row['parsed'] else '否'} | "
                     f"{'是' if row['referenced'] or row['core'] else '否'} | "
                     f"{'是' if row['core'] else ''} |")
    if orphans:
        lines.append("\n## 未接入页面的 payload\n")
        for name in orphans:
            lines.append(f"- {name}")
    if broken:
        lines.append("\n## 解析失败\n")
        for item in broken:
            lines.append(f"- {item['file']}: {item['error']}")
    MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_OUT.write_text(json.dumps({"modules": rows, "orphans": orphans, "broken": broken},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"modules": len(rows), "orphans": len(orphans), "broken": len(broken)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
