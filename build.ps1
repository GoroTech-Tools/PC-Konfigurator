# Build-Skript für PC-Konfigurator-Portable
# Erstellt automatisch das Build und führt Post-Build-Aktionen aus

# Setze die Konsole auf UTF-8 für korrekte Umlaut-Ausgabe
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 6) {
    $OutputEncoding = [System.Text.Encoding]::UTF8
}


# Schritt 0: Versionsnummer automatisch erhöhen
$buildInfoPath = Join-Path $PSScriptRoot 'src/build_info.py'
$buildInfoTxtPath = Join-Path $PSScriptRoot 'BUILD-INFO.txt'
if (Test-Path $buildInfoPath) {
    $content = Get-Content $buildInfoPath -Raw
    if ($content -match "'version': '([0-9]+)\.([0-9]+)\.([0-9]+)'") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        $patch = [int]$matches[3]
        $patch++
        if ($patch -ge 10) {
            $patch = 0
            $minor++
            if ($minor -ge 10) {
                $minor = 0
                $major++
            }
        }
        $newVersion = "$major.$minor.$patch"
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

Write-Host "`n1. PyInstaller Build wird erstellt..." -ForegroundColor Yellow
& python -m PyInstaller PC-Konfigurator-Portable.spec --noconfirm

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller Build fehlgeschlagen!" -ForegroundColor Red
    exit 1
}

# Schritt 2: Post-Build-Aktionen
Write-Host "`n2. Post-Build-Aktionen werden ausgeführt..." -ForegroundColor Yellow
& python post_build.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Post-Build fehlgeschlagen!" -ForegroundColor Red
    exit 1
}


# Schritt 2b/2c: Datei-Vorlagen und Fonts in alle Build-Verzeichnisse unter dist kopieren
$quelleVorlagen = Join-Path $PSScriptRoot 'Datei-Vorlagen'
$quelleFonts = Join-Path $PSScriptRoot 'Fonts'
$buildDirs = Get-ChildItem dist -Directory
foreach ($dir in $buildDirs) {
    # Kopiere Datei-Vorlagen und Fonts direkt ins Build-Root
    $zielVorlagen = Join-Path $dir.FullName 'Datei-Vorlagen'
    $zielFonts = Join-Path $dir.FullName 'Fonts'
    if (Test-Path $quelleVorlagen) {
        Write-Host "Kopiere Datei-Vorlagen nach: $zielVorlagen" -ForegroundColor Yellow
        Copy-Item $quelleVorlagen $zielVorlagen -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Warnung: Datei-Vorlagen-Quellverzeichnis nicht gefunden: $quelleVorlagen" -ForegroundColor Red
    }
    if (Test-Path $quelleFonts) {
        Write-Host "Kopiere Fonts nach: $zielFonts" -ForegroundColor Yellow
        Copy-Item $quelleFonts $zielFonts -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "Warnung: Fonts-Quellverzeichnis nicht gefunden: $quelleFonts" -ForegroundColor Red
    }

    # --- NEU: Kopiere wichtige Dokumentationsdateien ---
    $docsToCopy = @('ANLEITUNG.md', 'BUILD-INFO.txt', 'README.md')
    foreach ($doc in $docsToCopy) {
        $srcDoc = Join-Path $PSScriptRoot $doc
        if (Test-Path $srcDoc) {
            $dstDoc = Join-Path $dir.FullName $doc
            Copy-Item $srcDoc $dstDoc -Force -ErrorAction SilentlyContinue
            Write-Host "Kopiere $doc nach: $dstDoc" -ForegroundColor Yellow
        } else {
            Write-Host "Warnung: $doc nicht gefunden!" -ForegroundColor Red
        }
    }

    # Nach dem Kopieren: Lösche Fonts, Datei-Vorlagen und Doku-Dateien aus _internal, falls vorhanden
    $internalPath = Join-Path $dir.FullName '_internal'
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

    # --- NEU: Setze logs-Ordner auf 'hidden' ---
    $logsDir = Join-Path $dir.FullName 'logs'
    if (-not (Test-Path $logsDir)) {
        try {
            New-Item -ItemType Directory -Path $logsDir | Out-Null
            Write-Host "Erstelle logs-Ordner: $logsDir" -ForegroundColor DarkGray
        } catch {
            Write-Host "Konnte logs-Ordner nicht erstellen: $logsDir ($_ )" -ForegroundColor Red
        }
    }
    if (Test-Path $logsDir) {
        try {
            (Get-Item $logsDir).Attributes = 'Hidden,Directory'
            Write-Host "Setze Attribut 'hidden' für: $logsDir" -ForegroundColor DarkGray
        } catch {
            Write-Host "Konnte Attribut 'hidden' nicht setzen: $logsDir ($_ )" -ForegroundColor Red
        }
    }
}

# Schritt 3: Erfolgsmeldung
Write-Host "`nBuild erfolgreich abgeschlossen!" -ForegroundColor Green

# Zeige Ergebnis
$buildDir = Get-ChildItem dist -Directory | Where-Object {$_.Name -like "PC-Konfigurator-Portable-v*"} | Sort-Object LastWriteTime | Select-Object -Last 1

if ($buildDir) {
    Write-Host "`nErgebnis:" -ForegroundColor Cyan
    Write-Host "Build-Verzeichnis: dist/$($buildDir.Name)" -ForegroundColor White
    $exeFile = Get-ChildItem "$($buildDir.FullName)\*.exe" | Select-Object -First 1
    if ($exeFile) {
        $sizeInMB = [Math]::Round($exeFile.Length / 1MB, 2)
        Write-Host "EXE-Datei: $($exeFile.Name) (${sizeInMB} MB)" -ForegroundColor White
    }
    
    # Zähle Inhalte
    $fonts = Get-ChildItem "$($buildDir.FullName)\Fonts" -Recurse -File -ErrorAction SilentlyContinue
    $templates = Get-ChildItem "$($buildDir.FullName)\Datei-Vorlagen" -Recurse -File -ErrorAction SilentlyContinue
    $docs = Get-ChildItem "$($buildDir.FullName)\*.md" -ErrorAction SilentlyContinue
    
    Write-Host "Fonts: $($fonts.Count) Dateien" -ForegroundColor White
    Write-Host "Templates: $($templates.Count) Dateien" -ForegroundColor White
    Write-Host "Dokumentation: $($docs.Count) Dateien" -ForegroundColor White
}