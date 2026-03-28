# SchedSim

A lightweight Python library for simulating and evaluating job scheduling policies in a simplified compute environment.

SchedSim provides a discrete-event simulation engine, a pluggable policy abstraction layer, and an evaluation metrics module. It lets you define jobs, choose a scheduling strategy (FIFO, SJF, Priority — or write your own), run the simulation, and inspect the results — all from Python or the command line.

## Background

This project was built as a final course project focused on software engineering practices — clean architecture, modularity, testability, and clear interfaces — rather than algorithmic complexity.

The core idea: scheduling policies should be **decoupled** from the simulation engine. The engine manages time, resources, and job lifecycle; the policy only decides *which waiting job runs next*. This separation makes it trivial to add new policies without touching the engine.

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

- **Claude AI** (Anthropic) — via [Claude Code](https://claude.ai/claude-code), the CLI-based coding assistant.

### How It Was Used and What It Produced

| Phase | How Claude Was Used | What It Produced |
|---|---|---|
| **Code review** | After the core library was designed and implemented by the team, Claude was given the full codebase and asked to perform a structured review (architecture, correctness, testing, documentation). | A detailed review identifying strengths (clean policy abstraction, correct simulation logic, good test structure) and weaknesses (inconsistent tie-breaking in policies, missing policy-specific unit tests, missing metrics tests, incomplete README). |
| **Tie-breaking fix** | Based on the review, Claude was asked to add deterministic tie-breaking to `FIFOPolicy` and `SJFPolicy`. | Changed `FIFOPolicy.select_job` to sort by `(submit_time, job_id)` and `SJFPolicy.select_job` to sort by `(duration, submit_time)`. (~4 lines changed in `src/policies.py`.) |
| **Test coverage improvements** | Claude was asked to write missing unit tests for policies, metrics, and CLI loading. | Three new test files: `tests/test_policies.py` (15 tests), `tests/test_metrics.py` (5 tests), `tests/test_cli.py` (4 tests). Test count went from 28 to 51. |
| **`Metrics.__str__`** | Claude added a `__str__` method to the `Metrics` dataclass for human-readable output. | ~6 lines added to `src/metrics.py`. |
| **Packaging fix** | Claude identified that `cli/` lacked `__init__.py` and wasn't included in `pyproject.toml` packaging, and added a `[project.scripts]` console entry point. | Created `cli/__init__.py`, updated `pyproject.toml`. |
| **README rewrite** | Claude was asked to rewrite the README following the Standard Readme specification. | Produced the current README structure (Background, Install, Usage, Extending, Project Structure, etc.). |

### What Was NOT AI-Generated

The following were designed and implemented entirely by the team:

- Core data models (`Job`, `SimulationResult`)
- `BasePolicy` abstract interface and Strategy pattern design
- All three scheduling policies (FIFO, SJF, Priority)
- Discrete-event simulation engine (`Simulator`)
- `Metrics` evaluation module (factory method and metric formulas)
- CLI (`cli/run.py`)
- Original test suite (`test_simulator.py`, `test_integration.py`)
- All Git workflow (branching, PRs, merges)
