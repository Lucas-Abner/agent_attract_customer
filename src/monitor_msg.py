# monitor.py
import threading
import time
import json
import datetime
from agno.agent import RunOutput
from .utils import autenticar_instagram, load_json_from_response, delete_json_key
from .agents_message import analitic_agent, message_agent

class InstagramMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.results = {}
        self.user_ids_list = self._load_user_ids()

    def _load_user_ids(self):
        with open("infos_comments.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return [item['user_id'] for item in data]

    def start(self, user_ids=None):
        if self.running:
            return "Monitor já está rodando."

        self.running = True
        self.thread = threading.Thread(
            target=self.monitor_instagram_messages,
            args=(user_ids or self.user_ids_list,),
            daemon=True
        )
        self.thread.start()
        return "Monitor iniciado."

    def stop(self):
        if not self.running:
            return "Monitor já está parado."
        self.running = False
        return "Monitor encerrado."

    def get_status(self):
        return {
            "running": self.running,
            "results": self.results
        }

    def monitor_instagram_messages(self, user_ids):
        cl = autenticar_instagram()

        # aceita string ou lista
        if isinstance(user_ids, str):
            user_ids = [user_ids]

        self.results = {}
        print(f"Monitorando mensagens para: {user_ids}")

        while self.running:
            try:
                messages = cl.direct_threads()

                for thread in messages:
                    if not hasattr(thread, "messages") or not thread.messages:
                        continue

                    usuario_ids = [
                        str(msg.user_id)
                        for msg in thread.messages
                        if hasattr(msg, "user_id")
                    ]

                    if not usuario_ids:
                        continue

                    for uid in user_ids:
                        uid = str(uid)

                        if uid not in usuario_ids:
                            continue

                        ultima_geral = thread.messages[0]

                        # se a última msg não for do usuário → aguarda
                        if str(ultima_geral.user_id) != uid:
                            self.results[uid] = {
                                "thread_id": getattr(thread, "id", None),
                                "action": "aguardar",
                                "last_message_text": ultima_geral.text
                            }
                            print(f"Aguardando nova mensagem de {uid}...")
                            continue

                        ultima_mensagem_usuario = next(
                            (m for m in thread.messages if str(m.user_id) == uid),
                            None
                        )

                        messagens_usuario = [m for m in thread.messages if str(m.user_id) == uid]
                        ultimas_10_msgs = messagens_usuario[0:] if len(messagens_usuario) >= 10 else messagens_usuario

                        print(f"Últimas mensagens do usuário {uid}: {[m.text for m in ultimas_10_msgs]}")
                        print(f"Contagem de mensagens na thread {thread.id}: {len(thread.messages)}")

                        texto = ultima_mensagem_usuario.text if ultima_mensagem_usuario else ""

                        # --- Análise de sentimento ---
                        try:
                            analisy: RunOutput = analitic_agent.run(
                                f"Analise o sentimento da seguinte mensagem: {texto}"
                            )
                            parsed = load_json_from_response(analisy.content)

                            for entry in parsed:
                                if entry["analise_sentimento"] == "Negativo":
                                    delete_json_key(uid)
                                    self.results[uid] = {
                                        "thread_id": thread.id,
                                        "action": "encerrado",
                                        "reason": "sentimento negativo"
                                    }
                                    continue

                        except Exception as e:
                            self.results[uid] = {
                                "thread_id": thread.id,
                                "action": "erro_analise",
                                "error": str(e)
                            }
                            continue

                        # --- Gerar resposta ---
                        try:
                            msg_to_send = message_agent.run(
                                f"Receba as 10 ultimas mensagens do usuario como contexto: {[m.text for m in ultimas_10_msgs]}. "
                                f"Baseado na análise {parsed}, envie resposta apropriada para {uid}"
                            )
                            self.results[uid] = {
                                "thread_id": thread.id,
                                "action": "respondido",
                                "response": msg_to_send.content
                            }

                        except Exception as e:
                            self.results[uid] = {
                                "thread_id": thread.id,
                                "action": "erro_envio",
                                "error": str(e)
                            }

            except Exception as e:
                print(f"Erro geral: {e}")
                self.results["error"] = str(e)

            time.sleep(10) 