# Mission Design

## Required shape

Each mission connects a story problem to observable technical evidence:

```text
story event -> problem -> concept -> action -> visible result -> consequence -> reflection
```

A `TaskSpec` declares its chapter, copy, command or outcome, mission type, new skills, review skills, hints, success text, and deterministic scenario. Complex missions also declare canonical build steps so later mission snapshots remain reproducible; those steps do not restrict player solutions.

## Guidance and hints

New ideas receive brief explanations and immediate action. Later appearances remove syntax guidance. Hints progress from a conceptual question to a command reminder, partial shape, and full example. Hint use is recorded as learning evidence and caps new mastery evidence at the guided stage.

## Choosing validation

Use exact command validation when syntax is itself the learning objective. Use outcome validation when the objective is what the computer becomes or produces.

Good outcome checks include:

- a report exists with the required content;
- dangerous data is absent while useful data remains;
- a program produces the expected behavior;
- a repository operation produces a saved snapshot;
- several valid command orders lead to the same safe state.

Avoid checking command history in a capstone unless use of that operation is explicitly part of the objective. The final campaign intentionally permits alternative implementations.

## Failure copy

Errors should identify syntax, target, state, or strategy without treating debugging as personal failure. Multi-step missions retain successful intermediate state. Single-step practice rooms reset after a miss so retries remain predictable.

## Author checklist

1. State the story consequence and observable objective.
2. Declare every introduced and reviewed skill.
3. Confirm prerequisites are already available.
4. Supply three progressively revealing hints.
5. Prefer state/output validation for independent work.
6. Add a deterministic canonical state transition.
7. Run curriculum validation, unit tests, and the full campaign smoke test.
