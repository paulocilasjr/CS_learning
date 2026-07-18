from __future__ import annotations

import ast
import io
import os
import sys
import textwrap
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from terminal_quest.command_engine import (
    CommandDefinition,
    CommandExecutor,
    CommandParser,
    CommandRegistry,
)
from terminal_quest.filesystem import FileSystemError, VirtualFileSystem
from terminal_quest.learning import ReviewEngine
from terminal_quest.persistence import ProgressStore
from terminal_quest.state import LearningState, StoryState
from terminal_quest.tasks import CHAPTERS, Task, build_tasks
from terminal_quest.validation import outcome_is_satisfied
from terminal_quest.version_control import VirtualRepository


SAVE_FILE = Path(".star_wars_terminal_quest_progress.json")

COMMAND_OUTPUT_COLOR = "\033[36m"
COMMAND_ERROR_COLOR = "\033[31m"
ANSI_RESET = "\033[0m"


@dataclass
class CommandResult:
    raw: str
    name: str
    args: list[str]
    output: str = ""
    error: str = ""
    executed_commands: tuple[str, ...] = ()


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


def normalize_args(command: str, args: list[str]) -> list[str]:
    if command in {"help", "pwd"}:
        return args

    if command == "ls":
        flags = sorted({arg for arg in args if arg.startswith("-")})
        paths = [_normalize_path(arg) for arg in args if not arg.startswith("-")]
        return flags + paths

    if command in {"tree", "cd", "mkdir", "touch", "cat", "rm", "rmdir", "find", "python"}:
        return [_normalize_path(arg) for arg in args]

    if command in {"write", "append"}:
        return [_normalize_path(args[0]), args[1]]

    if command in {"cp", "mv"}:
        return [_normalize_path(args[0]), _normalize_path(args[1])]

    return args


def run_python_program(code: str) -> str:
    safe_builtins = {
        "print": print,
        "range": range,
        "len": len,
        "str": str,
        "int": int,
        "float": float,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "bool": bool,
        "sorted": sorted,
        "sum": sum,
        "min": min,
        "max": max,
        "enumerate": enumerate,
    }
    globals_dict = {"__builtins__": safe_builtins}
    buffer = io.StringIO()

    try:
        tree = ast.parse(code, mode="exec")
        banned_nodes = (
            ast.Import,
            ast.ImportFrom,
            ast.Attribute,
            ast.ClassDef,
            ast.Lambda,
            ast.With,
            ast.AsyncWith,
            ast.Try,
            ast.Global,
            ast.Nonlocal,
            ast.Delete,
            ast.Raise,
            ast.Await,
            ast.Yield,
            ast.YieldFrom,
        )
        for node in ast.walk(tree):
            if isinstance(node, banned_nodes):
                raise FileSystemError(
                    f"Python safety system: `{node.__class__.__name__}` is not available in training programs."
                )
            if isinstance(node, ast.Name) and node.id.startswith("_"):
                raise FileSystemError("Python safety system: private names are not available.")
            if isinstance(node, ast.Call) and not isinstance(node.func, ast.Name):
                raise FileSystemError("Python safety system: call a named training function directly.")
        with redirect_stdout(buffer):
            exec(compile(tree, "<training-program>", "exec"), globals_dict, globals_dict)
    except SyntaxError as exc:
        raise FileSystemError(f"Python says: SyntaxError on line {exc.lineno}: {exc.msg}") from exc
    except FileSystemError:
        raise
    except Exception as exc:
        raise FileSystemError(f"Python says: {exc.__class__.__name__}: {exc}") from exc

    output = buffer.getvalue().rstrip("\n")
    return output if output else "(program finished with no printed output)"


class TutorialShell:
    def __init__(self, filesystem: VirtualFileSystem) -> None:
        self.fs = filesystem
        self._input_text: str | None = None
        self.repository = VirtualRepository(filesystem)
        handlers = {
            "help": self._help,
            "pwd": self._pwd,
            "ls": self._ls,
            "mkdir": self._mkdir,
            "cd": self._cd,
            "touch": self._touch,
            "cat": self._cat,
            "echo": self._echo,
            "clear": self._clear,
            "write": self._write,
            "append": self._append,
            "edit": self._edit,
            "cp": self._cp,
            "mv": self._mv,
            "rm": self._rm,
            "rmdir": self._rmdir,
            "tree": self._tree,
            "find": self._find,
            "grep": self._grep,
            "head": self._head,
            "tail": self._tail,
            "wc": self._wc,
            "sort": self._sort,
            "python": self._python,
            "test": self._test,
            "git": self._git,
        }
        help_topics: dict[str, tuple[str, str]] = {
            "help": ("help [command]", "Show the full command list or explain one command."),
            "pwd": ("pwd", "Show the path of your current folder."),
            "ls": ("ls [-a] [path]", "List files and folders. Use -a to show hidden files."),
            "mkdir": ("mkdir path", "Create a new folder."),
            "cd": ("cd path", "Move into a folder."),
            "touch": ("touch path", "Create a new empty file."),
            "cat": ("cat path", "Read a file."),
            "echo": ('echo "text"', "Print text so it can be read, piped, or redirected."),
            "clear": ("clear", "Clear old terminal output."),
            "write": ('write path "text"', "Replace a file's contents with one line of text."),
            "append": ('append path "text"', "Add one new line to the end of a file."),
            "edit": ('edit path line "text"', "Replace one numbered line in a text or code file."),
            "cp": ("cp source destination", "Copy a file or folder."),
            "mv": ("mv source destination", "Move or rename a file or folder."),
            "rm": ("rm path", "Remove a file."),
            "rmdir": ("rmdir path", "Remove an empty folder."),
            "tree": ("tree [path]", "Show a folder and everything inside it."),
            "find": ("find name", "Search for a file or folder by name."),
            "grep": ('grep "pattern" [path]', "Show lines that contain a text pattern."),
            "head": ("head [-n count] [path]", "Show the first lines of data."),
            "tail": ("tail [-n count] [path]", "Show the last lines of data."),
            "wc": ("wc [-l|-w|-c] [path]", "Count lines, words, or characters."),
            "sort": ("sort [path]", "Sort lines of data."),
            "python": ("python file.py", "Run a Python file and show what it prints."),
            "test": ("test file.py", "Run a Python file as a Rebel simulation test."),
            "git": ("git command [arguments]", "Inspect and manage simulated project history."),
        }
        self.registry = CommandRegistry()
        for name, handler in handlers.items():
            usage, description = help_topics[name]
            self.registry.register(CommandDefinition(name, usage, description, handler))
        self.parser = CommandParser()
        self.executor = CommandExecutor(self.registry)

    def execute(self, raw: str) -> CommandResult:
        try:
            parts = self.parser.parse(raw)
        except FileSystemError as exc:
            return CommandResult(raw=raw, name="", args=[], error=str(exc))

        if not parts:
            return CommandResult(raw=raw, name="", args=[], error="Please type a command.")

        first_operator = next((index for index, token in enumerate(parts) if token in {"|", ">", ">>", "&&"}), len(parts))
        first_command = parts[:first_operator]
        name = first_command[0].lower()
        args = first_command[1:]

        try:
            output, executed = self._execute_tokens(parts)
            return CommandResult(
                raw=raw,
                name=name,
                args=args,
                output=output,
                executed_commands=tuple(executed),
            )
        except FileSystemError as exc:
            return CommandResult(raw=raw, name=name, args=args, error=str(exc))
        except Exception as exc:  # pragma: no cover
            return CommandResult(raw=raw, name=name, args=args, error=f"Unexpected problem: {exc}")

    def _execute_tokens(self, tokens: list[str]) -> tuple[str, list[str]]:
        chains = self._split_on(tokens, "&&")
        output = ""
        executed: list[str] = []
        for chain in chains:
            output, names = self._execute_pipeline(chain)
            executed.extend(names)
        return output, executed

    def _execute_pipeline(self, tokens: list[str]) -> tuple[str, list[str]]:
        redirect_mode: str | None = None
        redirect_path: str | None = None
        for operator in (">>", ">"):
            if operator in tokens:
                index = tokens.index(operator)
                if index != len(tokens) - 2:
                    raise FileSystemError(f"`{operator}` needs exactly one destination file at the end.")
                redirect_mode = operator
                redirect_path = tokens[index + 1]
                tokens = tokens[:index]
                break

        commands = self._split_on(tokens, "|")
        input_text: str | None = None
        executed: list[str] = []
        for pieces in commands:
            if not pieces:
                raise FileSystemError("A pipe needs a command on both sides.")
            name = pieces[0].lower()
            args = self._expand_wildcards(name, pieces[1:])
            self._input_text = input_text
            input_text = self._dispatch(name, args)
            executed.append(name)
        self._input_text = None

        output = input_text or ""
        if redirect_path is not None:
            if redirect_mode == ">>":
                self.fs.append_file(redirect_path, output)
            else:
                self.fs.write_file(redirect_path, output)
            return f"Saved output to {redirect_path}", executed
        return output, executed

    def _split_on(self, tokens: list[str], operator: str) -> list[list[str]]:
        groups: list[list[str]] = [[]]
        for token in tokens:
            if token == operator:
                if not groups[-1]:
                    raise FileSystemError(f"`{operator}` needs an operation on both sides.")
                groups.append([])
            else:
                groups[-1].append(token)
        if not groups[-1]:
            raise FileSystemError(f"`{operator}` needs an operation on both sides.")
        return groups

    def _expand_wildcards(self, command: str, args: list[str]) -> list[str]:
        if command not in {"echo", "cat", "rm"}:
            return args
        expanded: list[str] = []
        for arg in args:
            if "*" in arg or "?" in arg:
                matches = self.fs.glob(arg)
                expanded.extend(matches or [arg])
            else:
                expanded.append(arg)
        return expanded

    def _dispatch(self, name: str, args: list[str]) -> str:
        return self.executor.execute(name, args)

    def _help(self, args: list[str]) -> str:
        if not args:
            lines = ["Command list:"]
            for definition in self.registry.definitions():
                lines.append(f"  {definition.usage:<28} {definition.description}")
            lines.extend(
                [
                    "",
                    "Game helpers:",
                    "  hint      show a clue for the current mission",
                    "  repeat    show the mission text again",
                    "  progress  show stars and mission progress",
                    "  skills    show skill mastery and the review queue",
                    "  reset     reset the current mission room",
                    "  exit      save and leave the game",
                ]
            )
            return "\n".join(lines)

        topic = args[0].lower()
        definition = self.registry.get(topic)
        if definition is None:
            raise FileSystemError(f"No help topic named `{topic}`.")
        return f"{definition.usage}\n{definition.description}"

    def _pwd(self, args: list[str]) -> str:
        self._expect_arg_count("pwd", args, 0)
        return self.fs.pwd()

    def _ls(self, args: list[str]) -> str:
        show_hidden = False
        path: str | None = None

        for arg in args:
            if arg == "-a":
                show_hidden = True
                continue
            if arg.startswith("-"):
                raise FileSystemError(f"Unknown option for `ls`: {arg}")
            if path is not None:
                raise FileSystemError("`ls` needs at most one path.")
            path = arg

        items = self.fs.ls(path, show_hidden=show_hidden)
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
        self._expect_arg_count("cat", args, (1, 100))
        contents = [self.fs.read_file(path) for path in args]
        output = "\n".join(contents)
        return output if output else "(empty file)"

    def _echo(self, args: list[str]) -> str:
        return " ".join(args)

    def _clear(self, args: list[str]) -> str:
        self._expect_arg_count("clear", args, 0)
        return "Terminal display cleared."

    def _write(self, args: list[str]) -> str:
        self._expect_arg_count("write", args, 2)
        self.fs.write_file(args[0], self._decode_text(args[1]))
        return f"Wrote to {args[0]}"

    def _append(self, args: list[str]) -> str:
        self._expect_arg_count("append", args, 2)
        self.fs.append_file(args[0], self._decode_text(args[1]))
        return f"Added a line to {args[0]}"

    def _edit(self, args: list[str]) -> str:
        self._expect_arg_count("edit", args, 3)
        try:
            line_number = int(args[1])
        except ValueError as exc:
            raise FileSystemError("`edit` needs a whole-number line.") from exc
        self.fs.replace_line(args[0], line_number, self._decode_text(args[2]))
        return f"Updated line {line_number} of {args[0]}"

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

    def _grep(self, args: list[str]) -> str:
        self._expect_arg_count("grep", args, (1, 2))
        pattern = args[0]
        text = self.fs.read_file(args[1]) if len(args) == 2 else self._require_input("grep")
        matches = [line for line in text.splitlines() if pattern in line]
        return "\n".join(matches) if matches else "(no matches)"

    def _head(self, args: list[str]) -> str:
        count, path = self._parse_line_command("head", args)
        text = self.fs.read_file(path) if path else self._require_input("head")
        return "\n".join(text.splitlines()[:count])

    def _tail(self, args: list[str]) -> str:
        count, path = self._parse_line_command("tail", args)
        text = self.fs.read_file(path) if path else self._require_input("tail")
        return "\n".join(text.splitlines()[-count:])

    def _wc(self, args: list[str]) -> str:
        option: str | None = None
        path: str | None = None
        for arg in args:
            if arg in {"-l", "-w", "-c"}:
                if option is not None:
                    raise FileSystemError("`wc` accepts at most one counting option.")
                option = arg
            elif path is None:
                path = arg
            else:
                raise FileSystemError("`wc` needs at most one file.")
        text = self.fs.read_file(path) if path else self._require_input("wc")
        lines = len(text.splitlines())
        words = len(text.split())
        characters = len(text)
        if option == "-l":
            return str(lines)
        if option == "-w":
            return str(words)
        if option == "-c":
            return str(characters)
        return f"{lines} {words} {characters}"

    def _sort(self, args: list[str]) -> str:
        self._expect_arg_count("sort", args, (0, 1))
        text = self.fs.read_file(args[0]) if args else self._require_input("sort")
        return "\n".join(sorted(text.splitlines()))

    def _parse_line_command(self, command: str, args: list[str]) -> tuple[int, str | None]:
        count = 10
        path: str | None = None
        index = 0
        while index < len(args):
            if args[index] == "-n":
                if index + 1 >= len(args):
                    raise FileSystemError(f"`{command} -n` needs a number.")
                try:
                    count = int(args[index + 1])
                except ValueError as exc:
                    raise FileSystemError(f"`{command} -n` needs a whole number.") from exc
                index += 2
                continue
            if path is not None:
                raise FileSystemError(f"`{command}` needs at most one file.")
            path = args[index]
            index += 1
        if count < 0:
            raise FileSystemError("Line count cannot be negative.")
        return count, path

    def _require_input(self, command: str) -> str:
        if self._input_text is None:
            raise FileSystemError(f"`{command}` needs a file or piped input.")
        return self._input_text

    def _python(self, args: list[str]) -> str:
        self._expect_arg_count("python", args, 1)
        path = args[0]
        if not path.endswith(".py"):
            raise FileSystemError("Python programs should end with `.py`.")
        code = self.fs.read_file(path)
        return run_python_program(code)

    def _test(self, args: list[str]) -> str:
        self._expect_arg_count("test", args, 1)
        path = args[0]
        if not path.endswith(".py"):
            raise FileSystemError("Simulation tests should be Python `.py` files.")
        run_python_program(self.fs.read_file(path))
        return "All Rebel simulation tests passed."

    def _git(self, args: list[str]) -> str:
        if not args:
            raise FileSystemError("`git` needs a subcommand such as `status` or `diff`.")
        subcommand = args[0].lower()
        rest = args[1:]
        if subcommand == "status":
            self._expect_arg_count("git status", rest, 0)
            return self.repository.status()
        if subcommand == "diff":
            self._expect_arg_count("git diff", rest, 0)
            return self.repository.diff()
        if subcommand == "add":
            if rest != ["."]:
                raise FileSystemError("The training repository currently supports `git add .`.")
            return self.repository.add_all()
        if subcommand == "commit":
            if len(rest) != 2 or rest[0] != "-m":
                raise FileSystemError('Use `git commit -m "message"`.')
            return self.repository.commit(rest[1])
        if subcommand == "log":
            self._expect_arg_count("git log", rest, 0)
            return self.repository.log()
        if subcommand == "branch":
            self._expect_arg_count("git branch", rest, (0, 1))
            return self.repository.branch(rest[0] if rest else None)
        if subcommand == "switch":
            self._expect_arg_count("git switch", rest, 1)
            return self.repository.switch(rest[0])
        if subcommand == "merge":
            self._expect_arg_count("git merge", rest, 1)
            return self.repository.merge(rest[0])
        raise FileSystemError(f"Unknown simulated git subcommand: {subcommand}")

    def reset_environment(self) -> None:
        self.repository.reset()

    @staticmethod
    def _decode_text(text: str) -> str:
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def _expect_arg_count(self, command: str, args: list[str], expected: int | tuple[int, int]) -> None:
        if isinstance(expected, int):
            if len(args) != expected:
                raise FileSystemError(f"`{command}` needs {expected} argument(s).")
            return

        low, high = expected
        if not (low <= len(args) <= high):
            raise FileSystemError(f"`{command}` needs between {low} and {high} argument(s).")


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
        self.learning_state = LearningState()
        self.story_state = StoryState()
        self.progress_store = ProgressStore(SAVE_FILE)
        self.review_engine = ReviewEngine()

    def run(self) -> None:
        self._handle_existing_save()
        self._show_welcome()

        previous_chapter = ""
        while self.current_index < len(self.tasks):
            task = self.tasks[self.current_index]

            if task.chapter_key != previous_chapter:
                self._show_chapter_intro(task)
                previous_chapter = task.chapter_key

            self._run_task(task)

        self._finish_campaign()

    def _run_task(self, task: Task) -> None:
        self._prepare_task(task)
        attempts = 0
        hints_used = 0
        command_history: list[str] = []
        self._show_task(task)

        while True:
            raw = input(self._prompt()).strip()
            if not raw:
                continue

            if raw.lower() == "hint":
                tip = task.tips[min(hints_used, len(task.tips) - 1)]
                hints_used += 1
                print(f"\nHint: {tip}")
                continue

            meta_action = self._handle_meta_command(raw, task, hints_used)
            if meta_action == "continue":
                continue
            if meta_action == "reset":
                self._prepare_task(task)
                continue
            if meta_action == "exit":
                self._exit_game()
                return

            result = self.shell.execute(raw)
            self._show_result(result)
            if not result.error:
                command_history.extend(result.executed_commands or (result.name,))

            if self._is_correct(task, result, command_history):
                self._complete_task(task, attempts, hints_used)
                return

            if task.multi_step:
                if not result.error:
                    print("\nGood step. Inspect the result and continue the mission.")
                    continue
                attempts += 1
                tip = task.tips[min(hints_used, len(task.tips) - 1)]
                hints_used += 1
                print("\nThat step did not work, but your completed mission state is still here.")
                print(f"Tip: {tip}")
                continue

            attempts += 1
            tip = task.tips[min(hints_used, len(task.tips) - 1)]
            hints_used += 1
            print("\nNot quite yet. The practice room is reset so you can try again.")
            print(f"Tip: {tip}")
            self._prepare_task(task)
            command_history.clear()

    def _complete_task(self, task: Task, attempts: int, hints_used: int) -> None:
        earned = 3 if attempts == 0 else 2 if attempts == 1 else 1
        self.stars += earned
        practiced_skills = tuple(dict.fromkeys((*task.new_skills, *task.review_skills)))
        self.learning_state.record_mission(
            mission_number=task.number,
            mission_type=task.mission_type,
            skills=practiced_skills,
            attempts=attempts,
            hints_used=hints_used,
        )
        self.story_state.current_episode = task.chapter_key
        self.story_state.current_mission = task.number + 1
        if task.number not in self.story_state.completed_objectives:
            self.story_state.completed_objectives.append(task.number)
        for flag in task.story_flags:
            self.story_state.story_flags[flag] = True

        print(f"\n{task.success}")
        print(f"Stars earned this mission: {earned}")

        self.current_index += 1
        chapter_finished = (
            self.current_index >= len(self.tasks)
            or self.tasks[self.current_index].chapter_key != task.chapter_key
        )
        chapter_reward = CHAPTERS[task.chapter_key].reward
        if chapter_finished and chapter_reward not in self.story_state.rewards:
            self.story_state.rewards.append(chapter_reward)
        self._save_progress()
        self._show_checkpoint(task)

    def _exit_game(self) -> None:
        self._save_progress()
        if self.save_enabled:
            print("\nProgress saved. See you next time.")
        else:
            print("\nSee you next time.")
        raise SystemExit

    def _finish_campaign(self) -> None:
        self.story_state.story_flags["campaign_complete"] = True
        self.story_state.current_mission = len(self.tasks) + 1
        self._save_progress()

        print(
            "\nYou completed the current Star Wars campaign."
            f"\nTotal stars: {self.stars}"
            "\nLeia has the briefing, the rescue team is set, and the Falcon is ready for the next chapter."
        )

    def _handle_existing_save(self) -> None:
        if not self.save_enabled or self.current_index > 0:
            return

        if self.reset_progress and self.progress_store.exists():
            self.progress_store.clear()
            return

        saved = self.progress_store.load()
        if saved is None:
            return

        saved_index = int(saved.get("current_index", 0))
        saved_stars = int(saved.get("stars", 0))
        saved_learning = LearningState.from_dict(dict(saved.get("learning_state", {})))
        saved_story = StoryState.from_dict(dict(saved.get("story_state", {})))
        if saved_index == len(self.tasks):
            print(
                "A completed campaign record was found."
                "\nType `review` to replay while keeping mastery, or `restart` to clear all progress."
            )
            while True:
                choice = input("> ").strip().lower()
                if choice == "review":
                    self.learning_state = saved_learning
                    self.story_state = saved_story
                    self.current_index = 0
                    self.stars = 0
                    return
                if choice == "restart":
                    self.progress_store.clear()
                    return
                print("Please type `review` or `restart`.")
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
                self.learning_state = saved_learning
                self.story_state = saved_story
                return
            if choice == "restart":
                self.progress_store.clear()
                self.current_index = 0
                self.stars = 0
                return
            print("Please type `resume` or `restart`.")

    def _save_progress(self) -> None:
        if not self.save_enabled:
            return

        self.progress_store.save(
            {
                "version": 2,
                "current_index": self.current_index,
                "stars": self.stars,
                "learning_state": self.learning_state.to_dict(),
                "story_state": self.story_state.to_dict(),
            }
        )

    def _show_welcome(self) -> None:
        message = """
        Welcome to Star Wars Terminal Quest.

        You are the newest Rebel technician at Yavin 4.
        Every mission happens inside a safe practice shell, so nothing touches your real computer files.
        Early missions use one command. Later missions let you build and verify multi-step solutions.

        Helpful game commands:
          hint      show a clue
          repeat    show the mission again
          progress  show stars and mission number
          skills    show your strongest skills and review queue
          reset     reset the current mission room
          exit      save and leave
        """
        print(textwrap.dedent(message).strip())

    def _show_chapter_intro(self, task: Task) -> None:
        chapter = CHAPTERS[task.chapter_key]
        line = "=" * 60
        print(f"\n{line}")
        print(f"Chapter {chapter.key}: {chapter.name}")
        print(textwrap.fill(chapter.intro, width=72))
        print(line)

    def _show_task(self, task: Task) -> None:
        print(f"\nMission {task.number}/{len(self.tasks)}")
        print(task.name)
        print()
        self._show_story_text(task.lesson)
        print()
        self._show_story_text(f"Your task: {task.instruction}")

    def _prepare_task(self, task: Task) -> None:
        self.fs.load_snapshot(
            cwd=task.scenario.cwd,
            dirs=task.scenario.dirs,
            files=task.scenario.files,
        )
        self.shell.reset_environment()

    def _prompt(self) -> str:
        return f"[{self.current_index + 1:03d}] {self.fs.pwd()} $ "

    def _show_story_text(self, text: str) -> None:
        paragraphs = text.split("\n\n")
        for index, paragraph in enumerate(paragraphs):
            print(textwrap.fill(paragraph, width=72))
            if index != len(paragraphs) - 1:
                print()

    def _supports_color(self) -> bool:
        return sys.stdout.isatty() and "NO_COLOR" not in os.environ

    def _paint(self, text: str, color: str) -> str:
        if not self._supports_color():
            return text
        return f"{color}{text}{ANSI_RESET}"

    def _show_command_box(self, title: str, text: str, color: str) -> None:
        lines = text.splitlines() or ["(no output)"]
        print()
        print(self._paint(f"+-- {title} --+", color))
        for line in lines:
            print(self._paint(f"| {line}", color))
        print(self._paint(f"+-- END {title} --+", color))

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

        if command == "skills":
            self._show_skills()
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
        print(f"Skills practiced: {len(self.learning_state.skills)}")

    def _show_skills(self) -> None:
        if not self.learning_state.skills:
            print("\nComplete a mission to begin your skill record.")
            return

        names = ["unseen", "introduced", "guided", "recalled", "transferred", "integrated"]
        print("\nSkill record:")
        for key, progress in sorted(
            self.learning_state.skills.items(),
            key=lambda item: (-item[1].mastery, item[0]),
        ):
            level = names[min(progress.mastery, len(names) - 1)]
            print(f"  {key:<20} {level:<12} attempts: {progress.attempts} hints: {progress.hints_used}")
        if self.learning_state.review_queue:
            print(f"Review queue: {', '.join(self.learning_state.review_queue)}")
        recommendations = self.review_engine.recommend(self.learning_state)
        if recommendations:
            print(f"Recommended next review: {', '.join(recommendations)}")

    def _show_result(self, result: CommandResult) -> None:
        if result.error:
            self._show_command_box("COMMAND ERROR", result.error, COMMAND_ERROR_COLOR)
            return

        if result.output:
            self._show_command_box("COMMAND OUTPUT", result.output, COMMAND_OUTPUT_COLOR)

    def _show_checkpoint(self, completed_task: Task) -> None:
        if self.current_index >= len(self.tasks):
            return

        next_task = self.tasks[self.current_index]
        if next_task.chapter_key == completed_task.chapter_key:
            return

        completed_chapter = CHAPTERS[completed_task.chapter_key]
        print(f"Chapter complete: {completed_chapter.name}")
        print(f"Reward unlocked: {completed_chapter.reward}")
        print(f"Progress so far: {self.current_index}/{len(self.tasks)} missions")

    def _is_correct(self, task: Task, result: CommandResult, command_history: list[str]) -> bool:
        if result.error:
            return False
        if task.outcome is not None:
            return outcome_is_satisfied(
                task.outcome,
                filesystem=self.fs,
                latest_output=result.output,
                command_history=command_history,
            )
        if result.name != task.expected_command:
            return False

        actual = normalize_args(task.expected_command, result.args)
        expected = normalize_args(task.expected_command, task.expected_args)
        return actual == expected


def main() -> None:
    game = TerminalQuestGame()
    try:
        game.run()
    except SystemExit:
        return


if __name__ == "__main__":
    main()
