# DOKUMENTATION_CHECKLISTE

Diese Checkliste dient als Qualitäts- und Freigabegrundlage für die Projektdokumentation.

## Metadaten

- Projektname: `PC-Konfigurator`
- Version/Stand: `3.3.1`
- Datum der Prüfung: `31.05.2026`
- Geprüft von: `____________________`

## A) Struktur und Ablage

- [ ] Alle Doku-Dateien liegen in `docs/`
- [ ] `docs/README.md` als zentraler Einstieg vorhanden
- [ ] Anwender- und Technikdoku getrennt vorhanden
- [ ] Veraltete Doku außerhalb `docs/` entfernt oder als Verweisdatei markiert

## B) Anwenderdokumentation

- [ ] Zweck und Zielgruppe klar beschrieben
- [ ] Voraussetzungen vollständig
- [ ] Bedienablauf Schritt für Schritt dokumentiert
- [ ] Troubleshooting/FAQ vorhanden
- [ ] Sicherheits-/Nutzungshinweise enthalten

## C) Technikdokumentation

- [ ] Architektur und Hauptkomponenten beschrieben
- [ ] Laufzeitfluss nachvollziehbar
- [ ] Build-/Release-Prozess dokumentiert
- [ ] CI/CD und Artefaktfluss beschrieben
- [ ] Risiken und Testempfehlungen enthalten

## D) Konsistenz und Verlinkung

- [ ] Root-README verlinkt auf `docs/`
- [ ] Interne Links in Doku funktionieren
- [ ] Versionsangaben sind konsistent (`src/build_info.py`, README, Doku)

## E) Freigabe

- [ ] Technischer Review abgeschlossen
- [ ] Fachlicher Review abgeschlossen
- [ ] Release-Doku freigegeben

Freigegeben am: `____________________`  
Freigegeben durch: `____________________`
