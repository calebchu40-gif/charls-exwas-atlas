import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from project_paths import require_private_path


class PrivatePathTests(unittest.TestCase):
    def test_sync_folder_is_rejected(self):
        unsafe = Path(tempfile.gettempdir()) / "OneDrive" / "CHARLS_ExWAS_Atlas" / "qa.csv"
        with self.assertRaises(ValueError):
            require_private_path(unsafe)

    def test_local_path_is_allowed(self):
        local = Path(tempfile.gettempdir()) / "CHARLS_ExWAS_Atlas" / "qa.csv"
        self.assertEqual(require_private_path(local), local.resolve())


if __name__ == "__main__":
    unittest.main()
