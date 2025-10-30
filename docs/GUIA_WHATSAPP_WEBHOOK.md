# 🔗 Guia: Configurando WhatsApp Sandbox + Webhook

## Status Atual ✅
- ✅ FastAPI Webhook Server rodando na porta 8000
- ⏳ ngrok tunnel sendo criado (aguarde mensagem com URL pública)

---

## 📋 Próximos Passos (assim que o ngrok se conectar)

### 1. Aguarde a URL pública do ngrok
Na janela do ngrok, você verá algo assim:
```
📍 URL PÚBLICA DO WEBHOOK:
   https://xxxx-xx-xxx-xxx.ngrok.io/webhook
```

**Copie essa URL** — você precisará dela nos próximos passos.

---

### 2. Configure o Webhook no Twilio Console
1. Acesse: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Procure pela seção **"When a message comes in"**
3. Cole a URL do ngrok (exemplo: `https://xxxx-xx-xxx-xxx.ngrok.io/webhook`)
4. Clique em **Save**

---

### 3. Confirme seu Número de Celular no Sandbox
1. Mesma página, procure por **"Join our Sandbox"**
2. Escaneie o QR Code com WhatsApp ou
3. Envie uma mensagem de texto (conforme instruído) para o número do Sandbox

**Após confirmar**, você poderá enviar e receber mensagens de/para o Sandbox.

---

### 4. Teste o Fluxo Completo
1. Abra WhatsApp no seu celular
2. Procure pelo número do Twilio Sandbox (você verá na página)
3. **Envie uma Nota de Voz** (voice note / áudio)
   - Segure o botão de microfone
   - Grave uma mensagem curta (ex: "Cliente João Silva, +55 11 9 9999-9999")
   - Solte para enviar

---

### 5. Monitore os Outputs
Quando o webhook receber a nota de voz:
1. Ele baixará o áudio
2. Processará com Whisper (transcrição local)
3. Executará o Orchestrator (matching + ranking)
4. Salvará resultados em `outputs/`

**Verifique a pasta `outputs/`** para ver:
- `*_transcricao_real.txt` — transcrição do áudio
- `*_analise_real.json` — metadados (source_phone, etc)
- `*_orchestrator_result.json` — resultado do matching e decisão

---

## 📱 Exemplo de Áudio Ideal
Para maximize a precisão da extração:
> "Oi, eu sou o João Silva, meu telefone é 11 9 9999-9999, estou interessado em conhecer mais sobre os produtos de consultoria"

**O sistema extrairá automaticamente:**
- Nome: João Silva
- Telefone: +55 11 99999999 (normalizado)
- Interesse: consultoria

---

## 🔍 Troubleshooting

### Ngrok não conecta?
- Certifique-se que o FastAPI Server está rodando (verifique a outra janela)
- Se houver erro de firewall, desabilite temporariamente

### Webhook não recebe eventos?
- Verifique se a URL foi salva no Twilio Console
- Confirme seu número novamente no Sandbox

### Áudio não é processado?
- Verifique em `outputs/` se existem arquivos gerados
- Cheque os logs do servidor FastAPI para erros

---

## 🛑 Parando os Serviços
- Pressione **Ctrl+C** na janela do FastAPI Webhook para parar
- Pressione **Ctrl+C** na janela do ngrok tunnel para parar
- Ambos podem ser parados independentemente

---

**Pronto! Você tem um webhook WhatsApp funcional e pronto para processar áudios! 🎉**
