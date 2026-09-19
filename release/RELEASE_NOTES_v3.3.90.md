# Release Notes v3.3.90

Datum: 2026-09-19

## Highlights

- Building Blocks werden benutzerbezogen gesichert und nach dem Prinzip „neueste Datei gewinnt“ wiederhergestellt.
- Das neue Tool **Tools → Building Blocks manuell bearbeiten** öffnet die persönliche `.dotx` direkt zur Bearbeitung in Word.
- Vor der manuellen Bearbeitung wird eine datierte Sicherung angelegt.
- OneDrive-/Dateisystem-Rennen beim Anlegen und Kopieren der Building-Blocks-Sicherung werden mit Retry behandelt.
- Anwender- und Technikdokumentation wurden um den Building-Blocks-Workflow ergänzt.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.
- Markdownlint erfolgreich durchlaufen.
- Building-Blocks-Backup und Restore in isolierten Temp-Verzeichnissen erfolgreich geprüft.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.90/
- EXE: dist/PC-Konfigurator-v3.3.90/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.90.zip

## Enthaltene Commits (aktuelle Historie)

- `0e20ea7` release: v3.3.88
- `d5b743c` cleanup-documentation
- `c9e0961` archive-release-notes-v3.3.75
- `a71cd65` release-v3.3.76
- `b609cc2` archive-release-notes-v3.3.74

## Technische Build-Informationen

- Build-Datum: 2026-09-19 19:56:05
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
