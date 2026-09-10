# Release Notes v3.3.45

Datum: 2026-09-10

## Highlights

- Namens-, Build- und Doku-Anpassungen wurden in diesem Release-Stand konsolidiert.
- Das Build wurde als Onefile-EXE erzeugt und für die Verteilung aufbereitet.
- Bitte Highlights bei Bedarf projektspezifisch ergänzen.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.45/
- EXE: dist/PC-Konfigurator-v3.3.45/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.45.zip

## Enthaltene Commits (aktuelle Historie)

- `d17dd49` fix: Vorlagen-Verify und Windows-Erfolgstatus korrigieren
- `0f92bb5` fix: Word AutoCorrect und Release-Archivierung aktualisieren
- `c63ad35` fix: korrigiere Excel-Standardfont und Post-Verify
- `fa601ff` fix: normalisiere Fontnamen für Corporate Themes
- `9eb04bd` fix: sichere Template-Verarbeitung gegen Korruption

## Technische Build-Informationen

- Build-Datum: 2026-09-10 19:03:55
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
