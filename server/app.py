from fastapi import FastAPI
import sys
import os

# Add parent directory to path so we can import models and env
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from medical_triage_env_environment import MedicalTriageEnv
from models import Action

app = FastAPI()
env = MedicalTriageEnv()

@app.get("/")
def home():
    return {"message": "Medical Triage OpenEnv Running"}

@app.get("/reset")
def reset(task: str = "easy"):
    obs = env.reset(task)
    return obs.dict()

@app.post("/step")
def step(action: Action):
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    return env.state()


# THIS PART IS REQUIRED FOR OPENENV VALIDATION
def main():
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()