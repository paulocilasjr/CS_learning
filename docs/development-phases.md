# Development Phases

The original ten-phase roadmap is implemented as follows:

| Phase | Delivered |
| ---: | --- |
| 1 | 53-skill curriculum registry, prerequisite validation, mission types, mastery model, curriculum and skill-tree documentation. |
| 2 | Virtual filesystem, parser, command registry, executor, safe terminal, and initial filesystem commands. |
| 3 | Data-driven task specifications, deterministic world snapshots, campaign builder, objectives, hints, transitions, and outcome validation. |
| 4 | Complete filesystem/navigation story foundation, including creation, movement, copying, deletion, and paths. |
| 5 | Persistent per-skill attempts, hints, mastery, independent successes, story state, review queue, and recommendations. |
| 6 | Search, partial reads, counts, sorting, wildcards, pipes, redirection, append redirection, conditional chaining, and Plan-and-Run. |
| 7 | Integrated Python missions for variables, data types, expressions, logic, loops, functions, collections, and algorithms. |
| 8 | Reproducible behavior bugs, line editing, expected-versus-actual reasoning, assertions, and simulation test missions. |
| 9 | Safe simulated Git status, diff, staging, commits, logs, branches, switching, and merging. |
| 10 | Five open-ended capstones validated by output and final state, including terminal, programming, debugging, and history work. |

The Terminal CS campaign contains 66 missions across 12 chapters. A separate Picture Logic campaign adds 12 gradual, click-based visual planning levels for younger learners. `tools/smoke_campaign.py` and `tools/smoke_picture_campaign.py` prove both complete golden paths through their real execution engines.
