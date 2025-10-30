"""
Exemplo básico de uso do sistema de transcrição
"""

import os
import sys

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from transcription.whisper_client import WhisperTranscriber


def exemplo_transcricao():
    """Exemplo de como usar o transcritor."""
    
    print("=== Exemplo de Transcrição de Áudio ===\n")
    
    # Verificar se existe arquivo de exemplo
    audio_exemplo = "exemplo_audio.wav"
    if not os.path.exists(audio_exemplo):
        print("Para testar, adicione um arquivo de áudio chamado 'exemplo_audio.wav'")
        print("Formatos suportados: WAV, MP3, M4A, FLAC, etc.")
        return
    
    try:
        # Inicializar transcritor
        transcriber = WhisperTranscriber()
        
        print(f"Transcrevendo: {audio_exemplo}")
        
        # Fazer transcrição simples
        resultado = transcriber.transcribe_file(audio_exemplo)
        
        if resultado:
            print("\n" + "="*60)
            print("RESULTADO DA TRANSCRIÇÃO:")
            print("="*60)
            print(f"Texto: {resultado['text']}")
            print(f"Idioma: {resultado['language']}")
            print(f"Arquivo: {resultado['file_path']}")
            print(f"Tamanho: {resultado['file_size_mb']} MB")
            print("="*60)
            
            # Salvar resultado
            with open('transcricao_resultado.txt', 'w', encoding='utf-8') as f:
                f.write(resultado['text'])
            print("Resultado salvo em: transcricao_resultado.txt")
            
        else:
            print("Erro: Não foi possível transcrever o áudio")
    
    except Exception as e:
        print(f"Erro: {str(e)}")


if __name__ == "__main__":
    exemplo_transcricao()