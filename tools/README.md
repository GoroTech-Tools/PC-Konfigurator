# Tools

Dieses Verzeichnis enthält unterstützende Projekt-Routinen.

## Enthaltene Skripte

- `lint-markdown.ps1`  
  Führt Markdownlint für alle Markdown-Dateien im Repository aus.
- `check-office-registry.ps1`  
  Prüft zentrale Office-Registry-Sollwerte (Word/Excel) inkl. offener Validierungspunkte.

## Verwendung

### Markdown linten

```powershell
.\tools\lint-markdown.ps1
```

### Markdown linten und Auto-Fixes anwenden

```powershell
.\tools\lint-markdown.ps1 -Fix
```

### Office-Registry-Sollwerte prüfen

```powershell
.\tools\check-office-registry.ps1
```

### Office-Registry-Sollwerte als JSON ausgeben

```powershell
.\tools\check-office-registry.ps1 -AsJson
```

## Hinweise

- Die Konfiguration liegt in `.markdownlint.json`.
- Ausgeschlossene Pfade liegen in `.markdownlintignore`.
- Der Build-Prozess (`build.ps1`) führt die Markdown-Prüfung standardmäßig zweistufig aus (erst `-Fix`, dann Gate-Lauf ohne Fix).
- Mit `build.ps1 -SkipMarkdownLint` kann die Prüfung bei Bedarf übersprungen werden.
