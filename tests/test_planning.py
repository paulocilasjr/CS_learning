from __future__ import annotations

import unittest

from terminal_quest.planning import ExecutionPlan, PlanRunner


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

    def test_empty_steps_are_rejected(self) -> None:
        plan = ExecutionPlan()

        with self.assertRaises(ValueError):
            plan.add("   ")


if __name__ == "__main__":
    unittest.main()
