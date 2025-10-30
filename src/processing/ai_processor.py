"""
Processador de IA para extrair informações estruturadas de transcrições
"""

import os
import json
import openai
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import re


class TranscriptionProcessor:
    """Processa transcrições usando IA para extrair informações de CRM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o processador de IA.
        
        Args:
            api_key: Chave da API OpenAI. Se None, usa variável de ambiente.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key da OpenAI é obrigatória")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def extrair_informacoes_crm(self, texto_transcrito: str) -> Dict:
        """
        Extrai informações estruturadas do texto transcrito para CRM.
        
        Args:
            texto_transcrito: Texto da transcrição de áudio
        
        Returns:
            Dict com informações extraídas
        """
        prompt = self._criar_prompt_extracao(texto_transcrito)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Modelo mais econômico
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um assistente especializado em extrair informações de CRM de conversas de vendas.
                        Analise o texto e extraia informações relevantes no formato JSON solicitado.
                        Seja preciso e extraia apenas informações que estão claramente mencionadas."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            resultado = json.loads(response.choices[0].message.content)
            return self._processar_resultado(resultado, texto_transcrito)
            
        except Exception as e:
            print(f"Erro no processamento IA: {str(e)}")
            return self._resultado_vazio()
    
    def _criar_prompt_extracao(self, texto: str) -> str:
        """Cria prompt para extração de informações."""
        return f"""
        Analise o seguinte texto de uma conversa de vendas/CRM e extraia as informações no formato JSON:

        TEXTO: "{texto}"

        Extraia as seguintes informações (se mencionadas):
        {{
            "contato": {{
                "nome": "Nome da pessoa mencionada",
                "empresa": "Empresa/organização se mencionada",
                "cargo": "Cargo se mencionado"
            }},
            "lead": {{
                "identificador": "ID, código ou nome do lead se mencionado",
                "status": "Status atual do lead",
                "produto_interesse": "Produto ou serviço de interesse"
            }},
            "proxima_acao": {{
                "acao": "Descrição da próxima ação a ser tomada",
                "data": "Data mencionada (formato YYYY-MM-DD se possível)",
                "prazo": "Prazo em dias se mencionado relativamente (ex: 'em 15 dias')"
            }},
            "observacoes": "Informações importantes da conversa",
            "sentimento": "positivo/neutro/negativo - como foi o tom da conversa",
            "urgencia": "baixa/media/alta - nível de urgência percebido"
        }}

        Se alguma informação não estiver presente, use null para esse campo.
        """
    
    def _processar_resultado(self, resultado: Dict, texto_original: str) -> Dict:
        """Processa e enriquece o resultado da IA."""
        # Adicionar timestamp
        resultado['processamento'] = {
            'timestamp': datetime.now().isoformat(),
            'texto_original': texto_original,
            'modelo_usado': 'gpt-4o-mini'
        }
        
        # Processar datas relativas
        if resultado.get('proxima_acao', {}).get('prazo'):
            resultado['proxima_acao']['data_calculada'] = self._calcular_data_relativa(
                resultado['proxima_acao']['prazo']
            )
        
        return resultado
    
    def _calcular_data_relativa(self, prazo_texto: str) -> Optional[str]:
        """Calcula data baseada em texto relativo (ex: 'em 15 dias')."""
        try:
            # Buscar padrões como "15 dias", "1 semana", etc.
            numeros = re.findall(r'\d+', prazo_texto.lower())
            if not numeros:
                return None
            
            dias = 0
            numero = int(numeros[0])
            
            if 'dia' in prazo_texto.lower():
                dias = numero
            elif 'semana' in prazo_texto.lower():
                dias = numero * 7
            elif 'mes' in prazo_texto.lower() or 'mês' in prazo_texto.lower():
                dias = numero * 30
            else:
                dias = numero  # assume dias por padrão
            
            data_futura = datetime.now() + timedelta(days=dias)
            return data_futura.strftime('%Y-%m-%d')
            
        except Exception:
            return None
    
    def _resultado_vazio(self) -> Dict:
        """Retorna estrutura vazia em caso de erro."""
        return {
            "contato": {"nome": None, "empresa": None, "cargo": None},
            "lead": {"identificador": None, "status": None, "produto_interesse": None},
            "proxima_acao": {"acao": None, "data": None, "prazo": None},
            "observacoes": None,
            "sentimento": "neutro",
            "urgencia": "baixa",
            "processamento": {
                "timestamp": datetime.now().isoformat(),
                "erro": "Falha no processamento da IA"
            }
        }
    
    def gerar_resumo(self, informacoes: Dict) -> str:
        """Gera resumo textual das informações extraídas."""
        resumo = []
        
        # Contato
        contato = informacoes.get('contato', {})
        if contato.get('nome'):
            linha_contato = f"👤 Contato: {contato['nome']}"
            if contato.get('empresa'):
                linha_contato += f" ({contato['empresa']})"
            resumo.append(linha_contato)
        
        # Lead
        lead = informacoes.get('lead', {})
        if lead.get('identificador'):
            resumo.append(f"🎯 Lead: {lead['identificador']}")
        
        # Próxima ação
        proxima = informacoes.get('proxima_acao', {})
        if proxima.get('acao'):
            linha_acao = f"📅 Próxima ação: {proxima['acao']}"
            if proxima.get('data'):
                linha_acao += f" - Data: {proxima['data']}"
            resumo.append(linha_acao)
        
        # Sentimento
        sentimento = informacoes.get('sentimento', 'neutro')
        emoji_sentimento = {"positivo": "😊", "neutro": "😐", "negativo": "😟"}
        resumo.append(f"{emoji_sentimento.get(sentimento, '😐')} Sentimento: {sentimento}")
        
        return "\n".join(resumo) if resumo else "Nenhuma informação relevante extraída."