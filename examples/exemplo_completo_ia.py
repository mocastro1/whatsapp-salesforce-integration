"""
Exemplo de uso completo: Transcrição + Processamento IA
"""

import os
import sys
import json

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from transcription.whisper_client import WhisperTranscriber
from processing.ai_processor import TranscriptionProcessor


def exemplo_completo_ia():
    """Demonstra o fluxo completo: áudio -> transcrição -> IA -> CRM."""
    
    print("=== EXEMPLO COMPLETO: ÁUDIO → IA → CRM ===\n")
    
    # Verificar configuração
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Configure OPENAI_API_KEY no arquivo .env primeiro!")
        return
    
    # Texto de exemplo (simulando uma transcrição real)
    texto_exemplo = """
    Oi, acabei de terminar a reunião com o João Silva da empresa TechCorp. 
    Ele está interessado no nosso pacote premium de consultoria. 
    Vamos marcar uma nova conversa para o dia 15 de novembro quando ele 
    voltar da viagem de negócios. O lead ID é TCP-2024-001. 
    Ele pareceu bem animado com a proposta, então acho que temos boas chances de fechar.
    """
    
    print("📝 TEXTO DE EXEMPLO (simulando transcrição):")
    print("-" * 60)
    print(texto_exemplo.strip())
    print("-" * 60)
    
    try:
        # Processar com IA
        print("\n🤖 PROCESSANDO COM IA...")
        processor = TranscriptionProcessor()
        
        informacoes = processor.extrair_informacoes_crm(texto_exemplo)
        
        print("\n" + "="*60)
        print("📊 INFORMAÇÕES EXTRAÍDAS PELA IA:")
        print("="*60)
        print(processor.gerar_resumo(informacoes))
        
        print("\n" + "="*60)
        print("🔍 DADOS ESTRUTURADOS (JSON):")
        print("="*60)
        print(json.dumps(informacoes, ensure_ascii=False, indent=2))
        
        # Simular próximos passos
        print("\n" + "="*60)
        print("🚀 PRÓXIMOS PASSOS SUGERIDOS:")
        print("="*60)
        
        proxima_acao = informacoes.get('proxima_acao', {})
        if proxima_acao.get('acao'):
            print(f"✅ Criar task: {proxima_acao['acao']}")
            if proxima_acao.get('data'):
                print(f"📅 Para a data: {proxima_acao['data']}")
        
        contato = informacoes.get('contato', {})
        if contato.get('nome'):
            print(f"👤 Atualizar contato: {contato['nome']}")
            if contato.get('empresa'):
                print(f"🏢 Na empresa: {contato['empresa']}")
        
        lead = informacoes.get('lead', {})
        if lead.get('identificador'):
            print(f"🎯 Atualizar lead: {lead['identificador']}")
            
        print("\n💡 Próximo passo: Integrar com Salesforce API!")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


def exemplo_com_audio_real():
    """Exemplo usando arquivo de áudio real."""
    
    print("\n" + "="*60)
    print("🎵 TESTE COM ÁUDIO REAL")
    print("="*60)
    
    audio_teste = "teste_audio.wav"  # ou .mp3, .m4a, etc.
    
    if not os.path.exists(audio_teste):
        print(f"Para testar com áudio real, adicione um arquivo: {audio_teste}")
        print("Formatos suportados: WAV, MP3, M4A, FLAC, etc.")
        print("\nGrave algo como:")
        print("'Acabei de falar com Maria Santos da ABC Corp sobre o projeto XYZ, vamos nos reunir na próxima segunda-feira'")
        return
    
    try:
        # Transcrever áudio
        transcriber = WhisperTranscriber()
        print(f"🎙️ Transcrevendo: {audio_teste}")
        
        result = transcriber.transcribe_file(audio_teste)
        if not result:
            print("❌ Erro na transcrição")
            return
        
        texto = result['text']
        print(f"\n📝 Transcrição: {texto}")
        
        # Processar com IA
        processor = TranscriptionProcessor()
        info = processor.extrair_informacoes_crm(texto)
        
        print(f"\n🤖 Análise IA:")
        print(processor.gerar_resumo(info))
        
        # Salvar resultado
        with open('resultado_completo.json', 'w', encoding='utf-8') as f:
            json.dump({
                'transcricao': result,
                'analise_ia': info
            }, f, ensure_ascii=False, indent=2)
        
        print("\n💾 Resultado salvo em: resultado_completo.json")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    # Carregar variáveis de ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    # Executar exemplos
    exemplo_completo_ia()
    exemplo_com_audio_real()