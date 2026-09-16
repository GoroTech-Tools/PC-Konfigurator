"""Windows-Benutzerpfade mit Unterstützung für Ordnerumleitungen."""

from __future__ import annotations

import os
from pathlib import Path


def get_documents_directory() -> Path:
    """Liefert den echten Dokumente-Ordner des aktuellen Windows-Benutzers.

    Der Registry-Eintrag ``User Shell Folders\\Personal`` hat Vorrang und
    berücksichtigt damit OneDrive- oder andere Gruppenrichtlinien-Umleitungen.
    Ohne Umleitung wird bewusst der deutsche Ordnername ``Dokumente`` verwendet.
    """
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                value, _value_type = winreg.QueryValueEx(key, "Personal")
            if value:
                redirected = Path(os.path.expandvars(str(value))).expanduser()
                if redirected.is_absolute():
                    return redirected
        except (OSError, ImportError):
            pass

    return Path.home() / "Dokumente"
