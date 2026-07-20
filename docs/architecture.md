# Architecture

The project is separated into story-neutral engines and Star Wars curriculum data.

```text
main.py game launcher
        |
        +---- Local browser UI ---- Picture missions ---- Picture world
        |              \\            /
        |               Plan-and-Run / PlanStepper
        |              /            \\
        +---- Terminal CS UI ----- Terminal missions ---- Outcome validator
                                      |
                         Command parser / virtual filesystem / Python / Git

Each game ---- independent progress file
```

## Components

- `main.py` is the shared launcher. With no `--game` option it asks the player to choose; direct CLI options remain available for testing and shortcuts.
- `game_core/planning.py` is the interface-neutral Plan-and-Run model. `PlanRunner` supports synchronous terminal play and `PlanStepper` lets visual interfaces pause between animation frames. `game_core/persistence.py` supplies generic JSON storage while each game chooses a different save file.
- `picture_logic/web_app.py` hosts a tokenized localhost-only browser session and sends plan steps to Python. `picture_logic/web/` contains the responsive click interface, `picture_logic/engine.py` executes cards against a fresh visual board, and `picture_logic/missions.py` contains the independent twelve-level younger curriculum. `picture_logic/game.py` retains a text fallback when no browser is available.
- `terminal_quest/game.py` owns the terminal UI loop, chapter transitions, hints, and coordination. It does not implement filesystem storage or curriculum ordering.
- `terminal_quest/tasks.py` contains data-driven chapter, world, and mission specifications. `CampaignBuilder` snapshots deterministic starting states and produces immutable playable tasks.
- `terminal_quest/curriculum.py` is the canonical story-neutral skill registry, prerequisite graph, mastery vocabulary, and content validator.
- `terminal_quest/command_engine.py` separates tokenization, command registration, and command dispatch. Its parser supports the deliberately limited grammar required by the curriculum.
- `terminal_quest/filesystem.py` implements safe files, directories, paths, cloning, search, wildcards, and snapshots entirely in memory.
- `terminal_quest/validation.py` checks observable outcomes: location, file presence or absence, exact content, output fragments, and used operations. Exact syntax remains available for early guided missions.
- `terminal_quest/state.py` stores story progress and per-skill learning evidence independently.
- `terminal_quest/learning.py` ranks review needs without changing narrative order.
- `terminal_quest/version_control.py` provides deterministic Git concepts over virtual filesystem snapshots.

## Terminal grammar

The teaching shell intentionally implements only the required subset:

```text
command arguments
command | command
command > file
command >> file
command && command
```

Quoted arguments are parsed with shell-like rules. Commands can consume piped input, and redirection writes only to the virtual filesystem. Wildcard expansion is limited and predictable.

## Mission validation

Early guided missions compare normalized command names and arguments. Multi-step and capstone missions inspect final state and output. This accepts equivalent strategies while still allowing a curriculum author to require evidence that a particular composition concept was practiced. Missions can also require Plan-and-Run evidence when the skill under assessment is building an ordered solution before executing it.

## Plan-and-Run

Plan-and-Run is intentionally below both game interfaces and above their execution engines. A plan is a list of interface-neutral steps. The Picture Logic Game stores action-card keys with `source="picture"`; the Terminal CS Game stores text commands. Both use the same step ordering and stop-on-error behavior. The browser requests one Python `PlanStepper` advance per visual frame, preserving the direct relationship between a picture card and its consequence. Terminal validation also records commands and relevant virtual-filesystem state from a specific run, so a planning mission cannot receive credit for work completed outside the plan.

## Safety boundaries

- Lesson commands never call the host shell.
- `rm` and simulated Git mutate only in-memory virtual state.
- Python programs execute with a small built-in namespace and no import built-in.
- Mission reset reloads a deterministic snapshot.
- Progress persistence writes only the two documented, game-specific save files.
- Picture and terminal progress use different files, so resetting one game cannot erase the other.
- The picture browser binds only to `127.0.0.1`, uses an unguessable session path, limits request sizes, and stops when the player chooses Leave.
