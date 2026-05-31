# Tools

Dieses Verzeichnis enthält unterstützende Projekt-Routinen.

## Enthaltene Skripte

- `lint-markdown.ps1`  
  Führt Markdownlint für alle Markdown-Dateien im Repository aus.

## Verwendung

### Markdown linten

```powershell
.\tools\lint-markdown.ps1
```

### Markdown linten und Auto-Fixes anwenden

```powershell
.\tools\lint-markdown.ps1 -Fix
```

## Hinweise

- Die Konfiguration liegt in `.markdownlint.json`.
- Ausgeschlossene Pfade liegen in `.markdownlintignore`.
- Der Build-Prozess (`build.ps1`) führt die Markdown-Prüfung standardmäßig aus.
- Mit `build.ps1 -SkipMarkdownLint` kann die Prüfung bei Bedarf übersprungen werden.
