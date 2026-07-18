from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from terminal_quest.game import CommandResult, TerminalQuestGame


class TerminalUiTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
