from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Callable

from terminal_quest.filesystem import FileSystemError


CommandHandler = Callable[[list[str]], str]


@dataclass(frozen=True)
class CommandDefinition:
    name: str
    usage: str
    description: str
    handler: CommandHandler


class CommandRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, CommandDefinition] = {}

    def register(self, definition: CommandDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(f"Command `{definition.name}` is already registered.")
        self._definitions[definition.name] = definition

    def get(self, name: str) -> CommandDefinition | None:
        return self._definitions.get(name)

    def definitions(self) -> list[CommandDefinition]:
        return [self._definitions[name] for name in sorted(self._definitions)]


class CommandParser:
    OPERATORS = {"|", ">", ">>", "&&"}

    def parse(self, raw: str) -> list[str]:
        try:
            lexer = shlex.shlex(raw, posix=True, punctuation_chars="|>&")
            lexer.whitespace_split = True
            lexer.commenters = ""
            return list(lexer)
        except ValueError as exc:
            raise FileSystemError(f"Parsing error: {exc}") from exc


class CommandExecutor:
    def __init__(self, registry: CommandRegistry) -> None:
        self.registry = registry

    def execute(self, name: str, args: list[str]) -> str:
        definition = self.registry.get(name)
        if definition is None:
            raise FileSystemError(f"Unknown command: {name}")
        return definition.handler(args)
