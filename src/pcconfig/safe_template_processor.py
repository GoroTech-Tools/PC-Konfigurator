"""
Sichere Office Template Verarbeitung
=====================================

Bevorzugt python-docx (Word) und openpyxl (Excel) für Template-Anpassung.
COM-Automation als optionaler Fallback.
"""

import win32com.client
import pythoncom
from pathlib import Path
import logging
import time


class SafeTemplateProcessor:

    # XML-Namespaces für Office Open XML
    _NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    _NS_XL = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    def update_word_template_xml(self, template_path, font_name, font_size):
        """
        Setzt Schriftart und -größe in einem Word-Template (.dotm/.dotx/.docx) via lxml.
        lxml behält Namespace-Präfixe beim Serialisieren (keine Namespace-Korruption).
        Unterstützt auch .dotm-Dateien (Makro-Templates), die python-docx ablehnt.
        """
        import zipfile, shutil, tempfile, os
        try:
            from lxml import etree
        except ImportError:
            self.logger.error("lxml nicht verfügbar. Bitte 'pip install lxml' ausführen.")
            return False

        template_path = Path(template_path)
        if not template_path.exists():
            self.logger.error(f"Vorlagendatei nicht gefunden: {template_path}")
            return False
        try:
            W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            sz_val = str(int(font_size) * 2)  # Office speichert Halbpunkte

            # Temp-Kopie anlegen
            with tempfile.NamedTemporaryFile(delete=False, suffix=template_path.suffix) as tmp:
                tmp_path = tmp.name
            shutil.copy2(str(template_path), tmp_path)

            # styles.xml lesen
            styles_entry = None
            with zipfile.ZipFile(tmp_path, 'r') as z:
                names = z.namelist()
                styles_entry = next((n for n in names if n.lower() == 'word/styles.xml'), None)
                if not styles_entry:
                    self.logger.error(f"word/styles.xml nicht in {template_path.name} gefunden.")
                    os.unlink(tmp_path)
                    return False
                styles_xml = z.read(styles_entry)

            # Mit lxml parsen (behält Namespace-Präfixe)
            tree = etree.fromstring(styles_xml)
            changed = 0

            def _set_rpr(rpr_elem):
                nonlocal changed
                # rFonts setzen
                rfonts = rpr_elem.find(f'{{{W}}}rFonts')
                if rfonts is None:
                    rfonts = etree.SubElement(rpr_elem, f'{{{W}}}rFonts')
                # Theme-Font-Attribute entfernen – diese übersteuern w:ascii und würden
                # die explizit gesetzte Schriftart in Outlook/Word ignorieren
                for theme_attr in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
                    rfonts.attrib.pop(f'{{{W}}}{theme_attr}', None)
                rfonts.set(f'{{{W}}}ascii', font_name)
                rfonts.set(f'{{{W}}}hAnsi', font_name)
                rfonts.set(f'{{{W}}}cs', font_name)
                rfonts.set(f'{{{W}}}eastAsia', font_name)
                # Schriftgröße (Halbpunkte)
                for tag in [f'{{{W}}}sz', f'{{{W}}}szCs']:
                    el = rpr_elem.find(tag)
                    if el is None:
                        el = etree.SubElement(rpr_elem, tag)
                    el.set(f'{{{W}}}val', sz_val)
                changed += 1

            # 1. docDefaults
            doc_defaults = tree.find(f'{{{W}}}docDefaults')
            if doc_defaults is not None:
                rpr_default = doc_defaults.find(f'{{{W}}}rPrDefault')
                if rpr_default is not None:
                    rpr = rpr_default.find(f'{{{W}}}rPr')
                    if rpr is None:
                        rpr = etree.SubElement(rpr_default, f'{{{W}}}rPr')
                    _set_rpr(rpr)

            # 2. Absatz-Standard-Stil: in deutschen Templates "Standard", in englischen "Normal"
            #    Zusätzlich wird der Default-Stil (w:default="1") immer gesetzt.
            default_style_ids = {'Normal', 'Standard'}  # EN + DE
            for style in tree.findall(f'{{{W}}}style'):
                style_id = style.get(f'{{{W}}}styleId', '')
                is_default = style.get(f'{{{W}}}default', '') == '1' and \
                             style.get(f'{{{W}}}type', '') == 'paragraph'
                if style_id in default_style_ids or is_default:
                    rpr = style.find(f'{{{W}}}rPr')
                    if rpr is None:
                        rpr = etree.SubElement(style, f'{{{W}}}rPr')
                    _set_rpr(rpr)

            self.logger.info(f"lxml: {changed} rPr-Blöcke in {template_path.name} gesetzt ({font_name} {font_size}pt)")

            # Serialisieren — lxml behält alle originalen Namespace-Präfixe
            new_styles_bytes = etree.tostring(
                tree,
                xml_declaration=True,
                encoding='UTF-8',
                standalone=True
            )

            # theme1.xml patchen: minorFont + majorFont auf font_name setzen.
            # Ohne diesen Patch zeigt Outlook "Aptos (Textkörper)" statt der
            # explizit gesetzten Schriftart, weil Theme-Referenzen Vorrang haben.
            # HINWEIS: Suche case-insensitiv, da manche Office-Versionen
            # "word/theme/Theme1.xml" (Großbuchstabe T) in der ZIP ablegen.
            A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
            new_theme_bytes = None
            theme_entry = None
            with zipfile.ZipFile(tmp_path, 'r') as z:
                names = z.namelist()
                # Case-insensitive Suche nach dem Theme-Eintrag
                theme_entry = next(
                    (n for n in names if n.lower() == 'word/theme/theme1.xml'), None
                )
                if theme_entry:
                    theme_xml = z.read(theme_entry)
                    t = etree.fromstring(theme_xml)
                    fmtscheme = t.find(f'.//{{{A}}}fontScheme')
                    if fmtscheme is not None:
                        for section_tag in ('majorFont', 'minorFont'):
                            section = fmtscheme.find(f'{{{A}}}{section_tag}')
                            if section is not None:
                                latin = section.find(f'{{{A}}}latin')
                                if latin is None:
                                    latin = etree.SubElement(section, f'{{{A}}}latin')
                                latin.set('typeface', font_name)
                                latin.attrib.pop('panose', None)
                    new_theme_bytes = etree.tostring(
                        t, xml_declaration=True, encoding='UTF-8', standalone=True
                    )
                else:
                    self.logger.warning(
                        f"Kein word/theme/theme1.xml in {template_path.name} gefunden – "
                        f"Theme-Schrift kann nicht überschrieben werden."
                    )

            # ZIP in-place patchen
            out_tmp = tmp_path + '.out'
            with zipfile.ZipFile(tmp_path, 'r') as zin, \
                 zipfile.ZipFile(out_tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == styles_entry:
                        zout.writestr(item, new_styles_bytes)
                    elif theme_entry and item.filename == theme_entry and new_theme_bytes is not None:
                        zout.writestr(item, new_theme_bytes)
                    else:
                        zout.writestr(item, zin.read(item.filename))

            os.unlink(tmp_path)
            shutil.move(out_tmp, str(template_path))
            self.logger.info(f"Word-Template angepasst (lxml): {template_path.name}")
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Word-Template-Anpassung ({template_path.name}): {e}")
            for f in [locals().get('tmp_path', ''), locals().get('tmp_path', '') + '.out']:
                try:
                    if f and os.path.exists(f):
                        os.unlink(f)
                except Exception:
                    pass
            return False

    def update_excel_template_xml(self, template_path, font_name, font_size):
        """
        Setzt Schriftart und -größe in einem Excel-Template (.xltx/.xlsx) via openpyxl.
        Kein COM, kein Bitness-Problem.
        """
        template_path = Path(template_path)
        if not template_path.exists():
            self.logger.error(f"Vorlagendatei nicht gefunden: {template_path}")
            return False
        try:
            import zipfile
            from lxml import etree
            from openpyxl import load_workbook
            from openpyxl.styles import Font

            wb = load_workbook(str(template_path))
            wb.template = True  # .xltx-Typ beibehalten

            # 1. Erste Schriftart in der Fonts-Liste (Zell-Standard) überschreiben
            if wb._fonts:
                old = wb._fonts[0]
                wb._fonts[0] = Font(
                    name=font_name,
                    size=float(font_size),
                    bold=old.bold,
                    italic=old.italic,
                    underline=old.underline,
                    color=old.color,
                )

            # 2. Named Style setzen — in deutschen Excel-Installationen heißt er "Standard"
            for style_name in ('Standard', 'Normal'):
                if style_name in wb._named_styles.names:
                    wb._named_styles[style_name].font = Font(
                        name=font_name,
                        size=float(font_size)
                    )
                    self.logger.info(f"Named Style '{style_name}' gesetzt.")
                    break

            wb.save(str(template_path))

            # 3. XML-Feinschliff für echten Default:
            #    In manchen Templates hat cellXfs[0] kein applyFont=1.
            #    Dann zeigt Excel in der Font-Auswahl weiter Aptos,
            #    bis man die Stilvorlage "Standard" manuell anklickt.
            with zipfile.ZipFile(str(template_path), 'r') as zin:
                styles_xml = zin.read('xl/styles.xml')

            XL = self._NS_XL
            root = etree.fromstring(styles_xml)

            # cellXfs: alle Standard-xf (xfId=0) aktiv auf Font anwenden
            # In manchen Templates zeigt Excel initial auf xf[1] (ebenfalls xfId=0).
            cell_xfs = root.find(f'{{{XL}}}cellXfs')
            if cell_xfs is not None and len(cell_xfs) > 0:
                for xf in cell_xfs:
                    xf_id = xf.get('xfId', '0')
                    if xf_id == '0':
                        xf.set('fontId', '0')
                        xf.set('applyFont', '1')

            # cellStyleXfs[0] ebenfalls auf Font 0 fixieren
            cell_style_xfs = root.find(f'{{{XL}}}cellStyleXfs')
            if cell_style_xfs is not None and len(cell_style_xfs) > 0:
                sxf0 = cell_style_xfs[0]
                sxf0.set('fontId', '0')

            new_styles = etree.tostring(
                root,
                xml_declaration=True,
                encoding='UTF-8',
                standalone=True
            )

            # xl/theme/theme1.xml patchen: minorFont auf font_name setzen.
            # Ohne diesen Patch zeigt Excel in der Zellenformatvorlage "Standard"
            # weiterhin die Theme-Schrift, wenn das Template von einer anderen
            # Office-Installation stammt (z. B. Calibri-Theme von Office 2019).
            A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
            new_xl_theme_bytes = None
            xl_theme_entry = None
            with zipfile.ZipFile(str(template_path), 'r') as zin_theme:
                xl_names = zin_theme.namelist()
                xl_theme_entry = next(
                    (n for n in xl_names if n.lower() == 'xl/theme/theme1.xml'), None
                )
                if xl_theme_entry:
                    xl_theme_xml = zin_theme.read(xl_theme_entry)
                    t = etree.fromstring(xl_theme_xml)
                    fmtscheme = t.find(f'.//{{{A}}}fontScheme')
                    if fmtscheme is not None:
                        for section_tag in ('majorFont', 'minorFont'):
                            section = fmtscheme.find(f'{{{A}}}{section_tag}')
                            if section is not None:
                                latin = section.find(f'{{{A}}}latin')
                                if latin is None:
                                    latin = etree.SubElement(section, f'{{{A}}}latin')
                                latin.set('typeface', font_name)
                                latin.attrib.pop('panose', None)
                    new_xl_theme_bytes = etree.tostring(
                        t, xml_declaration=True, encoding='UTF-8', standalone=True
                    )
                else:
                    self.logger.warning(
                        f"Kein xl/theme/theme1.xml in {template_path.name} gefunden – "
                        f"Excel-Theme-Schrift kann nicht überschrieben werden."
                    )

            tmp_out = str(template_path) + '.tmp'
            with zipfile.ZipFile(str(template_path), 'r') as zin, zipfile.ZipFile(tmp_out, 'w', zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == 'xl/styles.xml':
                        zout.writestr(item, new_styles)
                    elif xl_theme_entry and item.filename == xl_theme_entry and new_xl_theme_bytes is not None:
                        zout.writestr(item, new_xl_theme_bytes)
                    else:
                        zout.writestr(item, zin.read(item.filename))

            import os
            os.replace(tmp_out, str(template_path))

            self.logger.info(f"Excel-Template angepasst (openpyxl + Theme): {template_path.name} → {font_name} {font_size}pt")
            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Excel-Template-Anpassung ({template_path.name}): {e}")
            return False

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
            style = None
            for style_name in ("Standard", "Normal"):
                try:
                    style = doc.Styles(style_name)
                    break
                except Exception:
                    continue

            if style is None:
                try:
                    style = doc.Styles(1)
                except Exception:
                    style = None

            if style is not None:
                font_name = style.Font.Name
                font_size = style.Font.Size
            else:
                # Fallback auf Dokument-Default
                font_name = doc.Content.Font.Name
                font_size = doc.Content.Font.Size

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
            # robust gegen Codepage/Unicode-Ausgaben
            # (verhindert sporadische UnicodeDecodeError in Reader-Threads)
            if hasattr(result, "stdout") and isinstance(result.stdout, bytes):
                stdout = result.stdout.decode("utf-8", errors="replace").strip()
            else:
                stdout = result.stdout.strip() if result.stdout else "(keine Ausgabe)"
            if hasattr(result, "stderr") and isinstance(result.stderr, bytes):
                stderr = result.stderr.decode("utf-8", errors="replace").strip()
            else:
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
