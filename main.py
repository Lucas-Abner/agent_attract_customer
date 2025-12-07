from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from src.monitor_msg import InstagramMonitor
import json
import os

load_dotenv()

app = FastAPI()
monitor = InstagramMonitor()

data_id = []

with open("infos_comments.json", "r", encoding="utf-8") as f:
    read_json = json.load(f)
    data_id = [str(item["user_id"]) for item in read_json]

class StartRequest(BaseModel):
    user_ids: list[str] | None = data_id

@app.get("/")
def read_root():
    return {"message": "Bem vindo a aplicação!"}

@app.post("/start_monitor")
def analyze_message(ids: StartRequest):
    request = monitor.start(user_ids=ids.user_ids)
    return {"status": request}

@app.post("/stop")
def stop_monitor():
    request = monitor.stop()
    return {"status": request}

@app.get("/status")
def get_status():
    status = monitor.get_status()
    return status