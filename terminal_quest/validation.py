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
    planned_commands: tuple[str, ...] = (),
    plan_initial_snapshot: dict[str, object] | None = None,
) -> bool:
    if outcome.requires_plan and not plan_used:
        return False

    commands_to_check = list(planned_commands) if outcome.requires_plan else command_history
    if any(command not in commands_to_check for command in outcome.required_commands):
        return False

    if outcome.requires_plan and not _plan_changed_relevant_state(
        outcome,
        plan_initial_snapshot,
    ):
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

    return True


def _plan_changed_relevant_state(
    outcome: Outcome,
    initial_snapshot: dict[str, object] | None,
) -> bool:
    """Prove that a state-based outcome was not already complete before the plan."""

    has_state_requirement = bool(
        outcome.cwd is not None
        or outcome.files_present
        or outcome.files_absent
        or outcome.file_contents
    )
    if not has_state_requirement:
        return True
    if initial_snapshot is None:
        return False

    initial = VirtualFileSystem()
    initial.load_snapshot(
        cwd=str(initial_snapshot["cwd"]),
        dirs=list(initial_snapshot["dirs"]),
        files=dict(initial_snapshot["files"]),
    )

    if outcome.cwd is not None and initial.pwd() != outcome.cwd:
        return True

    for path in outcome.files_present:
        try:
            initial.resolve(path)
        except FileSystemError:
            return True

    for path in outcome.files_absent:
        try:
            initial.resolve(path)
        except FileSystemError:
            pass
        else:
            return True

    for path, expected in outcome.file_contents.items():
        try:
            actual = initial.read_file(path)
        except FileSystemError:
            return True
        if actual != expected:
            return True

    return False
