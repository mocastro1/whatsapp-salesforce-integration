"""
Cliente Whisper local (offline) para transcrição real de áudio
"""

import os
import whisper
from typing import Dict, Optional
import tempfile
import subprocess


class LocalWhisperTranscriber:
    """Transcritor usando Whisper local (offline)."""
    
    def __init__(self, model_name: str = "base"):
        """
        Inicializa o transcritor Whisper local.
        
        Args:
            model_name: Modelo Whisper a usar (tiny, base, small, medium, large)
                       - tiny: mais rápido, menor qualidade
                       - base: balanceado (recomendado)
                       - small: melhor qualidade, mais lento
        """
        self.model_name = model_name
        self.model = None
        
        print(f"🔄 Carregando modelo Whisper '{model_name}'...")
        print("⏳ Primeira vez pode demorar (baixa o modelo)...")
        
        try:
            self.model = whisper.load_model(model_name)
            print(f"✅ Modelo '{model_name}' carregado com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {str(e)}")
            raise
    
    def transcribe_file(self, audio_path: str, language: str = 'pt') -> Optional[Dict]:
        """
        Transcreve arquivo de áudio usando Whisper local.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            language: Código do idioma ('pt', 'en', etc.)
        
        Returns:
            Dict com resultado da transcrição
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
            
            file_size = os.path.getsize(audio_path)
            print(f"🎙️ Transcrevendo: {os.path.basename(audio_path)}")
            print(f"📊 Tamanho: {file_size / (1024*1024):.1f}MB")
            
            # Converter arquivo se necessário (Whisper aceita vários formatos)
            audio_to_process = audio_path
            
            # Se for .ogg, pode precisar converter para melhor compatibilidade
            if audio_path.lower().endswith('.ogg'):
                audio_to_process = self._convert_ogg_to_wav(audio_path)
            
            print("🤖 Processando com Whisper local...")
            
            # Transcrever com Whisper
            result = self.model.transcribe(
                audio_to_process,
                language=language if language != 'pt' else 'portuguese',
                verbose=False
            )
            
            # Limpar arquivo temporário se foi criado
            if audio_to_process != audio_path:
                try:
                    os.remove(audio_to_process)
                except:
                    pass
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', language),
                'file_path': audio_path,
                'file_size_mb': round(file_size / (1024*1024), 2),
                'model_used': self.model_name,
                'segments': result.get('segments', [])
            }
            
        except Exception as e:
            print(f"❌ Erro na transcrição: {str(e)}")
            return None
    
    def _convert_ogg_to_wav(self, ogg_path: str) -> str:
        """
        Converte arquivo .ogg para .wav usando ffmpeg ou pydub.
        
        Args:
            ogg_path: Caminho do arquivo .ogg
            
        Returns:
            Caminho do arquivo .wav temporário
        """
        try:
            # Tentar usar pydub primeiro
            from pydub import AudioSegment
            
            # Criar arquivo temporário
            temp_wav = tempfile.mktemp(suffix='.wav')
            
            # Converter
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(temp_wav, format="wav")
            
            print(f"📝 Convertido .ogg → .wav temporário")
            return temp_wav
            
        except ImportError:
            print("⚠️ pydub não disponível, tentando usar arquivo original...")
            return ogg_path
        except Exception as e:
            print(f"⚠️ Erro na conversão: {str(e)}, usando arquivo original...")
            return ogg_path
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = 'pt') -> Optional[Dict]:
        """
        Transcreve com timestamps detalhados.
        
        Returns:
            Dict com transcrição e timestamps por palavra/segmento
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language=language if language != 'pt' else 'portuguese',
                word_timestamps=True,
                verbose=False
            )
            
            return {
                'text': result['text'].strip(),
                'language': result.get('language', language),
                'segments': result.get('segments', []),
                'words': self._extract_word_timestamps(result)
            }
            
        except Exception as e:
            print(f"❌ Erro na transcrição com timestamps: {str(e)}")
            return None
    
    def _extract_word_timestamps(self, result: Dict) -> list:
        """Extrai timestamps de palavras dos segmentos."""
        words = []
        
        for segment in result.get('segments', []):
            for word_data in segment.get('words', []):
                words.append({
                    'word': word_data.get('word', '').strip(),
                    'start': word_data.get('start', 0),
                    'end': word_data.get('end', 0),
                    'probability': word_data.get('probability', 0)
                })
        
        return words


class OfflineTranscriptionSystem:
    """Sistema completo de transcrição offline."""
    
    def __init__(self, whisper_model: str = "base"):
        """Inicializa sistema offline."""
        self.transcriber = LocalWhisperTranscriber(whisper_model)
        
        # Importar processador IA se disponível
        try:
            from .copilot_client import CopilotTranscriptionProcessor
            self.processor = CopilotTranscriptionProcessor()
            self.has_ai = True
            print("✅ Processamento IA disponível")
        except ImportError:
            self.processor = None
            self.has_ai = False
            print("ℹ️ Processamento IA não disponível (só transcrição)")
    
    def process_audio_complete(self, audio_path: str, language: str = 'pt') -> Dict:
        """
        Processa áudio completo: transcrição + análise IA.
        
        Returns:
            Dict com transcrição e análise (se disponível)
        """
        result = {
            'transcription': None,
            'ai_analysis': None,
            'success': False
        }
        
        # Transcrever
        transcription = self.transcriber.transcribe_file(audio_path, language)
        
        if not transcription:
            result['error'] = 'Falha na transcrição'
            return result
        
        result['transcription'] = transcription
        
        # Analisar com IA se disponível
        if self.has_ai and transcription['text'].strip():
            try:
                analysis = self.processor.extrair_informacoes_crm(transcription['text'])
                result['ai_analysis'] = analysis
                print("✅ Análise IA concluída")
            except Exception as e:
                print(f"⚠️ Erro na análise IA: {str(e)}")
                result['ai_analysis'] = None
        
        result['success'] = True
        return result