---
title: Medical Triage OpenEnv
emoji: 🏥
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Medical Triage OpenEnv

An OpenEnv-compatible reinforcement learning environment for **medical triage classification** — where an LLM agent must assess patient severity under uncertainty, request clinical information strategically, and make time-critical decisions.

Built for the **Meta × OpenEnv × Hugging Face SST Hackathon**.

---

## Why This Environment?

Medical triage is one of the most consequential sequential decision-making tasks in the real world. Every minute of delay in identifying an emergency costs lives. This environment models that pressure:

- The agent receives **incomplete patient information** and must decide: act now or gather more data?
- **Wrong severity classification is penalized** — calling a stroke "mild" matters
- **Efficiency is rewarded** — correct diagnosis in fewer steps scores higher
- The environment is designed to be genuinely useful for **training and evaluating LLM-based clinical agents**

---

## System Architecture

```
Client → FastAPI Server → MedicalTriageEnv → LLM Agent → Action → Reward
```

### Episode Flow

1. `/reset` → returns initial patient observation: symptoms, age, pain level
2. Agent reasons about severity — may request hidden clinical info if ambiguous
3. `/step` → evaluates the action: reveals more info OR scores the severity prediction
4. Reward returned based on correctness + diagnostic efficiency

---

## Agent Design: Two-Stage Decision Pipeline

The agent combines LLM reasoning with a deterministic safety layer — neither alone is sufficient.

### Stage 1 — LLM Chain-of-Thought
Structured prompt feeds symptoms, pain score, age, and any revealed clinical findings into `Qwen3-30B-A3B` at `temperature=0`. The model produces step-by-step medical reasoning before committing to a severity prediction.

### Stage 2 — Rule-Based Safety Override
Critical patterns are caught deterministically, regardless of LLM output:

| Pattern | Override | Clinical Rationale |
|---|---|---|
| Pediatric + breathing symptoms | → Emergency | Pediatric airways decompensate fast |
| Age 70+ + confusion/fatigue | → Emergency | Sepsis presentation in elderly |
| Fruity breath | → Emergency | Diabetic ketoacidosis (DKA) |
| Slurred speech / facial droop | → Emergency | Stroke — time-to-treatment critical |
| Rebound tenderness (hidden) | → Emergency | Peritonitis / surgical abdomen |
| ST elevation (hidden) | → Emergency | STEMI — minutes matter |
| Ambiguous abdominal pain, no hidden info | → `request_more_info` | Rule out ectopic, appendicitis |

This two-stage design reflects real clinical practice: experienced clinicians use heuristics for high-acuity patterns and deliberate reasoning for ambiguous presentations.

---

## The `request_more_info` Mechanic

A key design decision: the agent is **not forced to commit on incomplete information**.

When clinical presentation is ambiguous, the agent can issue `request_more_info` — triggering the environment to reveal hidden clinical findings (lab values, vitals, secondary symptoms). This models the real triage workflow where a nurse asks follow-up questions before routing a patient.

This makes the environment genuinely **multi-step** and forces the agent to balance information gain against time cost.

---

## Reward Design

Graders are difficulty-tiered (Easy / Medium / Hard) and score across four dimensions:

| Component | What it measures |
|---|---|
| `CORRECT_SEVERITY` | Did the agent classify the right tier? |
| `CORRECT_SERVICE` | Appropriate care pathway (emergency vs urgent vs GP)? |
| `CORRECT_PATTERN` | Did the agent recognize the clinical pattern? |
| `TIME_BONUS_FAST` | Bonus for correct diagnosis in a single step |

**Score ranges — all strictly in (0, 1):**

| Outcome | Easy | Medium | Hard |
|---|---|---|---|
| Correct, 1 step | ~0.90 | ~0.85 | ~0.77 |
| Correct, 2+ steps | ~0.85 | ~0.80 | ~0.72 |
| Off by one tier | 0.30 | 0.25 | 0.20 |
| Wrong / null | 0.05 | 0.05 | 0.05 |

Scores never reach 0 or 1 — boundary values are explicitly excluded to reflect real-world uncertainty in clinical judgment.

---

## Task Difficulty Progression

15 tasks across three difficulty tiers, each requiring progressively more nuanced reasoning:

**Easy** — Clear symptom-severity mapping. Single-step diagnosis expected. Classic presentations (ankle sprain → Mild, chest pain + ST elevation → Emergency).

**Medium** — Ambiguous initial presentation. Hidden info reveal likely needed. Age and comorbidity context matters.

**Hard** — Atypical presentations, misleading initial symptoms, high penalty for missed emergencies. Requires correct identification of rare but critical patterns (DKA, sepsis in elderly, ectopic pregnancy).

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | POST | Initialize episode, returns patient observation |
| `/step` | POST | Submit `assign_severity` or `request_more_info` action |
| `/close` | POST | End episode, finalize scoring |

---

## Deployment

- Fully Dockerized — runs anywhere
- Deployed on Hugging Face Spaces (Docker SDK)
- FastAPI server on port `7860`
- Passes all OpenEnv Phase 1 + Phase 2 validation checks

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

```
Model:       Qwen/Qwen3-30B-A3B (via Hugging Face router)
Temperature: 0  (deterministic, reproducible evaluation)
Max steps:   10 per episode
Fallback:    Rule-based override catches all critical safety patterns
```

---

## Validation

- OpenEnv Phase 1 — structural + spec compliance
- Docker build + inference execution
- Output parsing (`[START]` / `[STEP]` / `[END]` format)
- Task validation — 15/15 tasks scored
- LLM criteria check
- Phase 2 — **Submission Validated**

---

## Project Structure

```
openenv-agent/
├── server/
│   ├── app.py                              # FastAPI server
│   ├── medical_triage_env_environment.py   # Core RL environment
│   ├── graders.py                          # EasyGrader, MediumGrader, HardGrader
│   └── models.py                           # Typed observation/action/reward models
├── Dockerfile
├── inference.py                            # Agent logic + output formatting
├── tasks.py                                # 15 triage scenarios
├── graders.py                              # Internal grade() function
├── openenv.yaml                            # OpenEnv spec config
├── requirements.txt
└── README.md
```

---

## Team — AI Alchemists

- **Nishit Patel** (Lead)
- Pranav Adhikari
- Rahul Kiran

---

## License

MIT License