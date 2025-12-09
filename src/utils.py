from instagrapi import Client
from pydantic import ValidationError
import json
import re
from dotenv import load_dotenv
import os
import time
import random


load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

def autenticar_instagram():
    """
    Retorna cliente Instagram já autenticado usando sessão salva.
    """
    SESSION_FILE_PATH = "session_instagram.json"
    cl = Client()
    
    if os.path.exists(SESSION_FILE_PATH):
        try:
            cl.load_settings(SESSION_FILE_PATH)
            # IMPORTANTE: NÃO chamar login() se já tem sessão válida
            # cl.login(USERNAME, PASSWORD)  # ← REMOVA ISSO
            cl.get_timeline_feed()  # Valida se sessão está ativa
            return cl
        except Exception as e:
            print(f"Erro ao validar sessão: {e}")
            print("Sessão expirada, fazendo novo login...")
            # Remove sessão antiga
            os.remove(SESSION_FILE_PATH)
    
    # Se não tem sessão ou expirou, faz novo login
    try:
        cl.login(os.getenv("LOGIN_USERNAME"), os.getenv("LOGIN_PASSWORD"))
        cl.dump_settings(SESSION_FILE_PATH)
        print("Nova sessão criada e salva")
        return cl
    except Exception as e:
        raise Exception(f"Falha ao autenticar: {e}")
    
def load_json_from_response(response_text: str):
    """
    Extrai JSON de uma resposta que pode conter markdown ou texto adicional.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Tenta extrair JSON de blocos de código markdown
    json_pattern = r'```(?:json)?\s*(\[[\s\S]*?\]|\{[\s\S]*?\})\s*```'
    matches = re.findall(json_pattern, response_text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON em markdown inválido: {e}")
            print(f"Conteúdo: {matches[0][:200]}...")
    
    # Tenta encontrar array ou objeto JSON diretamente no texto
    json_pattern_direct = r'(\[[\s\S]*?\]|\{[\s\S]*?\})'
    matches_direct = re.findall(json_pattern_direct, response_text, re.DOTALL)
    
    if matches_direct:
        try:
            return json.loads(matches_direct[0])
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON direto inválido: {e}")
            print(f"Conteúdo: {matches_direct[0][:200]}...")
    
    raise ValueError(f"Não foi possível extrair JSON válido da resposta. Resposta recebida:\n{response_text[:500]}...")

def json_save_data(data, filename="infos_comments.json"):

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.extend(data)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# def fetch_posts(target_hashtag_for_liking: list[str] | str, amount: int):
#     """
#     Loga no instagram.
#     Busca posts recentes com uma hashtag específica e recupera os comentários.
    
#     Args:
#         target_hashtag_for_liking: Nome da hashtag sem o símbolo # (exemplo: ['pythonprogramming', 'coding'])
#         amount: Quantidade de posts para buscar (exemplo: 3)
    
#     Returns:
#         dict: Dicionário com total_posts e lista de posts com comentários
#     """

#     import ast
#     if isinstance(target_hashtag_for_liking, str):
#         try:
#             parsed = ast.literal_eval(target_hashtag_for_liking)
#             if isinstance(parsed, (list, tuple)):
#                 hashtags = [str(h).strip() for h in parsed]
#             else:
#                 hashtags = [target_hashtag_for_liking]
#         except (ValueError, SyntaxError):
#             hashtags = [target_hashtag_for_liking] if target_hashtag_for_liking else []  # ✅ FIX
#     else:
#         hashtags = target_hashtag_for_liking if target_hashtag_for_liking else []

#     # ✅ Adicione validação extra para remover strings vazias
#     hashtags = [h.strip() for h in hashtags if h and h.strip()]

#     if not hashtags:
#         if os.path.exists("hashtag.txt"):
#             with open("hashtag.txt", "r", encoding="utf-8") as f:
#                 hashtags_input = [line.strip() for line in f if line.strip()]
#                 print(f"Hashtags carregadas de hashtag.txt: {hashtags_input}")
#             hashtags = random.sample(hashtags_input, min(len(hashtags_input), 3))
#         else:
#             raise ValueError("Nenhuma hashtag fornecida e arquivo hashtag.txt não encontrado.")

#     print(f"Hashtags selecionadas: {hashtags}")

#     cl = autenticar_instagram()
#     results = []

#     for hashtag in hashtags:
#         print(f"Processando hashtag individual: {hashtag}")
#         hashtag_search = hashtag.lstrip('#')  # Remove '#' se estiver presente
#         try:
#             print(f"Posts com a hashtag #{hashtag_search}")
#             recent_hash_media = cl.hashtag_medias_recent(hashtag_search, amount=amount)
#             print(f"Posts encontrados: {len(recent_hash_media)}")
#             time.sleep(random.uniform(1,3))

#             for media in recent_hash_media:
#                 try:
#                     media_id = cl.media_id(media.pk)
#                     print(f"ID do post: {media_id}")
#                     # Aqui é onde a validação pode falhar (media_info usa modelos pydantic)
#                     results.append({
#                         "pk": media.pk,
#                         "id": media_id,
#                         "hashtag": hashtag_search
#                     })
#                 except ValidationError as ve:
#                     # pydantic ValidationError -> pular e logar
#                     print(f"[ValidationError] Pulando media.pk={getattr(media, 'pk', 'unknown')}: {ve}")
#                     # # opcional: salvar/inspecionar o raw response para debugar
#                     # try:
#                     #     raw = getattr(media, "json", None) or getattr(media, "raw", None)
#                     #     print("Raw media (parte):", str(raw)[:1000])
#                     # except Exception:
#                     #     pass
#                     # continue
#                 except Exception as e:
#                     # captura outros erros (rede, parsing, etc.) mas não interrompe tudo
#                     print(f"[Erro] ao processar media.pk={getattr(media, 'pk', 'unknown')}: {e}")
#                     continue
#             time.sleep(random.uniform(2,5))

#         except Exception as e_hashtag:
#             print(f"Erro ao buscar posts para a hashtag #{target_hashtag_for_liking}: {e_hashtag}")
#             print("[INFO] Pulando para a próxima hashtag...")
#             continue
            
#     return results


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