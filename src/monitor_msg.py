import threading
import time
import json
import os
import random
from agno.agent import RunOutput
from .utils import autenticar_instagram, load_json_from_response, delete_json_key
from .agents_message import analitic_agent, message_agent, email_agent

class InstagramMonitor:
    def __init__(self):
        self.running = False
        self.thread = None
        self.results = {}
        self.json_file = "infos_comments.json"
        self.user_ids_list = self._load_user_ids()
        self.last_processed_messages = {}  # ✅ Controla mensagens já processadas

    def _load_user_ids(self):
        """Carrega user_ids do arquivo JSON com validação robusta."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if not isinstance(data, list):
                        print(f"[AVISO] {self.json_file} não contém uma lista. Resetando...")
                        return []
                    
                    user_ids = []
                    for item in data:
                        if isinstance(item, dict) and 'user_id' in item:
                            user_ids.append(str(item['user_id']))
                    
                    print(f"[INFO] Carregados {len(user_ids)} user_ids válidos")
                    return user_ids
                    
            except Exception as e:
                print(f"[ERRO] Erro ao carregar user_ids: {e}")
                return []
        else:
            print(f"[INFO] Criando {self.json_file}...")
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []

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

        if isinstance(user_ids, str):
            user_ids = [user_ids]

        # ✅ Pega o user_id da própria conta
        my_user_id = str(cl.user_id)
        print(f"[INFO] Meu user_id: {my_user_id}")

        self.results = {}
        print(f"[INFO] Monitorando {len(user_ids)} usuários: {user_ids}")

        while self.running:
            try:
                print("\n🔄 Verificando novas mensagens...")
                threads = cl.direct_threads(amount=20)

                for thread in threads:
                    thread_id = str(thread.id)
                    
                    if not hasattr(thread, "messages") or not thread.messages:
                        continue

                    # ✅ Identifica usuários na thread
                    thread_users = [str(u.pk) for u in thread.users] if thread.users else []
                    
                    # Verifica se tem algum usuário monitorado
                    monitored_user = None
                    for uid in user_ids:
                        if str(uid) in thread_users:
                            monitored_user = str(uid)
                            break
                    
                    if not monitored_user:
                        continue  # Pula threads sem usuários monitorados

                    print(f"\n📍 Thread {thread_id}")
                    print(f"   Usuário monitorado: {monitored_user}")
                    print(f"   Total de mensagens: {len(thread.messages)}")

                    # ✅ FILTRA: Apenas mensagens DO USUÁRIO (não suas)
                    user_messages = [
                        msg for msg in thread.messages
                        if str(msg.user_id) == monitored_user 
                        and msg.text  # Tem texto
                        and str(msg.user_id) != my_user_id  # Não é sua mensagem
                    ]

                    if not user_messages:
                        print(f"   ⏭️ Sem mensagens novas do usuário")
                        continue

                    print(f"   📨 {len(user_messages)} mensagens do usuário encontradas")
                    print(f"   Mensagens: {[m.text for m in user_messages[:5]]}")

                    # Pega a última mensagem do usuário
                    last_user_msg = user_messages[0]
                    msg_id = str(last_user_msg.id) if hasattr(last_user_msg, 'id') else f"{thread_id}_{last_user_msg.text[:10]}"
                    msg_text = last_user_msg.text

                    # ✅ Verifica se já processou esta mensagem
                    if thread_id in self.last_processed_messages:
                        if self.last_processed_messages[thread_id] == msg_id:
                            print(f"   ⏭️ Mensagem já processada")
                            continue

                    print(f"   🆕 NOVA MENSAGEM: '{msg_text}'")

                    # Pega últimas 10 mensagens do usuário para contexto
                    context_messages = user_messages[:10]
                    context_texts = [m.text for m in context_messages]

                    # --- Análise de sentimento ---
                    print(f"   📊 Analisando sentimento...")
                    try:
                        analisy: RunOutput = analitic_agent.run(
                            f"Analise o sentimento da mensagem do usuário {monitored_user}: '{msg_text}'"
                        )
                        
                        parsed = load_json_from_response(analisy.content)
                        
                        if not parsed:
                            print(f"   ⚠️ Falha ao parsear análise")
                            continue

                        print(f"   ✅ Análise: {parsed}")

                        # Garante que parsed seja uma lista
                        if isinstance(parsed, dict):
                            parsed = [parsed]

                        for entry in parsed:
                            # Verifica se tem contato
                            if entry.get("contato"):
                                contato = entry["contato"]
                                print(f"   📞 CONTATO OBTIDO: {contato}")
                                
                                # Encerra conversa
                                message_agent.run(
                                    f"Envie mensagem de agradecimento e encerre a conversa com o usuário {monitored_user} comentando que entraremos em contato."
                                )
                                delete_json_key(monitored_user)
                                user_ids.remove(monitored_user)
                                
                                self.results[monitored_user] = {
                                    "thread_id": thread_id,
                                    "action": "encerrado",
                                    "reason": "contato encontrado",
                                    "contato": contato
                                }
                                
                                # Envia email
                                try:
                                    email_response: RunOutput = email_agent.run(
                                        f"Envie email com contato: {contato}"
                                    )
                                    self.results[monitored_user]["email_status"] = "enviado"
                                    print(f"   ✅ Email enviado")
                                except Exception as e:
                                    print(f"   ⚠️ Erro ao enviar email: {e}")
                                    self.results[monitored_user]["email_status"] = f"erro: {e}"
                                
                                if not user_ids:
                                    print("\n✅ Todos processados!")
                                    self.running = False
                                    return
                                
                                break

                            # Verifica sentimento
                            sentimento = entry.get("analise_sentimento", "Neutro")
                            print(f"   😊 Sentimento: {sentimento}")

                            if sentimento == "Negativo":
                                print(f"   🚫 Sentimento negativo, encerrando")
                                
                                # Envia despedida
                                farewell = (
                                    "Entendo! Obrigado pelo seu tempo. "
                                    "Se mudar de ideia, estamos à disposição. "
                                    "Tenha um ótimo dia! 😊"
                                )
                                time.sleep(random.uniform(10, 40))
                                cl.direct_send(farewell, thread_ids=[thread_id])
                                print(f"   ✅ Despedida enviada")
                                
                                delete_json_key(monitored_user)
                                user_ids.remove(monitored_user)
                                
                                self.results[monitored_user] = {
                                    "thread_id": thread_id,
                                    "action": "encerrado",
                                    "reason": "sentimento negativo"
                                }
                                
                                if not user_ids:
                                    print("\n✅ Todos processados!")
                                    self.running = False
                                    return
                                
                                break

                        # --- Gerar resposta ---
                        print(f"   💭 Gerando resposta...")
                        try:
                            # Tenta usar o agente
                            msg_response: RunOutput = message_agent.run(
                                f"Contexto (últimas mensagens): {context_texts}. "
                                f"Análise: {parsed}. "
                                f"Envie resposta apropriada para usuário {monitored_user} "
                                f"usando a ferramenta send_direct_message."
                            )
                            
                            print(f"   ✅ Resposta enviada pelo agente")
                            
                            self.results[monitored_user] = {
                                "thread_id": thread_id,
                                "action": "respondido",
                                "response": msg_response.content[:100]
                            }

                        except Exception as agent_error:
                            print(f"   ⚠️ Agente falhou: {agent_error}")
                            print(f"   📤 Enviando resposta direta...")
                            
                            # Fallback: resposta manual baseada no sentimento
                            if sentimento == "Positivo":
                                response_text = (
                                    "Que ótimo! 😊 Para te ajudar melhor, "
                                    "poderia me passar seu WhatsApp ou telefone? "
                                    "Assim consigo enviar ideias e orçamentos personalizados!"
                                )
                            else:  # Neutro
                                response_text = (
                                    "Entendi! 👍 Trabalhamos com projetos personalizados "
                                    "em design de interiores e móveis planejados. "
                                    "Você tem algum ambiente específico em mente?"
                                )
                            
                            time.sleep(random.uniform(10, 40))
                            cl.direct_send(response_text, thread_ids=[thread_id])
                            
                            print(f"   ✅ Resposta enviada: {response_text[:50]}...")
                            
                            self.results[monitored_user] = {
                                "thread_id": thread_id,
                                "action": "respondido",
                                "response": response_text
                            }

                        # Marca como processada
                        self.last_processed_messages[thread_id] = msg_id

                    except Exception as e:
                        print(f"   ❌ Erro ao processar: {e}")
                        self.results[monitored_user] = {
                            "thread_id": thread_id,
                            "action": "erro",
                            "error": str(e)
                        }
                        continue

            except Exception as e:
                print(f"❌ Erro geral no monitor: {e}")
                self.results["error"] = str(e)

            print(f"\n⏱️ Aguardando {random.uniform(6, 20):.1f}s...")
            time.sleep(random.uniform(6, 20))  # Delay aumentado para evitar bloqueios