# Star Wars Command Adventure

This repository is now a small command-line story set in the Star Wars galaxy.
Each exercise gives:

- a reason to use the command
- the command to type
- the result the learner should see

The goal is to connect the command with a real action in the story instead of memorizing random words.

The missions are sequential, so each one starts where the previous one ended.
Missions 7 to 10 modify the training files on purpose.

## Story Setup

The Rebellion is preparing a mission against the Death Star. You are the new helper inside the Rebel base, and Han Solo, Leia Organa, Luke Skywalker, Chewbacca, and R2-D2 need your help.

Start in the root of this project:

```sh
cd /Users/4475918/Projects/personal/CS_learning
```

If you want to repeat the write commands more than once, practice on a copy of `star_wars_training` first.

## The Practice Galaxy

```text
star_wars_training/
└── rebel_base/
    ├── archive/
    │   ├── death_star_plans.txt
    │   └── rebel_code.txt
    └── millennium_falcon/
        ├── .escape_routes.txt
        ├── cargo/
        │   ├── coaxium_crate.txt
        │   ├── med_kit.txt
        │   └── tool_box.txt
        ├── crew/
        │   ├── chewbacca.txt
        │   ├── han_solo.txt
        │   ├── leia_organa.txt
        │   ├── luke_skywalker.txt
        │   └── r2_d2.txt
        ├── faulty_hyperdrive_note.txt
        ├── mission_briefing.txt
        └── training_bay/
            └── repair_log.txt
```

## Mission 1: Where Are You?

Leia hands you the first order: before helping the Rebellion, you must know where you are standing in the galaxy.

Use:

```sh
pwd
```

Expected result:

```text
/Users/4475918/Projects/personal/CS_learning
```

Meaning: `pwd` shows your current location.

## Mission 2: What Is In The Base?

Han Solo wants a fast list of what is around you at the project root.

Use:

```sh
ls
```

Expected result:

```text
LICENSE
README.md
star_wars_training
```

Meaning: `ls` lists what is present in the current directory.

## Mission 3: Go To The Millennium Falcon Crew Room

Chewbacca waves at you from the ship. You need to move through the Rebel base until you reach the crew room inside the Millennium Falcon.

Use:

```sh
cd star_wars_training/rebel_base/millennium_falcon/crew
```

Then confirm with:

```sh
pwd
```

Expected result:

```text
/Users/4475918/Projects/personal/CS_learning/star_wars_training/rebel_base/millennium_falcon/crew
```

Meaning: `cd` changes directory.

## Mission 4: Who Is On Board?

Han Solo is ready for departure, but first he wants to see who is already on board.

Use:

```sh
ls
```

Expected result:

```text
chewbacca.txt
han_solo.txt
leia_organa.txt
luke_skywalker.txt
r2_d2.txt
```

Meaning: `ls` can also show the names of people or items stored as files.

## Mission 5: Find Hidden Rebel Information

R2-D2 beeps loudly. He has detected a hidden file near the cockpit. Normal `ls` will not show it, so you must reveal everything.

Use:

```sh
cd ..
ls -a
```

Expected result:

```text
.
..
.escape_routes.txt
cargo
crew
faulty_hyperdrive_note.txt
mission_briefing.txt
training_bay
```

Meaning: `ls -a` shows all files, even hidden ones that begin with a dot.

## Mission 6: Read Leia's Orders

The crew is waiting. Leia needs you to read the mission briefing out loud.

Use:

```sh
cat mission_briefing.txt
```

Expected result:

```text
Mission Briefing
---------------
1. Check the crew before takeoff.
2. Study the Death Star plans from the archive.
3. Prepare a rescue team in the training bay.
4. Keep the Falcon ready for a hyperspace jump.
```

Meaning: `cat` prints the content of a file.

## Mission 7: Build A Rescue Team Folder

Luke says the rescue team needs its own place to organize. You must create a new folder inside the training bay.

Use:

```sh
mkdir training_bay/rescue_team
```

Check the result with:

```sh
ls training_bay
```

Expected result:

```text
repair_log.txt
rescue_team
```

Meaning: `mkdir` creates a new directory.

## Mission 8: Add Obi-Wan To The Team List

The rescue team needs its first member. Create a file for Obi-Wan Kenobi.

Use:

```sh
touch training_bay/rescue_team/obi_wan.txt
```

Check the result with:

```sh
ls training_bay/rescue_team
```

Expected result:

```text
obi_wan.txt
```

Meaning: `touch` creates a file.

## Mission 9: Copy The Death Star Plans

Leia wants a study copy of the Death Star plans inside the rescue team folder, but the original must stay in the archive.

Use:

```sh
cp ../archive/death_star_plans.txt training_bay/rescue_team/death_star_plans.txt
```

Check the result with:

```sh
ls training_bay/rescue_team
```

Expected result:

```text
death_star_plans.txt
obi_wan.txt
```

Meaning: `cp` copies a file from one place to another.

## Mission 10: Move The Faulty Hyperdrive Note

Chewbacca does not want the faulty hyperdrive note left in the middle of the Falcon. Move it into the training bay so the mechanics can inspect it.

Use:

```sh
mv faulty_hyperdrive_note.txt training_bay/faulty_hyperdrive_note.txt
```

Check the result with:

```sh
ls training_bay
```

Expected result:

```text
faulty_hyperdrive_note.txt
repair_log.txt
rescue_team
```

Meaning: `mv` moves a file from one place to another.

## Why This Version Works Better

Instead of remembering:

- `ls = list`
- `cat = show file`
- `mkdir = make directory`

the learner connects each command to a moment in the story:

- `ls` becomes "Who is on board?"
- `cat` becomes "Read Leia's orders."
- `mkdir` becomes "Build the rescue team room."
- `cp` becomes "Make a copy of the Death Star plans."
- `mv` becomes "Move the broken note to the mechanics."

That makes the command easier to remember because it has a purpose, an action, and a visible result.
