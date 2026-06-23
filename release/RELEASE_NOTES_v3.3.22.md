# Release Notes v3.3.22

Datum: 2026-06-23

## Highlights

- Font-Installation für eingeschränkte Benutzerprofile robuster gemacht:
  - Fallback auf `Path.home()/AppData/Local/Microsoft/Windows/Fonts`, wenn `LOCALAPPDATA` nicht sauber verfügbar ist.
  - Fonts-Verzeichnis wird bei Bedarf automatisch angelegt.
  - Bereits vorhandene Fonts werden erneut registriert statt still übersprungen.
  - Diagnose-Logging zeigt Zielpfad, `LOCALAPPDATA`-Wert und Registry-Schreibvorgänge.
- Windows-11-Defaults erweitert:
  - Empfohlene Dateien im Startmenü deaktiviert.
  - Zuletzt verwendete Dateien im Datei-Explorer deaktiviert.
  - Sprunglisten-Einträge standardmäßig deaktiviert.
  - Anwendungen im Startmenü standardmäßig in Listenansicht.

## Qualitätsstatus

- Code- und Dokumentationsänderungen abgeschlossen.
- Syntaxprüfung für die geänderten Python-Dateien erfolgreich.
- Build/ZIP-Erzeugung wurde in dieser Runde nicht separat ausgeführt.

## Artefakte

- Quelländerungen in `src/`, `docs/` und `README.md`
- Neue Release-Notiz: `release/RELEASE_NOTES_v3.3.22.md`

## Enthaltene Änderungen

- `src/font_installer.py` – robuster Pfad, Rekonfiguration und Diagnose-Logging
- `src/ui/execution_flow.py` – differenzierte Font-Schritt-Meldungen
- `src/office_configurator.py` – neue Windows-Defaults
- `src/registry_explainer.py` – erweiterte Registry-Beschreibungen
- `README.md`, `docs/DOKUMENTATION_ANWENDER.md`, `docs/DOKUMENTATION_TECHNIK.md` – Doku-Updates
