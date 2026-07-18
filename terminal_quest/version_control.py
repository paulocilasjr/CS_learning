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
    parents: tuple[int, ...] = ()


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
        commit = Commit(
            f"{len(self.commits):04x}",
            message,
            self.staged,
            parents=(self.branches[self.current_branch],),
        )
        self.commits.append(commit)
        self.branches[self.current_branch] = len(self.commits) - 1
        self.staged = None
        return f"Committed {commit.commit_id}: {message}"

    def log(self) -> str:
        reachable = self._ancestor_distances(self.branches[self.current_branch])
        return "\n".join(
            f"commit {self.commits[index].commit_id}  {self.commits[index].message}"
            for index in sorted(reachable, reverse=True)
        )

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

        target_index = self.branches[self.current_branch]
        source_index = self.branches[name]
        base_index = self._merge_base(target_index, source_index)
        merged = self._merge_snapshots(
            self.commits[base_index].snapshot,
            self.commits[target_index].snapshot,
            self.commits[source_index].snapshot,
        )
        self._load(merged)
        merge_commit = Commit(
            f"{len(self.commits):04x}",
            f"Merge branch {name}",
            self.fs.snapshot(),
            parents=(target_index, source_index),
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

    def _ancestor_distances(self, start: int) -> dict[int, int]:
        distances = {start: 0}
        pending = [start]
        while pending:
            index = pending.pop(0)
            next_distance = distances[index] + 1
            for parent in self.commits[index].parents:
                if parent not in distances or next_distance < distances[parent]:
                    distances[parent] = next_distance
                    pending.append(parent)
        return distances

    def _merge_base(self, target: int, source: int) -> int:
        target_distances = self._ancestor_distances(target)
        source_distances = self._ancestor_distances(source)
        common = target_distances.keys() & source_distances.keys()
        if not common:  # pragma: no cover - every repository starts from commit zero
            raise FileSystemError("The branches do not share a common history.")
        return min(
            common,
            key=lambda index: (
                target_distances[index] + source_distances[index],
                max(target_distances[index], source_distances[index]),
                -index,
            ),
        )

    def _merge_snapshots(self, base: Snapshot, target: Snapshot, source: Snapshot) -> Snapshot:
        missing = object()
        base_files = dict(base["files"])
        target_files = dict(target["files"])
        source_files = dict(source["files"])
        merged_files: dict[str, str] = {}

        for path in sorted(base_files.keys() | target_files.keys() | source_files.keys()):
            value = self._merge_value(
                base_files.get(path, missing),
                target_files.get(path, missing),
                source_files.get(path, missing),
                path,
            )
            if value is not missing:
                merged_files[path] = str(value)

        base_dirs = set(base["dirs"])
        target_dirs = set(target["dirs"])
        source_dirs = set(source["dirs"])
        merged_dirs: set[str] = set()
        for path in sorted(base_dirs | target_dirs | source_dirs):
            present = self._merge_value(
                path in base_dirs,
                path in target_dirs,
                path in source_dirs,
                path,
            )
            if present:
                merged_dirs.add(path)

        for path in (*merged_dirs, *merged_files):
            merged_dirs.update(self._parent_directories(path))

        collisions = merged_dirs & merged_files.keys()
        if collisions:
            path = sorted(collisions)[0]
            raise FileSystemError(f"Merge conflict at `{path}`: file and folder changes overlap.")

        target_cwd = str(target["cwd"])
        merged_cwd = target_cwd if target_cwd == "/" or target_cwd in merged_dirs else "/"
        return {
            "cwd": merged_cwd,
            "dirs": sorted(merged_dirs, key=lambda path: (path.count("/"), path)),
            "files": merged_files,
        }

    @staticmethod
    def _merge_value(base: Any, target: Any, source: Any, path: str) -> Any:
        if target == source:
            return target
        if target == base:
            return source
        if source == base:
            return target
        raise FileSystemError(f"Merge conflict at `{path}`: both branches changed it.")

    @staticmethod
    def _parent_directories(path: str) -> set[str]:
        parents: set[str] = set()
        current = path.rsplit("/", 1)[0]
        while current and current != "/":
            parents.add(current)
            current = current.rsplit("/", 1)[0]
        return parents

    @staticmethod
    def _tracked(snapshot: Snapshot) -> tuple[tuple[str, ...], tuple[tuple[str, str], ...]]:
        return tuple(snapshot["dirs"]), tuple(sorted(dict(snapshot["files"]).items()))
