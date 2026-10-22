"""Portable locations for private CHARLS files used by project scripts.

Set CHARLS_EXWAS_PRIVATE_ROOT to the local, access-controlled workspace for
private derived files, or CHARLS_EXWAS_DATA_DIR to override the wave-table path.
No CHARLS microdata should be placed in the synchronized project directory.
"""
import os
from pathlib import Path


_local_base = Path(os.environ.get("LOCALAPPDATA", str(Path.home())))
PRIVATE_ROOT = Path(
    os.environ.get("CHARLS_EXWAS_PRIVATE_ROOT", str(_local_base / "CHARLS_ExWAS_Atlas"))
)
WAVE_DATA_DIR = Path(
    os.environ.get("CHARLS_EXWAS_DATA_DIR", str(PRIVATE_ROOT / "derived_wave_tables"))
)
