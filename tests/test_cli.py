"""Tests for the CLI module (CSV loading and argument handling)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from cli.run import load_jobs


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    """Write a standard jobs CSV and return its path."""
    p = tmp_path / "jobs.csv"
    p.write_text(textwrap.dedent("""\
        job_id,submit_time,duration,priority
        j1,0,5,1
        j2,2,3,2
    """))
    return p


class TestLoadJobs:
    def test_loads_valid_csv(self, csv_file: Path) -> None:
        jobs = load_jobs(csv_file)
        assert len(jobs) == 2
        assert jobs[0].job_id == "j1"
        assert jobs[0].submit_time == 0
        assert jobs[0].duration == 5
        assert jobs[0].priority == 1
        assert jobs[1].job_id == "j2"

    def test_missing_priority_defaults_to_zero(self, tmp_path: Path) -> None:
        """When priority column is absent, default to 0."""
        p = tmp_path / "no_priority.csv"
        p.write_text(textwrap.dedent("""\
            job_id,submit_time,duration
            j1,0,3
        """))
        jobs = load_jobs(p)
        assert len(jobs) == 1
        assert jobs[0].priority == 0

    def test_empty_csv_returns_empty_list(self, tmp_path: Path) -> None:
        """A CSV with headers only should produce an empty list."""
        p = tmp_path / "empty.csv"
        p.write_text("job_id,submit_time,duration,priority\n")
        jobs = load_jobs(p)
        assert jobs == []

    def test_invalid_duration_raises(self, tmp_path: Path) -> None:
        """Non-numeric values should cause an error during parsing."""
        p = tmp_path / "bad.csv"
        p.write_text(textwrap.dedent("""\
            job_id,submit_time,duration,priority
            j1,0,abc,1
        """))
        with pytest.raises(ValueError):
            load_jobs(p)
