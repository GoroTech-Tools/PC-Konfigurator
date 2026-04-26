
# Check if Normal.dotm in user profile is current and if Word is closed

$normalPath = Join-Path $env:APPDATA 'Microsoft\Templates\Normal.dotm'

Write-Host "Checking Normal.dotm in user profile..." -ForegroundColor Cyan
if (Test-Path $normalPath) {
    $info = Get-Item $normalPath
    Write-Host "Found: $normalPath" -ForegroundColor Green
    Write-Host ("Last change: " + $info.LastWriteTime)
    Write-Host ("Size: " + [Math]::Round($info.Length / 1KB, 2) + " KB")
} else {
    Write-Host "Normal.dotm not found in user profile!" -ForegroundColor Red
}

# Check if Word is running
$wordProc = Get-Process WINWORD -ErrorAction SilentlyContinue
if ($wordProc) {
    Write-Host "Warning: Word is currently open! Changes may not be applied." -ForegroundColor Yellow
} else {
    Write-Host "Word is closed." -ForegroundColor Green
}

# Show registry path for default templates
$regPath = 'HKCU:\\Software\\Microsoft\\Office\\16.0\\Word\\Options'
if (Test-Path $regPath) {
    $docPath = Get-ItemProperty -Path $regPath -Name 'DOC-PATH' -ErrorAction SilentlyContinue
    if ($docPath -and $docPath.'DOC-PATH') {
        Write-Host ("Registry DOC-PATH: " + $docPath.'DOC-PATH') -ForegroundColor White
    } else {
        Write-Host "Registry DOC-PATH not set." -ForegroundColor Yellow
    }
} else {
    Write-Host "Registry path for Word options not found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Please check if Normal.dotm in user profile is current and Word was closed!" -ForegroundColor Cyan