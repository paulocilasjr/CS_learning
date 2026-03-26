# Star Wars Terminal Quest

`Star Wars Terminal Quest` is a terminal-only tutorial game for kids.
It teaches command-line basics through a Star Wars story instead of abstract drills.

Every mission gives:

- a short story moment
- one command to type
- the actual result of that command inside a safe practice shell

The game does not touch your real files. It runs in its own Rebel training environment.

## Start The Game

The simplest launcher is:

```sh
./start.sh
```

You can also run it directly with Python:

```sh
python3 main.py
```

## Campaign Structure

Version 1 includes a first Star Wars campaign with chapter-based lessons:

- `Briefing At Yavin`
- `Preparing The Falcon`
- `Plans For The Assault`

The missions connect commands to story actions such as:

- checking your location with `pwd`
- listing the Rebel base with `ls`
- revealing hidden intel with `ls -a`
- reading Leia's orders with `cat`
- creating folders with `mkdir`
- creating files with `touch`
- moving and copying mission files with `mv` and `cp`

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
- `reset` resets the current mission room.
- `exit` leaves the game.

## Prototype Files

The repository also includes a [star_wars_training](star_wars_training/) folder with the original static Star Wars exercise prototype. The runnable game uses its own virtual file system, so the command story can restart cleanly every time.
