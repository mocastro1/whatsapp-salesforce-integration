"""
Cliente para transcrição usando OpenAI Whisper API
"""

import os
import openai
from typing import Dict, Optional
import mimetypes


class WhisperTranscriber:
    """Cliente para transcrição de áudio usando OpenAI Whisper."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente Whisper.
        
        Args:
            api_key: Chave da API OpenAI. Se None, usa variável de ambiente.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key da OpenAI é obrigatória")
        
        # Configurar cliente OpenAI
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def transcribe_file(self, audio_path: str, language: str = 'pt') -> Optional[Dict]:
        """
        Transcreve um arquivo de áudio.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma (ex: 'pt', 'en', 'es')
        
        Returns:
            Dict com resultado da transcrição ou None em caso de erro
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
            
            # Verificar tipo de arquivo
            mime_type, _ = mimetypes.guess_type(audio_path)
            if not mime_type or not mime_type.startswith('audio/'):
                print(f"Aviso: Tipo de arquivo pode não ser suportado: {mime_type}")
            
            # Verificar tamanho do arquivo (limite de 25MB)
            file_size = os.path.getsize(audio_path)
            if file_size > 25 * 1024 * 1024:  # 25MB
                raise ValueError(f"Arquivo muito grande: {file_size / (1024*1024):.1f}MB. Máximo: 25MB")
            
            print(f"Enviando arquivo para transcrição: {os.path.basename(audio_path)}")
            print(f"Tamanho: {file_size / (1024*1024):.1f}MB")
            
            # Fazer transcrição
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="json"
                )
            
            return {
                'text': transcript.text,
                'language': language,
                'file_path': audio_path,
                'file_size_mb': round(file_size / (1024*1024), 2)
            }
            
        except Exception as e:
            print(f"Erro na transcrição: {str(e)}")
            return None
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = 'pt') -> Optional[Dict]:
        """
        Transcreve áudio com timestamps detalhados.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma
        
        Returns:
            Dict com transcrição e timestamps ou None em caso de erro
        """
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            return {
                'text': transcript.text,
                'language': transcript.language,
                'duration': transcript.duration,
                'words': transcript.words if hasattr(transcript, 'words') else None,
                'segments': transcript.segments if hasattr(transcript, 'segments') else None
            }
            
        except Exception as e:
            print(f"Erro na transcrição com timestamps: {str(e)}")
            return None