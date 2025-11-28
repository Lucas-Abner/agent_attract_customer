from instagrapi.exceptions import LoginRequired
from instagrapi import Client
import os
import time
import random

USERNAME = os.getenv("LOGIN_USERNAME", "llucasabner")
PASSWORD = os.getenv("LOGIN_PASSWORD", "lucascaixeta1")

SESSION_FILE_PATH = "session_instagram.json"

cl = Client()

if os.path.exists(SESSION_FILE_PATH):
    cl.load_settings(SESSION_FILE_PATH)
    print(f"Loaded session from {SESSION_FILE_PATH}")

    try:
        cl.login(USERNAME, PASSWORD)
        cl.get_timeline_feed()
        print("Sessão validada e ativa.")
    except LoginRequired:
        print("Salvar a sessão não deu certo. Realizando login novamente...")
        try:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE_PATH)
            print(f"Nova sessão salva em {SESSION_FILE_PATH}")
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
    except Exception as e_session_use:
        print(f"Erro ao validar a sessão: {e_session_use}")
        try:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE_PATH)
            print(f"Nova sessão salva em {SESSION_FILE_PATH}")
        except Exception as e_fresh_login:
            print(f"Erro ao fazer login: {e_fresh_login}")

else:
    print("Não encontrado arquivo de sessão. Realizando login...")
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE_PATH)
        print(f"Sessão salva em {SESSION_FILE_PATH}")
    except Exception as e:
        print(f"Erro ao fazer login: {e}")

if cl.user_id:
    print(f"Login bem-sucedido como {cl.username} (ID: {cl.user_id})")
else:
    print("Autenticação no login falhou. Verifique suas credenciais.")

target_user = "llucasabnerr"

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

time.sleep(random.uniform(2,5))

try:
    print(f"Posts com a hashtag #{target_hashtag_for_liking}")
    recent_hash_media = cl.hashtag_medias_recent(target_hashtag_for_liking, amount=2)
    print(f"Posts encontrados: {len(recent_hash_media)}")
    time.sleep(random.uniform(1,3))

    for media in recent_hash_media:
        media_id = cl.media_id(media.pk)
        print(f"ID do post: {media_id}")

        # media_info = cl.media_info(media_id)
        # print(f"Informações do post: {media_info.dict()}")
        time.sleep(random.uniform(1,3))

        try:
            comments = cl.media_comments(media_id, amount=2)
            print(f"Comentários encontrados: {len(comments)}")
            for comment in comments:
                print(comment.user.username, ":", comment.text)
            time.sleep(random.uniform(1,3))

            user_ids_commented = cl.user_id_from_username(comments[0].user.username)
            print(f"ID do usuário que comentou primeiro: {user_ids_commented}")
            time.sleep(random.uniform(3,6))

        except Exception as e:
            print(f"Erro ao buscar comentários para o post {media_id}: {e}")

except Exception as e_hashtag:
    print(f"Erro ao buscar posts para a hashtag #{target_hashtag_for_liking}: {e_hashtag}")