from agno.agent import Agent, RunOutput
from agno.models.openai import OpenAIChat
from agno.models.ollama import Ollama
from .tools import send_direct_message, send_email
from dotenv import load_dotenv
import os

load_dotenv()

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

analitic_agent = Agent(
    # model=OpenAIChat(
    #     api_key=os.environ.get("GROQ_API_KEY"),
    #     base_url="https://api.groq.com/openai/v1",
    #     id="openai/gpt-oss-20b"
    # ),
    model=Ollama("gpt-oss:20b"),
    name="json_sentiment_data",
    description="Agente para analisar o sentimento das mensagens enviadas no Instagram.",
    markdown=True,
    tool_call_limit=1,
    instructions=("Pegue o resultado obtido pelo agente anterior e verifique o sentimento das mensagens enviadas."
                "O resultado será passado para você."
                "A primeira coisa a ser analisada é se na mensagem existe um contato"
                "Ex: telefone, email, whatsapp, instagram, facebook, linkedin."
                "Se encontrar um contato, RETORNE SOMENTE esse contato e o user_id em um json com os campos:"
                "```json\n"
                "  {\n"
                "    \"user_id\": \"12345678\",\n"
                "    \"contato\": \"contato@exemplo.com\"\n"
                "  }\n"
                "```"
                "Se não encontrar um contato, analise o sentimento da mensagem e retorne em um json com os campos:"
                "```json\n"
                "  {\n"
                "    \"user_id\": \"12345678\",\n"
                "    \"analise_sentimento\": \"Negativo, Positivo, Neutro\",\n"
                "    \"ultima_mensagem\": \"Ultima mensagem enviada pelo usuario e analisada\",\n"
                "  }\n"
                "```"),
    expected_output=("Analise o sentimento e envie uma nova mensagem e retorne em json com os campos:"
                    "```json\n"
                        "[\n"
                        "  {\n"
                        "    \"user_id\": \"12345678\",\n"
                        "    \"analise_sentimento\": \"Negativo, Positivo, Neutro\",\n"
                        "    \"ultima_mensagem\": \"Ultima mensagem enviada pelo usuario e analisada\",\n"
                        "  }\n"
                        "]\n"
                        "```"),
)


message_agent = Agent(
    # model=OpenAIChat(
    #     api_key=os.environ.get("GROQ_API_KEY"),
    #     base_url="https://api.groq.com/openai/v1",
    #     id="openai/gpt-oss-20b"
    # ),
    model=Ollama("llama3.1:8b"),
    system_message=SYSTEM_PROMPT,
    description="Agente para enviar mensagens diretas no Instagram.",
    tools=[send_direct_message],
    instructions=('Pegue o json do agente anterior e envie uma mensagem direta ao usuário.'
                'Use a ferramenta send_direct_message para enviar uma mensagem direta.'
                'Passe os parâmetros corretos: user_id como string e message como string.'
                'O user_id é a lista de IDs de usuários.'
                'Receba o histórico de mensagens e envie uma resposta apropriada com base no contexto da conversa.'
    ),
    expected_output="Envie uma mensagem direta personalizada para o usuário com base na análise de sentimento.",
    tool_call_limit=1,
)

email_agent = Agent(
    model = OpenAIChat(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        id="openai/gpt-oss-20b"
    ),
    description="Agente para enviar emails de leads capturados.",
    tools=[send_email],
    instructions=('Pegue o json do agente anterior e envie um email para o usuário.'
                  'Use a ferramenta send_email para enviar um email.'
                  'Passe os parâmetros corretos: message como string.'
                  'Envie uma mensagem de email repassando o contato extraído.'
    ),
    expected_output="Envie um email personalizado para o usuário com base na análise de sentimento.",
    tool_call_limit=1
)