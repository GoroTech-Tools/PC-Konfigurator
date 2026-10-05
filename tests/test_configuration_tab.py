import importlib
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))


class FakeWidget:
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.text = kwargs.get("text")
        self.children = []
        self.pack_calls = 0
        if parent is not None and hasattr(parent, "children"):
            parent.children.append(self)

    def pack(self, **kwargs):
        self.pack_calls += 1

    def grid(self, **kwargs):
        pass

    def grid_columnconfigure(self, *args, **kwargs):
        pass

    def grid_rowconfigure(self, *args, **kwargs):
        pass


fake_ctk = types.ModuleType("customtkinter")
for widget_name in ("CTkFrame", "CTkLabel", "CTkRadioButton", "CTkOptionMenu", "CTkCheckBox", "CTkButton"):
    setattr(fake_ctk, widget_name, FakeWidget)
fake_ctk.CTkFont = lambda **kwargs: None

fake_theme = types.ModuleType("ui.theme")
fake_theme.CARD_STYLE = {}
fake_theme.CARD_TITLE_COLOR = "title"
fake_theme.CONTINUE_BUTTON_STYLE = {}
fake_theme.PAGE_HEADING_COLOR = "heading"
fake_theme.PALE_BUTTON_STYLE = {}
fake_theme.create_scrollable_page = lambda parent: FakeWidget(parent)
fake_theme.create_section_card = lambda parent, **kwargs: (FakeWidget(parent), FakeWidget(parent))

with patch.dict(sys.modules, {"customtkinter": fake_ctk, "ui.theme": fake_theme}):
    configuration_tab = importlib.import_module("ui.configuration_tab")


class ConfigurationTabModeTests(unittest.TestCase):
    def _build_tab(self, advanced_mode):
        root = FakeWidget()
        configuration_tab.build_configuration_tab(
            types.SimpleNamespace(tab=lambda _name: root),
            advanced_mode=advanced_mode,
            use_documents_var=object(),
            target_drive_var=object(),
            startmenu_mode_var=object(),
            corporate_design_var=object(),
            hidden_items_mode_var=object(),
            taskbar_alignment_var=object(),
            reset_templates_var=object(),
            enable_edge_profile_sync_var=object(),
            enable_firm_mode_var=object(),
            enable_com_sync_var=object(),
            enable_office_preclose_var=object(),
            enable_office_warmup_var=object(),
            font_name_var=object(),
            font_size_word_var=object(),
            font_size_outlook_var=object(),
            font_size_excel_var=object(),
            available_font_families=[],
            on_continue_to_execution=lambda: None,
            on_open_font_preview=lambda: None,
        )
        page = root.children[0]
        cards = {}
        for widget in page.children:
            for child in widget.children:
                if child.text in ("Datei-Vorlagen zurücksetzen", "Edge-Profile synchronisieren"):
                    cards[child.text] = child.parent
        return cards

    def test_reset_and_edge_sync_cards_are_hidden_in_simple_mode(self):
        cards = self._build_tab(advanced_mode=False)

        self.assertEqual(
            {title: card.pack_calls for title, card in cards.items()},
            {"Datei-Vorlagen zurücksetzen": 0, "Edge-Profile synchronisieren": 0},
        )

    def test_reset_and_edge_sync_cards_are_visible_in_advanced_mode(self):
        cards = self._build_tab(advanced_mode=True)

        self.assertEqual(
            {title: card.pack_calls for title, card in cards.items()},
            {"Datei-Vorlagen zurücksetzen": 1, "Edge-Profile synchronisieren": 1},
        )


if __name__ == "__main__":
    unittest.main()
