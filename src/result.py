"""Container for simulation output."""

from __future__ import annotations

from dataclasses import dataclass

from src.job import Job


@dataclass(frozen=True)
class SimulationResult:
    """Immutable snapshot of a completed simulation run.

    Every :class:`Job` in completed_jobs must have both ``start_time``
    and ``end_time`` set; this is validated at construction time.

    Attributes:
        completed_jobs: All jobs that finished during the simulation,
            ordered by completion time.
        makespan: Total time from the start of the simulation (time 0)
            to the completion of the last job.
    """

    completed_jobs: list[Job]
    makespan: int

    def __post_init__(self) -> None:
        for job in self.completed_jobs:
            if job.start_time is None or job.end_time is None:
                raise ValueError(
                    f"Job {job.job_id!r} in completed_jobs is missing "
                    f"start_time or end_time"
                )

    @property
    def average_turnaround_time(self) -> float:
        """Mean turnaround time across all completed jobs."""
        if not self.completed_jobs:
            return 0.0
        total = 0
        for job in self.completed_jobs:
            tt = job.turnaround_time
            assert tt is not None  # guaranteed by __post_init__
            total += tt
        return total / len(self.completed_jobs)

    @property
    def average_waiting_time(self) -> float:
        """Mean waiting time across all completed jobs."""
        if not self.completed_jobs:
            return 0.0
        total = 0
        for job in self.completed_jobs:
            wt = job.waiting_time
            assert wt is not None  # guaranteed by __post_init__
            total += wt
        return total / len(self.completed_jobs)
