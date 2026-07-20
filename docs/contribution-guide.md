# Contribution Guide

## Local checks

The project uses the Python standard library and requires no dependency installation.

```sh
python3 tools/validate_curriculum.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_campaign.py
python3 tools/smoke_picture_campaign.py
python3 -m compileall -q main.py game_core picture_logic terminal_quest tools tests
```

## Adding curriculum content

Add or reuse a story-neutral skill in `terminal_quest/curriculum.py`, then add mission data in `terminal_quest/tasks.py`. Do not put story copy in command handlers or terminal implementation in mission text. New skills need stable keys, minimal genuine prerequisites, and an introduction before any review.

Missions that change state need canonical steps for deterministic later snapshots. Open-ended missions should validate outcomes rather than a single expected command string. Use Plan-and-Run when the learning objective is deciding and inspecting ordered steps before execution.

## Adding terminal behavior

Register a handler and help definition in `TutorialShell`. Keep the grammar intentionally small and add focused tests under `tests/`. Commands must operate only on the virtual filesystem, programming runtime, or simulated repository.

## Adding picture behavior

Add visual action cards and mission data under `picture_logic/`. Picture actions must remain command-free, execute through the shared `game_core.planning` stepper, start each run from a deterministic board, and display the board after every consequence. Keep click targets large, text short, hints progressive, and rewards independent of attempts. Validate the browser flow and responsive layout as well as the Python engine.

## Quality expectations

- Preserve deterministic reset behavior.
- Include friendly, actionable error messages.
- Test both a successful path and representative failure.
- Run both campaign smoke tests after curriculum or engine changes.
- Update documentation when command syntax, mission count, or architecture changes.
