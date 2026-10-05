import pathlib
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from file_sync import FileSync


class RobocopyCompletenessTests(unittest.TestCase):
    def test_reports_source_files_missing_after_successful_robocopy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            source = root / "source"
            target = root / "target"
            (source / "new folder").mkdir(parents=True)
            (source / "new folder" / "new-template.dotx").write_text("template")
            target.mkdir()

            with patch.dict("os.environ", {"PCONFIG_RUNTIME_ROOT": temp_dir}):
                with patch(
                    "file_sync.subprocess.run",
                    return_value=types.SimpleNamespace(
                        returncode=1, stdout="", stderr=""
                    ),
                ):
                    result = FileSync()._sync_with_robocopy(source, target)

        self.assertFalse(result["success"])
        self.assertIn("new folder/new-template.dotx", result["error"])


if __name__ == "__main__":
    unittest.main()
