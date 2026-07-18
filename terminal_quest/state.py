from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from terminal_quest.curriculum import MasteryStage, MissionType


MASTERY_TARGETS = {
    MissionType.INTRODUCE: MasteryStage.INTRODUCED,
    MissionType.PRACTICE: MasteryStage.GUIDED,
    MissionType.RECALL: MasteryStage.RECALLED,
    MissionType.TRANSFER: MasteryStage.TRANSFERRED,
    MissionType.COMBINE: MasteryStage.INTEGRATED,
    MissionType.DEBUG: MasteryStage.INTEGRATED,
    MissionType.CAPSTONE: MasteryStage.INTEGRATED,
}


@dataclass
class SkillProgress:
    mastery: int = MasteryStage.UNSEEN
    attempts: int = 0
    hints_used: int = 0
    independent_successes: int = 0
    last_practiced: str = ""

    def record(self, mission_type: MissionType, *, attempts: int, hints_used: int) -> None:
        target = MASTERY_TARGETS[mission_type]
        if hints_used:
            target = min(target, MasteryStage.GUIDED)

        self.mastery = max(self.mastery, int(target))
        self.attempts += attempts + 1
        self.hints_used += hints_used
        if attempts == 0 and hints_used == 0:
            self.independent_successes += 1
        self.last_practiced = datetime.now(timezone.utc).isoformat(timespec="seconds")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SkillProgress":
        return cls(
            mastery=int(data.get("mastery", 0)),
            attempts=int(data.get("attempts", 0)),
            hints_used=int(data.get("hints_used", 0)),
            independent_successes=int(data.get("independent_successes", 0)),
            last_practiced=str(data.get("last_practiced", "")),
        )

@dataclass
class LearningState:
    skills: dict[str, SkillProgress] = field(default_factory=dict)
    completed_challenges: list[int] = field(default_factory=list)
    review_queue: list[str] = field(default_factory=list)

    def record_mission(
        self,
        *,
        mission_number: int,
        mission_type: MissionType,
        skills: tuple[str, ...],
        attempts: int,
        hints_used: int,
    ) -> None:
        for key in skills:
            progress = self.skills.setdefault(key, SkillProgress())
            progress.record(mission_type, attempts=attempts, hints_used=hints_used)

        if mission_number not in self.completed_challenges:
            self.completed_challenges.append(mission_number)
        self._refresh_review_queue()

    def _refresh_review_queue(self) -> None:
        self.review_queue = sorted(
            key
            for key, progress in self.skills.items()
            if progress.mastery < MasteryStage.RECALLED
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skills": {key: asdict(value) for key, value in sorted(self.skills.items())},
            "completed_challenges": self.completed_challenges,
            "review_queue": self.review_queue,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningState":
        state = cls(
            skills={
                key: SkillProgress.from_dict(value)
                for key, value in dict(data.get("skills", {})).items()
            },
            completed_challenges=[int(value) for value in data.get("completed_challenges", [])],
            review_queue=[str(value) for value in data.get("review_queue", [])],
        )
        state._refresh_review_queue()
        return state


@dataclass
class StoryState:
    current_episode: str = "1"
    current_mission: int = 1
    unlocked_locations: list[str] = field(default_factory=lambda: ["yavin-4"])
    characters_met: list[str] = field(default_factory=lambda: ["Leia", "R2-D2"])
    completed_objectives: list[int] = field(default_factory=list)
    story_flags: dict[str, bool] = field(default_factory=dict)
    rewards: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StoryState":
        return cls(
            current_episode=str(data.get("current_episode", "1")),
            current_mission=int(data.get("current_mission", 1)),
            unlocked_locations=[str(value) for value in data.get("unlocked_locations", ["yavin-4"])],
            characters_met=[str(value) for value in data.get("characters_met", ["Leia", "R2-D2"])],
            completed_objectives=[int(value) for value in data.get("completed_objectives", [])],
            story_flags={str(key): bool(value) for key, value in dict(data.get("story_flags", {})).items()},
            rewards=[str(value) for value in data.get("rewards", [])],
        )
