from agno.agent import RunOutput
from utils import autenticar_instagram, load_json_from_response, delete_json_key
from agents_message import analitic_agent, message_agent
import json
import time
import datetime

with open("infos_comments.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    user_ids_list = [item['user_id'] for item in data]

hoje = datetime.date.today()

def monitor_instagram_messages(user_ids: list[str] | str = ["56295393358"]):
    """
    Docstring para monitor_instagram_messages
    
    :param user_ids: Lista de IDs de usuários do Instagram para monitorar mensagens diretas.
    :type user_ids: list[str] | None
    """
    
    cl = autenticar_instagram()

    if isinstance(user_ids, str):
        user_ids = [user_ids]
    elif isinstance(user_ids, list):
        user_ids = user_ids
        print("user_ids fornecidos como lista.")
    else:
        user_ids = []
        print("user_ids fornecidos em formato inválido. Usando lista vazia.")

    
    print(f"Monitorando mensagens diretas para user_ids: {user_ids}")

    results = {}

    while True:
        try:
            messages = cl.direct_threads()
            for thread in messages:
                if not getattr(thread, "messages", None):
                    continue

                # lista de user_ids na thread (strings)
                usuario_ids = [str(msg.user_id) for msg in thread.messages if getattr(msg, "user_id", None) is not None]
                if not usuario_ids:
                    continue

                # para cada user_id fornecido, checar presença nessa thread
                for uid in user_ids:
                    uid = str(uid)
                    if uid not in usuario_ids:
                        continue

                    print(f"\n--- DEBUG: Thread {getattr(thread, 'id', None)} ---")
                    for i, msg in enumerate(thread.messages):
                        print(f"Msg {i}: '{getattr(msg, 'text', '')}' de user_id {getattr(msg, 'user_id', None)}")
                    print("--- FIM DEBUG ---\n")

                    # última mensagem geral (mais recente)
                    ultima_geral = thread.messages[0]
                    print(f"Ultima mensagem na thread {getattr(thread, 'id', None)}: {getattr(ultima_geral, 'text', None)} de user_id {getattr(ultima_geral, 'user_id', None)}")

                    # se última mensagem NÃO for do usuário alvo -> não enviar (aguardar)
                    if str(ultima_geral.user_id) != uid:
                        print(f"Aguardando resposta do usuário {uid}, sendo que a ultima mensagem é do user_id {ultima_geral.user_id}.")
                        results[uid] = {
                            "thread_id": getattr(thread, "id", None),
                            "action": "aguardar",
                            "last_message_text": getattr(ultima_geral, "text", None)
                        }
                        continue

                    # última mensagem DO usuário alvo (mais recente mensagem do uid)
                    ultima_mensagem_usuario = next((m for m in thread.messages if str(m.user_id) == uid), None)
                    print(f"Ultima mensagem do usuário {uid} na thread {getattr(thread, 'id', None)}: {getattr(ultima_mensagem_usuario, 'text', None)}")
                    texto = getattr(ultima_mensagem_usuario, "text", "") if ultima_mensagem_usuario else ""


                    # analisa sentimento usando analitic_agent (assume agente definido globalmente)
                    try:
                        analisy: RunOutput = analitic_agent.run(f"Analise o sentimento da seguinte mensagem: {texto}")
                        parsed = load_json_from_response(analisy.content)
                        print(f"Análise de sentimento para user_id {uid}: {parsed}")

                        for i, entry in enumerate(parsed):
                            print(entry["analise_sentimento"])
                            if entry["analise_sentimento"] == "Negativo":
                                delete_json_key(uid)
                                results[uid] = {"thread_id": getattr(thread, "id", None), "action": "encerrado", "reason": "sentimento negativo"}
                                continue
                                

                    except Exception as e:
                        results[uid] = {"thread_id": getattr(thread, "id", None), "action": "erro_analise", "error": str(e)}
                        continue

                    # compor e enviar resposta usando message_agent (assume ferramenta send_direct_message disponível)
                    try:
                        msg_to_send = message_agent.run(f"Baseado na análise {parsed}, envie resposta apropriada para {uid}")
                        results[uid] = {"thread_id": getattr(thread, "id", None), "action": "respondido", "response": msg_to_send.content}
                    except Exception as e:
                        results[uid] = {"thread_id": getattr(thread, "id", None), "action": "erro_envio", "error": str(e)}
            print(results)

        except Exception as e:
            print(f"Erro ao receber mensagens diretas: {e}")
            return {"error": str(e)}
        
        time.sleep(20)  # aguardar antes de checar novamente

# Iniciar monitoramento (exemplo)
monitor_instagram_messages()

