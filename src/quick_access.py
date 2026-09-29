"""Explorer-Schnellzugriff konfigurieren."""

from __future__ import annotations

import sys

from user_paths import get_desktop_directory


def pin_desktop_to_quick_access() -> tuple[bool, str | None]:
    """Heftet den Desktop-Ordner des aktuellen Benutzers an den Schnellzugriff."""
    if sys.platform != "win32":
        return False, "Diese Funktion ist nur unter Windows verfügbar."

    desktop = get_desktop_directory()
    if not desktop.is_dir():
        return False, f"Der Desktop-Ordner wurde nicht gefunden: {desktop}"

    pythoncom = None
    initialized = False
    try:
        import pythoncom
        import win32com.client

        pythoncom.CoInitialize()
        initialized = True
        shell = win32com.client.Dispatch("Shell.Application")
        folder = shell.Namespace(str(desktop))
        if folder is None:
            return False, f"Der Desktop-Ordner kann nicht geöffnet werden: {desktop}"
        folder.Self.InvokeVerb("pintohome")
        return True, None
    except Exception as exc:
        return False, str(exc)
    finally:
        if initialized and pythoncom is not None:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
