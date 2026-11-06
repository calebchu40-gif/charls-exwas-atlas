#!/usr/bin/env python3
"""Cross-wave stability of the exposure-exposure network.

Reads the per-wave network JSON files and compares edges that appear in more
than one wave: sign agreement and the correlation of edge strengths.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site-prototype" / "dist"
OUT = SITE / "network_stability_v1.json"
WAVES = ("2011", "2013", "2015")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    networks = {}
    for wave in WAVES:
        path = SITE / f"exposure_network_{wave}_v1.json"
        if path.is_file():
            networks[wave] = json.loads(path.read_text(encoding="utf-8"))
    edges = {wave: {tuple(sorted((edge["source"], edge["target"]))): edge for edge in payload["edges"]}
             for wave, payload in networks.items()}

    pairs = set()
    for mapping in edges.values():
        pairs |= set(mapping)
    rows = []
    for pair in sorted(pairs):
        values = {wave: mapping[pair]["rho"] for wave, mapping in edges.items() if pair in mapping}
        qs = {wave: mapping[pair]["q"] for wave, mapping in edges.items() if pair in mapping}
        if len(values) < 2:
            continue
        signs = {1 if value > 0 else -1 for value in values.values()}
        xs = list(values.values())
        mean = sum(xs) / len(xs)
        sd = math.sqrt(sum((value - mean) ** 2 for value in xs) / len(xs)) if len(xs) > 1 else 0.0
        rows.append({
            "pair": list(pair),
            "waves": sorted(values),
            "rho": values,
            "q": qs,
            "sign_consistent": len(signs) == 1,
            "mean_rho": mean,
            "sd_rho": sd,
        })
    complete = [row for row in rows if len(row["waves"]) == len(networks)]
    payload = {
        "schema_version": 1,
        "waves": list(networks),
        "edges_in_multiple_waves": len(rows),
        "edges_in_all_waves": len(complete),
        "sign_consistent": sum(1 for row in rows if row["sign_consistent"]),
        "sign_consistent_fraction": round(
            sum(1 for row in rows if row["sign_consistent"]) / len(rows), 3) if rows else 0,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
                   encoding="utf-8")
    print(json.dumps({k: payload[k] for k in
                      ("edges_in_multiple_waves", "edges_in_all_waves", "sign_consistent_fraction")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
