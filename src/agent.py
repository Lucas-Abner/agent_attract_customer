from insta import (receive_direct_message, 
                   load_instagram_session,
                   send_direct_message, 
                   autenticar_instagram,
                   return_infos_thread,
                   fetch_comments_for_post, fetch_posts) 
from agno.agent import Agent, RunOutput
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat
from rich.pretty import pprint
from dotenv import load_dotenv
import os
import re
import json
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

SYSTEM_PROMPT = '''
Você é um especialista em design de interiores, PRINCIPALMENTE em móveis planejados. Seu objetivo é interagir com usuários, identificar interesse em nossos produtos.
Não inicie a conversa com saudações ou apresentações formais.
Crie mensagens diretas personalizadas e envolventes, adaptando-se ao contexto da conversa. Utilize uma linguagem amigável e profissional, demonstrando empatia e compreensão das necessidades do cliente.
Pegue a ultima mensagem enviada pelo usuário e analise seu sentimento, para isso, sigua as instruções:
- Se a mensagem expressar interesse ou intenção de compra, solicite educadamente o contato do usuário.
- Se a mensagem for neutra, continue sondando com perguntas abertas para entender melhor as necessidades do usuário.
- Se a mensagem for negativa, peça desculpas pela inconveniência e encerre a conversa de forma cortês.
Mantenha o contexto da conversa e evite repetições desnecessárias. Seu objetivo final é construir um relacionamento positivo com o cliente e obter seus contatos de forma natural.
Não mencione que você é um agente ou que está utilizando ferramentas automatizadas.
'''


def receive_direct_message(user_id: str = '56295393358'):
    """
    Ferramenta para verificar mensagens diretas de um usuário específico.
    Args:
        user_id: ID do usuário para verificar mensagens diretas.
    Returns:
        interactions: Lista de interações (mensagens) com o usuário específico.

    Se o usuário não tiver iniciado uma conversa, chame a função `send_direct_message`.
    Os parâmetros necessários para essa função são o ID do usuário e a mensagem a ser enviada.
    """

    cl = autenticar_instagram()
    try:
        messages = cl.direct_threads()
        for thread in messages:
            # Filtra apenas as mensagens do user_id específico
            usuario = [str(msg.user_id) for msg in thread.messages]
            print("User IDs na thread:", usuario[-1])

            if user_id in usuario:
                print(f"Thread ID: {thread.id}")

                ultima_mensagem = None
                for msg in reversed(thread.messages):
                    if str(msg.user_id) == user_id:
                        ultima_mensagem = msg
                        break

                ultima_mensagem_geral = thread.messages[0]
                print(f"Última mensagem geral na thread: {ultima_mensagem_geral.text}")
                if str(ultima_mensagem_geral.user_id) != user_id:
                    print(f"Última mensagem é sua, aguardando resposta do usuário")
                    print(f"Última mensagem do usuário: {ultima_mensagem.text if ultima_mensagem else 'N/A'}")
                    return f"Aguardando resposta do usuário {user_id}. Última mensagem dele: {ultima_mensagem.text if ultima_mensagem else 'N/A'}"

                else:
                    resp : RunOutput = send_agent.run(f"Envie uma mensagem direta para o usuário com user_id 56295393358'")

                    verify_resp = resp.content
                    print("Resposta do usuário recebida:", verify_resp) 

                    analisy: RunOutput = analitic_agent.run(f"Analise o sentimento da seguinte mensagem enviada ao usuário {user_id}: {ultima_mensagem_geral.text}.")
                    verify_analisy = analisy.content
                    print("Análise de sentimento recebida:", verify_analisy)
                    json_analisy = load_json_from_response(verify_analisy)

                    msg_to_send = message_agent.run(f"Com base na análise de sentimento: {json_analisy}, envie uma resposta apropriada ao usuário {user_id}. Mantenha o contexto da conversa e evite repetições desnecessárias.")
                    return msg_to_send.content


            elif user_id not in usuario:
                print("Conversa não iniciada com o usuário alvo.")
                response_message : RunOutput = initial_agent.run(f"Inicie uma conversa com o usuário com user_id 56295393358 enviando a mensagem 'Olá! Notei seu interesse em nossos produtos. Gostaria de saber mais?'.")
                return response_message.content


    except Exception as e:
        print(f"Erro ao receber mensagens diretas: {e}")


hashtags_file = 'hashtag.txt'
with open(hashtags_file, 'r') as file:
    hashtags = [line.strip() for line in file if line.strip() and not line.startswith('#')]

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

loaded_agent = Agent(
    model=Ollama("llama3.1:8b"),
    description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
    markdown=True,
    tools=[load_instagram_session],
    instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
    expected_output="Login realizado com sucesso ou mensagem de erro.",
)

monitoring_agent = Agent(
    # model=OpenAIChat(
    #      api_key=os.environ.get("GROQ_API_KEY"),
    #      base_url="https://api.groq.com/openai/v1",
    #      id="openai/gpt-oss-20b"
    # ),
    model=Ollama("llama3.1:8b"),
    markdown=True,
    tools=[fetch_posts],
    description="Agente para buscar posts recentes com uma hashtag específica e recuperar os comentários desses posts e Usuários.",
    instructions=(
        "Você deve usar APENAS a ferramenta fetch_posts disponível."
        "Pegue a lista de hashtags fornecida, escolha 2 hashtags e busque posts relacionados. "
        "Hashtags disponíveis: " + ", ".join(hashtags) + "."
        "Não invente código. Não simule resultados. "
        "Passe os parâmetros corretos: target_hashtag_for_liking como string e amount como número inteiro. "
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

loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)

resp: RunOutput = monitoring_agent.run(f"Quais posts recentes com a hashtag {hashtags}?")
context = resp.content

pprint(context)

json_data = load_json_from_response(context)

ids_recuperados = [post["id"] for post in json_data]
print("IDs recuperados:", ids_recuperados)

def get_comments():

    comments = []
    for post in ids_recuperados:
        comment = fetch_comments_for_post(media_id=post, amount=5)
        comments.append({post: comment})
    return comments

comments_data = get_comments()

sentiment_agent = Agent(
    # model=OpenAIChat(
    #     api_key=os.environ.get("GROQ_API_KEY"),
    #     base_url="https://api.groq.com/openai/v1",
    #     id="openai/gpt-oss-20b"
    # ),
    model=Ollama("llama3.1:8b"),
    markdown=True,
    description="Agente de análise de sentimentos dos comentários.",
    instructions=(
        "Analise os comentários fornecidos e retorne os IDs dos usuários que fizeram comentários positivos. "
        f"O dado de entrada é : {comments_data}. "
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

resp_post : RunOutput = sentiment_agent.run(f"Use o ID do post nesse json {ids_recuperados} para buscar os comentários desse post.")
post_context = resp_post.content
print("Contexto do post:", post_context)

context_json = load_json_from_response(post_context)

print("Contexto JSON carregado:", context_json)

list_id = []
for i, item in enumerate(context_json):
    list_id.append(item['user_id'])

resultt = receive_direct_message(user_id=list_id)
print("Resultado final do agente de recebimento de mensagens diretas:", resultt)

send_agent = Agent(
    model=Ollama("llama3.1:8b"),
    tools=[return_infos_thread],
    instructions=(
        f"O resultado do agente anterior é: {context_json}."
        "Pegue somente os user_id dos usuários que fizeram comentários positivos e retorne as mensagens deles."
        "Transforme em uma lista de user_id como string"
        "Use return_infos_thread para ver todas as mensagens."
        ),
    expected_output=("Um json no seguinte formato: \n"
                    "```json\n"
                        "[\n"
                        "  {\n"
                        "    \"thread_id\": \"123456789\",\n"
                        "    \"user_id\": \"usuario_exemplo\",\n"
                        "    \"message\": \"Adorei o design! Muito inspirador.\",\n"
                        "  }\n"
                        "]\n"
                        "```"
    ),
)

analitic_agent = Agent(
    model=OpenAIChat(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        id="openai/gpt-oss-20b"
    ),
    name="json_sentiment_data",
    description="Agente para analisar o sentimento das mensagens enviadas no Instagram.",
    markdown=True,
    tool_call_limit=1,
    instructions=("Pegue o resultado obtido pelo agente anterior e verifique o sentimento das mensagens enviadas."
                  "O resultado será passado para você."),
    expected_output=("Analise o sentimento e envie uma nova mensagem e retorne em json com os campos:"
                     "```json\n"
                        "[\n"
                        "  {\n"
                        "    \"user_id\": \"usuario_exemplo\",\n"
                        "    \"analise_sentimento\": \"Negativo, Positivo, Neutro\",\n"
                        "    \"ultima_mensagem\": \"Ultima mensagem enviada pelo usuario e analisada\",\n"
                        "  }\n"
                        "]\n"
                        "```"),
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
    instructions=("Use a ferramenta send_direct_message para iniciar uma conversa com o usuário que ainda não iniciou uma conversa."
                  "O user_id é '56295393358'."
                  "Envie uma mensagem amigável para iniciar a conversa e tentar obter o contato do usuário."
                  "Mantenha o contexto de que você é um agente que interage com clientes em potencial no Instagram."
                  "Se o usuário responder, analise o sentimento da resposta e aja de acordo."),
    expected_output="Envie uma mensagem inicial para o usuário e aguarde a resposta.",
)

message_agent = Agent(
    model=OpenAIChat(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        id="openai/gpt-oss-20b"
    ),
    system_message=SYSTEM_PROMPT,
    description="Agente para enviar mensagens diretas no Instagram.",
    tools=[send_direct_message],
    instructions=('Pegue o json do agente anterior e envie uma mensagem direta ao usuário.'
                'Use a ferramenta send_direct_message para enviar uma mensagem direta.'
                'Passe os parâmetros corretos: user_id como string e message como string.'
                'O user_id é "56295393358".'
                'Receba o histórico de mensagens e envie uma resposta apropriada com base no contexto da conversa.'
                  )
)


resp = receive_direct_message()

print("Resposta final do agente:", resp)
