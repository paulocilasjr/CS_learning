# Star Wars Computer Science Learning Adventures

This project contains two separate Star Wars learning games connected by the same Plan-and-Run backbone:

- **Picture Logic Game** for younger learners: choose emoji action cards, arrange a plan, run it, and watch BB-8 move through ten visual levels. No computer commands are required.
- **Terminal CS Game** for older learners: complete 66 missions covering terminal commands, programming, debugging, testing, version control, and independent problem solving.

Every Terminal CS mission gives:

- a short story moment
- a story-style explanation of the command
- an objective with progressively revealing hints
- the actual result inside a safe virtual computer
- optional Plan-and-Run steps when the learner should decide the sequence before executing it

Early terminal missions teach exact commands. Later missions accept multi-step and alternative solutions by validating their output and final virtual-computer state. The Picture Logic Game teaches the same planning cycle with visual cards and a safe board. Neither game applies lesson actions to real computer files.

## Start The Game

The simplest launcher is:

```sh
./start.sh
```

You can also run it directly with Python:

```sh
python3 main.py
```

The launcher asks which game to play:

```text
1. Terminal CS Game
2. Picture Logic Game
```

Start either game directly when desired:

```sh
python3 main.py --game terminal
python3 main.py --game picture
```

The games store progress independently. Resetting one selected game does not erase the other game's save.

## Terminal CS Campaign

The campaign contains 66 missions across 12 chapters:

1. terminal state and navigation;
2. reading and creating information;
3. organizing and safely removing data;
4. searching and filtering transmissions;
5. pipes, redirection, chaining, wildcards, and Plan-and-Run;
6. variables, values, and expressions;
7. comparisons, conditions, and Boolean logic;
8. lists and loops;
9. functions, mappings, and algorithms;
10. debugging and automated simulation tests;
11. simulated Git status, diffs, commits, history, branches, and merges;
12. open-ended capstones that combine the full curriculum.

The game records mastery evidence separately from story progress. Type `skills` during play to inspect attempts, hints, mastery stages, and recommended review topics.

## Helpful Options

```sh
python3 main.py --game terminal --reset
python3 main.py --game picture --reset
python3 main.py --game terminal --no-save --start-task 8
python3 main.py --game picture --no-save --start-level 4
```

- `--game` skips the launcher menu.
- `--reset` clears progress for the selected game.
- `--no-save` runs without writing progress to disk.
- `--start-task` jumps to a Terminal CS mission while testing.
- `--start-level` jumps to a Picture Logic level while testing.

## Terminal CS Commands

- `hint` shows a clue for the current mission.
- `repeat` shows the mission again.
- `progress` shows stars and mission progress.
- `skills` shows mastery evidence and recommended reviews.
- `plan` shows how to build, inspect, clear, and run ordered command steps.
- `reset` resets the current mission room.
- `exit` leaves the game.

## Picture Logic Controls

- Number keys add the picture cards shown on screen.
- `run` executes the complete picture plan.
- `show`, `undo`, and `clear` help revise the plan.
- `hint` gives a level clue.
- `board` repeats the starting board.
- `exit` leaves the picture game.

## Curriculum Development

The campaign now has a story-neutral skill registry, dependency graph, and explicit mission types. See [the curriculum](docs/curriculum.md) and [the skill tree](docs/skill-tree.md).

Validate the teaching order and run the tests with:

```sh
python3 tools/validate_curriculum.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_campaign.py
python3 tools/smoke_picture_campaign.py
```

The smoke tests complete all 66 terminal missions and all 10 picture levels through the same game loops used by players.

## Documentation

- [Product vision](docs/product-vision.md)
- [Curriculum](docs/curriculum.md)
- [Skill tree](docs/skill-tree.md)
- [Architecture](docs/architecture.md)
- [Mission design](docs/mission-design.md)
- [Story bible](docs/story-bible.md)
- [Contribution guide](docs/contribution-guide.md)
- [Development phases](docs/development-phases.md)
- [Picture Logic Game](docs/picture-logic-game.md)

## Prototype Files

The repository also includes a [star_wars_training](star_wars_training/) folder with the original static Star Wars exercise prototype. The runnable game uses its own virtual file system, so the command story can restart cleanly every time.
