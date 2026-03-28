# SchedSim

SchedSim is a lightweight Python library for simulating and comparing job scheduling policies in a simplified compute environment.

It includes three main parts: a discrete event simulation engine, a pluggable scheduling policy layer, and a metrics module for evaluating results. With SchedSim, users can define jobs, choose a scheduling policy such as FIFO, SJF, or Priority, run a simulation, and inspect the outcome through either Python code or the command line.

The library is designed to be simple, modular, and easy to extend. It is useful for experimenting with scheduling behavior, comparing policy performance, and understanding how design choices affect system outcomes.

## Background

SchedSim was originally developed as a final course project with a strong focus on software engineering rather than algorithmic complexity. The goal of the project was not to build the most advanced scheduler, but to design a clean and maintainable system with clear module boundaries, good testability, and easy extensibility.

The main idea behind the project is to separate the scheduling policy from the simulation engine. The engine is responsible for managing simulation time, tracking resource usage, and handling the lifecycle of jobs from arrival to completion. The policy, by contrast, only decides which waiting job should run next.

This separation makes the system easier to understand and much easier to extend. New scheduling policies can be added without changing the core simulation logic. As a result, the project provides a small but well structured platform for studying scheduling behavior while also demonstrating important software engineering principles such as decoupling, modular design, and interface based development.

SchedSim is not intended to model a full production grade cluster scheduler. Instead, it provides a simplified environment that is easy to work with, making it a practical tool for learning, experimentation, and further development.


## Install

This project requires [Python](https://www.python.org/) >= 3.11.

```bash
git clone https://github.com/Seliiiiina/SchedSim.git
cd SchedSim
pip install -e .
```

To install development dependencies (pytest, ruff):

```bash
pip install -e ".[dev]"
```

## Usage

### As a Library

```python
from src.job import Job
from src.policies import SJFPolicy
from src.simulator import Simulator
from src.metrics import Metrics

jobs = [
    Job("j1", submit_time=0, duration=5, priority=1),
    Job("j2", submit_time=0, duration=2, priority=3),
    Job("j3", submit_time=1, duration=3, priority=2),
]

result = Simulator(jobs, SJFPolicy(), total_resources=1).run()
metrics = Metrics.from_result(result, total_resources=1)

print(metrics)
```

Output:

```
Makespan           : 10
Avg Waiting Time   : 1.67
Avg Turnaround Time: 4.67
Utilization        : 100.0%
```

### Via CLI

Prepare a CSV file (`jobs.csv`):

```csv
job_id,submit_time,duration,priority
j1,0,5,1
j2,0,2,3
j3,1,3,2
```

Run the simulation:

```bash
python cli/run.py jobs.csv --policy sjf --resources 1
```

Output:

```
Policy             : SJF
Makespan           : 10
Avg Waiting Time   : 1.67
Avg Turnaround Time: 4.67
Utilization        : 100.0%
```

Available policies: `fifo`, `sjf`, `priority`.

## Extending SchedSim

Adding a new scheduling policy requires just one class:

```python
from src.policy import BasePolicy
from src.job import Job


class RoundRobinPolicy(BasePolicy):
    """Example: simple round-robin by arrival order."""

    @property
    def name(self) -> str:
        return "RoundRobin"

    def select_job(
        self, waiting_jobs: list[Job], current_time: int
    ) -> Job | None:
        return waiting_jobs[0]
```

Then pass it to the simulator:

```python
result = Simulator(jobs, RoundRobinPolicy(), total_resources=2).run()
```

To make it available via the CLI, add an entry to the `POLICIES` dict in `cli/run.py`.

## Project Structure

```
SchedSim/
├── src/
│   ├── __init__.py     # Package exports
│   ├── job.py          # Job data model
│   ├── policy.py       # BasePolicy abstract interface
│   ├── policies.py     # FIFO, Priority, SJF implementations
│   ├── simulator.py    # Discrete-event simulation engine
│   ├── result.py       # SimulationResult container
│   └── metrics.py      # Evaluation metrics
├── cli/
│   └── run.py          # Command-line interface
├── tests/
│   ├── test_simulator.py    # Core engine & validation tests
│   ├── test_policies.py     # Policy unit tests
│   ├── test_metrics.py      # Metrics unit tests
│   ├── test_cli.py          # CSV loading tests
│   └── test_integration.py  # Full-pipeline integration tests
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
pytest tests/
```

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy src/
```

## Generative AI Usage

As permitted by the course policy, generative AI tools were used during development.
Below is an exhaustive account of what was used, how, and what it produced.

### Tool

We used Claude as a supporting tool throughout the project. It helped us refine the project idea, structure the system, and divide responsibilities between team members. During development, we used it to improve code organization, standardize naming and interfaces, and assist with debugging and edge-case validation. We also used it for high-level code review and to help organize and refine project documentation, including the README.