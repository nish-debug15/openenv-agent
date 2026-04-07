from fastapi import FastAPI
from server.medical_triage_env_environment import MedicalTriageEnv
from server.models import Action
import uvicorn

app = FastAPI()
env = MedicalTriageEnv()

@app.get("/reset")
def reset_get():
    obs = env.reset()
    return obs.dict()

@app.post("/reset")
def reset_post():
    obs = env.reset()
    return obs.dict()

@app.get("/state")
def state():
    return env.state()

@app.post("/step")
def step(action: dict):
    try:
        action_obj = Action(**action)
    except Exception:
        return {"error": "Invalid action format"}

    try:
        obs, reward, done, info = env.step(action_obj)
    except Exception as e:
        return {"error": str(e)}

    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/")
def home():
    return {"message": "Medical Triage OpenEnv Running"}

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()