from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Union


class FileSystemError(Exception):
    pass


@dataclass
class VirtualFile:
    name: str
    content: str = ""
    parent: "VirtualDirectory | None" = None

    def clone(self, parent: "VirtualDirectory | None" = None) -> "VirtualFile":
        return VirtualFile(name=self.name, content=self.content, parent=parent)


@dataclass
class VirtualDirectory:
    name: str
    parent: "VirtualDirectory | None" = None
    children: Dict[str, "Node"] = field(default_factory=dict)

    def clone(self, parent: "VirtualDirectory | None" = None) -> "VirtualDirectory":
        copied = VirtualDirectory(name=self.name, parent=parent)
        for name in sorted(self.children):
            child = self.children[name]
            child_copy = child.clone(copied)
            copied.children[name] = child_copy
        return copied


Node = Union[VirtualFile, VirtualDirectory]


class VirtualFileSystem:
    def __init__(self) -> None:
        self.root = VirtualDirectory(name="")
        self.cwd = self.root

    def load_snapshot(
        self,
        *,
        cwd: str,
        dirs: list[str],
        files: dict[str, str],
    ) -> None:
        self.root = VirtualDirectory(name="")
        self.cwd = self.root
        for path in sorted(dirs, key=self._path_depth):
            self.mkdir(path)
        for path, content in sorted(files.items()):
            self.write_file(path, content)
        self.cwd = self._expect_directory(self.resolve(cwd))

    def snapshot(self) -> dict[str, object]:
        dirs: list[str] = []
        files: dict[str, str] = {}

        def walk(directory: VirtualDirectory) -> None:
            for name in sorted(directory.children):
                child = directory.children[name]
                child_path = self.path_for(child)
                if isinstance(child, VirtualDirectory):
                    dirs.append(child_path)
                    walk(child)
                else:
                    files[child_path] = child.content

        walk(self.root)
        return {"cwd": self.pwd(), "dirs": dirs, "files": files}

    def pwd(self) -> str:
        return self.path_for(self.cwd)

    def resolve(self, path: str, start: VirtualDirectory | None = None) -> Node:
        if path == "":
            return self.cwd

        current: Node = self.root if path.startswith("/") else (start or self.cwd)
        parts = path.split("/")
        for part in parts:
            if part in ("", "."):
                continue
            if part == "..":
                if isinstance(current, VirtualDirectory) and current.parent is not None:
                    current = current.parent
                continue
            if not isinstance(current, VirtualDirectory):
                raise FileSystemError(f"`{self.path_for(current)}` is not a directory.")
            child = current.children.get(part)
            if child is None:
                raise FileSystemError(f"Path not found: {path}")
            current = child
        return current

    def mkdir(self, path: str) -> None:
        parent, name = self._parent_and_name(path)
        if name in parent.children:
            raise FileSystemError(f"`{name}` already exists.")
        parent.children[name] = VirtualDirectory(name=name, parent=parent)

    def touch(self, path: str) -> None:
        parent, name = self._parent_and_name(path)
        existing = parent.children.get(name)
        if existing is None:
            parent.children[name] = VirtualFile(name=name, content="", parent=parent)
            return
        if isinstance(existing, VirtualDirectory):
            raise FileSystemError(f"`{name}` is a directory, not a file.")

    def read_file(self, path: str) -> str:
        file_node = self._expect_file(self.resolve(path))
        return file_node.content

    def write_file(self, path: str, text: str) -> None:
        parent, name = self._parent_and_name(path)
        existing = parent.children.get(name)
        if existing is None:
            parent.children[name] = VirtualFile(name=name, content=text, parent=parent)
            return
        if isinstance(existing, VirtualDirectory):
            raise FileSystemError(f"`{name}` is a directory, not a file.")
        existing.content = text

    def append_file(self, path: str, text: str) -> None:
        parent, name = self._parent_and_name(path)
        existing = parent.children.get(name)
        if existing is None:
            parent.children[name] = VirtualFile(name=name, content=text, parent=parent)
            return
        if isinstance(existing, VirtualDirectory):
            raise FileSystemError(f"`{name}` is a directory, not a file.")
        if existing.content:
            existing.content = f"{existing.content}\n{text}"
        else:
            existing.content = text

    def ls(self, path: str | None = None) -> list[str]:
        target = self.resolve(path or ".")
        if isinstance(target, VirtualFile):
            return [target.name]
        items = []
        for name in sorted(target.children):
            child = target.children[name]
            suffix = "/" if isinstance(child, VirtualDirectory) else ""
            items.append(f"{name}{suffix}")
        return items

    def change_directory(self, path: str) -> None:
        self.cwd = self._expect_directory(self.resolve(path))

    def remove_file(self, path: str) -> None:
        file_node = self._expect_file(self.resolve(path))
        if file_node.parent is None:
            raise FileSystemError("You cannot remove the root folder.")
        del file_node.parent.children[file_node.name]

    def remove_directory(self, path: str) -> None:
        directory = self._expect_directory(self.resolve(path))
        if directory.parent is None:
            raise FileSystemError("You cannot remove the root folder.")
        if directory.children:
            raise FileSystemError("That folder is not empty yet.")
        del directory.parent.children[directory.name]

    def copy(self, source: str, destination: str) -> None:
        source_node = self.resolve(source)
        destination_exists = self._try_resolve(destination)
        if destination_exists is not None:
            destination_dir = self._expect_directory(destination_exists)
            new_name = source_node.name
            if new_name in destination_dir.children:
                raise FileSystemError(f"`{new_name}` already exists in `{self.path_for(destination_dir)}`.")
            destination_dir.children[new_name] = source_node.clone(destination_dir)
            return

        parent, new_name = self._parent_and_name(destination)
        if new_name in parent.children:
            raise FileSystemError(f"`{new_name}` already exists.")
        clone = source_node.clone(parent)
        clone.name = new_name
        parent.children[new_name] = clone

    def move(self, source: str, destination: str) -> None:
        source_node = self.resolve(source)
        if source_node is self.root:
            raise FileSystemError("You cannot move the root folder.")
        assert source_node.parent is not None

        destination_exists = self._try_resolve(destination)
        if destination_exists is not None:
            destination_dir = self._expect_directory(destination_exists)
            if isinstance(source_node, VirtualDirectory) and self._is_inside(destination_dir, source_node):
                raise FileSystemError("You cannot move a folder into itself.")
            if source_node.name in destination_dir.children:
                raise FileSystemError(f"`{source_node.name}` already exists there.")
            del source_node.parent.children[source_node.name]
            source_node.parent = destination_dir
            destination_dir.children[source_node.name] = source_node
            return

        parent, new_name = self._parent_and_name(destination)
        if isinstance(source_node, VirtualDirectory) and self._is_inside(parent, source_node):
            raise FileSystemError("You cannot move a folder into itself.")
        if new_name in parent.children:
            raise FileSystemError(f"`{new_name}` already exists.")
        del source_node.parent.children[source_node.name]
        source_node.name = new_name
        source_node.parent = parent
        parent.children[new_name] = source_node

    def tree(self, path: str | None = None) -> list[str]:
        target = self.resolve(path or ".")
        lines: list[str] = []
        self._tree_lines(target, lines, prefix="")
        return lines

    def find(self, name: str, start_path: str | None = None) -> list[str]:
        start = self._expect_directory(self.resolve(start_path or "."))
        matches: list[str] = []

        def walk(directory: VirtualDirectory) -> None:
            for child_name in sorted(directory.children):
                child = directory.children[child_name]
                if child.name == name:
                    matches.append(self.path_for(child))
                if isinstance(child, VirtualDirectory):
                    walk(child)

        walk(start)
        return matches

    def path_for(self, node: Node) -> str:
        if node is self.root:
            return "/"
        parts = []
        current: Node | None = node
        while current is not None and current is not self.root:
            parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(parts))

    def _tree_lines(self, node: Node, lines: list[str], prefix: str) -> None:
        if node is self.root:
            lines.append("/")
            for name in sorted(self.root.children):
                self._tree_lines(self.root.children[name], lines, prefix="")
            return

        label = f"{node.name}/" if isinstance(node, VirtualDirectory) else node.name
        lines.append(f"{prefix}{label}")
        if isinstance(node, VirtualDirectory):
            child_prefix = f"{prefix}  "
            for name in sorted(node.children):
                self._tree_lines(node.children[name], lines, child_prefix)

    def _try_resolve(self, path: str) -> Node | None:
        try:
            return self.resolve(path)
        except FileSystemError:
            return None

    def _parent_and_name(self, path: str) -> tuple[VirtualDirectory, str]:
        cleaned = path.rstrip("/")
        if cleaned in ("", "/"):
            raise FileSystemError("That path needs a name at the end.")
        parts = cleaned.split("/")
        name = parts[-1]
        parent_path = "/".join(parts[:-1]) or ("." if not cleaned.startswith("/") else "/")
        parent = self._expect_directory(self.resolve(parent_path))
        return parent, name

    def _expect_directory(self, node: Node) -> VirtualDirectory:
        if not isinstance(node, VirtualDirectory):
            raise FileSystemError(f"`{self.path_for(node)}` is a file, not a directory.")
        return node

    def _expect_file(self, node: Node) -> VirtualFile:
        if not isinstance(node, VirtualFile):
            raise FileSystemError(f"`{self.path_for(node)}` is a directory, not a file.")
        return node

    def _is_inside(self, directory: VirtualDirectory, possible_parent: VirtualDirectory) -> bool:
        current: VirtualDirectory | None = directory
        while current is not None:
            if current is possible_parent:
                return True
            current = current.parent
        return False

    def _path_depth(self, path: str) -> int:
        return len([part for part in path.split("/") if part])
