# Release Notes v3.3.99

Datum: 2026-09-29

## Download

- [Release-Seite v3.3.99](https://github.com/GoroTech-Tools/PC-Konfigurator/releases/tag/v3.3.99)
- [ZIP direkt herunterladen](https://github.com/GoroTech-Tools/PC-Konfigurator/releases/download/v3.3.99/PC-Konfigurator-v3.3.99.zip)

## Änderungen

- Der Desktop-Ordner des aktuellen Benutzers bleibt bei der Konfiguration im
  Explorer-Schnellzugriff angeheftet. Der Release enthält damit die Korrektur,
  die ein unbeabsichtigtes Entfernen des Desktop-Eintrags verhindert.
- Versions-, Build- und Dokumentationsangaben sind auf den veröffentlichten
  Stand v3.3.99 konsolidiert.

## Enthaltener Funktionsstand

- Outlook classic einschließlich Outlook 2024 LTSC erhält Schriftart und
  -größe über `Common\MailSettings`, `Outlook\Options` und die synchronisierte
  `NormalEmail.dotm`.
- Persönliche Word-Building-Blocks können gesichert, wiederhergestellt und über
  **Tools → Building Blocks manuell bearbeiten** direkt in Word geöffnet werden.
- Die Datei-Vorlagen-Bibliothek wird im Update-Modus synchronisiert; der
  vollständige Reset bleibt eine optionale, ausdrücklich zu bestätigende Aktion.

## Qualitätsstatus

- Release-Build und Packaging wurden erfolgreich abgeschlossen.
- Das Build wurde als Onefile-/Windowed-Anwendung erzeugt.
- Das veröffentlichte ZIP-Asset ist über das GitHub-Release verfügbar.

## Artefakte

- Build-Verzeichnis: `dist/PC-Konfigurator-v3.3.99/`
- EXE: `dist/PC-Konfigurator-v3.3.99/PC-Konfigurator.exe`
- Release-ZIP: `release/PC-Konfigurator-v3.3.99.zip`

Das ZIP-Artefakt wird absichtlich nicht im Git-Repository versioniert. Es wird
ausschließlich über das GitHub-Release v3.3.99 ausgeliefert.

## Enthaltener Release-Commit

- `c5165b5` – Desktop beim Konfigurationslauf im Explorer-Schnellzugriff
  angeheftet lassen

## Technische Build-Informationen

- Build-Datum: 2026-09-29 18:35:15
- Build-Modus: `--onefile --windowed`
- EXE-Name: `PC-Konfigurator.exe`
