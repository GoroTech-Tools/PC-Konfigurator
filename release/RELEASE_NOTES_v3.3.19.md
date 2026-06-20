# Release Notes v3.3.19

Datum: 2026-06-20

## Highlights

- Explorer-Neustart wurde gegen verzögerte Shell-Reinitialisierung gehärtet
	(Taskleisten-Sichtbarkeitsprüfung + Recovery-Fallback).
- Outlook-Template-Pfadauflösung für `NormalEmail.dotm` in Direkt-/Script-Läufen
	robust gemacht (keine falsche "Vorlage nicht gefunden"-Warnung mehr).
- Doku umfassend aktualisiert (Anwender/Technik/Checklisten) inkl. transparenter
	Hinweise zur modernen Outlook-Compose-Einschränkung.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.19/
- EXE: dist/PC-Konfigurator-v3.3.19/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.19.zip

## Enthaltene Commits (aktuelle Historie)

- `c42c2f7` Release v3.3.17: Office-Konfiguration beschleunigen
- `95a8104` Release v3.3.16: Outlook MailSettings ohne COM
- `1c8a04d` Release v3.3.15: COM-Precheck, Outlook-Template-Feedback und Build-Robustheit
- `86e7636` Release v3.3.10: startmenu guard hardening and version bump
- `6883f9b` Release v3.3.9: Bugfixes Startmenu-Guard und Explorer-Kill beim App-Start

## Technische Build-Informationen

- Build-Datum: 2026-06-20 14:00:00
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
