from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from game_core.planning import (
    ExecutionPlan,
    PlanRunResult,
    PlanStep,
    PlanStepper,
    PlanStepResult as CoreStepResult,
)
from picture_logic.missions import ACTION_CARDS, PictureMission, Position


DIRECTIONS = ("north", "east", "south", "west")
DIRECTION_VECTORS: dict[str, Position] = {
    "north": (0, -1),
    "east": (1, 0),
    "south": (0, 1),
    "west": (-1, 0),
}
DIRECTION_PICTURES = {
    "north": "⬆️",
    "east": "➡️",
    "south": "⬇️",
    "west": "⬅️",
}


@dataclass(frozen=True)
class PictureStepResult:
    action: str
    message: str
    board: str
    error: str = ""


class PictureWorld:
    def __init__(self, mission: PictureMission) -> None:
        self.mission = mission
        self.position = mission.start
        self.facing = mission.facing
        self.remaining_stars = set(mission.stars)

    @property
    def complete(self) -> bool:
        return self.position == self.mission.goal and not self.remaining_stars

    def execute(self, action: str) -> PictureStepResult:
        if action == "forward":
            error = self._move_forward()
            message = "BB-8 moved one space."
        elif action == "left":
            self._turn(-1)
            error = ""
            message = "BB-8 turned left."
        elif action == "right":
            self._turn(1)
            error = ""
            message = "BB-8 turned right."
        elif action == "collect":
            error = self._collect(required=True)
            message = "BB-8 picked up the star map."
        elif action == "repeat2":
            error = self._move_forward()
            if not error:
                error = self._move_forward()
            message = "The repeat booster moved BB-8 two spaces."
        elif action == "if_collect":
            collected = self.position in self.remaining_stars
            error = self._collect(required=False)
            message = (
                "The check found a star, so BB-8 picked it up."
                if collected
                else "The check found no star, so BB-8 safely skipped the pickup."
            )
        else:
            error = f"Unknown picture card: {action}"
            message = "BB-8 could not read that card."

        if error:
            message = "The plan paused so you can change it."
        return PictureStepResult(action, message, self.render(), error)

    def render(self) -> str:
        rows: list[str] = []
        for y in range(self.mission.height):
            cells: list[str] = []
            for x in range(self.mission.width):
                position = (x, y)
                if position == self.position:
                    picture = DIRECTION_PICTURES[self.facing]
                elif position in self.mission.obstacles:
                    picture = "🪨"
                elif position in self.remaining_stars:
                    picture = "⭐"
                elif position == self.mission.goal:
                    picture = "🏁"
                else:
                    picture = "▫️"
                cells.append(picture)
            rows.append(" ".join(cells))
        return "\n".join(rows)

    def to_dict(self) -> dict[str, object]:
        return {
            "position": list(self.position),
            "facing": self.facing,
            "remaining_stars": [list(position) for position in sorted(self.remaining_stars)],
            "complete": self.complete,
        }

    def _move_forward(self) -> str:
        dx, dy = DIRECTION_VECTORS[self.facing]
        destination = (self.position[0] + dx, self.position[1] + dy)
        x, y = destination
        if not (0 <= x < self.mission.width and 0 <= y < self.mission.height):
            return "BB-8 reached the edge of the board."
        if destination in self.mission.obstacles:
            return "A space rock blocks that move."
        self.position = destination
        return ""

    def _turn(self, amount: int) -> None:
        index = DIRECTIONS.index(self.facing)
        self.facing = DIRECTIONS[(index + amount) % len(DIRECTIONS)]

    def _collect(self, *, required: bool) -> str:
        if self.position in self.remaining_stars:
            self.remaining_stars.remove(self.position)
            return ""
        return "There is no star under BB-8." if required else ""


@dataclass(frozen=True)
class PicturePlanResult:
    world: PictureWorld
    run: PlanRunResult[PictureStepResult]

    @property
    def complete(self) -> bool:
        return self.run.completed and self.world.complete


class PicturePlanSession:
    """One animated attempt, advanced by a UI between visual frames."""

    def __init__(self, mission: PictureMission, plan: ExecutionPlan) -> None:
        self.world = PictureWorld(mission)
        self.stepper = PlanStepper[PictureStepResult](
            plan,
            self.world.execute,
            lambda result: bool(result.error),
        )

    @property
    def finished(self) -> bool:
        return self.stepper.finished

    @property
    def complete(self) -> bool:
        return self.finished and self.stepper.stopped_at is None and self.world.complete

    def advance(self) -> CoreStepResult[PictureStepResult] | None:
        return self.stepper.advance()


def run_picture_plan(
    mission: PictureMission,
    plan: ExecutionPlan,
    *,
    before_step: Callable[[PlanStep, int, int], None] | None = None,
    after_step: Callable[[PictureStepResult], None] | None = None,
) -> PicturePlanResult:
    session = PicturePlanSession(mission, plan)
    results: list[PictureStepResult] = []
    while not session.finished:
        next_index = session.stepper.cursor + 1
        if before_step is not None:
            before_step(session.stepper.steps[next_index - 1], next_index, len(session.stepper.steps))
        progress = session.advance()
        assert progress is not None
        results.append(progress.result)
        if after_step is not None:
            after_step(progress.result)
    result = PlanRunResult(tuple(results), stopped_at=session.stepper.stopped_at)
    return PicturePlanResult(session.world, result)


def picture_for_action(action: str) -> str:
    card = ACTION_CARDS[action]
    return f"{card.picture} {card.name}"
