"""Fail closed when the GitHub Pages payload contains non-site files."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ALLOWED_SUFFIXES = {".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".js", ".json", ".png", ".svg", ".webp", ".woff", ".woff2"}
ALLOWED_DOTFILES = {".nojekyll"}


def validate_payload(root: Path) -> list[str]:
    """Return validation errors for a browser-facing static site directory."""
    errors: list[str] = []
    if not root.is_dir():
        return [f"Site payload directory does not exist: {root}"]

    for required in ("index.html", "app.js"):
        if not (root / required).is_file() or (root / required).stat().st_size == 0:
            errors.append(f"Required site file is missing or empty: {required}")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name not in ALLOWED_DOTFILES and path.suffix.lower() not in ALLOWED_SUFFIXES:
            errors.append(f"Unexpected non-site file type: {path.relative_to(root)}")
            continue
        if path.suffix.lower() == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"Invalid JSON catalog {path.relative_to(root)}: {exc}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site-prototype/dist")
    errors = validate_payload(root)
    if errors:
        print("Public site payload validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated public site payload: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
