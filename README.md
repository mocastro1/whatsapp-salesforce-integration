# WhatsApp Salesforce Integration

Sistema de integração entre WhatsApp e Salesforce usando Evolution API, webhook FastAPI e IA GitHub Models.

## 🎯 Funcionalidades

- ✅ **Captura de Mensagens**: Recebe e armazena todas as mensagens do WhatsApp
- ✅ **Resposta Automática**: Responde mensagens de números monitorados usando IA
- 🚧 **Consultas Salesforce**: Consultas em linguagem natural ao Salesforce (em desenvolvimento)
- 📊 **Logs Estruturados**: Armazenamento organizado de conversas e eventos

## 🏗️ Arquitetura

```
WhatsApp ↔ Evolution API ↔ Webhook ↔ IA GitHub ↔ Salesforce
```

### Componentes

- **Evolution API**: Gateway WhatsApp (Docker)
- **Webhook FastAPI**: Processamento de mensagens (`webhook_captura_mensagens.py`)
- **Localtunnel**: Exposição pública do webhook local
- **GitHub Models**: IA para processamento de linguagem natural
- **Salesforce**: CRM para consultas e integrações

## 🚀 Quick Start

### 1. Pré-requisitos

```bash
# Python 3.12+
# Node.js (para localtunnel)
# Docker (para Evolution API)
```

### 2. Configuração

1. **Clone e instale dependências**:
```bash
git clone <repository-url>
cd SalesForce
pip install -r requirements.txt
npm install
```

2. **Configure variáveis de ambiente**:
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

3. **Inicie os serviços**:
```powershell
.\INICIAR_SERVICOS.ps1
```

4. **Configure o webhook**:
```powershell
.\reconfigurar_webhook.ps1
```

### 3. Variáveis de Ambiente

```env
# GitHub AI
GITHUB_TOKEN=seu_token_github

# Evolution API
EVOLUTION_API_KEY=evolution_api_key_2025

# Salesforce (futuro)
SF_USERNAME=seu_usuario@salesforce.com
SF_PASSWORD=sua_senha
SF_SECURITY_TOKEN=seu_token
```

## 📁 Estrutura do Projeto

```
├── src/                          # Código fonte principal
│   ├── chatbot/                  # Módulos de chatbot
│   ├── integration/              # Integrações externas
│   ├── salesforce/               # Cliente Salesforce
│   └── transcription/            # Processamento de áudio
├── docs/                         # Documentação
├── mensagens_recebidas/          # Mensagens capturadas (auto-criado)
├── conversations/                # Conversas por número (auto-criado)
├── webhook_captura_mensagens.py  # 🎯 Webhook principal
├── INICIAR_SERVICOS.ps1          # 🚀 Script de inicialização
├── configurar_webhook.ps1        # ⚙️ Configuração webhook
└── reconfigurar_webhook.ps1      # 🔄 Reconfiguração webhook
```

## 🎮 Uso

### Iniciar Sistema
```powershell
.\INICIAR_SERVICOS.ps1
```

### Monitorar Logs
- Mensagens: `mensagens_recebidas/mensagens_YYYYMMDD.json`
- Conversas: `mensagens_recebidas/conversas_<numero>.json`
- Status: `http://localhost:8000/status`

### Endpoints Disponíveis
- `GET /status` - Status do webhook
- `POST /webhook` - Endpoint para Evolution API
- `GET /mensagens` - Listar mensagens capturadas
- `GET /conversas` - Listar conversas por número

## 🔧 Configuração Avançada

### Mudar Webhook Ativo
Edite `INICIAR_SERVICOS.ps1`:
```powershell
$WEBHOOK_SCRIPT = 'webhook_captura_mensagens.py'  # webhook desejado
```

### Configurar Número Monitorado
Edite `webhook_captura_mensagens.py`:
```python
NUMERO_MONITORADO = "556596977000"  # número para resposta automática
```

### Logs e Debug
- Logs do webhook: console da janela PowerShell
- Logs Evolution: `docker logs evolution_api`
- Status serviços: `docker ps`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📞 Suporte

- **Webhook não responde**: Verifique se o localtunnel está ativo e o webhook configurado
- **Evolution API**: Verifique `docker ps` e logs com `docker logs evolution_api`
- **IA não funciona**: Verifique `GITHUB_TOKEN` no `.env`

## 🎯 Roadmap

- [ ] Integração completa Salesforce (consultas SOQL)
- [ ] Interface web para monitoramento
- [ ] Suporte a múltiplos números monitorados
- [ ] Templates de resposta configuráveis
- [ ] Dashboard analytics

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**Status**: ✅ Webhook funcional | 🚧 Integração Salesforce em desenvolvimento
