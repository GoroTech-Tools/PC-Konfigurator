# Release Notes v3.3.2

Datum: 2026-05-31

## Highlights

- Projektweite Benennung konsolidiert:
  - `PC-Konfigurator-Portable` wurde in UI, Build- und Doku-Pfaden auf
    `PC-Konfigurator` harmonisiert.
- Build-/Release-Pipeline stabilisiert:
  - Wiederhergestelltes und überarbeitetes Root-Buildskript `build.ps1`
  - Robustere EXE-Übergabe beim Packaging (Retry + Copy-Fallback bei
    temporären Dateisperren, z. B. OneDrive/Scanner)
- PyInstaller-Spec auf neuen Projektnamen umgestellt:
  - `src/PC-Konfigurator.spec` als aktive Spec-Datei
  - `.gitignore` mit expliziter Ausnahme für die versionierte Spec erweitert
- Dokumentation und Release-Texte auf einheitliches Wording gebracht
  (`README.md`, Anwender-/Technikdoku, Release-Historie).

## Qualitätsstatus

- Release-Build für `3.3.2` erfolgreich erzeugt (Onefile, windowed).
- Release-Artefakt als GitHub-Asset veröffentlicht:
  - `PC-Konfigurator-v3.3.2.zip`
  - SHA256: `3e231f4d54dffb1ebe0de294c1a90201e76198742a7a98a958434e4b62a1890e`
- Tag und Release sind veröffentlicht und nicht als Draft markiert:
  - Tag: `v3.3.2`
  - Release: `PC-Konfigurator v3.3.2`

## Artefakte

- Build-Verzeichnis: `dist/PC-Konfigurator-v3.3.2/`
- EXE: `dist/PC-Konfigurator-v3.3.2/PC-Konfigurator.exe`
- Release-ZIP: `release/PC-Konfigurator-v3.3.2.zip`
- GitHub-Release:
  - `https://github.com/GoroTech-Tools/PC-Konfigurator/releases/tag/v3.3.2`

## Enthaltene Commits (seit v3.3.1)

- `7161f09` Harmonize naming to PC-Konfigurator and restore build pipeline
- `c07ca08` Ignore data directory in gitignore
- `8013152` Release v3.3.2

## Technische Build-Informationen

- Build-Datum: `2026-05-31 11:47:12`
- Build-Modus: `--onefile --windowed`
- Python: `3.13.13`
- PyInstaller: `6.17.0`
