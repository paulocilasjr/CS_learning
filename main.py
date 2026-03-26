from __future__ import annotations

import argparse

from terminal_quest import TerminalQuestGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play the Star Wars terminal tutorial game.")
    parser.add_argument("--no-save", action="store_true", help="Run without saving progress.")
    parser.add_argument("--reset", action="store_true", help="Ignore and clear saved progress.")
    parser.add_argument("--start-task", type=int, help="Start from a specific mission number.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    game = TerminalQuestGame(
        save_enabled=not args.no_save,
        start_task=args.start_task,
        reset_progress=args.reset,
    )
    game.run()


if __name__ == "__main__":
    main()
