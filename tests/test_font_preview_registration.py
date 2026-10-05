import logging
import pathlib
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

with patch.dict(sys.modules, {"winreg": types.ModuleType("winreg")}):
    from font_installer import FontInstaller


class FontPreviewRegistrationTests(unittest.TestCase):
    def test_registers_supported_font_files_once_for_preview(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fonts_dir = pathlib.Path(temp_dir)
            for filename in ("Roboto-Regular.ttf", "SegoeUI.otf", "webfont.woff2", "notes.txt"):
                (fonts_dir / filename).touch()

            installer = FontInstaller.__new__(FontInstaller)
            installer.logger = logging.getLogger(__name__)
            installer._preview_font_paths = set()
            with (
                patch.object(installer, "_register_font_with_api", return_value=True) as register,
                patch.object(installer, "_refresh_font_cache") as refresh,
            ):
                registered = installer.register_fonts_for_preview(fonts_dir)
                repeated = installer.register_fonts_for_preview(fonts_dir)

            self.assertEqual({path.name for path in registered}, {
                "Roboto-Regular.ttf",
                "SegoeUI.otf",
                "webfont.woff2",
            })
            self.assertEqual(repeated, [])
            self.assertEqual(register.call_count, 3)
            refresh.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
