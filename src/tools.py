from instagrapi.exceptions import LoginRequired
from instagrapi import Client
from .utils import autenticar_instagram
import os
import time
import random
from agno.tools import tool
from pydantic import ValidationError
import resend
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("LOGIN_PASSWORD")

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
    cl.delay_range = [6, 12]
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
    time.sleep(random.uniform(6, 20))
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
    Busca posts recentes com uma hashtag específica.
    Args:
        target_hashtag_for_liking: Lista de hashtags ou string única para buscar posts.
        amount: Número de posts a buscar por hashtag.
    Returns:
        Lista de dicionários contendo 'pk', 'id' e 'hashtag' de cada post.
    """
    import ast
    
    # Parse das hashtags
    if isinstance(target_hashtag_for_liking, str):
        try:
            parsed = ast.literal_eval(target_hashtag_for_liking)
            if isinstance(parsed, (list, tuple)):
                hashtags = [str(h).strip() for h in parsed]
            else:
                hashtags = [target_hashtag_for_liking]
        except (ValueError, SyntaxError):
            hashtags = [target_hashtag_for_liking] if target_hashtag_for_liking else []
    else:
        hashtags = target_hashtag_for_liking if target_hashtag_for_liking else []

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
    
    total_posts_processados = 0
    total_posts_com_erro = 0

    for hashtag in hashtags:
        print(f"\n📍 Processando hashtag: #{hashtag}")
        hashtag_search = hashtag.lstrip('#')
        
        try:
            print(f"Buscando posts recentes para #{hashtag_search}...")
            recent_hash_media = cl.hashtag_medias_recent(hashtag_search, amount=amount)
            print(f"✅ {len(recent_hash_media)} posts encontrados")
            time.sleep(random.uniform(3, 8))

            for idx, media in enumerate(recent_hash_media, 1):
                try:
                    # ✅ Tenta extrair apenas os dados essenciais
                    media_id = cl.media_id(media.pk)
                    
                    # ✅ Valida se os dados essenciais existem
                    if not media.pk or not media_id:
                        print(f"⚠️ Post {idx}: Dados incompletos (pk ou id ausente), pulando...")
                        total_posts_com_erro += 1
                        continue
                    
                    print(f"✅ Post {idx}: ID={media_id}, PK={media.pk}")
                    
                    results.append({
                        "pk": str(media.pk),
                        "id": str(media_id),
                        "hashtag": hashtag_search
                    })
                    
                    total_posts_processados += 1
                    cl.delay_range = [3, 8]
                    
                except ValidationError as ve:
                    # ✅ Captura erros de validação do Pydantic
                    total_posts_com_erro += 1
                    print(f"⚠️ Post {idx}: ValidationError (dados incompletos)")
                    print(f"   Detalhes: {ve.error_count()} erro(s) - {ve.errors()[0]['type']}")
                    continue
                    
                except AttributeError as ae:
                    # ✅ Captura quando media não tem os atributos esperados
                    total_posts_com_erro += 1
                    print(f"⚠️ Post {idx}: Atributo ausente - {ae}")
                    continue
                    
                except Exception as e:
                    # ✅ Captura outros erros inesperados
                    total_posts_com_erro += 1
                    print(f"❌ Post {idx}: Erro inesperado - {type(e).__name__}: {e}")
                    continue
            
            time.sleep(random.uniform(6, 20))
            print(f"✅ Hashtag #{hashtag_search} processada: {len([r for r in results if r['hashtag'] == hashtag_search])} posts válidos")

        except Exception as e_hashtag:
            print(f"❌ Erro ao buscar posts para #{hashtag_search}: {e_hashtag}")
            print("   Continuando para próxima hashtag...")
            continue
    
    # ✅ Relatório final
    print(f"\n{'='*50}")
    print(f"📊 RESUMO DA BUSCA")
    print(f"{'='*50}")
    print(f"✅ Posts processados com sucesso: {total_posts_processados}")
    print(f"⚠️ Posts com erros (pulados): {total_posts_com_erro}")
    print(f"📋 Total de posts válidos retornados: {len(results)}")
    print(f"{'='*50}\n")
            
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
    cl.delay_range = [10, 40]  # Delay maior para envio de DMs
    try:
        cl.direct_send(message_to_direct, user_ids=[id])
        return f"Mensagem enviada para o usuário com ID {id}"
    except Exception as e_direct:
        print(f"Erro ao enviar mensagem direta: {e_direct}")


@tool(
    name="send_email",
    description="Ferramenta para enviar um email usando a API Resend.",
)
def send_email(message):
    """
    Envia um email usando a API Resend.
    Args:
        message: Conteúdo do email a ser enviado.
    Returns:
        Confirmação do envio do email.
    """


    resend.api_key = os.getenv("RESEND_API_KEY")

    params: resend.Emails.SendParams = {
    "from": "Acme <onboarding@resend.dev>",
    "to": ["lucascaixeta02@gmail.com"],
    "subject": "Contato de Lead Capturado",
    "html": f"<p>{message}</p>"
    }

    email = resend.Emails.send(params)
    return email