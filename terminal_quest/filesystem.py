from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, TypeAlias


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
    children: dict[str, "Node"] = field(default_factory=dict)

    def clone(self, parent: "VirtualDirectory | None" = None) -> "VirtualDirectory":
        copied = VirtualDirectory(name=self.name, parent=parent)
        for name in sorted(self.children):
            copied.children[name] = self.children[name].clone(copied)
        return copied


Node: TypeAlias = VirtualFile | VirtualDirectory


class VirtualFileSystem:
    def __init__(self) -> None:
        self.root = VirtualDirectory(name="")
        self.cwd = self.root

    def load_snapshot(self, *, cwd: str, dirs: list[str], files: dict[str, str]) -> None:
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
        return {
            "cwd": self.pwd(),
            "dirs": dirs,
            "files": files,
        }

    def pwd(self) -> str:
        return self.path_for(self.cwd)

    def resolve(self, path: str, start: VirtualDirectory | None = None) -> Node:
        if path == "":
            return self.cwd

        current: Node = self.root if path.startswith("/") else (start or self.cwd)
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if isinstance(current, VirtualDirectory) and current.parent is not None:
                    current = current.parent
                continue
            current = self._resolve_child(current, part, original_path=path)
        return current

    def mkdir(self, path: str) -> None:
        parent, name = self._parent_and_name(path)
        self._ensure_name_available(parent, name)
        parent.children[name] = VirtualDirectory(name=name, parent=parent)

    def touch(self, path: str) -> None:
        file_node = self._get_or_create_file(path)
        if isinstance(file_node, VirtualDirectory):
            raise FileSystemError(f"`{file_node.name}` is a directory, not a file.")

    def read_file(self, path: str) -> str:
        return self._expect_file(self.resolve(path)).content

    def write_file(self, path: str, text: str) -> None:
        file_node = self._get_or_create_file(path)
        file_node.content = text

    def append_file(self, path: str, text: str) -> None:
        file_node = self._get_or_create_file(path)
        file_node.content = f"{file_node.content}\n{text}" if file_node.content else text

    def ls(self, path: str | None = None, *, show_hidden: bool = False) -> list[str]:
        target = self.resolve(path or ".")
        if isinstance(target, VirtualFile):
            return [target.name]

        items: list[str] = []
        for name in sorted(target.children):
            if not show_hidden and name.startswith("."):
                continue
            child = target.children[name]
            suffix = "/" if isinstance(child, VirtualDirectory) else ""
            items.append(f"{name}{suffix}")
        return items

    def change_directory(self, path: str) -> None:
        self.cwd = self._expect_directory(self.resolve(path))

    def remove_file(self, path: str) -> None:
        file_node = self._expect_file(self.resolve(path))
        self._remove_node(file_node, root_message="You cannot remove the root folder.")

    def remove_directory(self, path: str) -> None:
        directory = self._expect_directory(self.resolve(path))
        if directory.children:
            raise FileSystemError("That folder is not empty yet.")
        self._remove_node(directory, root_message="You cannot remove the root folder.")

    def copy(self, source: str, destination: str) -> None:
        source_node = self.resolve(source)
        parent, new_name = self._resolve_destination(destination, source_node.name)
        clone = source_node.clone(parent)
        clone.name = new_name
        parent.children[new_name] = clone

    def move(self, source: str, destination: str) -> None:
        source_node = self.resolve(source)
        if source_node is self.root:
            raise FileSystemError("You cannot move the root folder.")

        assert source_node.parent is not None
        parent, new_name = self._resolve_destination(destination, source_node.name)

        if isinstance(source_node, VirtualDirectory) and self._is_inside(parent, source_node):
            raise FileSystemError("You cannot move a folder into itself.")

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

        parts: list[str] = []
        current: Node | None = node
        while current is not None and current is not self.root:
            parts.append(current.name)
            current = current.parent
        return "/" + "/".join(reversed(parts))

    def _resolve_child(self, current: Node, part: str, *, original_path: str) -> Node:
        directory = self._expect_directory(current)
        child = directory.children.get(part)
        if child is None:
            raise FileSystemError(f"Path not found: {original_path}")
        return child

    def _get_or_create_file(self, path: str) -> VirtualFile:
        parent, name = self._parent_and_name(path)
        existing = parent.children.get(name)

        if existing is None:
            file_node = VirtualFile(name=name, parent=parent)
            parent.children[name] = file_node
            return file_node

        if isinstance(existing, VirtualDirectory):
            raise FileSystemError(f"`{name}` is a directory, not a file.")

        return existing

    def _resolve_destination(self, destination: str, default_name: str) -> tuple[VirtualDirectory, str]:
        existing = self._try_resolve(destination)
        if existing is not None:
            destination_dir = self._expect_directory(existing)
            self._ensure_name_available(
                destination_dir,
                default_name,
                message=f"`{default_name}` already exists in `{self.path_for(destination_dir)}`.",
            )
            return destination_dir, default_name

        parent, new_name = self._parent_and_name(destination)
        self._ensure_name_available(parent, new_name)
        return parent, new_name

    def _remove_node(self, node: Node, *, root_message: str) -> None:
        parent = node.parent
        if parent is None:
            raise FileSystemError(root_message)
        del parent.children[node.name]

    def _ensure_name_available(
        self,
        parent: VirtualDirectory,
        name: str,
        *,
        message: str | None = None,
    ) -> None:
        if name in parent.children:
            raise FileSystemError(message or f"`{name}` already exists.")

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

    @staticmethod
    def _path_depth(path: str) -> int:
        return len([part for part in path.split("/") if part])