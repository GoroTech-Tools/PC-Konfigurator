# Anwenderprüfung – Auswertungsvorlage (EXE)

Stand: 2026-05-31  
Projekt: `PC-Konfigurator`

## Zweck

Diese Vorlage bündelt die Rückmeldungen aus:

- `docs/ANWENDERPRUEFUNG_CHECKLISTE.md`
- `docs/ANWENDERPRUEFUNG_KURZCHECKLISTE.md`

Ziel ist eine belastbare Entscheidung, ob die EXE-Variante als primärer Weg
freigegeben werden kann.

## 1) Testkampagne – Übersicht

- Auswertungszeitraum: ____________________
- Verantwortlich: ____________________
- Gesamtzahl Rückmeldungen: ____________________
- Davon Kollegium: ____________________
- Davon Teilnehmende: ____________________

## 2) Umgebungsabdeckung

### Windows

- [ ] Windows 10 ausreichend abgedeckt
- [ ] Windows 11 ausreichend abgedeckt

Details/Anmerkungen:

- ______________________________________________________________

### Office

- [ ] Office 2019 abgedeckt
- [ ] Office 2021 abgedeckt
- [ ] Microsoft 365 abgedeckt

Details/Anmerkungen:

- ______________________________________________________________

### OneDrive-Szenarien

- [ ] Lokal verfügbare Dateien getestet
- [ ] Teilweise offline/Platzhalter-Szenarien getestet

Details/Anmerkungen:

- ______________________________________________________________

## 3) Ergebnis-Matrix (aggregiert)

| Testbereich                           | OK | Teilweise | Fehler | Hinweise |
|---------------------------------------|---:|----------:|-------:|----------|
| EXE-Start / Stabilität                |    |           |        |          |
| Bedienbarkeit / Verständlichkeit      |    |           |        |          |
| Vollständige Konfiguration            |    |           |        |          |
| Nur Office konfigurieren (Erweitert)  |    |           |        |          |
| Template-/Font-Handling               |    |           |        |          |
| Windows-/Registry-Anpassungen         |    |           |        |          |
| Explorer-Dateiinhaltssuche aktiviert  |    |           |        |          |
| Logging / Nachvollziehbarkeit         |    |           |        |          |

## 4) Kritische Befunde (Blocker)

| ID | Kurzbeschreibung | Reproduzierbar | Betroffene Umgebung | Priorität | Folge-Issue |
|----|------------------|----------------|---------------------|-----------|-------------|
| B1 |                  | ja / nein      |                     | hoch      |             |
| B2 |                  | ja / nein      |                     | hoch      |             |

## 5) Wichtige Nicht-Blocker

| ID | Thema | Auswirkung | Priorität | Folge-Issue |
|----|-------|------------|-----------|-------------|
| N1 |       |            | mittel    |             |
| N2 |       |            | niedrig   |             |

## 6) Vergleich EXE vs. PowerShell (Kurzfazit)

- Stabilität EXE im Vergleich: ____________________
- Bedienbarkeit EXE im Vergleich: ____________________
- Auffällige Unterschiede: ____________________

## 7) Entscheidungsvorlage

### Vorschlag

- [ ] EXE als primärer Weg freigeben
- [ ] EXE eingeschränkt freigeben (mit bekannten Einschränkungen)
- [ ] EXE vorerst nicht als primärer Weg freigeben

### Begründung

- ______________________________________________________________
- ______________________________________________________________

### Maßnahmen bis zur nächsten Bewertungsrunde

1. _____________________________________________________________
2. _____________________________________________________________
3. _____________________________________________________________

## 8) Freigabe

- Datum: ____________________
- Verantwortliche Person(en): ____________________
- Referenzen (Issue/PR/Release): ____________________
