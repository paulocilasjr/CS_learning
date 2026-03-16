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
    unit_key: str
    unit_name: str
    unit_intro: str
    name: str
    instruction: str
    expected_command: str
    expected_args: list[str]
    tips: list[str]
    success: str
    scenario: Scenario


@dataclass(frozen=True)
class Unit:
    key: str
    name: str
    intro: str
    badge: str


UNITS = {
    "1": Unit(
        key="1",
        name="Command Camp",
        intro="This is your first shell campsite. The operating system is the computer's helper. It keeps files and folders organized, and the shell is how we talk to it.",
        badge="Map Reader",
    ),
    "2": Unit(
        key="2",
        name="Path Park",
        intro="Paths are the road signs of the computer world. They tell the shell exactly where to go.",
        badge="Path Finder",
    ),
    "3": Unit(
        key="3",
        name="Story Scrolls",
        intro="Files can hold words, plans, and later even code. In this zone, you will practice writing and reading lines.",
        badge="Word Builder",
    ),
    "4": Unit(
        key="4",
        name="Move Mountain",
        intro="Smart computer explorers do not just create files. They also organize them by copying and moving them into better places.",
        badge="Mover Shaker",
    ),
    "5": Unit(
        key="5",
        name="Clean-Up Canyon",
        intro="Tidying up matters. Now you will remove files and empty folders the safe way.",
        badge="Cleanup Captain",
    ),
    "6": Unit(
        key="6",
        name="Search Safari",
        intro="Big computers can hold lots of stuff. Search commands help us track down what we need fast.",
        badge="Search Scout",
    ),
    "7": Unit(
        key="7",
        name="Project Plaza",
        intro="Real coding starts with a project folder. You will build one, organize it, and keep notes inside it.",
        badge="Project Planner",
    ),
    "8": Unit(
        key="8",
        name="Code Cave I",
        intro="Now the magic starts. Code is just text in a file until we ask Python to run it.",
        badge="Code Spark",
    ),
    "9": Unit(
        key="9",
        name="Code Cave II",
        intro="You already know how to run code. Next up: numbers, loops, and tiny programs with more than one idea inside them.",
        badge="Loop Leader",
    ),
    "10": Unit(
        key="10",
        name="Robot Finale",
        intro="Final zone. You will make little scripts that feel like real mini-programs and finish with a project map check.",
        badge="Terminal Hero",
    ),
}


def build_tasks() -> list[Task]:
    builder = CourseBuilder()
    builder.set_world(
        cwd="/home",
        dirs=["/home"],
        files={"/home/welcome.txt": "Welcome to Command Camp!"},
    )
    add_unit_1(builder)
    add_unit_2(builder)
    add_unit_3(builder)
    add_unit_4(builder)
    add_unit_5(builder)
    add_unit_6(builder)
    add_unit_7(builder)
    add_unit_8(builder)
    add_unit_9(builder)
    add_unit_10(builder)
    return builder.tasks


class CourseBuilder:
    def __init__(self) -> None:
        self.fs = VirtualFileSystem()
        self.tasks: list[Task] = []
        self.current_unit = UNITS["1"]

    def set_world(self, *, cwd: str, dirs: list[str], files: dict[str, str]) -> None:
        self.fs.load_snapshot(cwd=cwd, dirs=dirs, files=files)

    def use_unit(self, key: str) -> None:
        self.current_unit = UNITS[key]

    def add(self, name: str, instruction: str, command: str, *args: str) -> None:
        snapshot = self.fs.snapshot()
        self.tasks.append(
            Task(
                number=len(self.tasks) + 1,
                unit_key=self.current_unit.key,
                unit_name=self.current_unit.name,
                unit_intro=self.current_unit.intro,
                name=name,
                instruction=instruction,
                expected_command=command,
                expected_args=list(args),
                tips=build_tips(command, list(args)),
                success=success_line(command),
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
        "help": "Use `help` to see the list of commands you can use in this game shell.",
        "pwd": "Use `pwd` to ask the shell, 'Where am I right now?'",
        "ls": "Use `ls` to look around and list files and folders.",
        "mkdir": "Use `mkdir` to make a new folder.",
        "cd": "Use `cd` to move into a folder or path.",
        "touch": "Use `touch` to make a new empty file.",
        "cat": "Use `cat` to read what is inside a file.",
        "write": "Use `write file \"words\"` to put text into a file.",
        "append": "Use `append file \"words\"` to add a new line to the end of a file.",
        "cp": "Use `cp old new` to make a copy.",
        "mv": "Use `mv old new` to move or rename something.",
        "rm": "Use `rm` to remove a file.",
        "rmdir": "Use `rmdir` to remove an empty folder.",
        "tree": "Use `tree` to see a folder and everything inside it.",
        "find": "Use `find name` to search for a file or folder by name.",
        "python": "Use `python file.py` to run a Python program.",
    }[command]

    if command in {"help", "pwd"}:
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
    return {
        "help": "Nice work. You opened the guide book.",
        "pwd": "Nice work. You checked your place on the map.",
        "ls": "Nice work. You looked around your current area.",
        "mkdir": "Nice work. A new folder is ready.",
        "cd": "Nice work. You moved to the right place.",
        "touch": "Nice work. The new file is ready.",
        "cat": "Nice work. You read the file.",
        "write": "Nice work. You wrote text into the file.",
        "append": "Nice work. You added a fresh new line.",
        "cp": "Nice work. You made a copy.",
        "mv": "Nice work. You moved it into place.",
        "rm": "Nice work. That file is gone.",
        "rmdir": "Nice work. The empty folder is gone too.",
        "tree": "Nice work. You checked the full folder tree.",
        "find": "Nice work. You tracked it down.",
        "python": "Nice work. Your program ran.",
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
        fs.ls(args[0] if args else None)
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


def add_unit_1(builder: CourseBuilder) -> None:
    builder.use_unit("1")
    builder.add("Open the Guide", "Type the command that shows the shell's built-in help list.", "help")
    builder.add("Where Am I?", "Ask the shell to show your current folder.", "pwd")
    builder.add("Look Around", "List the things in this folder so you can see what is here.", "ls")
    builder.add("Make a Den", "Create a new folder named `den`.", "mkdir", "den")
    builder.add("Check Again", "List the folder again so you can spot your new `den`.", "ls")
    builder.add("Step Inside", "Move into the `den` folder.", "cd", "den")
    builder.add("Map Check", "Ask where you are now that you are inside `den`.", "pwd")
    builder.add("Make a File", "Create an empty file named `acorn.txt`.", "touch", "acorn.txt")
    builder.add("See the File", "List this folder to make sure `acorn.txt` is here.", "ls")
    builder.add("Read the Empty File", "Open `acorn.txt` and read it, even though it is empty right now.", "cat", "acorn.txt")
    builder.add("Write Words", "Put the words `golden acorn` into `acorn.txt`.", "write", "acorn.txt", "golden acorn")
    builder.add("Read It Back", "Read `acorn.txt` again so you can see the words you wrote.", "cat", "acorn.txt")
    builder.add("Go Back Up", "Move back to the parent folder.", "cd", "..")
    builder.add("See the Whole Camp", "Show the tree for where you are standing now.", "tree")
    builder.add("Pack a Bag", "Create a folder named `backpack` in `/home`.", "mkdir", "backpack")


def add_unit_2(builder: CourseBuilder) -> None:
    builder.use_unit("2")
    builder.add("Into the Backpack", "Move into the `backpack` folder.", "cd", "backpack")
    builder.add("Snack Pocket", "Create a folder named `snacks` here.", "mkdir", "snacks")
    builder.add("Open Snacks", "Move into the `snacks` folder.", "cd", "snacks")
    builder.add("Apple Note", "Create a file named `apple.txt`.", "touch", "apple.txt")
    builder.add("Back One Step", "Go back up one folder.", "cd", "..")
    builder.add("Toy Pocket", "Create another folder named `toys`.", "mkdir", "toys")
    builder.add("Peek Around", "List the current folder to see both pockets.", "ls")
    builder.add("Open Toys", "Move into the `toys` folder.", "cd", "toys")
    builder.add("Robot File", "Create a file named `robot.txt`.", "touch", "robot.txt")
    builder.add("Full Path Check", "Ask the shell to show your full path.", "pwd")
    builder.add("Jump to Root", "Move all the way to the root folder `/`.", "cd", "/")
    builder.add("Look at Home", "List the things inside `/home` without moving there.", "ls", "/home")
    builder.add("Big Home Tree", "Show the full tree for `/home`.", "tree", "/home")
    builder.add("Find the Robot", "Search from where you are now for a file named `robot.txt`.", "find", "robot.txt")
    builder.add("Fast Travel", "Move straight to `/home/backpack` in one command.", "cd", "/home/backpack")


def add_unit_3(builder: CourseBuilder) -> None:
    builder.use_unit("3")
    builder.add("Back Home", "Move to `/home` so you can start a new writing area.", "cd", "/home")
    builder.add("Story Shelf", "Create a new folder named `stories`.", "mkdir", "stories")
    builder.add("Open Stories", "Move into the `stories` folder.", "cd", "stories")
    builder.add("Dragon File", "Create a file named `dragon.txt`.", "touch", "dragon.txt")
    builder.add("First Story Line", "Write `The dragon naps.` into `dragon.txt`.", "write", "dragon.txt", "The dragon naps.")
    builder.add("Read the Story", "Read `dragon.txt` to see the first line.", "cat", "dragon.txt")
    builder.add("Add a Line", "Append `It likes marshmallows.` to `dragon.txt`.", "append", "dragon.txt", "It likes marshmallows.")
    builder.add("Read Both Lines", "Read `dragon.txt` again to see both lines.", "cat", "dragon.txt")
    builder.add("Costume List", "Create an empty file named `list.txt`.", "touch", "list.txt")
    builder.add("Write Item One", "Write `hat` into `list.txt`.", "write", "list.txt", "hat")
    builder.add("Write Item Two", "Append `cape` to `list.txt`.", "append", "list.txt", "cape")
    builder.add("Write Item Three", "Append `boots` to `list.txt`.", "append", "list.txt", "boots")
    builder.add("Read the List", "Read `list.txt` to see the whole costume list.", "cat", "list.txt")
    builder.add("Rename the List", "Rename `list.txt` to `costume.txt`.", "mv", "list.txt", "costume.txt")
    builder.add("Make a Copy", "Copy `costume.txt` into a new file named `costume-copy.txt`.", "cp", "costume.txt", "costume-copy.txt")


def add_unit_4(builder: CourseBuilder) -> None:
    builder.use_unit("4")
    builder.add("See Your Files", "List this folder to spot the story and both costume files.", "ls")
    builder.add("Make an Attic", "Create a folder named `attic`.", "mkdir", "attic")
    builder.add("Move the Copy", "Move `costume-copy.txt` into the `attic` folder.", "mv", "costume-copy.txt", "attic")
    builder.add("Check the Tree", "Show the tree so you can see where everything lives now.", "tree")
    builder.add("Copy the Dragon", "Copy `dragon.txt` to `attic/dragon-copy.txt`.", "cp", "dragon.txt", "attic/dragon-copy.txt")
    builder.add("Look in the Attic", "List the contents of `attic`.", "ls", "attic")
    builder.add("Make an Archive", "Create a folder named `archive`.", "mkdir", "archive")
    builder.add("Move the Original", "Move `dragon.txt` into `archive/dragon.txt`.", "mv", "dragon.txt", "archive/dragon.txt")
    builder.add("Tree Check", "Show the tree again to see the new layout.", "tree")
    builder.add("Climb Up", "Move into the `attic` folder.", "cd", "attic")
    builder.add("Attic Path", "Ask the shell where you are now.", "pwd")
    builder.add("Back to Stories", "Go back to the parent folder.", "cd", "..")
    builder.add("Read from Archive", "Read the file `archive/dragon.txt`.", "cat", "archive/dragon.txt")
    builder.add("Rename the Copy", "Rename `attic/dragon-copy.txt` to `attic/sleepy-dragon.txt`.", "mv", "attic/dragon-copy.txt", "attic/sleepy-dragon.txt")
    builder.add("List the Attic Again", "List `attic` so you can see the renamed file.", "ls", "attic")


def add_unit_5(builder: CourseBuilder) -> None:
    builder.use_unit("5")
    builder.add("Remove One File", "Delete `attic/sleepy-dragon.txt`.", "rm", "attic/sleepy-dragon.txt")
    builder.add("Check the Attic", "List `attic` to see what is left.", "ls", "attic")
    builder.add("Temporary File", "Create `attic/temp.txt`.", "touch", "attic/temp.txt")
    builder.add("Delete Temp", "Remove `attic/temp.txt`.", "rm", "attic/temp.txt")
    builder.add("Clear the Last File", "Remove `attic/costume-copy.txt`.", "rm", "attic/costume-copy.txt")
    builder.add("Empty Attic Check", "List `attic` to make sure it is empty.", "ls", "attic")
    builder.add("Remove Attic", "Delete the empty folder `attic`.", "rmdir", "attic")
    builder.add("Whole Tree Check", "Show the tree here after cleaning up.", "tree")
    builder.add("Delete Archive File", "Remove `archive/dragon.txt`.", "rm", "archive/dragon.txt")
    builder.add("Remove Archive", "Delete the now-empty folder `archive`.", "rmdir", "archive")
    builder.add("Back Home Again", "Move to `/home`.", "cd", "/home")
    builder.add("Make Cleanup Zone", "Create a folder named `cleanup`.", "mkdir", "cleanup")
    builder.add("Trash File", "Create `cleanup/trash.txt`.", "touch", "cleanup/trash.txt")
    builder.add("Take Out the Trash", "Delete `cleanup/trash.txt`.", "rm", "cleanup/trash.txt")
    builder.add("Remove Cleanup Zone", "Delete the empty `cleanup` folder.", "rmdir", "cleanup")


def add_unit_6(builder: CourseBuilder) -> None:
    builder.use_unit("6")
    builder.add("Make a Zoo", "Create a folder named `zoo`.", "mkdir", "zoo")
    builder.add("Bird House", "Create a folder named `zoo/birds`.", "mkdir", "zoo/birds")
    builder.add("Lion Card", "Create a file named `zoo/lion.txt`.", "touch", "zoo/lion.txt")
    builder.add("Owl Card", "Create a file named `zoo/birds/owl.txt`.", "touch", "zoo/birds/owl.txt")
    builder.add("Owl Sound", "Write `hoo hoo` into `zoo/birds/owl.txt`.", "write", "zoo/birds/owl.txt", "hoo hoo")
    builder.add("Track the Owl", "Search for `owl.txt`.", "find", "owl.txt")
    builder.add("Read the Owl Card", "Read `zoo/birds/owl.txt`.", "cat", "zoo/birds/owl.txt")
    builder.add("Look in the Zoo", "List the contents of `zoo`.", "ls", "zoo")
    builder.add("Look in Birds", "List the contents of `zoo/birds`.", "ls", "zoo/birds")
    builder.add("Make an Owl Copy", "Copy `zoo/birds/owl.txt` to `zoo/owl-copy.txt`.", "cp", "zoo/birds/owl.txt", "zoo/owl-copy.txt")
    builder.add("Find the Copy", "Search for `owl-copy.txt`.", "find", "owl-copy.txt")
    builder.add("Move the Copy Home", "Move `zoo/owl-copy.txt` into `zoo/birds/owl-copy.txt`.", "mv", "zoo/owl-copy.txt", "zoo/birds/owl-copy.txt")
    builder.add("Zoo Tree", "Show the tree for `zoo`.", "tree", "zoo")
    builder.add("Enter Birds", "Move into `zoo/birds`.", "cd", "zoo/birds")
    builder.add("Bird House Path", "Ask the shell where you are inside the zoo.", "pwd")


def add_unit_7(builder: CourseBuilder) -> None:
    builder.use_unit("7")
    builder.add("Back to Home Base", "Move to `/home` to start a project.", "cd", "/home")
    builder.add("Make a Project", "Create a folder named `project`.", "mkdir", "project")
    builder.add("Art Folder", "Create the folder `project/art`.", "mkdir", "project/art")
    builder.add("Code Folder", "Create the folder `project/code`.", "mkdir", "project/code")
    builder.add("Readme File", "Create `project/README.txt`.", "touch", "project/README.txt")
    builder.add("Project Title", "Write `Toy Robot Project` into `project/README.txt`.", "write", "project/README.txt", "Toy Robot Project")
    builder.add("Color Notes File", "Create `project/art/colors.txt`.", "touch", "project/art/colors.txt")
    builder.add("First Color", "Write `red` into `project/art/colors.txt`.", "write", "project/art/colors.txt", "red")
    builder.add("Second Color", "Append `blue` to `project/art/colors.txt`.", "append", "project/art/colors.txt", "blue")
    builder.add("Plan File", "Create `project/code/plan.txt`.", "touch", "project/code/plan.txt")
    builder.add("Write the Plan", "Write `make robot move` into `project/code/plan.txt`.", "write", "project/code/plan.txt", "make robot move")
    builder.add("Project Tree", "Show the tree for `project`.", "tree", "project")
    builder.add("Backup the Plan", "Copy `project/code/plan.txt` to `project/code/plan-copy.txt`.", "cp", "project/code/plan.txt", "project/code/plan-copy.txt")
    builder.add("Move Final Plan", "Move `project/code/plan-copy.txt` to `project/plan-final.txt`.", "mv", "project/code/plan-copy.txt", "project/plan-final.txt")
    builder.add("Find the Final Plan", "Search for `plan-final.txt`.", "find", "plan-final.txt")


def add_unit_8(builder: CourseBuilder) -> None:
    builder.use_unit("8")
    builder.add("Enter Code Folder", "Move into `/home/project/code`.", "cd", "/home/project/code")
    builder.add("Hello Program File", "Create a file named `hello.py`.", "touch", "hello.py")
    builder.add("Write First Code", "Write `print('Hello, explorer!')` into `hello.py`.", "write", "hello.py", "print('Hello, explorer!')")
    builder.add("Read the Code", "Read `hello.py`.", "cat", "hello.py")
    builder.add("Run Hello", "Run the Python file `hello.py`.", "python", "hello.py")
    builder.add("Robot Program File", "Create a file named `robot.py`.", "touch", "robot.py")
    builder.add("Robot Name Line", "Write `name = 'Bolt'` into `robot.py`.", "write", "robot.py", "name = 'Bolt'")
    builder.add("Robot Print Line", "Append `print(name)` to `robot.py`.", "append", "robot.py", "print(name)")
    builder.add("Read Robot Code", "Read `robot.py`.", "cat", "robot.py")
    builder.add("Run Robot Code", "Run `robot.py`.", "python", "robot.py")
    builder.add("Cheer Program File", "Create a file named `cheer.py`.", "touch", "cheer.py")
    builder.add("First Cheer Line", "Write `print('You can do it!')` into `cheer.py`.", "write", "cheer.py", "print('You can do it!')")
    builder.add("Second Cheer Line", "Append `print('Keep going!')` to `cheer.py`.", "append", "cheer.py", "print('Keep going!')")
    builder.add("Run Cheer Code", "Run `cheer.py`.", "python", "cheer.py")
    builder.add("See Your Code Files", "List the files in this code folder.", "ls")


def add_unit_9(builder: CourseBuilder) -> None:
    builder.use_unit("9")
    builder.add("Math Program File", "Create `math_fun.py`.", "touch", "math_fun.py")
    builder.add("Math Line One", "Write `apples = 2 + 3` into `math_fun.py`.", "write", "math_fun.py", "apples = 2 + 3")
    builder.add("Math Line Two", "Append `print(apples)` to `math_fun.py`.", "append", "math_fun.py", "print(apples)")
    builder.add("Run Math Fun", "Run `math_fun.py`.", "python", "math_fun.py")
    builder.add("Counter Program File", "Create `count.py`.", "touch", "count.py")
    builder.add("Loop Line One", "Write `for number in range(3):` into `count.py`.", "write", "count.py", "for number in range(3):")
    builder.add("Loop Line Two", "Append `    print(number)` to `count.py`.", "append", "count.py", "    print(number)")
    builder.add("Run Counter", "Run `count.py`.", "python", "count.py")
    builder.add("Joke Program File", "Create `joke.py`.", "touch", "joke.py")
    builder.add("Joke Line One", "Write `animal = 'cat'` into `joke.py`.", "write", "joke.py", "animal = 'cat'")
    builder.add("Joke Line Two", "Append `print('Funny ' + animal)` to `joke.py`.", "append", "joke.py", "print('Funny ' + animal)")
    builder.add("Run the Joke", "Run `joke.py`.", "python", "joke.py")
    builder.add("Stars Program File", "Create `stars.py`.", "touch", "stars.py")
    builder.add("Star Line", "Write `print('*' * 5)` into `stars.py`.", "write", "stars.py", "print('*' * 5)")
    builder.add("Run Stars", "Run `stars.py`.", "python", "stars.py")


def add_unit_10(builder: CourseBuilder) -> None:
    builder.use_unit("10")
    builder.add("Adventure Program File", "Create `adventure.py`.", "touch", "adventure.py")
    builder.add("Adventure Score", "Write `score = 3` into `adventure.py`.", "write", "adventure.py", "score = 3")
    builder.add("Adventure If Line", "Append `if score > 1:` to `adventure.py`.", "append", "adventure.py", "if score > 1:")
    builder.add("Adventure Print Line", "Append `    print('Level up!')` to `adventure.py`.", "append", "adventure.py", "    print('Level up!')")
    builder.add("Run Adventure", "Run `adventure.py`.", "python", "adventure.py")
    builder.add("Dance Program File", "Create `dance.py`.", "touch", "dance.py")
    builder.add("Dance Steps List", "Write `steps = ['hop', 'spin', 'clap']` into `dance.py`.", "write", "dance.py", "steps = ['hop', 'spin', 'clap']")
    builder.add("Dance Loop", "Append `for step in steps:` to `dance.py`.", "append", "dance.py", "for step in steps:")
    builder.add("Dance Print", "Append `    print(step)` to `dance.py`.", "append", "dance.py", "    print(step)")
    builder.add("Run Dance", "Run `dance.py`.", "python", "dance.py")
    builder.add("Finale Program File", "Create `finale.py`.", "touch", "finale.py")
    builder.add("Finale Line One", "Write `print('Mission complete!')` into `finale.py`.", "write", "finale.py", "print('Mission complete!')")
    builder.add("Finale Line Two", "Append `print('You are a code hero!')` to `finale.py`.", "append", "finale.py", "print('You are a code hero!')")
    builder.add("Run the Finale", "Run `finale.py`.", "python", "finale.py")
    builder.add("Project Map Check", "Show the tree for `/home/project`.", "tree", "/home/project")
