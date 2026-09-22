# Release Notes v3.3.95

Datum: 2026-09-22

## Download

- [Release-Seite v3.3.95](https://github.com/GoroTech-Tools/PC-Konfigurator/releases/tag/v3.3.95)
- [ZIP direkt herunterladen](https://github.com/GoroTech-Tools/PC-Konfigurator/releases/download/v3.3.95/PC-Konfigurator-v3.3.95.zip)

## Highlights

- Outlook classic einschließlich Outlook 2024 LTSC erhält Schriftart und -größe über `Common\MailSettings`, `Outlook\Options` und die synchronisierte `NormalEmail.dotm`.
- Der Outlook-Template-Patch setzt neben der direkten Formatvorlage auch die Theme-Schrift und behebt die lxml-Elementerzeugung im sicheren XML-Pfad.
- Die Registry-Prüfung erwartet für den aktuellen Outlook-Standard 12 pt.
- Das Build wurde als Onefile-EXE erzeugt und für die Verteilung aufbereitet.
- Bitte Highlights bei Bedarf projektspezifisch ergänzen.

## Qualitätsstatus

- Release-Build erfolgreich erzeugt.
- ZIP-Artefakt erstellt und im Release-Ordner abgelegt.
- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.

## Artefakte

- Build-Verzeichnis: dist/PC-Konfigurator-v3.3.95/
- EXE: dist/PC-Konfigurator-v3.3.95/PC-Konfigurator.exe
- Release-ZIP: release/PC-Konfigurator-v3.3.95.zip

## Enthaltene Commits (aktuelle Historie)

- `27ed553` chore: archive previous release notes
- `cd58669` release: v3.3.94 with complete data assets
- `12076e1` data: include all fonts in releases
- `b341b61` chore: archive previous release notes
- `7b0256f` release: v3.3.93 with complete file templates

## Technische Build-Informationen

- Build-Datum: 2026-09-22 18:20:51
- Build-Modus: --onefile --windowed
- EXE-Name: PC-Konfigurator.exe
