# Migrationsplan: GUI-Angleichung an AP1-Konfigurator-Portable

Stand: 2026-05-23
Projekt: `PC-Konfigurator-Portable`
Referenz: `AP1-Konfigurator-Portable/src/main.py`

## Ziel

Die GUI von `PC-Konfigurator-Portable` soll sich in **Struktur, Bedienlogik und visueller Sprache** an
`AP1-Konfigurator-Portable` anlehnen, ohne fachliche Funktionen zu verlieren.

## Ist-Analyse (Kurzfassung)

### AP1-Referenz (`tkinter/ttk`)

- Ein-Fenster-Layout mit klaren Bereichen: `Konfiguration`, `Aktionen`, `Ordner & Dokumentation`, `Fortschritt`
- Sichtbarer Prozessfluss mit:
  - Statuszeile (farblich codiert)
  - Fortschrittsbalken
  - Schritt-Checkliste (☐/☑)
  - Live-Protokoll
  - Letztes Ergebnis inkl. Log-Shortcut
- Wenige, klar priorisierte Hauptaktionen
- Persistente GUI-Settings (`engine`, `theme`, Flags)

### PC aktuell (`customtkinter`)

- Tab-basiertes UI (`Übersicht`, `Konfiguration`, `Registry-Info`, `Ausführung`, `Logs`)
- Sehr großer Funktionsumfang in `src/main.py`
- Viele Dialoge/Unterfenster (z. B. Registry-Details)
- Kein durchgängiger einheitlicher Fortschritts-Workflow über alle Aktionen

## Leitplanken

- **Keine fachliche Regression** (Templates, Registry, Fonts, Explorer-Handling müssen unverändert funktionieren)
- **Design angleichen, Domänenlogik behalten**
- **Schrittweise Migration** mit jederzeit lauffähiger GUI
- CustomTkinter kann bleiben (AP1-Layout wird visuell/funktional adaptiert)

---

## Delta-Mapping (AP1 -> PC)

- AP1 `Konfiguration`-Block -> PC: kompaktes Konfigurationspanel oben (statt verstreut über Tabs)
- AP1 `Aktionen`-Block -> PC: primäre Aktionen als prominente Buttons in einem gemeinsamen Bereich
- AP1 `Ordner & Dokumentation` -> PC: zentraler Schnellzugriff auf `Datei-Vorlagen`, `Fonts`, `docs`, `logs`
- AP1 `Fortschritt`-Block -> PC: einheitliches Panel mit Status + Progress + Schrittliste + Live-Log
- AP1 `Letztes Ergebnis` -> PC: Ergebnis-Kachel mit Startzeit, Modus, Erfolg/Fehler, Log-Datei

---

## Phasenplan (inkrementell)

## Phase 1 – UI-Rahmen harmonisieren (ohne Funktionsänderung)

- [ ] Neues Hauptlayout in `src/main.py` vorbereiten:
  - [ ] Header (Name + Version)
  - [ ] Konfigurationsbereich (kompakt)
  - [ ] Aktionsbereich (2–4 Hauptbuttons)
  - [ ] Fortschrittsbereich (Status + Log)
- [ ] Tab-Logik intern beibehalten, aber visuell in AP1-ähnliche Sektionen überführen
- [ ] Einheitliche Benennungen und Button-Hierarchie einführen

**Akzeptanzkriterium:** Nutzer erkennt auf den ersten Blick denselben Bedienfluss wie in AP1.

## Phase 2 – Fortschritts- und Run-Workflow vereinheitlichen

- [ ] Zentralen Run-Controller ergänzen (Start/Busy/Done/Failed)
- [ ] Konsistente Statusarten (`info`, `success`, `warning`, `error`)
- [ ] Schritt-Checkliste analog AP1 für:
  - [ ] Systemcheck
  - [ ] Font-Installation
  - [ ] Office/Registry-Konfiguration
  - [ ] Template-Verarbeitung
  - [ ] Abschluss
- [ ] Live-Protokoll in einem einheitlichen Widget bündeln

**Akzeptanzkriterium:** Jede Ausführung zeigt nachvollziehbaren Fortschritt statt nur verstreuter Textausgaben.

## Phase 3 – Zustands- und UX-Polish

- [ ] GUI-State-Datei einführen (z. B. Theme, gewählte Fonts, Zielpfad)
- [ ] Konsistente Fehlerdialoge + Erfolgsmeldungen
- [ ] „Letztes Ergebnis“-Panel inkl. „Log öffnen“
- [ ] Optional: Hell/Dunkel-Umschaltung wie AP1

**Akzeptanzkriterium:** Wiederholte Nutzung wirkt stabil, vorhersehbar und schnell.

## Phase 4 – Aufräumen & Entkoppeln

- [ ] Große `src/main.py` in UI-Teilmodule aufteilen (z. B. `ui/layout.py`, `ui/run_controller.py`)
- [ ] Registry-/Template-Dialoge sauber kapseln
- [ ] Regression-Checklist für GUI aufnehmen

**Akzeptanzkriterium:** Wartbarkeit verbessert, weniger Merge-Konflikte, klarere Zuständigkeiten.

---

## Konkretes Datei-Targeting

- Hauptumbau: `src/main.py`
- Unterfenster/Details: `src/registry_gui.py`
- Optional neue Struktur:
  - `src/ui/layout.py`
  - `src/ui/progress_panel.py`
  - `src/ui/actions_panel.py`
  - `src/ui/state_store.py`

---

## Risiken & Gegenmaßnahmen

- Risiko: UI-Refactor bricht Threading/Statusupdates
  - Maßnahme: Run-Controller zuerst isolieren, dann Layout umbauen
- Risiko: Zu großer Big-Bang-Change
  - Maßnahme: Phasenweise Merges, pro Phase Smoke-Tests
- Risiko: Inkonsistente Texte/Benennungen
  - Maßnahme: UI-Wording-Liste als Single Source festlegen

---

## Smoke-Checks pro Phase

- [ ] GUI startet fehlerfrei
- [ ] „Vollständige Konfiguration“ läuft durch
- [ ] „Nur Office konfigurieren“ läuft durch
- [ ] Logs werden angezeigt und gespeichert
- [ ] Registry-Info-Fenster öffnet/schließt stabil
- [ ] Keine Regression bei Template-Wiederherstellung

---

## Empfohlene Startreihenfolge (praktisch)

1. Fortschrittsbereich + Statusmodell vereinheitlichen
2. Aktionen in einen zentralen Bereich ziehen
3. Konfigurationspanel verdichten
4. Ergebnis-Panel ergänzen
5. Erst danach interne Modulaufteilung

So bekommst du schnell den größten UX-Gewinn bei geringem Risiko.
