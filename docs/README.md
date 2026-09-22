# Dokumentation – PC-Konfigurator

Diese Dokumentation ist zielgruppenspezifisch aufgebaut:

- **[DOKUMENTATION_ANWENDER.md](./DOKUMENTATION_ANWENDER.md)**  
  Bedienung, Voraussetzungen, Schritt-für-Schritt-Anleitung, Fehlerbehebung
- **[DOKUMENTATION_TECHNIK.md](./DOKUMENTATION_TECHNIK.md)**  
  Architektur, Build/Release, CI/CD, Wartung und technische Details
- **[DOKUMENTATION_DIAGRAMME.md](./DOKUMENTATION_DIAGRAMME.md)**  
  Übersicht der Mermaid-Quellen und erzeugten SVG-Diagramme
- **[Migrationsplan_GUI_Angleichung_AP1.md](./_archive/Migrationsplan_GUI_Angleichung_AP1.md)** *(archiviert)*  
  Abgeschlossener Migrationsplan zur GUI-Angleichung an den AP1-Konfigurator (Stand 31.05.2026)

## Empfohlener Einstieg

1. Für Benutzer:innen: `DOKUMENTATION_ANWENDER.md`
2. Für Entwickler:innen/Admins: zusätzlich `DOKUMENTATION_TECHNIK.md`

## Aktueller Betriebsstatus (Stand 2026-09-17)

- Datei-Vorlagen-Bibliothek wird bei jedem Lauf automatisch mit dem Zielordner
  abgeglichen (Update-Modus, keine Überschreibung eigener Änderungen).
- Neue optionale Funktion „Datei-Vorlagen zurücksetzen“ im Konfiguration-Tab
  (standardmäßig deaktiviert, mit Bestätigungsdialog).
- Dateisystem-Operationen auf OneDrive-Zielordnern (Edge-/Signatur-Backup,
  Datei-Vorlagen-Synchronisation) sind jetzt robust gegen kurzzeitige
  OneDrive-Sync-Races (automatische Wiederholung mit steigender Wartezeit).
- Fehlermeldungen bei blockiertem Dateizugriff enthalten jetzt einen Hinweis
  auf mögliche Ursachen (z. B. Kontrollierter Ordnerzugriff von Windows-Sicherheit).
- Explorer-Neustart in der GUI wurde für verzögerte Shell-Reinitialisierung gehärtet (Taskleisten-Sichtbarkeitsprüfung + Recovery-Fallback).
- Bekannte Einschränkung dokumentiert: Moderne Outlook-Compose-Oberfläche kann lokale Standardfont-Vorgaben trotz Registry-/Template-Konfiguration teilweise übersteuern.
- Outlook classic/Outlook 2024 LTSC erhält Schriftart und -größe zusätzlich über `Common\MailSettings`, `Outlook\Options` und einen Theme-synchronisierten `NormalEmail.dotm`-Patch.
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
