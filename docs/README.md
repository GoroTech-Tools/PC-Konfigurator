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
- **[GUI_REGRESSION_CHECKLISTE.md](./GUI_REGRESSION_CHECKLISTE.md)**  
  Regression-Checkliste für GUI-Änderungen im Rahmen der AP1-Angleichung
- **[Migrationsplan_GUI_Angleichung_AP1.md](./Migrationsplan_GUI_Angleichung_AP1.md)**  
  Konkreter Schritt-für-Schritt-Plan zur GUI-Angleichung an den AP1-Konfigurator

## Empfohlener Einstieg

1. Für Benutzer:innen: `DOKUMENTATION_ANWENDER.md`
2. Für Entwickler:innen/Admins: zusätzlich `DOKUMENTATION_TECHNIK.md`

## Projektkontext

`PC-Konfigurator` ist eine portable Windows-Anwendung zur automatisierten
Konfiguration von Office, Windows-Einstellungen, Vorlagen und Schriftarten.

- GUI/Anwendungslogik: `src/main.py`
- Sichere Template-Verarbeitung: `src/safe_template_processor.py`
- Build/Release: `build.ps1`, `setup.ps1`, `src/publish_release.ps1`
