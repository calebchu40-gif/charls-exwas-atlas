"""Run the unit suite and expose concise failure details in Actions annotations."""

from __future__ import annotations

import io
import os
import sys
import unittest
from pathlib import Path
from urllib.parse import quote


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0, str(root))
    suite = unittest.defaultTestLoader.discover("tests")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    output = stream.getvalue()
    print(output, end="", flush=True)

    failures = [("FAIL", test, detail) for test, detail in result.failures]
    failures.extend(("ERROR", test, detail) for test, detail in result.errors)
    if failures:
        details = ["## Unit test failures", ""]
        for kind, test, detail in failures:
            name = test.id()
            short_detail = " ".join(detail.strip().split())[-500:]
            annotation = quote(f"{kind}: {name} — {short_detail}", safe=" :/._-()")
            print(f"::error title=Unit test failure::{annotation}", flush=True)
            details.extend((f"### {kind}: `{name}`", "", "```text", detail.rstrip(), "```", ""))
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write("\n".join(details) + "\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
