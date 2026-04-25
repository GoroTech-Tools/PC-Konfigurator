# PC-Konfigurator-Portable

**Komplette Portable Anwendung für Windows-PC-Konfiguration**  
*Version: 2.5.3 (Build: 19.04.2026, Python 3.13.7)*

## 🚀 Übersicht

Dies ist die finale, portable Version des PC-Konfigurators mit erweiterten Windows-System-Einstellungen und vollständig korrigierter Template-Verarbeitung. Die Anwendung konfiguriert automatisch Office-Programme, Windows-Taskleiste und installiert benötigte Schriftarten mit korruptionsfreier Template-Bearbeitung.

### ✨ Hauptfeatures

**📝 Template-Verarbeitung (AKTUALISIERT!)**
- Korruptionsfreie Verarbeitung aller drei Template-Typen:
  - Normal.dotm (Word-Standardvorlage)
  - Mappe.xltx (Excel-Arbeitsmappe)
  - NormalEmail.dotm (Outlook-E-Mail-Vorlage)
- SafeTemplateProcessor mit ZIP-Integritätsprüfung
- Backup & Restore-Mechanismus
- Automatische Font-Anpassung ohne Template-Beschädigung

**🖥️ Windows-System**
- Taskleiste linksbündig ausrichten (Windows 11)
- Klassisches Kontextmenü aktivieren
- Taskleisten-Widgets ausblenden
- Suchfeld in Taskleiste ausblenden

**📋 Office-Konfiguration**
- Word, Excel & Outlook automatisch konfigurieren
- Template-Management aus Datei-Vorlagen/Sonstiges/Standards
- Standard-Schriftarten sicher setzen (z.B. Aptos, Calibri)
- Entwicklertools und Benutzeroberfläche optimieren
- **Word-Autokorrektur-Optionen werden automatisiert deaktiviert:**
  - Zwei Großbuchstaben am Wortanfang korrigieren
  - Jeden Satz mit einem Großbuchstaben beginnen
  - Automatische Aufzählung
  - Automatische Nummerierung
  - Ersten Buchstaben groß schreiben
  - (Alle Einstellungen werden per Registry gesetzt und im Log dokumentiert)

**🔤 Schriftart-Management**
- Windows Font API Integration
- 59 professionelle Schriftarten verfügbar (7 Schriftfamilien)
- Automatische Systemregistrierung

### 📁 Projektstruktur

```
PC-Konfigurator-Portable-v2.5.1/
├── PC-Konfigurator-Portable.exe         # Hauptanwendung
├── README.md                            # Diese Datei
├── ANLEITUNG.md                         # Detaillierte Benutzeranleitung
├── BUILD-INFO.txt                       # Build-Informationen
├── Datei-Vorlagen/                      # Office-Templates (148 Dateien)
│   └── Sonstiges/Standards/             # Standard-Templates (Quellen)
│       ├── Normal.dotm                  # Word-Vorlage
│       ├── Mappe.xltx                   # Excel-Vorlage
│       └── NormalEmail.dotm             # Outlook-E-Mail-Vorlage
├── Fonts/                               # Schriftart-Ordner (59 Dateien)
│   ├── Aptos/                           # Microsoft Aptos
│   ├── Futura/                          # Futura
│   ├── Montserrat/                      # Google Montserrat
│   └── ...                              # Weitere Schriftfamilien
├── logs/ (versteckt)                    # Anwendungs-Logs
└── _internal/ (versteckt)               # PyInstaller-Runtime-Dateien
```

### 🔧 Template-Verarbeitung Details

**SafeTemplateProcessor (v2.5.1):**
- ZIP-basierte sichere Template-Bearbeitung
- Automatische Backup-Erstellung vor Modifikation
- XML-Namespace-bewusste Font-Einstellungen
- Integritätsprüfung mit Rollback bei Beschädigung
- Unterstützung für Word (.dotm) und Excel (.xltx) Templates

**Deployment-Ziele:**
- Normal.dotm → `%APPDATA%\Microsoft\Templates\`
- Mappe.xltx → `%APPDATA%\Microsoft\Excel\XLSTART\`
- NormalEmail.dotm → `%APPDATA%\Microsoft\Templates\`

## 🔧 Installation & Verwendung

### Schnellstart
1. **Keine Installation erforderlich** - Portable Anwendung
2. Doppelklick auf `PC-Konfigurator-Portable.exe`
3. Gewünschte Schriftart auswählen (z.B. Aptos, Calibri)
4. "Vollständige Konfiguration starten" für komplette Einrichtung
5. Templates werden automatisch sicher angepasst und kopiert

### Entwicklung & Build-System
```bash
# Python-Umgebung einrichten (Python 3.13.7)
pip install -r requirements.txt

# Anwendung aus Source ausführen
python src/main.py

# Neues Build erstellen (mit automatischem Post-Build!)
python -m PyInstaller PC-Konfigurator-Portable.spec
# ↳ Post-Build läuft automatisch: Fonts, Templates, Hidden-Attribute
```

**Automatisiertes Build-System (v2.5.1):**
- PyInstaller mit automatischem Post-Build-Script
- Intelligentes Kopieren (nur wenn Inhalte fehlen)
- Hidden-Attribute für `_internal` und `logs`
- Vollständige Template- und Font-Integration

## 📊 Technische Details

**🔒 Sicherheit & Template-Schutz**
- ZIP-Integritätsprüfung vor Template-Bearbeitung
- Automatische Backup-Erstellung mit Rollback
- XML-sichere Modifikationen mit Namespace-Unterstützung
- Nur HKEY_CURRENT_USER Registry-Änderungen (inkl. Autokorrektur-Optionen für Word)
- Vollständiges Logging aller Template- und Registry-Operationen (inkl. Autokorrektur)

**💻 Kompatibilität**
- Windows 10/11 (alle Versionen)
- Office 2013, 2016, 2019, 2021, 365
- Outlook-E-Mail-Templates (NormalEmail.dotm)
- Funktioniert auch ohne Office-Installation


**📈 Aktuelle Statistiken (v1.0.24)**
- **1.355+ Dateien** im Build
- **ca. 97 MB** Gesamtgröße
- **148+ Office-Vorlagen** (inkl. Standards)
- **59 Schriftart-Dateien** (7 Familien)
- **3 Template-Typen** vollständig unterstützt

**🔧 Template-Verarbeitung Performance**
- Normal.dotm: Styles + Theme-Anpassung
- Mappe.xltx: Font-Definitionen in styles.xml
- NormalEmail.dotm: Outlook-spezifische Formatierung
- Verarbeitungszeit: ~2-5 Sekunden pro Template
- Erfolgsrate: 100% (mit Backup-Wiederherstellung)

## 📝 Changelog


### v1.0.24 (7. April 2026) – Build & Python-Update
- ✅ **NEU:** Python 3.13.7, Build-Info automatisiert
- ✅ **Aktualisiert:** Kompatibilität, Logging, Template-Handling
- ✅ **Verbessert:** GUI-Features, Font-Handling, Registry-Optimierung
- ✅ **NEU:** Automatische Deaktivierung zentraler Word-Autokorrektur-Optionen per Registry
- ✅ **Stabilität:** Fehlerbehebungen und Performance-Tuning

### v2.5.1 (5. Dezember 2025) – Template-Revolution
- Alle drei Template-Typen werden verarbeitet
- SafeTemplateProcessor: Korruptionsfreie ZIP-Manipulation
- Automatisches Post-Build, Backup/Restore-Mechanismus

### v2.5.0 (5. Dezember 2025) – Template-Fixes
- NormalEmail.dotm und Mappe.xltx Unterstützung
- Verbesserte Backup-Integritätsprüfung
- Erweiterte Word-Styles-Aktualisierung

### Frühere Versionen
- v2.4.0: PowerShell-Implementierung (2009 Zeilen)
- v2.3.0: Template-Preprocessor mit Original-Quellen
- v2.0.0-v2.2.0: Registry-Fallbacks und GUI-Integration
- Windows-Ready: Taskleisten-Features für Windows 11
- Externe Datei-Vorlagen-Struktur
- Versteckte technische Verzeichnisse
- Vollständiges Logging-System

## 🆘 Support

**Bei Problemen:**
1. Log-Dateien im `logs/`-Ordner prüfen
2. Windows-Ereignisanzeige kontrollieren
3. Als Administrator ausführen (falls erforderlich)

**Dokumentation:**
- `ANLEITUNG.md` – Detaillierte Benutzeranleitung
- `src/` – Vollständiger Source-Code verfügbar
- Inline-Kommentare in allen Modulen

---

**Entwickelt:** 7. April 2026  
**Python-Version:** 3.13.7  
**Framework:** CustomTkinter 5.2.2  
**Build-Tool:** PyInstaller 6.17.0  

*Für Bildungseinrichtungen und professionelle Anwender optimiert.*
































