import os
from openai import OpenAI
from server.medical_triage_env_environment import MedicalTriageEnv
from server.models import Action

# --- ENV VARIABLES ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

# --- CLIENT INIT ---
try:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY
    )
except Exception:
    client = None

# --- INIT ENV ---
env = MedicalTriageEnv()

tasks = ["easy", "medium", "hard"]
results = {}

# --- OBS PARSER ---
def parse_obs(obs):
    if isinstance(obs, dict):
        return (
            obs.get("symptoms", []),
            obs.get("pain_level", 0),
            obs.get("age", 0),
        )
    else:
        return (
            getattr(obs, "symptoms", []),
            getattr(obs, "pain_level", 0),
            getattr(obs, "age", 0),
        )

# --- LLM CALL ---
def get_prediction(prompt):
    if client is None:
        return "Moderate"

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = response.choices[0].message.content.strip().lower()
    except Exception:
        return "Moderate"

    if "emergency" in text:
        return "Emergency"
    elif "moderate" in text:
        return "Moderate"
    elif "mild" in text:
        return "Mild"
    else:
        return "Moderate"

# --- RULE OVERRIDE ---
def apply_rules(symptoms, pain_level, age, prediction):
    symptoms_lower = " ".join(symptoms).lower()

    if any(x in symptoms_lower for x in ["chest pain", "blurred vision", "unconscious", "stroke"]):
        return "Emergency"

    if age >= 60 and any(x in symptoms_lower for x in ["headache", "vomiting", "dizziness"]):
        return "Emergency"

    if pain_level >= 8:
        return "Emergency"

    return prediction

# --- MAIN LOOP ---
for task in tasks:
    try:
        obs = env.reset()
    except Exception:
        continue

    done = False
    total_score = 0
    step_count = 0

    while not done and step_count < 10:
        step_count += 1

        symptoms, pain_level, age = parse_obs(obs)

        prompt = f"""
You are a medical triage system.

Rules:
- Mild: minor symptoms, low pain (0-3), no risk
- Moderate: concerning symptoms, medium pain (4-6)
- Emergency: life-threatening symptoms OR high pain (7-10)

Patient:
Symptoms: {symptoms}
Pain level: {pain_level}
Age: {age}

Respond with ONLY one word:
Mild or Moderate or Emergency.
"""

        prediction = get_prediction(prompt)
        prediction = apply_rules(symptoms, pain_level, age, prediction)

        action = Action(
            action_type="assign_severity",
            content=prediction
        )

        try:
            obs, reward, done, _ = env.step(action)
            total_score += float(reward)
        except Exception:
            break

    results[task] = total_score

# --- FINAL OUTPUT ---
print("Baseline Scores:")
for t, s in results.items():
    print(t, ":", s)