# DOKUMENTATION_TECHNIK

## 1. Architekturüberblick

`PC-Konfigurator` besteht aus folgenden Schichten:

- **GUI/Orchestrierung** (`src/main.py`)
- **Office-/System-Konfiguration** (mehrere Module im `src/`-Verzeichnis)
- **Template-Schutz** (`SafeTemplateProcessor`, ZIP-Integritätsprüfung)
- **Build/Release-Automation** (`setup.ps1`, `build.ps1`, `src/publish_release.ps1`)

Ziel ist eine robuste, portable Auslieferung als Windows-EXE (`onefile`) inklusive
externer Assets aus `data/` (`data/Fonts`, `data/Datei-Vorlagen`) und Dokumentation.

```mermaid
flowchart LR
   A[GUI main.py] --> B[UI-Module src/ui]
   A --> C[Laufzeit-Module src/runtime]
   B --> D[Office und Registry-Konfiguration]
   C --> E[Asset-Bundle und Laufzeitpfade]
   D --> F[SafeTemplateProcessor]
   F --> G[Word Excel Outlook Templates]
```

![Systemüberblick Dokumentation Technik](diagramme/technik_systemuebersicht.svg)

_Mermaid-Quelle: `docs/diagramme/technik_systemuebersicht.mmd`_

## 2. Wichtige Projektstruktur

```text
PC-Konfigurator/
├── src/                       # Python-Anwendung + Module
├── data/
│   ├── Fonts/                 # Schriftarten (familienweise strukturiert)
│   └── Datei-Vorlagen/        # Office-Vorlagen und Arbeitsdateien
├── docs/                      # Projektdokumentation
├── build.ps1                  # Build-Orchestrierung + Versionierung
├── setup.ps1                  # venv-Setup + Dependencies
├── src/publish_release.ps1    # Veröffentlichung von ZIP-Artefakten
├── src/PC-Konfigurator.spec
├── README.md
└── src/BUILD-INFO.txt
```

## 3. Laufzeitfluss

1. Start der EXE/`src/main.py`
2. Navigation `Start` → **Weiter** → `Konfiguration` → **Weiter** → `Ausführung`
3. Auswahl von Schriftart, Optionen und Zielparametern
4. Konfigurationspipeline:
   - Registry-Anpassungen (HKCU)
   - Empfohlene Dateien/zuletzt verwendete Dateien/Sprunglisten deaktivieren
   - Explorer-Option „Immer Dateinamen und -inhalte suchen" aktivieren (`SearchFileNameAlways=1`)
   - Anwendungen im Startmenü standardmäßig als Liste darstellen
   - Office-Optimierungen
   - Template-Anpassungen über SafeTemplateProcessor
   - Font-Installation und Zuweisung
5. Ausführungsmodus:
   - `Einfach`: Vollständige Konfiguration
   - `Erweitert`: Vollständige Konfiguration oder Office-only
6. Logging und Ergebnisanzeige in der Oberfläche

### Aktueller Status: offene Word-Detailpunkte

Die Word-Optionen „Jede Tabellenzeile mit einem Großbuchstaben beginnen" und
„Bilder einfügen" = „Mit Text in Zeile" sind inzwischen als Standardwerte in
der Office-Registry-Konfiguration des `PC-Konfigurator` hinterlegt.

Der technische Prüfpfad dafür ist:

- `tools/check-office-registry.ps1`
- `docs/OFFENE_OFFICE_PUNKTE.md`

Der fachliche Praxisnachweis auf einem realen Testclient bleibt als separate
Abnahmeaufgabe bestehen.

```mermaid
flowchart TD
   A[Start-Tab] --> B[Weiter zu Konfiguration]
   B --> C[Parameter aus GUI]
   C --> D[Weiter zu Ausführung]
   D --> E{Bedienmodus}
   E -->|Einfach| F[Vollständige Konfiguration]
   E -->|Erweitert| G[Vollständige oder Office-only]
   F --> H[Registry und Office-Schritte]
   G --> H
   H --> I[Template-Backup]
   I --> J[Template-Anpassung]
   J --> K[Template-Deployment]
   K --> L[Statusausgabe und Logs]
```

![Datenfluss Dokumentation Technik](diagramme/technik_datenfluss.svg)

_Mermaid-Quelle: `docs/diagramme/technik_datenfluss.mmd`_

## 4. Build-Pipeline (lokal)

### 4.1 Setup

`setup.ps1` erstellt/aktualisiert die virtuelle Umgebung (`.venv`) und installiert Abhängigkeiten.

### 4.2 Build (`build.ps1`)

- Versionsverwaltung über `src/build_info.py`
- Optionaler Versionssprung (`-NoVersionBump` deaktiviert ihn)
- PyInstaller-Build (bevorzugt via `.spec`)
- Post-Build über `src/post_build.py`
- Optionales ZIP-Release (`-SkipZip` überspringt)

### 4.3 Post-Build (`src/post_build.py`)

Kopiert und validiert:

- `data/Fonts/`
- `data/Datei-Vorlagen/`
- `docs/`
- `README.md`
- `src/BUILD-INFO.txt`

Besonderheiten:

- fehlertolerantes Kopieren (OneDrive-Placeholder-resilient)
- Long-Path-Handling
- optionale Teilfreigabe bei Template-Lücken via `PCONFIG_ALLOW_PARTIAL_TEMPLATES=1`

## 5. CI/CD und Releases

- Release-Artefakte liegen in `release/`
- Veröffentlichung über `src/publish_release.ps1`
- GitHub-Release-Integration ist über Repo-Workflow möglich (je nach Projektstand)

```mermaid
flowchart LR
   A[setup.ps1] --> B[build.ps1]
   B --> C[PyInstaller Onefile]
   C --> D[dist PC-Konfigurator-vX.Y.Z]
   D --> E[release ZIP + Release Notes]
   E --> F[Git Tag und GitHub Release]
```

![Build-Release-Pipeline](diagramme/release_pipeline.svg)

_Mermaid-Quelle: `docs/diagramme/release_pipeline.mmd`_

## 6. Versionsmanagement

Single Source of Truth zur Build-Version:

- `src/build_info.py`

`build.ps1` synchronisiert daraus:

- `README.md`
- `docs/DOKUMENTATION_ANWENDER.md`
- `src/BUILD-INFO.txt`

## 7. Risiken und Randbedingungen

- OneDrive-Placeholder können Asset-Kopiervorgänge beeinträchtigen
- Office/COM-Verfügbarkeit kann je Client variieren
- Große Asset-Bestände beeinflussen Build- und ZIP-Zeit

## 8. Testempfehlungen

### Smoke-Test

1. Build ausführen (`build.ps1 -NoVersionBump`)
2. EXE starten
3. Konfiguration mit Standardwerten durchführen
4. Logausgabe auf Fehler/Warnungen prüfen

### Behobene Fehler (v3.3.9)

**1. `startmenu_guard.py` – SyntaxError beim Modulimport (f-String GUID)**

Die GUID `{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}` war in `_build_guard_ps1()`
direkt als Literal in einem f-String gesetzt. Python interpretierte `{86...}` als
Formatierungsausdruck und warf `SyntaxError: invalid decimal literal` bereits beim
Import, wodurch das gesamte Modul nicht geladen werden konnte. Kontextmenü-Klassik/
Modern-Wechsel und Autostart-Hinterlegung waren damit funktionslos.

**Fix:** Die Konstante `WIN11_CLASSIC_CONTEXTMENU_CLSID` wird jetzt per
`{WIN11_CLASSIC_CONTEXTMENU_CLSID}` in den f-String interpoliert.

**2. `main.py` – Explorer-Kill beim App-Start**

`_run_startmenu_guard()` wurde beim Kaltstart der App immer mit
`auto_restart_explorer=True` aufgerufen. Sobald der gespeicherte Modus nicht mit
dem aktuellen Registry-Stand übereinstimmte (z. B. frische ZIP-Installation ohne
vorhandene `gui_state.json`), wurde `taskkill /F /IM explorer.exe` ausgeführt. Das
destabilisierte die Shell und verhinderte einen sofortigen zweiten EXE-Start
(`Failed to load Python DLL`-Fehler aus `%TEMP%\_MEI...`).

**Fix:** `_run_startmenu_guard()` erhält einen Parameter `auto_restart_explorer`.
Beim Kaltstart wird `False` übergeben — der Autostart-Guard (Startup-Ordner) sorgt
beim nächsten Login für die Wirkung. Nur bei manueller GUI-Modus-Änderung wird
weiterhin `True` übergeben (sofortige sichtbare Wirkung gewünscht).

### Behobene Fehler (v3.3.19)

#### 1) Explorer-Neustart: Explorer-Prozess lief, Taskleiste blieb unsichtbar

In einzelnen Umgebungen war `explorer.exe` bereits wieder gestartet, die Shell war
jedoch noch nicht vollständig reinitialisiert (Taskleiste fehlte weiterhin).

**Fix:** Neustartlogik wurde auf Sichtbarkeitsprüfung der Taskleiste (`Shell_TrayWnd`)
umgestellt und um Recovery-Fallbacks erweitert (zusätzlicher Explorer-Start,
Shell-Komponenten-Reinit, `userinit.exe`-Fallback).

#### 2) Direktlauf-Warnung „Outlook-Vorlage nicht gefunden"

Bei Script-/Direktläufen konnte die Quellvorlage `NormalEmail.dotm` je nach
Runtime-Kontext fälschlich als fehlend gemeldet werden.

**Fix:** Robuste Kandidatenauflösung mit mehreren Basispfaden (Runtime-Root,
Projektwurzel, `cwd`) implementiert; Warnung tritt im validierten Direktlauf
nicht mehr auf.

### Sonder-Smoke-Check (31.05.2026): Explorer-/Startmenü-Registry

Durchgeführter Verifikationstest der neu ergänzten Windows-Registry-Werte
(`Hidden`, `Start_Layout`, `Start_TrackProgs`, `Start_TrackDocs`,
`Start_Show*`) auf dem Zielsystem:

- Systemstand: `Windows 10 Pro`, Build `26100.8524`
- Ergebnis Konfigurationslauf: `success = true`
- Vorher/Nachher-Vergleich der relevanten Explorer-Keys: stabil auf Zielwerten (`1`)
- Start-Zweig erkannt: `VisiblePlaces` ist vorhanden (build-spezifische Start-Ordnermatrix)
- Hinweis: `TaskbarDa` meldete lokal Zugriff verweigert, ist jedoch als optionaler Wert
   klassifiziert und blockiert den Lauf nicht

Damit ist die neue Registry-Logik für „Ausgeblendete Elemente anzeigen“ sowie die
Startmenü-Fallback-Werte technisch verifiziert.

### Regression

- je eine Ausführung pro wichtiger Font-Familie
- Office-only und vollständige Konfiguration testen
- Template-Backup/Restore gezielt validieren
- OneDrive-Szenario mit teilweise offline Dateien prüfen
