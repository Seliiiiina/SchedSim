"""Concrete scheduling policy implementations.

Available policies
------------------
FIFOPolicy
    First-In-First-Out: jobs run in the order they arrived.
SJFPolicy
    Shortest-Job-First: always picks the job with the smallest duration.
PriorityPolicy
    Priority scheduling: picks the job with the highest priority value.
    Ties are broken by submit_time (earlier arrival wins).
"""

from __future__ import annotations

from src.job import Job
from src.policy import BasePolicy


class FIFOPolicy(BasePolicy):
    """First-In-First-Out scheduling policy.

    Ties in ``submit_time`` are broken by ``job_id`` for determinism.
    """

    @property
    def name(self) -> str:
        return "FIFO"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return min(waiting_jobs, key=lambda j: (j.submit_time, j.job_id))


class SJFPolicy(BasePolicy):
    """Shortest-Job-First (non-preemptive) scheduling policy.

    Ties in ``duration`` are broken by ``submit_time`` (earlier arrival wins).
    """

    @property
    def name(self) -> str:
        return "SJF"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return min(waiting_jobs, key=lambda j: (j.duration, j.submit_time))


class PriorityPolicy(BasePolicy):
    """Priority-based scheduling policy (higher value = higher priority)."""

    @property
    def name(self) -> str:
        return "Priority"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return max(waiting_jobs, key=lambda j: (j.priority, -j.submit_time))
