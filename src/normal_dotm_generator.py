import os
from docx import Document

# Einstellungen für die Formatvorlage "Standard"
FONT_NAME = "Aptos Narrow"
FONT_SIZE = 11  # Punkt
LINE_SPACING = 1.15  # Einfach = 1.0, 1.15-fach = 1.15
SPACE_AFTER = 6  # Punkt

# Pfade
SOURCE_DOCX = r"data/Datei-Vorlagen/Sonstiges/Standards/Normal.docx"  # Vorlage als docx
TARGET_DOTM = r"data/Datei-Vorlagen/Sonstiges/Standards/Normal.dotm"   # Ziel-Datei

def update_normal_style(docx_path, dotm_path):
    doc = Document(docx_path)
    style = doc.styles["Normal"]  # "Standard" auf Deutsch, "Normal" auf Englisch
    font = style.font
    font.name = FONT_NAME
    font.size = FONT_SIZE
    # Absatzformatierung
    para_format = style.paragraph_format
    para_format.line_spacing = LINE_SPACING
    para_format.space_after = SPACE_AFTER
    # Hinweis: Absatzformatvorlage kann keine Schriftart direkt setzen (python-docx Limitation)
    doc.save(dotm_path)  # Speichern als .dotm (technisch .docx, aber Word akzeptiert das)

if __name__ == "__main__":
    if not os.path.exists(SOURCE_DOCX):
        print(f"Vorlage nicht gefunden: {SOURCE_DOCX}")
    else:
        update_normal_style(SOURCE_DOCX, TARGET_DOTM)
        print(f"Normal.dotm erfolgreich erstellt: {TARGET_DOTM}")
