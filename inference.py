import os
from openai import OpenAI
from server.medical_triage_env_environment import MedicalTriageEnv
from server.models import Action

# --- ENV ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

# --- CLIENT ---
try:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
except Exception:
    client = None

env = MedicalTriageEnv()
tasks = ["easy", "medium", "hard"]

# --- HELPERS ---
def parse_obs(obs):
    if isinstance(obs, dict):
        return obs.get("symptoms", []), obs.get("pain_level", 0), obs.get("age", 0)
    return getattr(obs, "symptoms", []), getattr(obs, "pain_level", 0), getattr(obs, "age", 0)

def get_prediction(prompt):
    if client is None:
        return "Moderate"
    try:
        r = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        t = r.choices[0].message.content.lower()
    except Exception:
        return "Moderate"

    if "emergency" in t:
        return "Emergency"
    if "moderate" in t:
        return "Moderate"
    if "mild" in t:
        return "Mild"
    return "Moderate"

def apply_rules(symptoms, pain_level, age, pred):
    s = " ".join(symptoms).lower()

    if any(x in s for x in ["chest pain", "blurred vision", "stroke"]):
        return "Emergency"

    if age >= 60 and any(x in s for x in ["headache", "vomiting", "dizziness"]):
        return "Emergency"

    if pain_level >= 8:
        return "Emergency"

    return pred

# --- MAIN ---
for task in tasks:

    print(f"[START] task={task}", flush=True)

    try:
        obs = env.reset()
    except Exception:
        print(f"[END] task={task} score=0 steps=0", flush=True)
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
- Mild: pain 0-3
- Moderate: pain 4-6
- Emergency: pain 7-10 OR critical symptoms

Symptoms: {symptoms}
Pain: {pain_level}
Age: {age}

Answer ONLY one word: Mild / Moderate / Emergency
"""

        pred = get_prediction(prompt)
        pred = apply_rules(symptoms, pain_level, age, pred)

        action = Action(action_type="assign_severity", content=pred)

        try:
            obs, reward, done, _ = env.step(action)
            total_score += float(reward)

            print(f"[STEP] step={step_count} reward={reward}", flush=True)

        except Exception:
            break

    print(f"[END] task={task} score={total_score} steps={step_count}", flush=True)