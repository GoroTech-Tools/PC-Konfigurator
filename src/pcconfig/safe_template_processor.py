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

    def update_excel_template_safely(self, template_path, font_name, font_size):
        """
        Aktualisiert Excel-Template (.xltx) über COM-Automation
        Setzt DisplayAlerts = False, um Nachfragen zu unterdrücken.
        Löscht ggf. Mappe.xlsx im Zielverzeichnis, um Dialoge zu verhindern.
        Kopiert nach Anpassung ins Benutzerverzeichnis.
        """
        import gc
        import subprocess
        import time
        import pythoncom
        import win32com.client
        import os
        import glob
        import sys
        template_path = str(Path(template_path).resolve())
        excel = None
        wb = None
        try:
            self.logger.info(f"Öffne Excel-Template über COM: {template_path}")
            pythoncom.CoInitialize()
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            # Fenster außerhalb des sichtbaren Bereichs positionieren (verhindert Aufblitzen)
            try:
                excel.WindowState = -2  # xlMinimized
                excel.Top = -10000
                excel.Left = -10000
            except Exception:
                pass
            excel.DisplayAlerts = False  # Keine Nachfragen beim Überschreiben
            wb = excel.Workbooks.Open(template_path, ReadOnly=False)
            ws = wb.Worksheets(1)
            ws.Cells.Font.Name = font_name
            ws.Cells.Font.Size = font_size
            wb.Save()
            wb.Close(False)
            excel.DisplayAlerts = True  # Dialoge wieder aktivieren
            excel.Quit()
            pythoncom.CoUninitialize()
            # Nach Anpassung: Alle Mappe*.xlsx im Zielverzeichnis löschen (Dialog-Prävention)
            xlstart = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART"
            try:
                for f in glob.glob(str(xlstart / "Mappe*.xlsx")):
                    try:
                        os.remove(f)
                        self.logger.info(f"Alte Datei im Zielverzeichnis gelöscht: {f}")
                    except Exception as e:
                        self.logger.warning(f"Konnte {f} nicht löschen: {e}")
            except Exception as e:
                self.logger.warning(f"Fehler beim Löschen von Mappe*.xlsx: {e}")
            # Nach Anpassung: Mappe.xltx ins Benutzerverzeichnis kopieren
            try:
                target = xlstart / "Mappe.xltx"
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                from shutil import copy2
                copy2(template_path, target)
                self.logger.info(f"Mappe.xltx ins Benutzerverzeichnis kopiert: {target}")
            except Exception as e:
                self.logger.error(f"Fehler beim Kopieren von Mappe.xltx ins Benutzerverzeichnis: {e}")
            return True
        except Exception as e:
            self.logger.error(f"Fehler bei Excel COM-Automation: {e}")
            try:
                if wb:
                    wb.Close(False)
                if excel:
                    excel.Quit()
                pythoncom.CoUninitialize()
                gc.collect()
            except Exception as cleanup_error:
                self.logger.warning(f"Fehler beim Beenden von Excel/COM: {cleanup_error}")
                creationflags = 0x08000000 if sys.platform == "win32" else 0
                subprocess.run(["taskkill", "/f", "/im", "excel.exe"], capture_output=True, check=False, creationflags=creationflags)
            return False

    def get_word_template_font_info(self, template_path):
        """Liest die Schriftart und -größe aus einer Word-Template-Datei (Normal.dotm, NormalEmail.dotm) aus."""
        import win32com.client
        import pythoncom
        from pathlib import Path
        template_path = str(Path(template_path).resolve())
        pythoncom.CoInitialize()
        word = None
        try:
            word = win32com.client.DispatchEx("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(template_path, ReadOnly=True)
            style = doc.Styles("Standard")
            font_name = style.Font.Name
            font_size = style.Font.Size
            doc.Close(False)
            return {"font_name": font_name, "font_size": font_size}
        except Exception as e:
            raise RuntimeError(f"Fehler beim Auslesen der Schriftart/-größe: {e}")
        finally:
            if word:
                word.Quit()
            pythoncom.CoUninitialize()

    def _kill_office_processes(self):
        """Beendet alle relevanten Office-Prozesse (Word, Excel, Outlook)."""
        import subprocess
        procs = ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE"]
        for proc in procs:
            try:
                self.logger.info(f"Beende ggf. laufenden Prozess: {proc}")
                subprocess.run(["taskkill", "/IM", proc, "/F"], check=False, capture_output=True)
            except Exception as e:
                self.logger.warning(f"Konnte {proc} nicht beenden: {e}")

    def _modify_template_via_powershell(self, template_path, font_name, font_size, app):
        self._kill_office_processes()
        import subprocess
        import sys
        from pathlib import Path
        ps_script = Path(__file__).parent / "set_word_template_font.ps1"
        if not ps_script.exists():
            self.logger.error(f"PowerShell-Skript nicht gefunden: {ps_script}")
            return False
        cmd = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps_script),
            "-TemplatePath", str(template_path),
            "-FontName", str(font_name),
            "-FontSize", str(font_size)
        ]
        self.logger.info(f"Starte PowerShell-Fallback: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            stdout = result.stdout.strip() if result.stdout else "(keine Ausgabe)"
            stderr = result.stderr.strip() if result.stderr else "(keine Fehlerausgabe)"
            if result.returncode == 0:
                self.logger.info(f"PowerShell-Fallback erfolgreich: {stdout}")
                return True
            else:
                self.logger.error(f"PowerShell-Fallback fehlgeschlagen: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Fehler beim PowerShell-Fallback: {e}")
            return False
    """Sichere Template-Verarbeitung mit Office COM-Automation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def update_word_template_safely(self, template_path, font_name, font_size):
        self._kill_office_processes()
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
            self.logger.info(f"Öffne Word-Template über COM: {template_path} | Font: {font_name} | Size: {font_size}")
            pythoncom.CoInitialize()
            try:
                word = win32com.client.GetActiveObject("Word.Application")
                self.logger.debug("Verwende bestehende Word-Instanz")
            except Exception as getactive_error:
                self.logger.debug(f"GetActiveObject fehlgeschlagen: {getactive_error}")
                word = win32com.client.Dispatch("Word.Application")
                self.logger.debug("Neue Word-Instanz gestartet")
            word.Visible = False
            # Fenster außerhalb des sichtbaren Bereichs positionieren (verhindert Aufblitzen)
            try:
                word.WindowState = 2  # wdWindowStateMinimize
                word.Top = -10000
                word.Left = -10000
            except Exception:
                pass
            word.DisplayAlerts = 0  # Keine Dialoge
            doc = word.Documents.Open(str(template_path), ReadOnly=False)
            styles_updated = 0
            for style in doc.Styles:
                try:
                    if style.Type == 1 or style.Type == 2:
                        self.logger.debug(f"Versuche Style: {style.NameLocal} (Type: {style.Type})")
                        style.Font.Name = font_name
                        style.Font.Size = font_size
                        styles_updated += 1
                        self.logger.debug(f"Style aktualisiert: {style.NameLocal}")
                except Exception as style_error:
                    self.logger.error(f"Style {style.NameLocal} konnte nicht geändert werden: {style_error}")
                    continue
            self.logger.info(f"Word-Template: {styles_updated} Formatvorlagen mit {font_name} {font_size}pt aktualisiert")
            doc.Save()
            doc.Close(False)
            word.DisplayAlerts = 1  # Dialoge wieder aktivieren
            word.Quit()
            pythoncom.CoUninitialize()
            return True
        except Exception as e:
            self.logger.error(f"Fehler bei Word COM-Automation für {template_path} (Font: {font_name}, Size: {font_size}): {e}")
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
            return self._modify_template_via_powershell(template_path, font_name, font_size, 'word')
