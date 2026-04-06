---
title: Medical Triage OpenEnv
emoji: 🏥
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---
# MedFlow-RL

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-v1.0-blue)](https://github.com/raun/openenv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-fidelity Electronic Health Record (EHR) simulation environment for training and evaluating agentic AI. Built on the OpenEnv specification, MedFlow-RL challenges agents to act as clinical co-pilots — navigating patient histories, parsing unstructured clinical notes, and executing multi-step diagnostic workflows.

**Team: AI Alchemists**
Nishit Patel (Lead) · Pranav Adhikari · Rahul Kiran

---

## Quick Start

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv

try:
    # Create environment from Docker image
    env = MedicalTriageEnv.from_docker_image("medical_triage_env-env:latest")

    # Reset
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")

    # Run steps
    messages = ["Hello, World!", "Testing echo", "Final message"]
    for msg in messages:
        result = env.step(MedicalTriageAction(message=msg))
        print(f"Sent: '{msg}' → Echoed: '{result.observation.echoed_message}'")
        print(f"  Length: {result.observation.message_length} | Reward: {result.reward}")

finally:
    env.close()
```

`MedicalTriageEnv.from_docker_image()` handles starting the container, waiting for readiness, connecting to the environment, and cleanup on `close()`.

---

## Environment Specification

### Observation Space

The agent receives a structured state containing:

- **Patient Dashboard** — JSON object with demographics and current vitals
- **Clinical Timeline** — Chronological list of previous encounters and lab results
- **Active View** — The specific document or screen the agent is currently accessing

### Action Space

| Action | Description |
| :--- | :--- |
| `SEARCH_PATIENT(id)` | Navigate to a specific patient record |
| `READ_DOCUMENT(doc_id)` | Extract text from lab reports or clinical notes |
| `UPDATE_FIELD(key, value)` | Modify or add data to the EHR |
| `FLAG_CRITICAL()` | Trigger an alert for urgent medical attention |

### Reward Function

| Signal | Value | Condition |
| :--- | :--- | :--- |
| Success | `+1.0` | Correct diagnosis or completed workflow |
| Progress | `+0.1` | Correct parsing of a sub-variable (e.g., extracting BP from a note) |
| Inefficiency | `-0.2` | Redundant clicks or API calls |
| Critical Error | `-1.0` | Overlooked red-flag lab result or incorrect medication logging |

---

## Benchmark Tasks

| Task | Difficulty | Goal | Metric |
| :--- | :--- | :--- | :--- |
| Data Sync | Easy | Extract vitals from a text note into the dashboard | Field accuracy (0–1) |
| Trend Analysis | Medium | Identify whether a patient's glucose levels are stabilizing over 3 visits | Logic verification (0–1) |
| Clinical Audit | Hard | Find a contraindication between a new prescription and existing history | Safety check (0–1) |

---

## Setup & Reproducibility

**Prerequisites:** Python 3.10+, Docker, Hugging Face CLI

```bash
# 1. Clone the repository
git clone https://github.com/nish-debug15/openenv-agent.git
cd openenv-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate OpenEnv specification
python -m openenv.validate .

# 4. Run baseline inference (set HF_TOKEN and MODEL_NAME first)
python inference.py
```

### Building the Docker Image

```bash
docker build -t medical_triage_env-env:latest -f server/Dockerfile .
```

### Connecting to an Existing Server

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv

env = MedicalTriageEnv(base_url="<ENV_HTTP_URL_HERE>")
result = env.reset()
result = env.step(MedicalTriageAction(message="Hello!"))
# Note: close() will NOT stop the server when connecting to an existing instance
```

### Context Manager (Recommended for Episodes)

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv

with MedicalTriageEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    for msg in ["Hello", "World", "!"]:
        result = env.step(MedicalTriageAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for lower latency, persistent session state, and efficient multi-step episodes.

### Concurrent Sessions

The server supports multiple concurrent WebSocket connections. Enable factory mode in `server/app.py`:

```python
app = create_app(
    MedicalTriageEnvironment,   # Pass class, not instance
    MedicalTriageAction,
    MedicalTriageObservation,
    max_concurrent_envs=4,
)
```

```python
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with MedicalTriageEnv(base_url="http://localhost:8000") as env:
        env.reset()
        for i in range(10):
            env.step(MedicalTriageAction(message=f"Client {client_id}, step {i}"))

with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(run_episode, range(4)))
```

---

## Deploying to Hugging Face Spaces

```bash
# Push from the environment directory (where openenv.yaml is located)
openenv push

# With options
openenv push --repo-id my-org/my-env --private
```

| Option | Description |
| :--- | :--- |
| `--directory`, `-d` | Directory containing the OpenEnv environment (default: current) |
| `--repo-id`, `-r` | Repository ID in `username/repo-name` format |
| `--base-image`, `-b` | Override the base Docker image |
| `--private` | Deploy as a private space (default: public) |

After deployment, the space exposes:

- `/web` — Interactive UI for exploring the environment
- `/docs` — OpenAPI / Swagger documentation
- `/health` — Container health check
- `/ws` — WebSocket endpoint for persistent, low-latency sessions

---

## Project Structure

```
openenv-agent/
├── openenv.yaml                            # OpenEnv manifest
├── pyproject.toml                          # Project metadata and dependencies
├── requirements.txt
├── inference.py                            # Baseline inference script
├── models.py                               # Action and Observation models
├── client.py                               # MedFlowEnv client
└── server/
    ├── app.py                              # FastAPI application (HTTP + WebSocket)
    ├── medical_triage_env_environment.py   # Core environment logic
    └── Dockerfile
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
