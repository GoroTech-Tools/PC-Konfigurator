param(
    [string]$TemplatePath,
    [string]$FontName = "Arial",
    [int]$FontSize = 10
)

Write-Host "[START] set_excel_template_font.ps1 | TemplatePath: $TemplatePath | Font: $FontName | Size: $FontSize"

if (!(Test-Path $TemplatePath)) {
    Write-Error "Vorlage nicht gefunden: $TemplatePath"
    exit 1
}

try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    try {
        $excel.WindowState = -2  # xlMinimized
        $excel.Top = -10000
        $excel.Left = -10000
    } catch {}
    $workbook = $excel.Workbooks.Open($TemplatePath)
    $worksheet = $workbook.Worksheets.Item(1)
    Write-Host "Setze Font für Blatt: $($worksheet.Name)"
    $worksheet.Cells.Font.Name = $FontName
    $worksheet.Cells.Font.Size = $FontSize
    $xlOpenXMLTemplate = 52
    $workbook.SaveAs($TemplatePath, $xlOpenXMLTemplate)
    $workbook.Close($false)
    $excel.Quit()
    Write-Host "[SUCCESS] Excel-Template erfolgreich angepasst: $TemplatePath ($FontName, $FontSize)"
    exit 0
} catch {
    Write-Error "Fehler beim Anpassen des Excel-Templates: $_"
    try { $excel.Quit() } catch {}
    exit 1
}
