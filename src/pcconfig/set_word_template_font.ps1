param(
    [string]$TemplatePath,
    [string]$FontName = "Arial",
    [int]$FontSize = 11
)

Write-Host "[START] set_word_template_font.ps1 | TemplatePath: $TemplatePath | Font: $FontName | Size: $FontSize"

if (!(Test-Path $TemplatePath)) {
    Write-Error "Vorlage nicht gefunden: $TemplatePath"
    exit 1
}

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    try {
        $word.WindowState = 2  # wdWindowStateMinimize
        $word.Top = -10000
        $word.Left = -10000
    } catch {}
    $doc = $word.Documents.Open($TemplatePath, [ref]$false, [ref]$false)
    $stylesUpdated = 0
    foreach ($style in $doc.Styles) {
        try {
            if ($style.Type -eq 1 -or $style.Type -eq 2) {
                Write-Host "Setze Style: $($style.NameLocal) (Type: $($style.Type))"
                $style.Font.Name = $FontName
                $style.Font.Size = $FontSize
                $stylesUpdated++
            }
        } catch {
            Write-Host "Konnte Style $($style.NameLocal) nicht ändern: $_"
        }
    }
    $doc.Save()
    $doc.Close()
    $word.Quit()
    Write-Host "[SUCCESS] $stylesUpdated Formatvorlagen aktualisiert."
    exit 0
} catch {
    Write-Error "Fehler bei der COM-Automation: $_"
    try { $word.Quit() } catch {}
    exit 2
}
