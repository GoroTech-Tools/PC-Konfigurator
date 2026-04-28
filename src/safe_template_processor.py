"""
Sichere Office Template Verarbeitung mit COM-Automation
=======================================================

Diese Klasse verwendet Office COM-Automation für professionelle Template-Bearbeitung.
"""

import win32com.client
import pythoncom
from pathlib import Path
import logging
import time


class SafeTemplateProcessor:
    """Sichere Template-Verarbeitung mit Office COM-Automation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def update_word_template_safely(self, template_path, font_name, font_size):
        """
        Aktualisiert Word-Template über COM-Automation
        
        Args:
            template_path: Pfad zum Word-Template
            font_name: Neue Schriftart
            font_size: Neue Schriftgröße
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        import gc
        import subprocess
        import time
        doc = None
        word = None
        try:
            self.logger.info(f"Öffne Word-Template über COM: {template_path}")
            pythoncom.CoInitialize()
            try:
                word = win32com.client.GetActiveObject("Word.Application")
        """
                self.logger.debug("Verwende bestehende Word-Instanz")
            except Exception:
                word = win32com.client.Dispatch("Word.Application")
                self.logger.debug("Neue Word-Instanz gestartet")
            word.Visible = False
            word.DisplayAlerts = 0  # Keine Dialoge
        import subprocess
            doc = word.Documents.Open(str(template_path))
            styles_updated = 0
            for style in doc.Styles:
                try:
                    if style.Type == 1 or style.Type == 2:
                        style.Font.Name = font_name
                        style.Font.Size = font_size
                        styles_updated += 1
                        self.logger.debug(f"Style aktualisiert: {style.NameLocal}")
                except Exception as style_error:
                    self.logger.debug(f"Style {style.NameLocal} konnte nicht geändert werden: {style_error}")
                    continue
            self.logger.info(f"Word-Template: {styles_updated} Formatvorlagen mit {font_name} {font_size}pt aktualisiert")
            doc.Save()
        except Exception as e:
            self.logger.error(f"Fehler bei Word COM-Automation: {e}")
            self.logger.info("Fallback: Verwende PowerShell COM-Konfiguration (wie PC-Konfigurator.ps1)")
            try:
                if doc:
                    doc.Close(SaveChanges=False)
                if word:
                    word.Quit()
                pythoncom.CoUninitialize()
                gc.collect()
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler beim Beenden von Word/COM: {cleanup_error}")
                subprocess.run(["taskkill", "/f", "/im", "winword.exe"], capture_output=True, check=False)
            powershell_success = self._modify_template_via_powershell(template_path, font_name, font_size, 'word')
            registry_success = self._configure_word_fonts_via_registry(font_name, font_size)
            return powershell_success or registry_success
        finally:
            try:
                if doc:
                    doc.Close(SaveChanges=False)
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler beim Schließen des Dokuments: {cleanup_error}")
            try:
                if word:
                    word.Quit()
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler beim Beenden von Word: {cleanup_error}")
            try:
                pythoncom.CoUninitialize()
                gc.collect()
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler beim COM-Cleanup: {cleanup_error}")
            # Notfall: Taskkill, falls Word-Prozess noch lebt
            try:
                time.sleep(2)
                subprocess.run(["taskkill", "/f", "/im", "winword.exe"], capture_output=True, check=False)
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler bei Taskkill: {cleanup_error}")
        self.logger.info(f"Word-Template erfolgreich über COM aktualisiert: {template_path}")
        return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Word COM-Automation: {e}")
            self.logger.info("Fallback: Verwende PowerShell COM-Konfiguration (wie PC-Konfigurator.ps1)")
            
            try:
                # Cleanup im Fehlerfall
                if 'doc' in locals():
                    doc.Close(SaveChanges=False)
                if 'word' in locals():
                    word.Quit()
                pythoncom.CoUninitialize()
            except Exception:$([char]10)                passpass
            
            # PowerShell-Fallback für direkte Word Template-Modifikation
            powershell_success = self._modify_template_via_powershell(template_path, font_name, font_size, 'word')
            
            # Registry-Fallback als zusätzliche Sicherheit
            registry_success = self._configure_word_fonts_via_registry(font_name, font_size)
            
            return powershell_success or registry_success
    
    def update_excel_template_safely(self, template_path, font_name, font_size):
        """
        Aktualisiert Excel-Template über COM-Automation
        
        Args:
            template_path: Pfad zum Excel-Template
            font_name: Neue Schriftart
            font_size: Neue Schriftgröße
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            self.logger.info(f"Öffne Excel-Template über COM: {template_path}")
            
            # COM initialisieren
            pythoncom.CoInitialize()
            
            # Excel starten - erst versuchen bestehende Instanz zu verwenden, sonst neue erstellen
            try:
                excel = win32com.client.GetActiveObject("Excel.Application")
                self.logger.debug("Verwende bestehende Excel-Instanz")
            except Exception:
                excel = win32com.client.Dispatch("Excel.Application")
                self.logger.debug("Neue Excel-Instanz gestartet")
            
            excel.Visible = False
            excel.DisplayAlerts = False
            
            # ROBUST: Altes Template löschen und neu erstellen (wie PC-Konfigurator.ps1)
            try:
                import os
                if os.path.exists(template_path):
                    os.remove(template_path)
                    self.logger.debug(f"Altes Template gelöscht: {template_path}")
            except Exception as delete_error:
                self.logger.debug(f"Template löschen fehlgeschlagen: {delete_error}")
            
            # Excel StandardFont setzen
            excel.StandardFont = font_name
            excel.StandardFontSize = font_size
            self.logger.debug(f"Excel StandardFont gesetzt: {font_name} {font_size}pt")
            
            # Neue leere Arbeitsmappe erstellen
            workbook = excel.Workbooks.Add()
            
            # KRITISCH: Normal-Style für Template setzen
            normal_style = workbook.Styles.Item("Normal")
            normal_style.Font.Name = font_name
            normal_style.Font.Size = font_size
            self.logger.debug(f"Template Normal-Style gesetzt: {font_name} {font_size}pt")
            
            # Erstes Arbeitsblatt formatieren
            worksheet = workbook.Worksheets.Item(1)
            worksheet.Cells.Font.Name = font_name
            worksheet.Cells.Font.Size = font_size
            
            worksheets_updated = 1
            self.logger.info(f"Excel-Template: {worksheets_updated} Arbeitsblätter mit {font_name} {font_size}pt aktualisiert")
            
            # Als Excel Template (.xltx) speichern - FileFormat 54 für Template!
            workbook.SaveAs(str(template_path), FileFormat=54)
            self.logger.debug("Neues Excel-Template als XLTX-Format gespeichert")
            
            # Arbeitsmappe schließen
            workbook.Close(False)
            excel.Quit()
            
            # COM cleanup mit Wartezeit für vollständiges Beenden
            import time
            time.sleep(2)  # 2 Sekunden warten
            pythoncom.CoUninitialize()
            
            # Sicherstellen, dass Excel-Prozesse beendet sind
            import subprocess
            try:
                subprocess.run(["taskkill", "/f", "/im", "excel.exe"], 
                             capture_output=True, check=False)
            except Exception:$([char]10)                passpass
            
            self.logger.info(f"Excel-Template erfolgreich über COM aktualisiert: {template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei Excel COM-Automation: {e}")
            self.logger.info("Fallback: Verwende Direkte Template-Kopie + Registry")
            
            try:
                # Cleanup im Fehlerfall
                if 'workbook' in locals():
                    workbook.Close(SaveChanges=False)
                if 'excel' in locals():
                    excel.Quit()
                pythoncom.CoUninitialize()
            except Exception:$([char]10)                passpass
            
            # PowerShell COM-Fallback (wie PC-Konfigurator.ps1)
            powershell_success = self._modify_template_via_powershell(template_path, font_name, font_size, 'excel')
            
            # Registry-Fallback als zusätzliche Sicherheit
            registry_success = self._configure_excel_fonts_via_registry(font_name, font_size)
            
            return powershell_success or registry_success
    
    def _verify_template_integrity(self, template_path):
        """Überprüft die Integrität einer Template-Datei"""
        try:
            template_name = template_path.name.lower()
            self.logger.debug(f"Prüfe Integrität von Template: {template_name}")
            
            # Für Backup-Dateien die ursprüngliche Endung ermitteln
            if template_name.endswith('.safe_backup'):
                # Entferne .safe_backup und verwende die vorherige Endung
                original_name = template_path.stem
                template_suffix = Path(original_name).suffix.lower()
                self.logger.debug(f"Backup-Datei erkannt, ursprüngliche Endung: {template_suffix}")
            else:
                template_suffix = template_path.suffix.lower()
            
            with zipfile.ZipFile(template_path, 'r') as zip_ref:
                # ZIP-Struktur testen
                bad_file = zip_ref.testzip()
                if bad_file:
                    self.logger.error(f"Beschädigte ZIP-Datei gefunden: {bad_file}")
                    return False
                    
                # Wichtige Dateien prüfen
                file_list = zip_ref.namelist()
                self.logger.debug(f"Template enthält {len(file_list)} Dateien")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Template-Integrität fehlerhaft: {e}")
            return False
    
    def verify_template_accessibility(self, template_path):
        """
        Überprüft, ob ein Template über COM zugänglich ist
        
        Args:
            template_path: Pfad zum Template
            
        Returns:
            bool: True wenn zugänglich, False sonst
        """
        try:
            template_path = Path(template_path)
            
            if not template_path.exists():
                return False
                
            # Teste je nach Template-Typ
            if template_path.suffix.lower() in ['.dotm', '.dotx']:
                return self._test_word_access(template_path)
            elif template_path.suffix.lower() in ['.xltx', '.xltm']:
                return self._test_excel_access(template_path)
            else:
                return False
                
        except Exception as e:
            self.logger.debug(f"Template-Zugriffstest fehlgeschlagen: {e}")
            return False
    
    def _test_word_access(self, template_path):
        """Testet Word-Template-Zugriff"""
        try:
            pythoncom.CoInitialize()
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            
            doc = word.Documents.Open(str(template_path))
            doc.Close(SaveChanges=False)
            word.Quit()
            pythoncom.CoUninitialize()
            
            return True
        except Exception:
            try:
                if 'doc' in locals():
                    doc.Close(SaveChanges=False)
                if 'word' in locals():
                    word.Quit()
                pythoncom.CoUninitialize()
            except Exception:$([char]10)                passpass
            return False
    
    def _test_excel_access(self, template_path):
        """Testet Excel-Template-Zugriff"""
        try:
            pythoncom.CoInitialize()
            
            try:
                excel = win32com.client.GetActiveObject("Excel.Application")
            except Exception:
                excel = win32com.client.Dispatch("Excel.Application")
                
            excel.Visible = False
            excel.DisplayAlerts = False
            
            workbook = excel.Workbooks.Open(str(template_path))
            workbook.Close(SaveChanges=False)
            excel.Quit()
            pythoncom.CoUninitialize()
            
            return True
        except Exception:
            try:
                if 'workbook' in locals():
                    workbook.Close(SaveChanges=False)
                if 'excel' in locals():
                    excel.Quit()
                pythoncom.CoUninitialize()
            except Exception:$([char]10)                passpass
            return False
    
    def _configure_word_fonts_via_registry(self, font_name, font_size):
        """Registry-basierte Word Font-Konfiguration als Fallback"""
        try:
            import winreg
            
            # Word Default Font Registry-Pfad
            word_key_path = r"SOFTWARE\Microsoft\Office\16.0\Word\Options"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, word_key_path, 0, winreg.KEY_SET_VALUE):
                    pass
                registry_root = winreg.HKEY_CURRENT_USER
            except Exception:
                # Fallback zu HKEY_LOCAL_MACHINE
                registry_root = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.CreateKey(registry_root, word_key_path) as key:
                winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, font_name)
                winreg.SetValueEx(key, "DefaultFontSize", 0, winreg.REG_DWORD, font_size)
            
            self.logger.info(f"Word Font via Registry konfiguriert: {font_name} {font_size}pt")
            return True
            
        except Exception as e:
            self.logger.error(f"Registry-Fallback für Word fehlgeschlagen: {e}")
            return False
    
    def _configure_excel_fonts_via_registry(self, font_name, font_size):
        """Registry-basierte Excel Font-Konfiguration als Fallback"""
        try:
            import winreg
            
            # Excel Default Font Registry-Pfad
            excel_key_path = r"SOFTWARE\Microsoft\Office\16.0\Excel\Options"
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, excel_key_path, 0, winreg.KEY_SET_VALUE):
                    pass
                registry_root = winreg.HKEY_CURRENT_USER
            except Exception:
                # Fallback zu HKEY_LOCAL_MACHINE
                registry_root = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.CreateKey(registry_root, excel_key_path) as key:
                winreg.SetValueEx(key, "DefaultFont", 0, winreg.REG_SZ, font_name)
                winreg.SetValueEx(key, "DefaultFontSize", 0, winreg.REG_DWORD, font_size)
            
            self.logger.info(f"Excel Font via Registry konfiguriert: {font_name} {font_size}pt")
            return True
        
        except Exception as e:
            self.logger.error(f"Registry Excel-Konfiguration fehlgeschlagen: {e}")
            return False
    
    def _touch_template_file(self, template_path):
        """
        Aktualisiert den Zeitstempel einer Template-Datei auf aktuelle Zeit
        
        Args:
            template_path: Pfad zur Template-Datei
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            import os
            import time
            from pathlib import Path
            
            if not Path(template_path).exists():
                self.logger.error(f"Template-Datei nicht gefunden: {template_path}")
                return False
            
            # Zeitstempel auf aktuelle Zeit setzen
            current_time = time.time()
            os.utime(template_path, (current_time, current_time))
            
            self.logger.info(f"Template-Zeitstempel aktualisiert: {template_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Template-Zeitstempel-Update fehlgeschlagen: {e}")
            return False
    
    def _modify_template_via_powershell(self, template_path, font_name, font_size, template_type):
        """
        Excel/Word-Konfiguration über PowerShell COM (wie PC-Konfigurator.ps1)
        Verwendet StandardFont-Properties statt Template-Manipulation
        
        Args:
            template_path: Pfad zur Template-Datei (wird nicht direkt modifiziert)
            font_name: Neue Schriftart
            font_size: Neue Schriftgröße
            template_type: 'excel' oder 'word'
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            import subprocess
            from pathlib import Path
            
            if template_type == 'excel':
                # Excel Template robust neu erstellen (bewährte Methode)
                ps_script = f"""
$excel = New-Object -ComObject Excel.Application -ErrorAction Stop
$excel.Visible = $false
$excel.DisplayAlerts = $false
try {{
    # Excel StandardFont setzen
    $excel.StandardFont = '{font_name}'
    $excel.StandardFontSize = {font_size}
    Write-Host "Excel StandardFont gesetzt: $($excel.StandardFont) $($excel.StandardFontSize)pt"
    
    # Template-Pfad definieren
    $templatePath = '{str(template_path).replace(chr(92), chr(92)*2)}'
    
    # Altes Template löschen
    Remove-Item $templatePath -Force -ErrorAction SilentlyContinue
    Write-Host "Altes Template gelöscht: $templatePath"
    
    # Neue Arbeitsmappe erstellen
    $newWorkbook = $excel.Workbooks.Add()
    
    # KRITISCH: Normal-Style für Template setzen
    $normalStyle = $newWorkbook.Styles.Item("Normal")
    $normalStyle.Font.Name = '{font_name}'
    $normalStyle.Font.Size = {font_size}
    Write-Host "Normal-Style gesetzt: $($normalStyle.Font.Name) $($normalStyle.Font.Size)pt"
    
    # Arbeitsblatt formatieren
    $worksheet = $newWorkbook.Worksheets.Item(1)
    $worksheet.Cells.Font.Name = '{font_name}'
    $worksheet.Cells.Font.Size = {font_size}
    
    # Als Excel Template speichern (FileFormat 54)
    $newWorkbook.SaveAs($templatePath, 54)
    $newWorkbook.Close($false)
    
    Write-Host "✅ Template erfolgreich erstellt mit $($normalStyle.Font.Name) $($normalStyle.Font.Size)pt"
    exit 0
}} catch {{
    Write-Host "❌ PowerShell Excel COM Fehler: $_"
    exit 1
}} finally {{
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}}
"""
            elif template_type == 'word':
                # Word Standard-Font setzen
                ps_script = f"""
$word = New-Object -ComObject Word.Application -ErrorAction Stop
$word.Visible = $false
try {{
    # Neues Dokument erstellen
    $doc = $word.Documents.Add()
    
    # Normal-Style modifizieren
    $normalStyle = $doc.Styles.Item("Normal")
    $normalStyle.Font.Name = '{font_name}'
    $normalStyle.Font.Size = {font_size}
    
    # Als Template speichern
    $templatePath = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\\Templates\\Normal.dotm')
    Remove-Item $templatePath -Force -ErrorAction SilentlyContinue
    $doc.SaveAs2($templatePath, 15) # Word Template Format
    $doc.Close()
    
    Write-Host "Word Template erfolgreich erstellt mit $($normalStyle.Font.Name) $($normalStyle.Font.Size)pt"
    exit 0
}} catch {{
    Write-Host "PowerShell Word COM Fehler: $_"
    exit 1
}} finally {{
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}}
"""
            else:
                self.logger.error(f"Unbekannter Template-Typ: {template_type}")
                return False
            
            # PowerShell-Skript ausführen
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=90  # Längerer Timeout für Template-Erstellung
            )
            
            if result.returncode == 0:
                self.logger.info(f"Template via PowerShell COM erstellt: {template_type} ({font_name} {font_size}pt)")
                return True
            else:
                self.logger.error(f"PowerShell Template-Erstellung fehlgeschlagen: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"PowerShell Template-Erstellung Fehler: {e}")
            return False
    
    def _modify_excel_template_direct(self, template_path, font_name, font_size):
        """
        Modifiziert Excel Template durch direkte ZIP/XML-Manipulation
        """
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            import tempfile
            import shutil
            import time
            import os
            from pathlib import Path
            
            template_path = Path(template_path)
            
            # Temporären Ordner für ZIP-Extraktion erstellen
            with tempfile.TemporaryDirectory() as temp_dir:
            # Vor jedem Versuch: WINWORD.EXE-Prozesse killen
            kill_winword()
            for attempt in range(2):
                try:
                    word = win32com.client.DispatchEx("Word.Application")
                    word.Visible = False
                    doc = word.Documents.Open(template_path, ReadOnly=False)
                    # ...
                    doc.Save()
                    doc.Close(False)
                    word.Quit()
                    pythoncom.CoUninitialize()
                    self.logger.info(f"Word-Template erfolgreich modifiziert: {template_path}")
                    return True
                except Exception as e:
                    self.logger.error(f"Fehler bei Word COM-Automation (Versuch {attempt+1}): {e}")
                    kill_winword()
                    if attempt == 0:
                        self.logger.info("Erneuter Versuch in 2 Sekunden...")
                        time.sleep(2)
                    else:
                        self.logger.info("Fallback: Verwende PowerShell COM-Konfiguration (wie PC-Konfigurator.ps1)")
                        return modify_word_template_powershell(template_path, font_name, font_size)
                temp_path = Path(temp_dir)
                
                # Excel Template als ZIP extrahieren
                with zipfile.ZipFile(template_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Styles.xml modifizieren (enthält Normal-Style)
                styles_path = temp_path / 'xl' / 'styles.xml'
                if styles_path.exists():
                    tree = ET.parse(styles_path)
                    root = tree.getroot()
                    
                    # Excel Namespace
                    ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    # Fonts-Section finden und Normal-Font aktualisieren
                    fonts_elem = root.find('.//fonts', ns)
                    if fonts_elem is not None:
                        for font in fonts_elem.findall('font', ns):
                            # Normal-Font ist meist der erste Font
                            name_elem = font.find('name', ns)
                            size_elem = font.find('sz', ns)
                            
                            if name_elem is not None:
                                name_elem.set('val', font_name)
                            if size_elem is not None:
                                size_elem.set('val', str(font_size))
                            
                            # Nur ersten Font modifizieren (Normal-Style)
                            break
                    
                    # Modifizierte styles.xml speichern
    def kill_winword():
        """Beendet alle laufenden WINWORD.EXE-Prozesse (hart)."""
        try:
            subprocess.run(["taskkill", "/IM", "WINWORD.EXE", "/F"], check=False, capture_output=True)
        except Exception as e:
            pass
                    tree.write(styles_path, encoding='utf-8', xml_declaration=True)
                    self.logger.info(f"Excel styles.xml modifiziert: {font_name} {font_size}pt")
                
                # Neues Template erstellen
                backup_path = template_path.with_suffix(template_path.suffix + '.backup')
                if template_path.exists():
                    shutil.move(template_path, backup_path)
                
                # Modifizierte Dateien zu neuem ZIP zusammenfassen
                with zipfile.ZipFile(template_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_ref.write(file_path, arcname)
                
                # Zeitstempel aktualisieren
                current_time = time.time()
                os.utime(template_path, (current_time, current_time))
                
                self.logger.info(f"Excel Template erfolgreich modifiziert: {template_path} ({font_name} {font_size}pt)")
                return True
                
        except Exception as e:
            self.logger.error(f"Excel Template ZIP-Modifikation fehlgeschlagen: {e}")
            return False
    
    def _modify_word_template_direct(self, template_path, font_name, font_size):
        """
        Modifiziert Word Template durch direkte ZIP/XML-Manipulation
        """
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            import tempfile
            import shutil
            import time
            import os
            from pathlib import Path
            
            template_path = Path(template_path)
            
            # Temporären Ordner für ZIP-Extraktion erstellen
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Word Template als ZIP extrahieren
                with zipfile.ZipFile(template_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # styles.xml modifizieren (enthält alle Styles)
                styles_path = temp_path / 'word' / 'styles.xml'
                if styles_path.exists():
                    tree = ET.parse(styles_path)
                    root = tree.getroot()
                    
                    # Word Namespace
                    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    
                    # Normal-Style finden und modifizieren
                    for style in root.findall('.//w:style[@w:styleId="Normal"]', ns):
                        rPr = style.find('.//w:rPr', ns)
                        if rPr is not None:
                            # Font name setzen
                            rFonts = rPr.find('w:rFonts', ns)
                            if rFonts is None:
                                rFonts = ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
                            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii', font_name)
                            rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi', font_name)
                            
                            # Font size setzen
                            sz = rPr.find('w:sz', ns)
                            if sz is None:
                                sz = ET.SubElement(rPr, '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz')
                            sz.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', str(font_size * 2))  # Word verwendet halbe Punkte
                    
                    # Modifizierte styles.xml speichern
                    tree.write(styles_path, encoding='utf-8', xml_declaration=True)
                    self.logger.info(f"Word styles.xml modifiziert: {font_name} {font_size}pt")
                
                # Neues Template erstellen
                backup_path = template_path.with_suffix(template_path.suffix + '.backup')
                if template_path.exists():
                    shutil.move(template_path, backup_path)
                
                # Modifizierte Dateien zu neuem ZIP zusammenfassen
                with zipfile.ZipFile(template_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                    for file_path in temp_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_path)
                            zip_ref.write(file_path, arcname)
                
                # Zeitstempel aktualisieren
                current_time = time.time()
                os.utime(template_path, (current_time, current_time))
                
                self.logger.info(f"Word Template erfolgreich modifiziert: {template_path} ({font_name} {font_size}pt)")
                return True
                
        except Exception as e:
            self.logger.error(f"Word Template ZIP-Modifikation fehlgeschlagen: {e}")
            return False
    
    def _fallback_copy_template_with_current_timestamp(self, template_path, destination_path):
        """
        Einfacher Fallback: Kopiert Template und setzt aktuellen Zeitstempel
        
        Args:
            template_path: Pfad zur Quell-Template
            destination_path: Ziel-Pfad für Template
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            import shutil
            import os
            import time
            from pathlib import Path
            
            source_path = Path(template_path)
            dest_path = Path(destination_path)
            
            if not source_path.exists():
                self.logger.error(f"Quell-Template nicht gefunden: {source_path}")
                return False
            
            # Zielverzeichnis erstellen falls nicht vorhanden
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Template kopieren
            shutil.copy2(source_path, dest_path)
            
            # Zeitstempel auf aktuelle Zeit setzen
            current_time = time.time()
            os.utime(dest_path, (current_time, current_time))
            
            self.logger.info(f"Template als Fallback kopiert mit aktuellem Zeitstempel: {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fallback Template-Kopie fehlgeschlagen: {e}")
            return False