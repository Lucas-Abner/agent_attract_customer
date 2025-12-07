from tools import (load_instagram_session,
                   send_direct_message, 
                   return_infos_thread, 
                   fetch_posts)
from utils import load_json_from_response, autenticar_instagram, fetch_comments_for_post, json_save_data
from agno.agent import Agent, RunOutput
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat
from rich.pretty import pprint
from dotenv import load_dotenv
import os
import re
import json
import warnings
import random
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

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

hashtags_file = 'hashtag.txt'
with open(hashtags_file, 'r') as file:
    hashtags = [line.strip() for line in file if line.strip() and not line.startswith('#')]

hashtags = random.sample(hashtags, min(len(hashtags), 3))  # Seleciona até 5 hashtags aleatórias
print(f"Hashtags selecionadas para monitoramento: {hashtags}")

loaded_agent = Agent(
    model=Ollama("llama3.1:8b"),
    description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
    markdown=True,
    tools=[load_instagram_session],
    instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
    expected_output="Login realizado com sucesso ou mensagem de erro.",
)

monitoring_agent = Agent(
    model=OpenAIChat(
         api_key=os.environ.get("GROQ_API_KEY"),
         base_url="https://api.groq.com/openai/v1",
         id="openai/gpt-oss-20b"
    ),
    # model=Ollama("llama3.1:8b"),
    markdown=True,
    tools=[fetch_posts],
    description="Agente para buscar posts recentes com uma hashtag específica e recuperar os comentários desses posts e Usuários.",
    instructions=(
        "Você deve usar APENAS a ferramenta fetch_posts disponível."
        "Pegue a lista de hashtags fornecida, escolha 2 hashtags e busque posts relacionados. "
        "Hashtags disponíveis: " + "\n".join(hashtags) + "."
        "Use cada hashtag SEPARADAMENTE para buscar posts recentes."
        "Não invente código. Não simule resultados. NÃO FAÇA NADA ALÉM DE USAR A FERRAMENTA."
        "Passe os parâmetros corretos: target_hashtag_for_liking como string e amount como número inteiro. "
        "O amount máximo deve ser de 6 (seis)."
        "Retorne exatamente o que a ferramenta retornar.",
    ),
    expected_output=("Lista de posts com comentários em formato JSON:"
                     "```json\n"
                        "[\n"
                        "  {\n"
                        "    \"id\": \"123456789\",\n"
                        "    \"pk\": \"PK do post.\",\n"
                        "  }\n"
                        "]\n"
                        "```"),
    tool_call_limit=2
)

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
    instructions=(
        "Analise os comentários fornecidos e retorne os IDs dos usuários que fizeram comentários positivos. "
        "Pegue os comentários dos posts. "
        "Considere um comentário positivo aquele que expressa satisfação, alegria ou aprovação. "
        "Retorne os resultados em formato JSON com o campo user_id, username, comentário e por que acha que é positivo o comentário."
    ),
    expected_output=(
        "Formato JSON deve ser sempre respeitado:"
        "```json\n"
        "[\n"
        "  {\n"
        "    \"user_id\": \"123456789\",\n"
        "    \"username\": \"usuario_exemplo\",\n"
        "    \"comment\": \"Adorei o design! Muito inspirador.\",\n"
        "    \"reason\": \"O comentário expressa satisfação e aprovação do design apresentado.\"\n"
        "  }\n"
        "]\n"
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
    description="Agente para iniciar uma conversa com um usuário no Instagram.",
    markdown=True,
    tools=[send_direct_message],
    tool_call_limit=1,
    instructions=(
        "Use a ferramenta send_direct_message para iniciar uma conversa com o usuário."
        "Envie uma mensagem amigável para iniciar a conversa e tentar obter o contato do usuário."
        "Mantenha o contexto de que você é um especialista em design de interiores."

    ),
    expected_output="Envie uma mensagem inicial para o usuário e aguarde a resposta.",
)

if __name__=="__main__":
    loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)

    resp: RunOutput = monitoring_agent.run(f"Quais posts recentes com a hashtag {hashtags}?")
    context = resp.content

    pprint(context)

    json_data = load_json_from_response(context)

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

    # list_id = [item['user_id'] for item in context_json]  # Mais pythônico ✅

    # resultt = receive_direct_message(user_ids=list_id)
    # print("Resultado final do agente de recebimento de mensagens diretas:", resultt)