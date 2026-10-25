"""Fast downstream refresh for the reviewed 2011 DA010 metadata update.

Use only after the upstream candidate catalog and source crosswalk are current.
For changes to upstream mappings or other topics, run build_ep_atlas_metadata.py.
This path applies the DA010 review, refreshes browser-facing derivatives, and
checks the formal lock inventory without replaying unrelated topic builders.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEPS = (
    "apply_2011_chronic_treatment_storage_review.py",
    "site_catalog_shards.py",
    "build_candidate_pair_explorer.py",
    "summarize_value_label_coverage.py",
    "validate_do_not_analyze_triage.py",
)


def main() -> int:
    for script in STEPS:
        path = ROOT / "scripts" / script
        print(f"Running {script}", flush=True)
        subprocess.run([sys.executable, str(path)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
