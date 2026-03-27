"""Container for simulation output."""

from __future__ import annotations

from dataclasses import dataclass

from src.job import Job


@dataclass(frozen=True)
class SimulationResult:
    """Immutable snapshot of a completed simulation run.

    Attributes:
        completed_jobs: All jobs that finished during the simulation,
            ordered by completion time.
        makespan: Total time from the start of the simulation (time 0)
            to the completion of the last job.
    """

    completed_jobs: list[Job]
    makespan: int

    @property
    def average_turnaround_time(self) -> float:
        """Mean turnaround time across all completed jobs."""
        if not self.completed_jobs:
            return 0.0
        total = sum(j.turnaround_time for j in self.completed_jobs)  # type: ignore[arg-type]
        return total / len(self.completed_jobs)

    @property
    def average_waiting_time(self) -> float:
        """Mean waiting time across all completed jobs."""
        if not self.completed_jobs:
            return 0.0
        total = sum(j.waiting_time for j in self.completed_jobs)  # type: ignore[arg-type]
        return total / len(self.completed_jobs)
