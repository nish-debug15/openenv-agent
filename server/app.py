from fastapi import FastAPI
from medical_triage_env_environment import MedicalTriageEnv
import uvicorn

app = FastAPI()
env = MedicalTriageEnv()

@app.get("/reset")
def reset_get():
    obs = env.reset("easy")
    return obs.dict()

@app.post("/reset")
def reset_post():
    obs = env.reset("easy")
    return obs.dict()

@app.get("/state")
def state():
    return env.state().dict()

@app.post("/step")
def step(action: dict):
    obs, reward, done, info = env.step(action)
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
