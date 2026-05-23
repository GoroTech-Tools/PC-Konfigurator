from __future__ import annotations

from typing import Callable


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
                "Office konfigurieren",
                "Abschluss",
            ]
        return [
            "System-Check",
            "Schriften installieren",
            "Office konfigurieren",
            "Templates verarbeiten",
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
        color = {
            "info": "#1f6aa5",
            "success": "#2e8b57",
            "warning": "#b36b00",
            "error": "#b00020",
        }.get(kind, "#1f6aa5")
        self.state_label.configure(text=text, text_color=color)

    def preview(self, mode: str = "full") -> None:
        self.steps = self._steps_for_mode(mode)
        self.step_index = -1

        def _update() -> None:
            self._render_steps()
            self.progress_bar.set(0)

        self.run_on_ui(_update)

    def reset(self, mode: str, title: str) -> None:
        self.steps = self._steps_for_mode(mode)
        self.step_index = -1
        self.log_buffer = [title]

        def _update() -> None:
            self.status_textbox.delete("0.0", "end")
            self.status_textbox.insert("0.0", title)
            self.progress_bar.set(0)
            self._render_steps()
            self._set_state("info", "Läuft ...")

        self.run_on_ui(_update)

    def append_status(self, text: str) -> None:
        self.log_buffer.append(text)

        def _update() -> None:
            self.status_textbox.insert("end", text)
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
