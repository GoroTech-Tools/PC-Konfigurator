# PC-Konfigurator-Portable

Komplette portable Anwendung für Windows-PC-Konfiguration.

**Version:** 3.3.1 (Build: 23.05.2026, Python 3.13.7)

## Übersicht

Dies ist die portable Version des PC-Konfigurators mit erweiterter
Windows-Systemkonfiguration, sicherer Template-Verarbeitung und dynamischer
Schriftfamilien-Auswahl aus dem Ordner `Fonts`.

Die Anwendung konfiguriert automatisch Office-Programme, Windows-Einstellungen,
Office-Vorlagen und benutzerspezifische Schriftarten.

## Hauptfunktionen

### Template-Verarbeitung

- Korruptionsfreie Verarbeitung aller drei Template-Typen:
  - `Normal.dotm` (Word-Standardvorlage)
  - `Mappe.xltx` (Excel-Arbeitsmappe)
  - `NormalEmail.dotm` (Outlook-E-Mail-Vorlage)
- `SafeTemplateProcessor` mit ZIP-Integritätsprüfung
- Backup-&-Restore-Mechanismus
- Automatische Font-Anpassung ohne Template-Beschädigung

### Windows-System

- Taskleiste linksbündig ausrichten (Windows 11)
- Klassisches Kontextmenü aktivieren
- Taskleisten-Widgets ausblenden
- Suchfeld in der Taskleiste ausblenden

### Office-Konfiguration

- Word, Excel und Outlook automatisch konfigurieren
- Template-Management aus `Datei-Vorlagen/Sonstiges/Standards`
- Standard-Schriftarten sicher setzen
- Entwicklertools und Benutzeroberfläche optimieren
- Zentrale Word-Autokorrektur-Optionen per Registry deaktivieren:
  - Zwei Großbuchstaben am Wortanfang korrigieren
  - Jeden Satz mit einem Großbuchstaben beginnen
  - Automatische Aufzählung
  - Automatische Nummerierung
  - Ersten Buchstaben groß schreiben

### Schriftart-Management

- Font-Familien werden dynamisch aus dem Ordner `Fonts` erkannt
- Die gewählte Familie wird ins Benutzerprofil installiert
- Die gewählte Familie wird anschließend Templates und Office-Einstellungen zugeordnet
- Windows Font API und Benutzer-Registry werden genutzt

## Projektstruktur

```text
PC-Konfigurator-Portable-v3.2.5/
├── PC-Konfigurator-Portable.exe
├── README.md
├── docs/
│   ├── README.md
│   ├── Dokumentation_Anwender.md
│   ├── Dokumentation_Technik.md
│   └── Dokumentation_Checkliste.md
├── BUILD-INFO.txt
├── Datei-Vorlagen/
│   └── Sonstiges/Standards/
│       ├── Normal.dotm
│       ├── Mappe.xltx
│       └── NormalEmail.dotm
├── Fonts/
│   ├── Aptos/
│   ├── Futura/
│   ├── Montserrat/
│   └── ...
├── logs/          # versteckt
└── _internal/     # versteckt
```

## Template-Verarbeitung im Detail

### SafeTemplateProcessor

- ZIP-basierte sichere Template-Bearbeitung
- Automatische Backup-Erstellung vor Modifikation
- XML-Namespace-bewusste Font-Einstellungen
- Integritätsprüfung mit Rollback bei Beschädigung
- Unterstützung für Word- und Excel-Templates

### Deployment-Ziele

- `Normal.dotm` → `%APPDATA%\Microsoft\Templates\`
- `Mappe.xltx` → `%APPDATA%\Microsoft\Excel\XLSTART\`
- `NormalEmail.dotm` → `%APPDATA%\Microsoft\Templates\`

## Installation und Verwendung

### Schnellstart

1. Keine Installation erforderlich.
2. Doppelklick auf `PC-Konfigurator-Portable.exe`.
3. Gewünschte Schriftfamilie auswählen.
4. `Vollständige Konfiguration starten` für die komplette Einrichtung wählen.
5. Templates werden automatisch sicher angepasst und kopiert.

### Entwicklung und Build-System

```bash
# Python-Umgebung einrichten
pip install -r requirements.txt

# Anwendung aus Source ausführen
python src/main.py

# Neues Build erstellen
python -m PyInstaller PC-Konfigurator-Portable.spec
```

Der Post-Build ergänzt automatisch:

- Fonts
- Templates
- Dokumentation
- Hidden-Attribute für `_internal` und `logs`

## Technische Details

### Sicherheit und Template-Schutz

- ZIP-Integritätsprüfung vor Template-Bearbeitung
- Automatische Backup-Erstellung mit Rollback
- XML-sichere Modifikationen mit Namespace-Unterstützung
- Nur `HKEY_CURRENT_USER` wird geändert
- Vollständiges Logging aller Template- und Registry-Operationen

### Kompatibilität

- Windows 10 und Windows 11
- Office 2013, 2016, 2019, 2021 und Microsoft 365
- Outlook-E-Mail-Templates (`NormalEmail.dotm`)
- Funktioniert auch ohne Office-Installation für Windows-/Font-Teile

### Aktuelle Statistiken

- 3 Template-Typen vollständig unterstützt
- 15 dynamisch erkannte Font-Familien im aktuellen Fonts-Bestand
- 55 Schriftart-Dateien im Build
- 173 Vorlagen-Dateien im Build

### Template-Verarbeitungszeiten

- `Normal.dotm`: Styles- und Theme-Anpassung
- `Mappe.xltx`: Font-Definitionen in `styles.xml`
- `NormalEmail.dotm`: Outlook-spezifische Formatierung
- Verarbeitungszeit typischerweise ca. 2 bis 5 Sekunden pro Template

## Changelog

### v3.2.5 (28. April 2026)

- Registry-UX deutlich verbessert (übersichtlichere Darstellung, Erklärungen)
- Word-Startverhalten wiederhergestellt (Dokument beim Start nicht automatisch öffnen)
- `publish_release.ps1` für automatisiertes Release-Packaging hinzugefügt
- `SafeTemplateProcessor` erweitert
- `office_configurator.py` überarbeitet
- Build-Skript (`build.ps1`) verbessert

### v3.0.0 (26. April 2026)

- Dynamische Font-Familien-Auswahl aus dem Ordner `Fonts`
- Gewählte Font-Familie wird gezielt ins Benutzerprofil installiert
- Zuordnung der gewählten Familie zu Templates und Office-Konfiguration verbessert
- EXE- und Fenster-Icon korrigiert
- Release-ZIP enthält `_internal` und `logs` zuverlässig
- ZIP-Struktur vereinfacht
- Release-ZIP-Artefakte werden nicht mehr in Git versioniert

### v2.6.9 (26. April 2026)

- Build- und Packaging-Verbesserungen
- Portable Release mit Hidden-Verzeichnissen

### Frühere Versionen

- `v2.5.1`: Template-Revolution mit sicherer ZIP-Manipulation
- `v2.5.0`: Template-Fixes für `NormalEmail.dotm` und `Mappe.xltx`
- `v2.4.0`: große PowerShell-Implementierung

## Support

### Bei Problemen

1. Log-Dateien im Ordner `logs/` prüfen.
2. Windows-Ereignisanzeige kontrollieren.
3. Falls nötig als Administrator starten.

### Dokumentation

- `docs/README.md` – Dokumentations-Einstieg
- `docs/Dokumentation_Anwender.md` – Detaillierte Benutzeranleitung
- `docs/Dokumentation_Technik.md` – Technische Dokumentation
- `docs/Dokumentation_Checkliste.md` – Doku-Qualitätscheckliste
- `src/` – Vollständiger Source-Code
- Inline-Kommentare in den Modulen

---

Entwickelt: 28. April 2026 | Python 3.13.7 | CustomTkinter 5.2.2 | PyInstaller 6.17.0

Für Bildungseinrichtungen und professionelle Anwender optimiert.
