# Architecture

The project is separated into story-neutral engines and Star Wars curriculum data.

```text
Game UI and story flow
        |
Mission data ---- Curriculum registry
        |                 |
Outcome validator     Learning state/review engine
        |
Command parser -> registry -> executor
        |                    |
Virtual filesystem     Programming / simulated Git
        |
Persistence store (story and learning state)
```

## Components

- `terminal_quest/game.py` owns the terminal UI loop, chapter transitions, hints, and coordination. It does not implement filesystem storage or curriculum ordering.
- `terminal_quest/tasks.py` contains data-driven chapter, world, and mission specifications. `CampaignBuilder` snapshots deterministic starting states and produces immutable playable tasks.
- `terminal_quest/curriculum.py` is the canonical story-neutral skill registry, prerequisite graph, mastery vocabulary, and content validator.
- `terminal_quest/command_engine.py` separates tokenization, command registration, and command dispatch. Its parser supports the deliberately limited grammar required by the curriculum.
- `terminal_quest/filesystem.py` implements safe files, directories, paths, cloning, search, wildcards, and snapshots entirely in memory.
- `terminal_quest/validation.py` checks observable outcomes: location, file presence or absence, exact content, output fragments, and used operations. Exact syntax remains available for early guided missions.
- `terminal_quest/state.py` stores story progress and per-skill learning evidence independently.
- `terminal_quest/learning.py` ranks review needs without changing narrative order.
- `terminal_quest/persistence.py` serializes versioned progress while remaining independent of UI prompts.
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

Early guided missions compare normalized command names and arguments. Multi-step and capstone missions inspect final state and output. This accepts equivalent strategies while still allowing a curriculum author to require evidence that a particular composition concept was practiced.

## Safety boundaries

- Lesson commands never call the host shell.
- `rm` and simulated Git mutate only in-memory virtual state.
- Python programs execute with a small built-in namespace and no import built-in.
- Mission reset reloads a deterministic snapshot.
- Progress persistence writes only the single documented save file.
