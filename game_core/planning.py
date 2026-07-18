from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar


ResultT = TypeVar("ResultT")


@dataclass(frozen=True)
class PlanStep:
    """One operation selected before execution.

    ``raw`` is deliberately interface-neutral: the terminal game stores a shell
    command key while the picture game stores an action-card key.
    """

    raw: str
    source: str = "text"


@dataclass
class ExecutionPlan:
    steps: list[PlanStep] = field(default_factory=list)

    def add(self, raw: str, *, source: str = "text") -> PlanStep:
        cleaned = raw.strip()
        if not cleaned:
            raise ValueError("A plan step needs an operation to run.")
        step = PlanStep(raw=cleaned, source=source)
        self.steps.append(step)
        return step

    def undo(self) -> PlanStep | None:
        return self.steps.pop() if self.steps else None

    def clear(self) -> None:
        self.steps.clear()

    def describe(self) -> str:
        if not self.steps:
            return "Plan is empty."
        lines = ["Plan steps:"]
        for index, step in enumerate(self.steps, start=1):
            lines.append(f"  {index}. {step.raw}")
        return "\n".join(lines)


@dataclass(frozen=True)
class PlanRunResult(Generic[ResultT]):
    step_results: tuple[ResultT, ...]
    stopped_at: int | None = None

    @property
    def completed(self) -> bool:
        return self.stopped_at is None

    @property
    def latest(self) -> ResultT | None:
        return self.step_results[-1] if self.step_results else None


class PlanRunner(Generic[ResultT]):
    def __init__(self, has_error: Callable[[ResultT], bool]) -> None:
        self.has_error = has_error

    def run(
        self,
        plan: ExecutionPlan,
        execute: Callable[[str], ResultT],
        *,
        before_step: Callable[[PlanStep, int, int], None] | None = None,
    ) -> PlanRunResult[ResultT]:
        results: list[ResultT] = []
        total = len(plan.steps)
        for index, step in enumerate(plan.steps, start=1):
            if before_step is not None:
                before_step(step, index, total)
            result = execute(step.raw)
            results.append(result)
            if self.has_error(result):
                return PlanRunResult(tuple(results), stopped_at=index)
        return PlanRunResult(tuple(results))
