# DOKUMENTATION_ANWENDER

**Version:** 3.3.2 (31.05.2026)

> Diese Datei enthält den vollständigen Inhalt der früheren `ANLEITUNG.md` aus dem Projektroot.

## Schnellstart

Der `PC-Konfigurator` wird als portable Windows-Anwendung ausgeliefert und kann
ohne klassische Installation direkt gestartet werden.

### 1. Programm starten

- Doppelklick auf `PC-Konfigurator.exe`
- Die Anwendung öffnet sich mit moderner Oberfläche und mehreren Tabs

### 2. Konfiguration auswählen

**Tab „Konfiguration“:**

- Gewünschtes Ziel-Laufwerk wählen (z. B. `Z:` für BFW)
- Schriftart und Schriftgröße für Word/Excel festlegen
- „Individuelle Einstellungen konfigurieren“ für erweiterte Optionen

### 3. Windows-Einstellungen

Im Bereich „Individuelle Einstellungen“ stehen zur Verfügung:

- **Taskleiste linksbündig ausrichten** (Windows 11)
- **Klassisches Kontextmenü aktivieren** (Windows 11)
- **Widgets in Taskleiste ausblenden**
- **Suchfeld in Taskleiste ausblenden**

### 4. Ausführung

**Tab „Ausführung“:**

- **Vollständige Konfiguration starten** – führt alle Anpassungen und Kopiervorgänge automatisiert aus
- **Nur Office konfigurieren** – schnelle Registry-Optimierungen und Template-Handling nur für Office

## Features im Detail

### Registry- und System-Einstellungen

**Word-Optimierungen:**

- Entwicklertools in Multifunktionsleiste
- Lineal und Formatierungszeichen standardmäßig anzeigen
- Tabellenlinien immer sichtbar
- **Automatische Deaktivierung zentraler Autokorrektur-Optionen:**
  - Zwei Großbuchstaben am Wortanfang korrigieren
  - Jeden Satz mit einem Großbuchstaben beginnen
  - Automatische Aufzählung
  - Automatische Nummerierung
  - Ersten Buchstaben groß schreiben

**Excel-Optimierungen:**

- Entwicklertools aktivieren
- Erweiterte Bearbeitungsleiste
- Gitternetzlinien anzeigen

**Windows-System:**

- Taskleiste links statt zentriert (Windows 11)
- Klassisches Kontextmenü (Windows 11)
- Taskleisten-Elemente und Suchfeld ausblenden

### Schriftarten & Template-Sicherheit

**Verfügbare Schriftarten:**

- Aptos (Standard), Aptos Narrow, Arial, Calibri, Futura, Montserrat,
  PT Sans, Raleway u. v. m.

**Sicheres Template-Management:**

- Templates werden vor jeder Änderung automatisch gesichert (Backup/Restore)
- Schriftarten werden systemweit und Office-sicher gesetzt
- Keine Korruption der Originaldateien durch `SafeTemplateProcessor`

## Datenstruktur

Die Anwendung nutzt standardmäßig folgende Laufzeitstruktur:

- `data/Datei-Vorlagen/`
- `data/Fonts/`
- `docs/`
- `logs/`

## Technische Details & Hinweise

### Sicherheit

- Nur `HKEY_CURRENT_USER` wird modifiziert (benutzersicher)
- Keine Systemdateien werden verändert
- Alle Änderungen sind reversibel (Backups)
- Windows Explorer kann automatisch neu gestartet werden

### Protokollierung

- Alle Aktionen werden in `logs/` gespeichert
- Registry- und Template-Änderungen werden dokumentiert
- Fehlermeldungen und Warnungen werden protokolliert

### Kompatibilität

- Windows 10 und Windows 11
- Office 2013, 2016, 2019, 2021, 365
- Funktioniert auch ohne Office-Installation (Windows-/Font-Teile)

## FAQ

**Muss ich Administrator sein?**  
Nein, die meisten Änderungen erfolgen im Benutzerbereich.

**Werden Systemdateien verändert?**  
Nein, geändert werden primär benutzerbezogene Registry-Werte und Templates im Profil.

**Kann ich die Änderungen rückgängig machen?**  
Ja, insbesondere bei Templates über die Backup-/Restore-Mechanik.

**Funktioniert es auch ohne Office?**  
Ja, die Schriftart-Installation und Windows-Einstellungen funktionieren unabhängig.

---

**Stand:** 25.05.2026

