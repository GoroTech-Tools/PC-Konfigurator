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

$globalNpmBin = Join-Path $env:APPDATA 'npm'
$programFilesNodeBin = Join-Path $env:ProgramFiles 'nodejs'
$originalPath = $env:PATH
foreach ($extraPath in @($programFilesNodeBin, $globalNpmBin)) {
    if ($extraPath -and (Test-Path $extraPath) -and ($env:PATH -notlike "*$extraPath*")) {
        $env:PATH = "$extraPath;$env:PATH"
    }
}
$candidateMarkdownlint = @(
    (Get-Command markdownlint -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
    (Join-Path $globalNpmBin 'markdownlint.cmd'),
    (Join-Path $programFilesNodeBin 'markdownlint.cmd')
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

$candidateNpx = @(
    (Get-Command npx -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -First 1),
    (Join-Path $globalNpmBin 'npx.cmd'),
    (Join-Path $programFilesNodeBin 'npx.cmd')
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

if ($candidateMarkdownlint) {
    $runner = 'markdownlint'
    & $candidateMarkdownlint @commonArgs
}
elseif ($candidateNpx) {
    $runner = 'npx markdownlint-cli'
    & $candidateNpx --yes markdownlint-cli @commonArgs
}
else {
    Write-Host "Weder 'markdownlint' noch 'npx' gefunden. Bitte Node.js/npm installieren oder markdownlint-cli global bereitstellen." -ForegroundColor Red
    exit 1
}

$env:PATH = $originalPath

if ($LASTEXITCODE -ne 0) {
    Write-Host "Markdownlint-Fehler gefunden (Runner: $runner)." -ForegroundColor Red
    exit 1
}

if (-not $Quiet) {
    Write-Host "Markdownlint-Prüfung erfolgreich (Runner: $runner)." -ForegroundColor Green
}

exit 0