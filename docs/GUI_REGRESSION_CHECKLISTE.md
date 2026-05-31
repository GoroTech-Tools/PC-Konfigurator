# GUI Regression-Checkliste

Stand: 2026-05-31  
Projekt: `PC-Konfigurator`

Diese Checkliste dient zur Absicherung nach GUI-Refactorings im Rahmen der
Angleichung an den `AP1-Konfigurator`.

## 1) Start und Navigation

- [ ] Anwendung startet ohne Traceback/Absturz
- [ ] Tabs `Übersicht`, `Start`, `Vorlagen/Ablage`, `Registry`, `Ausführung`, `Logs` vorhanden
- [ ] Wechsel zwischen Tabs funktioniert stabil
- [ ] Schnellnavigation aus dem Start-Tab funktioniert (Konfiguration/Registry/Ausführung)

## 2) Konfigurations- und Ausführungsfluss

- [ ] Vollständige Konfiguration startet und läuft durch
- [ ] Office-only-Konfiguration startet und läuft durch
- [ ] Fortschrittsbalken und Schritt-Checkliste werden korrekt aktualisiert
- [ ] Statusfarben/-texte wechseln plausibel (Info/Success/Error)

## 3) Ergebnis- und Logverhalten

- [ ] Letztes Ergebnis (Start/Modus/Status/Log) wird aktualisiert
- [ ] Letzte Log-Datei lässt sich öffnen
- [ ] Logs-Tab lädt Inhalte und Auto-Refresh funktioniert

## 4) Registry-/Template-Dialoge

- [ ] Registry-Info-Ansicht öffnet/schließt stabil
- [ ] Sichere Template-Wiederherstellung lässt sich starten
- [ ] Explorer-Neustart-Dialog verhält sich korrekt

## 5) Persistenz und Wiederanlauf

- [ ] GUI-Settings werden gespeichert (z. B. Font, Größen, Zielpfad)
- [ ] Gespeicherte Werte werden beim Neustart korrekt geladen

## 6) Abschlussbewertung

- [ ] Keine Regression festgestellt
- [ ] Auffälligkeiten als Issue dokumentiert

Anmerkungen:

- ______________________________________________________________
- ______________________________________________________________
