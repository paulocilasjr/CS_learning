# Picture Logic Game

The Picture Logic Game is a separate ten-level adventure for younger learners. It shares the Plan-and-Run engine with the Terminal CS Game but has its own missions, visual world, interaction loop, and progress file.

## Learning progression

1. Choose one action and observe its consequence.
2. Put repeated actions in order.
3. Turn toward a goal.
4. Plan around an obstacle.
5. Collect an object before finishing.
6. Combine collection, turns, and movement.
7. Debug a route after an obstacle stops it.
8. Use a repeat card.
9. Use a conditional collection card.
10. Combine the earlier ideas in a rescue plan.

The player never types a shell command. Numbered choices select large emoji cards such as move, turn, collect, repeat, and check. `run` executes the complete visual plan from the mission's starting state. The board appears after every step so the child can connect each selected picture to its consequence.

## Controls

- Number keys add the displayed picture cards. Multiple numbers can be entered together, such as `1 1 2`.
- `run` executes the plan.
- `show` displays the current plan.
- `undo` removes the last card.
- `clear` removes every card.
- `hint` gives one mission clue.
- `board` repeats the mission and starting board.
- `exit` saves picture-game progress and leaves.

## Independent progress

Picture progress is stored in `.star_wars_picture_logic_progress.json`. Terminal progress remains in `.star_wars_terminal_quest_progress.json`. Both files are optional when the launcher is run with `--no-save`.
