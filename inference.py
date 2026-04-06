import os
from openai import OpenAI
from server.medical_triage_env_environment import MedicalTriageEnv
from models import Action

print("Starting inference...")

# --- ENV VARIABLES ---
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not API_BASE_URL or not MODEL_NAME or not OPENAI_API_KEY:
    raise ValueError("Missing environment variables. Check API_BASE_URL, MODEL_NAME, OPENAI_API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("MODEL_NAME:", MODEL_NAME)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=OPENAI_API_KEY
)

env = MedicalTriageEnv()

tasks = ["easy", "medium", "hard"]
results = {}

# --- SAFE OBS PARSER ---
def parse_obs(obs):
    """Handles both dict and object-style observations safely"""
    if isinstance(obs, dict):
        return (
            obs.get("symptoms", "unknown"),
            obs.get("pain_level", "unknown"),
            obs.get("age", "unknown"),
        )
    else:
        return (
            getattr(obs, "symptoms", "unknown"),
            getattr(obs, "pain_level", "unknown"),
            getattr(obs, "age", "unknown"),
        )

# --- MAIN LOOP ---
for task in tasks:
    print("\nRunning task:", task)

    # Handle broken reset signatures
    try:
        obs = env.reset(task)
    except TypeError:
        obs = env.reset()

    done = False
    total_score = 0

    while not done:
        symptoms, pain_level, age = parse_obs(obs)

        prompt = f"""
Patient symptoms: {symptoms}
Pain level: {pain_level}
Age: {age}

Classify severity as exactly one of:
Mild, Moderate, Emergency.

Only output the label.
"""

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            text = response.choices[0].message.content.strip().lower()

        except Exception as e:
            print("LLM ERROR:", e)
            text = "moderate"  # fallback

        # --- ROBUST PARSING ---
        if "emergency" in text:
            prediction = "Emergency"
        elif "moderate" in text:
            prediction = "Moderate"
        elif "mild" in text:
            prediction = "Mild"
        else:
            prediction = "Moderate"  # safe default

        print("Model prediction:", prediction)

        action = Action(
            action_type="assign_severity",
            content=prediction
        )

        try:
            obs, reward, done, info = env.step(action)
        except Exception as e:
            print("ENV STEP ERROR:", e)
            print("DEBUG patient:", getattr(env, "patient", "NO PATIENT"))
            break

        total_score += reward

    results[task] = total_score
    print("Score for", task, ":", total_score)

# --- FINAL OUTPUT ---
print("\nBaseline Scores:")
for t, s in results.items():
    print(t, ":", s)