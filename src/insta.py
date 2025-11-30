from instagrapi.exceptions import LoginRequired
from instagrapi import Client
import os
import time
import random
from agno.tools import tool
from pydantic import ValidationError

USERNAME = os.getenv("LOGIN_USERNAME", "llucasabner")
PASSWORD = os.getenv("LOGIN_PASSWORD", "lucascaixeta1")

@tool(
        name="load_instagram_session",
        description="Carrega a sessão do Instagram usando credenciais armazenadas em variáveis de ambiente. Se o arquivo de sessão existir, tenta carregá-lo e validar a sessão. Se não existir ou se a validação falhar, faz login novamente e salva uma nova sessão.",
)
def load_instagram_session(USERNAME: str, PASSWORD: str) -> str:
    """
    Carrega a sessão do Instagram usando credenciais armazenadas em variáveis de ambiente. Se o arquivo de sessão existir, tenta carregá-lo e validar a sessão. Se não existir ou se a validação falhar, faz login novamente e salva uma nova sessão.
    """

    SESSION_FILE_PATH = "session_instagram.json"

    cl = Client()

    if os.path.exists(SESSION_FILE_PATH):
        cl.load_settings(SESSION_FILE_PATH)
        print(f"Loaded session from {SESSION_FILE_PATH}")

        try:
            cl.login(USERNAME, PASSWORD)
            cl.get_timeline_feed()
            return"Sessão validada e ativa."
        except LoginRequired:
            print("Salvar a sessão não deu certo. Realizando login novamente...")
            try:
                cl.login(USERNAME, PASSWORD)
                cl.dump_settings(SESSION_FILE_PATH)
                return f"Nova sessão salva em {SESSION_FILE_PATH}"
            except Exception as e:
                return f"Erro ao fazer login: {e}"
        except Exception as e_session_use:
            print(f"Erro ao validar a sessão: {e_session_use}")
            try:
                cl.login(USERNAME, PASSWORD)
                cl.dump_settings(SESSION_FILE_PATH)
                return f"Nova sessão salva em {SESSION_FILE_PATH}"
            except Exception as e_fresh_login:
                return f"Erro ao fazer login: {e_fresh_login}"

    else:
        print("Não encontrado arquivo de sessão. Realizando login...")
        try:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE_PATH)
            print(f"Sessão salva em {SESSION_FILE_PATH}")
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
    time.sleep(random.uniform(2, 5))
    if cl.user_id:
        return f"Login bem-sucedido como {cl.username} (ID: {cl.user_id})"
    else:
        return "Autenticação no login falhou. Verifique suas credenciais."

# target_user = "llucasabnerr"

# try:
#     user_id_num = cl.user_id_from_username(target_user)
#     print(f"ID user do @{target_user} é {user_id_num}")

#     user_details = cl.user_info_by_username(target_user)
#     print(f"\nDetails for @{target_user}:")
#     print(f" Followers: {user_details.follower_count}")
#     print(f" Bio: {user_details.biography[:50]}...")

# except Exception as e:
#     print(f"Erro ao obter o ID do usuário @{target_user}: {e}")

# target_hashtag_for_liking = ["pythonprogramming", "coding", "programming", "developer"]
# number_of_posts_to_like = 1

# try:
#     for hashtag in target_hashtag_for_liking:
#         print(f"Curtindo posts com a hashtag #{hashtag}...")
#         recent_hashtag_media = cl.hashtag_medias_recent(hashtag, amount=number_of_posts_to_like * 2)
#         print(f"Encontrados {len(recent_hashtag_media)} posts recentes para a hashtag #{hashtag}.")

#         liked_count = 0
#         if recent_hashtag_media:
#             for media in recent_hashtag_media:
#                 if liked_count >= number_of_posts_to_like:
#                     break

#                 if not media.has_liked:
#                     print(f" Curtindo post PK {media.pk} de @{media.user.username}...")
#                     try:
#                         media_id_str_to_like = cl.media_id(media.pk)
#                         cl.media_like(media_id_str_to_like)
#                         print(f"  Post curtido com sucesso!")

#                         time.sleep(random.uniform(1, 5))
#                     except Exception as e_like:
#                         print(f" Erro ao curtir o post: {e_like}")

#                 else:
#                     print(f" Post PK {media.pk} já foi curtido anteriormente.")
#             print(f"\nFinalizado o processo de curtir posts com a hashtag #{target_hashtag_for_liking}.")
#         else:
#             print(f"Nenhum post recente encontrado para a hashtag #{target_hashtag_for_liking}.")
# except Exception as e_hashtag:
#     print(f"Erro ao buscar posts para a hashtag #{target_hashtag_for_liking}: {e_hashtag}")


target_hashtag_for_liking = "pythonprogramming"

# time.sleep(random.uniform(2,5))

def autenticar_instagram():
    cl = Client()
    SESSION_FILE_PATH = "session_instagram.json"
    cl.load_settings(SESSION_FILE_PATH)
    print(f"Loaded session from {SESSION_FILE_PATH}")
    cl.login(USERNAME, PASSWORD)
    cl.get_timeline_feed()
    cl.dump_settings(SESSION_FILE_PATH)
    return cl

@tool(
        name="fetch_posts",
        description="Busca posts recentes com uma hashtag específica e recupera os comentários desses posts e Usuários.",
)
def fetch_posts(target_hashtag_for_liking: str, amount: int):
    """
    Busca posts recentes com uma hashtag específica e recupera os comentários.
    
    Args:
        target_hashtag_for_liking: Nome da hashtag sem o símbolo # (exemplo: 'pythonprogramming')
        amount: Quantidade de posts para buscar (exemplo: 3)
    
    Returns:
        dict: Dicionário com total_posts e lista de posts com comentários
    """

    # cl = Client()
    # SESSION_FILE_PATH = "session_instagram.json"
    # cl.load_settings(SESSION_FILE_PATH)
    # print(f"Loaded session from {SESSION_FILE_PATH}")
    # cl.login(USERNAME, PASSWORD)
    # cl.get_timeline_feed()
    # cl.dump_settings(SESSION_FILE_PATH)

    hashtag_search = target_hashtag_for_liking.replace("#", "")
    cl = autenticar_instagram()

    try:
        print(f"Posts com a hashtag #{target_hashtag_for_liking}")
        recent_hash_media = cl.hashtag_medias_recent(hashtag_search, amount=amount)
        print(f"Posts encontrados: {len(recent_hash_media)}")
        time.sleep(random.uniform(1,3))

        results = []

        for media in recent_hash_media:
            try:
                media_id = cl.media_id(media.pk)
                print(f"ID do post: {media_id}")

                # Aqui é onde a validação pode falhar (media_info usa modelos pydantic)
                media_info = cl.media_info(media_id)
                # print(f"Info do post: {media_info}")
                results.append({
                    "pk": media.pk,
                    "id": media_id
                })
            except ValidationError as ve:
                # pydantic ValidationError -> pular e logar
                print(f"[ValidationError] Pulando media.pk={getattr(media, 'pk', 'unknown')}: {ve}")
                # # opcional: salvar/inspecionar o raw response para debugar
                # try:
                #     raw = getattr(media, "json", None) or getattr(media, "raw", None)
                #     print("Raw media (parte):", str(raw)[:1000])
                # except Exception:
                #     pass
                # continue
            except Exception as e:
                # captura outros erros (rede, parsing, etc.) mas não interrompe tudo
                print(f"[Erro] ao processar media.pk={getattr(media, 'pk', 'unknown')}: {e}")
                continue

        return results



    except Exception as e_hashtag:
        print(f"Erro ao buscar posts para a hashtag #{target_hashtag_for_liking}: {e_hashtag}")
        print("Vamos tentar autenticar novamente...")
        for media in recent_hash_media:
            try:
                media_id = cl.media_id(media.pk)
                print(f"ID do post: {media_id}")

                # Aqui é onde a validação pode falhar (media_info usa modelos pydantic)
                media_info = cl.media_info(media_id)
                # print(f"Info do post: {media_info}")
                results.append({
                    "pk": media.pk,
                    "id": media_id
                })
            except ValidationError as ve:
                # pydantic ValidationError -> pular e logar
                print(f"[ValidationError] Pulando media.pk={getattr(media, 'pk', 'unknown')}: {ve}")
                # # opcional: salvar/inspecionar o raw response para debugar
                # try:
                #     raw = getattr(media, "json", None) or getattr(media, "raw", None)
                #     print("Raw media (parte):", str(raw)[:1000])
                # except Exception:
                #     pass
                # continue
            except Exception as e:
                # captura outros erros (rede, parsing, etc.) mas não interrompe tudo
                print(f"[Erro] ao processar media.pk={getattr(media, 'pk', 'unknown')}: {e}")
                continue


# @tool(
#         name="fetch_comments_for_post",
#         description="Ferramenta para busca de comentarios de um post especifico dado o media_id.",
# )
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


# message_to_direct = "Ola! Esta é uma mensagem automatizada."

# try:
#     cl.direct_send(message_to_direct, user_ids=[56295393358])
#     print(f"Mensagem enviada para o usuário com ID 56295393358")
# except Exception as e_direct:
#     print(f"Erro ao enviar mensagem direta: {e_direct}")