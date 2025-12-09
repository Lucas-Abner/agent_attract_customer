from .tools import (load_instagram_session,
                   send_direct_message, 
                   return_infos_thread, 
                   fetch_posts)
from .utils import load_json_from_response, autenticar_instagram, fetch_comments_for_post, json_save_data
from agno.agent import Agent, RunOutput
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat
from rich.pretty import pprint
from dotenv import load_dotenv
import os
import time
import warnings
import random
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")
EMPRESA_NOME = "InteriArt"
AREA_ATUACAO = "design de interiores especializado em projetos personalizados, modelagem 3D, consultoria e soluções para ambientes residenciais e comerciais."

# hashtags_file = 'hashtag.txt'
# with open(hashtags_file, 'r') as file:
#     hashtags = [line.strip() for line in file if line.strip() and not line.startswith('#')]
# hashtags = random.sample(hashtags, min(len(hashtags), 5))  # Seleciona até 4 hashtags aleatórias

# filepath: /home/lucas.abner/Documentos/code/agent_attract_customer/src/agent.py
# ...existing code...
def receive_direct_message(user_ids: list[str] | None = None):
    """
    Verifica threads para uma lista de user_ids.
    - Se o user_id estiver na thread e a ÚLTIMA mensagem for do usuário, analisa sentimento e responde.
    - Se o user_id não estiver na thread, inicia conversa via initial_agent.
    Retorna dict com resultados por user_id.
    """

    cl = autenticar_instagram()
    if user_ids is None:
        user_ids = []

    results = {}

        # para user_ids que não apareceram em nenhuma thread, iniciar conversa
    for uid in user_ids:
        if uid not in results:
            try:
                response_message: RunOutput = initial_agent.run(f"Inicie conversa com {uid} enviando: 'Olá! Notei seu interesse...'")
                results[uid] = {"thread_id": None, "action": "iniciado", "response": response_message.content}
            except Exception as e:
                results[uid] = {"thread_id": None, "action": "erro_iniciar", "error": str(e)}

    return results



loaded_agent = Agent(
    model=Ollama("llama3.1:8b"),
    description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
    markdown=True,
    tools=[load_instagram_session],
    instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
    expected_output="Login realizado com sucesso ou mensagem de erro.",
)

# monitoring_agent = Agent(
#     model=OpenAIChat(
#          api_key=os.environ.get("GROQ_API_KEY"),
#          base_url="https://api.groq.com/openai/v1",
#          id="openai/gpt-oss-20b"
#     ),
#     # model=Ollama("llama3.1:8b"),
#     markdown=True,
#     tools=[fetch_posts],
#     description="Agente para buscar posts recentes com uma hashtag específica e recuperar os comentários desses posts e Usuários.",
#     instructions=(
#         "Use APENAS a ferramenta fetch_posts."
#         "NÃO invente código Python. NÃO simule resultados."
#         f"Hashtags disponíveis: {', '.join(hashtags)}."
#         "Passe a lista completa de hashtags: fetch_posts(target_hashtag_for_liking={hashtags}, amount=6)"
#         "Retorne EXATAMENTE o JSON que a ferramenta retornar, no formato:"
#         "```json\n[{\"id\": \"...\", \"pk\": \"...\", \"hashtag\": \"...\"}]\n```"
#         "NÃO adicione texto explicativo. APENAS o JSON da ferramenta."
#     ),
#     expected_output=("Lista de posts com comentários em formato JSON:"
#                      "```json\n"
#                         "[\n"
#                         "  {\n"
#                         "    \"id\": \"123456789\",\n"
#                         "    \"pk\": \"PK do post.\",\n"
#                         "  }\n"
#                         "]\n"
#                         "```"),
#     tool_call_limit=2
# )

def get_comments(ids_recuperados):

    comments = []
    for post in ids_recuperados:
        comment = fetch_comments_for_post(media_id=post, amount=5)
        comments.append({post: comment})
    return comments


sentiment_agent = Agent(
    model=OpenAIChat(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        id="openai/gpt-oss-20b"
    ),
    # model=Ollama("llama3.1:8b"),
    markdown=True,
    description="Agente de análise de sentimentos dos comentários.",
    instructions=("""
        Analise os comentários fornecidos e identifique usuários com potencial de conversão em clientes.

        CRITÉRIOS DE IDENTIFICAÇÃO:
        Considere comentários que demonstrem:
        - Interesse direto no produto/serviço (perguntas sobre preço, disponibilidade, características)
        - Intenção de compra ou aquisição (ex: "como faço para comprar?", "onde encontro?", "quanto custa?")
        - Necessidade relacionada ao que você oferece (ex: "preciso de algo assim", "estava procurando isso")
        - Engagement qualificado (elogios específicos ao produto, comparações favoráveis, menções de uso futuro)
        - Solicitação de mais informações ou contato

        EXCLUA comentários que sejam:
        - Que não sejam em português
        - Apenas elogios genéricos sem intenção de compra
        - Marcações de amigos sem contexto de interesse
        - Interações sociais superficiais (ex: apenas emojis, "legal", "top")

        FORMATO DE RESPOSTA:
        Retorne em JSON com a seguinte estrutura:
        {
           [
                {
                "user_id": "ID do usuário",
                "comentario": "texto completo do comentário",
                "razao_qualificacao": "explicação específica do interesse demonstrado"
                }
            ]
        }"""
    ),
    expected_output=(
        "Formato JSON deve ser sempre respeitado:"
        "```json\n"
        """
        {
            [
                {
                "user_id": "ID do usuário",
                "comentario": "texto completo do comentário",
                "razao_qualificacao": "explicação específica do interesse demonstrado"
                }
            ]
        }"""
        "```"
    )
)

send_agent = Agent(
    model=Ollama("qwen2.5:7b"),
    tools=[return_infos_thread],
    instructions=(
        "Pegue os user_ids dos usuários que fizeram comentários positivos."
        "Transforme em uma lista de user_id como string."
        "Use return_infos_thread para ver todas as mensagens."
    ),
    expected_output=(
        "Um json no seguinte formato: \n"
        "```json\n"
        "[\n"
        "  {\n"
        "    \"thread_id\": \"123456789\",\n"
        "    \"user_id\": \"usuario_exemplo\",\n"
        "    \"message\": \"Adorei o design! Muito inspirador.\"\n"
        "  }\n"
        "]\n"
        "```"
    ),
)

initial_agent = Agent(
    model=OpenAIChat(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        id="openai/gpt-oss-20b"
    ),
    name="message_instagram_user",
    description="Agente especializado em iniciar conversas qualificadas com leads no Instagram através de mensagens personalizadas.",
    markdown=True,
    tools=[send_direct_message],
    tool_call_limit=1,
    instructions=(
        f"""Use a ferramenta send_direct_message para enviar apenas uma mensagem inicial e profissional ao usuário. 
        Sua função é iniciar uma conversa apresentando o nome da empresa ({EMPRESA_NOME}), sua área de atuação ({AREA_ATUACAO}) e o que ela faz (projetos personalizados, modelagem 3D, consultoria e soluções para ambientes).
        A mensagem deve ser curta, amigável e personalizada com base no interesse demonstrado pelo usuário.
        Evite mensagens genéricas ou muito longas. O objetivo é engajar o usuário
        de forma amigável e consultiva. Mostre autoridade como especialista em design de interiores, explique como 
        a empresa ajuda clientes e convide o usuário a continuar a conversa perguntando se ele gostaria de saber mais ou ver algumas ideias. 
        Use linguagem humana, curta e natural, sem soar como robô. Evite insistir, apenas abra espaço para diálogo. 
        Retorne somente a chamada da ferramenta send_direct_message com o texto final."""

    ),
    expected_output=(
        "Mensagem personalizada enviada com sucesso, "
        "contendo apresentação da empresa, referência ao interesse do usuário "
        "e call-to-action não invasivo para continuação da conversa."
    ),
)

def run_instagram_pipeline(hashtags_input: list[str] | str = None):
    """
    Executa o pipeline de monitoramento do Instagram com base nas hashtags fornecidas.
    Se nenhuma hashtag for fornecida, lê de 'hashtag.txt' e seleciona até 3 aleatoriamente.
    1. Login no Instagram.
    2. Busca posts recentes com as hashtags.
    3. Recupera comentários dos posts.
    4. Analisa sentimentos dos comentários.
    5. (Opcional) Inicia conversas com usuários interessados.

    Args:
        hashtags_input (list[str]): Lista de hashtags para monitoramento.
    
    Returns:
        dict: Resultados do pipeline, incluindo IDs recuperados e análises de sentimento.
    """
    
    if not hashtags_input:
        hashtags_file = 'hashtag.txt'
        with open(hashtags_file, 'r') as file:
            hashtags = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        hashtags = random.sample(hashtags, min(len(hashtags), 5))  # Seleciona até 3 hashtags aleatórias
    else:
        if isinstance(hashtags_input, str):
            hashtags = [hashtags_input.strip()]
        elif isinstance(hashtags_input, (list, tuple)):
            hashtags = [str(h).strip() for h in hashtags_input]
        else:
            hashtags = [str(hashtags_input).strip()]
    
    print(f"Hashtags selecionadas para monitoramento: {hashtags}")

    login_response = loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)
    
    time.sleep(random.uniform(2,5))

    json_data = fetch_posts(target_hashtag_for_liking=hashtags, amount=6)

    ids_recuperados = [post["id"] for post in json_data]
    print("IDs recuperados:", ids_recuperados)

    comments_data = get_comments(ids_recuperados)
    print("Dados dos comentários obtidos:", comments_data)

    resp_post : RunOutput = sentiment_agent.run(f"Analise esses comentários: {comments_data}")
    post_context = resp_post.content
    print("Contexto do post:", post_context)

    context_json = load_json_from_response(post_context)
    json_save_data(context_json)
    print("Contexto JSON carregado:", context_json)

    list_id = [item['user_id'] for item in context_json]  # Mais pythônico ✅

    resultt = receive_direct_message(user_ids=list_id)
    print("Resultado final do agente de recebimento de mensagens diretas:", resultt)
    return {
        "login": login_response,
        "hashtags": hashtags,
        "posts_found": len(ids_recuperados),
        "posts_ids": ids_recuperados,
        "comments_analyzed": len(context_json),
        "qualified_users": context_json
    }

if __name__=="__main__":
    result = run_instagram_pipeline()
    pprint(result)