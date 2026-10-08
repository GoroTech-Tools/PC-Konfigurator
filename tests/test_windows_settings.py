import importlib
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

winreg_stub = types.ModuleType("winreg")
winreg_stub.HKEY_CURRENT_USER = object()
with patch.dict(sys.modules, {"winreg": winreg_stub}):
    office_configurator_module = importlib.import_module("office_configurator")


class ConfigureWindowsSettingsTests(unittest.TestCase):
    def test_excel_template_registry_values_use_selected_template_directory(self):
        configurator = office_configurator_module.OfficeConfigurator()
        applied_settings = {}

        with patch.object(
            configurator,
            "_apply_excel_registry_settings",
            side_effect=lambda settings, _font_settings: applied_settings.update(settings),
        ):
            result = configurator.configure_excel(
                target_path="/selected",
                com_bootstrap={"skip_com": True},
            )

        expected_path = str((pathlib.Path("/selected") / "Datei-Vorlagen").resolve())
        self.assertTrue(result["success"])
        self.assertEqual(applied_settings["PersonalTemplates"][0], expected_path)
        self.assertEqual(applied_settings["DefaultPath"][0], expected_path)
        self.assertEqual(applied_settings["AltStartupPath"][0], expected_path)

    def test_applies_requested_start_and_taskbar_registry_values(self):
        configurator = office_configurator_module.OfficeConfigurator()
        documented_values = []
        extra_values = []

        with (
            patch.object(office_configurator_module, "pin_desktop_to_quick_access", return_value=(True, None)),
            patch.object(
                configurator,
                "_set_windows_value_with_fallback",
                side_effect=lambda path, name, value, explanation: documented_values.append(
                    (path, name, value, explanation)
                ) or True,
            ),
            patch.object(
                configurator,
                "_set_windows_extra_value_with_fallback",
                side_effect=lambda path, name, value: extra_values.append((path, name, value)) or True,
            ),
            patch.object(configurator, "_read_registry_value", return_value=None),
            patch.object(configurator, "_read_dword_registry_value", return_value=1),
        ):
            result = configurator.configure_windows_settings()

        advanced_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        start_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Start"
        search_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
        self.assertTrue(result["success"])
        self.assertIn(
            (advanced_path, "SearchboxTaskbarMode", 1, "windows_show_search_icon"),
            documented_values,
        )
        self.assertIn((advanced_path, "TaskbarGlomLevel", 0), extra_values)
        self.assertIn((advanced_path, "ShowTaskViewButton", 0), extra_values)
        self.assertIn((start_path, "AllAppsViewMode", 1), extra_values)
        self.assertIn((search_path, "SearchboxTaskbarMode", 1), extra_values)

    def test_enables_taskbar_labels_when_requested(self):
        configurator = office_configurator_module.OfficeConfigurator()
        extra_values = []

        with (
            patch.object(office_configurator_module, "pin_desktop_to_quick_access", return_value=(True, None)),
            patch.object(configurator, "_set_windows_value_with_fallback", return_value=True),
            patch.object(
                configurator,
                "_set_windows_extra_value_with_fallback",
                side_effect=lambda path, name, value: extra_values.append((path, name, value)) or True,
            ),
            patch.object(configurator, "_read_registry_value", return_value=None),
            patch.object(configurator, "_read_dword_registry_value", return_value=1),
        ):
            result = configurator.configure_windows_settings(show_taskbar_labels=True)

        self.assertTrue(result["success"])
        self.assertIn(
            (
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "TaskbarGlomLevel",
                2,
            ),
            extra_values,
        )


if __name__ == "__main__":
    unittest.main()
