# Release Notes v3.3.6

Datum: 2026-06-08

## Highlights

- Office-Konfiguration robuster gemacht: Registry-Write + COM-Synchronisierung für Word, Excel und Outlook.
- Word-Kompatibilitätskeys ergänzt, damit unterschiedliche Office-Builds konsistent getroffen werden.
- GUI-Status und Log-Ausgabe für COM-Gesundheit vereinheitlicht (`[COM-HEALTH] OK|DEGRADED`).
- Registry-Prüfung erweitert: Kontext (User/SID/Elevation) sowie Outlook-/Kompatibilitätsprüfungen ergänzt.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.
- Office-Lauf mit degradierter COM-Verfügbarkeit wurde sauber abgefangen (Registry-Fallback aktiv).
- Neue Ergebnisfelder geprüft: `com_sync_ok`, `com_sync_warning`.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.6/
- EXE: dist/PC-Konfigurator-v3.3.6/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.6.zip

## Enthaltene Commits (aktuelle Historie)

- `9e2537e` Release v3.3.6
- `859c739` Remove .venv-bfw support
- `e721401` Release v3.3.5
- `1370c18` Aktualisiere Release Notes v3.3.3
- `82f8dc2` Mache Start-Tab-Buttons blasser

## Wichtige Änderungen im Code

- `src/office_configurator.py`
  - COM-Best-Effort-Synchronisierung für Word/Excel/Outlook ergänzt.
  - Aggregierte COM-Health-Rückgabe (`com_sync_ok`, `com_sync_warning`) ergänzt.
  - Markante Log-Zeile ergänzt: `[COM-HEALTH] OK|DEGRADED`.
- `src/ui/execution_flow.py`
  - Live-Statuszeile auf COM-Health mit kurzem Präfix vereinheitlicht:
    - `COM: [COM-HEALTH] OK | Word, Excel, Outlook via COM synchronisiert`
    - `COM: [COM-HEALTH] DEGRADED | ...`
- `tools/check-office-registry.ps1`
  - Pfad-/Prüfkorrektur und Kontextfelder (`CurrentUser`, `CurrentUserSid`, `IsElevated`) ergänzt.
  - Outlook-Schriftkeys und Word-Kompatibilitätskeys in die Soll/Ist-Prüfung aufgenommen.

## Hinweis zur Office-Version 15.0 im Log

Die Konfiguration schreibt bewusst sowohl `16.0` als auch `15.0` Registry-Zweige für Kompatibilität.
Auf Office-16-Installationen ist das erwartetes Verhalten und unkritisch; der 15.0-Zweig dient als Fallback.

## Technische Build-Informationen

- Build-Datum: 2026-06-08 03:31:04
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
