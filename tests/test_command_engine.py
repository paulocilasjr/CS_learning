from __future__ import annotations

import unittest

from terminal_quest.command_engine import CommandParser
from terminal_quest.filesystem import VirtualFileSystem
from terminal_quest.game import TutorialShell


class CommandEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = VirtualFileSystem()
        self.fs.load_snapshot(
            cwd="/base",
            dirs=["/base", "/base/reports"],
            files={
                "/base/intel.txt": "REBEL: safe\nIMPERIAL: watch\nIMPERIAL: move",
                "/base/names.txt": "Zulu\nAlpha\nLeia",
            },
        )
        self.shell = TutorialShell(self.fs)

    def test_parser_preserves_operators_and_quoted_patterns(self) -> None:
        tokens = CommandParser().parse('grep "IMPERIAL: watch" intel.txt | wc -l > reports/count.txt')

        self.assertEqual(
            tokens,
            ["grep", "IMPERIAL: watch", "intel.txt", "|", "wc", "-l", ">", "reports/count.txt"],
        )

    def test_pipeline_filters_and_counts(self) -> None:
        result = self.shell.execute("cat intel.txt | grep IMPERIAL | wc -l")

        self.assertEqual(result.error, "")
        self.assertEqual(result.output, "2")
        self.assertEqual(result.executed_commands, ("cat", "grep", "wc"))

    def test_redirection_and_append_change_virtual_files_only(self) -> None:
        first = self.shell.execute("grep IMPERIAL intel.txt > reports/imperial.txt")
        second = self.shell.execute('echo "PRIORITY" >> reports/imperial.txt')

        self.assertEqual(first.error, "")
        self.assertEqual(second.error, "")
        self.assertEqual(
            self.fs.read_file("reports/imperial.txt"),
            "IMPERIAL: watch\nIMPERIAL: move\nPRIORITY",
        )

    def test_head_tail_sort_and_wildcard(self) -> None:
        self.assertEqual(self.shell.execute("head -n 1 names.txt").output, "Zulu")
        self.assertEqual(self.shell.execute("tail -n 1 names.txt").output, "Leia")
        self.assertEqual(self.shell.execute("sort names.txt").output, "Alpha\nLeia\nZulu")
        self.assertEqual(self.shell.execute("echo *.txt").output, "intel.txt names.txt")

    def test_python_edit_and_simulation_test(self) -> None:
        self.fs.write_file(
            "check.py",
            "def enough(fuel, distance):\n    return fuel < distance\n\nassert enough(5, 2) == True",
        )
        failing = self.shell.execute("test check.py")
        self.assertIn("AssertionError", failing.error)

        self.assertFalse(self.shell.execute('edit check.py 2 "    return fuel >= distance"').error)
        passing = self.shell.execute("test check.py")
        self.assertEqual(passing.output, "All Rebel simulation tests passed.")

    def test_python_runtime_blocks_host_access(self) -> None:
        self.fs.write_file("unsafe.py", "import os\nprint(os.getcwd())")

        result = self.shell.execute("python unsafe.py")

        self.assertIn("Python safety system", result.error)
        self.assertIn("Import", result.error)


if __name__ == "__main__":
    unittest.main()
