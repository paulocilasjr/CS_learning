from __future__ import annotations

import unittest
from unittest.mock import patch

import main as launcher


class LauncherTests(unittest.TestCase):
    def test_menu_selects_terminal_game(self) -> None:
        answers = iter(["wrong", "1"])
        output: list[str] = []

        with patch("main.TerminalQuestGame") as game_class:
            launcher.main([], input_fn=lambda _prompt: next(answers), output_fn=output.append)

        game_class.assert_called_once_with(
            save_enabled=True,
            start_task=None,
            reset_progress=False,
        )
        game_class.return_value.run.assert_called_once_with()
        self.assertIn("Please choose 1, 2, or Q.", output)

    def test_menu_selects_picture_game(self) -> None:
        answers = iter(["2"])
        output: list[str] = []
        write_output = output.append

        with patch("main.PictureLogicGame") as game_class:
            launcher.main([], input_fn=lambda _prompt: next(answers), output_fn=write_output)

        game_class.assert_called_once()
        kwargs = game_class.call_args.kwargs
        self.assertTrue(kwargs["save_enabled"])
        self.assertIsNone(kwargs["start_level"])
        self.assertIs(kwargs["output_fn"], write_output)
        game_class.return_value.run.assert_called_once_with()

    def test_start_options_infer_the_game_without_menu(self) -> None:
        with patch("main.TerminalQuestGame") as terminal_class:
            launcher.main(["--no-save", "--start-task", "35"])
        terminal_class.assert_called_once_with(
            save_enabled=False,
            start_task=35,
            reset_progress=False,
        )

        with patch("main.PictureLogicGame") as picture_class:
            launcher.main(["--no-save", "--start-level", "8"])
        self.assertEqual(picture_class.call_args.kwargs["start_level"], 8)

    def test_game_specific_start_options_cannot_be_mixed(self) -> None:
        with self.assertRaisesRegex(SystemExit, "either --start-task or --start-level"):
            launcher.main(["--start-task", "1", "--start-level", "1"])


if __name__ == "__main__":
    unittest.main()
