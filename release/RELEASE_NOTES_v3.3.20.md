# Release Notes v3.3.20

Datum: 2026-06-20

## Highlights

- Start-Tab und Menüstruktur deutlich vereinfacht:
	- Doku-Datei-Buttons aus dem Start-Tab entfernt.
	- Neues Menü **Hilfe** mit:
		- `Anwender-Dokumentation öffnen`
		- `Technik-Dokumentation öffnen`
		- `Mehr Informationen` (am Ende)
- Tools-Menü überarbeitet:
	- `System prüfen` als separater Menüeintrag entfernt.
	- `Systemstatus anzeigen` startet die Prüfung nun automatisch.
- Systemstatus-Fenster modernisiert:
	- Schaltfläche `System prüfen` entfernt.
	- `Schließen` unten rechts.
	- Kompakteres Fensterlayout.
- Neuer Bedienmodus im Start-Tab: **Einfach / Erweitert**
	- `Registry`-Tab nur im erweiterten Modus.
	- Zusätzliche Tools (Bitness/COM, GPO) nur im erweiterten Modus.
	- Bereich `Ausgangsmaterial` (Ordner-Buttons) nur im erweiterten Modus.
	- `Explorer neu starten` nur im erweiterten Modus.
	- Aktionshinweise im Start-Tab dynamisch nummeriert je Modus.
- Fensterpositionierung verbessert:
	- Hauptfenster zentriert im Arbeitsbereich (ohne Taskleisten-Überdeckung).
	- Fenster `Detaillierte Ansicht` gleich zentriert und vor dem Hauptfenster.
- Tab `Vorlagen/Ablage` überarbeitet:
	- Bereiche für Schriftart und Schriftgrößen horizontal nebeneinander.
	- Beschriftungen vereinheitlicht (`Schriftgröße Word/Outlook`, `Schriftgröße Excel`).
- Tab-Kopfzeilen robuster skaliert:
	- Einheitliche, besser lesbare Breite und stabiles Verhalten beim Moduswechsel.

## Qualitätsstatus

- Mehrfacher GUI-Smoke-Test durchgeführt (Start ohne Traceback).
- Sichtprüfung der neuen Modus-/Menülogik erfolgreich.
- Sichtprüfung der Fensterpositionierung und Tab-Layouts erfolgreich.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.20/
- EXE: dist/PC-Konfigurator-v3.3.20/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.20.zip

## Enthaltene Commits (aktuelle Historie)

- Wird mit dem Release-Commit `v3.3.20` aktualisiert.

## Technische Build-Informationen

- Build-Datum: 2026-06-20 14:51:16
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
