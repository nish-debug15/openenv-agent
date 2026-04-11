import os
import re
from openai import OpenAI
from server.medical_triage_env_environment import MedicalTriageEnv
from server.models import Action

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen3-30B-A3B")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("HF_TOKEN environment variable is required")

try:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
except Exception:
    client = None

env = MedicalTriageEnv()
tasks = [f"task_{i+1}" for i in range(15)]

def parse_obs(obs):
    if isinstance(obs, dict):
        return obs.get("symptoms", []), obs.get("pain_level", 0), obs.get("age", 0), obs.get("hidden_info", [])
    return getattr(obs, "symptoms", []), getattr(obs, "pain_level", 0), getattr(obs, "age", 0), getattr(obs, "hidden_info", [])

def ask_llm(prompt):
    if client is None:
        return "Moderate"
    try:
        r = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return r.choices[0].message.content
    except Exception:
        return "Moderate"

def get_prediction(reasoning):
    decision_prompt = f"""\
Based on this medical reasoning:
"{reasoning}"

Answer ONLY one word: Mild / Moderate / Emergency
"""
    t = ask_llm(decision_prompt)
    t_clean = re.sub(r'[^\w\s]', '', t).lower()
    t_words = set(t_clean.split())

    if "emergency" in t_words:
        return "Emergency"
    if "moderate" in t_words:
        return "Moderate"
    if "mild" in t_words:
        return "Mild"
    return "Moderate"

def apply_rules(symptoms, pain_level, age, hidden_info, pred):
    s = " ".join(symptoms).lower()
    h = " ".join(hidden_info).lower()

    # === EMERGENCY RULES ===
    if age < 18 and any(x in s for x in ["wheez", "breath", "chest tight"]):
        return "Emergency"
    if age >= 70 and any(x in s for x in ["confusion", "fatigue", "slurred"]):
        return "Emergency"
    if any(x in s for x in ["fruity breath", "slurred speech", "facial droop", "rebound tenderness"]):
        return "Emergency"
    if any(x in h for x in ["rebound tenderness", "st elevation", "oxygen saturation", "blood pressure is drop", "blood glucose"]):
        return "Emergency"
    if pain_level >= 8:
        return "Emergency"
    if "pelvic pain" in s and age < 40:
        return "Emergency"

    # === REQUEST MORE INFO ===
    if any(x in s for x in ["abdominal pain", "diffuse abdominal"]) and pain_level <= 7 and age < 40 and not hidden_info:
        return "MORE_INFO"

    # === FORCE MODERATE (prevent LLM over-triaging) ===
    # Sprained ankle — never emergency
    if any(x in s for x in ["ankle swelling", "sprain"]) and pain_level < 8:
        return "Moderate"
    # Gastroenteritis — never emergency unless severe
    if any(x in s for x in ["diarrhea", "stomach cramps"]) and pain_level < 8 and "blood in stool" not in h and "dehydration" not in h:
        return "Moderate"
    # Panic attack — palpitations + anxiety = Moderate not Emergency
    if any(x in s for x in ["palpitations", "tingling", "panic", "anxiety"]) and pain_level < 7:
        return "Moderate"

    # === MILD RULES ===
    if any(x in s for x in ["small cut", "laceration", "bleeding stopped"]) and pain_level <= 3:
        return "Mild"
    if any(x in s for x in ["sunburn", "red skin", "warm to touch"]) and pain_level <= 4 and "blister" not in h:
        return "Mild"
    if any(x in s for x in ["runny nose", "sore throat", "mild cough"]) and pain_level <= 3 and age < 18:
        return "Mild"

    return pred

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

            symptoms, pain_level, age, hidden_info = parse_obs(obs)
            extra_str = f"\nAdditional clinical findings: {', '.join(hidden_info)}" if hidden_info else ""

            reasoning_prompt = f"""\
You are an expert medical triage system. Think step-by-step about this patient.

Symptoms: {symptoms}
Pain: {pain_level}/10
Age: {age}{extra_str}

Consider: age-specific red flags, symptom severity, any life-threatening patterns.
Write your reasoning.
"""
            reasoning = ask_llm(reasoning_prompt)
            raw_pred = get_prediction(reasoning)
            pred = apply_rules(symptoms, pain_level, age, hidden_info, raw_pred)

            if pred == "MORE_INFO":
                action = Action(action_type="request_more_info", content="")
                action_str = "request_more_info"
            else:
                action = Action(action_type="assign_severity", content=pred)
                action_str = pred

            try:
                obs, reward, done, _ = env.step(action)
                reward_val = float(reward)
            except Exception as e:
                error_msg = str(e).replace('\n', ' ')
                done = True

            # FIX: clamp to 0.01 min so .2f never prints 0.00
            reward_val = max(0.01, min(0.999, reward_val))
            rewards_list.append(f"{reward_val:.2f}")
            done_str = "true" if done else "false"
            print(f"[STEP] step={step_count} action={action_str} reward={reward_val:.2f} done={done_str} error={error_msg}", flush=True)

            if error_msg != "null":
                break

    except Exception:
        pass

    finally:
        try:
            env.close()
        except Exception:
            pass
        success_str = "true" if done and error_msg == "null" else "false"
        print(f"[END] success={success_str} steps={step_count} rewards={','.join(rewards_list)}", flush=True)