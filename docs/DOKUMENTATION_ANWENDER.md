# DOKUMENTATION_ANWENDER

**Version:** 3.3.95 (22.09.2026)

> Diese Datei enthält den vollständigen Inhalt der früheren `ANLEITUNG.md` aus dem Projektroot.

## Schnellstart

Der `PC-Konfigurator` wird als portable Windows-Anwendung ausgeliefert und kann
ohne klassische Installation direkt gestartet werden.

## Ablauf auf einen Blick

```mermaid
flowchart LR
  A[Programm starten] --> B[Start-Tab]
  B --> C[Weiter]
  C --> D[Konfiguration]
  D --> E[Weiter]
  E --> F[Ausführung]
  F --> G[Vollständige Konfiguration]
  F --> H[Nur Office<br/>nur im erweiterten Modus]
  G --> I[Status und Logs prüfen]
  H --> I
```

![Ablauf Dokumentation Anwender](diagramme/anwender_ablauf.svg)

_Mermaid-Quelle: `docs/diagramme/anwender_ablauf.mmd`_

### 1. Programm starten

- Doppelklick auf `PC-Konfigurator.exe`
- Die Anwendung öffnet sich mit moderner Oberfläche und mehreren Tabs

### 2. Konfiguration auswählen

**Tab „Konfiguration“:**

- Gewünschtes Ziel-Laufwerk wählen (z. B. `Z:` für BFW)
- Schriftart und Schriftgröße für Word/Excel festlegen
- Optional: **„Vorhandene Datei-Vorlagen löschen und durch aktuellen
  Programmstand ersetzen“** aktivieren (siehe Abschnitt „Datei-Vorlagen-Bibliothek
  und Zurücksetzen-Option“ weiter unten)
- Über **„Weiter“** unten zum Tab `Ausführung` wechseln
- Bedienmodus `Einfach`/`Erweitert` im Start-Tab wählen

### 3. Windows-Einstellungen

Im Bereich „Individuelle Einstellungen“ stehen zur Verfügung:

- **Taskleiste linksbündig ausrichten** (Windows 11)
- **Klassisches Kontextmenü aktivieren** (Windows 11)
- **Widgets in Taskleiste ausblenden**
- **Suchfeld in Taskleiste ausblenden**
- **Startmenü-Modus umschalten:** `Windows 11 (empfohlen)` oder `Klassisch (Fallback)`

Hinweis: Der gewählte Startmenü-Modus wird dauerhaft gespeichert und beim nächsten
Start still in die Registry geschrieben (Benutzerkontext, ohne Adminrechte). Der
Windows-Explorer wird dabei **nicht** neu gestartet — die Wirkung des gesetzten Modus
tritt beim nächsten Windows-Login automatisch über den Autostart-Guard in Kraft.
Wird der Modus manuell in der GUI umgeschaltet, startet der Explorer sofort neu,
damit die Änderung sofort sichtbar wird.

Falls die Taskleiste nach einem Explorer-Neustart nicht sofort erscheint, führt die
Anwendung automatisch zusätzliche Wiederherstellungsschritte aus. In seltenen Fällen
kann die Shell trotzdem noch einige Sekunden benötigen.

Zusätzlich hinterlegt die Anwendung eine externe Autostart-Variante im Benutzerprofil,
damit der Startmenü-Modus bei jeder Windows-Anmeldung automatisch angewendet wird:

- `%APPDATA%\\PC-Konfigurator\\startmenu-guard\\Ensure-StartmenuMode.ps1`
- `%APPDATA%\\PC-Konfigurator\\startmenu-guard\\Ensure-StartmenuMode.cmd`
- `%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\PC-Konfigurator-StartmenuGuard.cmd`

### 3.1 Sichtbarkeit der Registerkarten

- Die Registerkarten im Hauptfenster und im separaten Registry-Detailfenster
  verwenden eine stabile Darstellung ohne aggressive Breiten-Skalierung.
- Dadurch bleiben die Tab-Beschriftungen auch bei kleineren Fensterbreiten
  zuverlässig lesbar.

### 4. Ausführung

**Tab „Ausführung“:**

- **Vollständige Konfiguration starten** – führt alle Anpassungen und Kopiervorgänge automatisiert aus
- **Nur Office konfigurieren** – nur im **erweiterten Modus**, schnelle Registry-Optimierungen und Template-Handling nur für Office

Vor der vollständigen Konfiguration müssen Microsoft Edge, Microsoft Outlook,
Microsoft Excel und Microsoft Word vollständig beendet werden. Beim Klick auf
**„Vollständige Konfiguration starten“** wird dies mit **Ja** bestätigt. Nur
dann beginnt der Lauf.

Wenn der Office-Preclose aktiviert ist, beendet die Anwendung Word, Excel und
Outlook zusätzlich automatisch **vor** der Datei-Vorlagen-Synchronisation. Ein
zweiter Konfigurationslauf kann während eines laufenden Laufes nicht gestartet
werden, damit persönliche Office-Dateien nicht gleichzeitig verarbeitet werden.
Ein vorübergehendes Problem beim optionalen Building-Blocks-Backup wird als
Warnung angezeigt; die übrige Konfiguration läuft weiter.

Im Laufstatus werden die Wiederherstellung sowie die Sicherung/Aktualisierung
von Edge-Profilen und E-Mail-Signaturen als eigene Schritte angezeigt.

### Building Blocks manuell bearbeiten

Für individuelle Word-Bausteine steht im Menü **Tools** der Eintrag
**Building Blocks manuell bearbeiten** zur Verfügung. Die Funktion arbeitet nur
mit der Building-Blocks-Datei des aktuell angemeldeten Windows-Benutzers:

1. Alle Office-Programme möglichst schließen.
2. **Tools → Building Blocks manuell bearbeiten** auswählen.
3. Die angezeigte Sicherheitsabfrage bestätigen.
4. Die Datei in Word bearbeiten und dort speichern.

Vor dem Öffnen wird automatisch eine datierte Sicherung im Ordner
`%APPDATA%\Microsoft\Document Building Blocks\<LCID>\16\_PC-Konfigurator-Backups`
angelegt. Wird keine passende Datei gefunden, bleibt der bestehende Office- und
Template-Workflow unverändert. Zusätzlich wird die persönliche Datei beim
Datei-Vorlagen-Abgleich nach
`Datei-Vorlagen\Sonstiges\Building Blocks\Building Blocks.dotx` gesichert.
Ist diese Sicherung neuer als die Datei im Benutzerprofil, wird sie vor dem
Öffnen des Tools automatisch wieder in `%APPDATA%` übernommen.

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

**Aktueller Status:**

- Die Word-Optionen „Jede Tabellenzeile mit einem Großbuchstaben beginnen" und „Bilder einfügen" = „Mit Text in Zeile" sind im `PC-Konfigurator` inzwischen als Standardkonfiguration hinterlegt.

**Word-Einfügeoptionen:**

- innerhalb desselben Dokuments: **Ursprüngliche Formatierung beibehalten**
- zwischen zwei Dokumenten: **Formatierung zusammenführen**
- bei nicht übereinstimmenden Formatvorlagen: **Formatvorlagen des Ziels verwenden**
- aus anderen Programmen: **Nur den Text übernehmen**

Die Schriftart- und Schriftgrößenanpassung betrifft ausschließlich die
Absatzformatvorlagen **Standard** und **Kein Leerraum**. Überschriften, Titel und
andere Formatvorlagen werden nicht verändert.

**Excel-Optimierungen:**

- Entwicklertools aktivieren
- Erweiterte Bearbeitungsleiste
- Gitternetzlinien anzeigen

**Windows-System:**

- Taskleiste links statt zentriert (Windows 11)
- Klassisches Kontextmenü (Windows 11)
- Taskleisten-Elemente und Suchfeld ausblenden
- Explorer-Suche auf „Immer Dateinamen und -inhalte suchen" setzen (pro Benutzer)
- Empfohlene Dateien im Startmenü, zuletzt verwendete Dateien im Datei-Explorer und Sprunglisten standardmäßig deaktivieren
- Anwendungen im Startmenü standardmäßig als Liste anzeigen

**Outlook-Hinweis (modernes Outlook):**

- Die klassische Outlook-Engine übernimmt Standardfonts aus Registry/Template i. d. R. zuverlässig.
- Outlook 2024 LTSC (classic) wird über die Office-16.0-Registry (`Common\MailSettings` und `Outlook\Options`) sowie `NormalEmail.dotm` versorgt. Schriftart und -größe für neue Nachrichten sowie Antworten/Weiterleitungen werden dabei gemeinsam gesetzt.
- Die Outlook-Vorlage wird zusätzlich an die gewählte Theme-Schrift angepasst. Dadurch greift die Auswahl auch dann, wenn Outlook classic die Theme-Definition statt nur der direkten Formatvorlage verwendet.
- Der Standardwert der Outlook-Schriftgröße beträgt 12 pt und kann im Tab „Konfiguration“ angepasst werden.
- In der modernen Outlook-Compose-Oberfläche kann Microsoft diese Vorgaben teilweise durch eigene UI-Standards übersteuern.
- Die Anwendung blendet dazu einen transparenten Hinweis in der Ausführung ein.

### Schriftarten & Template-Sicherheit

**Verfügbare Schriftarten:**

- Aptos (Standard), Aptos Narrow, Arial, Calibri, Futura, Montserrat,
  PT Sans, Raleway u. v. m.

**Sicheres Template-Management:**

- Templates werden vor jeder Änderung automatisch gesichert (Backup/Restore)
- Schriftarten werden systemweit und Office-sicher gesetzt
- Keine Korruption der Originaldateien durch `SafeTemplateProcessor`
- Building Blocks werden im normalen Konfigurationslauf optional synchronisiert;
  Office wird dafür bei aktiviertem Preclose bereits vor der Synchronisation
  beendet. Die manuelle Bearbeitung wird ausschließlich über das Tools-Menü
  gestartet.

### Edge-Profile und E-Mail-Signaturen

Diese Sicherung/Wiederherstellung ist **standardmäßig deaktiviert**, da das
ZIP-Komprimieren größerer Edge-Profile spürbar Zeit kosten kann. Über die
Checkbox „Edge-Profile synchronisieren“ im Tab „Konfiguration“ lässt sie sich
bei Bedarf aktivieren; ist sie deaktiviert, wird der entsprechende Schritt im
Ablauf übersprungen (Statushinweis „nicht aktiviert“).

Edge-Profile werden ZIP-komprimiert als `Datei-Vorlagen\Sonstiges\Edge-Profile.zip`
gesichert (spart deutlich Speicherplatz gegenüber einem unkomprimierten Ordner).
Outlook-Signaturen werden separat unter `Datei-Vorlagen\Sonstiges\E-Mail-Signaturen`
abgelegt. Vorhandene lokale Signaturen werden bei der Wiederherstellung nicht
überschrieben.

Das Ziel „Dokumente“ berücksichtigt OneDrive-Umleitungen. Ohne Umleitung wird
`C:\Users\<Benutzer>\Dokumente` verwendet. Läuft OneDrive gerade aktiv im
Hintergrund und synchronisiert, kann das Anlegen neuer Unterordner kurzzeitig
fehlschlagen; die Anwendung wiederholt solche Schreibversuche automatisch mit
steigender Wartezeit (bis zu ca. 15–20 Sekunden), bevor ein Fehler gemeldet wird.

### Datei-Vorlagen-Bibliothek und Zurücksetzen-Option

Bei jedem Lauf wird die mitgelieferte Vorlagenbibliothek (Standard-Templates,
Corporate-Design-Dateien usw.) automatisch mit dem Zielordner `Datei-Vorlagen`
abgeglichen. Dabei werden nur fehlende oder neuere Dateien ergänzt; bereits
vorhandene bzw. neuere Dateien im Ziel bleiben unangetastet.

Im Tab „Konfiguration“ steht zusätzlich die Option **„Vorhandene Datei-Vorlagen
löschen und durch aktuellen Programmstand ersetzen“** zur Verfügung:

- Standardmäßig deaktiviert.
- Beim Aktivieren erscheint ein Bestätigungsdialog mit dem ausdrücklichen
  Hinweis, dass dabei auch eigene, nachträglich hinzugefügte oder geänderte
  Vorlagendateien im Zielordner unwiderruflich verloren gehen.
- Wird die Aktion bestätigt, löscht der nächste Lauf den kompletten
  `Datei-Vorlagen`-Ordner im Ziel und ersetzt ihn 1:1 durch den aktuellen
  Programmstand.
- Die Option gilt als einmalige Aktion und wird nach dem Lauf automatisch
  wieder deaktiviert.

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

**Warum erscheinen manchmal Meldungen von Windows-Sicherheit während des Laufs?**  
Windows-Sicherheit (z. B. der Kontrollierte Ordnerzugriff) kann beim Schreiben in
Ordner wie „Dokumente" informative Meldungen anzeigen. Diese sind in der Regel
harmlos: Der `PC-Konfigurator` wiederholt betroffene Schreibvorgänge automatisch
und führt sie erfolgreich aus. Ein Eingreifen ist normalerweise nicht nötig.

---

**Stand:** 20.06.2026
