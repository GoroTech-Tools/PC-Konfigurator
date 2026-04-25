# PowerShell-Skript: Clean-Build.ps1
Write-Host "Bereinige Build- und Dist-Ordner ..."

# Build-Ordner löschen
if (Test-Path ".\\build") {
    Remove-Item ".\\build" -Recurse -Force
    Write-Host "Build-Ordner gelöscht."
}

# Alle _internal- und _py_internal-Ordner in dist löschen
Get-ChildItem ".\\dist" -Directory | ForEach-Object {
    $internalPath = Join-Path $_.FullName "_internal"
    if (Test-Path $internalPath) {
        Remove-Item $internalPath -Recurse -Force
        Write-Host "$internalPath gelöscht."
    }
    $pyInternalPath = Join-Path $_.FullName "_py_internal"
    if (Test-Path $pyInternalPath) {
        Remove-Item $pyInternalPath -Recurse -Force
        Write-Host "$pyInternalPath gelöscht."
    }
}

Write-Host "Bereinigung abgeschlossen. Jetzt kann der Build neu gestartet werden."