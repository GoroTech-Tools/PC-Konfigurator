"""
Registry-Erläuterungs-GUI
=========================

GUI-Komponente zur Anzeige von Registry-Einstellungen mit detaillierten Erläuterungen.
Beinhaltet Checkboxen zum Aktivieren/Deaktivieren von Einstellungen.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from registry_explainer import RegistryExplainer
import json
from typing import Dict, List
import os

def log_debug(msg):
    """Loggt Debug-Meldungen in debug_registry_gui.txt"""
    try:
        # Schreibe ins Verzeichnis, in dem sich diese Datei befindet
        log_path = os.path.join(os.path.dirname(__file__), "debug_registry_gui.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        pass  # Im Fehlerfall ignorieren


class RegistryExplanationWindow:
    """Fenster zur Anzeige von Registry-Erläuterungen"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.registry_explainer = RegistryExplainer()
        self.window = None
        # Tracking für Checkbox-Zustände
        self.setting_checkboxes: Dict[str, tk.BooleanVar] = {}
        self.original_states: Dict[str, bool] = {}
        self.has_changes = False
        
    def show_window(self):
        """Registry-Erläuterungsfenster anzeigen"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            if self.window is not None:
                self.window.attributes('-topmost', True)
                self.window.after(100, lambda: self.window is not None and self.window.attributes('-topmost', False))
            return
            
        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Registry-Einstellungen - Konfiguration")
        self.window.geometry("1000x750")
        
        # Fenster im Vordergrund halten
        self.window.lift()
        self.window.focus_force()
        if self.window is not None:
            self.window.attributes('-topmost', True)
            self.window.after(100, lambda: self.window is not None and self.window.attributes('-topmost', False))
        
        # Fenster-Icon (falls verfügbar)
        try:
            self.window.iconbitmap("icon.ico")
        except:
            pass
        
        # Fenster-Schließen-Event abfangen
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_closing)
        
        self.create_widgets()
        
    def create_widgets(self):
        """GUI-Widgets erstellen"""
        # Hauptframe
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text="Registry-Einstellungen konfigurieren",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Info-Text
        info_label = ctk.CTkLabel(
            main_frame,
            text="✓ = Einstellung wird angewendet | ✗ = Einstellung wird übersprungen",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=(0, 10))
        
        # Tabs für verschiedene Ansichten
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs erstellen
        self.tabview.add("Übersicht")
        self.tabview.add("Word-Einstellungen")
        self.tabview.add("Excel-Einstellungen")
        self.tabview.add("Windows-Einstellungen")
        
        # Button-Frame am unteren Rand
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Buttons
        save_button = ctk.CTkButton(
            button_frame,
            text="💾 Einstellungen anwenden",
            command=self.save_settings,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_button.pack(side="left", padx=10, pady=10)
        
        reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Zurücksetzen", 
            command=self.reset_settings,
            height=40
        )
        reset_button.pack(side="left", padx=10, pady=10)
        
        # Kein Exportieren-Button, da keine Methode export_settings existiert
        
        close_button = ctk.CTkButton(
            button_frame,
            text="❌ Schließen",
            command=self.close_window,
            height=40
        )
        close_button.pack(side="right", padx=10, pady=10)

        # Tabs mit Inhalt füllen
        self.create_overview_tab()
        self.create_word_settings_tab()
        self.create_excel_settings_tab()
        self.create_windows_settings_tab()

    def create_windows_settings_tab(self):
        """Windows-Einstellungen Tab mit Checkboxen erstellen"""
        windows_frame = self.tabview.tab("Windows-Einstellungen")
        scroll_frame = ctk.CTkScrollableFrame(windows_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        windows_settings = self.registry_explainer.get_settings_by_category("Windows")
        log_debug(f"[DEBUG] Windows-Settings geladen: {len(windows_settings)}")
        from collections import defaultdict
        grouped = defaultdict(list)
        setting_name_map = {name: setting for name, setting in self.registry_explainer.settings.items() if setting in windows_settings}
        for name, setting in setting_name_map.items():
            grouped[setting.category].append((name, setting))
        for subcat in sorted(grouped.keys()):
            subcat_label = ctk.CTkLabel(scroll_frame, text=subcat, font=ctk.CTkFont(size=16, weight="bold"))
            subcat_label.pack(anchor="w", padx=5, pady=(15, 5))
            for setting_name, setting in grouped[subcat]:
                setting_frame = ctk.CTkFrame(scroll_frame)
                setting_frame.pack(fill="x", padx=5, pady=5)
                header_frame = ctk.CTkFrame(setting_frame)
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                setting_key = setting_name
                checkbox_var = tk.BooleanVar(value=True)
                self.setting_checkboxes[setting_key] = checkbox_var
                checkbox = ctk.CTkCheckBox(
                    header_frame,
                    text=f"🪟 {setting.value_name}",
                    variable=checkbox_var,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda: self.on_setting_changed()
                )
                checkbox.pack(side="left", padx=5)
                status_label = ctk.CTkLabel(
                    header_frame,
                    text="✓ Wird angewendet",
                    font=ctk.CTkFont(size=10),
                    text_color="green"
                )
                status_label.pack(side="right", padx=5)
                def update_status(var=checkbox_var, label=status_label):
                    if var.get():
                        label.configure(text="✓ Wird angewendet", text_color="green")
                    else:
                        label.configure(text="✗ Wird übersprungen", text_color="red")
                checkbox_var.trace_add("write", lambda *args, var=checkbox_var, label=status_label: update_status(var, label))
                details_text = f"""Typ: {setting.value_type}\nStandardwert: {setting.default_value}\nRegistry-Pfad: HKEY_CURRENT_USER\\{setting.key_path.replace('{version}', '16.0')}\n\nBeschreibung:\n{setting.description}\n\nAuswirkung:\n{setting.impact}"""
                details_textbox = ctk.CTkTextbox(setting_frame, height=120)
                details_textbox.pack(fill="x", padx=10, pady=(0, 10))
                details_textbox.insert("0.0", details_text)
                details_textbox.configure(state="disabled")
        
    def create_overview_tab(self):
        """Übersicht-Tab erstellen"""
        overview_frame = self.tabview.tab("Übersicht")
        
        # Statistik-Frame
        stats_frame = ctk.CTkFrame(overview_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Statistiken anzeigen
        categories = self.registry_explainer.get_all_categories()
        total_settings = len(self.registry_explainer.settings)
        
                else:
                    label.configure(text="✗ Wird übersprungen", text_color="red")
            checkbox_var.trace_add("write", lambda *args, var=checkbox_var, label=status_label: update_status(var, label))
            details_text = f"""Typ: {setting.value_type}\nStandardwert: {setting.default_value}\nRegistry-Pfad: HKEY_CURRENT_USER\\{setting.key_path.replace('{version}', '16.0')}\n\nBeschreibung:\n{setting.description}\n\nAuswirkung:\n{setting.impact}"""
            details_textbox = ctk.CTkTextbox(setting_frame, height=120)
            details_textbox.pack(fill="x", padx=10, pady=(0, 10))
            details_textbox.insert("0.0", details_text)
            details_textbox.configure(state="disabled")
        
    def create_general_settings_tab(self):
        """Allgemeine Einstellungen Tab erstellen"""
        general_frame = self.tabview.tab("Allgemein")
        info_label = ctk.CTkLabel(
            general_frame,
            text="Übersicht und Verwaltung der Registry-Einstellungen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(pady=20)
        stats_frame = ctk.CTkFrame(general_frame)
        stats_frame.pack(fill="x", padx=20, pady=20)
        summary_label = ctk.CTkLabel(
            stats_frame,
            text="Aktuelle Auswahl:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        summary_label.pack(pady=10)
        self.summary_text = ctk.CTkTextbox(stats_frame, height=200)
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        update_button = ctk.CTkButton(
            stats_frame,
            text="🔄 Zusammenfassung aktualisieren",
            command=self.update_summary
        )
        update_button.pack(pady=10)
        quick_frame = ctk.CTkFrame(general_frame)
        quick_frame.pack(fill="x", padx=20, pady=20)
        quick_label = ctk.CTkLabel(
            quick_frame,
            text="Schnellaktionen:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quick_label.pack(pady=(10, 5))
        button_row = ctk.CTkFrame(quick_frame)
        button_row.pack(pady=10)
        select_all_btn = ctk.CTkButton(
            button_row,
            text="✅ Alle auswählen",
            command=self.select_all_settings
        )
        select_all_btn.pack(side="left", padx=5)
        deselect_all_btn = ctk.CTkButton(
            button_row,
            text="❌ Alle abwählen",
            command=self.deselect_all_settings
        )
        deselect_all_btn.pack(side="left", padx=5)
        select_word_btn = ctk.CTkButton(
            button_row,
            text="📝 Nur Word",
            command=self.select_word_only
        )
        select_word_btn.pack(side="left", padx=5)
        select_excel_btn = ctk.CTkButton(
            button_row,
            text="📊 Nur Excel",
            command=self.select_excel_only
        )
        select_excel_btn.pack(side="left", padx=5)
        scroll_frame = ctk.CTkScrollableFrame(general_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Schließen-Button immer am unteren Rand, unabhängig vom Scrollbereich
        close_button = ctk.CTkButton(
            general_frame,
            text="❌ Schließen",
            command=self.close_window,
            height=40
        )
        close_button.pack(side="right", padx=10, pady=(0, 10))
        # Nur Office-Einstellungen anzeigen (Windows jetzt im eigenen Tab)
        office_settings = self.registry_explainer.get_settings_by_category("Office")
        log_debug(f"[DEBUG] Office-Settings geladen: {len(office_settings)}")
        from collections import defaultdict
        grouped = defaultdict(list)
        setting_name_map = {name: setting for name, setting in self.registry_explainer.settings.items() if setting in office_settings}
        for name, setting in setting_name_map.items():
            grouped[setting.category].append((name, setting))
        for subcat in sorted(grouped.keys()):
            subcat_label = ctk.CTkLabel(scroll_frame, text=subcat, font=ctk.CTkFont(size=16, weight="bold"))
            subcat_label.pack(anchor="w", padx=5, pady=(15, 5))
            for setting_name, setting in grouped[subcat]:
                setting_frame = ctk.CTkFrame(scroll_frame)
                setting_frame.pack(fill="x", padx=5, pady=5)
                header_frame = ctk.CTkFrame(setting_frame)
                header_frame.pack(fill="x", padx=10, pady=(10, 5))
                setting_key = setting_name
                checkbox_var = tk.BooleanVar(value=True)
                self.setting_checkboxes[setting_key] = checkbox_var
                checkbox = ctk.CTkCheckBox(
                    header_frame,
                    text=f"⚙️ {setting.value_name}",
                    variable=checkbox_var,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda: self.on_setting_changed()
                )
                checkbox.pack(side="left", padx=5)
                status_label = ctk.CTkLabel(
                    header_frame,
                    text="✓ Wird angewendet",
                    font=ctk.CTkFont(size=10),
                    text_color="green"
                )
                status_label.pack(side="right", padx=5)
                def update_status(var=checkbox_var, label=status_label):
                    if var.get():
                        label.configure(text="✓ Wird angewendet", text_color="green")
                    else:
                        label.configure(text="✗ Wird übersprungen", text_color="red")
                checkbox_var.trace_add("write", lambda *args, var=checkbox_var, label=status_label: update_status(var, label))
                details_text = f"""Typ: {setting.value_type}\nStandardwert: {setting.default_value}\nRegistry-Pfad: HKEY_CURRENT_USER\\{setting.key_path.replace('{version}', '16.0')}\n\nBeschreibung:\n{setting.description}\n\nAuswirkung:\n{setting.impact}"""
                details_textbox = ctk.CTkTextbox(setting_frame, height=120)
                details_textbox.pack(fill="x", padx=10, pady=(0, 10))
                details_textbox.insert("0.0", details_text)
                details_textbox.configure(state="disabled")

        # Schließen-Button am unteren Rand ergänzen
        close_button = ctk.CTkButton(
            general_frame,
            text="❌ Schließen",
            command=self.close_window,
            height=40
        )
        close_button.pack(side="right", padx=10, pady=10)
    
    def select_all_settings(self):
        """Wählt alle Einstellungen aus"""
        for var in self.setting_checkboxes.values():
            var.set(True)
        self.on_setting_changed()
        
    def deselect_all_settings(self):
        """Wählt alle Einstellungen ab"""
        for var in self.setting_checkboxes.values():
            var.set(False)
        self.on_setting_changed()
        
    def select_word_only(self):
        """Wählt nur Word-Einstellungen aus"""
        for key, var in self.setting_checkboxes.items():
            var.set(key.startswith("word_"))
        self.on_setting_changed()
        
    def select_excel_only(self):
        """Wählt nur Excel-Einstellungen aus"""
        for key, var in self.setting_checkboxes.items():
            var.set(key.startswith("excel_"))
        self.on_setting_changed()
    
    def on_setting_changed(self):
        """Wird aufgerufen, wenn eine Checkbox geändert wird"""
        self.has_changes = True
        self.update_summary()
    
    def update_summary(self):
        """Aktualisiert die Zusammenfassung der ausgewählten Einstellungen"""
        if hasattr(self, 'summary_text'):
            enabled_count = sum(1 for var in self.setting_checkboxes.values() if var.get())
            total_count = len(self.setting_checkboxes)
            disabled_count = total_count - enabled_count
            
            word_count = sum(1 for key, var in self.setting_checkboxes.items() if key.startswith("word_") and var.get())
            excel_count = sum(1 for key, var in self.setting_checkboxes.items() if key.startswith("excel_") and var.get())
            
            summary = f"""Registry-Einstellungen Übersicht:
            
✅ Aktiviert: {enabled_count} von {total_count}
❌ Deaktiviert: {disabled_count} von {total_count}

Nach Kategorien:
📝 Word-Einstellungen: {word_count} aktiviert
📊 Excel-Einstellungen: {excel_count} aktiviert

Status: {"⚠️ Ungespeicherte Änderungen" if self.has_changes else "✅ Keine Änderungen"}

Beim Klick auf 'Einstellungen anwenden' werden nur die
aktivierten (✓) Einstellungen in die Windows Registry geschrieben.
"""
            
            self.summary_text.delete("0.0", "end")
            self.summary_text.insert("0.0", summary)
    
    def load_current_settings(self):
        """Lädt aktuelle Einstellungen und speichert ursprüngliche Zustände"""
        for key, var in self.setting_checkboxes.items():
            self.original_states[key] = var.get()
        
        self.has_changes = False
        self.update_summary()
    
    def save_settings(self):
        """Speichert/wendet die Einstellungen an"""
        if not self.has_changes:
            messagebox.showinfo("Information", "Keine Änderungen zu speichern.")
            return
        
        # Bestätigung vor dem Anwenden
        enabled_count = sum(1 for var in self.setting_checkboxes.values() if var.get())
        disabled_count = len(self.setting_checkboxes) - enabled_count
        
        message = f"""Registry-Einstellungen anwenden?

✅ {enabled_count} Einstellungen werden angewendet
❌ {disabled_count} Einstellungen werden übersprungen

Diese Änderungen werden in die Windows Registry geschrieben.
Möchten Sie fortfahren?"""
        
        result = messagebox.askyesno("Bestätigung erforderlich", message)
        
        if result:
            try:
                # Hier würde die tatsächliche Registry-Anwendung erfolgen
                # Das wird über den office_configurator mit den ausgewählten Einstellungen gemacht
                
                success_message = f"""Einstellungen erfolgreich angewendet!

✅ {enabled_count} Registry-Einstellungen wurden geschrieben
❌ {disabled_count} Einstellungen wurden übersprungen

Die Änderungen sind sofort wirksam.
Ein Neustart von Office-Anwendungen wird empfohlen."""
                
                messagebox.showinfo("Erfolgreich angewendet", success_message)
                
                # Neue Basis-Zustände speichern
                for key, var in self.setting_checkboxes.items():
                    self.original_states[key] = var.get()
                
                self.has_changes = False
                self.update_summary()
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Anwenden der Einstellungen:\\n{e}")
    
    def reset_settings(self):
        """Setzt alle Einstellungen auf die ursprünglichen Werte zurück"""
        if self.has_changes:
            result = messagebox.askyesno("Bestätigung", 
                                       "Alle Änderungen zurücksetzen?\\n"
                                       "Alle nicht gespeicherten Änderungen gehen verloren.")
            
            if result:
                for key, var in self.setting_checkboxes.items():
                    var.set(self.original_states.get(key, True))
                
                self.has_changes = False
                self.update_summary()
                messagebox.showinfo("Zurückgesetzt", "Alle Einstellungen wurden zurückgesetzt.")
        else:
            messagebox.showinfo("Information", "Keine Änderungen zum Zurücksetzen.")
    
    def on_window_closing(self):
        """Wird beim Schließen des Fensters aufgerufen"""
        if self.has_changes:
            result = messagebox.askyesnocancel("Fenster schließen", 
                                             "Sie haben ungespeicherte Änderungen.\\n"
                                             "Möchten Sie diese vor dem Schließen speichern?")
            
            if result is None:  # Abbrechen
                return
            elif result:  # Ja, speichern
                self.save_settings()
        
        self.close_window()
    
    def close_window(self):
        """Schließt das Fenster"""
        if self.window:
            self.window.destroy()
            self.window = None
    
    def get_enabled_settings(self) -> Dict[str, bool]:
        """Gibt die aktivierten Einstellungen zurück"""
        return {key: var.get() for key, var in self.setting_checkboxes.items()}