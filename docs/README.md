# Dokumentation – PC-Konfigurator

Diese Dokumentation ist zielgruppenspezifisch aufgebaut:

- **[DOKUMENTATION_ANWENDER.md](./DOKUMENTATION_ANWENDER.md)**  
  Bedienung, Voraussetzungen, Schritt-für-Schritt-Anleitung, Fehlerbehebung
- **[DOKUMENTATION_TECHNIK.md](./DOKUMENTATION_TECHNIK.md)**  
  Architektur, Build/Release, CI/CD, Wartung und technische Details
- **[DOKUMENTATION_CHECKLISTE.md](./DOKUMENTATION_CHECKLISTE.md)**  
  Qualitäts- und Freigabecheck für die Projektdokumentation
- **[DOKUMENTATION_DIAGRAMME.md](./DOKUMENTATION_DIAGRAMME.md)**  
  Übersicht der Mermaid-Quellen und erzeugten SVG-Diagramme
- **[ANWENDERPRUEFUNG_CHECKLISTE.md](./ANWENDERPRUEFUNG_CHECKLISTE.md)**  
  Vollständige Praxis-Checkliste für EXE-Tests durch Kollegium und Teilnehmende
- **[ANWENDERPRUEFUNG_KURZCHECKLISTE.md](./ANWENDERPRUEFUNG_KURZCHECKLISTE.md)**  
  Kompakter 5–10-Minuten-Schnellcheck für die EXE-Variante
- **[ANWENDERPRUEFUNG_AUSWERTUNG.md](./ANWENDERPRUEFUNG_AUSWERTUNG.md)**  
  Einheitliche Auswertungsvorlage für die Rückmeldungen aus den EXE-Tests
- **[OFFENE_OFFICE_PUNKTE.md](./OFFENE_OFFICE_PUNKTE.md)**  
  Zentrale Validierungssammlung für aktuell offene Office-Detailpunkte
- **[GUI_REGRESSION_CHECKLISTE.md](./GUI_REGRESSION_CHECKLISTE.md)**  
  Regression-Checkliste für GUI-Änderungen im Rahmen der AP1-Angleichung
- **[Migrationsplan_GUI_Angleichung_AP1.md](./_archive/Migrationsplan_GUI_Angleichung_AP1.md)** *(archiviert)*  
  Abgeschlossener Migrationsplan zur GUI-Angleichung an den AP1-Konfigurator (Stand 31.05.2026)

## Empfohlener Einstieg

1. Für Benutzer:innen: `DOKUMENTATION_ANWENDER.md`
2. Für Entwickler:innen/Admins: zusätzlich `DOKUMENTATION_TECHNIK.md`

## Office-Validierung (offene Detailpunkte)

Für laufende Prüfungen der offenen Office-Detailpunkte bitte kombiniert nutzen:

- `tools/check-office-registry.ps1` für den Soll/Ist-Registry-Check
- `docs/OFFENE_OFFICE_PUNKTE.md` für die strukturierte Testdokumentation

Aktueller Status: Die beiden Word-Optionen („Jede Tabellenzeile mit einem Großbuchstaben beginnen" und „Bilder einfügen" = „Mit Text in Zeile") sind inzwischen als Standardkonfiguration im `PC-Konfigurator` hinterlegt; offen bleibt nur noch der praktische Nachweis auf einem Testclient.

## Aktueller Betriebsstatus (Stand 2026-06-20)

- Explorer-Neustart in der GUI wurde für verzögerte Shell-Reinitialisierung gehärtet (Taskleisten-Sichtbarkeitsprüfung + Recovery-Fallback).
- Bekannte Einschränkung dokumentiert: Moderne Outlook-Compose-Oberfläche kann lokale Standardfont-Vorgaben trotz Registry-/Template-Konfiguration teilweise übersteuern.
- Office-Konfiguration nutzt standardmäßig den robusten Registry/XML-Pfad; COM-Synchronisierung ist nur noch optional.

## Projektkontext

`PC-Konfigurator` ist eine portable Windows-Anwendung zur automatisierten
Konfiguration von Office, Windows-Einstellungen, Vorlagen und Schriftarten.

- GUI/Anwendungslogik: `src/main.py`
- Sichere Template-Verarbeitung: `src/safe_template_processor.py`
- Build/Release: `build.ps1`, `setup.ps1`, `src/publish_release.ps1`
