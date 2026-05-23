# Dokumentation – PC-Konfigurator-Portable

Diese Dokumentation ist zielgruppenspezifisch aufgebaut:

- **[Dokumentation_Anwender.md](./Dokumentation_Anwender.md)**  
  Bedienung, Voraussetzungen, Schritt-für-Schritt-Anleitung, Fehlerbehebung
- **[Dokumentation_Technik.md](./Dokumentation_Technik.md)**  
  Architektur, Build/Release, CI/CD, Wartung und technische Details
- **[Dokumentation_Checkliste.md](./Dokumentation_Checkliste.md)**  
  Qualitäts- und Freigabecheck für die Projektdokumentation
- **[Migrationsplan_GUI_Angleichung_AP1.md](./Migrationsplan_GUI_Angleichung_AP1.md)**  
  Konkreter Schritt-für-Schritt-Plan zur GUI-Angleichung an den AP1-Konfigurator-Portable

## Empfohlener Einstieg

1. Für Benutzer:innen: `Dokumentation_Anwender.md`
2. Für Entwickler:innen/Admins: zusätzlich `Dokumentation_Technik.md`

## Projektkontext

`PC-Konfigurator-Portable` ist eine portable Windows-Anwendung zur automatisierten
Konfiguration von Office, Windows-Einstellungen, Vorlagen und Schriftarten.

- GUI/Anwendungslogik: `src/main.py`
- Sichere Template-Verarbeitung: `src/safe_template_processor.py`
- Build/Release: `build.ps1`, `setup.ps1`, `publish_release.ps1`
