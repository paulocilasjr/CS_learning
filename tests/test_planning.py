from __future__ import annotations

import unittest

from game_core.planning import ExecutionPlan, PlanRunner, PlanStepper


class PlanningTests(unittest.TestCase):
    def test_plan_records_steps_in_order(self) -> None:
        plan = ExecutionPlan()

        plan.add("ls")
        plan.add("cat mission.txt")

        self.assertEqual(plan.describe(), "Plan steps:\n  1. ls\n  2. cat mission.txt")

    def test_runner_stops_on_first_error(self) -> None:
        plan = ExecutionPlan()
        plan.add("first")
        plan.add("bad")
        plan.add("never")
        runner = PlanRunner(lambda result: result.startswith("error"))

        result = runner.run(plan, lambda raw: "error: bad" if raw == "bad" else f"ok: {raw}")

        self.assertFalse(result.completed)
        self.assertEqual(result.stopped_at, 2)
        self.assertEqual(result.step_results, ("ok: first", "error: bad"))

    def test_runner_reports_each_step_before_execution(self) -> None:
        plan = ExecutionPlan()
        plan.add("first")
        plan.add("second")
        events: list[str] = []
        runner = PlanRunner(lambda _result: False)

        runner.run(
            plan,
            lambda raw: events.append(f"run:{raw}"),
            before_step=lambda step, index, total: events.append(
                f"show:{index}/{total}:{step.raw}"
            ),
        )

        self.assertEqual(
            events,
            ["show:1/2:first", "run:first", "show:2/2:second", "run:second"],
        )

    def test_empty_steps_are_rejected(self) -> None:
        plan = ExecutionPlan()

        with self.assertRaises(ValueError):
            plan.add("   ")

    def test_plan_can_undo_the_latest_step(self) -> None:
        plan = ExecutionPlan()
        plan.add("first")
        latest = plan.add("second")

        self.assertEqual(plan.undo(), latest)
        self.assertEqual([step.raw for step in plan.steps], ["first"])

    def test_stepper_advances_one_operation_at_a_time(self) -> None:
        plan = ExecutionPlan()
        plan.add("first")
        plan.add("second")
        stepper = PlanStepper(plan, lambda raw: f"done:{raw}", lambda _result: False)

        first = stepper.advance()

        self.assertEqual(first.result, "done:first")
        self.assertFalse(first.finished)
        self.assertEqual(stepper.cursor, 1)
        second = stepper.advance()
        self.assertEqual(second.result, "done:second")
        self.assertTrue(second.finished)
        self.assertIsNone(stepper.advance())


if __name__ == "__main__":
    unittest.main()
