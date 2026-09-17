"""Diagnose-Hinweise für Dateisystem-Fehler, die durch Windows-Sicherheitsfunktionen verursacht sein können."""

from __future__ import annotations

_CONTROLLED_FOLDER_ACCESS_HINT = (
    "Hinweis: Dieser Fehler tritt typischerweise auf, wenn der 'Kontrollierte Ordnerzugriff' von "
    "Windows-Sicherheit (Viren- & Bedrohungsschutz > Einstellungen für Ransomware-Schutz) oder eine "
    "andere Endpoint-/Antiviren-Richtlinie den Schreibzugriff auf geschützte Ordner (z. B. Dokumente) "
    "blockiert. Bitte PC-Konfigurator.exe dort als zugelassene App eintragen oder den Zielordner von "
    "der Schutzrichtlinie ausnehmen."
)

# ERROR_FILE_NOT_FOUND, ERROR_PATH_NOT_FOUND, ERROR_ACCESS_DENIED
_BLOCKED_ACCESS_WINERRORS = (2, 3, 5)


def describe_filesystem_error(exc: OSError) -> str:
    """Ergänzt eine Fehlermeldung um einen Hinweis auf mögliche Sicherheitsblockaden."""
    message = str(exc)
    winerror = getattr(exc, "winerror", None)
    if winerror in _BLOCKED_ACCESS_WINERRORS:
        return f"{message}\n{_CONTROLLED_FOLDER_ACCESS_HINT}"
    return message
