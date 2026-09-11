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
$newlyAddedFonts = @()
$existingFonts = @()
$failedFonts = @()

foreach ($fontFile in $fontFiles) {
    $targetFontPath = Join-Path $targetFolder $fontFile.Name
    if (Test-Path -Path $targetFontPath) {
        $existingFonts += $fontFile.Name
        continue
    }
    try {
        Copy-Item -Path $fontFile.FullName -Destination $targetFontPath -Force
        $newlyAddedFonts += $fontFile.Name
    } catch {
        $failedFonts += $fontFile.Name
        Write-Host "Fehler beim Installieren von $($fontFile.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}
$totalFonts = $fontFiles.Count
Write-Host "$($newlyAddedFonts.Count) von $totalFonts Schrift(en) neu hinzugefügt ($($existingFonts.Count) bereits vorhanden)." -ForegroundColor Green
if ($failedFonts.Count -gt 0) {
    Write-Host "$($failedFonts.Count) Schrift(en) konnten nicht installiert werden." -ForegroundColor Red
}
