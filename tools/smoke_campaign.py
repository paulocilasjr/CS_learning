#!/usr/bin/env python3
from __future__ import annotations

import builtins
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terminal_quest.game import TerminalQuestGame  # noqa: E402
from terminal_quest.tasks import Task, format_command  # noqa: E402


SPECIAL_SOLUTIONS: dict[int, list[str]] = {
    30: ["grep Tatooine transmissions/intercepts.txt > reports/tatooine.txt"],
    31: ['echo "PRIORITY: HIGH" >> reports/tatooine.txt'],
    32: ["cat transmissions/intercepts.txt | grep IMPERIAL | wc -l"],
    33: ["mkdir processed && cp reports/tatooine.txt processed/tatooine.txt"],
    34: ["grep REBEL transmissions/intercepts.txt | sort > reports/rebel_sorted.txt"],
    51: [
        'edit diagnostics/broken_navigation.py 3 "if fuel >= distance:"',
        "python diagnostics/broken_navigation.py",
    ],
    52: [
        'edit diagnostics/syntax_fault.py 2 "if enemy_near:"',
        "python diagnostics/syntax_fault.py",
    ],
    53: [
        'edit diagnostics/jump_tests.py 2 "    return fuel >= distance"',
        "test diagnostics/jump_tests.py",
    ],
    55: ['edit mission_plan.py 2 "shields = True"', "git diff"],
    56: ['edit mission_plan.py 1 \'route = "Endor"\'', "git add .", "git status"],
    57: [
        'edit mission_plan.py 1 \'route = "Dagobah"\'',
        "git add .",
        'git commit -m "Choose Dagobah"',
    ],
    60: [
        "git branch endor-route",
        "git switch endor-route",
        'edit mission_plan.py 1 \'route = "Endor"\'',
        "git add .",
        'git commit -m "Choose Endor"',
        "git switch main",
        "git merge endor-route",
    ],
    61: ["grep FLEET intelligence/incoming/beta.log > safe/fleet_location.txt"],
    62: [
        "cp intelligence/navigation.map safe/navigation.map",
        "rm intelligence/imperial_tracker.dat",
    ],
    63: ['edit programs/defense.py 2 "if enemy_near == True:"', "python programs/defense.py"],
    64: ['write programs/final_scan.py \'print("Dantooine")\'', "python programs/final_scan.py"],
    65: [
        'write mission_summary.txt "MISSION COMPLETE"',
        "git add .",
        'git commit -m "Complete final mission"',
    ],
}


def solution_for(task: Task) -> list[str]:
    if task.number in SPECIAL_SOLUTIONS:
        return SPECIAL_SOLUTIONS[task.number]
    if task.outcome is None:
        return [format_command(task.expected_command, task.expected_args)]
    if 35 <= task.number <= 49:
        path, code = next(iter(task.outcome.file_contents.items()))
        escaped_code = code.replace("\n", "\\n")
        return [format_command("write", [path, escaped_code]), f"python {path}"]
    raise ValueError(f"No smoke-test solution for mission {task.number}: {task.name}")


def main() -> int:
    game = TerminalQuestGame(save_enabled=False)
    commands = [command for task in game.tasks for command in solution_for(task)]
    command_iterator = iter(commands)
    original_input = builtins.input
    output = io.StringIO()

    try:
        builtins.input = lambda _prompt="": next(command_iterator)
        with redirect_stdout(output):
            game.run()
    finally:
        builtins.input = original_input

    transcript = output.getvalue()
    expected_stars = len(game.tasks) * 3
    if "You completed the current Star Wars campaign." not in transcript:
        raise RuntimeError("Campaign did not reach its completion message.")
    if game.stars != expected_stars:
        raise RuntimeError(f"Expected {expected_stars} stars, received {game.stars}.")
    if game.current_index != len(game.tasks):
        raise RuntimeError(f"Stopped at mission index {game.current_index}.")
    if not game.story_state.story_flags.get("final_campaign_complete"):
        raise RuntimeError("Final story flag was not recorded.")

    print(
        f"Campaign smoke test passed: {len(game.tasks)} missions, "
        f"{game.stars} stars, {len(game.learning_state.skills)} practiced skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
