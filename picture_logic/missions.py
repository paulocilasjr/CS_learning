from __future__ import annotations

from dataclasses import dataclass


Position = tuple[int, int]


@dataclass(frozen=True)
class ActionCard:
    key: str
    picture: str
    name: str


ACTION_CARDS: dict[str, ActionCard] = {
    "forward": ActionCard("forward", "⬆️", "Move one space"),
    "left": ActionCard("left", "↩️", "Turn left"),
    "right": ActionCard("right", "↪️", "Turn right"),
    "collect": ActionCard("collect", "🖐️⭐", "Pick up the star"),
    "repeat2": ActionCard("repeat2", "🔁2️⃣", "Move two spaces"),
    "if_collect": ActionCard("if_collect", "❓⭐🖐️", "If on a star, pick it up"),
}


@dataclass(frozen=True)
class PictureMission:
    number: int
    name: str
    story: str
    instruction: str
    width: int
    height: int
    start: Position
    facing: str
    goal: Position
    obstacles: frozenset[Position] = frozenset()
    stars: frozenset[Position] = frozenset()
    cards: tuple[str, ...] = ("forward",)
    solution: tuple[str, ...] = ("forward",)
    hint: str = "Look at the droid, then look at the flag. Which picture moves the droid closer?"


def build_picture_missions() -> list[PictureMission]:
    return [
        PictureMission(
            1,
            "Wake Up, BB-8!",
            "BB-8 sees the Rebel flag one space away.",
            "Choose one picture card, then run the plan.",
            3,
            1,
            (0, 0),
            "east",
            (1, 0),
            solution=("forward",),
        ),
        PictureMission(
            2,
            "Two Steps to Leia",
            "Leia is waiting two spaces away.",
            "Put two move pictures in the plan.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            solution=("forward", "forward"),
            hint="A plan can use the same picture more than once.",
        ),
        PictureMission(
            3,
            "Turn Toward the Beacon",
            "The beacon is around the corner.",
            "Move, turn right, and move to the flag.",
            3,
            3,
            (0, 0),
            "east",
            (1, 1),
            cards=("forward", "right"),
            solution=("forward", "right", "forward"),
            hint="First move beside the flag. Then turn the droid toward it.",
        ),
        PictureMission(
            4,
            "Go Around the Rock",
            "A space rock blocks the straight path.",
            "Plan a safe path around the rock.",
            4,
            3,
            (0, 1),
            "east",
            (2, 1),
            obstacles=frozenset({(1, 1)}),
            cards=("forward", "left", "right"),
            solution=("left", "forward", "right", "forward", "forward", "right", "forward"),
            hint="Try going above the rock, across, and then back down.",
        ),
        PictureMission(
            5,
            "Rescue the Star Map",
            "A glowing star map lies on the path.",
            "Pick up the star before reaching the flag.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            stars=frozenset({(1, 0)}),
            cards=("forward", "collect"),
            solution=("forward", "collect", "forward"),
            hint="Move onto the star, pick it up, and then continue.",
        ),
        PictureMission(
            6,
            "Deliver the Star Map",
            "BB-8 must collect the map and carry it down the corridor.",
            "Collect the star and reach the flag.",
            3,
            4,
            (0, 0),
            "east",
            (1, 2),
            stars=frozenset({(1, 0)}),
            cards=("forward", "right", "collect"),
            solution=("forward", "collect", "right", "forward", "forward"),
            hint="After collecting the star, turn toward the bottom of the board.",
        ),
        PictureMission(
            7,
            "Repair the Route",
            "The first route crashed into a rock. Engineers change the plan and try again.",
            "Build a route that reaches the flag without touching a rock.",
            4,
            3,
            (0, 2),
            "east",
            (3, 1),
            obstacles=frozenset({(1, 2), (2, 2)}),
            cards=("forward", "left", "right"),
            solution=("left", "forward", "right", "forward", "forward", "forward"),
            hint="Turn away from the rocks before moving forward.",
        ),
        PictureMission(
            8,
            "The Repeat Booster",
            "R2-D2 can bundle two matching moves into one repeat card.",
            "Use the repeat card to reach the flag.",
            5,
            1,
            (0, 0),
            "east",
            (3, 0),
            cards=("forward", "repeat2"),
            solution=("repeat2", "forward"),
            hint="The repeat card moves two spaces. One more move finishes the route.",
        ),
        PictureMission(
            9,
            "Check Before Collecting",
            "A smart droid checks whether it is standing on a star before reaching down.",
            "Use the question card to collect the star safely.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            stars=frozenset({(1, 0)}),
            cards=("forward", "if_collect"),
            solution=("forward", "if_collect", "forward"),
            hint="Move onto the star before using the question card.",
        ),
        PictureMission(
            10,
            "The Rebel Rescue Plan",
            "The final route needs movement, turns, a repeat, and a star rescue.",
            "Collect the star and reach the flag without touching the rocks.",
            5,
            4,
            (0, 3),
            "east",
            (4, 0),
            obstacles=frozenset({(2, 3), (2, 2), (4, 1)}),
            stars=frozenset({(3, 1)}),
            cards=("forward", "left", "right", "collect", "repeat2"),
            solution=(
                "forward",
                "left",
                "repeat2",
                "right",
                "repeat2",
                "collect",
                "left",
                "forward",
                "right",
                "forward",
            ),
            hint="Travel up the left corridor, cross to the star, then turn toward the flag.",
        ),
    ]
