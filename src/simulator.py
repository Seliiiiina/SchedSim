"""Core discrete-event simulation engine."""

from __future__ import annotations

from src.job import Job
from src.policy import BasePolicy
from src.result import SimulationResult


class Simulator:
    """Discrete-time job scheduling simulator.

    The simulator advances a clock one tick at a time, uses the supplied
    :class:`BasePolicy` to decide which waiting jobs to start, and tracks
    resource usage until all jobs have completed.

    Args:
        jobs: The workload — a list of jobs to schedule.
        policy: The scheduling policy that selects which job runs next.
        total_resources: Number of resource slots available.  Each running
            job occupies exactly one slot.

    Raises:
        ValueError: If *jobs* is empty or *total_resources* < 1.
    """

    def __init__(
        self,
        jobs: list[Job],
        policy: BasePolicy,
        total_resources: int = 1,
    ) -> None:
        if not jobs:
            raise ValueError("jobs must not be empty")
        if total_resources < 1:
            raise ValueError(
                f"total_resources must be >= 1, got {total_resources}"
            )

        self._policy = policy
        self._total_resources = total_resources

        # Simulation state — initialised at the start of each run().
        self._current_time: int = 0
        self._waiting_jobs: list[Job] = []
        self._running_jobs: list[Job] = []
        self._completed_jobs: list[Job] = []
        self._available_resources: int = total_resources

        # Keep an immutable copy of the original workload so that
        # the simulator can be re-run without external side effects.
        self._all_jobs: list[Job] = list(jobs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> SimulationResult:
        """Execute the simulation and return the result.

        Returns:
            A :class:`SimulationResult` containing all completed jobs
            and aggregate metrics.

        .. note:: Full implementation will be added in a later iteration.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Internal helpers (to be implemented)
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset all mutable state so the simulator can be re-run."""
        raise NotImplementedError

    def _advance_time(self) -> None:
        """Move the clock forward by one tick and update job states."""
        raise NotImplementedError

    def _admit_jobs(self) -> None:
        """Move newly submitted jobs into the waiting queue."""
        raise NotImplementedError

    def _schedule_jobs(self) -> None:
        """Use the policy to start waiting jobs on available resources."""
        raise NotImplementedError

    def _complete_jobs(self) -> None:
        """Move finished jobs from running to completed and free resources."""
        raise NotImplementedError
