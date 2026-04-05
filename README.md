<<<<<<< HEAD
---
title: Medical Triage Env Environment Server
emoji: 🥇
colorFrom: blue
colorTo: blue
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# Medical Triage Env Environment

A simple test environment that echoes back messages. Perfect for testing the env APIs as well as demonstrating environment usage patterns.

## Quick Start

The simplest way to use the Medical Triage Env environment is through the `MedicalTriageEnv` class:

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv

try:
    # Create environment from Docker image
    medical_triage_envenv = MedicalTriageEnv.from_docker_image("medical_triage_env-env:latest")

    # Reset
    result = medical_triage_envenv.reset()
    print(f"Reset: {result.observation.echoed_message}")

    # Send multiple messages
    messages = ["Hello, World!", "Testing echo", "Final message"]

    for msg in messages:
        result = medical_triage_envenv.step(MedicalTriageAction(message=msg))
        print(f"Sent: '{msg}'")
        print(f"  → Echoed: '{result.observation.echoed_message}'")
        print(f"  → Length: {result.observation.message_length}")
        print(f"  → Reward: {result.reward}")

finally:
    # Always clean up
    medical_triage_envenv.close()
```

That's it! The `MedicalTriageEnv.from_docker_image()` method handles:
- Starting the Docker container
- Waiting for the server to be ready
- Connecting to the environment
- Container cleanup when you call `close()`

## Building the Docker Image

Before using the environment, you need to build the Docker image:

```bash
# From project root
docker build -t medical_triage_env-env:latest -f server/Dockerfile .
```

## Deploying to Hugging Face Spaces

You can easily deploy your OpenEnv environment to Hugging Face Spaces using the `openenv push` command:

```bash
# From the environment directory (where openenv.yaml is located)
openenv push

# Or specify options
openenv push --namespace my-org --private
```

The `openenv push` command will:
1. Validate that the directory is an OpenEnv environment (checks for `openenv.yaml`)
2. Prepare a custom build for Hugging Face Docker space (enables web interface)
3. Upload to Hugging Face (ensuring you're logged in)

### Prerequisites

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**MedicalTriageAction**: Contains a single field
- `message` (str) - The message to echo back

### Observation
**MedicalTriageObservation**: Contains the echo response and metadata
- `echoed_message` (str) - The message echoed back
- `message_length` (int) - Length of the message
- `reward` (float) - Reward based on message length (length × 0.1)
- `done` (bool) - Always False for echo environment
- `metadata` (dict) - Additional info like step count

### Reward
The reward is calculated as: `message_length × 0.1`
- "Hi" → reward: 0.2
- "Hello, World!" → reward: 1.3
- Empty message → reward: 0.0

## Advanced Usage

### Connecting to an Existing Server

If you already have a Medical Triage Env environment server running, you can connect directly:

```python
from medical_triage_env import MedicalTriageEnv

# Connect to existing server
medical_triage_envenv = MedicalTriageEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = medical_triage_envenv.reset()
result = medical_triage_envenv.step(MedicalTriageAction(message="Hello!"))
```

Note: When connecting to an existing server, `medical_triage_envenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv

# Connect with context manager (auto-connects and closes)
with MedicalTriageEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(MedicalTriageAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    MedicalTriageEnvironment,  # Pass class, not instance
    MedicalTriageAction,
    MedicalTriageObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from medical_triage_env import MedicalTriageAction, MedicalTriageEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with MedicalTriageEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(MedicalTriageAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/medical_triage_env_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
medical_triage_env/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # MedicalTriageEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── medical_triage_env_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
=======
# MedFlow-RL: A High-Fidelity EHR Simulation for Agentic AI

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-v1.0-blue)](https://github.com/raun/openenv)
[![Framework: PyTorch](https://img.shields.io/badge/Framework-PyTorch-ee4c2c)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Team: [AI Alchmists]
* **Nishit Patel** (Team Lead)
* **Pranav Adhikari**
* **Rahul Kiran**

---

## Project Overview
**MedFlow-RL** is a specialized OpenEnv environment designed to train and evaluate AI agents on real-world medical data management. Unlike "toy" environments, MedFlow-RL simulates an **Electronic Health Record (EHR)** system where an agent must navigate patient histories, parse unstructured clinical notes, and execute multi-step diagnostic workflows.

The environment challenges agents to act as "Clinical Co-pilots," minimizing administrative errors while identifying critical health markers across long-horizon interactions.

---

## Environment Specification

### 1. Observation Space
The agent receives a structured state containing:
* **Patient Dashboard:** JSON object with demographics and current vitals.
* **Clinical Timeline:** A chronological list of previous encounters and lab results.
* **Active View:** The specific document or "screen" the agent is currently accessing.

### 2. Action Space
The agent interacts using a discrete action set:
* `SEARCH_PATIENT(id)`: Navigates to a specific record.
* `READ_DOCUMENT(doc_id)`: Extracts text from lab reports or notes.
* `UPDATE_FIELD(key, value)`: Modifies or adds data to the EHR.
* `FLAG_CRITICAL()`: Triggers an alert for urgent medical attention.

### 3. Reward Function
* **+1.0 (Success):** Correctly identifying a diagnosis or completing a workflow.
* **+0.1 (Progress):** Correctly parsing a sub-variable (e.g., extracting BP from a note).
* **-0.2 (Efficiency):** Penalty for redundant "clicks" or API calls.
* **-1.0 (Critical Error):** Overlooking a "Red Flag" lab result or incorrect medication logging.

---

## Tasks & Grading
We provide three benchmark tasks with automated agent-graders:

| Task | Difficulty | Goal | Grading Metric |
| :--- | :--- | :--- | :--- |
| **Data Sync** | Easy | Extract vitals from a text note into the dashboard. | Field accuracy (0.0 - 1.0) |
| **Trend Analysis**| Medium | Identify if a patient's glucose levels are stabilizing over 3 visits. | Logic verification (0.0 - 1.0) |
| **Clinical Audit**| Hard | Find a contraindication between a new script and existing history. | Safety check (0.0 - 1.0) |

---

## Setup & Reproducibility

### Prerequisites
* Python 3.10+
* Docker (for local validation)
* Hugging Face CLI (for deployment)

### Local Installation & Execution
```bash
# 1. Clone the repository
git clone [https://github.com/](https://github.com/)[Your-Username]/medflow-rl.git
cd medflow-rl

# 2. Install dependencies
pip install -r requirements.txt

# 3. Validate OpenEnv Specification
python -m openenv.validate .

# 4. Run Baseline Inference
# Ensure environment variables (HF_TOKEN, MODEL_NAME) are set
python inference.py
>>>>>>> 324ed86b1bff95171991b7de39735c16b9f88a34
