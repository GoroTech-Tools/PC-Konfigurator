# Release Notes v3.3.3

Datum: 2026-05-31

## Highlights

- Namens-, Build- und Doku-Anpassungen wurden in diesem Release-Stand konsolidiert.
- Das Build wurde als Onefile-EXE erzeugt und für die Verteilung aufbereitet.
- Nachpflege: Mermaid-Diagramme in README/Anwender-/Technikdoku ergänzt und als SVG + `.mmd` unter `docs/diagramme/` bereitgestellt.

## Nachträgliche Release-Pflege (31.05.2026)

- Dokumentationsdiagramme nach dem Release ergänzt, analog zu den Schwesterprojekten.
- Neue Datei: `docs/DOKUMENTATION_DIAGRAMME.md` als zentrale Übersicht.
- Neue Diagrammquellen: `docs/diagramme/*.mmd`.
- Neue Diagrammgrafiken: `docs/diagramme/*.svg`.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.3/
- EXE: dist/PC-Konfigurator-v3.3.3/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.3.zip

## Enthaltene Commits (aktuelle Historie)

- `33ac688` Add tools README for lint routine
- `d7d34ae` Add markdownlint config and integrate lint routine
- `519890f` Add EXE feedback evaluation template
- `0f91630` Add EXE user testing checklists and documentation links
- `d87277d` Use detailed release notes template in build script

## Technische Build-Informationen

- Build-Datum: 2026-05-31 13:00:14
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
