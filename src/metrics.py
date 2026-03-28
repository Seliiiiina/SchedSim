"""Evaluation metrics for simulation results."""

from __future__ import annotations

from dataclasses import dataclass

from src.result import SimulationResult


@dataclass(frozen=True)
class Metrics:
    """Computed evaluation metrics for a single simulation run.

    Attributes:
        average_waiting_time: Mean time jobs spent waiting before execution.
        average_turnaround_time: Mean time from submission to completion.
        makespan: Total time from simulation start to last job completion.
        utilization: Fraction of resource-time actually spent running jobs
            (0.0–1.0).  Requires ``total_resources`` to be passed to
            :meth:`from_result`.
    """

    average_waiting_time: float
    average_turnaround_time: float
    makespan: int
    utilization: float

    @classmethod
    def from_result(
        cls,
        result: SimulationResult,
        total_resources: int = 1,
    ) -> Metrics:
        """Compute all metrics from a completed SimulationResult.

        Args:
            result: The completed simulation result.
            total_resources: Number of resource slots used in the simulation.
                Used to compute utilization. Defaults to 1.

        Returns:
            A :class:`Metrics` instance with all computed values.
        """
        total_work = sum(j.duration for j in result.completed_jobs)
        utilization = (
            total_work / (result.makespan * total_resources)
            if result.makespan > 0
            else 0.0
        )

        return cls(
            average_waiting_time=result.average_waiting_time,
            average_turnaround_time=result.average_turnaround_time,
            makespan=result.makespan,
            utilization=utilization,
        )