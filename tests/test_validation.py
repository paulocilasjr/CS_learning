from __future__ import annotations

import unittest

from terminal_quest.filesystem import VirtualFileSystem
from terminal_quest.validation import Outcome, outcome_is_satisfied


class OutcomeValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = VirtualFileSystem()
        self.fs.load_snapshot(cwd="/mission", dirs=["/mission"], files={})

    def test_accepts_observable_state_and_output(self) -> None:
        self.fs.write_file("answer.txt", "FLEET: Dantooine")
        outcome = Outcome(
            cwd="/mission",
            file_contents={"answer.txt": "FLEET: Dantooine"},
            output_contains=("verified",),
            required_commands=("grep",),
        )

        self.assertTrue(
            outcome_is_satisfied(
                outcome,
                filesystem=self.fs,
                latest_output="verified result",
                command_history=["cat", "grep"],
            )
        )

    def test_rejects_wrong_or_dangerous_final_state(self) -> None:
        self.fs.write_file("tracker.dat", "active")
        outcome = Outcome(files_absent=("tracker.dat",), files_present=("map.txt",))

        self.assertFalse(
            outcome_is_satisfied(
                outcome,
                filesystem=self.fs,
                latest_output="",
                command_history=[],
            )
        )


if __name__ == "__main__":
    unittest.main()
