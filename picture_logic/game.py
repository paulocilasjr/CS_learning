from __future__ import annotations

import os
import sys
import time
from collections.abc import Callable

from game_core.persistence import ProgressStore
from game_core.planning import ExecutionPlan, PlanStep
from picture_logic.engine import PictureStepResult, PictureWorld, picture_for_action, run_picture_plan
from picture_logic.missions import ACTION_CARDS, PictureMission, build_picture_missions
from picture_logic.settings import PICTURE_SAVE_FILE
from picture_logic.web_app import launch_picture_browser


PICTURE_STEP_DELAY_SECONDS = 0.6


class PictureLogicGame:
    """Picture-card planning adventure for pre-reading and early-reading learners."""

    def __init__(
        self,
        *,
        save_enabled: bool = True,
        start_level: int | None = None,
        reset_progress: bool = False,
        input_fn: Callable[[str], str] | None = None,
        output_fn: Callable[[str], None] | None = None,
    ) -> None:
        self.missions = build_picture_missions()
        self.start_level = start_level
        self.current_index = max(0, (start_level - 1) if start_level else 0)
        self.stars = 0
        self.save_enabled = save_enabled
        self.reset_progress = reset_progress
        self.progress_store = ProgressStore(PICTURE_SAVE_FILE)
        self.plan = ExecutionPlan()
        self.input = input_fn or input
        self.output = output_fn or print
        self.animate = output_fn is None and sys.stdout.isatty()
        self.text_mode = input_fn is not None or output_fn is not None

    def run(self) -> None:
        force_text = os.environ.get("PICTURE_LOGIC_TEXT_MODE", "0").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if not self.text_mode and not force_text:
            self.output("Opening the click-and-play Picture Logic Game in your browser…")
            if launch_picture_browser(
                save_enabled=self.save_enabled,
                start_level=self.start_level,
                reset_progress=self.reset_progress,
            ):
                return
            self.output("A browser could not open, so the simple text fallback will start.")

        self._run_text_game()

    def _run_text_game(self) -> None:
        self._handle_existing_save()
        self._show_welcome()
        while self.current_index < len(self.missions):
            if not self._play_mission(self.missions[self.current_index]):
                return
        self._finish_game()

    def _play_mission(self, mission: PictureMission) -> bool:
        self.plan.clear()
        for action in mission.starter_plan:
            self.plan.add(action, source="picture")
        failed_runs = 0
        hint_index = 0
        self._show_mission(mission)

        while True:
            try:
                choice = self.input("picture> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                self._save_progress()
                self._show_exit_message()
                return False

            if not choice:
                continue
            if choice in {"exit", "q", "quit"}:
                self._save_progress()
                self._show_exit_message()
                return False
            if choice in {"hint", "h"}:
                hint = mission.hints[min(hint_index, len(mission.hints) - 1)]
                hint_index += 1
                self.output(f"💡 {hint}")
                continue
            if choice in {"clear", "c"}:
                self.plan.clear()
                self.output("🧹 The plan is empty. Choose new cards.")
                self._show_cards(mission)
                continue
            if choice in {"undo", "u"}:
                removed = self.plan.undo()
                if removed is None:
                    self.output("The plan is already empty.")
                else:
                    self.output(f"↶ Removed {picture_for_action(removed.raw)}")
                self._show_plan()
                continue
            if choice in {"show", "s", "plan"}:
                self._show_plan()
                continue
            if choice in {"repeat", "board", "b"}:
                self._show_mission(mission)
                continue
            if choice in {"run", "r", "go"}:
                if not self.plan.steps:
                    self.output("Choose at least one picture card before running the plan.")
                    continue
                result = run_picture_plan(
                    mission,
                    self.plan,
                    before_step=self._before_step,
                    after_step=self._after_step,
                )
                if result.complete:
                    self.stars += 1
                    self.current_index += 1
                    tries = failed_runs + 1
                    self.output(f"\n🎉 Mission complete! You earned a thinking badge in {tries} tries.")
                    self._save_progress()
                    return True
                failed_runs += 1
                if result.run.completed:
                    self.output("\nThe plan finished, but BB-8 is not at the flag with every star yet.")
                else:
                    latest = result.run.latest
                    self.output(f"\n⚠️ {latest.error if latest else 'The plan paused.'}")
                self.output("Change the picture plan, then run it again.")
                continue

            if self._add_cards(choice, mission):
                self._show_plan()
            else:
                self.output("Choose card numbers, or type run, undo, clear, hint, board, or exit.")

    def _add_cards(self, choice: str, mission: PictureMission) -> bool:
        tokens = choice.replace(",", " ").split()
        if not tokens or any(not token.isdigit() for token in tokens):
            return False
        for token in tokens:
            index = int(token) - 1
            if not 0 <= index < len(mission.cards):
                return False
        for token in tokens:
            action = mission.cards[int(token) - 1]
            self.plan.add(action, source="picture")
        return True

    def _show_welcome(self) -> None:
        self.output("\n🌌 STAR WARS PICTURE PLAN ADVENTURE 🌌")
        self.output("LOOK 👀  →  PLAN 🧩  →  TRY ▶  →  CHANGE 🔧")
        self.output("Every try teaches your brain something useful.")
        self.output("No computer commands are needed in this game.\n")

    def _show_mission(self, mission: PictureMission) -> None:
        self.output(f"\n{'═' * 48}")
        self.output(f"LEVEL {mission.number}/{len(self.missions)} — {mission.name}")
        self.output(f"📖 {mission.story}")
        self.output(f"🎯 {mission.instruction}\n")
        self.output(PictureWorld(mission).render())
        self.output("\n➡️⬆️⬇️⬅️ = BB-8   🏁 = finish   ⭐ = collect   🪨 = avoid")
        self._show_cards(mission)

    def _show_cards(self, mission: PictureMission) -> None:
        self.output("\nPICTURE CARDS")
        for index, action in enumerate(mission.cards, start=1):
            card = ACTION_CARDS[action]
            self.output(f"  {index}. {card.picture}  {card.name}")
        self.output("Choose card numbers, then type run. A grown-up can help with typing.")

    def _show_plan(self) -> None:
        if not self.plan.steps:
            self.output("PLAN: [ empty ]")
            return
        pictures = [ACTION_CARDS[step.raw].picture for step in self.plan.steps]
        self.output(f"PLAN: {'  ➜  '.join(pictures)}")

    def _before_step(self, step: PlanStep, index: int, total: int) -> None:
        self.output(f"\n▶ Step {index}/{total}: {picture_for_action(step.raw)}")

    def _after_step(self, result: PictureStepResult) -> None:
        self.output(result.board)
        self.output(f"   {result.message}")
        animation_setting = os.environ.get("PICTURE_LOGIC_ANIMATION", "1").lower()
        if self.animate and animation_setting not in {"0", "false", "off"}:
            time.sleep(PICTURE_STEP_DELAY_SECONDS)

    def _show_exit_message(self) -> None:
        if self.save_enabled:
            self.output("Progress saved. See you next time! 👋")
        else:
            self.output("See you next time! 👋")

    def _handle_existing_save(self) -> None:
        if not self.save_enabled:
            return
        if self.reset_progress:
            self.progress_store.clear()
            return
        if self.current_index > 0:
            return
        saved = self.progress_store.load()
        if saved is None:
            return
        saved_index = int(saved.get("current_index", 0))
        if not 0 < saved_index < len(self.missions):
            return
        self.output(f"A picture-game save was found at level {saved_index + 1}.")
        self.output("1. Continue    2. Start again")
        while True:
            choice = self.input("choose> ").strip().lower()
            if choice in {"1", "continue", "resume"}:
                self.current_index = saved_index
                self.stars = int(saved.get("badges", saved.get("stars", 0)))
                return
            if choice in {"2", "restart"}:
                self.progress_store.clear()
                return
            self.output("Choose 1 or 2.")

    def _save_progress(self) -> None:
        if self.save_enabled:
            self.progress_store.save(
                {"version": 2, "current_index": self.current_index, "badges": self.stars}
            )

    def _finish_game(self) -> None:
        self._save_progress()
        self.output("\n🏆 PICTURE ADVENTURE COMPLETE! 🏆")
        self.output(f"BB-8 completed every picture plan. Thinking badges: {self.stars}")
