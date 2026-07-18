from __future__ import annotations

from terminal_quest.state import LearningState


class ReviewEngine:
    """Ranks practiced skills that would benefit most from another mission."""

    def recommend(self, state: LearningState, *, limit: int = 3) -> list[str]:
        ranked = sorted(
            state.skills.items(),
            key=lambda item: (
                item[1].mastery,
                item[1].independent_successes,
                -item[1].hints_used,
                item[1].last_practiced,
                item[0],
            ),
        )
        return [key for key, _progress in ranked[:limit]]
