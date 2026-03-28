# SchedSim

A lightweight Python library for simulating and evaluating job scheduling policies.

## Features

- Discrete-event simulation engine with multi-resource support
- Three built-in scheduling policies: FIFO, Priority, SJF
- Metrics module for evaluating simulation results
- Simple CLI for running simulations from CSV files

## Installation
```bash
git clone https://github.com/Seliiiiina/SchedSim.git
cd SchedSim
pip install -e .
```

## Usage

### As a library
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

print(f"Makespan: {metrics.makespan}")
print(f"Avg Waiting Time: {metrics.average_waiting_time:.2f}")
```

### Via CLI

Prepare a CSV file (`jobs.csv`):
```
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

## Project Structure
```
SchedSim/
├── src/
│   ├── job.py          # Job data model
│   ├── policy.py       # BasePolicy abstract interface
│   ├── policies.py     # FIFO, Priority, SJF implementations
│   ├── simulator.py    # Discrete-event simulation engine
│   ├── result.py       # SimulationResult container
│   └── metrics.py      # Evaluation metrics
├── cli/
│   └── run.py          # Command-line interface
├── tests/
│   ├── test_simulator.py
│   └── test_integration.py
└── README.md
```

## Running Tests
```bash
pytest tests/
```