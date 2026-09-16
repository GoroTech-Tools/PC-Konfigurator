# Anwenderprüfung – Vollständige Checkliste (EXE)

Version: 1.0  
Stand: 2026-06-20

## Ziel und Einsatz

Diese Checkliste dient der strukturierten Praxisprüfung der **EXE-Variante** des
`PC-Konfigurator` durch:

- Kolleginnen und Kollegen
- Teilnehmende

Die PowerShell-Variante gilt bereits als stabiler Referenzpfad.

## Testumgebung dokumentieren

- [ ] Name/Team der testenden Person notiert
- [ ] Rolle markiert (Kollegium / Teilnehmende)
- [ ] Windows-Version dokumentiert (z. B. Win10/Win11 + Build)
- [ ] Office-Version dokumentiert (z. B. 2019 / 2021 / M365)
- [ ] OneDrive-Status dokumentiert (aktiv/inaktiv, Dateien lokal verfügbar?)
- [ ] Ausführungsart notiert (normal / als Administrator)

## A) Start und Grundstabilität der EXE

- [ ] `PC-Konfigurator.exe` startet ohne Fehlermeldung
- [ ] GUI wird vollständig geladen (Tabs, Buttons, Statusbereiche sichtbar)
- [ ] Keine sofortigen Abstürze/Hänger in den ersten 2 Minuten
- [ ] Logs werden erzeugt bzw. aktualisiert

## B) Bedienbarkeit und Verständlichkeit

- [ ] Testperson findet den Startpunkt ohne zusätzliche Hilfe
- [ ] Bezeichnungen in Tabs/Buttons sind verständlich
- [ ] Reihenfolge „Konfiguration -> Ausführung -> Ergebnis" ist nachvollziehbar
- [ ] Hinweise/Fehlermeldungen sind verständlich formuliert
- [ ] Start-Tab zeigt die ausführliche Konfigurationsübersicht
- [ ] Hinweis zum Beenden von Edge, Outlook, Excel und Word ist sichtbar

## C) Funktionsprüfung „Vollständige Konfiguration"

- [ ] Lauf startet aus der GUI ohne Fehler
- [ ] Fortschrittsanzeige/Statusmeldungen laufen plausibel durch
- [ ] Font-Installation wird nachvollziehbar durchgeführt
- [ ] Office-Konfiguration wird ohne kritischen Fehler abgeschlossen
- [ ] Template-Anpassung/Kopie wird durchgeführt
- [ ] Abschlussmeldung ist konsistent mit dem realen Ergebnis
- [ ] Bestätigungsdialog wird bei „Nein“ abgebrochen und bei „Ja“ fortgesetzt
- [ ] Laufstatus zeigt Edge-Profil- und Signaturvorgänge

## D) Funktionsprüfung „Nur Office konfigurieren" (nur im erweiterten Modus)

- [ ] Bedienmodus auf **Erweitert** gestellt
- [ ] Lauf startet ohne Fehler
- [ ] Office-Einstellungen werden sichtbar angewendet
- [ ] Lauf endet ohne Absturz/Freeze
- [ ] Ergebnisstatus und Logs passen zusammen

### D1) Office-Detailcheck (Registry + GUI)

- [ ] `src/tools/check-office-registry.ps1` ausgeführt
- [ ] Registry-Sollwerte für Word/Excel plausibel (`IsCompliant = True`) geprüft
- [ ] Offener Punkt in Word geprüft: „Jede Tabellenzeile mit einem Großbuchstaben beginnen" deaktiviert
- [ ] Offener Punkt in Word geprüft: „Bilder einfügen = Mit Text in Zeile"
- [ ] Auffälligkeiten inkl. Office-Version im Feedback dokumentiert

## E) Template- und Font-Handling

- [ ] `Normal.dotm`, `Mappe.xltx`, `NormalEmail.dotm` werden verarbeitet
- [ ] Gewählte Schriftart wird konsistent angewendet
- [ ] Keine offensichtliche Dateikorruption der Vorlagen
- [ ] Verhalten bei fehlenden/gesperrten Dateien ist verständlich (Warnung statt Crash)

## F) Windows-/Registry-Einstellungen

- [ ] Gewählte Optionen (Taskleiste/Kontextmenü/etc.) werden angewendet
- [ ] Explorer-Suchoption „Immer Dateinamen und -inhalte suchen" ist aktiviert (Benutzerkontext)
- [ ] Hinweis auf Explorer-Neustart/Neuanmeldung ist sichtbar
- [ ] Nach Neustart/Neuanmeldung sind Änderungen wie erwartet aktiv
- [ ] Explorer-Neustart über GUI getestet (Taskleiste wird innerhalb ~20 Sekunden wieder sichtbar)
- [ ] Falls verzögert: Recovery-Hinweis erscheint verständlich und ohne Absturz

## F1) Outlook-Hinweisprüfung (modernes Outlook)

- [ ] In der Ausführung wird der Hinweis zur modernen Outlook-Einschränkung angezeigt
- [ ] Erwartung ist klar: klassische Outlook-Engine folgt den Vorgaben, moderne Compose-Oberfläche ggf. eingeschränkt

## G) OneDrive- und Praxis-Sonderfälle

- [ ] Test mit lokal verfügbaren Dateien erfolgreich
- [ ] Test mit teilweise nicht lokal verfügbaren Dateien durchgeführt
- [ ] Anwendung reagiert robust auf OneDrive-Sperren/Platzhalter
- [ ] Fehlerbild ist reproduzierbar dokumentiert (falls aufgetreten)
- [ ] Edge-Profile werden unter `Datei-Vorlagen\Edge-Profile` gesichert
- [ ] E-Mail-Signaturen werden unter `Datei-Vorlagen\E-Mail-Signaturen` gesichert
- [ ] OneDrive-umgeleitetes Dokumente-Verzeichnis wird als Ziel verwendet

## H) Abschlussbewertung

- [ ] Gesamtbewertung vergeben: **OK / eingeschränkt nutzbar / nicht nutzbar**
- [ ] Kritische Blocker separat benannt
- [ ] Empfehlungen für Verbesserungen dokumentiert

## Feedback-Vorlage (ausfüllen)

### 1) Testprofil

- Rolle: ____________________
- Datum/Uhrzeit: ____________________
- Gerät/Standort: ____________________

### 2) Umgebung

- Windows: ____________________
- Office: ____________________
- OneDrive: ____________________

### 3) Durchgeführte Schritte

- ______________________________________________________________
- ______________________________________________________________

### 4) Ergebnis

- Ergebnisstatus (OK/Fehler): ____________________
- Auffälligkeiten/Fehlertext: ____________________
- Log-Datei (Pfad/Name): ____________________

### 5) Verbesserungsvorschläge

- ______________________________________________________________
- ______________________________________________________________
