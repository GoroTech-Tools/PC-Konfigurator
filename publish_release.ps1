param(
    [string]$SourceDir = (Join-Path $PSScriptRoot 'release'),
    [string]$TargetDir = $(
        if ($env:OneDrive) {
            Join-Path $env:OneDrive 'Releases\PC-Konfigurator-Portable'
        } else {
            Join-Path $PSScriptRoot 'release-published'
        }
    ),
    [switch]$LatestOnly,
    [switch]$WhatIf
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if (-not (Test-Path $SourceDir)) {
    Write-Host "Quellordner nicht gefunden: $SourceDir" -ForegroundColor Red
    exit 1
}

$zipFiles = Get-ChildItem -Path $SourceDir -Filter '*.zip' -File | Sort-Object LastWriteTime -Descending
if (-not $zipFiles) {
    Write-Host "Keine ZIP-Dateien in $SourceDir gefunden." -ForegroundColor Yellow
    exit 1
}

if ($LatestOnly) {
    $zipFiles = @($zipFiles | Select-Object -First 1)
}

if (-not (Test-Path $TargetDir)) {
    if ($WhatIf) {
        Write-Host "[WhatIf] Würde Zielordner erstellen: $TargetDir" -ForegroundColor DarkGray
    } else {
        New-Item -Path $TargetDir -ItemType Directory -Force | Out-Null
        Write-Host "Zielordner erstellt: $TargetDir" -ForegroundColor DarkGray
    }
}

$copied = 0
foreach ($zip in $zipFiles) {
    $targetFile = Join-Path $TargetDir $zip.Name

    if ($WhatIf) {
        Write-Host "[WhatIf] Würde kopieren: $($zip.FullName) -> $targetFile" -ForegroundColor Cyan
        continue
    }

    Copy-Item -Path $zip.FullName -Destination $targetFile -Force
    $copied++
    Write-Host "OK Kopiert: $($zip.Name)" -ForegroundColor Green
}

if (-not $WhatIf) {
    Write-Host "Fertig. $copied ZIP-Datei(en) nach '$TargetDir' veröffentlicht." -ForegroundColor Green
}
