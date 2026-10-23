"""Build role-specific static catalog files from the audited master catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROLES = ("e", "p", "c")


def rows_for_role(records: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    if role not in ROLES:
        raise ValueError(f"unsupported catalog role: {role}")
    return [
        record for record in records
        if role in {part.strip().lower() for part in str(record.get("epcf", "")).split(",")}
    ]


def write_role_catalogs(records: list[dict[str, Any]], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for role in ROLES:
        path = output_dir / f"catalog_{role}.json"
        path.write_text(
            json.dumps(rows_for_role(records, role), ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        paths[role] = path
    return paths


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    master_path = root / "site-prototype" / "dist" / "catalog.json"
    records = json.loads(master_path.read_text(encoding="utf-8"))
    paths = write_role_catalogs(records, master_path.parent)
    for role, path in paths.items():
        print(f"catalog_{role}: rows={len(rows_for_role(records, role))}; bytes={path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
