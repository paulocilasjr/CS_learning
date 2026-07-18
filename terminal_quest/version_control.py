from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from terminal_quest.filesystem import FileSystemError, VirtualFileSystem


Snapshot = dict[str, Any]


@dataclass(frozen=True)
class Commit:
    commit_id: str
    message: str
    snapshot: Snapshot


class VirtualRepository:
    """A deliberately small, deterministic Git model for teaching concepts safely."""

    def __init__(self, filesystem: VirtualFileSystem) -> None:
        self.fs = filesystem
        self.commits: list[Commit] = []
        self.branches: dict[str, int] = {}
        self.current_branch = "main"
        self.staged: Snapshot | None = None
        self.reset()

    def reset(self) -> None:
        initial = self.fs.snapshot()
        self.commits = [Commit("0000", "Initial Rebel snapshot", initial)]
        self.branches = {"main": 0}
        self.current_branch = "main"
        self.staged = None

    def status(self) -> str:
        head = self._tracked(self._head.snapshot)
        working = self._tracked(self.fs.snapshot())
        lines = [f"On branch {self.current_branch}"]
        if self.staged is not None and self._tracked(self.staged) != head:
            lines.append("Changes staged for commit.")
        if working != (self._tracked(self.staged) if self.staged is not None else head):
            lines.append("Changes not staged.")
        if len(lines) == 1:
            lines.append("Working tree clean.")
        return "\n".join(lines)

    def diff(self) -> str:
        before = dict(self._head.snapshot["files"])
        after = dict(self.fs.snapshot()["files"])
        lines: list[str] = []
        for path in sorted(before.keys() | after.keys()):
            if path not in before:
                lines.extend((f"+++ {path}", f"+{after[path]}"))
            elif path not in after:
                lines.extend((f"--- {path}", f"-{before[path]}"))
            elif before[path] != after[path]:
                lines.extend((f"--- {path}", f"+++ {path}"))
                lines.extend(f"-{line}" for line in str(before[path]).splitlines())
                lines.extend(f"+{line}" for line in str(after[path]).splitlines())
        return "\n".join(lines) if lines else "No unstaged changes."

    def add_all(self) -> str:
        self.staged = self.fs.snapshot()
        return "Staged all changes."

    def commit(self, message: str) -> str:
        if self.staged is None or self._tracked(self.staged) == self._tracked(self._head.snapshot):
            raise FileSystemError("There are no staged changes to commit.")
        commit = Commit(f"{len(self.commits):04x}", message, self.staged)
        self.commits.append(commit)
        self.branches[self.current_branch] = len(self.commits) - 1
        self.staged = None
        return f"Committed {commit.commit_id}: {message}"

    def log(self) -> str:
        index = self.branches[self.current_branch]
        visible = self.commits[: index + 1]
        return "\n".join(f"commit {commit.commit_id}  {commit.message}" for commit in reversed(visible))

    def branch(self, name: str | None = None) -> str:
        if name is None:
            return "\n".join(
                f"{'*' if branch == self.current_branch else ' '} {branch}"
                for branch in sorted(self.branches)
            )
        if name in self.branches:
            raise FileSystemError(f"Branch `{name}` already exists.")
        self.branches[name] = self.branches[self.current_branch]
        return f"Created branch {name}."

    def switch(self, name: str) -> str:
        if name not in self.branches:
            raise FileSystemError(f"Unknown branch: {name}")
        if self._tracked(self.fs.snapshot()) != self._tracked(self._head.snapshot):
            raise FileSystemError("Commit or discard working changes before switching branches.")
        self.current_branch = name
        self._load(self._head.snapshot)
        self.staged = None
        return f"Switched to branch {name}."

    def merge(self, name: str) -> str:
        if name not in self.branches:
            raise FileSystemError(f"Unknown branch: {name}")
        if name == self.current_branch:
            raise FileSystemError("A branch cannot merge into itself.")
        if self._tracked(self.fs.snapshot()) != self._tracked(self._head.snapshot):
            raise FileSystemError("Commit working changes before merging.")

        source = self.commits[self.branches[name]].snapshot
        self._load(source)
        merge_commit = Commit(
            f"{len(self.commits):04x}",
            f"Merge branch {name}",
            self.fs.snapshot(),
        )
        self.commits.append(merge_commit)
        self.branches[self.current_branch] = len(self.commits) - 1
        self.staged = None
        return f"Merged {name} into {self.current_branch}."

    @property
    def _head(self) -> Commit:
        return self.commits[self.branches[self.current_branch]]

    def _load(self, snapshot: Snapshot) -> None:
        self.fs.load_snapshot(
            cwd=str(snapshot["cwd"]),
            dirs=list(snapshot["dirs"]),
            files=dict(snapshot["files"]),
        )

    @staticmethod
    def _tracked(snapshot: Snapshot) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
        return tuple(snapshot["dirs"]), tuple(sorted(dict(snapshot["files"]).items()))
