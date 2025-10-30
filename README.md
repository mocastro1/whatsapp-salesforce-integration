# WhatsApp Bot com IA# WhatsApp Salesforce Integration



Sistema de chatbot WhatsApp com resposta automática por IA (GitHub Models / Copilot), usando Evolution API como gateway e webhook FastAPI para processamento em tempo real.Sistema de integração entre WhatsApp e Salesforce usando Evolution API, webhook FastAPI e IA GitHub Models.



## 🎯 Funcionalidades## 🎯 Funcionalidades



- ✅ **Captura de Mensagens**: Recebe todas as mensagens do WhatsApp em tempo real- ✅ **Captura de Mensagens**: Recebe e armazena todas as mensagens do WhatsApp

- ✅ **Resposta Automática com IA**: Processa mensagens com GitHub Models/Copilot- ✅ **Resposta Automática**: Responde mensagens de números monitorados usando IA

- ✅ **Monitoramento de Números**: Responde automaticamente mensagens de números específicos- 🚧 **Consultas Salesforce**: Consultas em linguagem natural ao Salesforce (em desenvolvimento)

- 📊 **Logs Estruturados**: Armazena conversas em JSON por data e por número- 📊 **Logs Estruturados**: Armazenamento organizado de conversas e eventos

- 🚀 **Zero Setup Complexity**: Tudo rodando localmente com Docker

## 🏗️ Arquitetura

## 🏗️ Arquitetura

```

```WhatsApp ↔ Evolution API ↔ Webhook ↔ IA GitHub ↔ Salesforce

WhatsApp ↔ Evolution API (Docker) ↔ Localtunnel (URL pública) ```

                                    ↓

                            Webhook FastAPI### Componentes

                                    ↓

                        GitHub Models / Copilot IA- **Evolution API**: Gateway WhatsApp (Docker)

                                    ↓- **Webhook FastAPI**: Processamento de mensagens (`webhook_captura_mensagens.py`)

                            Resposta → WhatsApp- **Localtunnel**: Exposição pública do webhook local

```- **GitHub Models**: IA para processamento de linguagem natural

- **Salesforce**: CRM para consultas e integrações

## 🚀 Quick Start

## 🚀 Quick Start

### 1. Pré-requisitos

### 1. Pré-requisitos

```bash

# Python 3.12+```bash

# Node.js (para localtunnel)# Python 3.12+

# Docker (para Evolution API)# Node.js (para localtunnel)

```# Docker (para Evolution API)

```

### 2. Setup

### 2. Configuração

1. **Clonar e instalar**:

```bash1. **Clone e instale dependências**:

git clone https://github.com/mocastro1/whatsapp-salesforce-integration.git```bash

cd whatsapp-salesforce-integrationgit clone <repository-url>

pip install -r requirements.txtcd SalesForce

npm installpip install -r requirements.txt

```npm install

```

2. **Configurar variáveis de ambiente**:

```bash2. **Configure variáveis de ambiente**:

cp .env.example .env```bash

# Edite .env com sua chave GitHubcp .env.example .env

GITHUB_TOKEN=seu_token_github# Edite .env com suas credenciais

``````



3. **Iniciar serviços**:3. **Inicie os serviços**:

```powershell```powershell

.\INICIAR_SERVICOS.ps1.\INICIAR_SERVICOS.ps1

``````



4. **Configurar webhook no Evolution**:4. **Configure o webhook**:

```powershell```powershell

.\reconfigurar_webhook.ps1.\reconfigurar_webhook.ps1

``````



### 3. Como Usar### 3. Variáveis de Ambiente



- Envie uma mensagem para o número monitorado (padrão: `556596977000`)```env

- O webhook captura, envia para a IA processar# GitHub AI

- A IA responde automaticamenteGITHUB_TOKEN=seu_token_github



## 📁 Estrutura# Evolution API

EVOLUTION_API_KEY=evolution_api_key_2025

```

├── webhook_captura_mensagens.py   # 🎯 Webhook principal# Salesforce (futuro)

├── INICIAR_SERVICOS.ps1           # 🚀 Inicialização dos serviçosSF_USERNAME=seu_usuario@salesforce.com

├── configurar_webhook.ps1         # ⚙️ Configura webhook EvolutionSF_PASSWORD=sua_senha

├── reconfigurar_webhook.ps1       # 🔄 Reconfigura webhookSF_SECURITY_TOKEN=seu_token

├── mensagens_recebidas/           # 📊 Logs de mensagens (auto-criado)```

├── conversations/                 # 💬 Conversas por número (auto-criado)

├── src/                           # Código fonte modular## 📁 Estrutura do Projeto

│   ├── chatbot/                   # Chatbot utilities

│   ├── integration/               # Integrações (Evolution, etc)```

│   └── transcription/             # Processamento de áudio (opcional)├── src/                          # Código fonte principal

└── docs/                          # Documentação│   ├── chatbot/                  # Módulos de chatbot

```│   ├── integration/              # Integrações externas

│   ├── salesforce/               # Cliente Salesforce

## ⚙️ Configuração│   └── transcription/            # Processamento de áudio

├── docs/                         # Documentação

### Mudar o Número Monitorado├── mensagens_recebidas/          # Mensagens capturadas (auto-criado)

├── conversations/                # Conversas por número (auto-criado)

Edite `webhook_captura_mensagens.py`:├── webhook_captura_mensagens.py  # 🎯 Webhook principal

```python├── INICIAR_SERVICOS.ps1          # 🚀 Script de inicialização

NUMERO_MONITORADO = "556596977000"  # seu número aqui├── configurar_webhook.ps1        # ⚙️ Configuração webhook

```└── reconfigurar_webhook.ps1      # 🔄 Reconfiguração webhook

```

### Variáveis de Ambiente Essenciais

## 🎮 Uso

```env

# GitHub IA (obrigatório)### Iniciar Sistema

GITHUB_TOKEN=seu_token_github```powershell

.\INICIAR_SERVICOS.ps1

# Evolution API```

EVOLUTION_API_KEY=evolution_api_key_2025

EVOLUTION_API_URL=http://localhost:3001### Monitorar Logs

INSTANCE_NAME=salesforce-bot- Mensagens: `mensagens_recebidas/mensagens_YYYYMMDD.json`

- Conversas: `mensagens_recebidas/conversas_<numero>.json`

# Webhook- Status: `http://localhost:8000/status`

WEBHOOK_PORT=8000

```### Endpoints Disponíveis

- `GET /status` - Status do webhook

## 🔗 Endpoints Disponíveis- `POST /webhook` - Endpoint para Evolution API

- `GET /mensagens` - Listar mensagens capturadas

```- `GET /conversas` - Listar conversas por número

GET  /status         - Status do webhook

POST /webhook        - Recebe eventos do Evolution## 🔧 Configuração Avançada

GET  /mensagens      - Lista últimas mensagens

GET  /conversas      - Lista conversas por número### Mudar Webhook Ativo

GET  /               - Info do webhookEdite `INICIAR_SERVICOS.ps1`:

``````powershell

$WEBHOOK_SCRIPT = 'webhook_captura_mensagens.py'  # webhook desejado

## 📊 Logs e Monitoramento```



### Verificar Status### Configurar Número Monitorado

```bashEdite `webhook_captura_mensagens.py`:

curl http://localhost:8000/status```python

```NUMERO_MONITORADO = "556596977000"  # número para resposta automática

```

### Ver Mensagens Capturadas

```bash### Logs e Debug

curl http://localhost:8000/mensagens- Logs do webhook: console da janela PowerShell

```- Logs Evolution: `docker logs evolution_api`

- Status serviços: `docker ps`

### Logs em Arquivo

- Mensagens: `mensagens_recebidas/mensagens_YYYYMMDD.json`## 🤝 Contribuição

- Conversas: `mensagens_recebidas/conversas_<numero>.json`

1. Fork o projeto

## 🐛 Troubleshooting2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)

3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)

| Problema | Solução |4. Push para a branch (`git push origin feature/nova-funcionalidade`)

|----------|---------|5. Abra um Pull Request

| **Webhook não responde** | Verifique se o localtunnel está rodando e o URL foi registrado no Evolution Manager |

| **Evolution API não conecta** | Verifique `docker ps` e logs com `docker logs evolution_api` |## 📞 Suporte

| **IA não responde** | Verifique se `GITHUB_TOKEN` está configurado e válido no `.env` |

| **Mensagens não são capturadas** | Reinicie o webhook: `.\INICIAR_SERVICOS.ps1` |- **Webhook não responde**: Verifique se o localtunnel está ativo e o webhook configurado

- **Evolution API**: Verifique `docker ps` e logs com `docker logs evolution_api`

## 🤝 Comandos Úteis- **IA não funciona**: Verifique `GITHUB_TOKEN` no `.env`



```powershell## 🎯 Roadmap

# Iniciar tudo

.\INICIAR_SERVICOS.ps1- [ ] Integração completa Salesforce (consultas SOQL)

- [ ] Interface web para monitoramento

# Reconfigurar webhook após trocar a URL do localtunnel- [ ] Suporte a múltiplos números monitorados

.\reconfigurar_webhook.ps1- [ ] Templates de resposta configuráveis

- [ ] Dashboard analytics

# Verificar status do Evolution API

docker ps## 📄 Licença

docker logs evolution_api

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

# Parar webhook

# (usar Ctrl+C na janela do webhook)---

```

**Status**: ✅ Webhook funcional | 🚧 Integração Salesforce em desenvolvimento

## 📝 Exemplo de Conversa

**Usuário**: Oi, tudo bem?

**Bot**: Oi! Tudo certo por aqui. Como posso ajudar? 😊

**Usuário**: Como está o sistema?

**Bot**: O sistema está funcionando perfeitamente! O webhook está online e capturando mensagens em tempo real. Pronto para ajudá-lo com qualquer coisa.

## 🎯 Próximos Passos

- [ ] Adicionar persistência de histórico (BD)
- [ ] Multi-número monitorado
- [ ] Templates de resposta customizáveis
- [ ] Análise de sentimento das mensagens
- [ ] Dashboard web de monitoramento

## 📄 Licença

MIT - Veja LICENSE para detalhes.

---

**Status**: ✅ Sistema funcional e em produção

**Mantido por**: [mocastro1](https://github.com/mocastro1)

**Última atualização**: 30/10/2025