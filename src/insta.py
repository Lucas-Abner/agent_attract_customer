from instagrapi.exceptions import LoginRequired
from instagrapi import Client
import os

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

try:
    user_id_num = cl.user_id_from_username(target_user)
    print(f"ID user do @{target_user} é {user_id_num}")

    user_details = cl.user_info_by_username(target_user)
    print(f"\nDetails for @{target_user}:")
    print(f" Followers: {user_details.follower_count}")
    print(f" Bio: {user_details.biography[:50]}...")

except Exception as e:
    print(f"Erro ao obter o ID do usuário @{target_user}: {e}")