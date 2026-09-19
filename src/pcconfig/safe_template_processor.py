"""Sichere, möglichst COM-unabhängige Verarbeitung von Office-Vorlagen."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
import zipfile
from copy import deepcopy
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
            # lxml erhält die vorhandenen Open-XML-Namespace-Präfixe stabiler
            # als xml.etree.ElementTree. Das ist für Normal.dotm besonders
            # wichtig, weil die Vorlage VBA-, Glossary- und Theme-Teile enthält.
            # Der Fallback hält die Anwendung auch in schlanken EXE-Umgebungen
            # ohne lxml funktionsfähig.
            try:
                from lxml import etree
                use_lxml = True
            except ImportError:
                etree = ET
                use_lxml = False
                self.logger.warning(
                    "lxml nicht verfügbar; Word-DOTM wird mit stdlib XML verarbeitet."
                )

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / path.name
                shutil.copy2(path, temp_path)
                with zipfile.ZipFile(temp_path, "r") as source:
                    names = source.namelist()
                    styles_name = next((n for n in names if n.lower() == "word/styles.xml"), None)
                    theme_name = next((n for n in names if n.lower() == "word/theme/theme1.xml"), None)
                    if not styles_name:
                        raise ValueError("word/styles.xml fehlt")
                    styles_root = etree.fromstring(source.read(styles_name))
                    self._patch_word_styles(styles_root, font_name, font_size)
                    if use_lxml:
                        styles_bytes = etree.tostring(
                            styles_root,
                            encoding="UTF-8",
                            xml_declaration=True,
                            standalone=True,
                        )
                    else:
                        styles_bytes = etree.tostring(
                            styles_root,
                            encoding="utf-8",
                            xml_declaration=True,
                        )
                    theme_bytes = None
                    if theme_name:
                        # Die Word-Theme-Schrift bleibt unverändert. Eine
                        # globale Theme-Anpassung würde auch Überschrift 1/2,
                        # Titel usw. beeinflussen. Die gewünschte Schrift wird
                        # ausschließlich in Standard/Kein Leerraum gesetzt.
                        theme_bytes = source.read(theme_name)
                    out_path = Path(temp_dir) / ("out" + path.suffix)
                    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
                        for item in source.infolist():
                            if item.filename == styles_name:
                                target.writestr(item, styles_bytes)
                            elif theme_name and item.filename == theme_name and theme_bytes is not None:
                                target.writestr(item, theme_bytes)
                            else:
                                target.writestr(item, source.read(item.filename))

                # Nicht nur CRC prüfen: Word-relevante XML-Teile müssen vor dem
                # Austausch parsebar sein. Die Originaldatei bleibt bei jedem
                # Fehler unangetastet.
                with zipfile.ZipFile(out_path, "r") as validation_zip:
                    if validation_zip.testzip() is not None:
                        raise ValueError("Die fertig gepatchte Word-Vorlage ist beschädigt.")
                    for required_name in ("[Content_Types].xml", "word/document.xml", styles_name):
                        etree.fromstring(validation_zip.read(required_name))
                    if theme_name:
                        etree.fromstring(validation_zip.read(theme_name))
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
        temp_save = None
        out_path = None
        try:
            from lxml import etree
            from openpyxl import load_workbook

            suffix = path.suffix.lower()
            keep_vba = suffix in {".xlsm", ".xltm"}
            temp_save = path.with_name(path.name + ".pckconfig-save.tmp")
            out_path = path.with_name(path.name + ".pckconfig-out.tmp")
            if temp_save.exists():
                temp_save.unlink()
            if out_path.exists():
                out_path.unlink()

            # Nie direkt in die Quelle schreiben: Ein Fehler darf die Vorlage
            # nicht halb überschrieben zurücklassen.
            workbook = load_workbook(path, keep_vba=keep_vba)
            workbook.template = path.suffix.lower() == ".xltx"
            workbook.save(temp_save)
            with zipfile.ZipFile(temp_save, "r") as source:
                if source.testzip() is not None:
                    raise ValueError("Die temporäre Excel-Vorlage ist nach dem Speichern beschädigt.")
                styles_name = "xl/styles.xml"
                styles_root = etree.fromstring(source.read(styles_name))
                ns = {"x": self.EXCEL_NS}

                # Excel liest die Standardschrift aus der ersten Fontdefinition
                # und nicht nur aus cellXfs. Beide Stellen müssen konsistent
                # gesetzt werden, sonst meldet die Verifikation weiterhin z. B.
                # Aptos, obwohl die Registry bereits Arial enthält.
                fonts = styles_root.find(f"{{{self.EXCEL_NS}}}fonts")
                if fonts is not None and len(fonts) > 0:
                    default_font = fonts[0]
                    name_element = default_font.find(f"{{{self.EXCEL_NS}}}name")
                    if name_element is None:
                        name_element = etree.SubElement(default_font, f"{{{self.EXCEL_NS}}}name")
                    name_element.set("val", str(font_name))
                    size_element = default_font.find(f"{{{self.EXCEL_NS}}}sz")
                    if size_element is None:
                        size_element = etree.SubElement(default_font, f"{{{self.EXCEL_NS}}}sz")
                    size_element.set("val", str(float(font_size)))

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
                with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as target:
                    for item in source.infolist():
                        if item.filename == styles_name:
                            target.writestr(item, styles_bytes)
                        elif theme_name and item.filename == theme_name and theme_bytes is not None:
                            target.writestr(item, theme_bytes)
                        else:
                            target.writestr(item, source.read(item.filename))
            # Vor dem Austausch die erzeugte ZIP vollständig prüfen.
            with zipfile.ZipFile(out_path, "r") as validation_zip:
                if validation_zip.testzip() is not None:
                    raise ValueError("Die fertig gepatchte Excel-Vorlage ist beschädigt.")
                etree.fromstring(validation_zip.read("xl/styles.xml"))
                if theme_name:
                    etree.fromstring(validation_zip.read(theme_name))

            # Atomarer Austausch: Bei einem Lock bleibt die intakte Quelle erhalten.
            os.replace(out_path, path)
            return True
        except Exception as exc:
            self.logger.error("Excel-XML-Verarbeitung fehlgeschlagen: %s", exc)
            return False
        finally:
            for temporary in (temp_save, out_path):
                if temporary is not None:
                    try:
                        if temporary.exists():
                            temporary.unlink()
                    except Exception:
                        self.logger.debug("Temporäre Datei konnte nicht entfernt werden: %s", temporary)

    def update_word_template_safely(self, template_path, font_name, font_size):
        """XML zuerst, COM nur als optionaler Fallback."""
        return self.update_word_template_xml(template_path, font_name, font_size)

    def update_word_building_blocks_xml(self, template_path, font_name, font_size):
        """Patcht eine Word-Building-Blocks-Datei, falls sie vorhanden ist.

        Diese Methode ist bewusst isoliert und nur als zusätzliches, optionales
        Feature gedacht. Sie nutzt denselben XML-Pfad wie die Standard-Word-
        Templates, aber sie wird nur aufgerufen, wenn eine passende Datei
        tatsächlich gefunden wurde.
        """
        path = Path(template_path)
        if not path.exists():
            self.logger.info("Building-Blocks-Datei nicht gefunden: %s", path)
            return False
        return self.update_word_template_xml(path, font_name, font_size)

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
            original_theme_bytes = None
            if target_entry == "word/theme/theme1.xml":
                with zipfile.ZipFile(template_path) as template_zip:
                    if target_entry in template_zip.namelist():
                        original_theme_bytes = template_zip.read(target_entry)
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
                if original_theme_bytes is not None:
                    self._preserve_word_theme_fonts(theme_root, ET.fromstring(original_theme_bytes))
                    theme_bytes = ET.tostring(theme_root, encoding="utf-8")
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
        target_style_ids = {"normal", "no spacing", "nospacing"}
        target_style_names = {"standard", "normal", "kein leerraum", "no spacing"}
        patched_styles = []
        for style in root.findall(".//" + w + "style"):
            if style.get(w + "type", "paragraph") != "paragraph":
                continue
            style_id = str(style.get(w + "styleId", "")).strip().casefold()
            name_element = style.find(w + "name")
            style_name = str(name_element.get(w + "val", "")) if name_element is not None else ""
            if style_id not in target_style_ids and style_name.strip().casefold() not in target_style_names:
                continue
            rpr = style.find(w + "rPr")
            if rpr is None:
                rpr = self._sub_element(style, w + "rPr")
            rfonts = rpr.find(w + "rFonts")
            if rfonts is None:
                rfonts = self._sub_element(rpr, w + "rFonts")
            for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
                rfonts.attrib.pop(w + attr, None)
            for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                rfonts.set(w + attr, str(font_name))
            for tag in ("sz", "szCs"):
                size = rpr.find(w + tag)
                if size is None:
                    size = self._sub_element(rpr, w + tag)
                size.set(w + "val", str(int(font_size) * 2))
            patched_styles.append(style_id or style_name)
        self.logger.info("Word-Formatvorlagen angepasst: %s", ", ".join(patched_styles) or "keine")

    def _preserve_word_theme_fonts(self, target_root, original_root):
        """Übernimmt die Original-Theme-Schriften und lässt nur Theme-Farben zu."""
        a = "{" + self.DRAWING_NS + "}"
        target_scheme = target_root.find(".//" + a + "themeElements/" + a + "fontScheme")
        original_scheme = original_root.find(".//" + a + "themeElements/" + a + "fontScheme")
        if target_scheme is None or original_scheme is None:
            return
        target_scheme.clear()
        target_scheme.attrib.update(original_scheme.attrib)
        for child in original_scheme:
            target_scheme.append(deepcopy(child))

    def _patch_theme_fonts(self, root, font_name):
        a = "{" + self.DRAWING_NS + "}"
        for section_name in ("majorFont", "minorFont"):
            section = root.find(".//" + a + "fontScheme/" + a + section_name)
            if section is not None:
                latin = section.find(a + "latin")
                if latin is None:
                    latin = self._sub_element(section, a + "latin")
                latin.set("typeface", str(font_name))
                latin.attrib.pop("panose", None)

    @staticmethod
    def _sub_element(parent, tag):
        """Erzeugt ein XML-Kind passend zum verwendeten XML-Backend."""
        if hasattr(parent, "makeelement"):
            return parent.makeelement(tag, {})
        return ET.SubElement(parent, tag)

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
