from agno.agent import Agent, RunOutput
from agno.models.ollama import Ollama
# from agent import json_sentiment_data
from insta import receive_direct_message, load_instagram_session,send_direct_message
from rich.pretty import pprint
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

loaded_agent = Agent(
    model=Ollama("qwen2.5:7b"),
    description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
    markdown=True,
    tools=[load_instagram_session],
    instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
    expected_output="Login realizado com sucesso ou mensagem de erro.",
)


send_agent = Agent(
    model=Ollama("qwen2.5:7b"),
    name="send_instagram_message",
    description="Agente para enviar mensagens diretas no Instagram.",
    markdown=True,
    tools=[receive_direct_message],
    instructions=("Use a ferramenta receive_direct_message para enviar uma mensagem direta."
                  "Passe os parâmetros corretos: user_id como string e message como string."
                  "Não invente código. Não simule resultados. "
                  "O user_id é '56295393358'."
                  "A mensagem pode ser personalizada para você"),
    expected_output=("Mensagem enviada com sucesso"
                     "Ou um json no seguinte formato: \n"
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


loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)

resp : RunOutput = send_agent.run(f"Envie uma mensagem direta para o usuário com user_id 56295393358 com a mensagem 'Olá! Esta é uma mensagem de teste enviada via agente.'")

verify_resp = resp.content

print(f"Verificando resposta: {verify_resp}")

analitic_agent = Agent(
    model=Ollama("qwen2.5:7b"),
    name="json_sentiment_data",
    description="Agente para analisar o sentimento das mensagens enviadas no Instagram.",
    markdown=True,
    tools=[send_direct_message],
    tool_call_limit=1,
    instructions=("Pegue o resultado obtido pelo agente anterior e verifique o sentimento das mensagens enviadas."
                  f"Esse é o resultado a ser analisado: {verify_resp}. "
                  "Verifique se as mensagens tem intenção de compra, interesse ou são neutras."
                  "Se tiver intenção de compra ou interesse, solicite o contado do usuario."
                  "Se for neutra, continue sondando e tentando obter o contato."
                  "Se for negativa, peça desculpas e encerre a conversa."
                  "Mantenha o contexto de que você é um agente que interage com clientes em potencial no Instagram."
                  "Analise o sentimento das mensagens e aja de acordo."),
    expected_output="Analise o sentimento e envie uma nova mensagem apropriada ao usuário, solicitando o contato se houver interesse.",
)

response : RunOutput = analitic_agent.run(f"Analise o sentimento das mensagens enviadas e aja de acordo.")