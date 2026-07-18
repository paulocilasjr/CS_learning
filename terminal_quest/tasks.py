from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from terminal_quest.curriculum import MissionType, validate_campaign
from terminal_quest.filesystem import VirtualFileSystem
from terminal_quest.validation import Outcome


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
    mission_type: MissionType
    new_skills: tuple[str, ...]
    review_skills: tuple[str, ...]
    outcome: Outcome | None
    multi_step: bool
    story_flags: tuple[str, ...]
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
    mission_type: MissionType
    new_skills: tuple[str, ...] = ()
    review_skills: tuple[str, ...] = ()
    outcome: Outcome | None = None
    multi_step: bool = False
    story_flags: tuple[str, ...] = ()
    args: tuple[str, ...] = ()
    success: str | None = None
    tips: list[str] | None = None
    canonical_steps: tuple["CommandStep", ...] = ()


@dataclass(frozen=True)
class CommandStep:
    command: str
    args: tuple[str, ...] = ()


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
    "4": Chapter(
        key="4",
        name="The Secret Transmission",
        intro=(
            "A flood of Imperial messages has reached Rebel Intelligence. Leia needs you to inspect, "
            "search, count, sort, and clean the data before the fleet changes course."
        ),
        reward="Rebel Intelligence Analyst",
    ),
    "5": Chapter(
        key="5",
        name="The Intelligence Machine",
        intro=(
            "The transmissions are arriving too quickly for one tool at a time. R2-D2 will teach you "
            "to connect command machines and save their results as reusable reports."
        ),
        reward="Command Systems Engineer",
    ),
    "6": Chapter(
        key="6",
        name="Build Your First Droid Program",
        intro=(
            "R2-D2 opens the droid laboratory. Instead of giving the computer one command at a time, "
            "you will store data in a program and make it calculate useful answers."
        ),
        reward="Junior Droid Programmer",
    ),
    "7": Chapter(
        key="7",
        name="Teach The Droid To Think",
        intro=(
            "A useful droid must react when its pilot is busy. You will give it comparisons and rules "
            "for deciding whether to jump, refuel, or raise shields."
        ),
        reward="Droid Logic Specialist",
    ),
    "8": Chapter(
        key="8",
        name="The Galactic Scanner",
        intro=(
            "The Alliance cannot scan every world by hand. Collections and loops will let your droid "
            "remember many targets and repeat work reliably."
        ),
        reward="Galactic Automation Pilot",
    ),
    "9": Chapter(
        key="9",
        name="The Rebel Engineering Corps",
        intro=(
            "Your programs are growing. The engineering corps will show you how to name reusable solutions, "
            "pass them data, return answers, and build simple algorithms."
        ),
        reward="Rebel Software Engineer",
    ),
    "10": Chapter(
        key="10",
        name="The Broken Navigation Computer",
        intro=(
            "The navigation computer is producing dangerous answers. R2-D2 reminds you that bugs are evidence: "
            "observe the behavior, form a hypothesis, change one thing, and test again."
        ),
        reward="Rebel Debugging Specialist",
    ),
    "11": Chapter(
        key="11",
        name="The Rebel Code Repository",
        intro=(
            "Many Rebel engineers are changing the same mission systems. A simulated repository lets you inspect "
            "changes, save meaningful snapshots, explore alternate plans, and combine successful work safely."
        ),
        reward="Rebel Repository Guardian",
    ),
    "12": Chapter(
        key="12",
        name="The Final Campaign",
        intro=(
            "An Imperial relay has found the Rebel fleet. Leia gives you objectives, not command recipes. Inspect "
            "state, choose tools, verify outcomes, repair code, and preserve the final solution in history."
        ),
        reward="Rebel Computer Science Knight",
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


INTELLIGENCE_WORLD = {
    "cwd": "/galaxy/rebel_intelligence",
    "dirs": [
        "/galaxy",
        "/galaxy/rebel_intelligence",
        "/galaxy/rebel_intelligence/transmissions",
        "/galaxy/rebel_intelligence/reports",
        "/galaxy/rebel_intelligence/quarantine",
    ],
    "files": {
        "/galaxy/rebel_intelligence/transmissions/intercepts.txt": (
            "HEADER: Imperial relay K-7\n"
            "REBEL: Alderaan convoy is safe\n"
            "IMPERIAL: patrol moved toward Tatooine\n"
            "REBEL: Red Squadron awaiting orders\n"
            "IMPERIAL: tracker activated\n"
            "IMPERIAL: Tatooine landing window 19:00\n"
            "FOOTER: transmission complete"
        ),
        "/galaxy/rebel_intelligence/transmissions/call_signs.txt": (
            "Gold Leader\nBlue Seven\nRed Five\nGreen Three"
        ),
        "/galaxy/rebel_intelligence/transmissions/fleet.log": (
            "X-Wing\nA-Wing\nY-Wing\nX-Wing\nB-Wing\nX-Wing"
        ),
        "/galaxy/rebel_intelligence/navigation_map.txt": "Safe route to the Rebel fleet.",
        "/galaxy/rebel_intelligence/imperial_tracker.exe": "TRACKING ACTIVE",
    },
}


PROGRAMS = {
    "fuel.py": "fuel = 75\nprint(fuel)",
    "identity.py": 'ship = "Millennium Falcon"\nactive = True\nprint(ship, active)',
    "fuel_math.py": "fuel = 80\nused = 25\nprint(fuel - used)",
    "range_check.py": "fuel = 40\ndistance = 50\nprint(fuel >= distance)",
    "jump_rule.py": (
        'fuel = 60\ndistance = 50\nif fuel >= distance:\n    print("jump")\nelse:\n    print("refuel")'
    ),
    "shield_rule.py": (
        'enemy_near = True\nshields_ready = True\nif enemy_near and shields_ready:\n    print("raise shields")'
    ),
    "planets.py": 'planets = ["Hoth", "Naboo", "Endor"]\nprint(planets[1])',
    "scanner.py": (
        'planets = ["Hoth", "Naboo", "Endor"]\nfor planet in planets:\n    print("scanning", planet)'
    ),
    "counter.py": 'for sector in range(1, 5):\n    print("sector", sector)',
    "function.py": 'def scan():\n    print("scan analyze report")\n\nscan()\nscan()',
    "parameter.py": 'def scan(planet):\n    print("scanning", planet)\n\nscan("Dagobah")',
    "return.py": 'def fuel_left(fuel, used):\n    return fuel - used\n\nprint(fuel_left(90, 35))',
    "mapping.py": 'ships = {"X-Wing": 5, "A-Wing": 3}\nprint(ships["X-Wing"])',
    "search.py": (
        'planets = ["Hoth", "Naboo", "Endor"]\nfor planet in planets:\n'
        '    if planet == "Endor":\n        print("signal found", planet)'
    ),
    "sorting.py": 'fuel_levels = [30, 90, 50, 10]\nprint(sorted(fuel_levels))',
}


DROID_WORLD = {
    "cwd": "/galaxy/droid_lab",
    "dirs": [
        "/galaxy",
        "/galaxy/droid_lab",
        "/galaxy/droid_lab/programs",
        "/galaxy/droid_lab/diagnostics",
    ],
    "files": {
        "/galaxy/droid_lab/README.txt": (
            "Droid programs live in programs/. Use write with \\n for line breaks, then run them with python."
        ),
        "/galaxy/droid_lab/diagnostics/broken_navigation.py": (
            'fuel = 20\ndistance = 50\nif fuel < distance:\n    print("jump")\nelse:\n    print("refuel")'
        ),
        "/galaxy/droid_lab/diagnostics/syntax_fault.py": (
            'enemy_near = True\nif enemy_near\n    print("raise shields")'
        ),
        "/galaxy/droid_lab/diagnostics/jump_tests.py": (
            "def can_jump(fuel, distance):\n    return fuel < distance\n\n"
            "assert can_jump(100, 50) == True\nassert can_jump(20, 50) == False"
        ),
    },
}


REPOSITORY_WORLD = {
    "cwd": "/galaxy/rebel_repository",
    "dirs": ["/galaxy", "/galaxy/rebel_repository", "/galaxy/rebel_repository/docs"],
    "files": {
        "/galaxy/rebel_repository/mission_plan.py": 'route = "Hoth"\nshields = False',
        "/galaxy/rebel_repository/docs/README.txt": (
            "Every commit is a recoverable mission-plan snapshot. Use branches for alternate plans."
        ),
    },
}


FINAL_WORLD = {
    "cwd": "/galaxy/final_campaign",
    "dirs": [
        "/galaxy",
        "/galaxy/final_campaign",
        "/galaxy/final_campaign/intelligence",
        "/galaxy/final_campaign/intelligence/incoming",
        "/galaxy/final_campaign/safe",
        "/galaxy/final_campaign/programs",
    ],
    "files": {
        "/galaxy/final_campaign/intelligence/incoming/alpha.log": (
            "DECOY: Mustafar\nPATROL: sector 7\nSTATUS: old"
        ),
        "/galaxy/final_campaign/intelligence/incoming/beta.log": (
            "PRIORITY: highest\nFLEET: Dantooine\nSTATUS: verified"
        ),
        "/galaxy/final_campaign/intelligence/navigation.map": "Route: Dantooine -> Endor",
        "/galaxy/final_campaign/intelligence/imperial_tracker.dat": "TRACKER ACTIVE",
        "/galaxy/final_campaign/programs/defense.py": (
            'enemy_near = True\nif enemy_near == False:\n    print("shields raised")\n'
            'else:\n    print("shields lowered")'
        ),
        "/galaxy/final_campaign/mission_summary.txt": "MISSION INCOMPLETE",
    },
}


def program_task(
    *,
    name: str,
    lesson: str,
    filename: str,
    code_key: str,
    output: str,
    mission_type: MissionType,
    new_skills: tuple[str, ...] = (),
    review_skills: tuple[str, ...] = (),
    success: str,
) -> TaskSpec:
    code = PROGRAMS[code_key]
    path = f"programs/{filename}"
    escaped = code.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
    return TaskSpec(
        name=name,
        lesson=f"{lesson}\n\nProgram to build:\n{code}",
        instruction=f"Write the program to `{path}`, then run it with `python {path}`.",
        command="write",
        mission_type=mission_type,
        new_skills=new_skills,
        review_skills=review_skills,
        outcome=Outcome(
            file_contents={path: code},
            output_contains=(output,),
            required_commands=("write", "python"),
        ),
        multi_step=True,
        tips=[
            "Use `write` to save the shown program. Type `\\n` wherever the program starts a new line.",
            f"After writing the file, run `python {path}` and inspect its output.",
            f'First command: `write {path} "{escaped}"`. Then: `python {path}`.',
        ],
        canonical_steps=(CommandStep("write", (path, code)),),
        success=success,
    )


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
            mission_type=MissionType.INTRODUCE,
            new_skills=("pwd",),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("ls",),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("cat",),
            review_skills=("ls",),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("relative_paths", "nested_paths", "cd"),
            review_skills=("ls",),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("targeted_listing",),
            review_skills=("ls", "relative_paths"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("hidden_files",),
            review_skills=("ls",),
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
            mission_type=MissionType.RECALL,
            review_skills=("cat", "hidden_files"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("mkdir",),
            review_skills=("cd",),
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
            mission_type=MissionType.TRANSFER,
            review_skills=("mkdir", "relative_paths", "nested_paths"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("touch",),
            review_skills=("mkdir", "nested_paths"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("mv",),
            review_skills=("touch", "relative_paths"),
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
            mission_type=MissionType.RECALL,
            review_skills=("ls", "targeted_listing"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("parent_paths", "cp"),
            review_skills=("cat", "relative_paths"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("find",),
            review_skills=("ls", "cat"),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("tree",),
            review_skills=("ls", "nested_paths"),
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
            mission_type=MissionType.RECALL,
            review_skills=("cd", "relative_paths"),
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
            mission_type=MissionType.RECALL,
            review_skills=("ls",),
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
            mission_type=MissionType.RECALL,
            review_skills=("cat",),
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
            mission_type=MissionType.INTRODUCE,
            new_skills=("absolute_paths",),
            review_skills=("cd",),
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
            mission_type=MissionType.RECALL,
            review_skills=("cat", "absolute_paths"),
            args=("report_terminal.txt",),
            success="Leia smiles. This chapter is complete, and the next world is waiting.",
        ),
    ],
    "4": [
        TaskSpec(
            name="Clear The Intelligence Screen",
            lesson=(
                "The console is crowded with old alerts. `clear` wipes old output from the display "
                "without deleting files, giving you a clean place to investigate."
            ),
            instruction="Clear the terminal display.",
            command="clear",
            mission_type=MissionType.INTRODUCE,
            new_skills=("clear",),
            success="The old alerts vanish and the intelligence console is ready.",
        ),
        TaskSpec(
            name="Answer Red Squadron",
            lesson=(
                "The command `echo` asks the computer to produce text as output. Output can be read now "
                "or connected to other tools later."
            ),
            instruction='Send the words `Red Squadron ready` with `echo`.',
            command="echo",
            mission_type=MissionType.INTRODUCE,
            new_skills=("echo",),
            review_skills=("cat",),
            args=("Red Squadron ready",),
            success="Red Squadron receives your clear reply.",
        ),
        TaskSpec(
            name="Inspect The Transmission Header",
            lesson=(
                "Large files do not always need to be read all at once. `head -n 2` shows only the first "
                "two lines, which is perfect for checking a transmission header."
            ),
            instruction="Show the first two lines of `transmissions/intercepts.txt`.",
            command="head",
            mission_type=MissionType.INTRODUCE,
            new_skills=("head",),
            review_skills=("cat", "relative_paths"),
            args=("-n", "2", "transmissions/intercepts.txt"),
            success="The relay header confirms that the message is Imperial.",
        ),
        TaskSpec(
            name="Inspect The Final Signal",
            lesson=(
                "The matching tool `tail` reads from the end of a file. It saves time when the newest or "
                "final status is what matters."
            ),
            instruction="Show the final line of `transmissions/intercepts.txt` with `tail -n 1`.",
            command="tail",
            mission_type=MissionType.INTRODUCE,
            new_skills=("tail",),
            review_skills=("cat", "relative_paths"),
            args=("-n", "1", "transmissions/intercepts.txt"),
            success="The footer confirms that the intercepted message is complete.",
        ),
        TaskSpec(
            name="Search For Tatooine",
            lesson=(
                "Reading every line becomes slow as intelligence grows. `grep` selects only lines containing "
                "a pattern, letting engineers reduce unnecessary work."
            ),
            instruction="Search `transmissions/intercepts.txt` for `Tatooine`.",
            command="grep",
            mission_type=MissionType.INTRODUCE,
            new_skills=("grep",),
            review_skills=("cat", "find"),
            args=("Tatooine", "transmissions/intercepts.txt"),
            success="Two Tatooine clues stand out from the noise.",
        ),
        TaskSpec(
            name="Count The Fleet Log",
            lesson=(
                "`wc` measures data. The `-l` option counts lines, so each ship record becomes one item in "
                "the total."
            ),
            instruction="Count the lines in `transmissions/fleet.log`.",
            command="wc",
            mission_type=MissionType.INTRODUCE,
            new_skills=("wc",),
            review_skills=("cat",),
            args=("-l", "transmissions/fleet.log"),
            success="The fleet log contains six ship records.",
        ),
        TaskSpec(
            name="Order The Call Signs",
            lesson=(
                "`sort` rearranges lines into order. Predictable order makes patterns, duplicates, and missing "
                "records easier to notice."
            ),
            instruction="Sort `transmissions/call_signs.txt`.",
            command="sort",
            mission_type=MissionType.INTRODUCE,
            new_skills=("sort",),
            review_skills=("cat",),
            args=("transmissions/call_signs.txt",),
            success="The call signs line up in a clean, predictable order.",
        ),
        TaskSpec(
            name="Destroy The Imperial Tracker",
            lesson=(
                "`rm` permanently removes a file inside this safe virtual computer. Inspecting the target matters: "
                "the navigation map is useful, but `imperial_tracker.exe` is dangerous."
            ),
            instruction="Remove `imperial_tracker.exe` while preserving the navigation map.",
            command="rm",
            mission_type=MissionType.INTRODUCE,
            new_skills=("rm",),
            review_skills=("ls", "cat"),
            args=("imperial_tracker.exe",),
            success="The tracker disappears while the Rebel route remains safe.",
        ),
        TaskSpec(
            name="Scan Every Text Transmission",
            lesson=(
                "A wildcard such as `*` stands for matching names. `transmissions/*.txt` expands to every text "
                "file in that folder, so one pattern can describe several files."
            ),
            instruction="Use `echo transmissions/*.txt` to reveal all matching text transmissions.",
            command="echo",
            mission_type=MissionType.INTRODUCE,
            new_skills=("wildcards",),
            review_skills=("echo", "relative_paths"),
            args=("transmissions/*.txt",),
            success="The wildcard finds both text transmissions in one scan.",
        ),
    ],
    "5": [
        TaskSpec(
            name="Save The Tatooine Report",
            lesson=(
                "The `>` operator redirects a command's output into a file. It turns a temporary answer into data "
                "that another Rebel can use later."
            ),
            instruction=(
                "Search the intercepts for `Tatooine` and redirect the matching lines into "
                "`reports/tatooine.txt`."
            ),
            command="grep",
            mission_type=MissionType.INTRODUCE,
            new_skills=("redirection",),
            review_skills=("grep", "touch"),
            outcome=Outcome(
                file_contents={
                    "reports/tatooine.txt": (
                        "IMPERIAL: patrol moved toward Tatooine\n"
                        "IMPERIAL: Tatooine landing window 19:00"
                    )
                }
            ),
            multi_step=True,
            tips=[
                "First form the `grep` command that shows the Tatooine lines.",
                "Place `>` after the search command, followed by the report path.",
                "Exact answer: `grep Tatooine transmissions/intercepts.txt > reports/tatooine.txt`.",
            ],
            canonical_steps=(
                CommandStep(
                    "write",
                    (
                        "reports/tatooine.txt",
                        "IMPERIAL: patrol moved toward Tatooine\nIMPERIAL: Tatooine landing window 19:00",
                    ),
                ),
            ),
            success="The Tatooine clues are now a durable Rebel report.",
        ),
        TaskSpec(
            name="Append Leia's Priority",
            lesson=(
                "`>>` redirects output too, but appends it instead of replacing the existing file. This preserves "
                "the intelligence already collected."
            ),
            instruction='Append `PRIORITY: HIGH` to `reports/tatooine.txt` using `echo` and `>>`.',
            command="echo",
            mission_type=MissionType.INTRODUCE,
            new_skills=("append_redirection",),
            review_skills=("echo", "redirection"),
            outcome=Outcome(
                file_contents={
                    "reports/tatooine.txt": (
                        "IMPERIAL: patrol moved toward Tatooine\n"
                        "IMPERIAL: Tatooine landing window 19:00\n"
                        "PRIORITY: HIGH"
                    )
                }
            ),
            multi_step=True,
            tips=[
                "Use `echo` to produce the priority line.",
                "The append operator has two greater-than signs: `>>`.",
                "Exact answer: `echo \"PRIORITY: HIGH\" >> reports/tatooine.txt`.",
            ],
            canonical_steps=(CommandStep("append", ("reports/tatooine.txt", "PRIORITY: HIGH")),),
            success="Leia's priority is added without erasing the Tatooine evidence.",
        ),
        TaskSpec(
            name="Connect The Intelligence Machines",
            lesson=(
                "A pipe `|` connects output to input. Think of `cat`, `grep`, and `wc` as machines: read all data, "
                "keep Imperial lines, then count what remains."
            ),
            instruction="Pipe the intercept file through `grep IMPERIAL` and `wc -l` to count Imperial lines.",
            command="cat",
            mission_type=MissionType.INTRODUCE,
            new_skills=("pipes",),
            review_skills=("cat", "grep", "wc"),
            outcome=Outcome(output_contains=("3",), required_commands=("cat", "grep", "wc")),
            multi_step=True,
            tips=[
                "Start by reading the file with `cat`.",
                "Connect `cat`, `grep IMPERIAL`, and `wc -l` with `|`.",
                "Exact answer: `cat transmissions/intercepts.txt | grep IMPERIAL | wc -l`.",
            ],
            success="Three Imperial records are counted without manual scanning.",
        ),
        TaskSpec(
            name="Build A Processed Report Bay",
            lesson=(
                "`&&` expresses a dependency: perform the next operation only if the first succeeded. Engineers use "
                "it when a later step depends on earlier state."
            ),
            instruction=(
                "Create `processed` and then copy `reports/tatooine.txt` to "
                "`processed/tatooine.txt` in one chained command."
            ),
            command="mkdir",
            mission_type=MissionType.INTRODUCE,
            new_skills=("command_chaining",),
            review_skills=("mkdir", "cp"),
            outcome=Outcome(files_present=("processed/tatooine.txt",)),
            multi_step=True,
            tips=[
                "The first operation is `mkdir processed`.",
                "Connect the folder creation and copy commands with `&&`.",
                "Exact answer: `mkdir processed && cp reports/tatooine.txt processed/tatooine.txt`.",
            ],
            canonical_steps=(
                CommandStep("mkdir", ("processed",)),
                CommandStep("cp", ("reports/tatooine.txt", "processed/tatooine.txt")),
            ),
            success="The dependent steps complete in order and the processed copy is safe.",
        ),
        TaskSpec(
            name="Assemble The Rebel Intelligence Digest",
            lesson=(
                "R2-D2 gives no exact syntax this time. Produce a sorted file containing only Rebel records. Use the "
                "search, connection, ordering, and saving tools you have already learned."
            ),
            instruction="Create `reports/rebel_sorted.txt` containing the sorted `REBEL` lines from the intercepts.",
            command="grep",
            mission_type=MissionType.COMBINE,
            review_skills=("grep", "sort", "pipes", "redirection"),
            outcome=Outcome(
                file_contents={
                    "reports/rebel_sorted.txt": (
                        "REBEL: Alderaan convoy is safe\nREBEL: Red Squadron awaiting orders"
                    )
                }
            ),
            multi_step=True,
            tips=[
                "Reduce the intercepts to lines containing `REBEL`.",
                "Pipe the matching lines through `sort`, then redirect the result.",
                "One solution: `grep REBEL transmissions/intercepts.txt | sort > reports/rebel_sorted.txt`.",
            ],
            canonical_steps=(
                CommandStep(
                    "write",
                    (
                        "reports/rebel_sorted.txt",
                        "REBEL: Alderaan convoy is safe\nREBEL: Red Squadron awaiting orders",
                    ),
                ),
            ),
            success="The final digest proves that simple tools can become a larger solution.",
        ),
    ],
    "6": [
        program_task(
            name="Give Fuel A Name",
            lesson=(
                "A variable gives a value a useful name. `fuel = 75` stores the number 75 so later instructions "
                "can talk about fuel instead of repeating a mystery number."
            ),
            filename="fuel.py",
            code_key="fuel.py",
            output="75",
            mission_type=MissionType.INTRODUCE,
            new_skills=("variables",),
            success="The droid remembers its fuel level and reports 75.",
        ),
        program_task(
            name="Identify The Droid's Ship",
            lesson=(
                "Programs store different kinds of data. Quoted text is a string, numbers measure quantities, "
                "and `True` or `False` records a yes-or-no fact."
            ),
            filename="identity.py",
            code_key="identity.py",
            output="Millennium Falcon True",
            mission_type=MissionType.INTRODUCE,
            new_skills=("data_types",),
            review_skills=("variables",),
            success="The droid can distinguish its ship name from its active status.",
        ),
        program_task(
            name="Calculate Remaining Fuel",
            lesson=(
                "An expression combines values and an operation to produce a new value. Subtracting `used` from "
                "`fuel` lets the computer calculate instead of making the pilot do arithmetic."
            ),
            filename="fuel_math.py",
            code_key="fuel_math.py",
            output="55",
            mission_type=MissionType.INTRODUCE,
            new_skills=("expressions",),
            review_skills=("variables", "data_types"),
            success="The droid calculates that 55 units of fuel remain.",
        ),
    ],
    "7": [
        program_task(
            name="Compare Fuel And Distance",
            lesson=(
                "A comparison asks a precise question and produces `True` or `False`. `fuel >= distance` asks "
                "whether there is at least enough fuel for the trip."
            ),
            filename="range_check.py",
            code_key="range_check.py",
            output="False",
            mission_type=MissionType.INTRODUCE,
            new_skills=("comparisons",),
            review_skills=("expressions",),
            success="The droid correctly warns that 40 fuel cannot cover 50 distance.",
        ),
        program_task(
            name="Choose Jump Or Refuel",
            lesson=(
                "An `if` and `else` give the computer rules for choosing behavior. The pilot supplies the rule now; "
                "the droid can apply it later without waiting for another command."
            ),
            filename="jump_rule.py",
            code_key="jump_rule.py",
            output="jump",
            mission_type=MissionType.INTRODUCE,
            new_skills=("conditions",),
            review_skills=("comparisons",),
            success="With enough fuel, the droid independently chooses to jump.",
        ),
        program_task(
            name="Combine Shield Conditions",
            lesson=(
                "Boolean logic connects yes-or-no facts. `and` requires both facts to be true, so shields rise only "
                "when an enemy is near and the shield system is ready."
            ),
            filename="shield_rule.py",
            code_key="shield_rule.py",
            output="raise shields",
            mission_type=MissionType.INTRODUCE,
            new_skills=("boolean_logic",),
            review_skills=("conditions",),
            success="The droid combines both safety checks before raising shields.",
        ),
    ],
    "8": [
        program_task(
            name="Remember A List Of Planets",
            lesson=(
                "A list stores an ordered collection under one name. Square brackets keep the values together, and "
                "an index selects one position. Python starts counting list positions at zero."
            ),
            filename="planets.py",
            code_key="planets.py",
            output="Naboo",
            mission_type=MissionType.INTRODUCE,
            new_skills=("lists",),
            review_skills=("variables", "data_types"),
            success="The droid retrieves Naboo from the second list position.",
        ),
        program_task(
            name="Scan Every Planet",
            lesson=(
                "A `for` loop repeats instructions for every value in a collection. This is where the computer takes "
                "over tedious repetition without losing precision."
            ),
            filename="scanner.py",
            code_key="scanner.py",
            output="scanning Endor",
            mission_type=MissionType.INTRODUCE,
            new_skills=("loops",),
            review_skills=("conditions", "lists"),
            success="One loop scans Hoth, Naboo, and Endor in order.",
        ),
        program_task(
            name="Transfer The Loop To Sectors",
            lesson=(
                "The same repetition idea works on generated numbers. `range(1, 5)` supplies sectors 1 through 4, "
                "showing that a concept can transfer to different data."
            ),
            filename="counter.py",
            code_key="counter.py",
            output="sector 4",
            mission_type=MissionType.TRANSFER,
            review_skills=("loops",),
            success="The loop transfers from planet names to numbered sectors.",
        ),
    ],
    "9": [
        program_task(
            name="Package A Scouting Routine",
            lesson=(
                "A function gives a meaningful name to reusable behavior. Defining `scan` once prevents the same "
                "instructions from being copied everywhere."
            ),
            filename="function.py",
            code_key="function.py",
            output="scan analyze report\nscan analyze report",
            mission_type=MissionType.INTRODUCE,
            new_skills=("functions",),
            review_skills=("variables", "conditions", "loops"),
            success="The reusable scouting routine runs twice from one definition.",
        ),
        program_task(
            name="Give The Function A Target",
            lesson=(
                "A parameter is an input name inside a function. The same scanning behavior can now receive Dagobah, "
                "Endor, or any later target without being rewritten."
            ),
            filename="parameter.py",
            code_key="parameter.py",
            output="scanning Dagobah",
            mission_type=MissionType.INTRODUCE,
            new_skills=("parameters",),
            review_skills=("functions",),
            success="The scouting function accepts Dagobah as its target.",
        ),
        program_task(
            name="Return A Fuel Answer",
            lesson=(
                "A return value sends an answer back from a function. This lets one solution feed another part of a "
                "program instead of only printing a message."
            ),
            filename="return.py",
            code_key="return.py",
            output="55",
            mission_type=MissionType.INTRODUCE,
            new_skills=("return_values",),
            review_skills=("functions", "expressions"),
            success="The function returns 55 fuel units to its caller.",
        ),
        program_task(
            name="Map Ship Names To Counts",
            lesson=(
                "A mapping stores key/value pairs. Looking up `X-Wing` is clearer than remembering a numeric list "
                "position, because the key describes exactly what the value means."
            ),
            filename="mapping.py",
            code_key="mapping.py",
            output="5",
            mission_type=MissionType.INTRODUCE,
            new_skills=("mappings",),
            review_skills=("lists",),
            success="The fleet mapping reports five X-Wings immediately.",
        ),
        program_task(
            name="Search For The Rebel Signal",
            lesson=(
                "An algorithm is a set of steps for solving a problem. This search checks each planet and reports "
                "when its comparison finds Endor."
            ),
            filename="search.py",
            code_key="search.py",
            output="signal found Endor",
            mission_type=MissionType.INTRODUCE,
            new_skills=("search_algorithms",),
            review_skills=("loops", "lists", "functions"),
            success="The step-by-step search locates the signal on Endor.",
        ),
        program_task(
            name="Order Ships By Fuel",
            lesson=(
                "Sorting is another algorithmic problem. Python's `sorted` tool returns the levels in order, letting "
                "the engineers focus on why ordering helps the mission."
            ),
            filename="sorting.py",
            code_key="sorting.py",
            output="[10, 30, 50, 90]",
            mission_type=MissionType.INTRODUCE,
            new_skills=("sorting_algorithms",),
            review_skills=("comparisons", "loops", "lists"),
            success="The ships are ordered from the lowest fuel level to the highest.",
        ),
    ],
    "10": [
        TaskSpec(
            name="Observe The Navigation Bug",
            lesson=(
                "Debugging begins by reproducing a problem. The ship has only 20 fuel for a distance of 50, but "
                "the program unexpectedly says `jump`. Run it before changing anything and compare actual behavior "
                "with the expected `refuel`."
            ),
            instruction="Run `diagnostics/broken_navigation.py` and observe its incorrect output.",
            command="python",
            mission_type=MissionType.INTRODUCE,
            new_skills=("debugging",),
            review_skills=("conditions", "comparisons"),
            args=("diagnostics/broken_navigation.py",),
            success="You reproduced the failure: expected refuel, actual jump. That evidence points to the comparison.",
        ),
        TaskSpec(
            name="Repair The Reversed Comparison",
            lesson=(
                "Change one suspected line, then rerun the same case. `edit` replaces a numbered line without "
                "rewriting the whole file. Line 3 should allow a jump only when fuel is at least the distance."
            ),
            instruction=(
                "Use `edit diagnostics/broken_navigation.py 3 \"if fuel >= distance:\"`, then run the program "
                "and confirm that it reports `refuel`."
            ),
            command="edit",
            mission_type=MissionType.DEBUG,
            review_skills=("debugging", "conditions", "comparisons"),
            outcome=Outcome(
                file_contents={
                    "diagnostics/broken_navigation.py": (
                        'fuel = 20\ndistance = 50\nif fuel >= distance:\n    print("jump")\n'
                        'else:\n    print("refuel")'
                    )
                },
                output_contains=("refuel",),
                required_commands=("edit", "python"),
            ),
            multi_step=True,
            tips=[
                "The condition is on line 3; compare its direction with the intended behavior.",
                "Replace line 3 with `if fuel >= distance:` and run the file again.",
                "Commands: `edit diagnostics/broken_navigation.py 3 \"if fuel >= distance:\"`, then `python diagnostics/broken_navigation.py`.",
            ],
            canonical_steps=(
                CommandStep("edit", ("diagnostics/broken_navigation.py", "3", "if fuel >= distance:")),
            ),
            success="Expected and actual behavior now agree: the under-fueled ship chooses to refuel.",
        ),
        TaskSpec(
            name="Repair A Syntax Fault",
            lesson=(
                "Some bugs prevent a program from starting. Python identifies the line where its grammar became "
                "invalid. The `if` on line 2 needs a colon to mark the beginning of its instruction block."
            ),
            instruction="Add the missing colon to line 2 of `diagnostics/syntax_fault.py`, then run it.",
            command="edit",
            mission_type=MissionType.DEBUG,
            review_skills=("debugging", "conditions"),
            outcome=Outcome(
                file_contents={
                    "diagnostics/syntax_fault.py": (
                        'enemy_near = True\nif enemy_near:\n    print("raise shields")'
                    )
                },
                output_contains=("raise shields",),
                required_commands=("edit", "python"),
            ),
            multi_step=True,
            tips=[
                "Python conditions end with a colon before the indented instructions.",
                "Use `edit` on line 2, then rerun with `python`.",
                "Commands: `edit diagnostics/syntax_fault.py 2 \"if enemy_near:\"`, then `python diagnostics/syntax_fault.py`.",
            ],
            canonical_steps=(CommandStep("edit", ("diagnostics/syntax_fault.py", "2", "if enemy_near:")),),
            success="The syntax fault is gone and the shield command runs.",
        ),
        TaskSpec(
            name="Make The Simulations Pass",
            lesson=(
                "Tests are automated questions about expected behavior. `test` runs the assertions in a Python file. "
                "The current function has its comparison reversed; repair it and let both cases verify the result."
            ),
            instruction=(
                "Change line 2 of `diagnostics/jump_tests.py` to `return fuel >= distance`, then run "
                "`test diagnostics/jump_tests.py`."
            ),
            command="edit",
            mission_type=MissionType.INTRODUCE,
            new_skills=("testing",),
            review_skills=("debugging", "return_values"),
            outcome=Outcome(
                file_contents={
                    "diagnostics/jump_tests.py": (
                        "def can_jump(fuel, distance):\n    return fuel >= distance\n\n"
                        "assert can_jump(100, 50) == True\nassert can_jump(20, 50) == False"
                    )
                },
                output_contains=("All Rebel simulation tests passed.",),
                required_commands=("edit", "test"),
            ),
            multi_step=True,
            tips=[
                "The first assertion expects enough fuel to return True; inspect line 2's comparison.",
                "Edit line 2 to use `>=`, then run the test command.",
                "Commands: `edit diagnostics/jump_tests.py 2 \"    return fuel >= distance\"`, then `test diagnostics/jump_tests.py`.",
            ],
            canonical_steps=(
                CommandStep("edit", ("diagnostics/jump_tests.py", "2", "    return fuel >= distance")),
            ),
            success="Both simulations pass, so the repaired rule handles enough and insufficient fuel.",
        ),
    ],
    "11": [
        TaskSpec(
            name="Inspect Repository State",
            lesson=(
                "A repository remembers project history. `git status` compares your working files with the latest "
                "saved snapshot before you decide what to do next."
            ),
            instruction="Inspect the simulated repository with `git status`.",
            command="git",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_status",),
            args=("status",),
            success="The repository reports a clean working tree on the main branch.",
        ),
        TaskSpec(
            name="Review An Exact Change",
            lesson=(
                "Engineers inspect a change before trusting it. Change the shield setting, then `git diff` will show "
                "the old and new lines instead of making you reread every file."
            ),
            instruction=(
                "Edit line 2 of `mission_plan.py` to `shields = True`, then inspect the change with `git diff`."
            ),
            command="edit",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_diff",),
            review_skills=("git_status", "debugging"),
            outcome=Outcome(
                file_contents={"mission_plan.py": 'route = "Hoth"\nshields = True'},
                output_contains=("-shields = False", "+shields = True"),
                required_commands=("edit", "git"),
            ),
            multi_step=True,
            tips=[
                "Use `edit mission_plan.py 2` to change only the shield line.",
                "After the edit, `git diff` displays the exact before-and-after text.",
                "Commands: `edit mission_plan.py 2 \"shields = True\"`, then `git diff`.",
            ],
            canonical_steps=(CommandStep("edit", ("mission_plan.py", "2", "shields = True")),),
            success="The diff makes the shield change visible before it enters history.",
        ),
        TaskSpec(
            name="Stage A Route Change",
            lesson=(
                "Staging chooses what belongs in the next snapshot. After changing the route, `git add .` stages the "
                "working project and `git status` confirms that choice."
            ),
            instruction=(
                "Change line 1 to `route = \"Endor\"`, stage the project with `git add .`, then inspect status."
            ),
            command="edit",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_add",),
            review_skills=("git_diff",),
            outcome=Outcome(
                file_contents={"mission_plan.py": 'route = "Endor"\nshields = True'},
                output_contains=("Changes staged for commit.",),
                required_commands=("edit", "git"),
            ),
            multi_step=True,
            tips=[
                "Edit line 1 first, then stage all training files with `git add .`.",
                "Run `git status` after staging to inspect the repository state.",
                "Commands: `edit mission_plan.py 1 'route = \"Endor\"'`, `git add .`, then `git status`.",
            ],
            canonical_steps=(CommandStep("edit", ("mission_plan.py", "1", 'route = "Endor"')),),
            success="The route change is deliberately staged for the next snapshot.",
        ),
        TaskSpec(
            name="Commit A Mission Snapshot",
            lesson=(
                "A commit saves staged work with a message explaining why it matters. Good history is a sequence of "
                "meaningful, recoverable decisions rather than an unexplained pile of files."
            ),
            instruction=(
                "Change line 1 to `route = \"Dagobah\"`, stage it, and commit with the message `Choose Dagobah`."
            ),
            command="edit",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_commit",),
            review_skills=("git_add",),
            outcome=Outcome(
                file_contents={"mission_plan.py": 'route = "Dagobah"\nshields = True'},
                output_contains=("Committed", "Choose Dagobah"),
                required_commands=("edit", "git"),
            ),
            multi_step=True,
            tips=[
                "Edit the route, then stage with `git add .`.",
                "A commit message follows `-m` and should be quoted.",
                "Finish with `git commit -m \"Choose Dagobah\"`.",
            ],
            canonical_steps=(CommandStep("edit", ("mission_plan.py", "1", 'route = "Dagobah"')),),
            success="The Dagobah decision is stored as a named, recoverable snapshot.",
        ),
        TaskSpec(
            name="Read Repository History",
            lesson=(
                "`git log` displays saved snapshots from newest to oldest. History answers who changed the plan and "
                "why without relying on memory."
            ),
            instruction="Inspect the simulated history with `git log`.",
            command="git",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_log",),
            review_skills=("git_commit",),
            args=("log",),
            success="The initial Rebel snapshot appears in repository history.",
        ),
        TaskSpec(
            name="Create An Alternate Plan",
            lesson=(
                "A branch gives an alternate line of work a name. The main plan remains stable while engineers "
                "explore another route."
            ),
            instruction="Create a branch named `rescue-route` with `git branch rescue-route`.",
            command="git",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_branch",),
            review_skills=("git_log",),
            args=("branch", "rescue-route"),
            success="The rescue-route branch points to the current safe snapshot.",
        ),
        TaskSpec(
            name="Merge A Successful Route",
            lesson=(
                "Now use the complete collaboration cycle. Create and switch to a branch, change the route, commit "
                "the branch, return to main, and merge the successful plan."
            ),
            instruction=(
                "On a branch named `endor-route`, commit `route = \"Endor\"`, then merge that branch into `main`."
            ),
            command="git",
            mission_type=MissionType.INTRODUCE,
            new_skills=("git_merge",),
            review_skills=("git_branch", "git_commit"),
            outcome=Outcome(
                file_contents={"mission_plan.py": 'route = "Endor"\nshields = True'},
                output_contains=("Merged endor-route into main.",),
                required_commands=("git", "edit"),
            ),
            multi_step=True,
            tips=[
                "Create `endor-route`, switch to it, and edit line 1 before staging and committing.",
                "After the branch commit, `git switch main` returns to the stable plan.",
                "Finish with `git merge endor-route`.",
            ],
            canonical_steps=(CommandStep("edit", ("mission_plan.py", "1", 'route = "Endor"')),),
            success="The alternate Endor work is safely merged into the main mission plan.",
        ),
    ],
    "12": [
        TaskSpec(
            name="Secure The Fleet Location",
            lesson=(
                "Leia knows one incoming file contains a verified fleet location. Explore the intelligence area, "
                "find the useful line, and save only that line in the safe folder. The final state matters; choose "
                "the commands yourself."
            ),
            instruction="Create `safe/fleet_location.txt` containing exactly `FLEET: Dantooine`.",
            command="grep",
            mission_type=MissionType.CAPSTONE,
            review_skills=("find", "grep", "pipes", "redirection", "relative_paths"),
            outcome=Outcome(file_contents={"safe/fleet_location.txt": "FLEET: Dantooine"}),
            multi_step=True,
            story_flags=("fleet_location_secured",),
            tips=[
                "Inspect or search the files under `intelligence/incoming` for the fleet marker.",
                "Use `grep` on the relevant log and redirect its matching line into the safe folder.",
                "One solution: `grep FLEET intelligence/incoming/beta.log > safe/fleet_location.txt`.",
            ],
            canonical_steps=(CommandStep("write", ("safe/fleet_location.txt", "FLEET: Dantooine")),),
            success="The verified fleet location is isolated from the decoys and stored safely.",
        ),
        TaskSpec(
            name="Preserve The Route And Remove The Tracker",
            lesson=(
                "The intelligence folder contains both a navigation map and Imperial tracking data. Preserve what "
                "the fleet needs, remove what threatens it, and verify targets before using destructive operations."
            ),
            instruction=(
                "Copy `intelligence/navigation.map` to `safe/navigation.map` and remove "
                "`intelligence/imperial_tracker.dat`."
            ),
            command="cp",
            mission_type=MissionType.CAPSTONE,
            review_skills=("ls", "cat", "cp", "rm", "relative_paths"),
            outcome=Outcome(
                files_present=("safe/navigation.map",),
                files_absent=("intelligence/imperial_tracker.dat",),
                file_contents={"safe/navigation.map": "Route: Dantooine -> Endor"},
            ),
            multi_step=True,
            story_flags=("tracker_destroyed", "navigation_preserved"),
            tips=[
                "Inspect both targets so you know which must survive.",
                "Use `cp` for the map and `rm` for the tracker; either safe order can work.",
                "One solution: `cp intelligence/navigation.map safe/navigation.map`, then `rm intelligence/imperial_tracker.dat`.",
            ],
            canonical_steps=(
                CommandStep("cp", ("intelligence/navigation.map", "safe/navigation.map")),
                CommandStep("rm", ("intelligence/imperial_tracker.dat",)),
            ),
            success="The escape route is safe and the Imperial tracker is gone.",
        ),
        TaskSpec(
            name="Repair The Fleet Defense Program",
            lesson=(
                "The defense program lowers shields while an enemy is near. Reproduce or inspect the behavior, fix "
                "the faulty logic, and run it until the actual output is `shields raised`."
            ),
            instruction="Repair `programs/defense.py` so running it prints `shields raised`.",
            command="edit",
            mission_type=MissionType.CAPSTONE,
            review_skills=("debugging", "testing", "conditions", "boolean_logic"),
            outcome=Outcome(
                files_present=("programs/defense.py",),
                output_contains=("shields raised",),
                required_commands=("python",),
            ),
            multi_step=True,
            story_flags=("defense_program_repaired",),
            tips=[
                "Compare `enemy_near` with the condition on line 2.",
                "Change only the incorrect comparison, then run the program again.",
                "One solution: `edit programs/defense.py 2 \"if enemy_near == True:\"`, then `python programs/defense.py`.",
            ],
            canonical_steps=(
                CommandStep("edit", ("programs/defense.py", "2", "if enemy_near == True:")),
            ),
            success="The repaired program raises shields when danger is present.",
        ),
        TaskSpec(
            name="Automate The Final Planet Scan",
            lesson=(
                "Create any Python program that uses your programming knowledge and prints a result containing "
                "`Dantooine`. The validator checks the behavior, not one exact implementation."
            ),
            instruction="Create `programs/final_scan.py` and run it so its output includes `Dantooine`.",
            command="write",
            mission_type=MissionType.CAPSTONE,
            review_skills=("variables", "lists", "loops", "conditions", "functions", "search_algorithms"),
            outcome=Outcome(
                files_present=("programs/final_scan.py",),
                output_contains=("Dantooine",),
                required_commands=("python",),
            ),
            multi_step=True,
            story_flags=("final_scan_automated",),
            tips=[
                "Start with a small correct program; it may use a variable, list, loop, or function.",
                "Save the program with `write`, then execute it with `python`.",
                "A minimal solution is `write programs/final_scan.py 'print(\"Dantooine\")'`, then `python programs/final_scan.py`.",
            ],
            canonical_steps=(
                CommandStep(
                    "write",
                    (
                        "programs/final_scan.py",
                        'planets = ["Hoth", "Dantooine", "Endor"]\nfor planet in planets:\n'
                        '    if planet == "Dantooine":\n        print("located", planet)',
                    ),
                ),
            ),
            success="Your independent program locates Dantooine and reports it to the fleet.",
        ),
        TaskSpec(
            name="Commit The Completed Mission",
            lesson=(
                "Leave the next engineer a clear, recoverable final state. Update the mission summary, inspect what "
                "changed if useful, stage the work, and commit it with a meaningful message of your choice."
            ),
            instruction=(
                "Change `mission_summary.txt` to `MISSION COMPLETE`, then save that change in a simulated commit."
            ),
            command="write",
            mission_type=MissionType.CAPSTONE,
            review_skills=("git_status", "git_diff", "git_add", "git_commit", "testing"),
            outcome=Outcome(
                file_contents={"mission_summary.txt": "MISSION COMPLETE"},
                output_contains=("Committed",),
                required_commands=("git",),
            ),
            multi_step=True,
            story_flags=("final_campaign_complete",),
            tips=[
                "Use `write` to update the summary, then inspect or stage the repository.",
                "Stage with `git add .`, then create a commit with `git commit -m` and your message.",
                "One solution ends with `git commit -m \"Complete final mission\"`.",
            ],
            canonical_steps=(CommandStep("write", ("mission_summary.txt", "MISSION COMPLETE")),),
            success="The fleet is safe, the systems work, and the complete solution is preserved in history.",
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
    "echo": "Use `echo` to ask the terminal to produce text output.",
    "clear": "Use `clear` to wipe old output from the terminal display.",
    "write": "Use `write file \"text\"` to replace a file with one line of text.",
    "append": "Use `append file \"text\"` to add a new line to a file.",
    "edit": "Use `edit file line \"text\"` to replace one numbered line.",
    "cp": "Use `cp old new` to make a safe copy while keeping the original.",
    "mv": "Use `mv old new` to move a file into its proper place.",
    "rm": "Use `rm` to remove a file.",
    "rmdir": "Use `rmdir` to remove an empty folder.",
    "tree": "Use `tree` to draw the whole folder map.",
    "find": "Use `find name` to search the ship by file name.",
    "grep": "Use `grep pattern file` to keep lines containing a pattern.",
    "head": "Use `head` to inspect the first lines of data.",
    "tail": "Use `tail` to inspect the final lines of data.",
    "wc": "Use `wc` to count parts of data.",
    "sort": "Use `sort` to put lines into order.",
    "python": "Use `python file.py` to run a Python program.",
    "test": "Use `test file.py` to run the Rebel simulation checks.",
    "git": "Use a `git` subcommand to inspect or manage simulated history.",
}


SUCCESS_LINES = {
    "help": "The command guide opens in your console.",
    "pwd": "You checked your current coordinates.",
    "ls": "You scanned the area successfully.",
    "mkdir": "A new Rebel workspace is ready.",
    "cd": "You moved to the right place.",
    "touch": "The file is ready.",
    "cat": "The report is now on screen.",
    "echo": "The terminal produced your message.",
    "clear": "The terminal display is clear.",
    "write": "The file has fresh orders.",
    "append": "You added a new line to the report.",
    "edit": "You changed one precise line.",
    "cp": "The copy is in place.",
    "mv": "The item has been moved.",
    "rm": "The file is gone.",
    "rmdir": "The empty folder is gone too.",
    "tree": "The full layout is visible.",
    "find": "You tracked it down.",
    "grep": "You filtered the intelligence.",
    "head": "You inspected the start of the data.",
    "tail": "You inspected the end of the data.",
    "wc": "You counted the records.",
    "sort": "The records are now ordered.",
    "python": "The program ran.",
    "test": "The simulations passed.",
    "git": "The repository operation completed.",
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
                mission_type=spec.mission_type,
                new_skills=spec.new_skills,
                review_skills=spec.review_skills,
                outcome=spec.outcome,
                multi_step=spec.multi_step,
                story_flags=spec.story_flags,
                tips=spec.tips or build_tips(spec.command, args),
                success=spec.success or success_line(spec.command),
                scenario=build_scenario(snapshot),
            )
        )
        if spec.canonical_steps:
            for step in spec.canonical_steps:
                apply_expected(self.fs, step.command, list(step.args))
        elif spec.outcome is not None:
            return
        else:
            apply_expected(self.fs, spec.command, args)


def build_tasks() -> list[Task]:
    builder = CampaignBuilder()
    builder.set_world(**WORLD)

    for chapter_key in ("1", "2", "3"):
        builder.use_chapter(chapter_key)
        for spec in CHAPTER_TASKS[chapter_key]:
            builder.add_task_spec(spec)

    builder.set_world(**INTELLIGENCE_WORLD)
    for chapter_key in ("4", "5"):
        builder.use_chapter(chapter_key)
        for spec in CHAPTER_TASKS[chapter_key]:
            builder.add_task_spec(spec)

    builder.set_world(**DROID_WORLD)
    for chapter_key in ("6", "7", "8", "9"):
        builder.use_chapter(chapter_key)
        for spec in CHAPTER_TASKS[chapter_key]:
            builder.add_task_spec(spec)

    builder.use_chapter("10")
    for spec in CHAPTER_TASKS["10"]:
        builder.add_task_spec(spec)

    builder.set_world(**REPOSITORY_WORLD)
    builder.use_chapter("11")
    for spec in CHAPTER_TASKS["11"]:
        builder.add_task_spec(spec)

    builder.set_world(**FINAL_WORLD)
    builder.use_chapter("12")
    for spec in CHAPTER_TASKS["12"]:
        builder.add_task_spec(spec)

    validate_campaign(builder.tasks)
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
    elif command in {"help", "pwd", "clear"}:
        second = f"Try this exact command: `{format_command(command, args)}`."
    elif command in {
        "ls", "tree", "cd", "mkdir", "touch", "cat", "rm", "rmdir", "find", "python",
        "grep", "head", "tail", "wc", "sort",
    }:
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
    if command in {"help", "pwd", "clear", "echo", "git"}:
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
    if command == "edit":
        fs.replace_line(args[0], int(args[1]), args[2])
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
    if command in {"grep", "head", "tail", "wc", "sort"}:
        path = args[-1] if args and not args[-1].startswith("-") else None
        if path and command == "grep" and len(args) < 2:
            path = None
        if path:
            fs.read_file(path)
        return
    if command in {"python", "test"}:
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
