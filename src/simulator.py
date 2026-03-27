"""Core discrete-event simulation engine."""

from __future__ import annotations

from dataclasses import replace

from src.job import Job
from src.policy import BasePolicy
from src.result import SimulationResult


class Simulator:
    """Discrete-time job scheduling simulator.

    The simulator uses an event-driven clock that jumps to the next
    meaningful point in time (job arrival or job completion).  At each
    event the supplied :class:`BasePolicy` decides which waiting jobs
    to start on the available resources.

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
        self._all_jobs: list[Job] = list(jobs)

        # Mutable simulation state — (re)initialised by _reset().
        self._current_time: int = 0
        self._pending_jobs: list[Job] = []
        self._waiting_jobs: list[Job] = []
        self._running_jobs: list[Job] = []
        self._completed_jobs: list[Job] = []
        self._available_resources: int = total_resources

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> SimulationResult:
        """Execute the simulation and return the result.

        The main loop repeats until every job has completed:

        1. Admit newly arrived jobs into the waiting queue.
        2. Retire running jobs whose duration has elapsed.
        3. Ask the policy to fill available resource slots.
        4. Jump the clock to the next event.

        Returns:
            A :class:`SimulationResult` with all completed jobs and the
            makespan.
        """
        self._reset()

        while self._pending_jobs or self._waiting_jobs or self._running_jobs:
            self._add_arrived_jobs()
            self._complete_finished_jobs()
            self._start_jobs()

            if not (self._pending_jobs or self._waiting_jobs or self._running_jobs):
                break
            self._advance_time()

        return SimulationResult(
            completed_jobs=list(self._completed_jobs),
            makespan=self._current_time,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset(self) -> None:
        """Reset all mutable state so the simulator can be re-run."""
        self._current_time = 0
        self._pending_jobs = sorted(
            (replace(j, start_time=None, end_time=None) for j in self._all_jobs),
            key=lambda j: j.submit_time,
        )
        self._waiting_jobs = []
        self._running_jobs = []
        self._completed_jobs = []
        self._available_resources = self._total_resources

    def _add_arrived_jobs(self) -> None:
        """Move pending jobs whose ``submit_time <= current_time`` into the waiting queue."""
        still_pending: list[Job] = []
        for job in self._pending_jobs:
            if job.submit_time <= self._current_time:
                self._waiting_jobs.append(job)
            else:
                still_pending.append(job)
        self._pending_jobs = still_pending

    def _complete_finished_jobs(self) -> None:
        """Retire running jobs whose ``end_time <= current_time`` and free their resources."""
        still_running: list[Job] = []
        for job in self._running_jobs:
            if job.end_time is not None and job.end_time <= self._current_time:
                self._completed_jobs.append(job)
                self._available_resources += 1
            else:
                still_running.append(job)
        self._running_jobs = still_running

    def _start_jobs(self) -> None:
        """Repeatedly ask the policy to fill available resource slots with waiting jobs."""
        while self._available_resources > 0 and self._waiting_jobs:
            selected = self._policy.select_job(
                self._waiting_jobs, self._current_time,
            )
            if selected is None:
                break
            self._waiting_jobs.remove(selected)
            selected.start_time = self._current_time
            selected.end_time = self._current_time + selected.duration
            self._running_jobs.append(selected)
            self._available_resources -= 1

    def _advance_time(self) -> None:
        """Jump the clock forward to the next event.

        The next event is the earlier of:
        - the next pending job arrival (``submit_time``), or
        - the next running job completion (``end_time``).

        Raises:
            RuntimeError: If no future event exists (deadlock — the policy
                refuses to start any waiting job and nothing else can
                make progress).
        """
        candidates: list[int] = []

        if self._pending_jobs:
            # _pending_jobs is sorted by submit_time.
            candidates.append(self._pending_jobs[0].submit_time)

        if self._running_jobs:
            earliest_end = min(
                j.end_time for j in self._running_jobs
                if j.end_time is not None
            )
            candidates.append(earliest_end)

        if not candidates:
            raise RuntimeError(
                "Simulation deadlock: waiting jobs exist but no future event "
                "can make progress. This usually means the policy refuses to "
                "start any waiting job."
            )

        self._current_time = min(candidates)
