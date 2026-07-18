from __future__ import annotations

import unittest

from terminal_quest.filesystem import VirtualFileSystem
from terminal_quest.version_control import VirtualRepository


class VersionControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fs = VirtualFileSystem()
        self.fs.load_snapshot(cwd="/repo", dirs=["/repo"], files={"/repo/plan.txt": "Hoth"})
        self.repo = VirtualRepository(self.fs)

    def test_status_diff_stage_commit_and_log(self) -> None:
        self.fs.write_file("plan.txt", "Endor")

        self.assertIn("Changes not staged", self.repo.status())
        self.assertIn("-Hoth", self.repo.diff())
        self.assertIn("+Endor", self.repo.diff())
        self.repo.add_all()
        self.assertIn("Changes staged", self.repo.status())
        self.assertIn("Choose Endor", self.repo.commit("Choose Endor"))
        self.assertIn("Choose Endor", self.repo.log())

    def test_branch_commit_and_merge_updates_main(self) -> None:
        self.repo.branch("alternate")
        self.repo.switch("alternate")
        self.fs.write_file("plan.txt", "Dagobah")
        self.repo.add_all()
        self.repo.commit("Try Dagobah")
        self.repo.switch("main")

        result = self.repo.merge("alternate")

        self.assertIn("Merged alternate into main", result)
        self.assertEqual(self.fs.read_file("plan.txt"), "Dagobah")


if __name__ == "__main__":
    unittest.main()
