from __future__ import annotations

import io
import json
import shlex
import textwrap
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from terminal_quest.filesystem import FileSystemError, VirtualFileSystem
from terminal_quest.tasks import Task, UNITS, build_tasks


SAVE_FILE = Path(".terminal_quest_progress.json")


@dataclass
class CommandResult:
    raw: str
    name: str
    args: list[str]
    output: str = ""
    error: str = ""


class TutorialShell:
    def __init__(self, filesystem: VirtualFileSystem) -> None:
        self.fs = filesystem
        self.help_topics: dict[str, tuple[str, str]] = {
            "help": ("help [command]", "Show the full command list or explain one command."),
            "pwd": ("pwd", "Show the path of your current folder."),
            "ls": ("ls [path]", "List files and folders."),
            "mkdir": ("mkdir path", "Create a new folder."),
            "cd": ("cd path", "Move into a folder."),
            "touch": ("touch path", "Create a new empty file."),
            "cat": ("cat path", "Read a file."),
            "write": ('write path "text"', "Replace a file's contents with one line of text."),
            "append": ('append path "text"', "Add one new line to the end of a file."),
            "cp": ("cp source destination", "Copy a file or folder."),
            "mv": ("mv source destination", "Move or rename a file or folder."),
            "rm": ("rm path", "Remove a file."),
            "rmdir": ("rmdir path", "Remove an empty folder."),
            "tree": ("tree [path]", "Show a folder and everything inside it."),
            "find": ("find name", "Search for a file or folder by name."),
            "python": ("python file.py", "Run a Python file and show what it prints."),
        }

    def execute(self, raw: str) -> CommandResult:
        try:
            parts = shlex.split(raw, posix=True)
        except ValueError as exc:
            return CommandResult(raw=raw, name="", args=[], error=f"Parsing error: {exc}")

        if not parts:
            return CommandResult(raw=raw, name="", args=[], error="Please type a command.")

        name = parts[0].lower()
        args = parts[1:]
        try:
            output = self._dispatch(name, args)
            return CommandResult(raw=raw, name=name, args=args, output=output)
        except FileSystemError as exc:
            return CommandResult(raw=raw, name=name, args=args, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return CommandResult(raw=raw, name=name, args=args, error=f"Unexpected problem: {exc}")

    def _dispatch(self, name: str, args: list[str]) -> str:
        commands: dict[str, Callable[[list[str]], str]] = {
            "help": self._help,
            "pwd": self._pwd,
            "ls": self._ls,
            "mkdir": self._mkdir,
            "cd": self._cd,
            "touch": self._touch,
            "cat": self._cat,
            "write": self._write,
            "append": self._append,
            "cp": self._cp,
            "mv": self._mv,
            "rm": self._rm,
            "rmdir": self._rmdir,
            "tree": self._tree,
            "find": self._find,
            "python": self._python,
        }
        handler = commands.get(name)
        if handler is None:
            raise FileSystemError(f"Unknown command: {name}")
        return handler(args)

    def _help(self, args: list[str]) -> str:
        if not args:
            lines = ["Command list:"]
            for name in sorted(self.help_topics):
                usage, description = self.help_topics[name]
                lines.append(f"  {usage:<28} {description}")
            lines.extend(
                [
                    "",
                    "Game helpers:",
                    "  hint      show a clue for the current mission",
                    "  repeat    show the mission text again",
                    "  progress  show stars and mission progress",
                    "  reset     reset the current mission room",
                    "  exit      save and leave the game",
                ]
            )
            return "\n".join(lines)

        topic = args[0].lower()
        info = self.help_topics.get(topic)
        if info is None:
            raise FileSystemError(f"No help topic named `{topic}`.")
        usage, description = info
        return f"{usage}\n{description}"

    def _pwd(self, args: list[str]) -> str:
        self._expect_arg_count("pwd", args, 0)
        return self.fs.pwd()

    def _ls(self, args: list[str]) -> str:
        self._expect_arg_count("ls", args, (0, 1))
        items = self.fs.ls(args[0] if args else None)
        return "\n".join(items) if items else "(empty)"

    def _mkdir(self, args: list[str]) -> str:
        self._expect_arg_count("mkdir", args, 1)
        self.fs.mkdir(args[0])
        return f"Folder created: {args[0]}"

    def _cd(self, args: list[str]) -> str:
        self._expect_arg_count("cd", args, 1)
        self.fs.change_directory(args[0])
        return self.fs.pwd()

    def _touch(self, args: list[str]) -> str:
        self._expect_arg_count("touch", args, 1)
        self.fs.touch(args[0])
        return f"File ready: {args[0]}"

    def _cat(self, args: list[str]) -> str:
        self._expect_arg_count("cat", args, 1)
        content = self.fs.read_file(args[0])
        return content if content else "(empty file)"

    def _write(self, args: list[str]) -> str:
        self._expect_arg_count("write", args, 2)
        self.fs.write_file(args[0], args[1])
        return f"Wrote to {args[0]}"

    def _append(self, args: list[str]) -> str:
        self._expect_arg_count("append", args, 2)
        self.fs.append_file(args[0], args[1])
        return f"Added a line to {args[0]}"

    def _cp(self, args: list[str]) -> str:
        self._expect_arg_count("cp", args, 2)
        self.fs.copy(args[0], args[1])
        return f"Copied {args[0]} to {args[1]}"

    def _mv(self, args: list[str]) -> str:
        self._expect_arg_count("mv", args, 2)
        self.fs.move(args[0], args[1])
        return f"Moved {args[0]} to {args[1]}"

    def _rm(self, args: list[str]) -> str:
        self._expect_arg_count("rm", args, 1)
        self.fs.remove_file(args[0])
        return f"Removed file: {args[0]}"

    def _rmdir(self, args: list[str]) -> str:
        self._expect_arg_count("rmdir", args, 1)
        self.fs.remove_directory(args[0])
        return f"Removed folder: {args[0]}"

    def _tree(self, args: list[str]) -> str:
        self._expect_arg_count("tree", args, (0, 1))
        return "\n".join(self.fs.tree(args[0] if args else None))

    def _find(self, args: list[str]) -> str:
        self._expect_arg_count("find", args, 1)
        matches = self.fs.find(args[0])
        return "\n".join(matches) if matches else "(no matches)"

    def _python(self, args: list[str]) -> str:
        self._expect_arg_count("python", args, 1)
        path = args[0]
        if not path.endswith(".py"):
            raise FileSystemError("Python programs should end with `.py`.")
        code = self.fs.read_file(path)
        return run_python_program(code)

    def _expect_arg_count(self, command: str, args: list[str], expected: int | tuple[int, int]) -> None:
        if isinstance(expected, int):
            if len(args) != expected:
                raise FileSystemError(f"`{command}` needs {expected} argument(s).")
            return
        low, high = expected
        if not (low <= len(args) <= high):
            raise FileSystemError(f"`{command}` needs between {low} and {high} argument(s).")


def run_python_program(code: str) -> str:
    safe_builtins = {
        "print": print,
        "range": range,
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
    }
    globals_dict = {"__builtins__": safe_builtins}
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            exec(code, globals_dict, {})
    except SyntaxError as exc:
        raise FileSystemError(f"Python says: SyntaxError on line {exc.lineno}: {exc.msg}") from exc
    except Exception as exc:
        raise FileSystemError(f"Python says: {exc.__class__.__name__}: {exc}") from exc
    output = buffer.getvalue().rstrip("\n")
    return output if output else "(program finished with no printed output)"


class TerminalQuestGame:
    def __init__(
        self,
        *,
        save_enabled: bool = True,
        start_task: int | None = None,
        reset_progress: bool = False,
    ) -> None:
        self.tasks = build_tasks()
        self.fs = VirtualFileSystem()
        self.shell = TutorialShell(self.fs)
        self.save_enabled = save_enabled
        self.current_index = max(0, (start_task - 1) if start_task else 0)
        self.stars = 0
        self.reset_progress = reset_progress

    def run(self) -> None:
        self._handle_existing_save()
        self._show_welcome()
        previous_unit = ""

        while self.current_index < len(self.tasks):
            task = self.tasks[self.current_index]
            if task.unit_key != previous_unit:
                self._show_unit_intro(task)
                previous_unit = task.unit_key

            self._prepare_task(task)
            attempts = 0
            tip_index = 0
            self._show_task(task)

            while True:
                raw = input(self._prompt()).strip()
                if not raw:
                    continue

                meta_result = self._handle_meta_command(raw, task, tip_index)
                if meta_result == "continue":
                    continue
                if meta_result == "exit":
                    self._save_progress()
                    if self.save_enabled:
                        print("\nProgress saved. See you next time.")
                    else:
                        print("\nSee you next time.")
                    return
                if meta_result == "reset":
                    self._prepare_task(task)
                    continue

                result = self.shell.execute(raw)
                self._show_result(result)

                if self._is_correct(task, result):
                    earned = 3 if attempts == 0 else 2 if attempts == 1 else 1
                    self.stars += earned
                    print(f"\n{task.success}")
                    print(f"Stars earned this mission: {earned}")
                    self.current_index += 1
                    self._save_progress()
                    self._show_checkpoint()
                    break

                attempts += 1
                tip = task.tips[min(tip_index, len(task.tips) - 1)]
                tip_index += 1
                print("\nNot quite yet. The practice room is reset so you can try again.")
                print(f"Tip: {tip}")
                self._prepare_task(task)

        if self.save_enabled and SAVE_FILE.exists():
            SAVE_FILE.unlink()
        print(
            "\nYou finished all 150 missions."
            f"\nTotal stars: {self.stars}"
            "\nYou are now a Terminal Hero."
        )

    def _handle_existing_save(self) -> None:
        if not self.save_enabled or self.current_index > 0:
            return
        if self.reset_progress and SAVE_FILE.exists():
            SAVE_FILE.unlink()
            return
        if not SAVE_FILE.exists():
            return

        try:
            saved = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        saved_index = int(saved.get("current_index", 0))
        saved_stars = int(saved.get("stars", 0))
        if not (0 < saved_index < len(self.tasks)):
            return

        print(
            f"Saved progress found at mission {saved_index + 1} of {len(self.tasks)}."
            "\nType `resume` to continue or `restart` to begin from mission 1."
        )
        while True:
            choice = input("> ").strip().lower()
            if choice == "resume":
                self.current_index = saved_index
                self.stars = saved_stars
                return
            if choice == "restart":
                SAVE_FILE.unlink(missing_ok=True)
                self.current_index = 0
                self.stars = 0
                return
            print("Please type `resume` or `restart`.")

    def _save_progress(self) -> None:
        if not self.save_enabled:
            return
        SAVE_FILE.write_text(
            json.dumps({"current_index": self.current_index, "stars": self.stars}, indent=2),
            encoding="utf-8",
        )

    def _show_welcome(self) -> None:
        message = """
        Welcome to Terminal Quest.

        This game happens inside a safe practice shell. Nothing touches your real computer files.
        Each mission asks for one command. If the command is wrong, you get another chance plus a tip.

        Helpful game commands:
          hint      show a clue
          repeat    show the mission again
          progress  show stars and mission number
          reset     reset the current mission room
          exit      save and leave
        """
        print(textwrap.dedent(message).strip())

    def _show_unit_intro(self, task: Task) -> None:
        unit = UNITS[task.unit_key]
        line = "=" * 60
        print(f"\n{line}")
        print(f"Unit {unit.key}: {unit.name}")
        print(textwrap.fill(unit.intro, width=72))
        print(line)

    def _show_task(self, task: Task) -> None:
        print(
            f"\nMission {task.number}/{len(self.tasks)}"
            f"\n{task.name}"
            f"\nGoal: {task.instruction}"
        )

    def _prepare_task(self, task: Task) -> None:
        self.fs.load_snapshot(
            cwd=task.scenario.cwd,
            dirs=task.scenario.dirs,
            files=task.scenario.files,
        )

    def _prompt(self) -> str:
        return f"[{self.current_index + 1:03d}] {self.fs.pwd()} $ "

    def _handle_meta_command(self, raw: str, task: Task, tip_index: int) -> str | None:
        command = raw.lower()
        if command == "hint":
            tip = task.tips[min(tip_index, len(task.tips) - 1)]
            print(f"\nHint: {tip}")
            return "continue"
        if command == "repeat":
            self._show_task(task)
            return "continue"
        if command == "progress":
            self._show_progress()
            return "continue"
        if command == "reset":
            print("\nMission room reset.")
            return "reset"
        if command == "exit":
            return "exit"
        return None

    def _show_progress(self) -> None:
        done = self.current_index
        total = len(self.tasks)
        blocks = 20
        filled = round((done / total) * blocks)
        bar = "#" * filled + "-" * (blocks - filled)
        print(f"\nProgress: [{bar}] {done}/{total}")
        print(f"Stars: {self.stars}")

    def _show_result(self, result: CommandResult) -> None:
        if result.error:
            print(f"\n{result.error}")
            return
        if result.output:
            print(f"\n{result.output}")

    def _show_checkpoint(self) -> None:
        if self.current_index == 0 or self.current_index % 15 != 0:
            return
        completed_unit = UNITS[str(self.current_index // 15)]
        print(f"Badge unlocked: {completed_unit.badge}")
        print(f"Progress so far: {self.current_index}/{len(self.tasks)} missions")

    def _is_correct(self, task: Task, result: CommandResult) -> bool:
        if result.error or result.name != task.expected_command:
            return False
        return normalize_args(task.expected_command, result.args) == normalize_args(
            task.expected_command, task.expected_args
        )


def normalize_args(command: str, args: list[str]) -> list[str]:
    if command in {"help", "pwd"}:
        return args
    if command in {"ls", "tree", "cd", "mkdir", "touch", "cat", "rm", "rmdir", "find", "python"}:
        return [_normalize_path(arg) for arg in args]
    if command in {"write", "append"}:
        return [_normalize_path(args[0]), args[1]]
    if command in {"cp", "mv"}:
        return [_normalize_path(args[0]), _normalize_path(args[1])]
    return args


def _normalize_path(path: str) -> str:
    cleaned = path.replace("\\", "/")
    if cleaned == "/":
        return "/"
    absolute = cleaned.startswith("/")
    parts: list[str] = []
    for part in cleaned.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts and parts[-1] != "..":
                parts.pop()
            elif not absolute:
                parts.append(part)
            continue
        parts.append(part)
    if absolute:
        return "/" + "/".join(parts)
    return "/".join(parts) or "."
