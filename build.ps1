# Build-Skript für PC-Konfigurator-Portable
# Erstellt automatisch das Build und führt Post-Build-Aktionen aus

param(
    [switch]$NoVersionBump,
    [switch]$SkipZip,
    [switch]$Help,
    [switch]$Quiet
)

# Setze die Konsole auf UTF-8 für korrekte Umlaut-Ausgabe
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 6) {
    $OutputEncoding = [System.Text.Encoding]::UTF8
}

function Show-Usage {
    Microsoft.PowerShell.Utility\Write-Host "PC-Konfigurator Build-Skript - Optionen:" -ForegroundColor DarkCyan
    Microsoft.PowerShell.Utility\Write-Host "  -Help          : Nur diese Hilfe anzeigen und beenden" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -NoVersionBump : Versionsnummer/README/ANLEITUNG/BUILD-INFO nicht aktualisieren" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -SkipZip       : ZIP-Erstellung im release-Ordner überspringen" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  -Quiet         : Kompakte Ausgabe (nur Fehler + Kurzfazit)" -ForegroundColor DarkGray
    Microsoft.PowerShell.Utility\Write-Host "  Beispiele: .\build.ps1 | .\build.ps1 -Help | .\build.ps1 -NoVersionBump | .\build.ps1 -NoVersionBump -SkipZip | .\build.ps1 -NoVersionBump -SkipZip -Quiet" -ForegroundColor DarkGray
}

if (-not $Quiet -or $Help) {
    Show-Usage
}

if ($Help) {
    exit 0
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
$buildInfoTxtPath = Join-Path $PSScriptRoot 'BUILD-INFO.txt'
$newVersion = $null
if (Test-Path $buildInfoPath) {
    $content = Get-Content $buildInfoPath -Raw
    if ($content -match "'version': '([0-9]+)\.([0-9]+)\.([0-9]+)'") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
        $currentVersion = "$major.$minor.$patch"

        if ($NoVersionBump) {
            $newVersion = $currentVersion
            Write-Host "Versionssprung übersprungen (-NoVersionBump). Verwende Version: $newVersion" -ForegroundColor Cyan
        } else {
            $nextMajor = $major
            $nextMinor = $minor
            $nextPatch = $patch + 1
            if ($nextPatch -ge 10) {
                $nextPatch = 0
                $nextMinor++
                if ($nextMinor -ge 10) {
                    $nextMinor = 0
                    $nextMajor++
                }
            }
            $newVersion = "$nextMajor.$nextMinor.$nextPatch"
            $newDate = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss')
            $content = $content -replace "'version': '\d+\.\d+\.\d+'", "'version': '$newVersion'"
            $content = $content -replace "'build_date': '[^']+'", "'build_date': '$newDate'"
            Set-Content $buildInfoPath $content -Encoding UTF8
            Write-Host "Neue Version: $newVersion (build_info.py aktualisiert)" -ForegroundColor Cyan

            # --- README.md und ANLEITUNG.md automatisch aktualisieren ---
            $readmePath = Join-Path $PSScriptRoot 'README.md'
            $anleitungPath = Join-Path $PSScriptRoot 'ANLEITUNG.md'
            $pythonVersionShort = $null
            if ($content -match "'python_version': '([^']+)'") {
                $pythonVersionShort = $matches[1] -replace ' \(.*', ''
            }
            $dateForMd = (Get-Date).ToString('dd.MM.yyyy')

            # README.md: *Version: 1.0.24 (Build: 07.04.2026, Python 3.13.7)*
            if (Test-Path $readmePath) {
                $readme = Get-Content $readmePath -Raw
                $readme = [regex]::Replace($readme, '\*Version: [0-9]+\.[0-9]+\.[0-9]+ \(Build: [0-9]{2}\.[0-9]{2}\.[0-9]{4}, Python [0-9.]+\)\*', "*Version: $newVersion (Build: $dateForMd, Python $pythonVersionShort)*")
                Set-Content $readmePath $readme -Encoding UTF8
                Write-Host "README.md automatisch aktualisiert." -ForegroundColor Cyan
            }

            # ANLEITUNG.md: **Version:** 1.0.24 (07.04.2026)
            if (Test-Path $anleitungPath) {
                $anleitung = Get-Content $anleitungPath -Raw
                $anleitung = [regex]::Replace($anleitung, '\*\*Version:\*\* [0-9]+\.[0-9]+\.[0-9]+ \([0-9]{2}\.[0-9]{2}\.[0-9]{4}\)', "**Version:** $newVersion ($dateForMd)")
                Set-Content $anleitungPath $anleitung -Encoding UTF8
                Write-Host "ANLEITUNG.md automatisch aktualisiert." -ForegroundColor Cyan
            }

            # --- BUILD-INFO.txt automatisch aktualisieren ---
            $pythonVersion = $null
            $platform = $null
            if ($content -match "'python_version': '([^']+)'") { $pythonVersion = $matches[1] }
            if ($content -match "'platform': '([^']+)'") { $platform = $matches[1] }
            $buildInfoTxt = @()
            $buildInfoTxt += "# Build-Informationen"
            $buildInfoTxt += ""
            $buildInfoTxt += "**Build:** PC-Konfigurator-Portable"
            $buildInfoTxt += "**Datum:** $newDate"
            $buildInfoTxt += "**Version:** $newVersion (Release)"
            $buildInfoTxt += ""
            $buildInfoTxt += "## Build-Details"
            $buildInfoTxt += ""
            $buildInfoTxt += "- **Python-Version:** $pythonVersion"
            $buildInfoTxt += "- **PyInstaller:** 6.17.0"
            $buildInfoTxt += "- **Build-Modus:** --onedir --windowed"
            $buildInfoTxt += "- **Build-Datum:** $newDate"
            $buildInfoTxt += "- **Build-Version:** $newVersion"
            $buildInfoTxt += "- **Plattform:** $platform"
            $buildInfoTxt += "- **EXE-Name:** PC-Konfigurator-Portable.exe"
            $buildInfoTxt += ""
            Set-Content $buildInfoTxtPath $buildInfoTxt -Encoding UTF8
            Write-Host "BUILD-INFO.txt automatisch aktualisiert." -ForegroundColor Cyan
        }
    } else {
        Write-Host "Konnte Versionsnummer nicht erkennen!" -ForegroundColor Red
    }
} else {
    Write-Host "build_info.py nicht gefunden!" -ForegroundColor Red
}

Write-Host "PC-Konfigurator Build-Prozess" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green


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
    $reuseBuildDir = Join-Path $PSScriptRoot "dist/PC-Konfigurator-Portable-v$newVersion"
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
$specPath = Join-Path $PSScriptRoot 'PC-Konfigurator-Portable.spec'
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

$buildName = if ($newVersion) { "PC-Konfigurator-Portable-v$newVersion" } else { "PC-Konfigurator-Portable-vmanual" }
$entryScript = Join-Path $PSScriptRoot 'src\main.py'
$iconPath = Join-Path $PSScriptRoot 'src\app_icon.ico'

if ($Quiet) {
    New-Item -ItemType Directory -Path (Split-Path $pyInstallerLog -Parent) -Force | Out-Null
    if (-not $specOffline) {
        & py -m PyInstaller $specPath --noconfirm --workpath $pyiWorkPath *> $pyInstallerLog
    } else {
        & py -m PyInstaller --noconfirm --workpath $pyiWorkPath --specpath $pyiWorkPath --onedir --windowed --name $buildName --icon $iconPath --paths (Join-Path $PSScriptRoot 'src') --hidden-import pythoncom --collect-submodules win32com $entryScript *> $pyInstallerLog
    }
} else {
    if (-not $specOffline) {
        & py -m PyInstaller $specPath --noconfirm --workpath $pyiWorkPath
    } else {
        & py -m PyInstaller --noconfirm --workpath $pyiWorkPath --specpath $pyiWorkPath --onedir --windowed --name $buildName --icon $iconPath --paths (Join-Path $PSScriptRoot 'src') --hidden-import pythoncom --collect-submodules win32com $entryScript
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

# Schritt 2: Post-Build-Aktionen
Write-Host "`n2. Post-Build-Aktionen werden ausgeführt..." -ForegroundColor Yellow
$postBuildLog = Join-Path $PSScriptRoot 'build\last-post-build.log'
if ($Quiet) {
    & py src/post_build.py *> $postBuildLog
} else {
    & py src/post_build.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Post-Build fehlgeschlagen!" -ForegroundColor Red
    if ($Quiet -and (Test-Path $postBuildLog)) {
        Write-Host "Details siehe: $postBuildLog" -ForegroundColor Yellow
        Write-Host "--- Letzte 40 Zeilen ---" -ForegroundColor Yellow
        Get-Content $postBuildLog -Tail 40
    }
    exit 1
}


# Schritt 2b: Aktuelles Build-Verzeichnis ermitteln (statt alle dist-Versionen zu bearbeiten)
$buildDir = $null
if ($newVersion) {
    $expectedBuildName = "PC-Konfigurator-Portable-v$newVersion"
    $buildDir = Get-ChildItem dist -Directory | Where-Object { $_.Name -eq $expectedBuildName } | Select-Object -First 1
}

if (-not $buildDir) {
    $buildDir = Get-ChildItem dist -Directory | Where-Object {$_.Name -like "PC-Konfigurator-Portable-v*"} | Sort-Object LastWriteTime | Select-Object -Last 1
}

if (-not $buildDir) {
    Write-Host "Kein Build-Verzeichnis nach Post-Build gefunden." -ForegroundColor Red
    exit 1
}

# Schritt 2c: Bereinige nur das _internal des aktuellen Builds
$internalPath = Join-Path $buildDir.FullName '_internal'
if (Test-Path $internalPath) {
    $delList = @('Fonts', 'Datei-Vorlagen', 'README.md', 'ANLEITUNG.md', 'BUILD-INFO.txt')
    foreach ($item in $delList) {
        $delPath = Join-Path $internalPath $item
        if (Test-Path $delPath) {
            try {
                Remove-Item $delPath -Recurse -Force -ErrorAction Stop
                Write-Host "Lösche $delPath aus _internal" -ForegroundColor DarkGray
            } catch {
                Write-Host "Konnte $delPath nicht löschen: $_" -ForegroundColor Red
            }
        }
    }
}

# Schritt 2d: Pflicht-Check - Externe Ordner müssen im Build vorhanden sein
$fontsPath = Join-Path $buildDir.FullName 'Fonts'
$templatesPath = Join-Path $buildDir.FullName 'Datei-Vorlagen'
$fontsCount = @(Get-ChildItem $fontsPath -Recurse -File -ErrorAction SilentlyContinue).Count
$templatesCount = @(Get-ChildItem $templatesPath -Recurse -File -ErrorAction SilentlyContinue).Count

if (-not (Test-Path $fontsPath) -or $fontsCount -le 0) {
    Write-Host "Pflicht-Check fehlgeschlagen: Fonts fehlt oder ist leer ($fontsPath)." -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $templatesPath) -or $templatesCount -le 0) {
    Write-Host "Pflicht-Check fehlgeschlagen: Datei-Vorlagen fehlt oder ist leer ($templatesPath)." -ForegroundColor Red
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
    
    # Zähle Inhalte
    $fonts = Get-ChildItem "$($buildDir.FullName)\Fonts" -Recurse -File -ErrorAction SilentlyContinue
    $templates = Get-ChildItem "$($buildDir.FullName)\Datei-Vorlagen" -Recurse -File -ErrorAction SilentlyContinue
    $docs = Get-ChildItem "$($buildDir.FullName)\*.md" -ErrorAction SilentlyContinue
    
    if ($Quiet) {
        Microsoft.PowerShell.Utility\Write-Host "Fonts: $($fonts.Count) Dateien" -ForegroundColor White
        Microsoft.PowerShell.Utility\Write-Host "Templates: $($templates.Count) Dateien" -ForegroundColor White
        Microsoft.PowerShell.Utility\Write-Host "Dokumentation: $($docs.Count) Dateien" -ForegroundColor White
    } else {
        Write-Host "Fonts: $($fonts.Count) Dateien" -ForegroundColor White
        Write-Host "Templates: $($templates.Count) Dateien" -ForegroundColor White
        Write-Host "Dokumentation: $($docs.Count) Dateien" -ForegroundColor White
    }

    if ($SkipZip) {
        if ($Quiet) {
            Microsoft.PowerShell.Utility\Write-Host "ZIP-Erstellung übersprungen (-SkipZip)." -ForegroundColor Yellow
        } else {
            Write-Host "ZIP-Erstellung übersprungen (-SkipZip)." -ForegroundColor Yellow
        }
    } else {
        # Schritt 4: ZIP-Release erstellen
        $releaseDir = Join-Path $PSScriptRoot 'release'
        if (-not (Test-Path $releaseDir)) {
            New-Item -ItemType Directory -Path $releaseDir | Out-Null
            Write-Host "Release-Ordner erstellt: $releaseDir" -ForegroundColor DarkGray
        }

        $zipPath = Join-Path $releaseDir "$($buildDir.Name).zip"
        try {
            if (Test-Path $zipPath) {
                Remove-Item $zipPath -Force -ErrorAction Stop
            }

            # tar.exe ist robuster bei langen Pfaden und versteckten Ordnern (_internal)
            # -a: Format anhand Dateiendung (.zip) erkennen
            # -C: aus dem dist-Ordner packen, damit der Build-Ordner als Root im ZIP liegt
            & tar.exe -a -c -f $zipPath -C $buildDir.Parent.FullName $buildDir.Name
            if ($LASTEXITCODE -ne 0) {
                throw "tar.exe fehlgeschlagen (ExitCode=$LASTEXITCODE)"
            }

            # ZIP-Sanity-Check: Kernordner müssen im Archiv enthalten sein
            $zipEntries = & tar.exe -tf $zipPath
            if ($LASTEXITCODE -ne 0 -or -not $zipEntries) {
                throw "ZIP-Sanity-Check fehlgeschlagen: Konnte ZIP-Inhalt nicht lesen."
            }

            $internalEntryCount = @($zipEntries | Where-Object { $_ -match '(^|/)_internal(/|$)' }).Count
            $fontsEntryCount = @($zipEntries | Where-Object { $_ -match '(^|/)Fonts(/|$)' }).Count
            $templatesEntryCount = @($zipEntries | Where-Object { $_ -match '(^|/)Datei-Vorlagen(/|$)' }).Count

            if ($internalEntryCount -le 0 -or $fontsEntryCount -le 0 -or $templatesEntryCount -le 0) {
                throw (
                    "ZIP-Sanity-Check fehlgeschlagen: " +
                    "_internal=$internalEntryCount, Fonts=$fontsEntryCount, Datei-Vorlagen=$templatesEntryCount"
                )
            }
            
            if ($Quiet) {
                Microsoft.PowerShell.Utility\Write-Host "ZIP-Release erstellt: $zipPath" -ForegroundColor Green
                Microsoft.PowerShell.Utility\Write-Host "ZIP-Check: _internal=$internalEntryCount, Fonts=$fontsEntryCount, Datei-Vorlagen=$templatesEntryCount" -ForegroundColor White
            } else {
                Write-Host "ZIP-Release erstellt: $zipPath" -ForegroundColor Green
                Write-Host "ZIP-Check: _internal=$internalEntryCount, Fonts=$fontsEntryCount, Datei-Vorlagen=$templatesEntryCount" -ForegroundColor White
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