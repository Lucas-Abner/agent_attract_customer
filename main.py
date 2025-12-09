from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from src.monitor_msg import InstagramMonitor
from src.agent import run_instagram_pipeline
import json
import os

load_dotenv()

app = FastAPI()

data_id = []

if os.path.exists("infos_comments.json"):
    with open("infos_comments.json", "r", encoding="utf-8") as f:
        try:
            read_json = json.load(f)
            # Validar se é uma lista e não está vazia
            if isinstance(read_json, list) and read_json:
                data_id = [str(item["user_id"]) for item in read_json if isinstance(item, dict) and "user_id" in item]
            else:
                data_id = []
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Erro ao ler infos_comments.json: {e}. Criando arquivo vazio.")
            data_id = []
            # Recriar o arquivo com estrutura correta
            with open("infos_comments.json", "w", encoding="utf-8") as fw:
                json.dump([], fw)
else:
    with open("infos_comments.json", "w", encoding="utf-8") as f:
        json.dump([], f)

monitor = InstagramMonitor()

class StartRequest(BaseModel):
    user_ids: list[str] | None = data_id

class HashtagRequest(BaseModel):
    hashtags: list[str] | str = None

@app.get("/")
def read_root():
    return {"message": "Bem vindo a aplicação!"}

@app.post("/run_pipeline")
def run_pipeline(hashtags: HashtagRequest):
    result = run_instagram_pipeline(hashtags.hashtags)

    try:
        return {
            "sucess": True,
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao executar o pipeline: {e}")

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
