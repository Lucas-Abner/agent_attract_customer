from instagrapi import Client
import json
import re
from dotenv import load_dotenv
import os
import datetime

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

def autenticar_instagram():
    cl = Client()
    SESSION_FILE_PATH = "session_instagram.json"
    cl.load_settings(SESSION_FILE_PATH)
    print(f"Loaded session from {SESSION_FILE_PATH}")
    cl.login(USERNAME, PASSWORD)
    cl.get_timeline_feed()
    cl.dump_settings(SESSION_FILE_PATH)
    return cl

def load_json_from_response(content : str):
    match = re.search(r"```json(.*?)```", content, re.S)
    print("Match encontrado:", match)

    if not match:
        raise ValueError("Nenhum bloco JSON encontrado na resposta do agente.")

    json_text = match.group(1).strip()
    print("JSON extraído:", json_text)

    json_data = json.loads(json_text)
    print("Dados JSON carregados:", json_data)
    return json_data

def json_save_data(data, filename="infos_comments.json"):

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.extend(data)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)


def fetch_comments_for_post(media_id: str, amount: int):
    """
    Ferramenta para busca de comentarios de um post especifico dado o media_id.
    Args:
        media_id: ID do post para busca de comentarios.
        amount: Quantidade de comentarios para buscar (exemplo: 2).
    
    Returns:
        list_id: Lista de IDs dos usuarios que comentaram no post.
    """

    cl = autenticar_instagram()

    try:
        comments = cl.media_comments(media_id, amount=amount)

        users_all = []
        print(f"Comentários encontrados: {len(comments)}")
        for comment in comments:
            user_ids_commented = cl.user_id_from_username(comment.user.username)
            if user_ids_commented:
                comment_info = {
                    "user_id": user_ids_commented,
                    "username": comment.user.username,
                    "text": comment.text
                }
                users_all.append(comment_info)
            print(comment.user.username, ":", comment.text)
        #     users_all.append(user_ids_commented)


        return users_all

    except Exception as e:
        print(f"Erro ao buscar comentários para o post {media_id}: {e}")

def delete_json_key(filename: str = "infos_comments.json", key: str = None):
    if not os.path.exists(filename):
        print(f"O arquivo {filename} não existe.")
        return

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    if key is None:
        print("Nenhuma chave fornecida para remoção.")
        return

    for item in data:
        if key in item:
            del item[key, "username", "comment", "reason"]

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)