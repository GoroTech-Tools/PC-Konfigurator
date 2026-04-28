# PC-Konfigurator-Portable

Komplette Portable Anwendung fÃ¼r Windows-PC-Konfiguration.

Version: 3.0.0 (Build: 26.04.2026, Python 3.13.7)

## ðŸš€ Ãœbersicht

Dies ist die portable Version des PC-Konfigurators mit erweiterter Windows-Systemkonfiguration, sicherer Template-Verarbeitung und dynamischer Schriftfamilien-Auswahl aus dem Ordner `Fonts`.

Die Anwendung konfiguriert automatisch Office-Programme, Windows-Einstellungen, Office-Vorlagen und benutzerspezifische Schriftarten.

## âœ¨ Hauptfunktionen

### ðŸ“ Template-Verarbeitung

- Korruptionsfreie Verarbeitung aller drei Template-Typen:
  - `Normal.dotm` (Word-Standardvorlage)
  - `Mappe.xltx` (Excel-Arbeitsmappe)
  - `NormalEmail.dotm` (Outlook-E-Mail-Vorlage)
- `SafeTemplateProcessor` mit ZIP-IntegritÃ¤tsprÃ¼fung
- Backup-&-Restore-Mechanismus
- Automatische Font-Anpassung ohne Template-BeschÃ¤digung

### ðŸ–¥ï¸ Windows-System

- Taskleiste linksbÃ¼ndig ausrichten (Windows 11)
- Klassisches KontextmenÃ¼ aktivieren
- Taskleisten-Widgets ausblenden
- Suchfeld in der Taskleiste ausblenden

### ðŸ“‹ Office-Konfiguration

- Word, Excel und Outlook automatisch konfigurieren
- Template-Management aus `Datei-Vorlagen/Sonstiges/Standards`
- Standard-Schriftarten sicher setzen
- Entwicklertools und BenutzeroberflÃ¤che optimieren
- Zentrale Word-Autokorrektur-Optionen per Registry deaktivieren:
  - Zwei GroÃŸbuchstaben am Wortanfang korrigieren
  - Jeden Satz mit einem GroÃŸbuchstaben beginnen
  - Automatische AufzÃ¤hlung
  - Automatische Nummerierung
  - Ersten Buchstaben groÃŸ schreiben

### ðŸ”¤ Schriftart-Management

- Font-Familien werden dynamisch aus dem Ordner `Fonts` erkannt
- Die gewÃ¤hlte Familie wird ins Benutzerprofil installiert
- Die gewÃ¤hlte Familie wird anschlieÃŸend Templates und Office-Einstellungen zugeordnet
- Windows Font API und Benutzer-Registry werden genutzt

## ðŸ“ Projektstruktur

```text
PC-Konfigurator-Portable-v3.0.0/
â”œâ”€â”€ PC-Konfigurator-Portable.exe
â”œâ”€â”€ README.md
â”œâ”€â”€ ANLEITUNG.md
â”œâ”€â”€ BUILD-INFO.txt
â”œâ”€â”€ Datei-Vorlagen/
â”‚   â””â”€â”€ Sonstiges/Standards/
â”‚       â”œâ”€â”€ Normal.dotm
â”‚       â”œâ”€â”€ Mappe.xltx
â”‚       â””â”€â”€ NormalEmail.dotm
â”œâ”€â”€ Fonts/
â”‚   â”œâ”€â”€ Aptos/
â”‚   â”œâ”€â”€ Futura/
â”‚   â”œâ”€â”€ Montserrat/
â”‚   â””â”€â”€ ...
â”œâ”€â”€ logs/          # versteckt
â””â”€â”€ _internal/     # versteckt
```

## ðŸ”§ Template-Verarbeitung im Detail

### SafeTemplateProcessor

- ZIP-basierte sichere Template-Bearbeitung
- Automatische Backup-Erstellung vor Modifikation
- XML-Namespace-bewusste Font-Einstellungen
- IntegritÃ¤tsprÃ¼fung mit Rollback bei BeschÃ¤digung
- UnterstÃ¼tzung fÃ¼r Word- und Excel-Templates

### Deployment-Ziele

- `Normal.dotm` â†’ `%APPDATA%\Microsoft\Templates\`
- `Mappe.xltx` â†’ `%APPDATA%\Microsoft\Excel\XLSTART\`
- `NormalEmail.dotm` â†’ `%APPDATA%\Microsoft\Templates\`

## ðŸ”§ Installation und Verwendung

### Schnellstart

1. Keine Installation erforderlich.
2. Doppelklick auf `PC-Konfigurator-Portable.exe`.
3. GewÃ¼nschte Schriftfamilie auswÃ¤hlen.
4. `VollstÃ¤ndige Konfiguration starten` fÃ¼r die komplette Einrichtung wÃ¤hlen.
5. Templates werden automatisch sicher angepasst und kopiert.

### Entwicklung und Build-System

```bash
# Python-Umgebung einrichten
pip install -r requirements.txt

# Anwendung aus Source ausfÃ¼hren
python src/main.py

# Neues Build erstellen
python -m PyInstaller PC-Konfigurator-Portable.spec
```

Der Post-Build ergÃ¤nzt automatisch:

- Fonts
- Templates
- Dokumentation
- Hidden-Attribute fÃ¼r `_internal` und `logs`

## ðŸ“Š Technische Details

### ðŸ”’ Sicherheit und Template-Schutz

- ZIP-IntegritÃ¤tsprÃ¼fung vor Template-Bearbeitung
- Automatische Backup-Erstellung mit Rollback
- XML-sichere Modifikationen mit Namespace-UnterstÃ¼tzung
- Nur `HKEY_CURRENT_USER` wird geÃ¤ndert
- VollstÃ¤ndiges Logging aller Template- und Registry-Operationen

### ðŸ’» KompatibilitÃ¤t

- Windows 10 und Windows 11
- Office 2013, 2016, 2019, 2021 und Microsoft 365
- Outlook-E-Mail-Templates (`NormalEmail.dotm`)
- Funktioniert auch ohne Office-Installation fÃ¼r Windows-/Font-Teile

### ðŸ“ˆ Aktuelle Statistiken

- 3 Template-Typen vollstÃ¤ndig unterstÃ¼tzt
- 15 dynamisch erkannte Font-Familien im aktuellen Fonts-Bestand
- 55 Schriftart-Dateien im Build
- 173 Vorlagen-Dateien im Build

### âš¡ Template-Verarbeitung

- `Normal.dotm`: Styles- und Theme-Anpassung
- `Mappe.xltx`: Font-Definitionen in `styles.xml`
- `NormalEmail.dotm`: Outlook-spezifische Formatierung
- Verarbeitungszeit typischerweise ca. 2 bis 5 Sekunden pro Template

## ðŸ“ Changelog

### v3.0.0 (26. April 2026)

- Dynamische Font-Familien-Auswahl aus dem Ordner `Fonts`
- GewÃ¤hlte Font-Familie wird gezielt ins Benutzerprofil installiert
- Zuordnung der gewÃ¤hlten Familie zu Templates und Office-Konfiguration verbessert
- EXE- und Fenster-Icon korrigiert
- Release-ZIP enthÃ¤lt `_internal` und `logs` zuverlÃ¤ssig
- ZIP-Struktur vereinfacht
- Release-ZIP-Artefakte werden nicht mehr in Git versioniert

### v2.6.9 (26. April 2026)

- Build- und Packaging-Verbesserungen
- Portable Release mit Hidden-Verzeichnissen

### FrÃ¼here Versionen

- `v2.5.1`: Template-Revolution mit sicherer ZIP-Manipulation
- `v2.5.0`: Template-Fixes fÃ¼r `NormalEmail.dotm` und `Mappe.xltx`
- `v2.4.0`: groÃŸe PowerShell-Implementierung

## ðŸ†˜ Support

### Bei Problemen

1. Log-Dateien im Ordner `logs/` prÃ¼fen.
2. Windows-Ereignisanzeige kontrollieren.
3. Falls nÃ¶tig als Administrator starten.

### Dokumentation

- `ANLEITUNG.md` â€“ Detaillierte Benutzeranleitung
- `src/` â€“ VollstÃ¤ndiger Source-Code
- Inline-Kommentare in den Modulen

---

Entwickelt: 26. April 2026

Python-Version: 3.13.7

Framework: CustomTkinter 5.2.2

Build-Tool: PyInstaller 6.17.0

FÃ¼r Bildungseinrichtungen und professionelle Anwender optimiert.
























