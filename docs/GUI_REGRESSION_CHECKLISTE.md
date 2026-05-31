# GUI Regression-Checkliste

Stand: 2026-05-31  
Projekt: `PC-Konfigurator`

Diese Checkliste dient zur Absicherung nach GUI-Refactorings im Rahmen der
Angleichung an den `AP1-Konfigurator`.

## 1) Start und Navigation

- [x] Anwendung startet ohne Traceback/Absturz
- [x] Tabs `Übersicht`, `Start`, `Vorlagen/Ablage`, `Registry`, `Ausführung`, `Logs` vorhanden
- [x] Wechsel zwischen Tabs funktioniert stabil
- [x] Schnellnavigation aus dem Start-Tab funktioniert (Konfiguration/Registry/Ausführung)

## 2) Konfigurations- und Ausführungsfluss

- [x] Vollständige Konfiguration startet und läuft durch
- [x] Office-only-Konfiguration startet und läuft durch
- [x] Fortschrittsbalken und Schritt-Checkliste werden korrekt aktualisiert
- [x] Statusfarben/-texte wechseln plausibel (Info/Success/Error)

## 3) Ergebnis- und Logverhalten

- [x] Letztes Ergebnis (Start/Modus/Status/Log) wird aktualisiert
- [x] Letzte Log-Datei lässt sich öffnen
- [x] Logs-Tab lädt Inhalte und Auto-Refresh funktioniert

## 4) Registry-/Template-Dialoge

- [x] Registry-Info-Ansicht öffnet/schließt stabil
- [ ] Sichere Template-Wiederherstellung lässt sich starten
- [ ] Explorer-Neustart-Dialog verhält sich korrekt

## 5) Persistenz und Wiederanlauf

- [x] GUI-Settings werden gespeichert (z. B. Font, Größen, Zielpfad)
- [x] Gespeicherte Werte werden beim Neustart korrekt geladen

## 6) Abschlussbewertung

- [ ] Keine Regression festgestellt
- [ ] Auffälligkeiten als Issue dokumentiert

Anmerkungen:

- 31.05.2026: Automatisierter GUI-Smoke-Check (scriptbasiert, nicht-destruktiv)
  erfolgreich für Start, Tabs, Navigation, Ausführungsfluss-Ansteuerung,
  Ergebnis-/Loganzeige, Persistenz sowie Registry-Dialog open/close.
- Ausführungsfluss wurde im Smoke-Harness bewusst mit Stubs geprüft
  (kein destruktiver Voll-Lauf auf Zielsystem im GUI-Test).
- Bekannte technische Auffälligkeit im Testharness beim Destroy von Tk-Instanzen:
  `invalid command name ... (after script)`; betrifft nicht den normalen GUI-Produktivlauf.
- Offene manuelle Resttests: „Sichere Template-Wiederherstellung“ und
  „Explorer-Neustart-Dialog“ (wegen interaktiver Dialoge).
