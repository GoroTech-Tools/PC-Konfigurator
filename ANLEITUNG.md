# PC-Konfigurator-Portable â€“ Anleitung

## ðŸŽ¯ Schnellstart

### 1. Programm starten

- Doppelklick auf `PC-Konfigurator-Portable.exe`
- Die Anwendung Ã¶ffnet sich mit moderner OberflÃ¤che und mehreren Tabs

### 2. Konfiguration auswÃ¤hlen

**Tab "Konfiguration":**

- WÃ¤hlen Sie das gewÃ¼nschte Ziel-Laufwerk (z. B. Z: fÃ¼r BFW)
- Schriftart und SchriftgrÃ¶ÃŸe fÃ¼r Word/Excel individuell festlegen
- "Individuelle Einstellungen konfigurieren" fÃ¼r erweiterte Optionen

### 3. Windows-Einstellungen

Im Bereich "Individuelle Einstellungen" stehen zur VerfÃ¼gung:

- âœ… **Taskleiste linksbÃ¼ndig ausrichten** (Windows 11)
- âœ… **Klassisches KontextmenÃ¼ aktivieren** (Windows 11)
- âœ… **Widgets in Taskleiste ausblenden**
- âœ… **Suchfeld in Taskleiste ausblenden**

### 4. AusfÃ¼hrung

**Tab "AusfÃ¼hrung":**

- **"VollstÃ¤ndige Konfiguration starten"** â€“ FÃ¼hrt alle Anpassungen und KopiervorgÃ¤nge automatisiert aus
- **"Nur Office konfigurieren"** â€“ Schnelle Registry-Optimierungen und Template-Handling nur fÃ¼r Office

## ðŸ” Features im Detail

### ðŸ“Š Registry- und System-Einstellungen

**Word-Optimierungen:**

- Entwicklertools in Multifunktionsleiste
- Lineal und Formatierungszeichen standardmÃ¤ÃŸig anzeigen
- Tabellenlinien immer sichtbar

- **Automatische Deaktivierung zentraler Autokorrektur-Optionen:**

- Zwei GroÃŸbuchstaben am Wortanfang korrigieren
- Jeden Satz mit einem GroÃŸbuchstaben beginnen
- Automatische AufzÃ¤hlung
- Automatische Nummerierung
- Ersten Buchstaben groÃŸ schreiben
- (Alle Einstellungen werden per Registry gesetzt und im Log dokumentiert)

**Excel-Optimierungen:**

- Entwicklertools aktivieren
- Erweiterte Bearbeitungsleiste
- Gitternetzlinien anzeigen

**Windows-System:**

- Taskleiste links statt zentriert (Windows 11)
- Klassisches KontextmenÃ¼ (Windows 11)
- Taskleisten-Elemente und Suchfeld ausblenden

### ðŸŽ¨ Schriftarten & Template-Sicherheit

**VerfÃ¼gbare Schriftarten:**

- Aptos (Standard), Aptos Narrow, Arial, Calibri, Futura, Montserrat, PT Sans, Raleway u. v. m.

**Sicheres Template-Management:**

- Templates werden vor jeder Ã„nderung automatisch gesichert (Backup/Restore)
- Schriftarten werden systemweit und Office-sicher gesetzt
- Keine Korruption der Originaldateien durch SafeTemplateProcessor

### ðŸ“ Datei-Vorlagen

Automatisch verfÃ¼gbare Vorlagen:

- Bewerbungsunterlagen, GeschÃ¤ftsbriefe, Lernsituationen, Excel-Kalkulationen, Office-Designs u. v. m.

## âš™ï¸ Technische Details & Hinweise

### ðŸ”’ Sicherheit

- Nur HKEY_CURRENT_USER wird modifiziert (benutzersicher)
- Keine Systemdateien werden verÃ¤ndert
- Alle Ã„nderungen sind reversibel (Backups)
- Windows Explorer wird automatisch neugestartet fÃ¼r sofortige Anwendung

### ðŸ“ Protokollierung

- Alle Aktionen werden in `logs/` gespeichert
- Detaillierte Registry- und Template-Ã„nderungen dokumentiert
- Fehlermeldungen und Warnungen protokolliert

### ðŸŽ¯ KompatibilitÃ¤t

- Windows 10 (alle Versionen)
- Windows 11 (alle Versionen)
- Office 2013, 2016, 2019, 2021, 365
- Funktioniert auch ohne Office-Installation

## â“ HÃ¤ufige Fragen (FAQ)

**Q: Muss ich Administrator sein?**
A: Nein, alle Ã„nderungen erfolgen nur im Benutzerbereich.

**Q: Werden Systemdateien verÃ¤ndert?**
A: Nein, nur Registry-Einstellungen im HKEY_CURRENT_USER und Office-Templates im Benutzerprofil.

**Q: Kann ich die Ã„nderungen rÃ¼ckgÃ¤ngig machen?**
A: Ja, alle Registry- und Template-Ã„nderungen sind reversibel (Backups werden automatisch erstellt).

**Q: Welche Word-Autokorrektur-Optionen werden automatisch deaktiviert?**
A: Die wichtigsten stÃ¶renden Autokorrektur-Optionen werden per Registry abgeschaltet:

- Zwei GroÃŸbuchstaben am Wortanfang korrigieren
- Jeden Satz mit einem GroÃŸbuchstaben beginnen
- Automatische AufzÃ¤hlung
- Automatische Nummerierung
- Ersten Buchstaben groÃŸ schreiben
  (Details siehe Logdatei)

**Q: Warum wird der Explorer neu gestartet?**
A: Damit die Windows-Taskleisten-Ã„nderungen sofort sichtbar werden.

**Q: Funktioniert es auch ohne Office?**
A: Ja, die Schriftart-Installation und Windows-Einstellungen funktionieren unabhÃ¤ngig.

## ðŸ†˜ Support

Bei Problemen prÃ¼fen Sie:

1. Log-Dateien im `logs/`-Ordner
2. Windows-Ereignisanzeige fÃ¼r Fehlermeldungen
3. Starten Sie das Programm als Administrator (falls nÃ¶tig)

---
**Version:** 3.2.5 (28.04.2026)
**Entwickelt fÃ¼r:** Bildungseinrichtungen und professionelle Anwender
























