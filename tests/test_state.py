from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from terminal_quest.curriculum import MasteryStage, MissionType
from terminal_quest.learning import ReviewEngine
from game_core.persistence import ProgressStore
from terminal_quest.state import LearningState, StoryState


class StateTests(unittest.TestCase):
    def test_independent_recall_advances_mastery(self) -> None:
        state = LearningState()
        state.record_mission(
            mission_number=1,
            mission_type=MissionType.INTRODUCE,
            skills=("ls",),
            attempts=0,
            hints_used=0,
        )
        state.record_mission(
            mission_number=2,
            mission_type=MissionType.RECALL,
            skills=("ls",),
            attempts=0,
            hints_used=0,
        )

        self.assertEqual(state.skills["ls"].mastery, MasteryStage.RECALLED)
        self.assertEqual(state.skills["ls"].independent_successes, 2)
        self.assertNotIn("ls", state.review_queue)

    def test_hint_caps_new_evidence_and_queues_review(self) -> None:
        state = LearningState()
        state.record_mission(
            mission_number=1,
            mission_type=MissionType.TRANSFER,
            skills=("cd",),
            attempts=1,
            hints_used=1,
        )

        self.assertEqual(state.skills["cd"].mastery, MasteryStage.GUIDED)
        self.assertIn("cd", state.review_queue)

    def test_learning_and_story_state_round_trip(self) -> None:
        learning = LearningState()
        learning.record_mission(
            mission_number=7,
            mission_type=MissionType.COMBINE,
            skills=("grep", "pipes"),
            attempts=0,
            hints_used=0,
        )
        story = StoryState(story_flags={"tracker_destroyed": True}, rewards=["Analyst"])

        restored_learning = LearningState.from_dict(learning.to_dict())
        restored_story = StoryState.from_dict(story.to_dict())

        self.assertEqual(restored_learning.skills["grep"].mastery, MasteryStage.INTEGRATED)
        self.assertTrue(restored_story.story_flags["tracker_destroyed"])
        self.assertEqual(restored_story.rewards, ["Analyst"])

    def test_review_engine_prioritizes_weaker_skill(self) -> None:
        state = LearningState()
        state.record_mission(
            mission_number=1,
            mission_type=MissionType.INTRODUCE,
            skills=("cd",),
            attempts=2,
            hints_used=1,
        )
        state.record_mission(
            mission_number=2,
            mission_type=MissionType.COMBINE,
            skills=("ls",),
            attempts=0,
            hints_used=0,
        )

        self.assertEqual(ReviewEngine().recommend(state, limit=1), ["cd"])

    def test_progress_store_round_trip_and_clear(self) -> None:
        with TemporaryDirectory() as directory:
            store = ProgressStore(Path(directory) / "progress.json")
            store.save({"version": 2, "stars": 12})

            self.assertEqual(store.load(), {"version": 2, "stars": 12})
            store.clear()
            self.assertFalse(store.exists())


if __name__ == "__main__":
    unittest.main()
