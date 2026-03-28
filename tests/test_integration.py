"""Integration tests: full pipeline with all three policies."""

from __future__ import annotations

import pytest

from src.job import Job
from src.metrics import Metrics
from src.policies import FIFOPolicy, PriorityPolicy, SJFPolicy
from src.simulator import Simulator

JOBS = [
    Job("j1", submit_time=0, duration=4, priority=1),
    Job("j2", submit_time=0, duration=2, priority=3),
    Job("j3", submit_time=1, duration=3, priority=2),
]


@pytest.mark.parametrize(
    "policy", [FIFOPolicy(), PriorityPolicy(), SJFPolicy()]
)
def test_all_jobs_complete(policy: FIFOPolicy | PriorityPolicy | SJFPolicy) -> None:
    """Every policy must complete all jobs."""
    result = Simulator(JOBS, policy, total_resources=1).run()
    assert len(result.completed_jobs) == len(JOBS)
    assert result.makespan > 0


@pytest.mark.parametrize(
    "policy", [FIFOPolicy(), PriorityPolicy(), SJFPolicy()]
)
def test_metrics_valid(policy: FIFOPolicy | PriorityPolicy | SJFPolicy) -> None:
    """Metrics must be non-negative and utilization within [0, 1]."""
    result = Simulator(JOBS, policy, total_resources=1).run()
    m = Metrics.from_result(result, total_resources=1)

    assert m.makespan > 0
    assert m.average_waiting_time >= 0
    assert m.average_turnaround_time >= 0
    assert 0.0 <= m.utilization <= 1.0


def test_parallel_resources_reduces_makespan() -> None:
    """More resources should not increase makespan."""
    result_1 = Simulator(JOBS, FIFOPolicy(), total_resources=1).run()
    result_2 = Simulator(JOBS, FIFOPolicy(), total_resources=2).run()

    assert result_2.makespan <= result_1.makespan
