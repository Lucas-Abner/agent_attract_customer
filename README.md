# Agent Attract Customer

Um sistema automatizado de atração e qualificação de clientes potenciais através do Instagram, especializado em design de interiores e móveis planejados.

## 📋 Descrição

Este projeto utiliza agentes de IA para automatizar o processo de:
1. **Monitoramento de hashtags** relevantes no Instagram
2. **Análise de comentários** para identificar leads qualificados
3. **Engajamento automático** via mensagens diretas
4. **Monitoramento contínuo** de conversas para nutrição de leads
5. **Análise de sentimento** para personalizar interações

## 🏗️ Arquitetura

### Estrutura de Diretórios

```
agent_attract_customer/
├── main.py                      # API FastAPI principal
├── src/
│   ├── agent.py                 # Pipeline principal de agentes
│   ├── agents_message.py        # Agentes de análise e resposta
│   ├── monitor_msg.py           # Monitor de mensagens em tempo real
│   ├── tools.py                 # Ferramentas Instagram (login, posts, DM)
│   ├── utils.py                 # Funções utilitárias
│   └── send_email.py            # Integração com Resend para emails
├── infos_comments.json          # Banco de dados de leads qualificados
├── hashtag.txt                  # Lista de hashtags para monitoramento
├── session_instagram.json       # Sessão persistente do Instagram
└── .env                         # Variáveis de ambiente
```

## 🚀 Funcionalidades Principais

### 1. Pipeline de Captação de Leads (`src/agent.py`)

O pipeline executa as seguintes etapas:

```python
run_instagram_pipeline(hashtags)
```

- **Login Automático**: Autentica no Instagram usando `load_instagram_session`
- **Busca de Posts**: Usa `fetch_posts` para encontrar posts recentes com hashtags específicas
- **Coleta de Comentários**: Extrai comentários usando `fetch_comments_for_post`
- **Análise de Sentimento**: Identifica usuários com intenção de compra via agente de IA
- **Contato Inicial**: Envia mensagens personalizadas para leads qualificados

### 2. Monitor de Conversas (`src/monitor_msg.py`)

Sistema de monitoramento contínuo que:

- Verifica novas mensagens a cada 10 segundos
- Analisa sentimento das respostas (Positivo/Neutro/Negativo)
- Detecta informações de contato (telefone, email, WhatsApp)
- Responde automaticamente com base no contexto da conversa
- Remove leads não qualificados (sentimento negativo ou contato obtido)

### 3. API REST (`main.py`)

Endpoints disponíveis:

```bash
GET  /              # Status da aplicação
POST /run_pipeline  # Executa pipeline de captação
POST /start_monitor # Inicia monitoramento de conversas
POST /stop          # Para o monitoramento
GET  /status        # Status do monitor
```

## 🛠️ Tecnologias Utilizadas

### Frameworks e Bibliotecas

- **[FastAPI](https://fastapi.tiangolo.com/)**: API REST assíncrona
- **[Agno](https://github.com/agno-ai/agno)**: Framework de agentes de IA
- **[Instagrapi](https://github.com/subzeroid/instagrapi)**: Automação do Instagram
- **[OpenAI/Groq](https://groq.com/)**: Modelos de linguagem para análise
- **[Ollama](https://ollama.ai/)**: Execução local de LLMs
- **[Resend](https://resend.com/)**: Envio de emails transacionais
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Validação de dados

### Modelos de IA Utilizados

- **GPT-OSS-20B** (via Groq): Análise de sentimento e geração de respostas
- **Llama 3.1 8B**: Orquestração de ferramentas
- **Qwen 2.5 7B**: Processamento de threads

## 📦 Instalação

### Requisitos

- Python 3.12 ou 3.13
- Conta no Instagram
- API Keys: Groq e Resend

### Passo a Passo

1. **Clone o repositório**

```bash
git clone <seu-repositorio>
cd agent_attract_customer
```

2. **Instale o UV (gerenciador de pacotes)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Instale as dependências**

```bash
uv sync
```

4. **Instale a versão específica do Instagrapi**

```bash
uv add "git+https://github.com/subzeroid/instagrapi.git"
```

5. **Configure as variáveis de ambiente**

Crie um arquivo .env na raiz do projeto:

```env
LOGIN_USERNAME="seu_usuario_instagram"
LOGIN_PASSWORD="sua_senha"
GROQ_API_KEY="sua_api_key_groq"
RESEND_API_KEY="sua_api_key_resend"
```

6. **Configure as hashtags**

Edite o arquivo hashtag.txt com suas hashtags (uma por linha):

```txt
arquitetura
designdeinteriores
moveisplanejados
```

## 🎯 Como Usar

### 1. Iniciar a API

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`

### 2. Executar Pipeline de Captação

```bash
curl -X POST http://localhost:8000/run_pipeline \
  -H "Content-Type: application/json" \
  -d '{"hashtags": ["designdeinteriores", "moveisplanejados"]}'
```

### 3. Iniciar Monitoramento de Conversas

```bash
curl -X POST http://localhost:8000/start_monitor \
  -H "Content-Type: application/json" \
  -d '{"user_ids": ["123456789", "987654321"]}'
```

### 4. Verificar Status

```bash
curl http://localhost:8000/status
```

## 🤖 Agentes de IA

### 1. `sentiment_agent`

**Função**: Analisa comentários e identifica leads qualificados

**Critérios de Qualificação**:
- Perguntas sobre preço, disponibilidade ou características
- Intenção de compra explícita
- Necessidade relacionada ao produto
- Solicitação de informações ou contato

**Saída**: JSON com `user_id`, `comentario` e `razao_qualificacao`

### 2. `initial_agent`

**Função**: Inicia conversas com leads qualificados

**Características**:
- Apresenta a empresa (InteriArt)
- Menciona área de atuação
- Cria mensagens personalizadas
- Convida para diálogo sem ser invasivo

### 3. `analitic_agent`

**Função**: Analisa sentimento de mensagens recebidas

**Detecta**:
- Sentimento (Positivo/Neutro/Negativo)
- Informações de contato (telefone, email, WhatsApp)
- Intenção de compra

### 4. `message_agent`

**Função**: Gera respostas contextualizadas

**Estratégias**:
- **Positivo**: Solicita contato educadamente
- **Neutro**: Faz perguntas abertas
- **Negativo**: Encerra cortesmente

## 📊 Estrutura de Dados

### infos_comments.json

Armazena leads qualificados:

```json
[
  {
    "user_id": "1914727865",
    "comentario": "Quero saber mais sobre esse projeto",
    "razao_qualificacao": "Expressa interesse direto em conhecer o produto"
  }
]
```

## 🔧 Funções Principais

### Autenticação (`src/utils.py`)

```python
autenticar_instagram()  # Gerencia sessão do Instagram
```

### Busca de Posts (`src/tools.py`)

```python
fetch_posts(target_hashtag_for_liking=["design"], amount=6)
```

### Envio de Mensagens (`src/tools.py`)

```python
send_direct_message(id="123456789", message_to_direct="Olá!")
```

### Análise de Threads (`src/tools.py`)

```python
return_infos_thread(user_id="123456789")
```

## ⚠️ Considerações Importantes

### Limites do Instagram

- **Delay entre ações**: 2-5 segundos (simulação humana)
- **Rate limiting**: Respeite os limites da API não oficial
- **Risco de ban**: Use com moderação

### Boas Práticas

1. **Não abuse das hashtags**: Máximo 3-5 por execução
2. **Monitore apenas leads qualificados**: Evite spam
3. **Personalize mensagens**: Não use templates genéricos
4. **Respeite o GDPR**: Obtenha consentimento para armazenar dados

## 🐛 Troubleshooting

### Erro de autenticação

```bash
# Remova a sessão antiga
rm session_instagram.json
# Execute novamente
```

### ValidationError no Pydantic

O código já possui tratamento para erros de validação em tools.py (linha 143-150)

### JSON inválido

A função `load_json_from_response` possui múltiplas estratégias de parsing

## 📈 Melhorias Futuras

- [ ] Dashboard web para visualização de métricas
- [ ] Integração com CRM (HubSpot, Salesforce)
- [ ] Análise de perfil antes do contato
- [ ] Sistema de templates de mensagens
- [ ] Relatórios automáticos por email
- [ ] Suporte a múltiplas contas do Instagram

## 📄 Licença

Este projeto é de uso educacional. Respeite os Termos de Uso do Instagram.

## 👤 Autor

**Lucas Caixeta**
- Email: lucascaixeta02@gmail.com

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor:
1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

**⚠️ AVISO**: Este projeto utiliza automação do Instagram através de APIs não oficiais. Use por sua conta e risco.