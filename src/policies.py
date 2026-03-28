"""Concrete scheduling policy implementations."""

from __future__ import annotations

from src.job import Job
from src.policy import BasePolicy


class FIFOPolicy(BasePolicy):
    """First-In-First-Out scheduling policy.

    Always selects the job that arrived earliest (smallest submit_time).
    Ties are broken by job_id for deterministic ordering.
    """

    @property
    def name(self) -> str:
        return "FIFO"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return min(waiting_jobs, key=lambda j: (j.submit_time, j.job_id))


class PriorityPolicy(BasePolicy):
    """Priority-based scheduling policy.

    Always selects the job with the highest priority value.
    Ties are broken by submit_time (earlier arrival wins), then by job_id.
    """

    @property
    def name(self) -> str:
        return "Priority"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return max(
            waiting_jobs,
            key=lambda j: (j.priority, -j.submit_time, j.job_id),
        )


class SJFPolicy(BasePolicy):
    """Shortest-Job-First (non-preemptive) scheduling policy.

    Always selects the job with the smallest duration.
    Ties are broken by submit_time (earlier arrival wins), then by job_id.
    """

    @property
    def name(self) -> str:
        return "SJF"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return min(waiting_jobs, key=lambda j: (j.duration, j.submit_time, j.job_id))