"""Portable locations for private CHARLS files used by project scripts.

Set CHARLS_EXWAS_PRIVATE_ROOT to the local, access-controlled workspace for
private derived files, or CHARLS_EXWAS_DATA_DIR to override the wave-table path.
No CHARLS microdata should be placed in the synchronized project directory.
"""
import os
from pathlib import Path


def require_private_path(path: Path) -> Path:
    """Reject paths under common cloud-sync folders before using private data."""
    resolved = Path(path).expanduser().resolve()
    blocked = {"onedrive", "dropbox", "googledrive", "icloud drive", "icloud"}
    if any(part.casefold() in blocked for part in resolved.parts):
        raise ValueError(f"Private CHARLS data/output cannot use a sync folder: {resolved}")
    return resolved


_local_base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
PRIVATE_ROOT = require_private_path(Path(
    os.environ.get("CHARLS_EXWAS_PRIVATE_ROOT", str(_local_base / "CHARLS_ExWAS_Atlas"))
))
WAVE_DATA_DIR = require_private_path(Path(
    os.environ.get("CHARLS_EXWAS_DATA_DIR", str(PRIVATE_ROOT / "derived_wave_tables"))
))
QA_OUTPUT_DIR = require_private_path(Path(
    os.environ.get("CHARLS_EXWAS_QA_DIR", str(PRIVATE_ROOT / "qa_outputs"))
))
