# Migrationsplan: GUI-Angleichung an AP1-Konfigurator

Stand: 2026-05-31
Projekt: `PC-Konfigurator`
Referenz: `AP1-Konfigurator/src/main.py`

## Ziel

Die GUI von `PC-Konfigurator` soll sich in **Struktur, Bedienlogik und visueller Sprache** an
`AP1-Konfigurator` anlehnen, ohne fachliche Funktionen zu verlieren.

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

- Tab-basiertes UI mit AP1-orientiertem Startbereich (`Übersicht`, `Start`, `Vorlagen/Ablage`, `Registry`, `Ausführung`, `Logs`)
- Sehr großer Funktionsumfang in `src/main.py`
- Viele Dialoge/Unterfenster (z. B. Registry-Details)
- Fortschritts-Workflow über `ExecutionRunController` vereinheitlicht

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

## Status 2026-05-31

Bereits umgesetzt:

- AP1-ähnlicher Start-Tab mit zentralen Aktionen und Schnellzugriffen
- Einheitlicher Ausführungs-/Fortschrittsfluss via `ExecutionRunController`
- Persistente GUI-Einstellungen via `GuiStateStore`
- UI in Teilmodule aufgeteilt (`start_tab`, `execution_tab`, `execution_flow`, `overview_tab`, `configuration_tab`, `registry_info_tab`, `layout`, `registry_dialogs`, `template_dialogs`, `tools_dialogs`, `logs_panel`, `system_status`, `explorer_actions`, `office_configuration_flow`, `status_output`, `runtime.runtime_bundle`, `file_actions`)
- Template-Status-Rendering zusätzlich ausgelagert nach `ui/template_status.py`
- Regression-Checkliste ergänzt: `docs/GUI_REGRESSION_CHECKLISTE.md`

Noch offen:

- Optionaler Theme-/Appearance-Abgleich mit AP1

## Abschlussstand (31.05.2026)

Die geplante GUI-Angleichung wurde strukturell umgesetzt. Der Kern der Migration ist
abgeschlossen:

- AP1-ähnlicher Bedienfluss ist implementiert
- Fortschritts- und Run-Workflow ist vereinheitlicht
- `src/main.py` wurde in fachlich getrennte Module entkoppelt

Offen bleiben bewusst nur:

- optionaler Theme-/Appearance-Abgleich (UX-Feinschliff)
- abschließende manuelle Smoke-Checks (siehe Checkliste unten)

## Phase 1 – UI-Rahmen harmonisieren (ohne Funktionsänderung)

- [x] Neues Hauptlayout in `src/main.py` vorbereiten:
  - [x] Header (Name + Version)
  - [x] Konfigurationsbereich (kompakt)
  - [x] Aktionsbereich (2–4 Hauptbuttons)
  - [x] Fortschrittsbereich (Status + Log)
- [x] Tab-Logik intern beibehalten, aber visuell in AP1-ähnliche Sektionen überführen
- [x] Einheitliche Benennungen und Button-Hierarchie einführen

**Akzeptanzkriterium:** Nutzer erkennt auf den ersten Blick denselben Bedienfluss wie in AP1.

## Phase 2 – Fortschritts- und Run-Workflow vereinheitlichen

- [x] Zentralen Run-Controller ergänzen (Start/Busy/Done/Failed)
- [x] Konsistente Statusarten (`info`, `success`, `warning`, `error`)
- [x] Schritt-Checkliste analog AP1 für:
  - [x] Systemcheck
  - [x] Font-Installation
  - [x] Office/Registry-Konfiguration
  - [x] Template-Verarbeitung
  - [x] Abschluss
- [x] Live-Protokoll in einem einheitlichen Widget bündeln

**Akzeptanzkriterium:** Jede Ausführung zeigt nachvollziehbaren Fortschritt statt nur verstreuter Textausgaben.

## Phase 3 – Zustands- und UX-Polish

- [x] GUI-State-Datei einführen (z. B. Theme, gewählte Fonts, Zielpfad)
- [x] Konsistente Fehlerdialoge + Erfolgsmeldungen
- [x] „Letztes Ergebnis“-Panel inkl. „Log öffnen“
- [ ] Optional: Hell/Dunkel-Umschaltung wie AP1

**Akzeptanzkriterium:** Wiederholte Nutzung wirkt stabil, vorhersehbar und schnell.

## Phase 4 – Aufräumen & Entkoppeln

- [x] Große `src/main.py` weiter in UI-Teilmodule aufteilen (u. a. `ui/layout.py`, `ui/run_controller.py`)
- [x] Registry-/Template-Dialoge sauber kapseln
- [x] Regression-Checklist für GUI aufnehmen

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
