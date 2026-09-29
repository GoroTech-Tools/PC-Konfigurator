import pathlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import quick_access
import user_paths


class GetDesktopDirectoryTests(unittest.TestCase):
    def test_uses_redirected_desktop_from_user_shell_folders(self):
        expected = pathlib.Path("/home/user/OneDrive/Desktop")
        registry_key = MagicMock()
        registry_key.__enter__.return_value = registry_key
        winreg = types.SimpleNamespace(
            HKEY_CURRENT_USER=object(),
            OpenKey=MagicMock(return_value=registry_key),
            QueryValueEx=MagicMock(return_value=(str(expected), 2)),
        )

        with (
            patch.object(user_paths.os, "name", "nt"),
            patch.object(user_paths, "Path", pathlib.PosixPath),
            patch.dict(sys.modules, {"winreg": winreg}),
        ):
            result = user_paths.get_desktop_directory()

        self.assertEqual(result, expected)
        winreg.OpenKey.assert_called_once_with(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
        )
        winreg.QueryValueEx.assert_called_once_with(registry_key, "Desktop")


class PinDesktopToQuickAccessTests(unittest.TestCase):
    def test_pins_current_desktop_and_balances_com_initialization(self):
        desktop = pathlib.Path("/home/user/OneDrive/Desktop")
        pythoncom = types.SimpleNamespace(
            CoInitialize=MagicMock(),
            CoUninitialize=MagicMock(),
        )
        folder = types.SimpleNamespace(Self=types.SimpleNamespace(InvokeVerb=MagicMock()))
        qa_folder = types.SimpleNamespace(Items=MagicMock(return_value=[]))
        shell = types.SimpleNamespace(
            Namespace=MagicMock(side_effect=[folder, qa_folder]),
        )
        win32com_client = types.SimpleNamespace(
            Dispatch=MagicMock(return_value=shell),
        )
        win32com = types.ModuleType("win32com")
        win32com.client = win32com_client

        with (
            patch.object(quick_access.sys, "platform", "win32"),
            patch.object(quick_access, "get_desktop_directory", return_value=desktop),
            patch.object(pathlib.Path, "is_dir", return_value=True),
            patch.dict(
                sys.modules,
                {"pythoncom": pythoncom, "win32com": win32com, "win32com.client": win32com_client},
            ),
        ):
            result = quick_access.pin_desktop_to_quick_access()

        self.assertEqual(result, (True, None))
        win32com_client.Dispatch.assert_called_once_with("Shell.Application")
        shell.Namespace.assert_has_calls(
            [unittest.mock.call(str(desktop)), unittest.mock.call(quick_access._QUICK_ACCESS_NAMESPACE)],
        )
        folder.Self.InvokeVerb.assert_called_once_with("pintohome")
        pythoncom.CoInitialize.assert_called_once_with()
        pythoncom.CoUninitialize.assert_called_once_with()

    def test_does_not_unpin_desktop_when_already_in_quick_access(self):
        desktop = pathlib.Path("/home/user/OneDrive/Desktop")
        pythoncom = types.SimpleNamespace(
            CoInitialize=MagicMock(),
            CoUninitialize=MagicMock(),
        )
        folder = types.SimpleNamespace(Self=types.SimpleNamespace(InvokeVerb=MagicMock()))
        qa_folder = types.SimpleNamespace(
            Items=MagicMock(return_value=[types.SimpleNamespace(Path=str(desktop))]),
        )
        shell = types.SimpleNamespace(
            Namespace=MagicMock(side_effect=[folder, qa_folder]),
        )
        win32com_client = types.SimpleNamespace(Dispatch=MagicMock(return_value=shell))
        win32com = types.ModuleType("win32com")
        win32com.client = win32com_client

        with (
            patch.object(quick_access.sys, "platform", "win32"),
            patch.object(quick_access, "get_desktop_directory", return_value=desktop),
            patch.object(pathlib.Path, "is_dir", return_value=True),
            patch.dict(
                sys.modules,
                {"pythoncom": pythoncom, "win32com": win32com, "win32com.client": win32com_client},
            ),
        ):
            result = quick_access.pin_desktop_to_quick_access()

        self.assertEqual(result, (True, None))
        folder.Self.InvokeVerb.assert_not_called()
        pythoncom.CoUninitialize.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
