# from agno.agent import Agent, RunOutput
# from agno.models.ollama import Ollama
# from agno.models.openai import OpenAIChat
# from insta import load_instagram_session, fetch_posts, fetch_comments_for_post
# from rich.pretty import pprint
# from agno.workflow import Workflow, Step, StepOutput
# from pydantic import BaseModel, Field
# from dotenv import load_dotenv

# load_dotenv()

# import re
# import json
# import os

# hashtags_file = 'hashtag.txt'
# with open(hashtags_file, 'r') as file:
#     hashtags = [line.strip() for line in file if line.strip() and not line.startswith('#')]

# def load_json_from_response(content: str):
#     match = re.search(r"```json(.*?)```", content, re.S)

#     if not match:
#         raise ValueError("Nenhum bloco JSON encontrado na resposta do agente.")

#     json_text = match.group(1).strip()

#     json_data = json.loads(json_text)

#     return json_data

# USERNAME = os.environ.get("LOGIN_USERNAME")
# PASSWORD = os.environ.get("LOGIN_PASSWORD")

# loaded_agent = Agent(
#     model=Ollama("qwen2.5:7b"),
#     description="Agente para conectar-se ao Instagram usando uma ferramenta dedicada.",
#     markdown=True,
#     tools=[load_instagram_session],
#     instructions=f"Sempre use a ferramenta load_instagram_session para fazer login no Instagram usando as credenciais armazenadas nas variáveis de ambiente, nome de usuario {USERNAME} e senha {PASSWORD}.",
#     expected_output="Login realizado com sucesso ou mensagem de erro.",
# )

# monitoring_agent = Agent(
#     # model=OpenAIChat(
#     #     api_key=os.environ.get("GROQ_API_KEY"),
#     #     base_url="https://api.groq.com/openai/v1",
#     #     id="openai/gpt-oss-20b"
#     # ),
#     model=Ollama("qwen2.5:7b"),
#     markdown=True,
#     tools=[fetch_posts],
#     description="Agente para buscar posts recentes com uma hashtag específica e recuperar os comentários desses posts e Usuários.",
#     instructions=(
#         "Você deve usar APENAS a ferramenta fetch_posts disponível."
#         "Pegue a lista de hashtags fornecida, escolha 2 hashtags e busque posts relacionados. "
#         "Hashtags disponíveis: " + ", ".join(hashtags) + "."
#         "Não invente código. Não simule resultados. "
#         "Passe os parâmetros corretos: target_hashtag_for_liking como string e amount como número inteiro. "
#         "Retorne exatamente o que a ferramenta retornar.",
#     ),
#     expected_output="Lista de posts com comentários em formato JSON com os campos id e pk.",
#     tool_call_limit=2
# )


# loaded_agent.print_response(f"Use a ferramenta load_instagram_session para fazer login no Instagram com o nome de usuário {USERNAME} e a senha {PASSWORD}, e retorne o resultado.", stream=True)

# resp: RunOutput = monitoring_agent.run(f"Quais posts recentes com a hashtag {hashtags}?")
# context = resp.content

# pprint(context)

# json_data = load_json_from_response(context)

# ids_recuperados = [post["id"] for post in json_data]
# print("IDs recuperados:", ids_recuperados)

# def get_comments():

#     comments = []
#     for post in ids_recuperados:
#         comment = fetch_comments_for_post(media_id=post, amount=5)
#         comments.append({post: comment})
#     return comments

# comments_data = get_comments()

# sentiment_agent = Agent(
#     # model=OpenAIChat(
#     #     api_key=os.environ.get("GROQ_API_KEY"),
#     #     base_url="https://api.groq.com/openai/v1",
#     #     id="openai/gpt-oss-20b"
#     # ),
#     model=Ollama("qwen2.5:7b"),
#     markdown=True,
#     description="Agente de análise de sentimentos dos comentários.",
#     instructions=(
#         "Analise os comentários fornecidos e retorne os IDs dos usuários que fizeram comentários positivos. "
#         f"O dado de entrada é : {comments_data}. "
#         "Considere um comentário positivo aquele que expressa satisfação, alegria ou aprovação. "
#         "Retorne os resultados em formato JSON com o campo user_id, username, comentário e por que acha que é positivo o comentário."
#     ),
#     expected_output=(
#         "Formato JSON deve ser sempre respeitado:"
#         "```json\n"
#         "[\n"
#         "  {\n"
#         "    \"user_id\": \"123456789\",\n"
#         "    \"username\": \"usuario_exemplo\",\n"
#         "    \"comment\": \"Adorei o design! Muito inspirador.\",\n"
#         "    \"reason\": \"O comentário expressa satisfação e aprovação do design apresentado.\"\n"
#         "  }\n"
#         "]\n"
#         "```"
#     )
# )

# resp_post : RunOutput = sentiment_agent.run(f"Use o ID do post nesse json {ids_recuperados} para buscar os comentários desse post.")
# post_context = resp_post.content
# print("Contexto do post:", post_context)

# json_sentiment_data = load_json_from_response(post_context)
# pprint(json_sentiment_data)