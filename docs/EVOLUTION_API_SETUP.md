# 🚀 EVOLUTION API - SETUP COMPLETO

## Status: ✅ Docker iniciado

**Aguardando containers iniciarem...**

Container Evolution normalmente leva 1-3 minutos para estar pronto.

---

## 📋 Próximas Etapas

### Passo 1: Acessar o painel (Quando Evolution estiver pronto)
```
Abra no navegador: http://localhost:3000
```

### Passo 2: Criar primeira instância
1. Clique em "Create New Instance"
2. Nomie: `salesforce-bot`
3. Clique em "Create"

### Passo 3: Escanear QR Code
1. Abra WhatsApp no seu telefone
2. Scannear QR code gerado
3. Confirmar conexão

### Passo 4: Configurar Webhook (Conectar com seu código Python)
Voltar em http://localhost:3000 e procurar por "Webhook Settings"

```
URL: http://localhost:8000/evolution-webhook
Method: POST
```

---

## 🔍 Como Verificar Status

```powershell
docker ps
# Deve mostrar containers:
# - evolution-api
# - evolution-postgres
# - evolution-redis
```

---

## ⏳ Se demorar muito

Se Evolution não aparecer em 5 minutos:

```powershell
docker logs evolution-api
# Ver mensagens de erro
```

