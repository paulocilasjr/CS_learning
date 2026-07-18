# Skill Tree

The canonical, machine-readable dependency graph is `terminal_quest/curriculum.py`. This document explains its structure for curriculum authors.

## Foundation and virtual terminal

```text
pwd

ls
├── cat
├── hidden files
├── targeted listing
├── relative paths
│   ├── nested paths
│   ├── cd
│   │   ├── parent paths
│   │   │   └── cp
│   │   └── absolute paths
│   └── mv
├── find
└── tree

cat + mkdir ──> touch
touch + relative paths ──> mv
```

The first playable campaign covers this branch. Some nodes are concepts rather than literal commands because a child must learn the mental model as well as syntax.

## Search and composition

```text
cat + find ──> grep
cat ─────────> head
cat ─────────> tail
cat ─────────> wc

echo + touch ──> redirection ──> append redirection
grep + wc ─────> pipes ────────> command chaining
                                      └── plan and run
ls + paths ────> wildcards
```

This branch should culminate in missions where the player discovers, filters, counts, saves intelligence, and plans a sequence before running it. Plan-and-Run is the same mental structure a picture-block interface can teach earlier and Python code can formalize later.

## Programming

```text
variables ──> data types ──> expressions ──> comparisons ──> conditions
                                                      conditions ──> Boolean logic

variables + data types ──> lists
conditions + lists ──────> loops
variables + conditions + loops ──> functions
functions ──> parameters
functions + expressions ──> return values
lists ──> mappings
```

Programming missions should change visible story state. The player is no longer issuing each action directly; they are defining data and rules that control later actions.

## Algorithms, debugging, and testing

```text
loops + lists + functions ──> search algorithms
comparisons + loops + lists ──> sorting algorithms
functions + conditions ──────> debugging
debugging + return values ───> testing
```

Debug missions explicitly contrast expected and actual behavior. Tests become automated questions the Rebel simulator can ask before trusting a program in a real mission.

## Version control

```text
git status
  └── git diff
      └── git add
          └── git commit
              └── git log
                  └── git branch
                      └── git merge
```

The story should establish why recoverable history and parallel work matter before expecting the player to memorize Git syntax.

## Authoring rules

When adding a skill:

1. Give it a stable, story-neutral key.
2. Place it in a category and delivery phase.
3. List only genuine prerequisites—skills a learner must understand first.
4. Add an `INTRODUCE` mission after those prerequisites.
5. Schedule later `PRACTICE`, `RECALL`, `TRANSFER`, and `COMBINE` evidence.
6. Run `python3 tools/validate_curriculum.py` and the tests.

Dependencies describe learning order, not every concept that might be useful. Keeping the graph minimal makes sequencing constraints meaningful and avoids blocking good mission design.
