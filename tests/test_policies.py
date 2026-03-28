"""Unit tests for individual scheduling policies."""

from __future__ import annotations

from src.job import Job
from src.policies import FIFOPolicy, PriorityPolicy, SJFPolicy


class TestFIFOPolicy:
    def test_selects_earliest_arrival(self) -> None:
        """FIFO should pick the job with the smallest submit_time."""
        jobs = [
            Job("j2", submit_time=5, duration=1),
            Job("j1", submit_time=1, duration=10),
            Job("j3", submit_time=3, duration=1),
        ]
        selected = FIFOPolicy().select_job(jobs, current_time=5)
        assert selected is not None
        assert selected.job_id == "j1"

    def test_tie_breaking_by_job_id(self) -> None:
        """When submit_times are equal, FIFO breaks ties by job_id."""
        jobs = [
            Job("b", submit_time=0, duration=1),
            Job("a", submit_time=0, duration=1),
            Job("c", submit_time=0, duration=1),
        ]
        selected = FIFOPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "a"

    def test_single_job(self) -> None:
        jobs = [Job("only", submit_time=0, duration=5)]
        selected = FIFOPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "only"

    def test_name(self) -> None:
        assert FIFOPolicy().name == "FIFO"


class TestSJFPolicy:
    def test_selects_shortest_duration(self) -> None:
        """SJF should pick the job with the smallest duration."""
        jobs = [
            Job("long", submit_time=0, duration=10),
            Job("short", submit_time=0, duration=1),
            Job("mid", submit_time=0, duration=5),
        ]
        selected = SJFPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "short"

    def test_tie_breaking_by_submit_time(self) -> None:
        """When durations are equal, SJF breaks ties by submit_time."""
        jobs = [
            Job("late", submit_time=5, duration=3),
            Job("early", submit_time=1, duration=3),
            Job("mid", submit_time=3, duration=3),
        ]
        selected = SJFPolicy().select_job(jobs, current_time=5)
        assert selected is not None
        assert selected.job_id == "early"

    def test_ignores_priority(self) -> None:
        """SJF should not consider priority at all."""
        jobs = [
            Job("high_prio", submit_time=0, duration=5, priority=99),
            Job("short", submit_time=0, duration=1, priority=0),
        ]
        selected = SJFPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "short"

    def test_single_job(self) -> None:
        jobs = [Job("only", submit_time=0, duration=5)]
        selected = SJFPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "only"

    def test_name(self) -> None:
        assert SJFPolicy().name == "SJF"


class TestPriorityPolicy:
    def test_selects_highest_priority(self) -> None:
        """Priority policy should pick the job with the highest priority value."""
        jobs = [
            Job("low", submit_time=0, duration=1, priority=1),
            Job("high", submit_time=0, duration=1, priority=10),
            Job("mid", submit_time=0, duration=1, priority=5),
        ]
        selected = PriorityPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "high"

    def test_tie_breaking_by_submit_time(self) -> None:
        """When priorities are equal, earlier arrival wins."""
        jobs = [
            Job("late", submit_time=5, duration=1, priority=3),
            Job("early", submit_time=1, duration=1, priority=3),
            Job("mid", submit_time=3, duration=1, priority=3),
        ]
        selected = PriorityPolicy().select_job(jobs, current_time=5)
        assert selected is not None
        assert selected.job_id == "early"

    def test_ignores_duration(self) -> None:
        """Priority policy should not consider duration."""
        jobs = [
            Job("short_low", submit_time=0, duration=1, priority=1),
            Job("long_high", submit_time=0, duration=100, priority=10),
        ]
        selected = PriorityPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "long_high"

    def test_single_job(self) -> None:
        jobs = [Job("only", submit_time=0, duration=5, priority=1)]
        selected = PriorityPolicy().select_job(jobs, current_time=0)
        assert selected is not None
        assert selected.job_id == "only"

    def test_name(self) -> None:
        assert PriorityPolicy().name == "Priority"
