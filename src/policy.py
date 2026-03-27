"""Abstract interface for scheduling policies."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.job import Job


class BasePolicy(ABC):
    """Interface that all scheduling policies must implement.

    A policy decides **which waiting job** should be started next, given the
    current simulation time and the set of jobs that are ready to run.

    Subclasses must override :meth:`select_job`.  They may carry internal
    state (e.g. for round-robin tracking) but should not mutate the
    jobs or the list that is passed in.
    """

    @abstractmethod
    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        """Choose the next job to execute.

        Args:
            waiting_jobs: Jobs whose ``submit_time <= current_time`` and
                that have not yet started.  Guaranteed to be non-empty
                when called by the simulator.
            current_time: The current simulation time step.

        Returns:
            The selected :class:`Job`, which must be an element of
            waiting_jobs, or ``None`` to indicate that no job should
            be started at this time.
        """
