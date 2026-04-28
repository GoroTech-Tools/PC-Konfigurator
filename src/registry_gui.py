"""Registry-Erläuterungs-GUI.

Stabile, kompakte Oberfläche zur Anzeige der vom Konfigurator genutzten
Registry-Einstellungen inklusive einfacher Auswahl-Checkboxen.
"""

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List, Tuple

from registry_explainer import RegistryExplainer, RegistrySettingInfo


class RegistryExplanationWindow:
    """Fenster zur Anzeige von Registry-Erläuterungen."""

    def __init__(self, parent=None, path_callback=None, config_callback=None):
        self.parent = parent
        # config_callback: () -> dict mit 'path', 'font', 'font_size_word', 'font_size_excel'
        # path_callback: Legacy-Support (nur Pfad als str)
        self.config_callback = config_callback or (lambda: {'path': path_callback(), 'font': '', 'font_size_word': 11, 'font_size_excel': 10} if path_callback else None)
        self.registry_explainer = RegistryExplainer()
        self.window = None
        self.tabview = None
        self.setting_checkboxes: Dict[str, tk.BooleanVar] = {}
        self.original_states: Dict[str, bool] = {}
        self.has_changes = False

    def show_window(self):
        """Registry-Erläuterungsfenster anzeigen."""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Registry-Einstellungen - Konfiguration")
        self.window.geometry("1000x750")
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_closing)

        self.create_widgets()
        self.load_current_settings()

        self.window.after(50, self._bring_to_front)

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            main_frame,
            text="Registry-Einstellungen konfigurieren",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            main_frame,
            text="✓ = Einstellung wird angewendet | ✗ = Einstellung wird übersprungen",
            font=ctk.CTkFont(size=12),
        ).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        self.tabview.add("Übersicht")
        self.tabview.add("Word-Einstellungen")
        self.tabview.add("Excel-Einstellungen")
        self.tabview.add("Windows-Einstellungen")

        self.create_overview_tab()
        self._populate_settings_tab("Word", "Word-Einstellungen", "📝")
        self._populate_settings_tab("Excel", "Excel-Einstellungen", "📊")
        self._populate_settings_tab("Windows", "Windows-Einstellungen", "🪟")

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="💾 Auswahl anwenden",
            command=self.save_settings,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="🔄 Zurücksetzen",
            command=self.reset_settings,
            height=40,
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="❌ Schließen",
            command=self.close_window,
            height=40,
        ).pack(side="right", padx=10, pady=10)

    def create_overview_tab(self):
        if self.tabview is None:
            return
        overview_frame = self.tabview.tab("Übersicht")

        total_settings = len(self.registry_explainer.settings)
        categories = self.registry_explainer.get_all_categories()
        by_category = {
            c: len(self.registry_explainer.get_settings_by_category(c)) for c in categories
        }

        summary = [
            "Verfügbare Einstellungskategorien:",
            "",
        ]
        for cat in categories:
            summary.append(f"• {cat}: {by_category[cat]} Einstellungen")
        summary.extend([
            "",
            f"Gesamt: {total_settings} Einstellungen",
            "",
            "Wählen Sie in den Reitern unten, welche Einstellungen angewendet werden sollen.",
            "Klicken Sie auf eine Zeile, um eine detaillierte Beschreibung zu sehen.",
        ])

        self.summary_text = ctk.CTkTextbox(overview_frame, height=350)
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.summary_text.insert("0.0", "\n".join(summary))
        self.summary_text.configure(state="disabled")

    def _populate_settings_tab(self, category_prefix: str, tab_name: str, icon: str):
        if self.tabview is None:
            return
        tab = self.tabview.tab(tab_name)

        # Einstellungen filtern und sortieren
        selected: List[Tuple[str, RegistrySettingInfo]] = sorted(
            [(n, s) for n, s in self.registry_explainer.settings.items()
             if s.category.startswith(category_prefix)],
            key=lambda x: (x[1].category, x[0])
        )

        # ── Treeview-Style (passend zu customtkinter Dark Theme) ──────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Reg.Treeview",
            background="#2b2b2b", foreground="white",
            fieldbackground="#2b2b2b", rowheight=22,
            borderwidth=0, font=("", 10),
        )
        style.configure("Reg.Treeview.Heading",
            background="#1f538d", foreground="white",
            font=("", 10, "bold"), relief="flat",
        )
        style.map("Reg.Treeview",
            background=[("selected", "#1f6aa5")],
            foreground=[("selected", "white")],
        )
        style.configure("Reg.Vertical.TScrollbar",
            troughcolor="#2b2b2b", background="#4a4a4a",
        )

        # ── Layout: Tabelle oben, Detail unten ────────────────────────────
        table_frame = tk.Frame(tab, bg="#2b2b2b")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(10, 4))

        detail_outer = ctk.CTkFrame(tab)
        detail_outer.pack(fill="x", padx=10, pady=(0, 8))

        detail_title = ctk.CTkLabel(
            detail_outer,
            text="Zeile auswählen für Details",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        detail_title.pack(anchor="w", padx=10, pady=(6, 2))

        detail_text = ctk.CTkTextbox(detail_outer, height=110)
        detail_text.pack(fill="x", padx=10, pady=(0, 8))
        detail_text.configure(state="disabled")

        # ── Treeview ──────────────────────────────────────────────────────
        cols = ("aktiv", "einstellung", "kategorie", "standardwert", "typ")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                            style="Reg.Treeview", selectmode="browse")

        tree.heading("aktiv",        text="")
        tree.heading("einstellung",  text="Einstellung")
        tree.heading("kategorie",    text="Kategorie")
        tree.heading("standardwert", text="Standardwert")
        tree.heading("typ",          text="Typ")

        tree.column("aktiv",        width=36,  minwidth=36,  anchor="center", stretch=False)
        tree.column("einstellung",  width=220, minwidth=120, anchor="w")
        tree.column("kategorie",    width=200, minwidth=120, anchor="w")
        tree.column("standardwert", width=120, minwidth=60,  anchor="center")
        tree.column("typ",          width=80,  minwidth=60,  anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=tree.yview, style="Reg.Vertical.TScrollbar")
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # Abwechselnde Zeilenfarben
        tree.tag_configure("odd",  background="#2b2b2b")
        tree.tag_configure("even", background="#333333")

        # Aktuelle Konfigurationswerte aus Callback holen (einmalig beim Öffnen)
        cfg: dict = {}
        if self.config_callback is not None:
            try:
                cfg = self.config_callback() or {}
            except Exception:
                pass

        current_path = cfg.get('path', '')
        current_font = cfg.get('font', '')
        current_size_word = cfg.get('font_size_word', '')
        current_size_excel = cfg.get('font_size_excel', '')

        datei_vorlagen_path_keys = {
            "word_dot_path", "word_personal_templates",
            "excel_xlstart_info", "excel_personal_templates",
        }
        path_keys = {
            "word_startup_path", "word_doc_path", "excel_path",
        }
        font_keys = {"word_default_font", "word_font_override", "excel_default_font", "excel_font_override"}
        font_size_word_keys = {"word_default_font_size"}
        font_size_excel_keys = {"excel_default_font_size"}
        clear_keys = {"word_font_substitutes"}
        excel_font_display_keys = {"excel_font_override"}

        setting_map: Dict[str, RegistrySettingInfo] = {}
        for i, (setting_name, setting) in enumerate(selected):
            checkbox_var = tk.BooleanVar(value=True)
            self.setting_checkboxes[setting_name] = checkbox_var
            tag = "odd" if i % 2 == 0 else "even"
            if setting_name in excel_font_display_keys and current_font:
                display_value = f"{current_font},{current_size_excel}" if current_size_excel else current_font
            elif setting_name in font_keys and current_font:
                display_value = current_font
            elif setting_name in font_size_word_keys and current_size_word:
                display_value = f"{current_size_word} pt"
            elif setting_name in font_size_excel_keys and current_size_excel:
                display_value = f"{current_size_excel} pt"
            elif setting_name in datei_vorlagen_path_keys and current_path:
                display_value = str(Path(current_path) / "Datei-Vorlagen")
            elif setting_name in path_keys and current_path:
                display_value = current_path
            elif setting_name in clear_keys:
                display_value = "(wird geleert)"
            elif setting.default_value != "":
                display_value = setting.default_value
            else:
                display_value = "–"
            tree.insert("", "end", iid=setting_name, tags=(tag,), values=(
                "☑", setting.value_name, setting.category,
                display_value, setting.value_type,
            ))
            setting_map[setting_name] = setting

        # ── Ereignisse ────────────────────────────────────────────────────
        def _refresh_row(iid: str):
            var = self.setting_checkboxes.get(iid)
            if var is None:
                return
            vals = list(tree.item(iid, "values"))
            vals[0] = "☑" if var.get() else "☐"
            tree.item(iid, values=vals)

        def on_click(event: tk.Event):
            region = tree.identify_region(event.x, event.y)
            col = tree.identify_column(event.x)
            iid = tree.identify_row(event.y)
            if not iid:
                return
            # Klick auf Aktiv-Spalte → Toggle
            if region == "cell" and col == "#1":
                var = self.setting_checkboxes.get(iid)
                if var is not None:
                    var.set(not var.get())
                    _refresh_row(iid)
                    self.has_changes = True

        def on_select(event: tk.Event):
            sel = tree.selection()
            if not sel:
                return
            iid = sel[0]
            s = setting_map.get(iid)
            if s is None:
                return
            key = s.key_path.replace("{version}", "16.0")
            text = (
                f"Registry-Pfad:  HKEY_CURRENT_USER\\{key}\n"
                f"Wertname:        {s.value_name}\n"
                f"Typ:             {s.value_type}    "
                f"Standardwert: {s.default_value}\n\n"
                f"Beschreibung:\n{s.description}\n\n"
                f"Auswirkung:\n{s.impact}"
            )
            detail_title.configure(text=f"{icon} {s.value_name}")
            detail_text.configure(state="normal")
            detail_text.delete("0.0", "end")
            detail_text.insert("0.0", text)
            detail_text.configure(state="disabled")

        tree.bind("<ButtonRelease-1>", on_click)
        tree.bind("<<TreeviewSelect>>", on_select)

        # Öffentliche Referenz für reset_settings
        if not hasattr(self, "_trees"):
            self._trees: Dict[str, ttk.Treeview] = {}
        self._trees[tab_name] = tree

    def on_setting_changed(self):
        self.has_changes = True

    def load_current_settings(self):
        for key, var in self.setting_checkboxes.items():
            self.original_states[key] = var.get()
        self.has_changes = False

    def save_settings(self):
        enabled_count = sum(1 for var in self.setting_checkboxes.values() if var.get())
        disabled_count = len(self.setting_checkboxes) - enabled_count

        messagebox.showinfo(
            "Auswahl gespeichert",
            f"✅ {enabled_count} Einstellungen aktiviert\n"
            f"❌ {disabled_count} Einstellungen deaktiviert\n\n"
            "Die Auswahl wird beim nächsten Konfigurationslauf berücksichtigt.",
        )

        for key, var in self.setting_checkboxes.items():
            self.original_states[key] = var.get()
        self.has_changes = False

    def reset_settings(self):
        if not self.setting_checkboxes:
            return
        for key, var in self.setting_checkboxes.items():
            var.set(self.original_states.get(key, True))
        # Treeview-Symbole aktualisieren
        for tree in getattr(self, "_trees", {}).values():
            for iid in tree.get_children():
                var = self.setting_checkboxes.get(iid)
                if var is not None:
                    vals = list(tree.item(iid, "values"))
                    vals[0] = "☑" if var.get() else "☐"
                    tree.item(iid, values=vals)
        self.has_changes = False

    def _bring_to_front(self):
        """Fenster in den Vordergrund bringen (verzögert, damit CTk fertig gerendert hat)."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            self.window.grab_set()

    def on_window_closing(self):
        if self.has_changes:
            result = messagebox.askyesnocancel(
                "Fenster schließen",
                "Sie haben ungespeicherte Änderungen.\nMöchten Sie diese vor dem Schließen speichern?",
            )
            if result is None:
                return
            if result:
                self.save_settings()
        self.close_window()

    def close_window(self):
        if self.window:
            try:
                self.window.grab_release()
            except Exception:
                pass
            self.window.destroy()
            self.window = None

    def get_enabled_settings(self) -> Dict[str, bool]:
        return {key: var.get() for key, var in self.setting_checkboxes.items()}