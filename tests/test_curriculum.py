from __future__ import annotations

import unittest
from dataclasses import dataclass

from terminal_quest.curriculum import (
    SKILLS,
    MissionType,
    campaign_errors,
    skill_graph_errors,
    validate_campaign,
)
from terminal_quest.tasks import build_tasks


@dataclass(frozen=True)
class ExampleMission:
    number: int
    mission_type: MissionType
    new_skills: tuple[str, ...] = ()
    review_skills: tuple[str, ...] = ()


class CurriculumTests(unittest.TestCase):
    def test_skill_graph_is_valid(self) -> None:
        self.assertEqual(skill_graph_errors(), [])

    def test_playable_campaign_is_valid(self) -> None:
        tasks = build_tasks()

        validate_campaign(tasks)

        self.assertGreaterEqual(len(tasks), 20)
        self.assertEqual(tasks[0].new_skills, ("pwd",))
        self.assertIn(tasks[-1].mission_type, set(MissionType))

    def test_complete_campaign_introduces_every_registered_skill(self) -> None:
        introduced = {key for task in build_tasks() for key in task.new_skills}

        self.assertEqual(introduced, set(SKILLS))
        self.assertEqual(len(build_tasks()), 65)

    def test_review_before_introduction_is_rejected(self) -> None:
        missions = [
            ExampleMission(
                number=1,
                mission_type=MissionType.RECALL,
                review_skills=("ls",),
            )
        ]

        self.assertIn("reviews `ls` before it is introduced", "\n".join(campaign_errors(missions)))

    def test_missing_prerequisite_is_rejected(self) -> None:
        missions = [
            ExampleMission(
                number=1,
                mission_type=MissionType.INTRODUCE,
                new_skills=("cp",),
            )
        ]

        errors = "\n".join(campaign_errors(missions))
        self.assertIn("introduces `cp` before prerequisites", errors)
        self.assertIn("parent_paths", errors)

    def test_unknown_skill_is_rejected(self) -> None:
        missions = [
            ExampleMission(
                number=1,
                mission_type=MissionType.INTRODUCE,
                new_skills=("force_push",),
            )
        ]

        self.assertIn("unknown skill `force_push`", "\n".join(campaign_errors(missions)))


if __name__ == "__main__":
    unittest.main()
