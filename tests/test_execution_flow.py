import pathlib
import sys
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from ui.execution_flow import _building_blocks_update_failed

theme_module = types.ModuleType("ui.theme")
theme_module.get_status_color = lambda kind: kind
with patch.dict(sys.modules, {"ui.theme": theme_module}):
    from ui.run_controller import ExecutionRunController


class BuildingBlocksUpdateFailureTests(unittest.TestCase):
    def test_reports_missing_or_failed_building_blocks_as_uncritical(self):
        self.assertTrue(_building_blocks_update_failed({"building_blocks": {}}))
        self.assertTrue(_building_blocks_update_failed({"building_blocks": {"Building Blocks.dotx": False}}))

    def test_does_not_report_success_or_other_template_failures_as_building_blocks_errors(self):
        self.assertFalse(_building_blocks_update_failed({"building_blocks": {"Building Blocks.dotx": True}}))
        self.assertFalse(_building_blocks_update_failed({"normal_dotm": False}))
        self.assertFalse(_building_blocks_update_failed({}))


class FinishExecutionProgressTests(unittest.TestCase):
    def _make_controller(self):
        state_label = types.SimpleNamespace(values={})
        state_label.configure = lambda **values: state_label.values.update(values)
        progress_bar = types.SimpleNamespace(set=lambda value: None)
        steps_label = types.SimpleNamespace(configure=lambda **values: None)
        status_textbox = types.SimpleNamespace()
        controller = ExecutionRunController(
            lambda callback: callback(),
            state_label,
            progress_bar,
            steps_label,
            status_textbox,
        )
        return controller, state_label

    def test_shows_uncritical_error_completion(self):
        controller, state_label = self._make_controller()

        controller.finish(success=True, uncritical_error=True)

        self.assertEqual(state_label.values["text"], "Mit unkritischem Fehler beendet")
        self.assertEqual(state_label.values["text_color"], "warning")

    def test_regular_failure_takes_precedence_over_uncritical_error(self):
        controller, state_label = self._make_controller()

        controller.finish(success=False, uncritical_error=True)

        self.assertEqual(state_label.values["text"], "Mit Fehlern beendet")
        self.assertEqual(state_label.values["text_color"], "error")

    def test_other_failures_keep_error_completion(self):
        controller, state_label = self._make_controller()

        controller.finish(success=False)

        self.assertEqual(state_label.values["text"], "Mit Fehlern beendet")
        self.assertEqual(state_label.values["text_color"], "error")


if __name__ == "__main__":
    unittest.main()
