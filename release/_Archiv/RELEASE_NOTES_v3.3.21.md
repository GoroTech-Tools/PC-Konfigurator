# Release Notes v3.3.21

Datum: 2026-06-20

## Highlights

- GUI-Moduswechsel (Einfach/Erweitert) stabilisiert:
  - `Registry`-Tab wird beim Umschalten zuverlässig ein-/ausgeblendet.
  - Start-Tab-/Menüaktualisierung läuft robust über den UI-Event-Zyklus.
- Tab-Kopfzeilen in der Haupt-GUI visuell verbessert:
  - Einheitliche Breiten mit gut lesbaren Beschriftungen.
  - Re-Anwendung nach Renderzyklen, damit CTk-Interne Updates nicht überschreiben.
- Layout- und Bedienfeinschliff aus v3.3.20 konsolidiert und releasefähig verpackt.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.21/
- EXE: dist/PC-Konfigurator-v3.3.21/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.21.zip

## Enthaltene Commits (aktuelle Historie)

- `64a7912` Chore: cleanup release notes formatting and ignore local release folders
- `8d495c0` Release v3.3.20: GUI mode/menu overhaul and layout fixes
- `335b304` Release v3.3.20: GUI-Bereinigung, Font-Status, Office-Tab in Registry-GUI
- `168f032` Chore: enable markdownlint rule MD010
- `a00aa27` Release v3.3.19: Explorer-Recovery hardening, Outlook template path fix, full docs update

## Technische Build-Informationen

- Build-Datum: 2026-06-20 20:43:46
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
