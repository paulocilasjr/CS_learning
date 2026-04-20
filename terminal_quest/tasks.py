from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from terminal_quest.filesystem import VirtualFileSystem


@dataclass(frozen=True)
class Scenario:
    cwd: str
    dirs: list[str]
    files: dict[str, str]


@dataclass(frozen=True)
class Task:
    number: int
    chapter_key: str
    chapter_name: str
    chapter_intro: str
    name: str
    lesson: str
    instruction: str
    expected_command: str
    expected_args: list[str]
    tips: list[str]
    success: str
    scenario: Scenario


@dataclass(frozen=True)
class Chapter:
    key: str
    name: str
    intro: str
    reward: str


@dataclass(frozen=True)
class TaskSpec:
    name: str
    lesson: str
    instruction: str
    command: str
    args: tuple[str, ...] = ()
    success: str | None = None
    tips: list[str] | None = None


CHAPTERS = {
    "1": Chapter(
        key="1",
        name="Leia's First Orders",
        intro=(
            "Yavin 4 is buzzing. Leia has a mission, Han wants the Falcon ready, "
            "and your first job is to learn the Rebel base before the launch window closes."
        ),
        reward="Base Cartographer",
    ),
    "2": Chapter(
        key="2",
        name="Secrets Of The Falcon",
        intro=(
            "The Falcon looks ready from the outside, but R2-D2 has hidden intel "
            "to reveal and the ship still needs new rooms for the rescue plan."
        ),
        reward="Falcon Quartermaster",
    ),
    "3": Chapter(
        key="3",
        name="The Rescue Setup",
        intro=(
            "Leia needs the rescue room stocked, the plans copied safely, "
            "and a clean report delivered before the next chapter can begin."
        ),
        reward="Mission Planner",
    ),
}


WORLD = {
    "cwd": "/galaxy/rebel_base",
    "dirs": [
        "/galaxy",
        "/galaxy/rebel_base",
        "/galaxy/rebel_base/archive",
        "/galaxy/rebel_base/briefing_room",
        "/galaxy/rebel_base/hangar",
        "/galaxy/rebel_base/hangar/millennium_falcon",
        "/galaxy/rebel_base/hangar/millennium_falcon/cargo",
        "/galaxy/rebel_base/hangar/millennium_falcon/crew",
    ],
    "files": {
        "/galaxy/rebel_base/briefing_room/mission_briefing.txt": (
            "Leia's Message\n"
            "--------------\n"
            "Han parked the Millennium Falcon inside the hangar.\n"
            "To reach it in one move, type:\n"
            "cd hangar/millennium_falcon\n"
            "The ship is carrying the next clue."
        ),
        "/galaxy/rebel_base/briefing_room/report_terminal.txt": (
            "Leia's Reply\n"
            "------------\n"
            "You brought the crew list, the rescue room, and the plans together.\n"
            "The Falcon is ready.\n"
            "Next chapter: a jump toward Kharis Moon."
        ),
        "/galaxy/rebel_base/archive/death_star_plans.txt": (
            "Death Star Study Copy\n"
            "---------------------\n"
            "Weak point: thermal exhaust port\n"
            "Targeting support: required\n"
            "Leia's note:\n"
            "Return to /galaxy/rebel_base/briefing_room\n"
            "Then read report_terminal.txt for the next chapter."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/.escape_routes.txt": (
            "R2-D2's Hidden Route Note\n"
            "------------------------\n"
            "This file was hidden with a dot so enemies would miss it.\n"
            "The Falcon needs a new planning room.\n"
            "Create a folder named training_bay."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/faulty_hyperdrive_note.txt": (
            "Reminder: hyperdrive calibration is still unstable."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/cargo/coaxium_crate.txt": (
            "Coaxium reserve locked and sealed."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/cargo/med_kit.txt": (
            "Field med kit ready."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/cargo/tool_box.txt": (
            "Tool box stocked with repair gear."
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/crew/han_solo.txt": (
            "Han Solo\nCaptain of the Millennium Falcon"
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/crew/chewbacca.txt": (
            "Chewbacca\nCo-pilot and mechanic"
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/crew/leia_organa.txt": (
            "Leia Organa\nMission commander"
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/crew/luke_skywalker.txt": (
            "Luke Skywalker\nPilot in training"
        ),
        "/galaxy/rebel_base/hangar/millennium_falcon/crew/r2_d2.txt": (
            "R2-D2\nAstromech carrying mission data"
        ),
    },
}


CHAPTER_TASKS: dict[str, list[TaskSpec]] = {
    "1": [
        TaskSpec(
            name="Check Your Coordinates",
            lesson=(
                "The Rebel base is huge and new technicians get lost fast. Before Leia trusts you "
                "with the mission, she wants you to ask the computer where you are standing. "
                "The special word is `pwd`, short for 'print working directory'. It shows your "
                "current location, like a glowing map on the wall."
            ),
            instruction="Use `pwd` to reveal your current location.",
            command="pwd",
            success="Leia sees the coordinates and knows you can read the map.",
        ),
        TaskSpec(
            name="Scan The Base",
            lesson=(
                "From here you can see several rooms, but you need the computer to name them. "
                "The word `ls` means 'list'. It shows what is present in the current place, "
                "the same way a hangar screen lists ships and doors."
            ),
            instruction="Use `ls` to list the rooms around you.",
            command="ls",
            success="The base layout appears, and the first mystery starts to make sense.",
        ),
        TaskSpec(
            name="Read The Briefing",
            lesson=(
                "Princess Leia left her orders inside a file named "
                "`briefing_room/mission_briefing.txt`. To crack a text file open, rebels use "
                "the word `cat`, short for 'concatenate'. In this game, `cat` lets you read "
                "what is inside a file. Type the special word and the file name to see Leia's message."
            ),
            instruction="Read Leia's mission file.",
            command="cat",
            args=("briefing_room/mission_briefing.txt",),
            success="Leia's message spills across the screen and points you toward the Falcon.",
        ),
        TaskSpec(
            name="Reach The Falcon Through The Hangar",
            lesson=(
                "Leia's note reveals a tricky idea: the Falcon is not directly under the base. "
                "It is inside the `hangar`, and the `hangar` contains `millennium_falcon`. "
                "The travel word is `cd`, short for 'change directory'. To move through rooms "
                "inside rooms, write the full path with a slash: `hangar/millennium_falcon`."
            ),
            instruction="Use `cd` with the full path to reach the Falcon.",
            command="cd",
            args=("hangar/millennium_falcon",),
            success="The ship ramp lowers. You found the Falcon by following the full path.",
            tips=[
                "The Falcon is not directly here. It is inside `hangar`, so your path must include both rooms.",
                "`cd` means change directory, and the one-jump path is `hangar/millennium_falcon`.",
                "Exact answer: `cd hangar/millennium_falcon`.",
            ],
        ),
        TaskSpec(
            name="Crew Manifest",
            lesson=(
                "Han wants a crew check before the ramp closes. You can use `ls` again, but this "
                "time point it at the `crew` folder. When `ls` is followed by a path, it lists "
                "what is inside that specific place without moving you there."
            ),
            instruction="List the files inside `crew`.",
            command="ls",
            args=("crew",),
            success="Han gets the crew manifest and knows exactly who is aboard.",
        ),
        TaskSpec(
            name="Reveal Hidden Routes",
            lesson=(
                "R2-D2 has spotted a hidden route file, but normal `ls` will skip secret names "
                "that begin with a dot. Add the flag `-a` after `ls` to show everything, even "
                "hidden files. Flags are little extra instructions you attach to a command."
            ),
            instruction="Use `ls -a` to reveal the hidden route file.",
            command="ls",
            args=("-a",),
            success="A hidden file appears. R2-D2 whistles like he knew it was there all along.",
        ),
    ],
    "2": [
        TaskSpec(
            name="Read The Escape Routes",
            lesson=(
                "Now that the hidden file is visible, you can read it with `cat`. R2-D2 says "
                "the file `.escape_routes.txt` contains the next step of the mission."
            ),
            instruction="Open `.escape_routes.txt`.",
            command="cat",
            args=(".escape_routes.txt",),
            success="The hidden note opens, and the Falcon's next problem is finally clear.",
        ),
        TaskSpec(
            name="Build The Training Bay",
            lesson=(
                "The hidden route file says the crew needs a new planning room. To build a new "
                "room in computer space, use `mkdir`, short for 'make directory'. A directory "
                "is just another word for folder."
            ),
            instruction="Create `training_bay`.",
            command="mkdir",
            args=("training_bay",),
            success="A brand-new planning room appears inside the Falcon.",
        ),
        TaskSpec(
            name="Create The Rescue Team Room",
            lesson=(
                "Luke wants a smaller room inside the new bay just for the rescue plan. "
                "`mkdir` can also build a room inside another room when you give it a path like "
                "`training_bay/rescue_team`."
            ),
            instruction="Create the `rescue_team` folder inside `training_bay`.",
            command="mkdir",
            args=("training_bay/rescue_team",),
            success="The rescue team room is built and waiting for names and plans.",
        ),
        TaskSpec(
            name="Add Obi-Wan To The Roster",
            lesson=(
                "The rescue team needs its first name on the board. To make a new empty file, "
                "use `touch`. Think of it like placing a blank data card into the folder so the "
                "team can use it later."
            ),
            instruction="Create `training_bay/rescue_team/obi_wan.txt`.",
            command="touch",
            args=("training_bay/rescue_team/obi_wan.txt",),
            success="Obi-Wan is now written into the rescue team's records.",
        ),
        TaskSpec(
            name="Move The Hyperdrive Note",
            lesson=(
                "Chewbacca finds a faulty hyperdrive note lying in the middle of the Falcon. "
                "The command `mv` means move. It picks something up from one place and drops it "
                "somewhere else."
            ),
            instruction="Move `faulty_hyperdrive_note.txt` into `training_bay`.",
            command="mv",
            args=("faulty_hyperdrive_note.txt", "training_bay/faulty_hyperdrive_note.txt"),
            success="Chewbacca grunts happily. The messy note is finally where it belongs.",
        ),
        TaskSpec(
            name="Inspect The Training Bay",
            lesson=(
                "Before Leia approves the bay, you need to show her what is inside it. Use `ls` "
                "with the path `training_bay` so the ship computer lists that room for you."
            ),
            instruction="List the contents of `training_bay`.",
            command="ls",
            args=("training_bay",),
            success="Leia can now see the rescue room and the repair note in one glance.",
        ),
        TaskSpec(
            name="Copy The Plans",
            lesson=(
                "The original Death Star plans must stay safe in the archive, so the rescue team "
                "needs a copy, not the only version. The command `cp` means copy. The tricky part "
                "is the path: the archive is two levels above the Falcon, so you must walk back "
                "with `../../` before entering `archive`."
            ),
            instruction="Copy the archived plans into `training_bay/rescue_team/death_star_plans.txt`.",
            command="cp",
            args=("../../archive/death_star_plans.txt", "training_bay/rescue_team/death_star_plans.txt"),
            success="A safe study copy lands in the rescue room while the archive stays protected.",
            tips=[
                "The archive is above the Falcon, so you must walk back two levels with `../../` before entering `archive`.",
                "Use `cp source destination`, and the source begins with `../../archive/death_star_plans.txt`.",
                "Exact answer: `cp ../../archive/death_star_plans.txt training_bay/rescue_team/death_star_plans.txt`.",
            ],
        ),
    ],
    "3": [
        TaskSpec(
            name="Find The Plans",
            lesson=(
                "The Falcon is getting crowded, and guessing where files landed is risky. "
                "The command `find` searches by name, like asking every droid in the ship "
                "whether it has seen a file."
            ),
            instruction="Search for `death_star_plans.txt`.",
            command="find",
            args=("death_star_plans.txt",),
            success="The search points straight to the plans, and no one wastes time guessing.",
        ),
        TaskSpec(
            name="Inspect The Full Bay",
            lesson=(
                "Leia wants the whole layout, not just one room at a time. The command `tree` "
                "draws the folder like a branching map so you can see every room and file underneath it."
            ),
            instruction="Show the full tree for `training_bay`.",
            command="tree",
            args=("training_bay",),
            success="The Falcon's planning area now looks like a clean tactical map.",
        ),
        TaskSpec(
            name="Enter The Rescue Team Room",
            lesson=(
                "Now you need to step into the rescue team room itself. `cd` changes your location, "
                "and here the path is relative to where you already are: `training_bay/rescue_team`."
            ),
            instruction="Move into `training_bay/rescue_team`.",
            command="cd",
            args=("training_bay/rescue_team",),
            success="You step into the rescue room, right where the copied plans are waiting.",
        ),
        TaskSpec(
            name="Check The Final Kit",
            lesson=(
                "Inside the rescue team room, Han wants one last quick glance at what is ready. "
                "A plain `ls` works because you are already standing in the correct place."
            ),
            instruction="List the files in the rescue team room.",
            command="ls",
            success="The final kit is on screen: one roster file and one plan file, ready to go.",
        ),
        TaskSpec(
            name="Read The Plans",
            lesson=(
                "The copied plans are finally in the right room. Use `cat` again to read the file "
                "and see Leia's final instructions for this chapter."
            ),
            instruction="Read `death_star_plans.txt`.",
            command="cat",
            args=("death_star_plans.txt",),
            success="The plans reveal the weakness and tell you exactly where to report.",
        ),
        TaskSpec(
            name="Return To Leia",
            lesson=(
                "The plans say it is time to report back. `cd` can also take a full path that "
                "starts with `/`. An absolute path is like using the full galaxy address instead "
                "of guessing from where you stand."
            ),
            instruction="Use a full path to return to `/galaxy/rebel_base/briefing_room`.",
            command="cd",
            args=("/galaxy/rebel_base/briefing_room",),
            success="You return to Leia's room in one clean jump across the base.",
            tips=[
                "This time Leia wants the full galaxy address, so your path must start with `/`.",
                "Use `cd` with the absolute path `/galaxy/rebel_base/briefing_room`.",
                "Exact answer: `cd /galaxy/rebel_base/briefing_room`.",
            ],
        ),
        TaskSpec(
            name="Open Leia's Reply",
            lesson=(
                "Leia left one more message waiting in `report_terminal.txt`. You already know the "
                "special reading word: `cat`. Use it one more time to open the reply and close "
                "this chapter of the adventure."
            ),
            instruction="Read `report_terminal.txt`.",
            command="cat",
            args=("report_terminal.txt",),
            success="Leia smiles. This chapter is complete, and the next world is waiting.",
        ),
    ],
}


COMMAND_TIPS = {
    "help": "If the Rebel console feels strange, use `help` to see the commands you can speak to it.",
    "pwd": "Use `pwd` to ask the base map where you are standing.",
    "ls": "Use `ls` to make the computer list what it can see.",
    "mkdir": "Use `mkdir` to build a new room or folder.",
    "cd": "Use `cd` to travel to another room.",
    "touch": "Use `touch` to place a new empty data card into a folder.",
    "cat": "Use `cat` to crack open a file and read its text.",
    "write": "Use `write file \"text\"` to replace a file with one line of text.",
    "append": "Use `append file \"text\"` to add a new line to a file.",
    "cp": "Use `cp old new` to make a safe copy while keeping the original.",
    "mv": "Use `mv old new` to move a file into its proper place.",
    "rm": "Use `rm` to remove a file.",
    "rmdir": "Use `rmdir` to remove an empty folder.",
    "tree": "Use `tree` to draw the whole folder map.",
    "find": "Use `find name` to search the ship by file name.",
    "python": "Use `python file.py` to run a Python program.",
}


SUCCESS_LINES = {
    "help": "The command guide opens in your console.",
    "pwd": "You checked your current coordinates.",
    "ls": "You scanned the area successfully.",
    "mkdir": "A new Rebel workspace is ready.",
    "cd": "You moved to the right place.",
    "touch": "The file is ready.",
    "cat": "The report is now on screen.",
    "write": "The file has fresh orders.",
    "append": "You added a new line to the report.",
    "cp": "The copy is in place.",
    "mv": "The item has been moved.",
    "rm": "The file is gone.",
    "rmdir": "The empty folder is gone too.",
    "tree": "The full layout is visible.",
    "find": "You tracked it down.",
    "python": "The program ran.",
}


class CampaignBuilder:
    def __init__(self) -> None:
        self.fs = VirtualFileSystem()
        self.tasks: list[Task] = []
        self.current_chapter = CHAPTERS["1"]

    def set_world(self, *, cwd: str, dirs: list[str], files: dict[str, str]) -> None:
        self.fs.load_snapshot(cwd=cwd, dirs=dirs, files=files)

    def use_chapter(self, key: str) -> None:
        self.current_chapter = CHAPTERS[key]

    def add_task_spec(self, spec: TaskSpec) -> None:
        snapshot = self.fs.snapshot()
        chapter = self.current_chapter
        args = list(spec.args)

        self.tasks.append(
            Task(
                number=len(self.tasks) + 1,
                chapter_key=chapter.key,
                chapter_name=chapter.name,
                chapter_intro=chapter.intro,
                name=spec.name,
                lesson=spec.lesson,
                instruction=spec.instruction,
                expected_command=spec.command,
                expected_args=args,
                tips=spec.tips or build_tips(spec.command, args),
                success=spec.success or success_line(spec.command),
                scenario=build_scenario(snapshot),
            )
        )
        apply_expected(self.fs, spec.command, args)


def build_tasks() -> list[Task]:
    builder = CampaignBuilder()
    builder.set_world(**WORLD)

    for chapter_key in ("1", "2", "3"):
        builder.use_chapter(chapter_key)
        for spec in CHAPTER_TASKS[chapter_key]:
            builder.add_task_spec(spec)

    return builder.tasks


def build_scenario(snapshot: dict[str, Any]) -> Scenario:
    return Scenario(
        cwd=str(snapshot["cwd"]),
        dirs=list(snapshot["dirs"]),
        files=dict(snapshot["files"]),
    )


def build_tips(command: str, args: list[str]) -> list[str]:
    first = COMMAND_TIPS[command]

    if command == "ls" and "-a" in args:
        second = "The `-a` flag reveals hidden names that begin with a dot."
    elif command in {"help", "pwd"}:
        second = f"Try this exact command: `{format_command(command, args)}`."
    elif command in {"ls", "tree", "cd", "mkdir", "touch", "cat", "rm", "rmdir", "find", "python"}:
        if args:
            second = f"The path or name for this mission is `{args[0]}`."
        else:
            second = f"Try this exact command: `{format_command(command, args)}`."
    elif command in {"write", "append"}:
        second = f"Start with `{command} {quote_arg(args[0])} \"...\"`."
    else:
        second = f"Try this command shape: `{format_command(command, args)}`."

    third = f"Exact answer: `{format_command(command, args)}`."
    return [first, second, third]


def success_line(command: str) -> str:
    return SUCCESS_LINES[command]


def format_command(command: str, args: list[str]) -> str:
    pieces = [command]
    for index, arg in enumerate(args):
        if command in {"write", "append"} and index == 1:
            pieces.append(quote_text(arg))
        else:
            pieces.append(quote_arg(arg))
    return " ".join(pieces)


def quote_arg(text: str) -> str:
    if text == "":
        return '""'
    if any(char.isspace() for char in text) or '"' in text:
        return quote_text(text)
    return text


def quote_text(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def apply_expected(fs: VirtualFileSystem, command: str, args: list[str]) -> None:
    if command in {"help", "pwd"}:
        return
    if command == "ls":
        path, show_hidden = parse_ls_args(args)
        fs.ls(path, show_hidden=show_hidden)
        return
    if command == "mkdir":
        fs.mkdir(args[0])
        return
    if command == "cd":
        fs.change_directory(args[0])
        return
    if command == "touch":
        fs.touch(args[0])
        return
    if command == "cat":
        fs.read_file(args[0])
        return
    if command == "write":
        fs.write_file(args[0], args[1])
        return
    if command == "append":
        fs.append_file(args[0], args[1])
        return
    if command == "cp":
        fs.copy(args[0], args[1])
        return
    if command == "mv":
        fs.move(args[0], args[1])
        return
    if command == "rm":
        fs.remove_file(args[0])
        return
    if command == "rmdir":
        fs.remove_directory(args[0])
        return
    if command == "tree":
        fs.tree(args[0] if args else None)
        return
    if command == "find":
        fs.find(args[0])
        return
    if command == "python":
        fs.read_file(args[0])
        return
    raise ValueError(f"Unsupported course command: {command}")


def parse_ls_args(args: list[str]) -> tuple[str | None, bool]:
    show_hidden = False
    path: str | None = None

    for arg in args:
        if arg == "-a":
            show_hidden = True
            continue
        if arg.startswith("-"):
            raise ValueError(f"Unsupported ls option in course data: {arg}")
        if path is not None:
            raise ValueError("Course data can only use one path with ls.")
        path = arg

    return path, show_hidden
