from __future__ import annotations

import unittest

from game_core.planning import ExecutionPlan
from picture_logic.engine import PictureWorld, run_picture_plan
from picture_logic.game import PICTURE_SAVE_FILE, PictureLogicGame
from picture_logic.missions import build_picture_missions
from terminal_quest.game import SAVE_FILE as TERMINAL_SAVE_FILE


class PictureLogicTests(unittest.TestCase):
    def test_picture_and_terminal_games_use_different_save_files(self) -> None:
        self.assertNotEqual(PICTURE_SAVE_FILE, TERMINAL_SAVE_FILE)

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
        mission = build_picture_missions()[3]
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
        self.assertEqual(game.stars, 3)
        self.assertTrue(any("Mission complete" in line for line in output))
        self.assertTrue(any("PICTURE CARDS" in line for line in output))
        self.assertEqual(output[-1], "See you next time! 👋")


if __name__ == "__main__":
    unittest.main()
