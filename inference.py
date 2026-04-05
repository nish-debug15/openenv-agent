import os
from openai import OpenAI
from server.medical_triage_env_environment import MedicalTriageEnv
from models import Action

print("Starting inference...")

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("API_BASE_URL:", API_BASE_URL)
print("MODEL_NAME:", MODEL_NAME)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=OPENAI_API_KEY
)

env = MedicalTriageEnv()

tasks = ["easy", "medium", "hard"]
results = {}

for task in tasks:
    print("\nRunning task:", task)
    obs = env.reset(task)
    done = False
    total_score = 0

    while not done:
        prompt = f"""
        Patient symptoms: {obs.symptoms}
        Pain level: {obs.pain_level}
        Age: {obs.age}

        Classify severity as Mild, Moderate, or Emergency.
        """

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        prediction = response.choices[0].message.content.strip()
        print("Model prediction:", prediction)

        action = Action(
            action_type="assign_severity",
            content=prediction
        )

        obs, reward, done, info = env.step(action)
        total_score += reward

    results[task] = total_score
    print("Score for", task, ":", total_score)

print("\nFinal Results:")
print(results)

# run this before running the server to test inference
#$env:API_BASE_URL="https://api-inference.huggingface.co/v1"
#$env:MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.2"
#$env:OPENAI_API_KEY="hf_your_new_token"*/