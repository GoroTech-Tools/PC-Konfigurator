param(
    [switch]$Fix,
    [switch]$Quiet
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $repoRoot

$targetPattern = '**/*.md'
$configPath = Join-Path $repoRoot '.markdownlint.json'
$ignorePath = Join-Path $repoRoot '.markdownlintignore'

if (-not (Test-Path $configPath)) {
    Write-Host "Konfiguration fehlt: $configPath" -ForegroundColor Red
    exit 1
}

if (-not $Quiet) {
    Write-Host "Markdownlint-Prüfung startet..." -ForegroundColor Cyan
}

$commonArgs = @('--config', $configPath)

if (Test-Path $ignorePath) {
    $ignoreEntries = Get-Content $ignorePath |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ -and -not $_.StartsWith('#') }

    foreach ($entry in $ignoreEntries) {
        $commonArgs += @('--ignore', $entry)
    }
}

$commonArgs += $targetPattern
if ($Fix) {
    $commonArgs = @('--fix') + $commonArgs
}

$runner = $null

if (Get-Command markdownlint -ErrorAction SilentlyContinue) {
    $runner = 'markdownlint'
    & markdownlint @commonArgs
}
elseif (Get-Command npx -ErrorAction SilentlyContinue) {
    $runner = 'npx markdownlint-cli'
    & npx --yes markdownlint-cli @commonArgs
}
else {
    Write-Host "Weder 'markdownlint' noch 'npx' gefunden. Bitte Node.js/npm installieren oder markdownlint-cli global bereitstellen." -ForegroundColor Red
    exit 1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Markdownlint-Fehler gefunden (Runner: $runner)." -ForegroundColor Red
    exit 1
}

if (-not $Quiet) {
    Write-Host "Markdownlint-Prüfung erfolgreich (Runner: $runner)." -ForegroundColor Green
}

exit 0