# GUI Regression-Checkliste

Stand: 2026-06-20  
Projekt: `PC-Konfigurator`

Diese Checkliste dient zur Absicherung nach GUI-Refactorings im Rahmen der
Angleichung an den `AP1-Konfigurator`.

## 1) Start und Navigation

- [x] Anwendung startet ohne Traceback/Absturz
- [x] Tabs `Übersicht`, `Start`, `Konfiguration`, `Registry`, `Ausführung`, `Logs` vorhanden
- [x] Wechsel zwischen Tabs funktioniert stabil
- [x] Schnellnavigation aus dem Start-Tab funktioniert (Konfiguration/Registry/Ausführung)
- [x] Start-Tab enthält Schaltfläche `Weiter` und öffnet Tab `Konfiguration`
- [x] Tab `Konfiguration` enthält unten Schaltfläche `Weiter` und öffnet Tab `Ausführung`

## 2) Konfigurations- und Ausführungsfluss

- [x] Vollständige Konfiguration startet und läuft durch
- [x] Office-only-Konfiguration startet und läuft durch (nur Modus `Erweitert`)
- [x] Schaltfläche `Nur Office konfigurieren` ist in `Einfach` ausgeblendet und in `Erweitert` sichtbar
- [x] Fortschrittsbalken und Schritt-Checkliste werden korrekt aktualisiert
- [x] Statusfarben/-texte wechseln plausibel (Info/Success/Error)
- [x] Start-Tab zeigt Konfigurationsübersicht und Hinweis zum Beenden von Edge/Office
- [x] Vollständiger Lauf verlangt die Bestätigung „Anwendungen geschlossen?“
- [x] Laufstatus zeigt Edge-/Signatur-Wiederherstellung und -Aktualisierung

## 3) Ergebnis- und Logverhalten

- [x] Letztes Ergebnis (Start/Modus/Status/Log) wird aktualisiert
- [x] Letzte Log-Datei lässt sich öffnen
- [x] Logs-Tab lädt Inhalte und Auto-Refresh funktioniert

## 4) Registry-/Template-Dialoge

- [x] Registry-Info-Ansicht öffnet/schließt stabil
- [x] Sichere Template-Wiederherstellung lässt sich starten
- [x] Explorer-Neustart-Dialog verhält sich korrekt

## 5) Persistenz und Wiederanlauf

- [x] GUI-Settings werden gespeichert (z. B. Font, Größen, Zielpfad)
- [x] Gespeicherte Werte werden beim Neustart korrekt geladen
- [x] Edge-Profile werden im gewählten Datei-Vorlagen-Ziel gesichert
- [x] E-Mail-Signaturen werden separat gesichert und vorhandene lokale Signaturen nicht überschrieben

## 6) Abschlussbewertung

- [x] Keine Regression festgestellt
- [x] Auffälligkeiten als Issue dokumentiert

Anmerkungen:

- 31.05.2026: Automatisierter GUI-Smoke-Check (scriptbasiert, nicht-destruktiv)
  erfolgreich für Start, Tabs, Navigation, Ausführungsfluss-Ansteuerung,
  Ergebnis-/Loganzeige, Persistenz sowie Registry-Dialog open/close.
- Ausführungsfluss wurde im Smoke-Harness bewusst mit Stubs geprüft
  (kein destruktiver Voll-Lauf auf Zielsystem im GUI-Test).
- Bekannte technische Auffälligkeit im Testharness beim Destroy von Tk-Instanzen:
  `invalid command name ... (after script)`; betrifft nicht den normalen GUI-Produktivlauf.
- 31.05.2026 (Nachtest): Interaktive Dialogpfade für
  „Sichere Template-Wiederherstellung“ und „Explorer-Neustart“
  wurden nicht-destruktiv via Funktionsharness validiert (Bestätigungsdialog,
  Ablauf/Status-Update, Rückgabepfade).
- Issue-Hinweis: Keine produktive Regression festgestellt; Testharness-Hinweise
  sind in dieser Checkliste dokumentiert, separates GitHub-Issue aktuell nicht erforderlich.
- 20.06.2026 (Nachtest): Explorer-Neustart-Funktion gegen verzögerte Shell-Reinitialisierung gehärtet und mit sichtbarer Taskleisten-Prüfung verifiziert (`Shell_TrayWnd` sichtbar).
