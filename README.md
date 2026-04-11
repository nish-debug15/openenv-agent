---
title: Medical Triage OpenEnv
emoji: 🏥
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Medical Triage OpenEnv

An OpenEnv-compatible reinforcement learning environment for **medical triage classification** using Large Language Models.

The system simulates patient scenarios and evaluates an agent's ability to classify severity into:

* **Mild**
* **Moderate**
* **Emergency**

---

## Overview

This project implements a triage environment where:

* The **environment generates patient cases** (symptoms, age, pain level)
* The **agent (LLM)** predicts severity using multi-step reasoning
* The **environment assigns rewards** based on correctness and efficiency

---

## System Architecture

```text
Client → FastAPI Server → MedicalTriageEnv → LLM Agent → Action → Reward
```

### Flow:

1. `/reset` → returns patient observation (symptoms, age, pain level)
2. Agent reasons about severity; may request more info if ambiguous
3. `/step` → evaluates prediction or reveals hidden clinical info
4. Reward returned based on correctness + steps taken

---

## Decision Logic

The agent uses a two-stage approach:

1. **LLM reasoning** — structured prompt with symptoms, pain, age → chain-of-thought → severity prediction
2. **Rule-based safety layer** — hard overrides for critical patterns:
   - Pediatric breathing issues → Emergency
   - Elderly confusion/fatigue → Emergency (sepsis risk)
   - Fruity breath → Emergency (DKA)
   - Slurred speech / facial droop → Emergency (stroke)
   - Ambiguous abdominal pain → `request_more_info`

Agent returns one of:

```text
Mild / Moderate / Emergency / request_more_info
```

---

## Reward Function

```python
def grade(predicted_severity, true_severity, steps):
    score = 0.0
    if predicted_severity == true_severity:
        score += 0.7          
    score += max(0, 0.3 - 0.05 * steps)  
    return min(score, 1.0)
```

| Outcome | Max Reward |
|--------|------------|
| Correct, 1 step | 0.75 |
| Correct, 2 steps | 0.70 |
| Incorrect | 0.00–0.25 |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Initialize environment, returns patient observation |
| `/step`  | POST | Submit action (assign_severity or request_more_info) |
| `/close` | POST | End episode |

---

## Deployment

* Fully Dockerized
* Deployed on Hugging Face Spaces
* Runs FastAPI server on port `7860`

---

## Running Locally

```bash
git clone https://github.com/nish-debug15/openenv-agent.git
cd openenv-agent

pip install -r requirements.txt
python -m server.app
```

---

## Inference

The agent uses an LLM via Hugging Face router:

* Model: `Qwen/Qwen3-30B-A3B` (via Hugging Face router)
* Temperature: 0 (deterministic)
* Multi-step: requests additional clinical info for ambiguous cases

---

## Project Structure

```text
openenv-agent/
├── server/
│   ├── app.py
│   ├── medical_triage_env_environment.py
│   ├── models.py
│   └── __init__.py
├── Dockerfile
├── inference.py
├── tasks.py
├── client.py
├── graders.py
├── openenv.yaml
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Validation

This project passes:

* OpenEnv Phase 1 validation (structural checks)
* Docker build checks
* API endpoint checks
* 15/15 tasks scored correctly in Phase 2

---

## Team

AI Alchemists

* Nishit Patel (Lead)
* Pranav Adhikari
* Rahul Kiran

---

## License

MIT License