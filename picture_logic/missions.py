from __future__ import annotations

from dataclasses import dataclass


Position = tuple[int, int]


@dataclass(frozen=True)
class ActionCard:
    key: str
    picture: str
    name: str
    spoken_name: str


ACTION_CARDS: dict[str, ActionCard] = {
    "forward": ActionCard("forward", "👣", "GO", "move forward one space"),
    "left": ActionCard("left", "↶", "LEFT", "turn left"),
    "right": ActionCard("right", "↷", "RIGHT", "turn right"),
    "collect": ActionCard("collect", "⭐", "GET", "pick up the star"),
    "repeat2": ActionCard("repeat2", "👣×2", "GO 2", "move forward two spaces"),
    "if_collect": ActionCard(
        "if_collect",
        "⭐?",
        "CHECK",
        "if BB-8 is on a star, pick it up",
    ),
}


@dataclass(frozen=True)
class PictureMission:
    number: int
    name: str
    skill: str
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
    hints: tuple[str, ...] = (
        "Look at BB-8, then look at the flag.",
        "Choose the card that moves BB-8 closer.",
    )
    starter_plan: tuple[str, ...] = ()
    max_steps: int = 10

    @property
    def hint(self) -> str:
        return self.hints[0]


def build_picture_missions() -> list[PictureMission]:
    """Small, gradual challenges designed around an age-five learning rhythm."""

    return [
        PictureMission(
            1,
            "Hello, BB-8!",
            "ONE STEP",
            "The flag is very close.",
            "Help BB-8 go to the flag.",
            3,
            1,
            (0, 0),
            "east",
            (1, 0),
            solution=("forward",),
            hints=("Tap the feet card.", "Your plan needs one GO card."),
            max_steps=3,
        ),
        PictureMission(
            2,
            "Go, Go!",
            "ORDER",
            "The flag is two spaces away.",
            "Make a plan with two steps.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            solution=("forward", "forward"),
            hints=("One GO is not enough yet.", "Tap GO two times."),
            max_steps=4,
        ),
        PictureMission(
            3,
            "Turn Right",
            "DIRECTION",
            "BB-8 is looking up. The flag is on the right.",
            "Turn toward the flag, then go.",
            4,
            3,
            (1, 1),
            "north",
            (2, 1),
            cards=("forward", "right"),
            solution=("right", "forward"),
            hints=("First make BB-8 look right.", "Tap RIGHT, then GO."),
            max_steps=4,
        ),
        PictureMission(
            4,
            "Turn Left",
            "DIRECTION",
            "BB-8 is looking down. The flag is on the right.",
            "Turn the other way, then go.",
            4,
            3,
            (1, 1),
            "south",
            (2, 1),
            cards=("forward", "left"),
            solution=("left", "forward"),
            hints=("Which turn makes BB-8 look right?", "Tap LEFT, then GO."),
            max_steps=4,
        ),
        PictureMission(
            5,
            "Save the Star",
            "GOAL FIRST",
            "A star map is waiting on the path.",
            "Get the star, then reach the flag.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            stars=frozenset({(1, 0)}),
            cards=("forward", "collect"),
            solution=("forward", "collect", "forward"),
            hints=("BB-8 must stand on the star before getting it.", "Tap GO, GET, GO."),
            max_steps=5,
        ),
        PictureMission(
            6,
            "Around the Rock",
            "PLAN AROUND",
            "The straight path is blocked.",
            "Find a safe way around the rock.",
            3,
            2,
            (0, 1),
            "east",
            (1, 0),
            obstacles=frozenset({(1, 1)}),
            cards=("forward", "left", "right"),
            solution=("left", "forward", "right", "forward"),
            hints=("Turn away before moving into the rock.", "Tap LEFT, GO, RIGHT, GO."),
            max_steps=7,
        ),
        PictureMission(
            7,
            "Carry the Map",
            "COMBINE",
            "The map must travel around a corner.",
            "Get the star and carry it to the flag.",
            3,
            3,
            (0, 0),
            "east",
            (1, 1),
            stars=frozenset({(1, 0)}),
            cards=("forward", "right", "collect"),
            solution=("forward", "collect", "right", "forward"),
            hints=("Get the star before turning.", "Tap GO, GET, RIGHT, GO."),
            max_steps=7,
        ),
        PictureMission(
            8,
            "Fix the Plan",
            "TRY AND CHANGE",
            "R2-D2 made a plan, but a rock is in the way.",
            "Try the plan. Notice what happens. Then fix it.",
            3,
            2,
            (0, 0),
            "east",
            (1, 1),
            obstacles=frozenset({(1, 0)}),
            cards=("forward", "left", "right"),
            solution=("right", "forward", "left", "forward"),
            hints=("The first GO hits the rock. Remove it and turn.", "Tap RIGHT, GO, LEFT, GO."),
            starter_plan=("forward",),
            max_steps=7,
        ),
        PictureMission(
            9,
            "The Go-Two Card",
            "REPEAT",
            "A new card can do two matching moves.",
            "Use GO 2 to make a shorter plan.",
            5,
            1,
            (0, 0),
            "east",
            (3, 0),
            cards=("forward", "repeat2"),
            solution=("repeat2", "forward"),
            hints=("GO 2 moves across two spaces.", "Tap GO 2, then GO."),
            max_steps=4,
        ),
        PictureMission(
            10,
            "Check for a Star",
            "IF THIS, THEN THAT",
            "The CHECK card looks before it acts.",
            "Move onto the star and use CHECK.",
            4,
            1,
            (0, 0),
            "east",
            (2, 0),
            stars=frozenset({(1, 0)}),
            cards=("forward", "if_collect"),
            solution=("forward", "if_collect", "forward"),
            hints=("CHECK only gets a star under BB-8.", "Tap GO, CHECK, GO."),
            max_steps=5,
        ),
        PictureMission(
            11,
            "Choose the Safe Route",
            "BREAK IT DOWN",
            "The safe route has a turn, a repeat, and a star.",
            "Get the star and reach the flag.",
            4,
            3,
            (0, 2),
            "east",
            (2, 0),
            obstacles=frozenset({(1, 2)}),
            stars=frozenset({(2, 1)}),
            cards=("forward", "left", "right", "collect", "repeat2"),
            solution=("left", "forward", "right", "repeat2", "collect", "left", "forward"),
            hints=(
                "First go above the rock. Then travel to the star.",
                "Try LEFT, GO, RIGHT, GO 2, GET, LEFT, GO.",
            ),
            max_steps=10,
        ),
        PictureMission(
            12,
            "The Big Rescue",
            "SOLVE IT",
            "This mission needs everything you practiced.",
            "Plan, try, notice, and change until the rescue works.",
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
            hints=(
                "Solve one small part at a time: up, across, star, flag.",
                "Go beside the rock, travel up, cross to the star, then turn to the flag.",
            ),
            max_steps=12,
        ),
    ]
