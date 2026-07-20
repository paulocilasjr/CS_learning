# Picture Logic Game

The Picture Logic Game is a separate twelve-level, click-based browser adventure designed for approximately five-year-old learners. It shares the Python Plan-and-Run engine with the Terminal CS Game but has its own curriculum, visual world, interaction loop, and progress file. The local browser interface requires no Internet connection.

## Child experience principles

- **No typing:** every learning action is a large, labeled picture button.
- **One idea at a time:** the first five levels use plans of three steps or fewer.
- **Visible causality:** the active plan card is highlighted and the board changes after each step.
- **Productive mistakes:** obstacles pause the plan and produce one specific question about what to change.
- **Perseverance without penalty:** hints and repeated tries never reduce the thinking badge earned for completion.
- **Low reading burden:** instructions are short, icons carry meaning, and Read to Me uses browser speech when available.
- **Consistent reasoning loop:** every level reinforces `LOOK → PLAN → TRY → CHANGE`.

## Learning progression

1. Choose one movement and observe its consequence.
2. Put two matching movements in order.
3. Turn right before moving.
4. Turn left before moving.
5. Collect an object before finishing.
6. Plan around an obstacle.
7. Combine collection, turning, and movement.
8. Try a deliberately broken plan, notice the collision, and repair it.
9. Replace repeated movements with a GO 2 card.
10. Use a simple conditional CHECK card.
11. Break a route into smaller parts and combine them.
12. Apply the full reasoning loop in a rescue plan.

The player never types a shell command. Clicking a card adds it to the visual plan. Try My Plan creates a fresh deterministic world in Python and advances the shared PlanStepper between animation frames. The board appears after every step so the child can connect each selected picture to its consequence.

## Controls

- Picture cards add actions.
- Plan cards remove a selected action.
- Undo removes the latest action.
- Clear creates an empty plan.
- Try My Plan executes and animates the plan.
- Give Me a Clue offers progressive hints.
- Read to Me speaks the mission aloud.
- Leave saves progress and stops the private local game session.

## Independent progress

Picture progress and thinking badges are stored in `.star_wars_picture_logic_progress.json`. Terminal progress remains in `.star_wars_terminal_quest_progress.json`. Both files are optional when the launcher is run with `--no-save`.

If a browser cannot open, the Python launcher retains a simpler text fallback for accessibility and constrained environments. Set `PICTURE_LOGIC_TEXT_MODE=1` to select that fallback explicitly.
