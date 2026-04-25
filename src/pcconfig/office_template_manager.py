"""
Office Template Manager
======================

Verwaltet Office-Vorlagendateien (Normal.dotm, Mappe.xltx, NormalEmail.dotm)
"""

import os
import shutil
import time
from pathlib import Path
import logging
import zipfile
import tempfile
from xml.etree import ElementTree as ET
from pcconfig.safe_template_processor import SafeTemplateProcessor


class OfficeTemplateManager:
    def check_templates_exist(self):
        """Prüft, ob alle Templates existieren. Gibt Dict zurück."""
        result = {}
        for key, path in self.source_templates.items():
            result[key] = path.exists()
        return result

    def get_current_fonts_in_templates(self):
        """Liefert die aktuelle Schriftart/-größe der Templates (soweit möglich). Gibt Dict zurück."""
        fonts = {}
        # Word/Outlook: Versuche Font auszulesen
        for key in ['normal_dotm', 'normal_email_dotm']:
            path = self.source_templates.get(key)
            if path and path.exists():
                try:
                    font_info = self.safe_processor.get_word_template_font_info(path)
                    fonts[key] = font_info
                except Exception as e:
                    fonts[key] = f"Fehler: {e}"
            else:
                fonts[key] = None
        # Excel: Font auslesen ist schwierig, daher nur Platzhalter
        key = 'mappe_xltx'
        path = self.source_templates.get(key)
        if path and path.exists():
            fonts[key] = "(nicht direkt auslesbar)"
        else:
            fonts[key] = None
        return fonts
    
    def __init__(self, app_dir):
        """
        Initialisiert den Office Template Manager
        
        Args:
            app_dir: Verzeichnis der Anwendung
        """
        self.app_dir = Path(app_dir)
        self.logger = logging.getLogger(__name__)
        self.safe_processor = SafeTemplateProcessor()  # Sichere Template-Verarbeitung
        # Template-Pfade definieren
        try:
            self.source_templates = {
                'normal_dotm': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Normal.dotm",
                'mappe_xltx': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "Mappe.xltx",
                'normal_email_dotm': self.app_dir / "Datei-Vorlagen" / "Sonstiges" / "Standards" / "NormalEmail.dotm"
            }
        except Exception as e:
            self.logger.error(f"Fehler bei source_templates-Initialisierung: {e}")
            self.source_templates = {}
        try:
            self.target_paths = {
                'normal_dotm': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Templates" / "Normal.dotm",
                'mappe_xltx': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART" / "Mappe.xltx",
                'normal_email_dotm': Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Templates" / "NormalEmail.dotm"
            }
        except Exception as e:
            self.logger.error(f"Fehler bei target_paths-Initialisierung: {e}")
            self.target_paths = {}

    def update_font_in_templates(self, font_name=None, font_size_word=None, font_size_excel=None, **kwargs):
        """Setzt die Schriftart in allen Templates (Word/Excel). Gibt Status-Dict zurück und prüft nach Anpassung die Fonts."""
        result = {}
        # Word-Template anpassen
        if 'normal_dotm' in self.source_templates and self.source_templates['normal_dotm'].exists():
            try:
                ok = self.safe_processor.update_word_template_safely(
                    self.source_templates['normal_dotm'],
                    font_name or 'Arial',
                    font_size_word or 11
                )
                result['normal_dotm'] = ok
                # Nach Anpassung: Font auslesen und loggen
                try:
                    font_info = self.safe_processor.get_word_template_font_info(self.source_templates['normal_dotm'])
                    self.logger.info(f"Normal.dotm Font-Check: {font_info}")
                except Exception as e:
                    self.logger.warning(f"Konnte Font-Info von Normal.dotm nicht auslesen: {e}")
            except Exception as e:
                self.logger.error(f"Fehler bei Word-Template-Anpassung: {e}")
                result['normal_dotm'] = False
        # Excel-Template anpassen (analog zu Word: immer Originaldatei im Quellordner bearbeiten)
        if 'mappe_xltx' in self.source_templates and self.source_templates['mappe_xltx'].exists():
            try:
                # 1. Bearbeite Mappe.xltx direkt im Quellordner
                ok = self.update_excel_template_safely(
                    self.source_templates['mappe_xltx'],
                    font_name or 'Arial',
                    font_size_excel or 10
                )
                result['mappe_xltx'] = ok
                if not ok:
                    # PowerShell-Fallback für Excel, falls COM fehlschlägt
                    fallback_ok = self._modify_excel_template_via_powershell(self.source_templates['mappe_xltx'], font_name or 'Arial', font_size_excel or 10)
                    result['mappe_xltx_powershell'] = fallback_ok
                    if fallback_ok:
                        self.logger.info("PowerShell-Fallback für Mappe.xltx erfolgreich.")
                # 2. Kopiere die bearbeitete Datei ins Benutzerprofil
                try:
                    target = self.target_paths['mappe_xltx']
                    from shutil import copy2
                    copy2(str(self.source_templates['mappe_xltx']), str(target))
                    self.logger.info(f"Mappe.xltx ins Benutzerverzeichnis kopiert: {target}")
                except Exception as copy_error:
                    self.logger.error(f"Fehler beim Kopieren von Mappe.xltx ins Benutzerverzeichnis: {copy_error}")
                # Nach Anpassung: Font-Check (Platzhalter, da nicht direkt auslesbar)
                self.logger.info("Mappe.xltx wurde angepasst (Font-Check für Excel-Templates ist nur eingeschränkt möglich).")
            except Exception as e:
                self.logger.error(f"Fehler bei Excel-Template-Anpassung: {e}")
                result['mappe_xltx'] = False

        # Outlook-Template (NormalEmail.dotm) anpassen
        if 'normal_email_dotm' in self.source_templates and self.source_templates['normal_email_dotm'].exists():
            try:
                ok = self.safe_processor.update_word_template_safely(
                    self.source_templates['normal_email_dotm'],
                    font_name or 'Arial',
                    font_size_word or 11
                )
                result['normal_email_dotm'] = ok
                # Nach Anpassung: Font auslesen und loggen
                try:
                    font_info = self.safe_processor.get_word_template_font_info(self.source_templates['normal_email_dotm'])
                    self.logger.info(f"NormalEmail.dotm Font-Check: {font_info}")
                except Exception as e:
                    self.logger.warning(f"Konnte Font-Info von NormalEmail.dotm nicht auslesen: {e}")
            except Exception as e:
                self.logger.error(f"Fehler bei NormalEmail.dotm-Anpassung: {e}")
                result['normal_email_dotm'] = False
        return result

    def _modify_excel_template_via_powershell(self, template_path, font_name, font_size):
        """PowerShell-Fallback für Excel-Templates (setzt Schriftart und -größe via Skript)."""
        import subprocess
        from pathlib import Path
        ps_script = Path(__file__).parent / "set_excel_template_font.ps1"
        if not ps_script.exists():
            self.logger.error(f"PowerShell-Skript für Excel nicht gefunden: {ps_script}")
            return False
        cmd = [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps_script),
            "-TemplatePath", str(template_path),
            "-FontName", str(font_name),
            "-FontSize", str(font_size)
        ]
        self.logger.info(f"Starte PowerShell-Fallback für Excel: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            stdout = result.stdout.strip() if result.stdout else "(keine Ausgabe)"
            stderr = result.stderr.strip() if result.stderr else "(keine Fehlerausgabe)"
            if result.returncode == 0:
                self.logger.info(f"PowerShell-Fallback für Excel erfolgreich: {stdout}")
                return True
            else:
                self.logger.error(f"PowerShell-Fallback für Excel fehlgeschlagen: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Fehler beim PowerShell-Fallback für Excel: {e}")
            return False

    def update_excel_template_safely(self, template_path, font_name, font_size):
        """Setzt die Schriftart und -größe in einer Excel-Vorlage (xltx) – direkt, ohne Umweg. Löscht ggf. Mappe.xlsx im Zielverzeichnis und kopiert Mappe.xltx explizit dorthin."""
        import subprocess
        import os
        import glob
        import sys
        from pathlib import Path
        procs = ["EXCEL.EXE", "WINWORD.EXE", "OUTLOOK.EXE"]
        creationflags = 0x08000000 if sys.platform == "win32" else 0
        for proc in procs:
            try:
                self.logger.info(f"Beende ggf. laufenden Prozess: {proc}")
                subprocess.run(["taskkill", "/IM", proc, "/F"], check=False, capture_output=True, creationflags=creationflags)
            except Exception as e:
                self.logger.warning(f"Konnte {proc} nicht beenden: {e}")
        # Vor dem Speichern: Alle Mappe*.xlsx im Zielverzeichnis löschen
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
        try:
            import win32com.client
            import pythoncom
            self.logger.info(f"Öffne Excel-Template über COM: {template_path} | Font: {font_name} | Size: {font_size}")
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
            wb = excel.Workbooks.Open(str(template_path), ReadOnly=False)
            for sheet in wb.Worksheets:
                try:
                    self.logger.debug(f"Setze Font für Blatt: {sheet.Name}")
                    sheet.Cells.Font.Name = font_name
                    sheet.Cells.Font.Size = font_size
                except Exception as sheet_error:
                    self.logger.error(f"Fehler beim Setzen des Fonts für Blatt {sheet.Name}: {sheet_error}")
            wb.SaveAs(str(template_path), FileFormat=52)  # 52 = xlOpenXMLTemplate
            wb.Close(False)
            excel.Quit()
            pythoncom.CoUninitialize()
            self.logger.info(f"Excel-Template erfolgreich modifiziert: {template_path}")
            # Nach Anpassung: Mappe.xlsx im Zielverzeichnis löschen, falls vorhanden
            xlstart = Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Excel" / "XLSTART"
            mappe_xlsx = xlstart / "Mappe.xlsx"
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
            self.logger.error(f"Fehler bei Excel COM-Automation für {template_path} (Font: {font_name}, Size: {font_size}): {e}")
            return False
    
    def copy_templates_to_user(self):
        """Kopiert Standard-Templates ins Benutzerprofil. Gibt Status-Dict zurück."""
        import subprocess
        # Vor dem Kopieren: Alle WINWORD.EXE-Prozesse beenden
        try:
            subprocess.run(["taskkill", "/IM", "WINWORD.EXE", "/F"], check=False, capture_output=True)
            self.logger.info("Alle WINWORD.EXE-Prozesse wurden vor dem Kopieren beendet.")
        except Exception as e:
            self.logger.warning(f"Konnte WINWORD.EXE nicht beenden: {e}")

        results = {}
        for template_key, source_path in self.source_templates.items():
            target_path = self.target_paths.get(template_key)
            if target_path is None:
                self.logger.error(f"Kein Zielpfad für Template-Key: {template_key}")
                results[template_key] = False
                continue
            if not source_path.exists():
                self.logger.warning(f"Quelldatei nicht gefunden: {source_path}")
                results[template_key] = False
                continue
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    target_path = Path(target_path)
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    from shutil import copy2
                    copy2(str(source_path), str(target_path))
                    self.logger.info(f"Kopiert: {source_path} -> {target_path}")
                    results[template_key] = True
                    break
                except Exception as e:
                    self.logger.error(f"Fehler beim Kopieren {source_path} -> {target_path} (Versuch {attempt}/{max_retries}): {e}")
                    results[template_key] = False
                    if attempt < max_retries:
                        time.sleep(2)
            else:
                self.logger.error(f"Konnte {source_path} nach {max_retries} Versuchen nicht kopieren.")
        return results
