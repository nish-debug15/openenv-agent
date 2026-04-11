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

    print(f"[START] task={task} env=medical_triage_env model={MODEL_NAME}", flush=True)

    done = False
    step_count = 0
    rewards_list = []
    error_msg = "null"

    try:
        obs = env.reset()

        while not done and step_count < 10:
            step_count += 1
            error_msg = "null"
            reward_val = 0.0

            symptoms, pain_level, age = parse_obs(obs)

            prompt = f"""\
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
            action_str = pred

            try:
                obs, reward, done, _ = env.step(action)
                reward_val = float(reward)
            except Exception as e:
                error_msg = str(e).replace('\n', ' ')
                done = True

            rewards_list.append(f"{reward_val:.2f}")
            done_str = "true" if done else "false"
            print(f"[STEP] step={step_count} action={action_str} reward={reward_val:.2f} done={done_str} error={error_msg}", flush=True)

            if error_msg != "null":
                break

    except Exception as e:
        pass

    finally:
        try:
            env.close()
        except Exception:
            pass
        success_str = "true" if done and error_msg == "null" else "false"
        rewards_str = ",".join(rewards_list)
        print(f"[END] success={success_str} steps={step_count} rewards={rewards_str}", flush=True)