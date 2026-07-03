# Release Notes v3.3.25

Datum: 2026-07-03

## Highlights

- GUI modernisiert und strukturiert (Kartenlayout, Quick-Actions, responsives Verhalten).
- Bedienfluss vereinfacht: Start → `Konfiguration` → `Ausführung` (inkl. neuer `Weiter`-Schaltflächen).
- Moduslogik geschärft: `Nur Office konfigurieren` wird im Tab `Ausführung` nur im erweiterten Modus angezeigt.
- Schriftkonfiguration erweitert: `Arial` und `Calibri` ergänzt, inklusive Live-Vorschau und Fontlisten-Vorschau.
- Bezeichnungen konsolidiert: `Vorlagen/Ablage` wurde in GUI und Dokumentation vollständig durch `Konfiguration` ersetzt.
- Mermaid-Diagramme und vollständige Dokumentation auf den neuen Ablauf aktualisiert.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.25/
- EXE: dist/PC-Konfigurator-v3.3.25/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.25.zip

## Enthaltene Commits (aktuelle Historie)

- `726cd4d` Release v3.3.23: update docs, build flow and release notes
- `eec897e` Release v3.3.22: build artifacts
- `cea6602` Release v3.3.22: font hardening and Windows defaults
- `bdb5081` Build: add two-step markdown quickcheck (fix + gate)
- `233cb5e` Build: enable markdownlint auto-fix during release creation

## Technische Build-Informationen

- Build-Datum: 2026-07-03 17:51:32
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
