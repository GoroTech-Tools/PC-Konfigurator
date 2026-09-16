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
- **[Migrationsplan_GUI_Angleichung_AP1.md](./_archive/Migrationsplan_GUI_Angleichung_AP1.md)** *(archiviert)*  
  Abgeschlossener Migrationsplan zur GUI-Angleichung an den AP1-Konfigurator (Stand 31.05.2026)

## Empfohlener Einstieg

1. Für Benutzer:innen: `DOKUMENTATION_ANWENDER.md`
2. Für Entwickler:innen/Admins: zusätzlich `DOKUMENTATION_TECHNIK.md`

## Aktueller Betriebsstatus (Stand 2026-09-16)

- Explorer-Neustart in der GUI wurde für verzögerte Shell-Reinitialisierung gehärtet (Taskleisten-Sichtbarkeitsprüfung + Recovery-Fallback).
- Bekannte Einschränkung dokumentiert: Moderne Outlook-Compose-Oberfläche kann lokale Standardfont-Vorgaben trotz Registry-/Template-Konfiguration teilweise übersteuern.
- Office-Konfiguration nutzt standardmäßig den robusten Registry/XML-Pfad; COM-Synchronisierung ist nur noch optional.
- Edge-Profile und Outlook-Signaturen werden getrennt gesichert und im Laufstatus angezeigt.
- Der Dokumente-Zielpfad berücksichtigt OneDrive-Umleitungen und verwendet ohne Umleitung den deutschen Ordner `Dokumente`.
- Der vollständige Lauf verlangt vor dem Start eine Bestätigung, dass Edge und die Office-Anwendungen beendet wurden.

## Projektkontext

`PC-Konfigurator` ist eine portable Windows-Anwendung zur automatisierten
Konfiguration von Office, Windows-Einstellungen, Vorlagen und Schriftarten.

- GUI/Anwendungslogik: `src/main.py`
- Sichere Template-Verarbeitung: `src/safe_template_processor.py`
- Build/Release: `build.ps1`, `setup.ps1`, `src/publish_release.ps1`
