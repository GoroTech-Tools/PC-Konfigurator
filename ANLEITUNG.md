# PC-Konfigurator-Portable – Anleitung

## 🎯 Schnellstart

### 1. Programm starten
- Doppelklick auf `PC-Konfigurator-Portable.exe`
- Die Anwendung öffnet sich mit moderner Oberfläche und mehreren Tabs

### 2. Konfiguration auswählen
**Tab "Konfiguration":**
- Wählen Sie das gewünschte Ziel-Laufwerk (z. B. Z: für BFW)
- Schriftart und Schriftgröße für Word/Excel individuell festlegen
- "Individuelle Einstellungen konfigurieren" für erweiterte Optionen

### 3. Windows-Einstellungen
Im Bereich "Individuelle Einstellungen" stehen zur Verfügung:
- ✅ **Taskleiste linksbündig ausrichten** (Windows 11)
- ✅ **Klassisches Kontextmenü aktivieren** (Windows 11)
- ✅ **Widgets in Taskleiste ausblenden**
- ✅ **Suchfeld in Taskleiste ausblenden**

### 4. Ausführung
**Tab "Ausführung":**
- **"Vollständige Konfiguration starten"** – Führt alle Anpassungen und Kopiervorgänge automatisiert aus
- **"Nur Office konfigurieren"** – Schnelle Registry-Optimierungen und Template-Handling nur für Office

## 🔍 Features im Detail

### 📊 Registry- und System-Einstellungen
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
	- (Alle Einstellungen werden per Registry gesetzt und im Log dokumentiert)

**Excel-Optimierungen:**
- Entwicklertools aktivieren
- Erweiterte Bearbeitungsleiste
- Gitternetzlinien anzeigen

**Windows-System:**
- Taskleiste links statt zentriert (Windows 11)
- Klassisches Kontextmenü (Windows 11)
- Taskleisten-Elemente und Suchfeld ausblenden

### 🎨 Schriftarten & Template-Sicherheit
**Verfügbare Schriftarten:**
- Aptos (Standard), Aptos Narrow, Arial, Calibri, Futura, Montserrat, PT Sans, Raleway u. v. m.

**Sicheres Template-Management:**
- Templates werden vor jeder Änderung automatisch gesichert (Backup/Restore)
- Schriftarten werden systemweit und Office-sicher gesetzt
- Keine Korruption der Originaldateien durch SafeTemplateProcessor

### 📁 Datei-Vorlagen
Automatisch verfügbare Vorlagen:
- Bewerbungsunterlagen, Geschäftsbriefe, Lernsituationen, Excel-Kalkulationen, Office-Designs u. v. m.

## ⚙️ Technische Details & Hinweise

### 🔒 Sicherheit
- Nur HKEY_CURRENT_USER wird modifiziert (benutzersicher)
- Keine Systemdateien werden verändert
- Alle Änderungen sind reversibel (Backups)
- Windows Explorer wird automatisch neugestartet für sofortige Anwendung

### 📝 Protokollierung
- Alle Aktionen werden in `logs/` gespeichert
- Detaillierte Registry- und Template-Änderungen dokumentiert
- Fehlermeldungen und Warnungen protokolliert

### 🎯 Kompatibilität
- Windows 10 (alle Versionen)
- Windows 11 (alle Versionen)
- Office 2013, 2016, 2019, 2021, 365
- Funktioniert auch ohne Office-Installation

## ❓ Häufige Fragen (FAQ)

**Q: Muss ich Administrator sein?**
A: Nein, alle Änderungen erfolgen nur im Benutzerbereich.

**Q: Werden Systemdateien verändert?**
A: Nein, nur Registry-Einstellungen im HKEY_CURRENT_USER und Office-Templates im Benutzerprofil.

**Q: Kann ich die Änderungen rückgängig machen?**
A: Ja, alle Registry- und Template-Änderungen sind reversibel (Backups werden automatisch erstellt).

**Q: Welche Word-Autokorrektur-Optionen werden automatisch deaktiviert?**
A: Die wichtigsten störenden Autokorrektur-Optionen werden per Registry abgeschaltet:
	- Zwei Großbuchstaben am Wortanfang korrigieren
	- Jeden Satz mit einem Großbuchstaben beginnen
	- Automatische Aufzählung
	- Automatische Nummerierung
	- Ersten Buchstaben groß schreiben
	(Details siehe Logdatei)

**Q: Warum wird der Explorer neu gestartet?**
A: Damit die Windows-Taskleisten-Änderungen sofort sichtbar werden.

**Q: Funktioniert es auch ohne Office?**
A: Ja, die Schriftart-Installation und Windows-Einstellungen funktionieren unabhängig.

## 🆘 Support

Bei Problemen prüfen Sie:
1. Log-Dateien im `logs/`-Ordner
2. Windows-Ereignisanzeige für Fehlermeldungen
3. Starten Sie das Programm als Administrator (falls nötig)

---
**Version:** 2.6.9 (26.04.2026)
**Entwickelt für:** Bildungseinrichtungen und professionelle Anwender
















































