from __future__ import annotations

from typing import Callable

from ui.theme import get_status_color


class ExecutionRunController:
    """Kapselt Fortschritts-/Schrittanzeige und Live-Log für Ausführungen."""

    def __init__(
        self,
        run_on_ui: Callable[[Callable[[], None]], None],
        state_label,
        progress_bar,
        steps_label,
        status_textbox,
    ) -> None:
        self.run_on_ui = run_on_ui
        self.state_label = state_label
        self.progress_bar = progress_bar
        self.steps_label = steps_label
        self.status_textbox = status_textbox

        self.steps: list[str] = []
        self.step_index = -1
        self.log_buffer: list[str] = []

    @staticmethod
    def _steps_for_mode(mode: str) -> list[str]:
        if mode == "office":
            return [
                "Schriften installieren",
                "Edge-Profile wiederherstellen",
                "Office konfigurieren",
                "Edge-Profile und E-Mail-Signaturen aktualisieren",
                "Abschluss",
            ]
        return [
            "System-Check",
            "Schriften installieren",
            "Edge-Profile wiederherstellen",
            "Office konfigurieren",
            "Templates verarbeiten",
            "Edge-Profile und E-Mail-Signaturen aktualisieren",
            "Abschluss",
        ]

    def _render_steps(self) -> None:
        lines = []
        for idx, label in enumerate(self.steps):
            mark = "☑" if idx <= self.step_index else "☐"
            lines.append(f"{mark} {label}")
        text = "\n".join(lines) if lines else "☐ Bereit"
        self.steps_label.configure(text=text)

    def _set_state(self, kind: str, text: str) -> None:
        color = get_status_color(kind)
        self.state_label.configure(text=text, text_color=color)

    def _setup_status_tags(self) -> None:
        """Definiert semantische Text-Tags für Live-Statusausgaben."""
        try:
            self.status_textbox.tag_config("status_info", foreground=get_status_color("info")[0])
            self.status_textbox.tag_config("status_success", foreground=get_status_color("success")[0])
            self.status_textbox.tag_config("status_warning", foreground=get_status_color("warning")[0])
            self.status_textbox.tag_config("status_error", foreground=get_status_color("error")[0])
        except Exception:
            pass

    @staticmethod
    def _classify_status_tag(text: str) -> str:
        upper = text.upper()
        if any(token in upper for token in ("FEHLER", "ERROR", "❌", "ABBRUCH")):
            return "status_error"
        if any(token in upper for token in ("WARN", "⚠", "HINWEIS")):
            return "status_warning"
        if any(token in upper for token in ("OK", "ERFOLG", "✅", "FERTIG", "ABGESCHLOSSEN")):
            return "status_success"
        return "status_info"

    def preview(self, mode: str = "full") -> None:
        self.steps = self._steps_for_mode(mode)
        self.step_index = -1

        def _update() -> None:
            self._setup_status_tags()
            self._render_steps()
            self.progress_bar.set(0)

        self.run_on_ui(_update)

    def reset(self, mode: str, title: str) -> None:
        self.steps = self._steps_for_mode(mode)
        self.step_index = -1
        self.log_buffer = [title]

        def _update() -> None:
            self._setup_status_tags()
            self.status_textbox.delete("0.0", "end")
            self.status_textbox.insert("0.0", title)
            self.progress_bar.set(0)
            self._render_steps()
            self._set_state("info", "Läuft ...")

        self.run_on_ui(_update)

    def append_status(self, text: str) -> None:
        self.log_buffer.append(text)

        def _update() -> None:
            tag = self._classify_status_tag(text)
            self.status_textbox.insert("end", text, tag)
            self.status_textbox.see("end")

        self.run_on_ui(_update)

    def advance(self, detail: str | None = None) -> None:
        self.step_index = min(self.step_index + 1, len(self.steps) - 1)

        def _update() -> None:
            if self.steps:
                self.progress_bar.set((self.step_index + 1) / len(self.steps))
            self._render_steps()

        self.run_on_ui(_update)
        if detail:
            self.append_status(detail)

    def finish(self, success: bool) -> None:
        def _update() -> None:
            if success:
                self.step_index = len(self.steps) - 1
                self.progress_bar.set(1)
                self._render_steps()
                self._set_state("success", "Erfolgreich abgeschlossen")
            else:
                self._set_state("error", "Mit Fehler beendet")

        self.run_on_ui(_update)

    def get_log_text(self) -> str:
        return "".join(self.log_buffer).strip()
