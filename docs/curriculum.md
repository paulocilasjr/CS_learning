# Curriculum

## Learning goal

Star Wars Terminal Quest teaches a child to move from copying an instruction to choosing and combining tools independently. A mission succeeds educationally when the player understands the computer state, chooses an appropriate operation, observes the result, and can reuse that idea in a different situation.

The story supplies a concrete reason for each technical action. Curriculum metadata remains story-neutral so the learning engine can be tested and reused independently of the narrative.

## Learning cycle

Every skill progresses through six observable mastery stages:

| Value | Stage | Evidence |
| ---: | --- | --- |
| 0 | Unseen | The skill has not appeared. |
| 1 | Introduced | The game explained the concept and showed its syntax. |
| 2 | Guided | The player completed a closely guided use. |
| 3 | Recalled | The player selected it again without an exact command. |
| 4 | Transferred | The player used it in a meaningfully different situation. |
| 5 | Integrated | The player combined it with other concepts to solve a larger problem. |

Mastery is evidence, not a permanent badge. The learning state records attempts, hints, time last practiced, and independent successes. The review engine prioritizes weaker and more help-dependent skills. Speed alone does not increase mastery.

## Mission types

Every mission declares one pedagogical type:

- `INTRODUCE`: explains a new concept and gives immediate practice.
- `PRACTICE`: repeats a newly introduced skill with substantial guidance.
- `RECALL`: asks the player to retrieve an earlier skill with less guidance.
- `TRANSFER`: applies a known skill in a changed setting or syntax shape.
- `COMBINE`: requires multiple known skills in a planned sequence.
- `DEBUG`: asks the player to compare expected and actual behavior and repair the cause.
- `CAPSTONE`: accepts outcome-equivalent solutions to an open-ended problem.

A mission also declares `new_skills` and `review_skills`. The content validator rejects unknown skills, reviews before introduction, repeated introductions, missing prerequisites, and dependency cycles.

## Curriculum sequence

| Phase | Arc | Primary abilities | Intended evidence |
| ---: | --- | --- | --- |
| 1 | The New Recruit | terminal state, `pwd`, `ls`, `cd`, paths | Inspect before changing; navigate deliberately. |
| 2 | The Missing Droid | `cat`, `echo`, `touch`, `mkdir` | Read, create, and organize information. |
| 3 | Imperial Sabotage | `cp`, `mv`, `rm` | Preserve, reorganize, and safely remove data. |
| 4 | The Secret Transmission | `find`, `grep`, `head`, `tail`, `wc` | Choose efficient search and filtering tools. |
| 5 | The Intelligence Machine | redirection, pipes, chaining, wildcards | Treat commands as composable input/output machines. |
| 6 | Build a Droid | variables, types, expressions | Represent story state as named data. |
| 7 | Teach the Droid to Think | comparisons, conditions, Boolean logic | Give the computer decision rules. |
| 8 | The Galactic Scanner | lists, loops | Automate repeated work over collections. |
| 9 | Rebel Engineering Corps | functions, parameters, return values, mappings | Decompose and reuse solutions. |
| 10 | Broken Navigation Computer | algorithms, debugging, testing | Investigate behavior and verify repairs. |
| 11 | Rebel Code Repository | status, diff, add, commit, log, branch, merge | Understand and manage software history. |
| 12 | Final Campaign | all prior skills | Independently plan and validate multi-step solutions. |

## Guidance progression

Guidance should fade across appearances of the same skill:

1. Give the exact command and explain its effect.
2. Name the command but let the player supply syntax or a target.
3. Describe the operation without naming the command.
4. State only the story objective.
5. Accept multiple solutions that produce the required state or output.

Hints reveal information progressively:

1. Ask a conceptual question.
2. Remind the player of a previously used command.
3. Reveal the command or partial syntax.
4. Reveal the full solution.

Using a hint is normal learning behavior. It should be recorded so the game can schedule another practice opportunity, not framed as failure.

## Current playable campaign

The implemented campaign contains 65 missions in all 12 arcs. Every registered skill is introduced, earlier concepts return in recall and transfer situations, command composition culminates in a `COMBINE` mission, and the final chapter contains five outcome-based `CAPSTONE` missions.

Programming is integrated with the virtual world through editable Python files and visible output. Deliberately broken programs establish expected-versus-actual reasoning, assertions provide automated tests, and a simulated repository teaches recoverable history without touching the player's real Git repositories.

## Content rules

- Technical skills and prerequisites live in `terminal_quest/curriculum.py`.
- Story missions may reference only registered skill keys.
- A skill must be introduced after all of its prerequisites are available.
- A review must occur after introduction.
- Story copy never implements terminal behavior, and command code never contains plot progression.
- Later open-ended missions validate output or final virtual-computer state rather than exact command text.
- Destructive commands remain confined to the virtual filesystem.
