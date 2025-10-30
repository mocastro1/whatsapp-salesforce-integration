# 📊 Fluxograma do Projeto Audio → AI → Salesforce

## 🎯 Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE PROCESSAMENTO DE ÁUDIO                    │
│                      (Audio → Transcrição → IA → Salesforce)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ ENTRADA: WhatsApp Sandbox

```
┌──────────────────────────────────────┐
│   📱 Usuário envia Nota de Voz       │
│   (WhatsApp Sandbox da Twilio)       │
└────────────────┬─────────────────────┘
                 │
                 │ POST /webhook
                 │ (com arquivo de áudio)
                 ▼
```

---

## 2️⃣ RECEPÇÃO: Webhook FastAPI

```
┌────────────────────────────────────────────────────────┐
│         🔗 WEBHOOK FASTAPI (porta 8000)               │
│                                                        │
│  URL: https://flat-pugs-judge.loca.lt/webhook         │
│  (gerada por localtunnel)                             │
│                                                        │
│  Função: whatsapp_webhook()                           │
│  - Recebe POST do Twilio                              │
│  - Extrai: From, MessageSid, MediaUrl0                │
│  - Baixa arquivo de áudio                             │
│  - Salva em: audios_teste/                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├─────────────────────────────────┐
                 │                                 │
                 ▼                                 ▼
         ✅ Retorna 200 OK     Processamento em background
         (resposta imediata)    (assincronamente)
                                │
                                ▼
```

---

## 3️⃣ PROCESSAMENTO: Transcrição com Whisper

```
┌─────────────────────────────────────────────────────────┐
│    🤖 WHISPER LOCAL (Transcrição Offline)              │
│                                                         │
│  Classe: LocalWhisperTranscriber                        │
│  Modelo: base (15% de erro em português)               │
│                                                         │
│  Passos:                                                │
│  1. Carrega modelo Whisper (primeira vez: ~1GB)        │
│  2. Converte .ogg → .wav (usando ffmpeg)               │
│  3. Transcreve em português (pt)                       │
│  4. Retorna texto + metadados                          │
│                                                         │
│  Saída: Dict com:                                       │
│  - text: "Oi, meu nome é João Silva..."               │
│  - language: "portuguese"                              │
│  - file_path: "audios_teste/WhatsApp Ptt ..."         │
│  - model_used: "base"                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
     📝 Salva em: outputs/<id>_transcricao_real.txt
                 │
                 ▼
```

---

## 4️⃣ EXTRAÇÃO: Análise com IA (GitHub Copilot Simulated)

```
┌──────────────────────────────────────────────────────────┐
│    🧠 PROCESSADOR IA (Extração de Dados CRM)            │
│                                                          │
│  Classe: GitHubCopilotProcessor                          │
│  Simulado: usa patterns locais + prompts                │
│                                                          │
│  Extrai do texto:                                        │
│  ├─ Nome: João Silva                                    │
│  ├─ Telefone: +55 11 9 9999-9999                       │
│  ├─ Email: joao@email.com (se mencionado)              │
│  ├─ Empresa: (se mencionado)                           │
│  └─ Interesse/Assunto: consultoria                     │
│                                                          │
│  Saída JSON:                                             │
│  {                                                       │
│    "nome": "João Silva",                                │
│    "telefone": "+5511999999999",                        │
│    "email": "",                                         │
│    "empresa": "",                                       │
│    "interesse": "consultoria",                         │
│    "confianca": 0.85                                    │
│  }                                                       │
└────────────────┬──────────────────────────────────────────┘
                 │
                 ▼
    📊 Salva em: outputs/<id>_analise_real.json
                 │
                 ▼
```

---

## 5️⃣ NORMALIZAÇÃO: Phone Matcher

```
┌──────────────────────────────────────────────────────────┐
│    📞 NORMALIZADOR DE TELEFONE (E.164)                  │
│                                                          │
│  Classe: phone_matcher.py                                │
│  Biblioteca: phonenumbers                                │
│                                                          │
│  Passos:                                                 │
│  1. Recebe telefone do webhook: "+556596063938"         │
│  2. Normaliza para E.164: "+55 65 96063938"            │
│  3. Procura em Salesforce (simulado):                   │
│     - Busca por telefone em Contacts                    │
│     - Busca por telefone em Leads                       │
│  4. Retorna matches com score de confiança              │
│                                                          │
│  Resultado:                                              │
│  {                                                       │
│    "encontrados": 0,  (nenhum match)                    │
│    "candidates": []                                      │
│  }                                                       │
└────────────────┬──────────────────────────────────────────┘
                 │
                 ▼
```

---

## 6️⃣ ORQUESTRAÇÃO: Decisão e Ação

```
┌──────────────────────────────────────────────────────────────┐
│         🎯 ORCHESTRATOR (Decisão e Próximas Ações)          │
│                                                              │
│  Classe: Orchestrator                                        │
│  Função: process_by_basename()                              │
│                                                              │
│  FLUXO DE DECISÃO:                                           │
│                                                              │
│  ┌─────────────────────────────────────┐                   │
│  │ 1. Procura por match de telefone?   │                   │
│  └─────────────────────────────────────┘                   │
│           │                                                  │
│     SIM   │   NÃO                                           │
│           │   │                                             │
│           │   ▼                                             │
│           │ ┌──────────────────────────┐                   │
│           │ │ 2. Score de confiança?   │                   │
│           │ └──────────────────────────┘                   │
│           │        │                                        │
│           │   ALTO │ BAIXO                                 │
│           │        │                                        │
│           ▼        ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ Ação Recomendada:                       │               │
│  ├─────────────────────────────────────────┤               │
│  │ ✅ update_existing      (match perfeito)│               │
│  │ ⚠️  manual_review       (confidence baixa)              │
│  │ ✨ create_lead         (novo prospect)  │               │
│  │ 📝 create_note_and_task (para análise)  │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
│  Resultado salvo em:                                         │
│  outputs/<id>_orchestrator_result.json                      │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 ▼
```

---

## 7️⃣ SAÍDA: Arquivo de Resultado

```
┌────────────────────────────────────────────────────────────┐
│         📁 OUTPUTS (Pasta com Resultados)                 │
│                                                            │
│  Para cada áudio, são criados:                             │
│                                                            │
│  ├─ <id>_transcricao_real.txt                            │
│  │  └─ Texto puro da transcrição                         │
│  │                                                        │
│  ├─ <id>_analise_real.json                               │
│  │  └─ Dados extraídos (nome, telefone, email, etc)     │
│  │                                                        │
│  ├─ <id>_orchestrator_result.json                        │
│  │  └─ Ação recomendada + dados para Salesforce          │
│  │                                                        │
│  └─ <id>_salesforce_data.json                            │
│     └─ Payload pronto para inserir no Salesforce         │
│                                                            │
│  Exemplo de estrutura:                                     │
│  {                                                         │
│    "audio_original": "WhatsApp Ptt MMc8ba63678022686.ogg"│
│    "transcricao": "Oi, meu nome é João Silva...",        │
│    "source_phone": "+556596063938",                       │
│    "action": "create_lead",                               │
│    "dados_salesforce": {                                  │
│      "FirstName": "João",                                 │
│      "LastName": "Silva",                                 │
│      "Phone": "+55 65 96063938",                         │
│      "Company": "",                                       │
│      "Status": "novo"                                     │
│    },                                                      │
│    "timestamp": "2025-10-24T16:49:53"                     │
│  }                                                         │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
```

---

## 8️⃣ SALESFORCE INTEGRATION (Futuro - Atualmente Simulado)

```
┌─────────────────────────────────────────────────────────┐
│    🔗 SALESFORCE (Integração - Modo Simulated)         │
│                                                         │
│  Classe: SalesforceIntegrator                           │
│  Status: SCAFFOLD (estrutura pronta, sem credenciais)  │
│                                                         │
│  Métodos disponíveis:                                   │
│  ├─ create_lead()                                       │
│  ├─ create_contact()                                    │
│  ├─ create_opportunity()                                │
│  ├─ create_note()                                       │
│  ├─ create_task()                                       │
│  └─ process_salesforce_data()                           │
│                                                         │
│  Para ativar (TODO):                                    │
│  1. Preencher .env:                                     │
│     - SALESFORCE_USERNAME                              │
│     - SALESFORCE_PASSWORD                              │
│     - SALESFORCE_TOKEN                                 │
│     - SALESFORCE_DOMAIN                                │
│  2. Definir simulate_sf=False no Orchestrator           │
│  3. Executar ações reais                                │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Fluxo Completo End-to-End

```
WhatsApp              Webhook           Transcrição       IA
  📱                    🔗                  🤖              🧠
   │                    │                   │               │
   │─ Áudio ──────────▶ │─────────────────▶ │──────────────▶│
   │                    │  (background)     │               │
   │  Retorna 200 OK    │                   │ Extrai dados  │
   │◀─────────────────  │                   │               │
                        │                   │               │
                        └─ salva em outputs/
                                            │
                                            ▼
                                      Normalização
                                        📞
                                      Telefone
                                        │
                                        ▼
                                    Orquestração
                                      🎯
                                    Decisão
                                        │
                                        ├─ Create Lead
                                        ├─ Update Contact
                                        ├─ Create Note+Task
                                        └─ Manual Review
                                        │
                                        ▼
                                    Salesforce
                                      🔗
                                   (Futuro)
```

---

## 🛠️ Tecnologias Utilizadas

```
┌──────────────────────────────────────────────────────────┐
│              STACK TECNOLÓGICO                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Backend:                                                 │
│  • Python 3.x (Conda)                                   │
│  • FastAPI (Webhook)                                    │
│  • Uvicorn (ASGI Server)                                │
│                                                          │
│ Processamento de Áudio:                                  │
│  • OpenAI Whisper (Transcrição)                         │
│  • ffmpeg (Conversão de áudio)                          │
│  • pydub (Manipulação de áudio)                         │
│                                                          │
│ IA/LLM:                                                  │
│  • GitHub Copilot API (Futuro)                          │
│  • Prompts locais (Atual)                               │
│                                                          │
│ Data Processing:                                         │
│  • phonenumbers (Normalização de telefone)              │
│  • rapidfuzz (Fuzzy matching)                           │
│                                                          │
│ CRM:                                                     │
│  • simple-salesforce (SDK)                              │
│                                                          │
│ Networking:                                              │
│  • localtunnel (Exposição pública)                      │
│  • Twilio WhatsApp Sandbox                              │
│                                                          │
│ Armazenamento:                                           │
│  • JSON (Resultados)                                    │
│  • Pasta: outputs/ (Consolidada)                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Diretórios

```
📦 Salesforce/
├── 🔧 src/
│   ├── transcription/
│   │   ├── whisper_offline.py (Transcrição)
│   │   └── copilot_client.py (IA simulada)
│   ├── processing/
│   │   └── github_processor.py (Extração de dados)
│   ├── integration/
│   │   └── salesforce_integrator.py (CRM scaffold)
│   ├── matching/
│   │   └── phone_matcher.py (Normalização de telefone)
│   └── orchestrator/
│       └── orchestrator.py (Orquestração)
│
├── 📂 outputs/
│   ├── *_transcricao_real.txt
│   ├── *_analise_real.json
│   ├── *_orchestrator_result.json
│   └── *_salesforce_data.json
│
├── 📂 audios_teste/
│   └── WhatsApp Ptt *.ogg (Arquivos de teste)
│
├── 🔌 webhook.py (Servidor FastAPI)
├── ⚙️ requirements.txt (Dependências)
├── 🔐 .env (Configurações)
└── 📋 README.md (Documentação)
```

---

## ✅ Status do Projeto

```
┌─────────────────────────────────────────────────────────┐
│               COMPONENTES E STATUS                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ✅ Webhook FastAPI                                     │
│    └─ Recebe eventos do Twilio                        │
│    └─ Baixa arquivos de áudio                         │
│                                                         │
│ ✅ Whisper (Transcrição)                              │
│    └─ Transcreve português offline                    │
│    └─ Converte .ogg com ffmpeg                        │
│                                                         │
│ ✅ Extração de Dados (IA Simulada)                     │
│    └─ Extrai nome, telefone, email                    │
│    └─ Calcula confiança                               │
│                                                         │
│ ✅ Phone Matcher                                       │
│    └─ Normaliza números em E.164                      │
│    └─ Procura por matches (simulado)                  │
│                                                         │
│ ✅ Orchestrator                                        │
│    └─ Toma decisões de ação                           │
│    └─ Gera JSONs de resultado                         │
│                                                         │
│ ⏳ Salesforce Integration                              │
│    └─ SCAFFOLD pronto (sem credenciais ainda)         │
│    └─ Aguarda credenciais no .env                     │
│                                                         │
│ 🚀 Próximos Passos:                                    │
│    ├─ [ ] Conectar Salesforce real                    │
│    ├─ [ ] Implementar LLM ranking                      │
│    ├─ [ ] Queue worker (RQ/Celery)                    │
│    ├─ [ ] UI de manual review                         │
│    └─ [ ] Testes e validação                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Caso de Uso: Fluxo Completo

```
Cenário: Vendedor recebe nota de voz de prospect

1️⃣  Vendedor grava: "Oi, meu nome é João Silva, meu 
                     celular é 65 9606-3938, quero 
                     saber sobre consultoria"

2️⃣  Envia via WhatsApp Sandbox

3️⃣  Twilio recebe → faz POST para webhook

4️⃣  Webhook baixa áudio e processa em background

5️⃣  Whisper transcreve: 
    "Oi, meu nome é João Silva, meu celular é 
     65 9606-3938, quero saber sobre consultoria"

6️⃣  IA extrai:
    {
      "nome": "João Silva",
      "telefone": "+55 65 96063938",
      "interesse": "consultoria",
      "confianca": 0.92
    }

7️⃣  Phone Matcher busca por +55 65 96063938
    → Sem matches encontrados → Ação: CREATE_LEAD

8️⃣  Salesforce integrator:
    → Cria novo Lead em Salesforce
    → Cria Note com transcrição original
    → Cria Task para follow-up

9️⃣  Resultado salvo em outputs/
    {
      "action": "create_lead",
      "lead_id": "0015g00000XXXXX",
      "timestamp": "2025-10-24T16:50:15",
      "status": "sucesso"
    }
```

---

## 📞 Resumo Executivo

**O que temos:**
- ✅ Receptor de áudio via WhatsApp (Webhook)
- ✅ Transcrição offline com Whisper
- ✅ Extração de dados com IA (simulada)
- ✅ Normalização e matching de telefones
- ✅ Orquestração de decisões
- ✅ Exportação de resultados em JSON

**O que falta:**
- ⏳ Conexão real com Salesforce (credenciais)
- ⏳ LLM ranking (GitHub Copilot real)
- ⏳ Queue worker para scale
- ⏳ UI para manual review
- ⏳ Testes e validação

**Próximo milestone:**
→ Conectar Salesforce real e testar create_lead end-to-end

