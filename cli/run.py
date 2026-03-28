"""Command-line interface for SchedSim."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from src.job import Job
from src.metrics import Metrics
from src.policies import FIFOPolicy, PriorityPolicy, SJFPolicy
from src.policy import BasePolicy
from src.simulator import Simulator

POLICIES: dict[str, type[BasePolicy]] = {
    "fifo": FIFOPolicy,
    "priority": PriorityPolicy,
    "sjf": SJFPolicy,
}


def load_jobs(path: Path) -> list[Job]:
    """Load jobs from a CSV file.

    Expected columns: job_id, submit_time, duration, priority (optional).
    """
    jobs: list[Job] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(
                Job(
                    job_id=row["job_id"],
                    submit_time=int(row["submit_time"]),
                    duration=int(row["duration"]),
                    priority=int(row.get("priority") or 0),
                )
            )
    return jobs


def print_metrics(metrics: Metrics, policy_name: str) -> None:
    """Print a formatted metrics summary to stdout."""
    print(f"Policy             : {policy_name}")
    print(f"Makespan           : {metrics.makespan}")
    print(f"Avg Waiting Time   : {metrics.average_waiting_time:.2f}")
    print(f"Avg Turnaround Time: {metrics.average_turnaround_time:.2f}")
    print(f"Utilization        : {metrics.utilization:.1%}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a SchedSim job scheduling simulation."
    )
    parser.add_argument(
        "jobs_csv",
        type=Path,
        help="Path to the CSV file containing job definitions.",
    )
    parser.add_argument(
        "--policy",
        choices=list(POLICIES),
        default="fifo",
        help="Scheduling policy to use (default: fifo).",
    )
    parser.add_argument(
        "--resources",
        type=int,
        default=1,
        help="Number of resource slots available (default: 1).",
    )
    args = parser.parse_args()

    if not args.jobs_csv.exists():
        print(f"Error: file not found: {args.jobs_csv}", file=sys.stderr)
        sys.exit(1)

    jobs = load_jobs(args.jobs_csv)
    policy = POLICIES[args.policy]()
    result = Simulator(jobs, policy, total_resources=args.resources).run()
    metrics = Metrics.from_result(result, total_resources=args.resources)
    print_metrics(metrics, policy.name)


if __name__ == "__main__":
    main()
