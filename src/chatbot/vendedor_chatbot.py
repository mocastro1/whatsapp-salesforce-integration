"""
Chatbot Vendedor - IA conversacional com histórico
Usa GitHub Copilot para responder mensagens de vendedores
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from transcription.copilot_client import GitHubCopilotClient
except ImportError:
    GitHubCopilotClient = None

try:
    import openai
except ImportError:
    openai = None


class VendedorChatbot:
    """Chatbot para vendedores com histórico de conversa."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Inicializar chatbot."""
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.conversations_dir = Path('conversations')
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Inicializar client de IA
        self.ai_client = None
        try:
            if GitHubCopilotClient:
                self.ai_client = GitHubCopilotClient(self.github_token)
        except Exception as e:
            print(f"⚠️ Aviso ao inicializar GitHub Copilot: {e}")
    
    def get_conversation_file(self, user_phone: str) -> Path:
        """Obter caminho do arquivo de histórico do usuário."""
        # Limpar telefone para nome de arquivo
        phone_clean = user_phone.replace('+', '').replace(' ', '').replace('-', '')
        return self.conversations_dir / f"conv_{phone_clean}.json"
    
    def load_conversation_history(self, user_phone: str) -> List[Dict]:
        """Carregar histórico de conversa do usuário."""
        conv_file = self.get_conversation_file(user_phone)
        
        if conv_file.exists():
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('messages', [])
            except Exception as e:
                print(f"⚠️ Erro ao carregar histórico: {e}")
                return []
        
        return []
    
    def save_conversation_history(self, user_phone: str, messages: List[Dict]):
        """Salvar histórico de conversa do usuário."""
        conv_file = self.get_conversation_file(user_phone)
        
        try:
            data = {
                'user_phone': user_phone,
                'messages': messages,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar histórico: {e}")
    
    def format_conversation_for_ai(self, messages: List[Dict]) -> str:
        """Formatar histórico de conversa para enviar à IA."""
        formatted = "=== HISTÓRICO DE CONVERSA ===\n\n"
        
        for msg in messages[-10:]:  # Últimas 10 mensagens
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                formatted += f"👤 Vendedor ({timestamp}): {content}\n"
            else:
                formatted += f"🤖 IA ({timestamp}): {content}\n"
        
        formatted += "\n=== FIM DO HISTÓRICO ===\n"
        return formatted
    
    def generate_system_prompt(self) -> str:
        """Gerar system prompt para o vendedor."""
        return """Você é um assistente de IA para VENDEDORES. Seu objetivo é ajudar vendedores a:
1. Qualificar leads
2. Preparar argumentos de venda
3. Responder perguntas de clientes
4. Agendar reuniões
5. Enviar propostas

REGRAS:
- Seja breve e direto
- Use linguagem profissional mas amigável
- Forneça sugestões práticas
- Pergunte sempre para confirmar próximos passos
- Se mencionar um cliente, tente extrair: nome, telefone, empresa, interesse
- Resuma decisões importantes

Responda em português brasileiro, de forma concisa (máximo 500 caracteres)."""
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Gerar resposta automática baseada em palavras-chave."""
        msg_lower = user_message.lower()
        
        # Dicionário de respostas por contexto
        if any(word in msg_lower for word in ['preço', 'custo', 'valor', 'caro', 'custa']):
            return """Bom ponto! Aqui estão estratégias para tratar objeção de preço:

1️⃣ **Foque no ROI**: "Este investimento traz X% de retorno em Y meses"
2️⃣ **Compare valor**: "Versus concorrente Z, temos mais recursos"
3️⃣ **Parcelamento**: "Podemos oferecer 3-12x sem juros"
4️⃣ **Prova social**: "Clientes similares economizaram 40%"

Qual desses argumentos combina com seu cliente?"""
        
        elif any(word in msg_lower for word in ['parcelado', 'parcelament', 'pagar', 'pagamento', 'condição']):
            return """Ótima pergunta sobre condições de pagamento!

💳 **Opções recomendadas**:
- À vista: -10% de desconto
- 3x: sem juros
- 6x até 12x: taxa de 2% a.m
- Customizado: para grandes volumes

📞 Dica: Ofereça sempre 2-3 opções. Deixe o cliente escolher = maior chance de fechar.

Qual é o investimento total?"""
        
        elif any(word in msg_lower for word in ['agenda', 'reunião', 'marcar', 'agendar', 'horário']):
            return """Perfeito! Hora de agendar:

📅 **Passo a passo**:
1. Confirme nome + telefone do cliente
2. Sugira 2-3 horários (não pergunte "quando você quer?")
3. Envie link do calendario ou WhatsApp direto
4. Confirme 1h antes da reunião

🎯 Dica: Reuniões com dia/hora específica têm 70% mais taxa de presença.

Qual é o próximo passo com seu cliente?"""
        
        elif any(word in msg_lower for word in ['cliente', 'prospect', 'lead', 'contato', 'pessoa']):
            return """Ótimo! Vamos qualificar esse contato:

❓ **Perguntas importantes**:
1. Nome completo + empresa?
2. Orçamento aproximado?
3. Quando precisa/quando quer decidir?
4. Quem mais precisa estar na conversa?
5. Qual problema ele quer resolver?

📊 Quanto mais info você tem = melhor sua proposta.

Me conta mais sobre esse cliente!"""
        
        elif any(word in msg_lower for word in ['proposta', 'cotação', 'orçamento', 'quote']):
            return """Vamos estruturar a proposta:

📋 **Elementos essenciais**:
1. Resumo executivo (o que ele vai ganhar)
2. Solução customizada (para o DELE)
3. Preço + condições (simples e claro)
4. Timeline de implementação
5. ROI + próximos passos

⚡ Dica: Proposta de 1 página é 3x melhor que 10 páginas.

Qual é o produto/serviço que você vende?"""
        
        elif any(word in msg_lower for word in ['objeção', 'problema', 'dificuldade', 'não quer', 'recusa']):
            return """Todo "não" é oportunidade! 🎯

**Framework para vencer objeções**:

1️⃣ **ESCUTE**: Deixe falar até o final
2️⃣ **EMPATIZE**: "Entendo sua preocupação"
3️⃣ **EXPLORE**: "Me conta mais sobre..."
4️⃣ **PIVOTE**: Mude de ângulo/benefício
5️⃣ **PROPONHA**: "E se fizéssemos assim..."

Qual é a objeção exatamente?"""
        
        else:
            # Resposta genérica
            return """Entendi! 📝

Para ajudar melhor, preciso saber:
- Está em qual etapa da venda? (prospecting, apresentação, fechamento)
- Qual é o principal desafio agora?
- Qual produto/serviço você vende?

Digite seus detalhes e vou te dar uma estratégia prática! 💡"""
    
    def chat(self, user_phone: str, user_message: str) -> Optional[str]:
        """Processar mensagem do usuário e gerar resposta."""
        
        # Carregar histórico
        messages = self.load_conversation_history(user_phone)
        
        # Adicionar nova mensagem do usuário
        messages.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Usar fallback response (sem IA para evitar JSON estruturado)
        # O ai_client retorna JSON estruturado para CRM, não é apropriado para chat
        response_text = self._generate_fallback_response(user_message)
        
        # Se ainda estiver muito longo, truncar
        if len(response_text) > 500:
            response_text = response_text[:497] + "..."
        
        # Adicionar resposta ao histórico
        messages.append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Salvar histórico atualizado
        self.save_conversation_history(user_phone, messages)
        
        return response_text
    
    def get_conversation_summary(self, user_phone: str) -> Optional[str]:
        """Obter resumo da conversa com um usuário."""
        messages = self.load_conversation_history(user_phone)
        
        if not messages:
            return "Nenhuma conversa registrada"
        
        summary = f"""📊 RESUMO DA CONVERSA COM {user_phone}
Mensagens: {len(messages)}
Última atualização: {datetime.now().isoformat()}

Últimas 3 mensagens:
"""
        
        for msg in messages[-3:]:
            role = "Vendedor" if msg.get('role') == 'user' else "IA"
            content = msg.get('content', '')[:100]
            summary += f"\n{role}: {content}..."
        
        return summary
    
    def clear_conversation(self, user_phone: str) -> bool:
        """Limpar histórico de conversa (começar do zero)."""
        conv_file = self.get_conversation_file(user_phone)
        
        try:
            if conv_file.exists():
                conv_file.unlink()
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar conversa: {e}")
            return False


class ChatbotManager:
    """Gerenciador central de chatbots."""
    
    def __init__(self):
        self.chatbot = VendedorChatbot()
    
    def processar_mensagem_whatsapp(self, phone_number: str, message_text: str) -> str:
        """Processar mensagem WhatsApp e retornar resposta."""
        
        # Verificar comandos especiais
        if message_text.lower() == '/limpar':
            self.chatbot.clear_conversation(phone_number)
            return "✅ Histórico limpo. Nova conversa iniciada!"
        
        if message_text.lower() == '/resumo':
            return self.chatbot.get_conversation_summary(phone_number)
        
        # Processar como mensagem normal
        response = self.chatbot.chat(phone_number, message_text)
        return response or "Desculpe, não consegui processar sua mensagem"


# Teste
if __name__ == "__main__":
    print("=== TESTE VENDEDOR CHATBOT ===\n")
    
    manager = ChatbotManager()
    
    # Simular conversa
    test_phone = "+556596063938"
    
    test_messages = [
        "Oi, tudo bem? Eu tenho um cliente interessado em comprar mas está em dúvida no preço",
        "Qual é o melhor argumento pra vencer essa objeção?",
        "Ok, e se o cliente quiser pagamento parcelado?",
    ]
    
    for msg in test_messages:
        print(f"👤 Vendedor: {msg}")
        response = manager.processar_mensagem_whatsapp(test_phone, msg)
        print(f"🤖 IA: {response}\n")
        print("-" * 60 + "\n")
    
    print("\n=== RESUMO DA CONVERSA ===")
    summary = manager.processar_mensagem_whatsapp(test_phone, "/resumo")
    print(summary)
