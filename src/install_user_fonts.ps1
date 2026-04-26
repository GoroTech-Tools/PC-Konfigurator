# Installiere alle Fonts aus einem Quellverzeichnis ins benutzerspezifische Windows-Font-Verzeichnis
# (z.B. %LOCALAPPDATA%\Microsoft\Windows\Fonts)

param(
    [Parameter(Mandatory=$true)]
    [string]$SourceDirectory
)

$targetFolder = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'

if (-Not (Test-Path -Path $SourceDirectory)) {
    Write-Host "Quellverzeichnis '$SourceDirectory' existiert nicht. Bitte überprüfen Sie den Pfad." -ForegroundColor Red
    exit 1
}

if (-Not (Test-Path -Path $targetFolder)) {
    New-Item -Path $targetFolder -ItemType Directory -Force | Out-Null
}

$fontFiles = Get-ChildItem -Path $SourceDirectory -Recurse -Include *.ttf,*.otf -File

foreach ($fontFile in $fontFiles) {
    $targetFontPath = Join-Path $targetFolder $fontFile.Name
    if (Test-Path -Path $targetFontPath) {
        Write-Host "Die Schriftart '$($fontFile.Name)' ist bereits vorhanden und wird übersprungen." -ForegroundColor Yellow
        continue
    }
    try {
        Copy-Item -Path $fontFile.FullName -Destination $targetFontPath -Force
        Write-Host "Schriftart installiert: $($fontFile.Name)" -ForegroundColor Green
    } catch {
        Write-Host "Fehler beim Installieren von $($fontFile.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host "Alle Schriftarten wurden verarbeitet." -ForegroundColor Green
