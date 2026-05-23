# PC-Konfigurator-Portable v3.3.1

## Build-Informationen

- Erzeugt am: 2026-05-23 21:27:32
- Build-Modus: Onefile (--onefile --windowed)
- EXE: PC-Konfigurator-Portable.exe

## Artefakte

- dist/PC-Konfigurator-Portable-v3.3.1/
- release/PC-Konfigurator-Portable-v3.3.1.zip

## Änderungen in v3.3.1

### UI/UX

- Oberfläche weiter an den AP1-Stil angeglichen.
- Tab-Reihenfolge und Benennungen vereinheitlicht:
  - `Konfiguration` -> `Vorlagen/Ablage`
  - `Registry-Info` -> `Registry`
- Start-Tab bereinigt (überflüssige Status-/Template-Elemente entfernt).
- Ausführungsbereich vereinfacht (Hinweisblock zwischen Titel und Aktionen entfernt).
- Registry-Detaildialog vereinheitlicht (Schaltflächen ohne Symbole).
- Logs-Tab mit Live-Aktualisierung ergänzt.

### Stabilität und Fixes

- Interne Tab-/Callback-Verknüpfungen in `main.py` konsolidiert.
- Verwaiste UI-Referenzen nach dem Refactoring entfernt.
- Konsistenz in Start-/Konfigurationsfluss und Anzeigeverhalten verbessert.

### Dokumentation und Qualität

- Encoding-/Umlautprobleme (Mojibake) in Anwenderdokumentation korrigiert.
- Markdown-Lint-Probleme (u. a. Listenabstände/Mehrfachleerzeilen) bereinigt.
- Dokumentationsstruktur unter `docs/` konsolidiert.

## Hinweis

Diese Release-Notes werden automatisch bei jedem Build erzeugt und bei ZIP-Erstellung aktualisiert.
