from instagrapi.exceptions import LoginRequired
from instagrapi import Client
from .utils import autenticar_instagram
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


@tool(        
    name="fetch_posts",
    description="Busca posts recentes com uma hashtag específica e recupera os comentários.",
)
def fetch_posts(target_hashtag_for_liking: list[str] | str, amount: int):
    """
    Loga no instagram.
    Busca posts recentes com uma hashtag específica e recupera os comentários.
    
    Args:
        target_hashtag_for_liking: Nome da hashtag sem o símbolo # (exemplo: ['pythonprogramming', 'coding'])
        amount: Quantidade de posts para buscar (exemplo: 3)
    
    Returns:
        dict: Dicionário com total_posts e lista de posts com comentários
    """

    import ast
    if isinstance(target_hashtag_for_liking, str):
        try:
            parsed = ast.literal_eval(target_hashtag_for_liking)
            if isinstance(parsed, (list, tuple)):
                hashtags = [str(h).strip() for h in parsed]
            else:
                hashtags = [target_hashtag_for_liking]
        except (ValueError, SyntaxError):
            hashtags = [target_hashtag_for_liking] if target_hashtag_for_liking else []  # ✅ FIX
    else:
        hashtags = target_hashtag_for_liking if target_hashtag_for_liking else []

    # ✅ Adicione validação extra para remover strings vazias
    hashtags = [h.strip() for h in hashtags if h and h.strip()]

    if not hashtags:
        if os.path.exists("hashtag.txt"):
            with open("hashtag.txt", "r", encoding="utf-8") as f:
                hashtags_input = [line.strip() for line in f if line.strip()]
                print(f"Hashtags carregadas de hashtag.txt: {hashtags_input}")
            hashtags = random.sample(hashtags_input, min(len(hashtags_input), 3))
        else:
            raise ValueError("Nenhuma hashtag fornecida e arquivo hashtag.txt não encontrado.")

    print(f"Hashtags selecionadas: {hashtags}")

    cl = autenticar_instagram()
    results = []

    for hashtag in hashtags:
        print(f"Processando hashtag individual: {hashtag}")
        hashtag_search = hashtag.lstrip('#')  # Remove '#' se estiver presente
        try:
            print(f"Posts com a hashtag #{hashtag_search}")
            recent_hash_media = cl.hashtag_medias_recent(hashtag_search, amount=amount)
            print(f"Posts encontrados: {len(recent_hash_media)}")
            time.sleep(random.uniform(1,3))

            for media in recent_hash_media:
                try:
                    media_id = cl.media_id(media.pk)
                    print(f"ID do post: {media_id}")
                    # Aqui é onde a validação pode falhar (media_info usa modelos pydantic)
                    results.append({
                        "pk": media.pk,
                        "id": media_id,
                        "hashtag": hashtag_search
                    })
                except ValidationError as ve:
                    # pydantic ValidationError -> pular e logar
                    print(f"[ValidationError] Pulando media.pk={getattr(media, 'pk', 'unknown')}: {ve}")
                except Exception as e:
                    # captura outros erros (rede, parsing, etc.) mas não interrompe tudo
                    print(f"[Erro] ao processar media.pk={getattr(media, 'pk', 'unknown')}: {e}")
                    continue
            time.sleep(random.uniform(2,5))

        except Exception as e_hashtag:
            print(f"Erro ao buscar posts para a hashtag #{target_hashtag_for_liking}: {e_hashtag}")
            print("[INFO] Pulando para a próxima hashtag...")
            continue
            
    return results

@tool(
        name="return_infos_thread",
        description="Ferramenta para retornar informações das threads de mensagens diretas.",
)
def return_infos_thread(user_id = None): 

    cl = autenticar_instagram()

    try:
        messages = cl.direct_threads()

        interactions = []
        for thread in messages:
            user_ids_in_thread = [str(msg.user_id) for msg in thread.messages]
            
            if isinstance(user_id, str):
                user_id = user_id
            elif isinstance(user_id, list):
                user_id = [str(uid) for uid in user_id]
            else:
                user_id = None  # Se user_id não for fornecido, defina como None
            if user_id in user_ids_in_thread:
                for msg in range(len(thread.messages[-10:])):
                                    interactions.append({
                                        "thread_id": thread.id,
                                        "user_id": thread.messages[msg].user_id,
                                        "message": thread.messages[msg].text
                                    })

        return interactions
    except Exception as e:
        print(f"Erro ao receber mensagens diretas: {e}")


@tool(
        name="send_direct_message",
        description="Ferramenta para enviar mensagens diretas para um usuário específico.",
)
def send_direct_message(id, message_to_direct: str):

    """
    Ferramenta para enviar mensagens diretas para um usuário específico.
    Args:
        id: ID do usuário para enviar a mensagem direta.
        message_to_direct: Conteúdo da mensagem a ser enviada.
    """

    cl = autenticar_instagram()
    cl.delay_range = [2, 5]
    try:
        cl.direct_send(message_to_direct, user_ids=[id])
        return f"Mensagem enviada para o usuário com ID {id}"
    except Exception as e_direct:
        print(f"Erro ao enviar mensagem direta: {e_direct}")