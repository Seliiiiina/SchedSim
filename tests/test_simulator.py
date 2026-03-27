"""Tests for the core simulation engine."""

from __future__ import annotations

import pytest

from src.job import Job
from src.policy import BasePolicy
from src.result import SimulationResult
from src.simulator import Simulator


# ------------------------------------------------------------------
# Test-only policy: always picks the first job in waiting_jobs (FIFO-like)
# ------------------------------------------------------------------

class DummyPolicy(BasePolicy):
    """Minimal policy that selects the first waiting job."""

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return waiting_jobs[0]


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture()
def policy() -> DummyPolicy:
    return DummyPolicy()


# ------------------------------------------------------------------
# Job validation
# ------------------------------------------------------------------

class TestJobValidation:
    def test_negative_submit_time(self) -> None:
        with pytest.raises(ValueError, match="submit_time"):
            Job("j", submit_time=-1, duration=1)

    def test_zero_duration(self) -> None:
        with pytest.raises(ValueError, match="duration"):
            Job("j", submit_time=0, duration=0)

    def test_negative_duration(self) -> None:
        with pytest.raises(ValueError, match="duration"):
            Job("j", submit_time=0, duration=-5)


# ------------------------------------------------------------------
# Simulator input validation
# ------------------------------------------------------------------

class TestSimulatorValidation:
    def test_empty_jobs(self, policy: DummyPolicy) -> None:
        with pytest.raises(ValueError, match="jobs must not be empty"):
            Simulator([], policy)

    def test_zero_resources(self, policy: DummyPolicy) -> None:
        jobs = [Job("j1", submit_time=0, duration=1)]
        with pytest.raises(ValueError, match="total_resources"):
            Simulator(jobs, policy, total_resources=0)

    def test_negative_resources(self, policy: DummyPolicy) -> None:
        jobs = [Job("j1", submit_time=0, duration=1)]
        with pytest.raises(ValueError, match="total_resources"):
            Simulator(jobs, policy, total_resources=-1)


# ------------------------------------------------------------------
# Core simulation behaviour
# ------------------------------------------------------------------

class TestSimulatorCore:
    def test_all_jobs_complete(self, policy: DummyPolicy) -> None:
        """Every input job must appear in the result's completed list."""
        jobs = [
            Job("j1", submit_time=0, duration=3),
            Job("j2", submit_time=1, duration=2),
            Job("j3", submit_time=2, duration=1),
        ]
        result = Simulator(jobs, policy, total_resources=1).run()

        completed_ids = {j.job_id for j in result.completed_jobs}
        assert completed_ids == {"j1", "j2", "j3"}

    def test_simple_execution_order(self, policy: DummyPolicy) -> None:
        """With 1 resource and FIFO, jobs run in arrival order."""
        jobs = [
            Job("j1", submit_time=0, duration=2),
            Job("j2", submit_time=0, duration=3),
        ]
        result = Simulator(jobs, policy, total_resources=1).run()

        # j1 submitted first in the list → started first by DummyPolicy
        j1 = next(j for j in result.completed_jobs if j.job_id == "j1")
        j2 = next(j for j in result.completed_jobs if j.job_id == "j2")

        assert j1.start_time == 0
        assert j2.start_time == 2  # starts after j1 finishes
        assert j1.end_time <= j2.start_time  # type: ignore[operator]

    def test_job_start_and_end_times(self, policy: DummyPolicy) -> None:
        """start_time and end_time must be set correctly on every job."""
        jobs = [
            Job("j1", submit_time=0, duration=4),
            Job("j2", submit_time=1, duration=2),
        ]
        result = Simulator(jobs, policy, total_resources=1).run()

        j1 = next(j for j in result.completed_jobs if j.job_id == "j1")
        j2 = next(j for j in result.completed_jobs if j.job_id == "j2")

        # j1: starts at 0, duration 4 → ends at 4
        assert j1.start_time == 0
        assert j1.end_time == 4

        # j2: arrives at 1, but resource busy until 4 → starts at 4, ends at 6
        assert j2.start_time == 4
        assert j2.end_time == 6

    def test_resource_limit(self, policy: DummyPolicy) -> None:
        """No more than total_resources jobs may run at the same time."""
        jobs = [
            Job("j1", submit_time=0, duration=5),
            Job("j2", submit_time=0, duration=5),
            Job("j3", submit_time=0, duration=5),
        ]
        result = Simulator(jobs, policy, total_resources=2).run()

        j1 = next(j for j in result.completed_jobs if j.job_id == "j1")
        j2 = next(j for j in result.completed_jobs if j.job_id == "j2")
        j3 = next(j for j in result.completed_jobs if j.job_id == "j3")

        # j1 and j2 start together; j3 must wait
        assert j1.start_time == 0
        assert j2.start_time == 0
        assert j3.start_time == 5  # starts after one of them finishes

    def test_makespan(self, policy: DummyPolicy) -> None:
        """Makespan equals the end_time of the last completed job."""
        jobs = [
            Job("j1", submit_time=0, duration=3),
            Job("j2", submit_time=0, duration=2),
        ]
        result = Simulator(jobs, policy, total_resources=1).run()
        assert result.makespan == 5  # 3 + 2 sequentially

    def test_delayed_arrival(self, policy: DummyPolicy) -> None:
        """Jobs that arrive later are not started before their submit_time."""
        jobs = [
            Job("j1", submit_time=0, duration=1),
            Job("j2", submit_time=10, duration=1),
        ]
        result = Simulator(jobs, policy, total_resources=1).run()

        j2 = next(j for j in result.completed_jobs if j.job_id == "j2")
        assert j2.start_time == 10
        assert j2.end_time == 11
        assert result.makespan == 11

    def test_parallel_execution(self, policy: DummyPolicy) -> None:
        """With enough resources, all jobs run in parallel."""
        jobs = [
            Job("j1", submit_time=0, duration=3),
            Job("j2", submit_time=0, duration=3),
            Job("j3", submit_time=0, duration=3),
        ]
        result = Simulator(jobs, policy, total_resources=3).run()

        for j in result.completed_jobs:
            assert j.start_time == 0
            assert j.end_time == 3
        assert result.makespan == 3

    def test_rerun_produces_same_result(self, policy: DummyPolicy) -> None:
        """Running the same simulator twice must yield identical results."""
        jobs = [
            Job("j1", submit_time=0, duration=3),
            Job("j2", submit_time=1, duration=2),
        ]
        sim = Simulator(jobs, policy, total_resources=1)
        r1 = sim.run()
        r2 = sim.run()

        assert r1.makespan == r2.makespan
        assert len(r1.completed_jobs) == len(r2.completed_jobs)
        for a, b in zip(r1.completed_jobs, r2.completed_jobs):
            assert a.job_id == b.job_id
            assert a.start_time == b.start_time
            assert a.end_time == b.end_time

    def test_rerun_does_not_mutate_input(self, policy: DummyPolicy) -> None:
        """The original Job objects passed in must not be modified."""
        jobs = [Job("j1", submit_time=0, duration=3)]
        Simulator(jobs, policy).run()

        assert jobs[0].start_time is None
        assert jobs[0].end_time is None


# ------------------------------------------------------------------
# SimulationResult metrics
# ------------------------------------------------------------------

class TestSimulationResult:
    def test_average_turnaround_time(self, policy: DummyPolicy) -> None:
        jobs = [
            Job("j1", submit_time=0, duration=2),
            Job("j2", submit_time=0, duration=3),
        ]
        # 1 resource: j1 0→2 (turnaround 2), j2 2→5 (turnaround 5)
        result = Simulator(jobs, policy, total_resources=1).run()
        assert result.average_turnaround_time == pytest.approx(3.5)

    def test_average_waiting_time(self, policy: DummyPolicy) -> None:
        jobs = [
            Job("j1", submit_time=0, duration=2),
            Job("j2", submit_time=0, duration=3),
        ]
        # 1 resource: j1 wait=0, j2 wait=2
        result = Simulator(jobs, policy, total_resources=1).run()
        assert result.average_waiting_time == pytest.approx(1.0)


# ------------------------------------------------------------------
# Deadlock detection
# ------------------------------------------------------------------

class TestDeadlock:
    def test_policy_always_returns_none(self) -> None:
        """A policy that never starts anything must trigger a RuntimeError."""

        class NeverPolicy(BasePolicy):
            def select_job(
                self, waiting_jobs: list[Job], current_time: int
            ) -> Job | None:
                return None

        jobs = [Job("j1", submit_time=0, duration=1)]
        with pytest.raises(RuntimeError, match="deadlock"):
            Simulator(jobs, NeverPolicy()).run()
