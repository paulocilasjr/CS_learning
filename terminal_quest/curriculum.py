from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Iterable, Protocol


class MissionType(str, Enum):
    """The learning job a mission performs."""

    INTRODUCE = "introduce"
    PRACTICE = "practice"
    RECALL = "recall"
    TRANSFER = "transfer"
    COMBINE = "combine"
    DEBUG = "debug"
    CAPSTONE = "capstone"


class MasteryStage(IntEnum):
    """Observable stages used by the future learning engine."""

    UNSEEN = 0
    INTRODUCED = 1
    GUIDED = 2
    RECALLED = 3
    TRANSFERRED = 4
    INTEGRATED = 5


@dataclass(frozen=True)
class SkillDefinition:
    key: str
    name: str
    category: str
    phase: int
    prerequisites: tuple[str, ...]
    description: str


def _skill(
    key: str,
    name: str,
    category: str,
    phase: int,
    description: str,
    *prerequisites: str,
) -> SkillDefinition:
    return SkillDefinition(key, name, category, phase, prerequisites, description)


# This registry is story-neutral on purpose. Missions connect these technical
# abilities to Star Wars situations; the dependency graph remains reusable.
SKILLS: dict[str, SkillDefinition] = {
    skill.key: skill
    for skill in (
        _skill("pwd", "Current location", "terminal", 1, "Inspect the current working directory."),
        _skill("ls", "Directory inspection", "terminal", 1, "List visible directory contents."),
        _skill("cat", "Read a file", "files", 1, "Display the information stored in a text file.", "ls"),
        _skill("relative_paths", "Relative paths", "navigation", 1, "Describe a location from the current directory.", "ls"),
        _skill("cd", "Change directory", "navigation", 1, "Move through a directory hierarchy.", "ls", "relative_paths"),
        _skill("targeted_listing", "Inspect another directory", "navigation", 1, "List a directory without moving into it.", "ls", "relative_paths"),
        _skill("hidden_files", "Hidden files", "files", 1, "Reveal names that begin with a dot by using an option.", "ls"),
        _skill("mkdir", "Create a directory", "files", 1, "Create a new place for organized information.", "cd"),
        _skill("nested_paths", "Nested paths", "navigation", 1, "Address an item inside more than one directory.", "relative_paths"),
        _skill("touch", "Create a file", "files", 1, "Create an empty file.", "cat", "mkdir"),
        _skill("mv", "Move information", "files", 1, "Move or rename a file or directory.", "touch", "relative_paths"),
        _skill("parent_paths", "Parent paths", "navigation", 1, "Use two dots to address a parent directory.", "cd", "relative_paths"),
        _skill("cp", "Copy information", "files", 1, "Duplicate information while preserving the source.", "cat", "relative_paths", "parent_paths"),
        _skill("find", "Find by name", "search", 1, "Search a directory tree for a named item.", "ls", "cat"),
        _skill("tree", "Inspect a hierarchy", "search", 1, "Display nested directories as a tree.", "ls", "nested_paths"),
        _skill("absolute_paths", "Absolute paths", "navigation", 1, "Address a location from the filesystem root.", "cd"),
        _skill("echo", "Produce text", "files", 2, "Send text to terminal output.", "cat"),
        _skill("rm", "Remove a file", "files", 2, "Delete a chosen file and reason about consequences.", "ls", "cat"),
        _skill("clear", "Clear the terminal", "terminal", 2, "Clear old output from the display."),
        _skill("grep", "Search file contents", "search", 6, "Select lines that contain a pattern.", "cat", "find"),
        _skill("head", "Read the beginning", "search", 6, "Inspect the first part of larger data.", "cat"),
        _skill("tail", "Read the ending", "search", 6, "Inspect the final part of larger data.", "cat"),
        _skill("wc", "Count data", "search", 6, "Count lines, words, or characters.", "cat"),
        _skill("sort", "Sort text data", "search", 6, "Arrange lines in a predictable order.", "cat"),
        _skill("redirection", "Redirect output", "composition", 6, "Save command output as file data.", "echo", "touch"),
        _skill("append_redirection", "Append output", "composition", 6, "Add command output to existing file data.", "redirection"),
        _skill("pipes", "Connect commands", "composition", 6, "Use one command's output as another command's input.", "grep", "wc"),
        _skill("command_chaining", "Sequence commands", "composition", 6, "Run a later operation only after an earlier one succeeds.", "pipes"),
        _skill("wildcards", "Match name patterns", "composition", 6, "Operate on several matching names.", "ls", "relative_paths"),
        _skill("variables", "Variables", "programming", 7, "Give meaningful names to values."),
        _skill("data_types", "Data types", "programming", 7, "Distinguish text, numbers, and truth values.", "variables"),
        _skill("expressions", "Expressions", "programming", 7, "Combine values and operations to calculate a result.", "variables", "data_types"),
        _skill("comparisons", "Comparisons", "logic", 7, "Compare values to produce true or false.", "expressions"),
        _skill("conditions", "Conditions", "logic", 7, "Choose behavior with if and else.", "comparisons"),
        _skill("boolean_logic", "Boolean logic", "logic", 7, "Combine and invert true-or-false conditions.", "conditions"),
        _skill("lists", "Lists", "collections", 7, "Store an ordered collection of values.", "variables", "data_types"),
        _skill("loops", "Loops", "programming", 7, "Repeat instructions across values.", "conditions", "lists"),
        _skill("functions", "Functions", "programming", 7, "Name and reuse a sequence of instructions.", "variables", "conditions", "loops"),
        _skill("parameters", "Parameters", "programming", 7, "Give reusable behavior input values.", "functions"),
        _skill("return_values", "Return values", "programming", 7, "Send a result back from reusable behavior.", "functions", "expressions"),
        _skill("mappings", "Key/value mappings", "collections", 7, "Look up structured values by meaningful keys.", "lists"),
        _skill("search_algorithms", "Search algorithms", "algorithms", 7, "Describe repeatable steps for locating a value.", "loops", "lists", "functions"),
        _skill("sorting_algorithms", "Sorting algorithms", "algorithms", 7, "Arrange values according to a comparison rule.", "comparisons", "loops", "lists"),
        _skill("debugging", "Debugging", "engineering", 8, "Compare expected and actual behavior to locate a problem.", "functions", "conditions"),
        _skill("testing", "Testing", "engineering", 8, "Check behavior automatically with representative cases.", "debugging", "return_values"),
        _skill("git_status", "Inspect repository state", "version-control", 9, "See which files have changed."),
        _skill("git_diff", "Inspect changes", "version-control", 9, "Review the exact difference between versions.", "git_status"),
        _skill("git_add", "Stage changes", "version-control", 9, "Choose changes for a future snapshot.", "git_diff"),
        _skill("git_commit", "Commit changes", "version-control", 9, "Save a meaningful project snapshot.", "git_add"),
        _skill("git_log", "Inspect history", "version-control", 9, "Read earlier project snapshots.", "git_commit"),
        _skill("git_branch", "Work on a branch", "version-control", 9, "Develop an alternate line of changes safely.", "git_log"),
        _skill("git_merge", "Merge work", "version-control", 9, "Combine compatible lines of project history.", "git_branch"),
    )
}


class CampaignMission(Protocol):
    number: int
    mission_type: MissionType
    new_skills: tuple[str, ...]
    review_skills: tuple[str, ...]


class CurriculumValidationError(ValueError):
    pass


def skill_graph_errors(skills: dict[str, SkillDefinition] = SKILLS) -> list[str]:
    errors: list[str] = []

    for key, skill in skills.items():
        for prerequisite in skill.prerequisites:
            if prerequisite not in skills:
                errors.append(f"Skill `{key}` has unknown prerequisite `{prerequisite}`.")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(key: str, path: tuple[str, ...]) -> None:
        if key in visited or key not in skills:
            return
        if key in visiting:
            cycle = " -> ".join((*path, key))
            errors.append(f"Skill dependency cycle: {cycle}.")
            return

        visiting.add(key)
        for prerequisite in skills[key].prerequisites:
            visit(prerequisite, (*path, key))
        visiting.remove(key)
        visited.add(key)

    for key in skills:
        visit(key, ())

    return errors


def campaign_errors(missions: Iterable[CampaignMission]) -> list[str]:
    errors = skill_graph_errors()
    introduced: set[str] = set()

    for mission in missions:
        label = f"Mission {mission.number}"
        new = set(mission.new_skills)
        review = set(mission.review_skills)

        if not new and not review:
            errors.append(f"{label} has no skill metadata.")
        if new & review:
            overlap = ", ".join(sorted(new & review))
            errors.append(f"{label} lists skills as both new and review: {overlap}.")
        if mission.mission_type is MissionType.INTRODUCE and not new:
            errors.append(f"{label} is INTRODUCE but introduces no skill.")

        unknown = (new | review) - SKILLS.keys()
        for key in sorted(unknown):
            errors.append(f"{label} references unknown skill `{key}`.")

        for key in sorted(new & introduced):
            errors.append(f"{label} re-introduces skill `{key}`.")

        for key in sorted(review - introduced):
            errors.append(f"{label} reviews `{key}` before it is introduced.")

        available = introduced | new
        for key in sorted(new):
            if key not in SKILLS:
                continue
            missing = set(SKILLS[key].prerequisites) - available
            if missing:
                errors.append(
                    f"{label} introduces `{key}` before prerequisites: "
                    f"{', '.join(sorted(missing))}."
                )

        introduced.update(new)

    return errors


def validate_campaign(missions: Iterable[CampaignMission]) -> None:
    errors = campaign_errors(missions)
    if errors:
        raise CurriculumValidationError("\n".join(errors))
