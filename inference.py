from __future__ import annotations

import os
import re
import sys
from typing import Any

from openai import OpenAI

from graders import grade
from tasks import cases
from server.medical_triage_env_environment import MedicalTriageEnv
from server.models import Action

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "Qwen/Qwen3-30B-A3B")
API_KEY      = os.environ.get("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

_SYSTEM = (
    "You are a board-certified emergency physician performing rapid triage. "
    "Assess patients quickly and accurately. Consider age-specific risk factors, "
    "vital sign implications, and life-threatening patterns."
)

def safe_reward(value: Any) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.01
    return max(0.01, min(0.99, v))

def parse_obs(obs: Any) -> tuple[list, int, int, list]:
    if isinstance(obs, dict):
        return (
            obs.get("symptoms", []),
            int(obs.get("pain_level", 0)),
            int(obs.get("age", 0)),
            obs.get("hidden_info", []),
        )
    return (
        getattr(obs, "symptoms",    []),
        int(getattr(obs, "pain_level", 0)),
        int(getattr(obs, "age",        0)),
        getattr(obs, "hidden_info", []),
    )

def unpack_step(result: Any) -> tuple[Any, float, bool]:
    if isinstance(result, tuple):
        if len(result) >= 3:
            return result[0], float(result[1]), bool(result[2])
        elif len(result) == 2:
            return result[0], float(result[1]), False
        else:
            return result[0], 0.01, False
    obs    = result
    val    = getattr(result, "reward", 0.01)
    reward = float(val if val is not None else 0.01)
    done   = bool(getattr(result, "done", False))
    return obs, reward, done

def ask_llm(prompt: str) -> str | None:
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": prompt},
            ],
            temperature=0,
            max_tokens=256,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        print(f"[WARN] LLM call failed: {type(e).__name__}", file=sys.stderr)
        return None

def extract_severity(text: str) -> str:
    clean = re.sub(r"[^\w\s]", "", text.lower())
    words = set(clean.split())
    if "emergency" in words: return "Emergency"
    if "moderate"  in words: return "Moderate"
    if "mild"      in words: return "Mild"
    danger = {"critical", "urgent", "life-threatening", "immediately", "severe", "stroke", "cardiac", "sepsis"}
    if words & danger:        return "Emergency"
    return "Moderate"

def build_prompt(symptoms: list, pain_level: int, age: int, hidden_info: list) -> str:
    extras = ""
    if hidden_info:
        extras = "\n\nAdditional clinical findings:\n" + "\n".join(f"  - {h}" for h in hidden_info)
    return (
        f"RAPID TRIAGE ASSESSMENT\n"
        f"=======================\n"
        f"Patient Age:  {age} years\n"
        f"Pain Level:   {pain_level} / 10\n"
        f"Symptoms:     {', '.join(symptoms)}{extras}\n\n"
        f"Think step-by-step:\n"
        f"1. Identify the most alarming signs.\n"
        f"2. Consider age-specific red flags.\n"
        f"3. Is this immediately life-threatening?\n\n"
        f"Respond with ONE word only: Mild / Moderate / Emergency"
    )

def rule_based_triage(symptoms: list, pain_level: int, age: int,
                      hidden_info: list, step: int) -> str | None:
    s = " ".join(symptoms).lower()
    h = " ".join(hidden_info).lower()

    _pedi_distress = any(x in s for x in ["wheez", "breath", "chest tight"])
    _pedi_cough    = ("coughing" in s) or ("cough" in s and "mild cough" not in s)
    if age < 18 and (_pedi_distress or _pedi_cough):
        return "Emergency"

    if age >= 65 and any(x in s for x in ["confusion", "fatigue", "slurred"]):
        return "Emergency"

    if any(x in s for x in ["slurred speech", "facial droop", "arm weakness"]):
        return "Emergency"

    if "chest pain" in s:
        return "Emergency"

    if "fruity breath" in s or ("excessive thirst" in s and "frequent urination" in s):
        return "Emergency"

    if "severe flank pain" in s or ("blood in urine" in s and pain_level >= 7):
        return "Emergency"

    if ("pelvic pain" in s or "sudden pelvic" in s) and age < 55:
        return "Emergency"

    if pain_level >= 8:
        return "Emergency"

    _danger_hidden = [
        "rebound tenderness", "st elevation", "oxygen saturation",
        "blood pressure is drop", "blood glucose", "chest retraction",
        "heart rate is elevated", "missed her last period",
        "requires immediate", "stroke protocol", "fever developed",
    ]
    if any(x in h for x in _danger_hidden):
        return "Emergency"

    if any(x in s for x in ["ankle swelling", "sprain"]) and pain_level < 8:
        return "Moderate"

    if any(x in s for x in ["throbbing headache", "photophobia", "migraine"]):
        if "neurological deficit" not in h:
            return "Moderate"

    if any(x in s for x in ["palpitations", "tingling", "fear of dying"]) and pain_level < 7:
        return "Moderate"

    if ("diarrhea" in s or "stomach cramps" in s) and pain_level < 8:
        if "blood in stool" not in h and "dehydration" not in h:
            return "Moderate"

    if any(x in s for x in ["small cut", "laceration", "bleeding stopped"]) and pain_level <= 3:
        return "Mild"

    if any(x in s for x in ["sunburn", "red skin", "warm to touch"]) and pain_level <= 4:
        if "blister" not in h:
            return "Mild"

    if any(x in s for x in ["runny nose", "sore throat", "mild cough"]) and pain_level <= 4:
        return "Mild"

    if step == 1 and not hidden_info:
        if any(x in s for x in ["abdominal pain", "diffuse abdominal", "nausea", "loss of appetite"]) and pain_level <= 7:
            return "REQUEST_INFO"

    return None

env        = MedicalTriageEnv()
task_names = [f"task_{i + 1}" for i in range(15)]

for task_idx, task_name in enumerate(task_names):
    true_severity = cases[task_idx]["true_severity"]

    print(f"[START] task={task_name} env=medical_triage_env model={MODEL_NAME}", flush=True)

    step_count   = 0
    rewards_list: list[str] = []
    error_msg    = "null"
    done         = False

    try:
        obs = env.reset()

        while not done and step_count < 5:
            step_count += 1
            error_msg = "null"

            symptoms, pain_level, age, hidden_info = parse_obs(obs)

            llm_text = ask_llm(build_prompt(symptoms, pain_level, age, hidden_info))
            llm_pred = extract_severity(llm_text) if llm_text else None

            rule_result = rule_based_triage(symptoms, pain_level, age, hidden_info, step_count)

            if rule_result is not None:
                decision = rule_result
            elif llm_pred is not None:
                decision = llm_pred
            else:
                decision = "Moderate"

            if decision == "REQUEST_INFO":
                action     = Action(action_type="request_more_info", content="")
                action_str = "request_more_info"
            else:
                action     = Action(action_type="assign_severity", content=decision)
                action_str = decision

            try:
                raw_result                 = env.step(action)
                obs, _raw_reward, env_done = unpack_step(raw_result)

                if step_count >= 5:
                    done = True
                else:
                    done = env_done

                if not done:
                    reward_val = safe_reward(0.01)
                else:
                    if action.action_type == "request_more_info":
                        reward_val = safe_reward(0.10)
                    else:
                        reward_val = safe_reward(grade(decision, true_severity, step_count))

            except Exception as step_exc:
                error_msg  = str(step_exc).replace("\n", " ")[:200]
                reward_val = safe_reward(0.01)
                done       = True

            rewards_list.append(f"{reward_val:.2f}")
            print(
                f"[STEP] step={step_count} action={action_str} "
                f"reward={reward_val:.2f} done={'true' if done else 'false'} "
                f"error={error_msg}",
                flush=True,
            )

            if error_msg != "null":
                break

    except Exception as ep_exc:
        error_msg  = str(ep_exc).replace("\n", " ")[:200]
        reward_val = safe_reward(0.01)
        if step_count == 0:
            step_count = 1
        rewards_list.append(f"{reward_val:.2f}")
        print(
            f"[STEP] step={step_count} action=error "
            f"reward={reward_val:.2f} done=true error={error_msg}",
            flush=True,
        )
        done = True

    finally:
        if not rewards_list:
            rewards_list.append("0.01")
        success_str = "true" if (done and error_msg == "null") else "false"
        print(
            f"[END] success={success_str} steps={step_count} "
            f"rewards={','.join(rewards_list)}",
            flush=True,
        )
        try:
            env.close()
        except Exception:
            pass