import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from font_options import FONT_OPTIONS


class FontOptionsTests(unittest.TestCase):
    def test_recently_added_fonts_are_supported(self):
        self.assertEqual(FONT_OPTIONS["Roboto"], "Roboto")
        self.assertEqual(FONT_OPTIONS["Segoe UI"], "Segoe UI")


if __name__ == "__main__":
    unittest.main()
