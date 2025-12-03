# from agno.agent import Agent, RunOutput
# from agno.models.openai import OpenAIChat
# from agno.models.ollama import Ollama
# # from agent import json_sentiment_data
# from insta import (receive_direct_message, 
#                    load_instagram_session,
#                    send_direct_message, 
#                    autenticar_instagram,
#                    return_infos_thread)
# from rich.pretty import pprint
# from dotenv import load_dotenv
# import os
# import re
# import json
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning)

# load_dotenv()

# def load_json_from_response(content : str):
#     match = re.search(r"```json(.*?)```", content, re.S)
#     print("Match encontrado:", match)

#     if not match:
#         raise ValueError("Nenhum bloco JSON encontrado na resposta do agente.")

#     json_text = match.group(1).strip()
#     print("JSON extraído:", json_text)

#     json_data = json.loads(json_text)
#     print("Dados JSON carregados:", json_data)
#     return json_data

# USERNAME = os.environ.get("LOGIN_USERNAME")
# PASSWORD = os.environ.get("LOGIN_PASSWORD")

# SYSTEM_PROMPT = '''
# Você é um especialista em design de interiores, PRINCIPALMENTE em móveis planejados. Seu objetivo é interagir com usuários, identificar interesse em nossos produtos.
# Não inicie a conversa com saudações ou apresentações formais.
# Crie mensagens diretas personalizadas e envolventes, adaptando-se ao contexto da conversa. Utilize uma linguagem amigável e profissional, demonstrando empatia e compreensão das necessidades do cliente.
# Pegue a ultima mensagem enviada pelo usuário e analise seu sentimento, para isso, sigua as instruções:
# - Se a mensagem expressar interesse ou intenção de compra, solicite educadamente o contato do usuário.
# - Se a mensagem for neutra, continue sondando com perguntas abertas para entender melhor as necessidades do usuário.
# - Se a mensagem for negativa, peça desculpas pela inconveniência e encerre a conversa de forma cortês.
# Mantenha o contexto da conversa e evite repetições desnecessárias. Seu objetivo final é construir um relacionamento positivo com o cliente e obter seus contatos de forma natural.
# Não mencione que você é um agente ou que está utilizando ferramentas automatizadas.
# '''

# loaded_agent = Agent(
#     model=Ollama("qwen2.5:7b"),
#     description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
#     markdown=True,
#     tools=[load_instagram_session],
#     instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
#     expected_output="Login realizado com sucesso ou mensagem de erro.",
# )


# send_agent = Agent(
#     model=Ollama("qwen2.5:7b"),
#     tools=[return_infos_thread],
#     instructions="Use return_infos_thread para ver todas as mensagens.",
#     expected_output=("Um json no seguinte formato: \n"
#                     "```json\n"
#                         "[\n"
#                         "  {\n"
#                         "    \"thread_id\": \"123456789\",\n"
#                         "    \"user_id\": \"usuario_exemplo\",\n"
#                         "    \"message\": \"Adorei o design! Muito inspirador.\",\n"
#                         "  }\n"
#                         "]\n"
#                         "```"
#     ),
# )


# loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)

# analitic_agent = Agent(
#     model=OpenAIChat(
#         api_key=os.environ.get("GROQ_API_KEY"),
#         base_url="https://api.groq.com/openai/v1",
#         id="openai/gpt-oss-20b"
#     ),
#     name="json_sentiment_data",
#     description="Agente para analisar o sentimento das mensagens enviadas no Instagram.",
#     markdown=True,
#     tool_call_limit=1,
#     instructions=("Pegue o resultado obtido pelo agente anterior e verifique o sentimento das mensagens enviadas."
#                   "O resultado será passado para você."),
#     expected_output=("Analise o sentimento e envie uma nova mensagem e retorne em json com os campos:"
#                      "```json\n"
#                         "[\n"
#                         "  {\n"
#                         "    \"user_id\": \"usuario_exemplo\",\n"
#                         "    \"analise_sentimento\": \"Negativo, Positivo, Neutro\",\n"
#                         "    \"ultima_mensagem\": \"Ultima mensagem enviada pelo usuario e analisada\",\n"
#                         "  }\n"
#                         "]\n"
#                         "```"),
# )

# initial_agent = Agent(
#     model=OpenAIChat(
#         api_key=os.environ.get("GROQ_API_KEY"),
#         base_url="https://api.groq.com/openai/v1",
#         id="openai/gpt-oss-20b"
#     ),
#     name="message_instagram_user",
#     description="Agente para iniciar uma conversa com um usuário no Instagram.",
#     markdown=True,
#     tools=[send_direct_message],
#     tool_call_limit=1,
#     instructions=("Use a ferramenta send_direct_message para iniciar uma conversa com o usuário que ainda não iniciou uma conversa."
#                   "O user_id é '56295393358'."
#                   "Envie uma mensagem amigável para iniciar a conversa e tentar obter o contato do usuário."
#                   "Mantenha o contexto de que você é um agente que interage com clientes em potencial no Instagram."
#                   "Se o usuário responder, analise o sentimento da resposta e aja de acordo."),
#     expected_output="Envie uma mensagem inicial para o usuário e aguarde a resposta.",
# )

# message_agent = Agent(
#     model=OpenAIChat(
#         api_key=os.environ.get("GROQ_API_KEY"),
#         base_url="https://api.groq.com/openai/v1",
#         id="openai/gpt-oss-20b"
#     ),
#     system_message=SYSTEM_PROMPT,
#     description="Agente para enviar mensagens diretas no Instagram.",
#     tools=[send_direct_message],
#     instructions=('Pegue o json do agente anterior e envie uma mensagem direta ao usuário.'
#                 'Use a ferramenta send_direct_message para enviar uma mensagem direta.'
#                 'Passe os parâmetros corretos: user_id como string e message como string.'
#                 'O user_id é "56295393358".'
#                 'Receba o histórico de mensagens e envie uma resposta apropriada com base no contexto da conversa.'
#                   )
# )


# resp = receive_direct_message()

# print("Resposta final do agente:", resp)