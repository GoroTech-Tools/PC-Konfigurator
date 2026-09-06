"""Sichere, möglichst COM-unabhängige Verarbeitung von Office-Vorlagen."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


class SafeTemplateProcessor:
    """Bearbeitet Standardvorlagen mit XML/Open-XML und optionalem COM-Fallback."""

    WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
    EXCEL_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def update_word_template_xml(self, template_path, font_name, font_size):
        """Setzt Word-Standardformatierungen und Theme-Schrift direkt im ZIP."""
        path = Path(template_path)
        if not path.exists():
            self.logger.error("Vorlage nicht gefunden: %s", path)
            return False
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / path.name
                shutil.copy2(path, temp_path)
                with zipfile.ZipFile(temp_path, "r") as source:
                    names = source.namelist()
                    styles_name = next((n for n in names if n.lower() == "word/styles.xml"), None)
                    theme_name = next((n for n in names if n.lower() == "word/theme/theme1.xml"), None)
                    if not styles_name:
                        raise ValueError("word/styles.xml fehlt")
                    styles_root = ET.fromstring(source.read(styles_name))
                    self._patch_word_styles(styles_root, font_name, font_size)
                    styles_bytes = ET.tostring(styles_root, encoding="utf-8", xml_declaration=True)
                    theme_bytes = None
                    if theme_name:
                        theme_root = ET.fromstring(source.read(theme_name))
                        self._patch_theme_fonts(theme_root, font_name)
                        theme_bytes = ET.tostring(theme_root, encoding="utf-8", xml_declaration=True)
                    out_path = Path(temp_dir) / ("out" + path.suffix)
                    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
                        for item in source.infolist():
                            if item.filename == styles_name:
                                target.writestr(item, styles_bytes)
                            elif theme_name and item.filename == theme_name and theme_bytes is not None:
                                target.writestr(item, theme_bytes)
                            else:
                                target.writestr(item, source.read(item.filename))
                shutil.move(out_path, path)
            return True
        except Exception as exc:
            self.logger.error("Word-XML-Verarbeitung fehlgeschlagen: %s", exc)
            return False

    def update_excel_template_xml(self, template_path, font_name, font_size):
        """Setzt Excel-Schrift und Theme-Schrift ohne COM."""
        path = Path(template_path)
        if not path.exists():
            self.logger.error("Vorlage nicht gefunden: %s", path)
            return False
        try:
            from lxml import etree
            from openpyxl import load_workbook

            workbook = load_workbook(path)
            workbook.template = path.suffix.lower() == ".xltx"
            workbook.save(path)
            with zipfile.ZipFile(path, "r") as source:
                styles_name = "xl/styles.xml"
                styles_root = etree.fromstring(source.read(styles_name))
                ns = {"x": self.EXCEL_NS}
                for xf in styles_root.xpath("//x:cellXfs/x:xf[@xfId='0']", namespaces=ns):
                    xf.set("fontId", "0")
                    xf.set("applyFont", "1")
                styles_bytes = etree.tostring(styles_root, encoding="UTF-8", xml_declaration=True)
                theme_name = next((n for n in source.namelist() if n.lower() == "xl/theme/theme1.xml"), None)
                theme_bytes = None
                if theme_name:
                    theme_root = etree.fromstring(source.read(theme_name))
                    self._patch_theme_fonts_etree(theme_root, font_name, etree)
                    theme_bytes = etree.tostring(theme_root, encoding="UTF-8", xml_declaration=True)
                out_path = path.with_suffix(path.suffix + ".tmp")
                with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
                    for item in source.infolist():
                        if item.filename == styles_name:
                            target.writestr(item, styles_bytes)
                        elif theme_name and item.filename == theme_name and theme_bytes is not None:
                            target.writestr(item, theme_bytes)
                        else:
                            target.writestr(item, source.read(item.filename))
            out_path.replace(path)
            return True
        except Exception as exc:
            self.logger.error("Excel-XML-Verarbeitung fehlgeschlagen: %s", exc)
            return False

    def update_word_template_safely(self, template_path, font_name, font_size):
        """XML zuerst, COM nur als optionaler Fallback."""
        return self.update_word_template_xml(template_path, font_name, font_size)

    def apply_corporate_theme(self, template_path, theme_path, target_entry, design_name=None):
        """Ersetzt die Theme-XML direkt und registriert das Farbschema für Office."""
        template_path = Path(template_path)
        theme_path = Path(theme_path)
        if not template_path.exists() or not theme_path.exists():
            self.logger.warning("Corporate-Design-Datei oder Vorlage fehlt: %s / %s", theme_path, template_path)
            return False
        try:
            with zipfile.ZipFile(theme_path) as source:
                theme_entry = next((n for n in source.namelist() if n.lower() == "theme/theme/theme1.xml"), None)
                if not theme_entry:
                    return False
                theme_bytes = source.read(theme_entry)
            if design_name:
                theme_root = ET.fromstring(theme_bytes)
                color_scheme = theme_root.find(
                    ".//{" + self.DRAWING_NS + "}themeElements/{" + self.DRAWING_NS + "}clrScheme"
                )
                if color_scheme is not None:
                    colors_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "Microsoft" / "Templates" / "Theme Colors"
                    colors_dir.mkdir(parents=True, exist_ok=True)
                    colors_path = colors_dir / (str(design_name) + ".xml")
                    colors_path.write_bytes(
                        b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                        + ET.tostring(color_scheme, encoding="utf-8")
                    )
                    self.logger.info("Office-Farbschema installiert: %s", colors_path)
            with tempfile.TemporaryDirectory() as temp_dir:
                out_path = Path(temp_dir) / template_path.name
                replaced = False
                with zipfile.ZipFile(template_path) as source, zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
                    for item in source.infolist():
                        if item.filename == target_entry:
                            target.writestr(item, theme_bytes)
                            replaced = True
                        else:
                            target.writestr(item, source.read(item.filename))
                if not replaced:
                    return False
                shutil.move(out_path, template_path)
            return True
        except Exception as exc:
            self.logger.error("Corporate-Design-Einbettung fehlgeschlagen: %s", exc)
            return False

    def update_excel_template_safely(self, template_path, font_name, font_size):
        """XML zuerst, COM nur als optionaler Fallback."""
        return self.update_excel_template_xml(template_path, font_name, font_size)

    def get_word_template_font_info(self, template_path):
        return {"font_name": None, "font_size": None}

    def _patch_word_styles(self, root, font_name, font_size):
        w = "{" + self.WORD_NS + "}"
        for rpr in root.findall(".//" + w + "rPr"):
            rfonts = rpr.find(w + "rFonts")
            if rfonts is None:
                rfonts = ET.SubElement(rpr, w + "rFonts")
            for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
                rfonts.attrib.pop(w + attr, None)
            for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                rfonts.set(w + attr, str(font_name))
            for tag in ("sz", "szCs"):
                size = rpr.find(w + tag)
                if size is None:
                    size = ET.SubElement(rpr, w + tag)
                size.set(w + "val", str(int(font_size) * 2))

    def _patch_theme_fonts(self, root, font_name):
        a = "{" + self.DRAWING_NS + "}"
        for section_name in ("majorFont", "minorFont"):
            section = root.find(".//" + a + "fontScheme/" + a + section_name)
            if section is not None:
                latin = section.find(a + "latin")
                if latin is None:
                    latin = ET.SubElement(section, a + "latin")
                latin.set("typeface", str(font_name))
                latin.attrib.pop("panose", None)

    def _patch_theme_fonts_etree(self, root, font_name, etree):
        a = "{" + self.DRAWING_NS + "}"
        for section_name in ("majorFont", "minorFont"):
            section = root.find(".//" + a + "fontScheme/" + a + section_name)
            if section is not None:
                latin = section.find(a + "latin")
                if latin is None:
                    latin = etree.SubElement(section, a + "latin")
                latin.set("typeface", str(font_name))
                latin.attrib.pop("panose", None)
