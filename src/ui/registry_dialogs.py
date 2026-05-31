from __future__ import annotations

import customtkinter as ctk


def show_gpo_theme_check_dialog(root) -> None:
    """Zeigt die GPO-Prüfung auf Office-Design-Richtlinien in einem Dialogfenster."""
    from registry_explainer import RegistryExplainer

    result = RegistryExplainer().check_gpo_office_theme()

    win = ctk.CTkToplevel(root)
    win.title("GPO-Design-Prüfung")
    win.geometry("820x540")
    win.lift()
    win.focus_force()
    win.grab_set()

    if result["gpo_active"]:
        if result["theme_related_count"] > 0:
            status = (
                f"⚠ GPO aktiv – {result['theme_related_count']} Theme-bezogene(r) Eintrag/Einträge "
                f"gefunden (gesamt: {result['all_entries_count']})"
            )
            color = "#e07800"
        else:
            status = (
                f"ℹ GPO aktiv – {result['all_entries_count']} Office-Richtlinie(n), "
                "kein direkter Theme-Eintrag"
            )
            color = "#1f6aa5"
    else:
        status = "✓ Keine Office-Gruppenrichtlinien für Themes/Designs gefunden."
        color = "#2e8b57"

    ctk.CTkLabel(
        win,
        text=status,
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=color,
        wraplength=780,
        justify="left",
    ).pack(anchor="w", padx=16, pady=(14, 4))

    ctk.CTkLabel(
        win,
        text=result["recommendation"],
        wraplength=780,
        justify="left",
    ).pack(anchor="w", padx=16, pady=(0, 8))

    lines = ["Geprüfte Registry-Pfade:"]
    for p in result["checked_paths"]:
        lines.append(f"  {p}")
    if result["entries"]:
        lines.append("")
        lines.append("Gefundene Richtlinien-Einträge:")
        for e in result["entries"]:
            marker = " [⚠ THEME]" if e["theme_related"] else ""
            lines.append(f"  {e['path']}")
            lines.append(f"    {e['name']} = {e['data']!r}{marker}")
    else:
        lines.append("")
        lines.append("Keine Richtlinien-Einträge gefunden.")

    box = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=11))
    box.pack(fill="both", expand=True, padx=16, pady=(0, 8))
    box.insert("0.0", "\n".join(lines))
    box.configure(state="disabled")

    ctk.CTkButton(win, text="Schließen", command=win.destroy).pack(pady=(0, 12))
