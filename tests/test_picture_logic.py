from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game_core.planning import ExecutionPlan
from picture_logic.engine import PictureWorld, run_picture_plan
from picture_logic.game import PICTURE_SAVE_FILE, PictureLogicGame
from picture_logic.missions import build_picture_missions
from terminal_quest.game import SAVE_FILE as TERMINAL_SAVE_FILE


class PictureLogicTests(unittest.TestCase):
    def test_picture_and_terminal_games_use_different_save_files(self) -> None:
        self.assertNotEqual(PICTURE_SAVE_FILE, TERMINAL_SAVE_FILE)

    def test_default_picture_game_opens_click_interface(self) -> None:
        game = PictureLogicGame(save_enabled=False, start_level=3, reset_progress=True)

        with patch("picture_logic.game.launch_picture_browser", return_value=True) as launch:
            with redirect_stdout(io.StringIO()):
                game.run()

        launch.assert_called_once_with(
            save_enabled=False,
            start_level=3,
            reset_progress=True,
        )

    def test_every_mission_has_a_working_picture_plan(self) -> None:
        for mission in build_picture_missions():
            with self.subTest(mission=mission.name):
                plan = ExecutionPlan()
                for action in mission.solution:
                    plan.add(action, source="picture")

                result = run_picture_plan(mission, plan)

                self.assertTrue(result.complete)
                self.assertTrue(all(step.source == "picture" for step in plan.steps))

    def test_plan_stops_when_a_picture_move_hits_a_rock(self) -> None:
        mission = next(
            mission for mission in build_picture_missions() if mission.name == "Around the Rock"
        )
        plan = ExecutionPlan()
        plan.add("forward", source="picture")
        plan.add("left", source="picture")

        result = run_picture_plan(mission, plan)

        self.assertFalse(result.complete)
        self.assertEqual(result.run.stopped_at, 1)
        self.assertIn("rock", result.run.latest.error.lower())
        self.assertEqual(result.world.position, mission.start)

    def test_running_a_plan_starts_from_a_fresh_mission_world(self) -> None:
        mission = build_picture_missions()[0]
        first_world = PictureWorld(mission)
        first_world.execute("forward")
        plan = ExecutionPlan()
        plan.add("forward", source="picture")

        result = run_picture_plan(mission, plan)

        self.assertTrue(result.complete)
        self.assertIsNot(result.world, first_world)

    def test_picture_game_is_playable_without_terminal_commands(self) -> None:
        choices = iter(["1", "run", "exit"])
        output: list[str] = []
        game = PictureLogicGame(
            save_enabled=False,
            input_fn=lambda _prompt: next(choices),
            output_fn=output.append,
        )

        game.run()

        self.assertEqual(game.current_index, 1)
        self.assertEqual(game.stars, 1)
        self.assertTrue(any("Mission complete" in line for line in output))
        self.assertTrue(any("PICTURE CARDS" in line for line in output))
        self.assertEqual(output[-1], "See you next time! 👋")

    def test_tries_and_hints_do_not_reduce_the_thinking_badge(self) -> None:
        choices = iter(["1 1", "run", "clear", "hint", "1", "run", "exit"])
        game = PictureLogicGame(
            save_enabled=False,
            input_fn=lambda _prompt: next(choices),
            output_fn=lambda _line: None,
        )

        game.run()

        self.assertEqual(game.current_index, 1)
        self.assertEqual(game.stars, 1)

    def test_curriculum_is_gradual_and_includes_debugging(self) -> None:
        missions = build_picture_missions()

        self.assertTrue(all(len(mission.solution) <= 3 for mission in missions[:5]))
        self.assertTrue(all(len(mission.hints) >= 2 for mission in missions))
        debugging = next(mission for mission in missions if mission.skill == "TRY AND CHANGE")
        self.assertTrue(debugging.starter_plan)
        self.assertNotEqual(debugging.starter_plan, debugging.solution)


if __name__ == "__main__":
    unittest.main()
