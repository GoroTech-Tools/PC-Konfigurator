# setup.ps1 — Erstellt .venv und installiert Abhängigkeiten aus requirements.txt
# Aufruf: .\setup.ps1
# Optional: .\setup.ps1 -Force            (löscht bestehende .venv und erstellt neu)
#           .\setup.ps1 -VenvName .venv-bfw (erstellt alternative venv mit eigenem Namen)
param(
    [switch]$Force,
    [string]$VenvName = ".venv"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Leaf

if ($Force -and (Test-Path ".\$VenvName")) {
    Write-Host "[$repo] Entferne bestehende $VenvName ..."
    Remove-Item ".\$VenvName" -Recurse -Force
}

if (-not (Test-Path ".\$VenvName")) {
    Write-Host "[$repo] Erstelle $VenvName ..."
    py -m venv $VenvName
} else {
    Write-Host "[$repo] $VenvName bereits vorhanden."
}

Write-Host "[$repo] Aktualisiere pip ..."
& ".\$VenvName\Scripts\python.exe" -m pip install --upgrade pip -q

if (Test-Path ".\requirements.txt") {
    Write-Host "[$repo] Installiere Pakete aus requirements.txt ..."
    & ".\$VenvName\Scripts\python.exe" -m pip install -r requirements.txt -q
    Write-Host "[$repo] Fertig. Aktivieren mit: .\$VenvName\Scripts\Activate.ps1"
} else {
    Write-Host "[$repo] Keine requirements.txt gefunden - $VenvName angelegt, aber leer."
}
