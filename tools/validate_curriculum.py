#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terminal_quest.curriculum import SKILLS, validate_campaign  # noqa: E402
from terminal_quest.tasks import build_tasks  # noqa: E402


def main() -> int:
    tasks = build_tasks()
    validate_campaign(tasks)
    introduced = {skill for task in tasks for skill in task.new_skills}
    print(
        f"Curriculum valid: {len(SKILLS)} registered skills, "
        f"{len(tasks)} missions, {len(introduced)} introduced skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

