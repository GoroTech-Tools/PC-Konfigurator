import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

FONT_INSTALLER_PATH = pathlib.Path(__file__).resolve().parents[1] / "src" / "font_installer.py"
spec = importlib.util.spec_from_file_location("font_installer_preview_test", FONT_INSTALLER_PATH)
font_installer_module = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {"winreg": types.ModuleType("winreg")}):
    spec.loader.exec_module(font_installer_module)


class FontInstallerPreviewTests(unittest.TestCase):
    def test_registers_bundled_fonts_privately_once(self):
        with tempfile.TemporaryDirectory() as directory:
            fonts_dir = pathlib.Path(directory)
            (fonts_dir / "sample.ttf").touch()
            (fonts_dir / "uppercase.TTF").touch()
            (fonts_dir / "readme.txt").touch()

            installer = font_installer_module.FontInstaller.__new__(
                font_installer_module.FontInstaller
            )
            installer._preview_font_paths = set()
            installer._register_font_with_api = Mock(return_value=True)

            first_result = installer.register_fonts_for_preview(fonts_dir)
            second_result = installer.register_fonts_for_preview(fonts_dir)

        self.assertEqual(len(first_result["registered_fonts"]), 2)
        self.assertEqual(second_result["registered_fonts"], [])
        self.assertEqual(installer._register_font_with_api.call_count, 2)


if __name__ == "__main__":
    unittest.main()
