"""Data model for a schedulable job."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Job:
    """A unit of work to be scheduled and executed by the simulator.

    Each job has a fixed submission time, processing duration, and priority.
    The simulator fills in ``start_time`` and ``end_time`` as the job
    progresses through its lifecycle:  waiting → running → completed.

    Attributes:
        job_id: Unique identifier for this job.
        submit_time: The time step at which the job enters the system.
            Must be >= 0.
        duration: How many time steps the job needs to run.
            Must be > 0.
        priority: Scheduling priority (higher value = higher priority).
        start_time: Set by the simulator when the job begins execution.
        end_time: Set by the simulator when the job finishes execution.
    """

    job_id: str
    submit_time: int
    duration: int
    priority: int = 0
    start_time: int | None = field(default=None, repr=False)
    end_time: int | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.job_id:
            raise ValueError("job_id must be a non-empty string")
        if self.submit_time < 0:
            raise ValueError(
                f"submit_time must be >= 0, got {self.submit_time}"
            )
        if self.duration <= 0:
            raise ValueError(
                f"duration must be > 0, got {self.duration}"
            )

    @property
    def turnaround_time(self) -> int | None:
        """Total time from submission to completion, or None if not yet completed."""
        if self.end_time is None:
            return None
        return self.end_time - self.submit_time

    @property
    def waiting_time(self) -> int | None:
        """Time spent waiting before execution started, or None if not yet started."""
        if self.start_time is None:
            return None
        return self.start_time - self.submit_time
