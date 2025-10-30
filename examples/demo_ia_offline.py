"""
Demo offline - mostra como a IA processaria uma transcrição
(sem usar API real da OpenAI)
"""

def demo_processamento_ia():
    """Demonstra o que a IA faria com exemplos reais."""
    
    exemplos = [
        {
            "transcricao": "Acabei de falar com João Silva da TechCorp sobre o lead TCP-001. Ele está interessado no pacote premium. Vamos marcar uma reunião para o dia 15 de novembro quando ele voltar da viagem.",
            "resultado_ia": {
                "contato": {
                    "nome": "João Silva",
                    "empresa": "TechCorp",
                    "cargo": None
                },
                "lead": {
                    "identificador": "TCP-001",
                    "status": "interessado",
                    "produto_interesse": "pacote premium"
                },
                "proxima_acao": {
                    "acao": "marcar reunião",
                    "data": "2025-11-15",
                    "prazo": None
                },
                "observacoes": "Contato interessado no pacote premium, aguardando retorno de viagem",
                "sentimento": "positivo",
                "urgencia": "media"
            }
        },
        {
            "transcricao": "Maria Santos da ABC Corp ligou sobre a proposta. Ela disse que precisa de mais tempo para avaliar. Vou ligar novamente em uma semana.",
            "resultado_ia": {
                "contato": {
                    "nome": "Maria Santos",
                    "empresa": "ABC Corp",
                    "cargo": None
                },
                "lead": {
                    "identificador": None,
                    "status": "avaliando",
                    "produto_interesse": "proposta mencionada"
                },
                "proxima_acao": {
                    "acao": "ligar novamente",
                    "data": "2025-10-31",
                    "prazo": "em uma semana"
                },
                "observacoes": "Cliente precisa de mais tempo para avaliar a proposta",
                "sentimento": "neutro",
                "urgencia": "baixa"
            }
        },
        {
            "transcricao": "O cliente da empresa XYZ cancelou o projeto. Disse que não tem orçamento no momento. Muito chateado com isso.",
            "resultado_ia": {
                "contato": {
                    "nome": None,
                    "empresa": "XYZ",
                    "cargo": None
                },
                "lead": {
                    "identificador": None,
                    "status": "cancelado",
                    "produto_interesse": None
                },
                "proxima_acao": {
                    "acao": None,
                    "data": None,
                    "prazo": None
                },
                "observacoes": "Projeto cancelado por falta de orçamento",
                "sentimento": "negativo",
                "urgencia": "baixa"
            }
        }
    ]
    
    print("🤖 DEMO: COMO A IA PROCESSA TRANSCRIÇÕES")
    print("=" * 70)
    
    for i, exemplo in enumerate(exemplos, 1):
        print(f"\n📝 EXEMPLO {i}:")
        print("Transcrição:", exemplo["transcricao"])
        print("\n🧠 IA Extraiu:")
        
        resultado = exemplo["resultado_ia"]
        
        # Contato
        contato = resultado["contato"]
        if contato["nome"]:
            print(f"👤 Contato: {contato['nome']}")
            if contato["empresa"]:
                print(f"🏢 Empresa: {contato['empresa']}")
        
        # Lead
        lead = resultado["lead"]
        if lead["identificador"]:
            print(f"🎯 Lead ID: {lead['identificador']}")
        if lead["produto_interesse"]:
            print(f"💼 Interesse: {lead['produto_interesse']}")
        
        # Próxima ação
        proxima = resultado["proxima_acao"]
        if proxima["acao"]:
            print(f"📅 Próxima ação: {proxima['acao']}")
            if proxima["data"]:
                print(f"🗓️ Data: {proxima['data']}")
        
        # Sentimento e urgência
        sentimento_emoji = {"positivo": "😊", "neutro": "😐", "negativo": "😟"}
        urgencia_emoji = {"alta": "🔴", "media": "🟡", "baixa": "🟢"}
        
        print(f"{sentimento_emoji.get(resultado['sentimento'], '😐')} Sentimento: {resultado['sentimento']}")
        print(f"{urgencia_emoji.get(resultado['urgencia'], '🟢')} Urgência: {resultado['urgencia']}")
        
        if resultado["observacoes"]:
            print(f"📋 Observação: {resultado['observacoes']}")
        
        print("-" * 70)
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Configure OPENAI_API_KEY no .env")
    print("2. Teste com: python main.py --audio seu_audio.wav --processar-ia")
    print("3. A IA vai extrair essas informações automaticamente!")
    print("\n💡 Futuro: Integração direta com Salesforce CRM")


if __name__ == "__main__":
    demo_processamento_ia()