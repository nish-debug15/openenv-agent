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
