from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from terminal_quest.game import (
    ANSI_RESET,
    COMMAND_OUTPUT_COLOR,
    FEEDBACK_COLOR,
    HINT_COLOR,
    MISSION_COLOR,
    TASK_COLOR,
    CommandResult,
    TerminalQuestGame,
)


class TerminalUiTests(unittest.TestCase):
    def color_game(self) -> TerminalQuestGame:
        game = TerminalQuestGame(save_enabled=False)
        game._supports_color = lambda: True  # type: ignore[method-assign]
        return game

    def test_command_output_is_labeled_and_boxed(self) -> None:
        game = TerminalQuestGame(save_enabled=False)
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            game._show_result(CommandResult(raw="pwd", name="pwd", args=[], output="/galaxy/rebel_base"))

        rendered = buffer.getvalue()
        self.assertIn("+-- COMMAND OUTPUT --+", rendered)
        self.assertIn("| /galaxy/rebel_base", rendered)
        self.assertIn("+-- END COMMAND OUTPUT --+", rendered)

    def test_command_error_uses_distinct_label(self) -> None:
        game = TerminalQuestGame(save_enabled=False)
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            game._show_result(CommandResult(raw="bogus", name="bogus", args=[], error="Unknown command: bogus"))

        rendered = buffer.getvalue()
        self.assertIn("+-- COMMAND ERROR --+", rendered)
        self.assertIn("| Unknown command: bogus", rendered)
        self.assertIn("+-- END COMMAND ERROR --+", rendered)

    def test_color_supported_command_output_uses_command_color(self) -> None:
        game = self.color_game()
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            game._show_result(CommandResult(raw="pwd", name="pwd", args=[], output="/galaxy/rebel_base"))

        rendered = buffer.getvalue()
        self.assertIn(f"{COMMAND_OUTPUT_COLOR}+-- COMMAND OUTPUT --+{ANSI_RESET}", rendered)

    def test_mission_and_task_text_have_distinct_colors(self) -> None:
        game = self.color_game()
        task = game.tasks[0]
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            game._show_task(task)

        rendered = buffer.getvalue()
        self.assertIn(f"{MISSION_COLOR}\nMISSION 1/", rendered)
        self.assertIn(f"{TASK_COLOR}YOUR TASK:", rendered)

    def test_feedback_and_hints_have_distinct_colors_and_labels(self) -> None:
        game = self.color_game()
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            game._show_feedback("Inspect the result and continue.")
            game._show_hint("Use `pwd`.")

        rendered = buffer.getvalue()
        self.assertIn(f"{FEEDBACK_COLOR}Mission feedback:", rendered)
        self.assertIn(f"{HINT_COLOR}Hint:", rendered)


if __name__ == "__main__":
    unittest.main()
