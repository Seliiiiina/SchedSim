"""Unit tests for the Metrics evaluation module."""

from __future__ import annotations

import pytest

from src.job import Job
from src.metrics import Metrics
from src.result import SimulationResult


def _make_job(
    job_id: str,
    submit_time: int,
    duration: int,
    start_time: int,
) -> Job:
    """Create a completed Job with start/end times already set."""
    j = Job(job_id, submit_time=submit_time, duration=duration)
    j.start_time = start_time
    j.end_time = start_time + duration
    return j


class TestMetricsFromResult:
    def test_basic_metrics(self) -> None:
        """Hand-calculated values for a simple two-job scenario."""
        # j1: submit=0, start=0, end=2 → wait=0, turnaround=2
        # j2: submit=0, start=2, end=5 → wait=2, turnaround=5
        j1 = _make_job("j1", submit_time=0, duration=2, start_time=0)
        j2 = _make_job("j2", submit_time=0, duration=3, start_time=2)
        result = SimulationResult(completed_jobs=[j1, j2], makespan=5)

        m = Metrics.from_result(result, total_resources=1)

        assert m.average_waiting_time == pytest.approx(1.0)
        assert m.average_turnaround_time == pytest.approx(3.5)
        assert m.makespan == 5
        assert m.utilization == pytest.approx(1.0)

    def test_utilization_with_multiple_resources(self) -> None:
        """Utilization should account for total_resources."""
        # 2 resources, makespan=5, total_work = 2 + 3 = 5
        # utilization = 5 / (5 * 2) = 0.5
        j1 = _make_job("j1", submit_time=0, duration=2, start_time=0)
        j2 = _make_job("j2", submit_time=0, duration=3, start_time=0)
        result = SimulationResult(completed_jobs=[j1, j2], makespan=5)

        m = Metrics.from_result(result, total_resources=2)

        assert m.utilization == pytest.approx(0.5)

    def test_utilization_full_parallel(self) -> None:
        """All resources fully occupied → utilization = 1.0."""
        # 3 resources, 3 jobs each duration=4, all start at 0
        # total_work = 12, makespan = 4, utilization = 12 / (4 * 3) = 1.0
        jobs = [
            _make_job(f"j{i}", submit_time=0, duration=4, start_time=0)
            for i in range(3)
        ]
        result = SimulationResult(completed_jobs=jobs, makespan=4)

        m = Metrics.from_result(result, total_resources=3)

        assert m.utilization == pytest.approx(1.0)

    def test_empty_completed_jobs(self) -> None:
        """Edge case: no completed jobs → zero averages, zero makespan."""
        result = SimulationResult(completed_jobs=[], makespan=0)
        m = Metrics.from_result(result, total_resources=1)

        assert m.average_waiting_time == 0.0
        assert m.average_turnaround_time == 0.0
        assert m.makespan == 0
        assert m.utilization == 0.0

    def test_metrics_is_frozen(self) -> None:
        """Metrics instances should be immutable."""
        j = _make_job("j1", submit_time=0, duration=1, start_time=0)
        result = SimulationResult(completed_jobs=[j], makespan=1)
        m = Metrics.from_result(result)

        with pytest.raises(AttributeError):
            m.makespan = 99  # type: ignore[misc]
