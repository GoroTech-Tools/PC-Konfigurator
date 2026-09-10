# Build-Skript für PC-Konfigurator
# Erstellt automatisch das Build und führt Post-Build-Aktionen aus

[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingWriteHost', '', Justification = 'Dieses Build-Skript schreibt bewusst Statusmeldungen auf die Konsole.')]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidOverwritingBuiltInCmdlets', '', Justification = 'Lokaler Wrapper dient der konditionalen Konsolenausgabe im Build.')]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseShouldProcessForStateChangingFunctions', '', Justification = 'Die Funktionen sind interne Build-Hilfsfunktionen ohne Benutzerbestätigung.')]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingEmptyCatchBlock', '', Justification = 'Fehler werden an dieser Stelle bewusst still ignoriert oder an anderer Stelle protokolliert.')]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '', Justification = 'Einige Zwischenwerte sind nur für Lesbarkeit bzw. zukünftige Erweiterungen vorgesehen.')]

param(
    [switch]$NoVersionBump,
    [switch]$SkipZip,
    [switch]$SkipMarkdownLint,
    [switch]$Help,
    [switch]$Quiet,
    [ValidateSet('.venv')]
    [string]$PreferredVenv
)

# Setze die Konsole auf UTF-8 für korrekte Umlaut-Ausgabe
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 6) {
    $OutputEncoding = [System.Text.Encoding]::UTF8
}

function Show-Usage {
    Microsoft.PowerShell.Utility\Write-Host "PC-Konfigurator Build-Skript - Optionen:" -ForegroundColor DarkCyan
    Microsoft.PowerShell.Utility\Write-Host "  -Help          : Nur diese Hilfe anzeigen und beenden" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -NoVersionBump : Versionsnummer/README/docs/BUILD-INFO nicht aktualisieren" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -SkipZip       : ZIP-Erstellung im release-Ordner überspringen" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -SkipMarkdownLint : Markdownlint-Prüfung vor dem Build überspringen" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -Quiet         : Kompakte Ausgabe (nur Fehler + Kurzfazit)" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -PreferredVenv : Bevorzugte venv wählen (.venv)" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  Beispiele: .\build.ps1 | .\build.ps1 -Help | .\build.ps1 -NoVersionBump | .\build.ps1 -NoVersionBump -SkipZip | .\build.ps1 -NoVersionBump -SkipZip -Quiet | .\build.ps1 -PreferredVenv .venv -Quiet | .\build.ps1 -PreferredVenv .venv | .\build.ps1 -SkipMarkdownLint" -ForegroundColor DarkGray
}

function Set-GitOneDriveSafety {
    [CmdletBinding()]
    param()

    $gitDir = Join-Path $PSScriptRoot '.git'
    if (-not (Test-Path $gitDir)) {
        return
    }

    try {
        $null = git -C $PSScriptRoot config --local gc.auto 0
        $null = git -C $PSScriptRoot config --local gc.autoDetach false
        $null = git -C $PSScriptRoot config --local maintenance.auto false
        Write-Host "Git-OneDrive-Schutz aktiv: gc.auto=0, gc.autoDetach=false, maintenance.auto=false" -ForegroundColor DarkGray
    } catch {
        Write-Host "Hinweis: Git-OneDrive-Schutz konnte nicht vollständig gesetzt werden: $_" -ForegroundColor Yellow
    }
}

function Update-MarkdownTail {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return
    }

    if (-not (Test-Path $Path)) {
        return
    }

    try {
        $raw = Get-Content -Path $Path -Raw -Encoding UTF8
        # Zeilenenden vereinheitlichen und trailing Leerzeilen entfernen
        $normalized = $raw -replace "`r`n", "`n"
        $normalized = $normalized -replace "`r", "`n"
        $normalized = [regex]::Replace($normalized, '(?s)(?:\n[ \t]*)+$', '')
        # Genau ein abschließender Zeilenumbruch (CRLF)
        $normalized = ($normalized + "`n") -replace "`n", "`r`n"

        Set-Content -Path $Path -Value $normalized -Encoding UTF8 -NoNewline
    } catch {
        Write-Host "Hinweis: Markdown-EOF-Normalisierung fehlgeschlagen für $Path : $_" -ForegroundColor Yellow
    }
}

function Copy-DirectoryRobust {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination,
        [string]$Label = 'Verzeichnis'
    )

    if (-not (Test-Path $Source)) {
        throw "$Label fehlt: $Source"
    }

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null

    $sourceRoot = (Resolve-Path $Source).Path.TrimEnd('\') + '\'
    $copied = 0
    $skipped = 0

    foreach ($item in Get-ChildItem -Path $Source -Recurse -File -ErrorAction SilentlyContinue) {
        $relativePath = $item.FullName.Substring($sourceRoot.Length)
        $targetFile = Join-Path $Destination $relativePath
        $targetDir = Split-Path $targetFile -Parent

        try {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
            Copy-Item -LiteralPath $item.FullName -Destination $targetFile -Force -ErrorAction Stop
            $copied++
        } catch {
            $skipped++
            Write-Host "Warnung: $Label-Datei übersprungen: $relativePath ($_ )" -ForegroundColor Yellow
        }
    }

    Write-Host "$Label kopiert: $copied Datei(en), $skipped übersprungen." -ForegroundColor DarkGray
    return [pscustomobject]@{
        Copied = $copied
        Skipped = $skipped
    }
}

function New-ReleaseNotesFile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Version,
        [Parameter(Mandatory = $true)]
        [string]$BuildDirName,
        [Parameter(Mandatory = $true)]
        [string]$ExeName,
        [Parameter(Mandatory = $true)]
        [string]$ReleaseDir,
        [string]$ZipFileName
    )

    if (-not (Test-Path $ReleaseDir)) {
        New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
    }

    $notesPath = Join-Path $ReleaseDir "RELEASE_NOTES_v$Version.md"
    $buildDate = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $displayDate = (Get-Date).ToString('yyyy-MM-dd')

    $zipArtifactLine = if ($ZipFileName) {
        "- Release-ZIP: release/$ZipFileName"
    } else {
        "- Release-ZIP: *(noch nicht erstellt - Build wurde mit -SkipZip ausgefuehrt)*"
    }

    $qualityZipLine = if ($ZipFileName) {
        "- ZIP-Artefakt erstellt und im Release-Ordner abgelegt."
    } else {
        "- ZIP-Artefakt in diesem Lauf nicht erstellt (-SkipZip)."
    }

    $recentCommits = @()
    try {
        $gitLog = git log --oneline --no-decorate -5 2>$null
        foreach ($entry in $gitLog) {
            if ([string]::IsNullOrWhiteSpace($entry)) {
                continue
            }
            $parts = $entry -split ' ', 2
            if ($parts.Count -eq 2) {
                $recentCommits += "- ``$($parts[0])`` $($parts[1])"
            } else {
                $recentCommits += "- $entry"
            }
        }
    } catch {
        # Fallback weiter unten
    }

    if (-not $recentCommits -or $recentCommits.Count -eq 0) {
        $recentCommits = @("- *(Commitliste konnte automatisch nicht ermittelt werden.)*")
    }

    $contentLines = @(
        "# Release Notes v$Version",
        "",
        "Datum: $displayDate",
        "",
        "## Highlights",
        "",
        "- Namens-, Build- und Doku-Anpassungen wurden in diesem Release-Stand konsolidiert.",
        "- Das Build wurde als Onefile-EXE erzeugt und für die Verteilung aufbereitet.",
        "- Bitte Highlights bei Bedarf projektspezifisch ergänzen.",
        "",
        "## Qualitätsstatus",
        "",
        "- Release-Build erfolgreich erzeugt.",
        "$qualityZipLine",
        "- Automatische Basisprüfung (Build/Packaging) im Skript durchlaufen.",
        "",
        "## Artefakte",
        "",
        "- Build-Verzeichnis: dist/$BuildDirName/",
        "- EXE: dist/$BuildDirName/$ExeName",
        "$zipArtifactLine",
        "",
        "## Enthaltene Commits (aktuelle Historie)",
        ""
    )

    $contentLines += $recentCommits

    $contentLines += @(
        "",
        "## Technische Build-Informationen",
        "",
        "- Build-Datum: $buildDate",
        "- Build-Modus: --onefile --windowed",
        "- EXE-Name: $ExeName"
    )

    $content = $contentLines -join "`r`n"

    Set-Content -Path $notesPath -Value $content -Encoding UTF8
    Update-MarkdownTail -Path $notesPath
    Write-Host "Release-Notes erstellt/aktualisiert: $notesPath" -ForegroundColor Green
    return $notesPath
}

function Move-PreviousReleaseArtifacts {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ReleaseDir,
        [Parameter(Mandatory = $true)]
        [string]$CurrentVersion
    )

    if (-not (Test-Path $ReleaseDir)) {
        return
    }

    $archiveDir = Join-Path $ReleaseDir '_Archiv'
    $versionPattern = '^(?:PC-Konfigurator-v|RELEASE_NOTES_v)(?<Version>\d+\.\d+\.\d+)(?:\.zip|\.md)?$'
    $previousArtifacts = Get-ChildItem -Path $ReleaseDir -Force -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match $versionPattern -and $matches.Version -ne $CurrentVersion
        }

    if (-not $previousArtifacts) {
        return
    }

    New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
    foreach ($artifact in $previousArtifacts) {
        $targetPath = Join-Path $archiveDir $artifact.Name
        if (Test-Path $targetPath) {
            Remove-Item -LiteralPath $targetPath -Recurse -Force -ErrorAction Stop
        }

        $archived = $false
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            try {
                Move-Item -LiteralPath $artifact.FullName -Destination $targetPath -Force -ErrorAction Stop
                $archived = $true
                break
            } catch {
                if ($attempt -lt 3) {
                    Write-Host "Archivierung wartet auf OneDrive-Freigabe ($attempt/3): $($artifact.Name)" -ForegroundColor Yellow
                    Start-Sleep -Milliseconds 1000
                } else {
                    Write-Host "Warnung: Älteres Release konnte wegen einer Dateisperre nicht archiviert werden: $($artifact.Name)" -ForegroundColor Yellow
                }
            }
        }

        if ($archived) {
            Write-Host "Älteres Release archiviert: $($artifact.Name) -> release/_Archiv/" -ForegroundColor DarkGray
        }
    }
}

if (-not $Quiet -or $Help) {
    Show-Usage
}

if ($Help) {
    exit 0
}

# OneDrive-Locks vermeiden: lokale Git-Autowartung im Repo deaktivieren
Set-GitOneDriveSafety

# Vorab: bekannte Markdown-Dateien auf sauberen EOF normalisieren
foreach ($mdPath in @(
    (Join-Path $PSScriptRoot 'README.md'),
    (Join-Path $PSScriptRoot 'docs\DOKUMENTATION_ANWENDER.md')
)) {
    Update-MarkdownTail -Path $mdPath
}

# Vorab: Markdownlint als Standard-Dokuroutine ausführen
if ($SkipMarkdownLint) {
    Write-Host "Markdownlint-Prüfung übersprungen (-SkipMarkdownLint)." -ForegroundColor Yellow
} else {
    $mdLintScript = Join-Path $PSScriptRoot 'tools\lint-markdown.ps1'
    if (Test-Path $mdLintScript) {
        Write-Host "Markdownlint-Auto-Fix läuft..." -ForegroundColor Cyan
        & $mdLintScript -Fix -Quiet:$Quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Build abgebrochen: Markdownlint-Fehler beim Auto-Fix erkannt." -ForegroundColor Red
            exit 1
        }

        Write-Host "Markdownlint-Verifikation (ohne Auto-Fix) läuft..." -ForegroundColor Cyan
        & $mdLintScript -Quiet:$Quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Build abgebrochen: Nicht automatisch behebbarer Markdownlint-Fehler erkannt." -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Hinweis: Markdownlint-Skript nicht gefunden, Prüfung wird übersprungen: $mdLintScript" -ForegroundColor Yellow
    }
}

$script:QuietMode = $Quiet
function Write-Host {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [object[]]$Object,
        [ConsoleColor]$ForegroundColor,
        [switch]$NoNewline,
        [object]$Separator = ' '
    )

    if (-not $script:QuietMode) {
        Microsoft.PowerShell.Utility\Write-Host @PSBoundParameters
        return
    }

    $text = if ($null -eq $Object) { '' } else { ($Object -join [string]$Separator) }
    $isErrorColor = $PSBoundParameters.ContainsKey('ForegroundColor') -and $ForegroundColor -eq [ConsoleColor]::Red
    $isImportantErrorText = $text -match 'fehlgeschlagen|nicht gefunden|Konnte .* nicht|ERROR|Kein Build-Verzeichnis|konnte nicht erstellt werden'
    $isSummary = $text -match 'Build erfolgreich abgeschlossen!|^Ergebnis:|^Build-Verzeichnis:|^EXE-Datei:|^Fonts:|^Templates:|^Dokumentation:|^ZIP-'

    if ($isErrorColor -or $isImportantErrorText -or $isSummary) {
        Microsoft.PowerShell.Utility\Write-Host @PSBoundParameters
    }
}


# Schritt 0: Versionsnummer automatisch erhöhen (optional überspringbar)
$buildInfoPath = Join-Path $PSScriptRoot 'src/build_info.py'
$buildInfoTxtPath = Join-Path $PSScriptRoot 'src\BUILD-INFO.txt'
if (Test-Path $buildInfoPath) {
    $content = Get-Content $buildInfoPath -Raw
    if ($content -match "'version': '([0-9]+)\.([0-9]+)\.([0-9]+)'") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
        if ($NoVersionBump) {
            $newVersion = "$major.$minor.$patch"
            Write-Host "Versionssprung übersprungen (-NoVersionBump). Verwende Version: $newVersion" -ForegroundColor Cyan
        } else {
            $nextMajor = $major
            $nextMinor = $minor
            $nextPatch = $patch + 1
            $newVersion = "$nextMajor.$nextMinor.$nextPatch"
            $newDate = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss')
            $content = $content -replace "'version': '\d+\.\d+\.\d+'", "'version': '$newVersion'"
            $content = $content -replace "'build_date': '[^']+'", "'build_date': '$newDate'"
            Set-Content $buildInfoPath $content -Encoding UTF8
            Write-Host "Neue Version: $newVersion (build_info.py aktualisiert)" -ForegroundColor Cyan

            # --- README.md und docs/DOKUMENTATION_ANWENDER.md automatisch aktualisieren ---
            $readmePath = Join-Path $PSScriptRoot 'README.md'
            $anwenderDocPath = Join-Path $PSScriptRoot 'docs\DOKUMENTATION_ANWENDER.md'
            $pythonVersionShort = $null
            if ($content -match "'python_version': '([^']+)'") {
                $pythonVersionShort = $matches[1] -replace ' \(.*', ''
            }
            $dateForMd = (Get-Date).ToString('dd.MM.yyyy')

            # README.md: **Version:** 3.3.1 (Build: 23.05.2026, Python 3.13.7)
            if (Test-Path $readmePath) {
                $readme = Get-Content $readmePath -Raw
                $readme = [regex]::Replace($readme, '\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+ \(Build: [0-9]{2}\.[0-9]{2}\.[0-9]{4}, Python [0-9.]+\)', "**Version:** $newVersion (Build: $dateForMd, Python $pythonVersionShort)")
                Set-Content $readmePath $readme -Encoding UTF8
                Update-MarkdownTail -Path $readmePath
                Write-Host "README.md automatisch aktualisiert." -ForegroundColor Cyan
            }

            # docs/DOKUMENTATION_ANWENDER.md: **Version:** 3.3.1 (25.05.2026)
            if (Test-Path $anwenderDocPath) {
                $anwenderDoc = Get-Content $anwenderDocPath -Raw
                $anwenderDoc = [regex]::Replace($anwenderDoc, '\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+ \([0-9]{2}\.[0-9]{2}\.[0-9]{4}\)', "**Version:** $newVersion ($dateForMd)")
                Set-Content $anwenderDocPath $anwenderDoc -Encoding UTF8
                Update-MarkdownTail -Path $anwenderDocPath
                Write-Host "docs/DOKUMENTATION_ANWENDER.md automatisch aktualisiert." -ForegroundColor Cyan
            }

            # --- src/BUILD-INFO.txt automatisch aktualisieren ---
            $pythonVersion = $null
            $platform = $null
            if ($content -match "'python_version': '([^']+)'") { $pythonVersion = $matches[1] }
            if ($content -match "'platform': '([^']+)'") { $platform = $matches[1] }
            $buildInfoTxt = @()
            $buildInfoTxt += "# Build-Informationen"
            $buildInfoTxt += ""
            $buildInfoTxt += "**Build:** PC-Konfigurator"
            $buildInfoTxt += "**Datum:** $newDate"
            $buildInfoTxt += "**Version:** $newVersion (Release)"
            $buildInfoTxt += ""
            $buildInfoTxt += "## Build-Details"
            $buildInfoTxt += ""
            $buildInfoTxt += "- **Python-Version:** $pythonVersion"
            $buildInfoTxt += "- **PyInstaller:** 6.17.0"
            $buildInfoTxt += "- **Build-Modus:** --onefile --windowed"
            $buildInfoTxt += "- **Build-Datum:** $newDate"
            $buildInfoTxt += "- **Build-Version:** $newVersion"
            $buildInfoTxt += "- **Plattform:** $platform"
            $buildInfoTxt += "- **EXE-Name:** PC-Konfigurator.exe"
            $buildInfoTxt += ""
            Set-Content $buildInfoTxtPath $buildInfoTxt -Encoding UTF8
            Write-Host "src/BUILD-INFO.txt automatisch aktualisiert." -ForegroundColor Cyan
        }
    } else {
        Write-Host "Konnte Versionsnummer nicht erkennen!" -ForegroundColor Red
    }
} else {
    Write-Host "build_info.py nicht gefunden!" -ForegroundColor Red
}

Write-Host "PC-Konfigurator Build-Prozess" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

# Python-Interpreter bestimmen (unterstützt .venv)
$pythonExe = $null
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'

if ($PreferredVenv -eq '.venv') {
    if (Test-Path $venvPython) {
        $pythonExe = $venvPython
        Write-Host "Verwende Python aus .venv (explizit gewählt)" -ForegroundColor Cyan
    }
} elseif (Test-Path $venvPython) {
    $pythonExe = $venvPython
    Write-Host "Verwende Python aus .venv" -ForegroundColor Cyan
} else {
    $pythonExe = 'py'
    Write-Host "Keine lokale venv gefunden, verwende py-Launcher" -ForegroundColor Yellow
}


# Schritt 1: PyInstaller Build

Write-Host "`nVorbereitung: Lösche alte Logdateien in dist..." -ForegroundColor Yellow
if (Test-Path dist) {
    $logFiles = Get-ChildItem dist -Recurse -Include *.log -File -ErrorAction SilentlyContinue
    foreach ($log in $logFiles) {
        try {
            Remove-Item $log.FullName -Force -ErrorAction Stop
            Write-Host "  Gelöscht: $($log.FullName)" -ForegroundColor DarkGray
        } catch {
            Write-Host "  Konnte nicht löschen: $($log.FullName) ($_ )" -ForegroundColor Red
        }
    }
}

if ($NoVersionBump -and $newVersion) {
    $reuseBuildDir = Join-Path $PSScriptRoot "dist/PC-Konfigurator-v$newVersion"
    if (Test-Path $reuseBuildDir) {
        Write-Host "Vorhandenen Build-Ordner für -NoVersionBump bereinigen: $reuseBuildDir" -ForegroundColor Yellow
        try {
            & attrib -r -h -s "$reuseBuildDir\*" /S /D 2>$null
        } catch {
            # Ignorieren: attrib kann bei einzelnen Dateien fehlschlagen
        }

        try {
            Remove-Item $reuseBuildDir -Recurse -Force -ErrorAction Stop
            Write-Host "Alter Build-Ordner entfernt." -ForegroundColor DarkGray
        } catch {
            Write-Host "Konnte vorhandenen Build-Ordner nicht entfernen: $_" -ForegroundColor Red
            Write-Host "Bitte ggf. Explorer-Fenster schließen oder OneDrive-Sync kurz pausieren." -ForegroundColor Yellow
            exit 1
        }
    }
}

Write-Host "`n1. PyInstaller Build wird erstellt..." -ForegroundColor Yellow
$pyInstallerLog = Join-Path $PSScriptRoot 'build\last-pyinstaller.log'
# Workpath außerhalb von OneDrive, damit der OneDrive-Sync die Intermediate-Dateien nicht sperrt
$pyiWorkPath = Join-Path $env:TEMP 'pyi-build-pc-konfigurator'
$specPath = Join-Path $PSScriptRoot 'src\PC-Konfigurator.spec'
$specOffline = $false
if (Test-Path $specPath) {
    try {
        # OneDrive-Offline robust via attrib prüfen (zeigt z.B. "A O P ...")
        $attribLine = (& attrib $specPath 2>$null | Select-Object -First 1)
        if ($attribLine -match '\sO\s') {
            $specOffline = $true
            Write-Host "Hinweis: Spec-Datei ist OneDrive-Offline markiert. Fallback ohne .spec wird verwendet." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Warnung: Konnte Spec-Attribute nicht lesen. Verwende Fallback ohne .spec." -ForegroundColor Yellow
        $specOffline = $true
    }
} else {
    $specOffline = $true
    Write-Host "Hinweis: Spec-Datei nicht gefunden. Fallback ohne .spec wird verwendet." -ForegroundColor Yellow
}

$entryScript = Join-Path $PSScriptRoot 'src\main.py'
$iconPath = Join-Path $PSScriptRoot 'src\app_icon.ico'

if ($Quiet) {
    New-Item -ItemType Directory -Path (Split-Path $pyInstallerLog -Parent) -Force | Out-Null
    if (-not $specOffline) {
        & $pythonExe -m PyInstaller $specPath --noconfirm --workpath $pyiWorkPath *> $pyInstallerLog
    } else {
        & $pythonExe -m PyInstaller --noconfirm --workpath $pyiWorkPath --specpath $pyiWorkPath --onefile --windowed --name 'PC-Konfigurator' --icon $iconPath --paths (Join-Path $PSScriptRoot 'src') --hidden-import pythoncom --collect-submodules win32com --add-data "$PSScriptRoot\data;data" --add-data "$PSScriptRoot\docs;docs" --add-data "$PSScriptRoot\src\pcconfig;pcconfig" --add-data "$PSScriptRoot\src\BUILD-INFO.txt;." --add-data "$PSScriptRoot\README.md;." --add-data "$PSScriptRoot\src\app_icon.ico;." $entryScript *> $pyInstallerLog
    }
} else {
    if (-not $specOffline) {
        & $pythonExe -m PyInstaller $specPath --noconfirm --workpath $pyiWorkPath
    } else {
        & $pythonExe -m PyInstaller --noconfirm --workpath $pyiWorkPath --specpath $pyiWorkPath --onefile --windowed --name 'PC-Konfigurator' --icon $iconPath --paths (Join-Path $PSScriptRoot 'src') --hidden-import pythoncom --collect-submodules win32com --add-data "$PSScriptRoot\data;data" --add-data "$PSScriptRoot\docs;docs" --add-data "$PSScriptRoot\src\pcconfig;pcconfig" --add-data "$PSScriptRoot\src\BUILD-INFO.txt;." --add-data "$PSScriptRoot\README.md;." --add-data "$PSScriptRoot\src\app_icon.ico;." $entryScript
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller Build fehlgeschlagen!" -ForegroundColor Red
    if ($Quiet -and (Test-Path $pyInstallerLog)) {
        Write-Host "Details siehe: $pyInstallerLog" -ForegroundColor Yellow
        Write-Host "--- Letzte 40 Zeilen ---" -ForegroundColor Yellow
        Get-Content $pyInstallerLog -Tail 40
    }
    exit 1
}

# Schritt 2: Onefile-EXE in versionierten Ausgabeordner verschieben
Write-Host "`n2. Onefile-Ausgabe wird vorbereitet..." -ForegroundColor Yellow

$distRoot = Join-Path $PSScriptRoot 'dist'
$builtExe = Join-Path $distRoot 'PC-Konfigurator.exe'
if (-not (Test-Path $builtExe)) {
    Write-Host "Build-EXE nicht gefunden: $builtExe" -ForegroundColor Red
    exit 1
}

$buildDirName = if ($newVersion) { "PC-Konfigurator-v$newVersion" } else { "PC-Konfigurator-vmanual" }
$buildDirPath = Join-Path $distRoot $buildDirName

if (Test-Path $buildDirPath) {
    try {
        Remove-Item $buildDirPath -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Host "Konnte vorhandenes Build-Verzeichnis nicht entfernen: $_" -ForegroundColor Red
        exit 1
    }
}

New-Item -ItemType Directory -Path $buildDirPath -Force | Out-Null
$targetExe = Join-Path $buildDirPath 'PC-Konfigurator.exe'

$moved = $false
for ($attempt = 1; $attempt -le 3; $attempt++) {
    try {
        Move-Item -Path $builtExe -Destination $targetExe -Force -ErrorAction Stop
        $moved = $true
        break
    } catch {
        if ($attempt -lt 3) {
            Write-Host "EXE ist noch gesperrt (Versuch $attempt/3). Neuer Versuch..." -ForegroundColor Yellow
            Start-Sleep -Milliseconds 700
        }
    }
}

if (-not $moved) {
    try {
        Write-Host "Move fehlgeschlagen, versuche Copy-Fallback..." -ForegroundColor Yellow
        Copy-Item -Path $builtExe -Destination $targetExe -Force -ErrorAction Stop
        Remove-Item -Path $builtExe -Force -ErrorAction SilentlyContinue
        $moved = $true
    } catch {
        Write-Host "Konnte EXE weder verschieben noch kopieren: $_" -ForegroundColor Red
        exit 1
    }
}

# Zusätzliche Release-Artefakte neben der EXE bereitstellen
$docsSource = Join-Path $PSScriptRoot 'docs'
$docsTarget = Join-Path $buildDirPath 'docs'
if (-not (Test-Path $docsSource)) {
    Write-Host "docs-Verzeichnis fehlt: $docsSource" -ForegroundColor Red
    exit 1
}

Copy-DirectoryRobust -Source $docsSource -Destination $docsTarget -Label 'docs'

$dataSource = Join-Path $PSScriptRoot 'data'
$dataTarget = Join-Path $buildDirPath 'data'
if (-not (Test-Path $dataSource)) {
    Write-Host "data-Verzeichnis fehlt: $dataSource" -ForegroundColor Red
    exit 1
}

Copy-DirectoryRobust -Source $dataSource -Destination $dataTarget -Label 'data'

$buildDir = Get-Item $buildDirPath

if (-not (Test-Path $targetExe)) {
    Write-Host "Onefile-EXE konnte nicht in den Build-Ordner verschoben werden." -ForegroundColor Red
    exit 1
}

# Schritt 3: Erfolgsmeldung
if ($Quiet) {
    Microsoft.PowerShell.Utility\Write-Host "Build erfolgreich abgeschlossen!" -ForegroundColor Green
} else {
    Write-Host "`nBuild erfolgreich abgeschlossen!" -ForegroundColor Green
}

# Zeige Ergebnis

if ($buildDir) {
    if ($Quiet) {
        Microsoft.PowerShell.Utility\Write-Host "Ergebnis:" -ForegroundColor Cyan
        Microsoft.PowerShell.Utility\Write-Host "Build-Verzeichnis: dist/$($buildDir.Name)" -ForegroundColor White
    } else {
        Write-Host "`nErgebnis:" -ForegroundColor Cyan
        Write-Host "Build-Verzeichnis: dist/$($buildDir.Name)" -ForegroundColor White
    }
    $exeFile = Get-ChildItem "$($buildDir.FullName)\*.exe" | Select-Object -First 1
    if ($exeFile) {
        $sizeInMB = [Math]::Round($exeFile.Length / 1MB, 2)
        if ($Quiet) {
            Microsoft.PowerShell.Utility\Write-Host "EXE-Datei: $($exeFile.Name) (${sizeInMB} MB)" -ForegroundColor White
        } else {
            Write-Host "EXE-Datei: $($exeFile.Name) (${sizeInMB} MB)" -ForegroundColor White
        }
    }

    if ($Quiet) {
        Microsoft.PowerShell.Utility\Write-Host "Ausgabe: Onefile-EXE (keine externe _internal-Struktur)" -ForegroundColor White
    } else {
        Write-Host "Ausgabe: Onefile-EXE (keine externe _internal-Struktur)" -ForegroundColor White
    }

    $releaseDir = Join-Path $PSScriptRoot 'release'
    $notesVersion = if ($newVersion) { $newVersion } else { 'manual' }
    Move-PreviousReleaseArtifacts -ReleaseDir $releaseDir -CurrentVersion $notesVersion
    $null = New-ReleaseNotesFile `
        -Version $notesVersion `
        -BuildDirName $buildDir.Name `
        -ExeName $exeFile.Name `
        -ReleaseDir $releaseDir

    if ($SkipZip) {
        if ($Quiet) {
            Microsoft.PowerShell.Utility\Write-Host "ZIP-Erstellung übersprungen (-SkipZip)." -ForegroundColor Yellow
        } else {
            Write-Host "ZIP-Erstellung übersprungen (-SkipZip)." -ForegroundColor Yellow
        }
    } else {
        # Schritt 4: ZIP-Release erstellen
        if (-not (Test-Path $releaseDir)) {
            New-Item -ItemType Directory -Path $releaseDir | Out-Null
            Write-Host "Release-Ordner erstellt: $releaseDir" -ForegroundColor DarkGray
        }

        $zipPath = Join-Path $releaseDir "$($buildDir.Name).zip"
        try {
            if (Test-Path $zipPath) {
                Remove-Item $zipPath -Force -ErrorAction Stop
            }

            # Explorer-kompatibles ZIP ohne Wrapper-Ordner erzeugen
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $zipSourceItems = Join-Path $buildDir.FullName '*'
            Compress-Archive -Path $zipSourceItems -DestinationPath $zipPath -CompressionLevel Optimal -Force

            # ZIP-Sanity-Check: Entpacktest in Temp + Kernartefakte prüfen
            $extractRoot = Join-Path $env:TEMP ("zip-verify-pc-konfigurator-" + [guid]::NewGuid().ToString("N"))
            New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
            Expand-Archive -Path $zipPath -DestinationPath $extractRoot -Force

            $exeEntryCount = @(Get-ChildItem $extractRoot -Recurse -File -Filter 'PC-Konfigurator.exe' -ErrorAction SilentlyContinue).Count
            $docsEntryCount = @(Get-ChildItem (Join-Path $extractRoot 'docs') -Recurse -File -ErrorAction SilentlyContinue).Count
            $dataEntryCount = @(Get-ChildItem (Join-Path $extractRoot 'data') -Recurse -File -ErrorAction SilentlyContinue).Count

            if ($exeEntryCount -le 0) {
                throw "ZIP-Sanity-Check fehlgeschlagen: EXE nicht gefunden."
            }
            if ($docsEntryCount -le 0) {
                throw "ZIP-Sanity-Check fehlgeschlagen: docs-Verzeichnis nicht gefunden."
            }
            if ($dataEntryCount -le 0) {
                throw "ZIP-Sanity-Check fehlgeschlagen: data-Verzeichnis nicht gefunden."
            }

            $null = New-ReleaseNotesFile `
                -Version $notesVersion `
                -BuildDirName $buildDir.Name `
                -ExeName $exeFile.Name `
                -ReleaseDir $releaseDir `
                -ZipFileName (Split-Path $zipPath -Leaf)

            try {
                Remove-Item $extractRoot -Recurse -Force -ErrorAction Stop
            } catch {
                Write-Host "Warnung: Konnte temporären ZIP-Check-Ordner nicht entfernen: $_" -ForegroundColor Yellow
            }

            if ($Quiet) {
                Microsoft.PowerShell.Utility\Write-Host "ZIP-Release erstellt: $zipPath" -ForegroundColor Green
                Microsoft.PowerShell.Utility\Write-Host "ZIP-Check: EXE=$exeEntryCount, docs=$docsEntryCount, data=$dataEntryCount" -ForegroundColor White
            } else {
                Write-Host "ZIP-Release erstellt: $zipPath" -ForegroundColor Green
                Write-Host "ZIP-Check: EXE=$exeEntryCount, docs=$docsEntryCount, data=$dataEntryCount" -ForegroundColor White
            }
        } catch {
            Write-Host "ZIP-Release konnte nicht erstellt werden: $_" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "Kein Build-Verzeichnis für ZIP-Erstellung gefunden." -ForegroundColor Red
    exit 1
}