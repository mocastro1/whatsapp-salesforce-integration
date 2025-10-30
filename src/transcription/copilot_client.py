"""
Cliente para usar GitHub Copilot API para transcrição e processamento
"""

import os
import requests
import json
from typing import Dict, Optional
import base64


class GitHubCopilotClient:
    """Cliente para usar GitHub Copilot API."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Inicializa cliente do GitHub Copilot.
        
        Args:
            token: Token do GitHub (Personal Access Token)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("Token do GitHub é obrigatório")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        
    def processar_texto_com_copilot(self, texto: str, prompt: str) -> Optional[str]:
        """
        Processa texto usando GitHub Copilot Chat.
        
        Args:
            texto: Texto a ser processado
            prompt: Prompt com instruções
            
        Returns:
            Resposta do Copilot ou None se erro
        """
        try:
            # Usar a API do GitHub Copilot Chat
            # Nota: Esta é uma implementação conceitual
            # A API real pode ter endpoints diferentes
            
            messages = [
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em análise de conversas de CRM e vendas."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nTexto para analisar: {texto}"
                }
            ]
            
            # Por enquanto, vamos simular uma resposta estruturada
            # até que a API oficial esteja disponível
            return self._simular_resposta_copilot(texto)
            
        except Exception as e:
            print(f"Erro ao processar com Copilot: {str(e)}")
            return None
    
    def _simular_resposta_copilot(self, texto: str) -> str:
        """
        Simula resposta do Copilot analisando o texto com regras simples.
        Esta é uma implementação temporária até a API oficial estar disponível.
        """
        
        # Análise simples por palavras-chave
        informacoes = {
            "contato": {"nome": None, "empresa": None},
            "lead": {"identificador": None, "status": None},
            "proxima_acao": {"acao": None, "data": None},
            "sentimento": "neutro",
            "observacoes": texto[:200] + "..." if len(texto) > 200 else texto
        }
        
        texto_lower = texto.lower()
        
        # Detectar nomes (palavras capitalizadas)
        import re
        nomes = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', texto)
        if nomes:
            # Pegar o primeiro nome que não seja uma palavra comum
            palavras_comuns = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Janeiro', 'Fevereiro']
            for nome in nomes:
                if nome not in palavras_comuns and len(nome) > 3:
                    informacoes["contato"]["nome"] = nome
                    break
        
        # Detectar empresas (Corp, Ltda, etc.)
        empresas = re.findall(r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\s+(?:Corp|Ltda|SA|Inc|Tech|Solutions)', texto)
        if empresas:
            informacoes["contato"]["empresa"] = empresas[0]
        
        # Detectar IDs de lead (padrões como ABC-123, Lead123, etc.)
        leads = re.findall(r'\b(?:lead\s+)?[A-Z]{2,4}-?\d{3,4}|\blead\s+\d+', texto, re.IGNORECASE)
        if leads:
            informacoes["lead"]["identificador"] = leads[0]
        
        # Detectar sentimento por palavras-chave
        if any(palavra in texto_lower for palavra in ['ótimo', 'excelente', 'animado', 'positivo', 'bom']):
            informacoes["sentimento"] = "positivo"
        elif any(palavra in texto_lower for palavra in ['ruim', 'problema', 'negativo', 'cancelou', 'chateado']):
            informacoes["sentimento"] = "negativo"
        
        # Detectar próximas ações
        if any(palavra in texto_lower for palavra in ['reunião', 'encontro', 'marcar', 'agendar']):
            informacoes["proxima_acao"]["acao"] = "Agendar reunião"
        elif any(palavra in texto_lower for palavra in ['ligar', 'telefonar', 'contatar']):
            informacoes["proxima_acao"]["acao"] = "Fazer contato telefônico"
        elif any(palavra in texto_lower for palavra in ['proposta', 'orçamento', 'enviar']):
            informacoes["proxima_acao"]["acao"] = "Enviar proposta"
        
        # Detectar datas simples
        datas = re.findall(r'\b(?:segunda|terça|quarta|quinta|sexta)-?feira\b|\b\d{1,2}/\d{1,2}\b|\b\d{1,2}\s+de\s+\w+', texto_lower)
        if datas:
            informacoes["proxima_acao"]["data"] = datas[0]
        
        return json.dumps(informacoes, ensure_ascii=False, indent=2)


class CopilotTranscriptionProcessor:
    """Processador usando GitHub Copilot para análise de transcrições."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Inicializa processador com Copilot."""
        self.copilot = GitHubCopilotClient(github_token)
    
    def extrair_informacoes_crm(self, texto_transcrito: str) -> Dict:
        """
        Extrai informações de CRM usando Copilot.
        
        Args:
            texto_transcrito: Texto da transcrição
            
        Returns:
            Dict com informações estruturadas
        """
        prompt = """
        Analise este texto de uma conversa de vendas/CRM e extraia informações no formato JSON:
        
        - Nome do contato e empresa
        - ID do lead se mencionado
        - Próxima ação e data
        - Sentimento da conversa (positivo/neutro/negativo)
        - Observações importantes
        
        Responda apenas com JSON válido.
        """
        
        try:
            resposta = self.copilot.processar_texto_com_copilot(texto_transcrito, prompt)
            
            if resposta:
                return json.loads(resposta)
            else:
                return self._resultado_vazio()
                
        except Exception as e:
            print(f"Erro no processamento: {str(e)}")
            return self._resultado_vazio()
    
    def _resultado_vazio(self) -> Dict:
        """Resultado vazio em caso de erro."""
        return {
            "contato": {"nome": None, "empresa": None},
            "lead": {"identificador": None, "status": None},
            "proxima_acao": {"acao": None, "data": None},
            "sentimento": "neutro",
            "observacoes": "Erro no processamento"
        }
    
    def gerar_resumo(self, informacoes: Dict) -> str:
        """Gera resumo das informações extraídas."""
        resumo = []
        
        contato = informacoes.get('contato', {})
        if contato.get('nome'):
            linha = f"👤 Contato: {contato['nome']}"
            if contato.get('empresa'):
                linha += f" ({contato['empresa']})"
            resumo.append(linha)
        
        lead = informacoes.get('lead', {})
        if lead.get('identificador'):
            resumo.append(f"🎯 Lead: {lead['identificador']}")
        
        proxima = informacoes.get('proxima_acao', {})
        if proxima.get('acao'):
            linha = f"📅 Próxima ação: {proxima['acao']}"
            if proxima.get('data'):
                linha += f" ({proxima['data']})"
            resumo.append(linha)
        
        sentimento = informacoes.get('sentimento', 'neutro')
        emoji = {"positivo": "😊", "neutro": "😐", "negativo": "😟"}
        resumo.append(f"{emoji.get(sentimento, '😐')} Sentimento: {sentimento}")
        
        return "\n".join(resumo) if resumo else "Nenhuma informação relevante extraída."


# Simulador de transcrição para teste sem API
class MockTranscriber:
    """Simulador de transcrição para testes sem API."""
    
    def transcribe_file(self, audio_path: str, language: str = 'pt') -> Optional[Dict]:
        """
        Simula transcrição de arquivo de áudio.
        
        Returns:
            Dict simulando resultado da transcrição
        """
        
        # Textos de exemplo baseados no nome do arquivo
        exemplos_transcricao = {
            'whatsapp': "Oi, acabei de falar com o João Silva da TechCorp sobre o lead TCP-001. Ele está bem interessado no nosso pacote premium. Vamos marcar uma reunião para segunda-feira que vem quando ele voltar da viagem de negócios.",
            'reuniao': "A reunião com a Maria Santos da ABC Corp foi muito produtiva. Ela aprovou a proposta inicial e quer avançar para a próxima fase. Preciso enviar o contrato até sexta-feira.",
            'ligacao': "Cliente da empresa XYZ ligou reclamando do serviço. Está muito chateado com os atrasos. Preciso resolver isso urgente e ligar de volta ainda hoje.",
            'default': "Esta é uma transcrição simulada do arquivo de áudio. O sistema está funcionando corretamente para testes sem usar APIs pagas."
        }
        
        # Escolher exemplo baseado no nome do arquivo
        nome_arquivo = os.path.basename(audio_path).lower()
        
        if 'whatsapp' in nome_arquivo or 'ptt' in nome_arquivo:
            texto = exemplos_transcricao['whatsapp']
        elif 'reuniao' in nome_arquivo:
            texto = exemplos_transcricao['reuniao']
        elif 'ligacao' in nome_arquivo or 'call' in nome_arquivo:
            texto = exemplos_transcricao['ligacao']
        else:
            texto = exemplos_transcricao['default']
        
        # Simular informações do arquivo
        file_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 1024
        
        return {
            'text': texto,
            'language': language,
            'file_path': audio_path,
            'file_size_mb': round(file_size / (1024*1024), 2),
            'mock': True  # Indicar que é simulação
        }