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

The system simulates patient scenarios and evaluates an agent’s ability to classify severity into:

* **Mild**
* **Moderate**
* **Emergency**

---

## Overview

This project implements a triage environment where:

* The **environment generates patient cases** (symptoms, age, pain level)
* The **agent (LLM)** predicts severity
* The **environment assigns rewards** based on correctness

---

## System Architecture

```text
Client → FastAPI Server → MedicalTriageEnv → LLM → Action → Reward
```

### Flow:

1. `/reset` → returns patient case
2. Agent predicts severity
3. `/step` → evaluates prediction
4. Reward returned

---

## Decision Logic

The agent classifies severity based on:

* Symptoms
* Pain level
* Age (risk factor)

LLM is prompted with structured input and returns one of:

```text
Mild / Moderate / Emergency
```

---

## Reward Function

| Prediction               | Reward |
| ------------------------ | ------ |
| Correct classification   | +1.0   |
| Incorrect classification | 0.0    |

---

## API Endpoints

| Endpoint | Method     | Description            |
| -------- | ---------- | ---------------------- |
| `/reset` | GET / POST | Initialize environment |
| `/state` | GET        | Get current state      |
| `/step`  | POST       | Submit prediction      |

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

pip install -r server/requirements.txt
pip install fastapi uvicorn openai
python -m server.app
```

---

## Inference

The baseline agent uses an LLM via Hugging Face router:

* Model: `meta-llama/Llama-3.1-8B-Instruct` (via Hugging Face router)
* Deterministic output (temperature = 0)

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

* OpenEnv validation
* Docker build checks
* API endpoint checks

---

## Team

AI Alchemists

* Nishit Patel (Lead)
* Pranav Adhikari
* Rahul Kiran

---

## License

MIT License
