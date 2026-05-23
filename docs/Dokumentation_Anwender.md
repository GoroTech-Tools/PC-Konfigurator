# Dokumentation_Anwender

**Version:** 3.3.1 (23.05.2026)

## Zweck der Anwendung

`PC-Konfigurator-Portable` konfiguriert Windows- und Office-Arbeitsplätze automatisiert,
insbesondere für standardisierte Bildungs- und Verwaltungsumgebungen.

Die Anwendung unterstützt unter anderem:

- Office-Optimierungen (Word, Excel, Outlook)
- sichere Vorlagenverarbeitung
- Schriftart-Auswahl und -Installation
- optionale Windows-Taskleisten-/Explorer-Anpassungen

## Voraussetzungen

- Windows 10 oder Windows 11
- Schreibrechte im Benutzerprofil
- Für Office-Konfigurationen: installierte Office-Anwendungen (empfohlen)
- Vorhandene Projektordner:
  - `Datei-Vorlagen/`
  - `Fonts/`

## Schnellstart

1. Release-ZIP entpacken
2. `PC-Konfigurator-Portable.exe` starten
3. Im Tab **Konfiguration** Laufwerk, Schriftart und Optionen festlegen
4. Im Tab **Ausführung** gewünschte Aktion starten:

- **Vollständige Konfiguration starten**
- **Nur Office konfigurieren**

## Bedienung

### Konfiguration

- Ziel-Laufwerk auswählen (z. B. für Netzwerk-/Schulungsumgebungen)
- Schriftfamilie und Schriftgröße festlegen
- Optional: individuelle Windows-Einstellungen aktivieren

### Ausführung

- **Vollständige Konfiguration**: Office + Windows + Vorlagen + Schriftarten
- **Nur Office konfigurieren**: Fokus auf Office-Optimierungen und Templates

## Was wird typischerweise geändert?

- Registry-Werte im Benutzerkontext (`HKEY_CURRENT_USER`)
- Office-Einstellungen (Word/Excel/Outlook)
- Benutzerbezogene Schriftarten
- Vorlagen im Benutzerprofil (mit Backup/Restore)
- Optionale Explorer-/Taskleistenwerte

## Sicherheit und Rücksicherung

- Es werden keine Systemdateien überschrieben.
- Änderungen erfolgen primär im Benutzerprofil.
- Templates werden vor der Anpassung gesichert.
- Bei Fehlern greift ein Restore-/Rollback-Mechanismus.

## Fehlerbehebung (Troubleshooting)

### Anwendung startet nicht

- Prüfen, ob alle Dateien aus dem Release vollständig entpackt wurden.
- Antivirus-/SmartScreen-Hinweise prüfen.

### Vorlagen werden nicht übernommen

- Sicherstellen, dass Office beendet ist.
- Verfügbarkeit von `Datei-Vorlagen/` prüfen.
- Logdateien im `logs/`-Ordner auswerten.

### Schriftart fehlt in der Auswahl

- Prüfen, ob die Font-Familie korrekt unter `Fonts/` liegt.
- Dateiendungen und Struktur des Font-Ordners prüfen.

### Windows-Änderungen sind nicht sofort sichtbar

- Explorer neu starten oder ab-/anmelden.

## FAQ

**Muss ich Administrator sein?**  
In der Regel nein. Die meisten Änderungen sind benutzerbezogen.

**Kann ich Änderungen rückgängig machen?**  
Ja, insbesondere bei Templates über die Backup-/Restore-Mechanik.

**Funktioniert die App ohne Office?**  
Teilweise. Windows- und Font-Teile funktionieren, Office-Funktionen entsprechend eingeschränkt.
