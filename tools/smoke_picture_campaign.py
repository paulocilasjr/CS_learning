#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from picture_logic.game import PictureLogicGame  # noqa: E402
from picture_logic.missions import build_picture_missions  # noqa: E402


def main() -> int:
    missions = build_picture_missions()
    commands: list[str] = []
    for mission in missions:
        commands.append(" ".join(str(mission.cards.index(action) + 1) for action in mission.solution))
        commands.append("run")
    command_iterator = iter(commands)
    transcript: list[str] = []
    game = PictureLogicGame(
        save_enabled=False,
        input_fn=lambda _prompt: next(command_iterator),
        output_fn=transcript.append,
    )

    game.run()

    if game.current_index != len(missions):
        raise RuntimeError(f"Stopped at picture mission index {game.current_index}.")
    if game.stars != len(missions) * 3:
        raise RuntimeError(f"Expected {len(missions) * 3} stars, received {game.stars}.")
    if not any("PICTURE ADVENTURE COMPLETE" in line for line in transcript):
        raise RuntimeError("Picture campaign did not reach its completion message.")

    print(f"Picture campaign smoke test passed: {len(missions)} levels, {game.stars} stars.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
