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


@dataclass(frozen=True)
class PlanStepResult(Generic[ResultT]):
    step: PlanStep
    result: ResultT
    index: int
    total: int
    stopped: bool
    finished: bool


class PlanStepper(Generic[ResultT]):
    """Advance a fixed plan one operation at a time.

    Animated interfaces use ``advance`` between visual frames. ``PlanRunner``
    uses the same stepper synchronously, keeping both execution modes aligned.
    """

    def __init__(
        self,
        plan: ExecutionPlan,
        execute: Callable[[str], ResultT],
        has_error: Callable[[ResultT], bool],
        *,
        before_step: Callable[[PlanStep, int, int], None] | None = None,
    ) -> None:
        self.steps = tuple(plan.steps)
        self.execute = execute
        self.has_error = has_error
        self.before_step = before_step
        self.cursor = 0
        self.stopped_at: int | None = None

    @property
    def finished(self) -> bool:
        return self.stopped_at is not None or self.cursor >= len(self.steps)

    def advance(self) -> PlanStepResult[ResultT] | None:
        if self.finished:
            return None
        step = self.steps[self.cursor]
        index = self.cursor + 1
        total = len(self.steps)
        if self.before_step is not None:
            self.before_step(step, index, total)
        result = self.execute(step.raw)
        self.cursor = index
        stopped = self.has_error(result)
        if stopped:
            self.stopped_at = index
        return PlanStepResult(
            step=step,
            result=result,
            index=index,
            total=total,
            stopped=stopped,
            finished=self.finished,
        )


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
        stepper = PlanStepper(plan, execute, self.has_error, before_step=before_step)
        while not stepper.finished:
            progress = stepper.advance()
            assert progress is not None
            results.append(progress.result)
        return PlanRunResult(tuple(results), stopped_at=stepper.stopped_at)
