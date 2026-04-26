# Post-Build-Skript für PC-Konfigurator-Portable
# Setzt versteckte Attribute für technische Ordner

param(
    [Parameter(Mandatory=$true)]
    [string]$BuildPath
)

Write-Host "Setze versteckte Attribute für technische Ordner in: $BuildPath"

# Logs-Ordner erstellen falls nicht vorhanden
$logsPath = Join-Path $BuildPath "logs"
if (-not (Test-Path $logsPath)) {
    New-Item -Path $logsPath -ItemType Directory -Force | Out-Null
    Write-Host "✓ logs-Ordner erstellt"
}

# Versteckte Attribute setzen
$internalPath = Join-Path $BuildPath "_internal"
if (Test-Path $internalPath) {
    attrib +H "$internalPath"
    Write-Host "✓ _internal-Ordner als versteckt markiert"
}

if (Test-Path $logsPath) {
    attrib +H "$logsPath"
    Write-Host "✓ logs-Ordner als versteckt markiert"
}

Write-Host "Post-Build-Konfiguration abgeschlossen!"