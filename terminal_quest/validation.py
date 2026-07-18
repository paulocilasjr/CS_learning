from __future__ import annotations

from dataclasses import dataclass, field

from terminal_quest.filesystem import FileSystemError, VirtualFileSystem


@dataclass(frozen=True)
class Outcome:
    """Observable state that can be reached through more than one command sequence."""

    cwd: str | None = None
    files_present: tuple[str, ...] = ()
    files_absent: tuple[str, ...] = ()
    file_contents: dict[str, str] = field(default_factory=dict)
    output_contains: tuple[str, ...] = ()
    required_commands: tuple[str, ...] = ()
    requires_plan: bool = False


def outcome_is_satisfied(
    outcome: Outcome,
    *,
    filesystem: VirtualFileSystem,
    latest_output: str,
    command_history: list[str],
    plan_used: bool = False,
) -> bool:
    if outcome.requires_plan and not plan_used:
        return False

    if outcome.cwd is not None and filesystem.pwd() != outcome.cwd:
        return False

    for path in outcome.files_present:
        try:
            filesystem.resolve(path)
        except FileSystemError:
            return False

    for path in outcome.files_absent:
        try:
            filesystem.resolve(path)
        except FileSystemError:
            pass
        else:
            return False

    for path, expected in outcome.file_contents.items():
        try:
            actual = filesystem.read_file(path)
        except FileSystemError:
            return False
        if actual != expected:
            return False

    if any(fragment not in latest_output for fragment in outcome.output_contains):
        return False

    if any(command not in command_history for command in outcome.required_commands):
        return False

    return True
