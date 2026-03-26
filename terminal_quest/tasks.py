from __future__ import annotations

from dataclasses import dataclass

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
class CommandLesson:
    syntax: str
    example: str
    what: str
    why: str


CHAPTERS = {
    "1": Chapter(
        key="1",
        name="Briefing At Yavin",
        intro=(
            "Yavin 4 is buzzing. Leia has a mission, Han wants the Falcon ready, "
            "and your first job is to learn the Rebel base before the launch window closes."
        ),
        reward="Base Cartographer",
    ),
    "2": Chapter(
        key="2",
        name="Preparing The Falcon",
        intro=(
            "The Falcon looks ready from the outside, but R2-D2 has detected hidden intel "
            "and Chewbacca wants the ship organized before launch."
        ),
        reward="Falcon Quartermaster",
    ),
    "3": Chapter(
        key="3",
        name="Plans For The Assault",
        intro=(
            "Leia needs the rescue team room stocked with the Death Star plans, "
            "and the whole setup must be ready for the next chapter of the mission."
        ),
        reward="Mission Planner",
    ),
}


def build_tasks() -> list[Task]:
    builder = CampaignBuilder()
    builder.set_world(
        cwd="/galaxy/rebel_base",
        dirs=[
            "/galaxy",
            "/galaxy/rebel_base",
            "/galaxy/rebel_base/archive",
            "/galaxy/rebel_base/briefing_room",
            "/galaxy/rebel_base/hangar",
            "/galaxy/rebel_base/hangar/millennium_falcon",
            "/galaxy/rebel_base/hangar/millennium_falcon/cargo",
            "/galaxy/rebel_base/hangar/millennium_falcon/crew",
        ],
        files={
            "/galaxy/rebel_base/briefing_room/mission_briefing.txt": (
                "Mission Briefing\n"
                "---------------\n"
                "1. Reach the Millennium Falcon.\n"
                "2. Confirm the crew.\n"
                "3. Prepare a rescue team.\n"
                "4. Copy the Death Star plans.\n"
                "5. Report back to Leia."
            ),
            "/galaxy/rebel_base/archive/death_star_plans.txt": (
                "Death Star Plans\n"
                "----------------\n"
                "Weak point: thermal exhaust port\n"
                "Targeting support: required\n"
                "Protection level: extreme"
            ),
            "/galaxy/rebel_base/hangar/millennium_falcon/.escape_routes.txt": (
                "Escape Routes\n"
                "-------------\n"
                "1. Yavin 4 jungle route\n"
                "2. Hyperspace vector 77\n"
                "3. Emergency rendezvous with the fleet"
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
    )
    add_chapter_1(builder)
    add_chapter_2(builder)
    add_chapter_3(builder)
    return builder.tasks


class CampaignBuilder:
    def __init__(self) -> None:
        self.fs = VirtualFileSystem()
        self.tasks: list[Task] = []
        self.current_chapter = CHAPTERS["1"]

    def set_world(self, *, cwd: str, dirs: list[str], files: dict[str, str]) -> None:
        self.fs.load_snapshot(cwd=cwd, dirs=dirs, files=files)

    def use_chapter(self, key: str) -> None:
        self.current_chapter = CHAPTERS[key]

    def add(
        self,
        name: str,
        instruction: str,
        command: str,
        *args: str,
        success: str | None = None,
    ) -> None:
        snapshot = self.fs.snapshot()
        chapter = self.current_chapter
        self.tasks.append(
            Task(
                number=len(self.tasks) + 1,
                chapter_key=chapter.key,
                chapter_name=chapter.name,
                chapter_intro=chapter.intro,
                name=name,
                instruction=instruction,
                expected_command=command,
                expected_args=list(args),
                tips=build_tips(command, list(args)),
                success=success or success_line(command),
                scenario=Scenario(
                    cwd=snapshot["cwd"],  # type: ignore[arg-type]
                    dirs=list(snapshot["dirs"]),  # type: ignore[arg-type]
                    files=dict(snapshot["files"]),  # type: ignore[arg-type]
                ),
            )
        )
        apply_expected(self.fs, command, list(args))


def build_tips(command: str, args: list[str]) -> list[str]:
    first = {
        "help": "Use `help` to see the command list in this training shell.",
        "pwd": "Use `pwd` to ask the shell where you are right now.",
        "ls": "Use `ls` to look around and list files or folders.",
        "mkdir": "Use `mkdir` to create a new folder.",
        "cd": "Use `cd` to move into a folder or full path.",
        "touch": "Use `touch` to create a new empty file.",
        "cat": "Use `cat` to read a file.",
        "write": "Use `write file \"text\"` to replace a file with one line of text.",
        "append": "Use `append file \"text\"` to add a new line to a file.",
        "cp": "Use `cp old new` to make a copy.",
        "mv": "Use `mv old new` to move or rename something.",
        "rm": "Use `rm` to remove a file.",
        "rmdir": "Use `rmdir` to remove an empty folder.",
        "tree": "Use `tree` to see a folder and everything inside it.",
        "find": "Use `find name` to search for a file or folder by name.",
        "python": "Use `python file.py` to run a Python program.",
    }[command]

    if command == "ls" and "-a" in args:
        path_args = [arg for arg in args if arg != "-a"]
        if path_args:
            second = f"Use `-a` to reveal hidden files inside `{path_args[0]}`."
        else:
            second = "Use `-a` to reveal hidden files that begin with a dot."
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


def build_command_lesson(command: str, args: list[str]) -> CommandLesson:
    return CommandLesson(
        syntax=command_syntax(command, args),
        example=format_command(command, args),
        what=command_what(command, args),
        why=command_why(command, args),
    )


def command_syntax(command: str, args: list[str]) -> str:
    if command == "ls":
        return "ls [-a] [path]" if "-a" in args else "ls [path]"
    return {
        "help": "help [command]",
        "pwd": "pwd",
        "mkdir": "mkdir path",
        "cd": "cd path",
        "touch": "touch path",
        "cat": "cat path",
        "write": 'write path "text"',
        "append": 'append path "text"',
        "cp": "cp source destination",
        "mv": "mv source destination",
        "rm": "rm path",
        "rmdir": "rmdir path",
        "tree": "tree [path]",
        "find": "find name",
        "python": "python file.py",
    }[command]


def command_what(command: str, args: list[str]) -> str:
    if command == "ls" and "-a" in args:
        return "It lists files and folders, and `-a` also reveals hidden names that start with a dot."
    return {
        "help": "It shows the available training-shell commands.",
        "pwd": "It prints the path of the folder you are standing in right now.",
        "ls": "It lists the files and folders in your current location or in a path you name.",
        "mkdir": "It creates a new folder.",
        "cd": "It moves you into another folder.",
        "touch": "It creates a new empty file.",
        "cat": "It opens a file and prints its contents.",
        "write": "It replaces a file with one new line of text.",
        "append": "It adds one new line to the end of a file.",
        "cp": "It copies a file or folder to a new place.",
        "mv": "It moves or renames a file or folder.",
        "rm": "It removes a file.",
        "rmdir": "It removes an empty folder.",
        "tree": "It shows a folder and everything inside it as a full layout.",
        "find": "It searches for a file or folder by name.",
        "python": "It runs a Python file and shows what it prints.",
    }[command]


def command_why(command: str, args: list[str]) -> str:
    if command == "ls" and "-a" in args:
        return "Rebel intel is sometimes hidden on purpose, so this flag helps you spot secret route files."
    return {
        "help": "A new Rebel technician needs a map of the controls before a mission starts.",
        "pwd": "Knowing your exact position keeps you from running to the wrong room on the base or ship.",
        "ls": "Before the crew can act, they need to know what is present in the area.",
        "mkdir": "Mission gear stays useful only when each team has its own organized space.",
        "cd": "Moving to the right folder is like walking to the right room on the Falcon.",
        "touch": "A new file gives the crew a place to register a person, note, or mission artifact.",
        "cat": "Orders, plans, and route files only help if the crew can actually read them.",
        "write": "Clear written orders keep the mission from drifting off course.",
        "append": "Adding one more line lets the crew grow a plan without losing what was already written.",
        "cp": "The Rebellion often needs a working copy so the original intel stays safe.",
        "mv": "Moving files puts mission notes exactly where the right crew member expects them.",
        "rm": "Removing outdated files keeps the mission room clean and less confusing.",
        "rmdir": "Cleaning empty folders makes the ship layout easier to understand.",
        "tree": "Commanders need to see the whole layout at once before they approve the setup.",
        "find": "Searching by name is faster than guessing when the base starts to fill up with mission files.",
        "python": "Running code turns written instructions into something the ship computer can actually do.",
    }[command]


def success_line(command: str) -> str:
    return {
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
    }[command]


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


def add_chapter_1(builder: CampaignBuilder) -> None:
    builder.use_chapter("1")
    builder.add(
        "Check Your Coordinates",
        "Leia wants proof that you know your location inside the Rebel base. Ask the shell where you are.",
        "pwd",
        success="Leia nods. You have the Rebel base coordinates.",
    )
    builder.add(
        "Scan The Base",
        "Han wants a quick list of the rooms available from here. Look around the base.",
        "ls",
        success="The base layout is on screen, and the crew can move fast.",
    )
    builder.add(
        "Read The Briefing",
        "Leia left the mission in `briefing_room/mission_briefing.txt`. Read it before you run.",
        "cat",
        "briefing_room/mission_briefing.txt",
        success="The orders are clear: reach the Falcon, prepare the team, and report back.",
    )
    builder.add(
        "Run To The Hangar",
        "The Falcon is waiting. Move into the `hangar`.",
        "cd",
        "hangar",
        success="You reach the hangar entrance before the launch window slips away.",
    )
    builder.add(
        "Board The Falcon",
        "Step into `millennium_falcon` so the preflight checks can begin.",
        "cd",
        "millennium_falcon",
        success="The Falcon ramp closes behind you. The story is moving now.",
    )
    builder.add(
        "Crew Manifest",
        "Han asks who is already on board. List the contents of `crew`.",
        "ls",
        "crew",
        success="Han has the crew manifest and knows exactly who is aboard.",
    )


def add_chapter_2(builder: CampaignBuilder) -> None:
    builder.use_chapter("2")
    builder.add(
        "Reveal Hidden Routes",
        "R2-D2 detected a hidden route file in the Falcon. Use the list command with the hidden-file flag.",
        "ls",
        "-a",
        success="R2-D2 chirps with approval. The hidden route file is revealed.",
    )
    builder.add(
        "Read The Escape Routes",
        "Open `.escape_routes.txt` so the crew knows the fallback jumps.",
        "cat",
        ".escape_routes.txt",
        success="The emergency routes are now in the crew's hands.",
    )
    builder.add(
        "Build The Training Bay",
        "Luke needs a place to organize the rescue prep. Create `training_bay`.",
        "mkdir",
        "training_bay",
        success="Luke has a new place to gather the rescue gear.",
    )
    builder.add(
        "Create The Rescue Team Room",
        "Inside the training bay, make a folder named `rescue_team`.",
        "mkdir",
        "training_bay/rescue_team",
        success="The rescue team room is ready for assignments.",
    )
    builder.add(
        "Add Obi-Wan",
        "Register Obi-Wan by creating `training_bay/rescue_team/obi_wan.txt`.",
        "touch",
        "training_bay/rescue_team/obi_wan.txt",
        success="Obi-Wan is now on the rescue team roster.",
    )
    builder.add(
        "Move The Hyperdrive Note",
        "Chewbacca wants the faulty note moved out of the main deck and into the training bay.",
        "mv",
        "faulty_hyperdrive_note.txt",
        "training_bay/faulty_hyperdrive_note.txt",
        success="Chewbacca grunts happily. The hyperdrive note is with the mechanics.",
    )
    builder.add(
        "Inspect The Training Bay",
        "List `training_bay` to confirm the note and the rescue team room are both in place.",
        "ls",
        "training_bay",
        success="The training bay is organized and ready for the next mission step.",
    )


def add_chapter_3(builder: CampaignBuilder) -> None:
    builder.use_chapter("3")
    builder.add(
        "Copy The Plans",
        "Make a study copy of the archived Death Star plans into `training_bay/rescue_team/death_star_plans.txt`.",
        "cp",
        "../../archive/death_star_plans.txt",
        "training_bay/rescue_team/death_star_plans.txt",
        success="Leia now has a safe study copy for the rescue team.",
    )
    builder.add(
        "Find The Plans",
        "Confirm the study copy exists by searching for `death_star_plans.txt` from your current location.",
        "find",
        "death_star_plans.txt",
        success="The copied plans are exactly where the team needs them.",
    )
    builder.add(
        "Inspect The Full Bay",
        "Show the full tree for `training_bay` so Leia can inspect the setup.",
        "tree",
        "training_bay",
        success="Leia can see the full rescue setup in one clean view.",
    )
    builder.add(
        "Enter The Rescue Team Room",
        "Move into `training_bay/rescue_team` so you can inspect the final kit up close.",
        "cd",
        "training_bay/rescue_team",
        success="You step into the rescue team room for final checks.",
    )
    builder.add(
        "Check The Final Kit",
        "List the files in the rescue team room.",
        "ls",
        success="The rescue team kit is complete and on display.",
    )
    builder.add(
        "Read The Plans",
        "Open `death_star_plans.txt` for one final look before departure.",
        "cat",
        "death_star_plans.txt",
        success="The weakness is confirmed. The mission can move forward.",
    )
    builder.add(
        "Return To Leia",
        "Report back fast by moving straight to `/galaxy/rebel_base/briefing_room`.",
        "cd",
        "/galaxy/rebel_base/briefing_room",
        success="Leia receives your report. The Falcon is ready for the next chapter.",
    )
