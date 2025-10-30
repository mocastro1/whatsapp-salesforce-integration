"""
📥 Webhook de Captura de Mensagens - Evolution API
Salva TODAS as mensagens recebidas de QUALQUER número
Responde mensagens do numero monitorado usando IA do GitHub
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# ========== CONFIGURAÇÕES ==========
EVOLUTION_API_URL = "http://localhost:3001"
EVOLUTION_API_KEY = "evolution_api_key_2025"
INSTANCE_NAME = "salesforce-bot"

# GitHub API Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API_URL = "https://models.inference.ai.azure.com/chat/completions"

# Número para monitorar e responder
NUMERO_MONITORADO = "556596977000"

# Pasta para salvar mensagens
MENSAGENS_DIR = Path('mensagens_recebidas')
MENSAGENS_DIR.mkdir(exist_ok=True)

# ========== FUNÇÕES AUXILIARES ==========

def extrair_numero_telefone(remote_jid: str) -> str:
    """Extrai o número do remoteJid"""
    return remote_jid.split('@')[0] if '@' in remote_jid else remote_jid


def perguntar_ia_github(mensagem: str) -> str:
    """Envia mensagem para IA do GitHub e retorna resposta"""
    try:
        if not GITHUB_TOKEN:
            print("   ⚠️ GITHUB_TOKEN não configurado!")
            return "Desculpe, não consigo processar sua mensagem no momento."
        
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um assistente útil e amigável que responde mensagens de WhatsApp de forma clara e objetiva."
                },
                {
                    "role": "user",
                    "content": mensagem
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        print(f"   🤖 Enviando para IA do GitHub...")
        response = requests.post(
            GITHUB_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            resposta_ia = response.json()['choices'][0]['message']['content']
            print(f"   ✅ Resposta da IA recebida: {resposta_ia[:50]}...")
            return resposta_ia
        else:
            print(f"   ❌ Erro na IA: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return "Desculpe, tive um problema ao processar sua mensagem."
            
    except Exception as e:
        print(f"   ❌ Erro ao chamar IA: {e}")
        import traceback
        traceback.print_exc()
        return "Desculpe, ocorreu um erro ao processar sua mensagem."


def enviar_resposta(numero: str, mensagem: str) -> bool:
    """Envia resposta via Evolution API"""
    try:
        headers = {"apikey": EVOLUTION_API_KEY}
        body = {
            "number": numero,
            "text": mensagem
        }
        
        response = requests.post(
            f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}",
            headers=headers,
            json=body,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"   ✅ Resposta enviada para {numero}")
            return True
        else:
            print(f"   ❌ Erro ao enviar: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao enviar resposta: {e}")
        return False


def salvar_mensagem(numero: str, mensagem: str, message_data: dict):
    """Salva mensagem recebida em arquivo JSON"""
    try:
        timestamp = datetime.now()
        
        # Verificar se é mensagem própria
        from_me = message_data.get('key', {}).get('fromMe', False)
        tipo = "ENVIADA" if from_me else "RECEBIDA"
        
        # Nome do arquivo por data
        data_str = timestamp.strftime('%Y%m%d')
        arquivo = MENSAGENS_DIR / f"mensagens_{data_str}.json"
        
        # Criar entrada
        entrada = {
            "timestamp": timestamp.isoformat(),
            "hora": timestamp.strftime('%H:%M:%S'),
            "numero": numero,
            "tipo": tipo,
            "from_me": from_me,
            "mensagem": mensagem,
            "message_id": message_data.get('key', {}).get('id', 'N/A'),
            "dados_completos": message_data
        }
        
        # Carregar mensagens existentes
        mensagens = []
        if arquivo.exists():
            with open(arquivo, 'r', encoding='utf-8') as f:
                mensagens = json.load(f)
        
        # Adicionar nova mensagem
        mensagens.append(entrada)
        
        # Salvar
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(mensagens, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Mensagem salva: {arquivo.name}")
        
        # Também salvar por número
        arquivo_numero = MENSAGENS_DIR / f"conversas_{numero}.json"
        conversas = []
        if arquivo_numero.exists():
            with open(arquivo_numero, 'r', encoding='utf-8') as f:
                conversas = json.load(f)
        
        conversas.append(entrada)
        
        with open(arquivo_numero, 'w', encoding='utf-8') as f:
            json.dump(conversas, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Conversa atualizada: {arquivo_numero.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========== ENDPOINTS ==========

@app.post('/webhook')
async def webhook_evolution(request: Request):
    """
    Webhook que captura TODAS as mensagens
    """
    try:
        data = await request.json()
        event = data.get('event', '')
        
        print(f"\n{'='*70}")
        print(f"🔔 Evento recebido: {event}")
        print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        
        # Processar apenas mensagens recebidas
        if event == 'messages.upsert':
            message_data = data.get('data', {})
            key = message_data.get('key', {})
            
            # ✅ CAPTURAR TODAS - incluindo mensagens próprias
            from_me = key.get('fromMe', False)
            tipo_msg = "ENVIADA" if from_me else "RECEBIDA"
            
            # Extrair informações
            remote_jid = key.get('remoteJid', '')
            numero = extrair_numero_telefone(remote_jid)
            
            print(f"   📱 De: {numero}")
            print(f"   📍 Tipo: {tipo_msg}")
            
            # Extrair texto da mensagem
            message_content = message_data.get('message', {})
            texto = (
                message_content.get('conversation') or 
                message_content.get('extendedTextMessage', {}).get('text') or
                '[Mensagem sem texto ou mídia]'
            )
            
            print(f"   💬 Mensagem: {texto[:100]}")
            
            # Verificar se é do número monitorado
            if numero == NUMERO_MONITORADO:
                print(f"   🎯 NÚMERO MONITORADO DETECTADO!")
            
            # Salvar mensagem
            sucesso = salvar_mensagem(numero, texto, message_data)
            
            if sucesso:
                print(f"   ✅ Mensagem salva com sucesso")
                
                # Se for do número monitorado E não for mensagem própria, enviar resposta
                if numero == NUMERO_MONITORADO and not from_me:
                    print(f"   📤 Processando com IA...")
                    resposta_ia = perguntar_ia_github(texto)
                    enviar_resposta(numero, resposta_ia)
                
                return JSONResponse({
                    'status': 'success',
                    'message': 'saved',
                    'numero': numero,
                    'resposta_enviada': (numero == NUMERO_MONITORADO and not from_me)
                })
            else:
                print(f"   ❌ Falha ao salvar mensagem")
                return JSONResponse({
                    'status': 'error',
                    'message': 'failed_to_save'
                }, status_code=500)
        
        # Ignorar outros eventos
        return JSONResponse({'status': 'ignored', 'reason': 'not_message_event'})
        
    except Exception as e:
        print(f"\n❌ ERRO no webhook: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse({'status': 'error', 'message': str(e)}, status_code=500)


@app.get('/status')
async def status():
    """Status do webhook"""
    # Contar mensagens
    total = 0
    for arquivo in MENSAGENS_DIR.glob('mensagens_*.json'):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                msgs = json.load(f)
                total += len(msgs)
        except:
            pass
    
    return {
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'mensagens_capturadas': total,
        'pasta': str(MENSAGENS_DIR),
        'instance': INSTANCE_NAME
    }


@app.get('/mensagens')
async def listar_mensagens():
    """Lista todas as mensagens capturadas"""
    try:
        todas_mensagens = []
        
        for arquivo in sorted(MENSAGENS_DIR.glob('mensagens_*.json')):
            with open(arquivo, 'r', encoding='utf-8') as f:
                msgs = json.load(f)
                todas_mensagens.extend(msgs)
        
        return {
            'total': len(todas_mensagens),
            'mensagens': todas_mensagens[-50:]  # Últimas 50
        }
    except Exception as e:
        return {'error': str(e)}


@app.get('/conversas')
async def listar_conversas():
    """Lista todas as conversas por número"""
    try:
        conversas = {}
        
        for arquivo in MENSAGENS_DIR.glob('conversas_*.json'):
            numero = arquivo.stem.replace('conversas_', '')
            with open(arquivo, 'r', encoding='utf-8') as f:
                msgs = json.load(f)
                conversas[numero] = {
                    'total_mensagens': len(msgs),
                    'ultima_mensagem': msgs[-1] if msgs else None
                }
        
        return conversas
    except Exception as e:
        return {'error': str(e)}


@app.get('/')
async def root():
    """Root endpoint"""
    return {
        'name': 'Webhook de Captura de Mensagens',
        'descricao': 'Salva todas as mensagens recebidas de qualquer número',
        'endpoints': {
            'webhook': '/webhook',
            'status': '/status',
            'mensagens': '/mensagens',
            'conversas': '/conversas'
        }
    }


if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*70)
    print("  📥 WEBHOOK DE CAPTURA DE MENSAGENS")
    print("="*70)
    print(f"\n  📁 Pasta de mensagens: {MENSAGENS_DIR}/")
    print(f"  🔗 Instance: {INSTANCE_NAME}")
    print(f"  ℹ️  Salvando TODAS as mensagens de TODOS os números")
    print(f"  ℹ️  SEM respostas automáticas")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_level='info'
    )
