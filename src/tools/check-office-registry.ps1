[CmdletBinding()]
param(
    [string[]]$OfficeVersions = @("16.0", "15.0", "14.0"),
    [switch]$AsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

class RegistryValueInfo {
    [string]$Group
    [string]$Path
    [string]$Name
    [object]$Expected
    [bool]$Exists
    [bool]$ValueFound
    [object]$Actual
    [bool]$IsCompliant
}

class PictureCandidateInfo {
    [string]$Path
    [string]$Name
    [object]$Value
}

class OfficeRegistrySummary {
    [string]$Timestamp
    [string]$CurrentUser
    [string]$CurrentUserSid
    [bool]$IsElevated
    [string[]]$OfficeVersionsChecked
    [int]$TotalChecks
    [int]$CompliantChecks
    [int]$MissingOrDifferentChecks
    [RegistryValueInfo[]]$Checks
    [PictureCandidateInfo[]]$PictureCandidateValues
    [string[]]$Notes
}

function Get-ExecutionContextInfo {
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = [System.Security.Principal.WindowsPrincipal]::new($identity)
    $isElevated = $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

    return [pscustomobject]@{
        CurrentUser = $identity.Name
        CurrentUserSid = $identity.User.Value
        IsElevated = [bool]$isElevated
    }
}

function Get-RegistryValueInfo {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $false)]$Expected,
        [Parameter(Mandatory = $false)][string]$Group = "General"
    )

    $exists = Test-Path -LiteralPath $Path
    $actual = $null
    $valueExists = $false

    if ($exists) {
        $item = Get-ItemProperty -LiteralPath $Path -ErrorAction SilentlyContinue
        if ($null -ne $item -and ($item.PSObject.Properties.Name -contains $Name)) {
            $actual = $item.$Name
            $valueExists = $true
        }
    }

    $info = [RegistryValueInfo]::new()
    $info.Group = $Group
    $info.Path = $Path
    $info.Name = $Name
    $info.Expected = $Expected
    $info.Exists = $exists
    $info.ValueFound = $valueExists
    $info.Actual = $actual
    $info.IsCompliant = ($valueExists -and $null -ne $Expected -and ([string]$actual -eq [string]$Expected))
    return $info
}

function Get-OpenPointPictureCandidates {
    param(
        [Parameter(Mandatory = $true)][string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }

    $patterns = @(
        'Picture',
        'Wrap',
        'Inline',
        'Insert',
        'Paste'
    )

    $key = Get-Item -LiteralPath $Path -ErrorAction SilentlyContinue
    if ($null -eq $key) {
        return @()
    }

    $candidates = foreach ($name in $key.GetValueNames()) {
        $hasPatternHit = $false
        foreach ($pattern in $patterns) {
            if ([string]::IsNullOrWhiteSpace($pattern)) {
                continue
            }
            if ($name.IndexOf($pattern, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $hasPatternHit = $true
                break
            }
        }

        if ($hasPatternHit) {
            $candidate = [PictureCandidateInfo]::new()
            $candidate.Path = $Path
            $candidate.Name = $name
            $candidate.Value = $key.GetValue($name)
            $candidate
        }
    }

    return @($candidates)
}

$checks = @()
$pictureCandidates = @()

foreach ($version in $OfficeVersions) {
    $wordOptionsPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Office\$version\Word\Options"
    $excelOptionsPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Office\$version\Excel\Options"
    $outlookOptionsPath = "Registry::HKEY_CURRENT_USER\Software\Microsoft\Office\$version\Outlook\Options"

    # Word: aktive Sollwerte aus PC-Konfigurator + offene Punkte
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'CorrectSentenceCaps' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatAsYouTypeApplyBulletedLists' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatAsYouTypeApplyNumberedLists' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatApplyBulletedLists' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatApplyNumberedLists' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatCapitalizeTableCells' -Expected 0 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'PictureInsertLayout' -Expected 1 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'AutoFormatAsYouTypeReplaceQuotes' -Expected 1 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'PasteFormattingOtherApp' -Expected 2 -Group "Word"
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'PasteFormattingTwoDocumentsNoStyles' -Expected 1 -Group "Word"

    # Offener Punkt: Key ist im Konfigurator gesetzt; hier nur noch Sichtprüfung
    $checks += Get-RegistryValueInfo -Path $wordOptionsPath -Name 'CorrectTableCells' -Expected 0 -Group "Word-OpenPoint"

    # Excel
    $checks += Get-RegistryValueInfo -Path $excelOptionsPath -Name 'CorrectSentenceCap' -Expected 0 -Group "Excel"
    $checks += Get-RegistryValueInfo -Path $excelOptionsPath -Name 'AutoSaveInterval' -Expected 5 -Group "Excel"

    # Outlook
    $checks += Get-RegistryValueInfo -Path $outlookOptionsPath -Name 'NewMailFont' -Expected 'Aptos' -Group "Outlook"
    $checks += Get-RegistryValueInfo -Path $outlookOptionsPath -Name 'NewMailFontSize' -Expected 11 -Group "Outlook"
    $checks += Get-RegistryValueInfo -Path $outlookOptionsPath -Name 'ReplyForwardFont' -Expected 'Aptos' -Group "Outlook"
    $checks += Get-RegistryValueInfo -Path $outlookOptionsPath -Name 'ReplyForwardFontSize' -Expected 11 -Group "Outlook"
    $checks += Get-RegistryValueInfo -Path $outlookOptionsPath -Name 'DefaultMailFont' -Expected 'Aptos' -Group "Outlook"

    # Bild-Layout ist jetzt im Konfigurator hinterlegt; die Kandidatensuche bleibt ergänzend.
    $pictureCandidates += Get-OpenPointPictureCandidates -Path $wordOptionsPath
}

$summary = [OfficeRegistrySummary]::new()
$contextInfo = Get-ExecutionContextInfo
$summary.Timestamp = (Get-Date).ToString("s")
$summary.CurrentUser = [string]$contextInfo.CurrentUser
$summary.CurrentUserSid = [string]$contextInfo.CurrentUserSid
$summary.IsElevated = [bool]$contextInfo.IsElevated
$summary.OfficeVersionsChecked = $OfficeVersions
$summary.TotalChecks = $checks.Count
$summary.CompliantChecks = @($checks | Where-Object { $_.Expected -ne $null -and $_.IsCompliant }).Count
$summary.MissingOrDifferentChecks = @($checks | Where-Object { $_.Expected -ne $null -and -not $_.IsCompliant }).Count
$summary.Checks = @($checks)
$summary.PictureCandidateValues = @($pictureCandidates)
$summary.Notes = @(
    "CorrectTableCells und Bild-Einfügeoption sind als offene Validierungspunkte markiert.",
    "PictureInsertLayout wird im Konfigurator aktiv gesetzt; finale Verifikation weiterhin zusätzlich in der Office-GUI vornehmen."
)

if ($AsJson) {
    $summary | ConvertTo-Json -Depth 6
    return
}

Write-Host "=== Office Registry Check (PC-Konfigurator) ==="
Write-Host "Zeit: $($summary.Timestamp)"
Write-Host "Benutzer: $($summary.CurrentUser)"
Write-Host "SID: $($summary.CurrentUserSid)"
Write-Host "Erhöht gestartet: $($summary.IsElevated)"
Write-Host "Versionen: $($OfficeVersions -join ', ')"
Write-Host ""

$checks |
    Select-Object Group, Name, Expected, Actual, IsCompliant, ValueFound, Path |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Treffer: $($summary.CompliantChecks)/$($summary.TotalChecks)"

if ($pictureCandidates.Count -gt 0) {
    Write-Host ""
    Write-Host "Mögliche Bild-/Einfüge-Kandidaten (manuelle Sichtprüfung):"
    $pictureCandidates |
        Select-Object Name, Value, Path |
        Sort-Object Name -Unique |
        Format-Table -AutoSize
}
else {
    Write-Host ""
    Write-Host "Keine offensichtlichen Bild-/Einfüge-Kandidaten in den geprüften Word-Options gefunden."
}

Write-Host ""
Write-Host "Hinweis: Offene Punkte (CorrectTableCells/Bild-Einfügen) sollten zusätzlich in der Office-GUI geprüft werden."
