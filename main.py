from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

from picture_logic import PictureLogicGame
from terminal_quest import TerminalQuestGame


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Choose and play a Star Wars learning game.")
    parser.add_argument(
        "--game",
        choices=("terminal", "picture"),
        help="Skip the launcher and start one game directly.",
    )
    parser.add_argument("--no-save", action="store_true", help="Run without saving progress.")
    parser.add_argument("--reset", action="store_true", help="Clear progress for the selected game.")
    parser.add_argument("--start-task", type=int, help="Start the Terminal CS game at a mission.")
    parser.add_argument("--start-level", type=int, help="Start the Picture Logic game at a level.")
    return parser.parse_args(argv)


def choose_game(
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> str:
    ask = input_fn or input
    show = output_fn or print
    show("\n🌌 CHOOSE YOUR STAR WARS ADVENTURE 🌌")
    show("1. 💻 Terminal CS Game — commands, Python, debugging, and Git")
    show("2. 🧩 Picture Logic Game — picture cards, plans, and BB-8")
    show("Q. Leave")

    while True:
        try:
            choice = ask("choose> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return "exit"
        if choice in {"1", "terminal", "terminal cs"}:
            return "terminal"
        if choice in {"2", "picture", "picture logic"}:
            return "picture"
        if choice in {"q", "quit", "exit"}:
            return "exit"
        show("Please choose 1, 2, or Q.")


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> None:
    args = parse_args(argv)
    if args.start_task is not None and args.start_level is not None:
        raise SystemExit("Choose either --start-task or --start-level, not both.")

    selected = args.game
    if selected is None and args.start_task is not None:
        selected = "terminal"
    if selected is None and args.start_level is not None:
        selected = "picture"
    if selected is None:
        selected = choose_game(input_fn=input_fn, output_fn=output_fn)
    if selected == "exit":
        return

    if selected == "terminal":
        if args.start_level is not None:
            raise SystemExit("--start-level belongs to the Picture Logic game.")
        game = TerminalQuestGame(
            save_enabled=not args.no_save,
            start_task=args.start_task,
            reset_progress=args.reset,
        )
    else:
        if args.start_task is not None:
            raise SystemExit("--start-task belongs to the Terminal CS game.")
        game = PictureLogicGame(
            save_enabled=not args.no_save,
            start_level=args.start_level,
            reset_progress=args.reset,
            input_fn=input_fn,
            output_fn=output_fn,
        )
    game.run()


if __name__ == "__main__":
    main()
