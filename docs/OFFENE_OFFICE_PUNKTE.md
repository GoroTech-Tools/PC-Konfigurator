# Offene Office-Punkte – Validierungssammlung

Stand: 2026-06-08

Diese Datei sammelt Ergebnisse zu aktuell offenen Office-Validierungspunkten,
die nicht vollständig belastbar per Registry verifiziert sind.

## Ziel

- Einheitliche Dokumentation von Testergebnissen je Office-Version
- Nachvollziehbarkeit von Soll-/Ist-Verhalten
- Schnellere Entscheidung, ob zusätzliche Registry-Keys oder GUI-basierte
  Hinweise erforderlich sind

## Offene Prüfpunkte

1. **Word:** „Jede Tabellenzeile mit einem Großbuchstaben beginnen" = deaktiviert *(im PC-Konfigurator jetzt per Registry gesetzt)*
2. **Word:** „Bilder einfügen" = „Mit Text in Zeile" *(im PC-Konfigurator jetzt per Registry gesetzt)*

## Bereits im PC-Konfigurator umgesetzt

- `AutoFormatCapitalizeTableCells = 0`
- `PictureInsertLayout = 1`

Die folgenden Abschnitte bleiben als Nachweis-/Prüfvorlage für Testclienten erhalten.

**Kurzfazit:** Die beiden Word-Optionen sind im PC-Konfigurator jetzt standardmäßig gesetzt; offen ist nur noch der praktische Nachweis auf einem echten Testclient.

## Vorgehen pro Testlauf

1. `tools/check-office-registry.ps1` ausführen und Ergebnis sichern.
2. Word starten und die beiden offenen Punkte in den Optionen prüfen.
3. Einen kurzen Praxistest mit Einfügen/Tabellen durchführen.
4. Ergebnis unten als neuen Eintrag ergänzen.

## Testprotokoll-Vorlage

> Bitte pro Lauf einen neuen Block kopieren und ausfüllen.

### Lauf (Nummer eintragen)

- Datum/Uhrzeit:
- Tester:in / Team:
- Gerät:
- Windows-Version:
- Office-Version (z. B. 2019/2021/M365 + Build):
- Ausführung (normal / Administrator):

#### Registry-Check

- Script: `tools/check-office-registry.ps1`
- Ergebnis (Treffer):
- Auffällige Werte:

#### Word-Optionen (GUI)

- „Jede Tabellenzeile mit einem Großbuchstaben beginnen" deaktiviert:
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden
- „Bilder einfügen" = „Mit Text in Zeile":
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden

#### Praxistest

- Tabelle: Verhalten beim Eingeben neuer Zeilen:
- Bild einfügen: Verhalten/Umbruch:
- Abweichungen vom Soll:

#### Bewertung

- Ergebnis:
  - [ ] OK
  - [ ] eingeschränkt
  - [ ] nicht OK
- Handlungsempfehlung:

---

## Entscheidungskriterien für Abschluss

Ein Punkt kann als „stabil verifiziert" markiert werden, wenn:

- mindestens 3 Testläufe auf unterschiedlichen Office-Ständen vorliegen,
- das Verhalten konsistent ist,
- und die Einstellung reproduzierbar (Registry oder GUI dokumentiert) gesetzt werden kann.

## Go/No-Go-Abnahme (kurz)

### Go

- Mindestens 3 dokumentierte Läufe auf unterschiedlichen Office-Ständen liegen vor.
- Beide offenen Prüfpunkte sind in allen Läufen konsistent nachvollziehbar.
- Es gibt keine kritische Abweichung, die den produktiven Einsatz blockiert.

### No-Go

- Weniger als 3 belastbare Läufe vorhanden, **oder**
- einer der offenen Prüfpunkte zeigt widersprüchliches Verhalten zwischen den Office-Ständen, **oder**
- ein Verhalten ist fachlich nicht akzeptabel und derzeit nicht reproduzierbar steuerbar.

### Entscheidungsvorlage

- Entscheidung (Go/No-Go):
- Datum:
- Verantwortlich:
- Begründung (1–3 Sätze):
- Nächster Schritt (falls No-Go):

## Musterläufe (Startvorlagen)

### Musterlauf 1 (aus aktueller Sitzung)

- Datum/Uhrzeit: 2026-06-08T02:01
- Tester:in / Team: Copilot-gestützter Technik-Check
- Gerät: Entwicklungsrechner
- Windows-Version: nicht erfasst
- Office-Version (z. B. 2019/2021/M365 + Build): 16.0 (per Script geprüft)
- Ausführung (normal / Administrator): normal

#### Registry-Check

- Script: `tools/check-office-registry.ps1 -OfficeVersions 16.0`
- Ergebnis (Treffer): `0/9`
- Auffällige Werte: alle geprüften Sollwerte nicht compliant (vor manuellem Office-Lauf)

#### Word-Optionen (GUI)

- „Jede Tabellenzeile mit einem Großbuchstaben beginnen" deaktiviert:
  - [ ] Ja
  - [ ] Nein
  - [x] Option nicht vorhanden
- „Bilder einfügen" = „Mit Text in Zeile":
  - [ ] Ja
  - [ ] Nein
  - [x] Option nicht vorhanden

#### Praxistest

- Tabelle: noch nicht durchgeführt
- Bild einfügen: noch nicht durchgeführt
- Abweichungen vom Soll: offen

#### Bewertung

- Ergebnis:
  - [ ] OK
  - [x] eingeschränkt
  - [ ] nicht OK
- Handlungsempfehlung: GUI-Validierung auf echter Office-Installation nach Lauf „Nur Office konfigurieren" wiederholen.

### Musterlauf 2 (Vorlage Teamtest)

- Datum/Uhrzeit:
- Tester:in / Team:
- Gerät:
- Windows-Version:
- Office-Version (z. B. 2019/2021/M365 + Build):
- Ausführung (normal / Administrator):

#### Registry-Check

- Script: `tools/check-office-registry.ps1`
- Ergebnis (Treffer):
- Auffällige Werte:

#### Word-Optionen (GUI)

- „Jede Tabellenzeile mit einem Großbuchstaben beginnen" deaktiviert:
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden
- „Bilder einfügen" = „Mit Text in Zeile":
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden

#### Praxistest

- Tabelle: Verhalten beim Eingeben neuer Zeilen:
- Bild einfügen: Verhalten/Umbruch:
- Abweichungen vom Soll:

#### Bewertung

- Ergebnis:
  - [ ] OK
  - [ ] eingeschränkt
  - [ ] nicht OK
- Handlungsempfehlung:

### Musterlauf 3 (Vorlage Gegentest)

- Datum/Uhrzeit:
- Tester:in / Team:
- Gerät:
- Windows-Version:
- Office-Version (z. B. 2019/2021/M365 + Build):
- Ausführung (normal / Administrator):

#### Registry-Check

- Script: `tools/check-office-registry.ps1`
- Ergebnis (Treffer):
- Auffällige Werte:

#### Word-Optionen (GUI)

- „Jede Tabellenzeile mit einem Großbuchstaben beginnen" deaktiviert:
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden
- „Bilder einfügen" = „Mit Text in Zeile":
  - [ ] Ja
  - [ ] Nein
  - [ ] Option nicht vorhanden

#### Praxistest

- Tabelle: Verhalten beim Eingeben neuer Zeilen:
- Bild einfügen: Verhalten/Umbruch:
- Abweichungen vom Soll:

#### Bewertung

- Ergebnis:
  - [ ] OK
  - [ ] eingeschränkt
  - [ ] nicht OK
- Handlungsempfehlung:
