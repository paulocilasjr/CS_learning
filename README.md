# Star Wars Terminal Quest

`Star Wars Terminal Quest` is a safe, terminal-only computer science adventure for young learners. It begins with command-line basics and progresses through programming, debugging, testing, version control, and independent problem solving.

Every mission gives:

- a short story moment
- a story-style explanation of the command
- an objective with progressively revealing hints
- the actual result inside a safe virtual computer
- optional Plan-and-Run steps when the learner should decide the sequence before executing it

Early missions teach exact commands. Later missions accept multi-step and alternative solutions by validating their output and final virtual-computer state. Plan-and-Run lets the learner write ordered steps first, inspect the plan, and then run it through the same command engine. The game never applies lesson commands to real files.

## Start The Game

The simplest launcher is:

```sh
./start.sh
```

You can also run it directly with Python:

```sh
python3 main.py
```

## Complete Campaign

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
python3 main.py --reset
python3 main.py --no-save
python3 main.py --start-task 8
```

- `--reset` starts from mission 1 and clears saved progress.
- `--no-save` runs without writing progress to disk.
- `--start-task` jumps to a specific mission while testing.

## In-Game Commands

- `hint` shows a clue for the current mission.
- `repeat` shows the mission again.
- `progress` shows stars and mission progress.
- `skills` shows mastery evidence and recommended reviews.
- `plan` shows how to build, inspect, clear, and run ordered command steps.
- `reset` resets the current mission room.
- `exit` leaves the game.

## Curriculum Development

The campaign now has a story-neutral skill registry, dependency graph, and explicit mission types. See [the curriculum](docs/curriculum.md) and [the skill tree](docs/skill-tree.md).

Validate the teaching order and run the tests with:

```sh
python3 tools/validate_curriculum.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_campaign.py
```

The smoke test completes all 66 missions through the same game loop used by a player.

## Documentation

- [Product vision](docs/product-vision.md)
- [Curriculum](docs/curriculum.md)
- [Skill tree](docs/skill-tree.md)
- [Architecture](docs/architecture.md)
- [Mission design](docs/mission-design.md)
- [Story bible](docs/story-bible.md)
- [Contribution guide](docs/contribution-guide.md)
- [Development phases](docs/development-phases.md)

## Prototype Files

The repository also includes a [star_wars_training](star_wars_training/) folder with the original static Star Wars exercise prototype. The runnable game uses its own virtual file system, so the command story can restart cleanly every time.
