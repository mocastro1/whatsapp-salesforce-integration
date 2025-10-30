"""
Processador usando GitHub API para análise de transcrições e preparo para Salesforce
"""

import os
import json
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import re


class GitHubCopilotProcessor:
    """Processador usando GitHub API para análise inteligente."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Inicializa processador GitHub.
        
        Args:
            github_token: Token de acesso pessoal do GitHub
        """
        self.token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token é obrigatório")
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/json'
        }
    
    def processar_para_salesforce(self, transcricao_texto: str) -> Dict:
        """
        Processa transcrição para criar estrutura compatível com Salesforce.
        
        Args:
            transcricao_texto: Texto da transcrição real
            
        Returns:
            Dict com dados estruturados para Salesforce
        """
        
        # Usar análise local inteligente (já que GitHub Copilot API ainda não tem endpoint público)
        analise_local = self._analisar_texto_localmente(transcricao_texto)
        
        # Estruturar para Salesforce
        dados_salesforce = self._preparar_dados_salesforce(analise_local, transcricao_texto)
        
        return dados_salesforce
    
    def _analisar_texto_localmente(self, texto: str) -> Dict:
        """Análise local inteligente do texto."""
        
        analise = {
            'tipo_conversa': 'indefinido',
            'sentimento': 'neutro',
            'urgencia': 'baixa',
            'palavras_chave': [],
            'possivel_negocio': False,
            'necessita_followup': False,
            'categoria_crm': 'nota'
        }
        
        texto_lower = texto.lower()
        
        # Detectar tipo de conversa
        if any(palavra in texto_lower for palavra in ['reunião', 'meeting', 'encontro', 'apresentação']):
            analise['tipo_conversa'] = 'reuniao'
            analise['categoria_crm'] = 'evento'
        elif any(palavra in texto_lower for palavra in ['proposta', 'orçamento', 'contrato', 'venda']):
            analise['tipo_conversa'] = 'comercial'
            analise['categoria_crm'] = 'oportunidade'
            analise['possivel_negocio'] = True
        elif any(palavra in texto_lower for palavra in ['problema', 'suporte', 'erro', 'bug']):
            analise['tipo_conversa'] = 'suporte'
            analise['categoria_crm'] = 'case'
        
        # Detectar sentimento
        palavras_positivas = ['bom', 'ótimo', 'excelente', 'perfeito', 'consegui', 'sucesso', 'fechou']
        palavras_negativas = ['problema', 'erro', 'não consegui', 'cancelou', 'ruim', 'chateado']
        
        pos_count = sum(1 for palavra in palavras_positivas if palavra in texto_lower)
        neg_count = sum(1 for palavra in palavras_negativas if palavra in texto_lower)
        
        if pos_count > neg_count:
            analise['sentimento'] = 'positivo'
        elif neg_count > pos_count:
            analise['sentimento'] = 'negativo'
        
        # Detectar urgência
        if any(palavra in texto_lower for palavra in ['urgente', 'hoje', 'agora', 'imediato']):
            analise['urgencia'] = 'alta'
        elif any(palavra in texto_lower for palavra in ['semana', 'próximo', 'depois']):
            analise['urgencia'] = 'media'
        
        # Detectar necessidade de follow-up
        if any(palavra in texto_lower for palavra in ['ligar', 'retornar', 'agendar', 'marcar', 'voltar']):
            analise['necessita_followup'] = True
        
        # Extrair palavras-chave importantes
        palavras_relevantes = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', texto)
        analise['palavras_chave'] = list(set(palavras_relevantes))
        
        return analise
    
    def _extrair_contato(self, texto: str) -> Dict:
        """Extrai dados de contato do texto (nome, email, telefone)."""
        
        contato = {
            'nome': None,
            'email': None,
            'telefone': None,
            'empresa': None
        }
        
        # ESTRATÉGIA: Procurar por padrões específicos onde nome aparece
        # Padrão 1: "cliente de nome [Nome]" ou "nome do cliente [Nome]" ou "nome [Nome]"
        match_nome_cliente = re.search(
            r'(?:cliente de nome|nome do cliente|nome)\s+([A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+(?:\s+(?:da|de|do)\s+[A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+|\s+[A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+)*)',
            texto,
            re.IGNORECASE
        )
        
        if match_nome_cliente:
            contato['nome'] = match_nome_cliente.group(1).strip()
        else:
            # Padrão 2: Procurar sequências de 2+ nomes próprios capitalizados (com acentos)
            nomes_candidatos = re.findall(
                r'\b([A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+(?:\s+(?:da|de|do|e)\s+[A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+|\s+[A-ZÃÁÀÂÉ][a-záãàâéèêíïóôõöüú]+)+)\b',
                texto
            )
            
            if nomes_candidatos:
                # Usar primeiro nome encontrado, mas excluir palavras que não parecem nomes
                for nome_cand in nomes_candidatos:
                    # Excluir se contém palavras muito genéricas
                    if not any(palavra in nome_cand.lower() for palavra in ['preciso', 'criado', 'telefone', 'cliente']):
                        contato['nome'] = nome_cand
                        break
                
                # Se não encontrou nenhum que passe no filtro, usar o primeiro mesmo assim
                if not contato['nome'] and nomes_candidatos:
                    contato['nome'] = nomes_candidatos[0]
        
        # Extrair email
        match_email = re.search(r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', texto)
        if match_email:
            contato['email'] = match_email.group(1).lower()
        
        # Extrair telefone (sequência de dígitos de 7-15 dígitos, incluindo quando lido dígito por dígito)
        # Procurar "telefone é", "telefone dele é", ou "me é" seguido de dígitos
        match_telefone = re.search(
            r'(?:telefone|telefone dele|me)\s*(?:é|é)?\s*([\d\s,\.\-]+)',
            texto,
            re.IGNORECASE
        )
        
        if match_telefone:
            # Extrair apenas dígitos
            digitos = re.findall(r'\d', match_telefone.group(1))
            if 7 <= len(digitos) <= 15:
                contato['telefone'] = ''.join(digitos)
        
        # Se não encontrou via padrão acima, procurar qualquer sequência de 7+ dígitos
        if not contato['telefone']:
            match_digitos = re.search(r'\b(\d{7,15})\b', texto)
            if match_digitos:
                contato['telefone'] = match_digitos.group(1)
        
        # Extrair empresa
        match_empresa = re.search(r'(?:empresa|para (?:a|da|a empresa)?|cliente de)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', texto, re.IGNORECASE)
        if match_empresa:
            contato['empresa'] = match_empresa.group(1).strip()
        
        return contato
    
    def _criar_lead(self, contato: Dict, texto: str, analise: Dict, timestamp) -> Optional[Dict]:
        """Cria estrutura de Lead para Salesforce."""
        
        # Se não tem pelo menos nome, retornar None (não criar lead)
        if not contato.get('nome'):
            return None
        
        # Separar nome em FirstName e LastName
        partes_nome = contato['nome'].split()
        first_name = partes_nome[0] if partes_nome else 'Sem'
        last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else partes_nome[0] if partes_nome else 'Nome'
        
        lead = {
            'FirstName': first_name,
            'LastName': last_name,
            'Email': contato.get('email'),
            'Phone': contato.get('telefone'),
            'Company': contato.get('empresa') or 'Não informada',
            'LeadSource': 'Áudio/Transcrição',
            'Status': 'New',
            'Description': f'Contato extraído de transcrição de áudio\n\nTexto original: {texto[:200]}...',
            'Industry': 'Não especificado',
            'Rating': 'Hot' if analise.get('possivel_negocio') else 'Warm'
        }
        
        return lead
        
    def _preparar_dados_salesforce(self, analise: Dict, texto_original: str) -> Dict:
        """Prepara dados no formato Salesforce."""
        
        agora = datetime.now()
        
        # NOVO: Extrair dados de contato (nome, email, telefone)
        contato_extraido = self._extrair_contato(texto_original)
        
        # Estrutura base para Salesforce
        dados = {
            'Lead': self._criar_lead(contato_extraido, texto_original, analise, agora),
            'Contact': None,
            'Opportunity': None,
            'Task': None,
            'Event': None,
            'Note': {
                'Title': f'Transcrição de Áudio - {agora.strftime("%d/%m/%Y %H:%M")}',
                'Body': texto_original,
                'IsPrivate': False
            }
        }
        
        # Criar Task se necessário follow-up
        if analise['necessita_followup']:
            dados['Task'] = {
                'Subject': 'Follow-up da conversa de áudio',
                'Description': f'Baseado na conversa: {texto_original[:100]}...',
                'Status': 'Not Started',
                'Priority': 'Normal' if analise['urgencia'] != 'alta' else 'High',
                'ActivityDate': (agora + timedelta(days=1)).strftime('%Y-%m-%d')
            }
        
        # Criar Opportunity se é comercial
        if analise['possivel_negocio']:
            dados['Opportunity'] = {
                'Name': f'Oportunidade - Áudio {agora.strftime("%d/%m")}',
                'StageName': 'Prospecting',
                'CloseDate': (agora + timedelta(days=30)).strftime('%Y-%m-%d'),
                'Description': texto_original,
                'LeadSource': 'Áudio/Telefone'
            }
        
        # Criar Event se é reunião
        if analise['tipo_conversa'] == 'reuniao':
            dados['Event'] = {
                'Subject': 'Reunião mencionada em áudio',
                'Description': texto_original,
                'StartDateTime': agora.isoformat(),
                'EndDateTime': (agora + timedelta(hours=1)).isoformat(),
                'Type': 'Meeting'
            }
        
        # Adicionar metadados
        dados['_metadata'] = {
            'transcricao_timestamp': agora.isoformat(),
            'analise': analise,
            'fonte': 'audio_transcription',
            'processado_por': 'GitHub_Copilot_Processor'
        }
        
        return dados
    
    def gerar_resumo_salesforce(self, dados_sf: Dict) -> str:
        """Gera resumo dos dados que serão enviados ao Salesforce."""
        
        resumo = []
        resumo.append("🔄 DADOS PREPARADOS PARA SALESFORCE:")
        resumo.append("=" * 50)
        
        # Verificar cada tipo de objeto
        if dados_sf.get('Note'):
            resumo.append("📝 Note (Nota):")
            resumo.append(f"   • Título: {dados_sf['Note']['Title']}")
            
        if dados_sf.get('Task'):
            resumo.append("📋 Task (Tarefa):")
            resumo.append(f"   • Assunto: {dados_sf['Task']['Subject']}")
            resumo.append(f"   • Prioridade: {dados_sf['Task']['Priority']}")
            resumo.append(f"   • Data: {dados_sf['Task']['ActivityDate']}")
            
        if dados_sf.get('Opportunity'):
            resumo.append("💰 Opportunity (Oportunidade):")
            resumo.append(f"   • Nome: {dados_sf['Opportunity']['Name']}")
            resumo.append(f"   • Estágio: {dados_sf['Opportunity']['StageName']}")
            
        if dados_sf.get('Event'):
            resumo.append("📅 Event (Evento):")
            resumo.append(f"   • Assunto: {dados_sf['Event']['Subject']}")
        
        # Metadados da análise
        metadata = dados_sf.get('_metadata', {})
        analise = metadata.get('analise', {})
        
        resumo.append("\n🧠 ANÁLISE IA:")
        resumo.append(f"   • Tipo: {analise.get('tipo_conversa', 'indefinido')}")
        resumo.append(f"   • Sentimento: {analise.get('sentimento', 'neutro')}")
        resumo.append(f"   • Urgência: {analise.get('urgencia', 'baixa')}")
        resumo.append(f"   • Negócio: {'Sim' if analise.get('possivel_negocio') else 'Não'}")
        resumo.append(f"   • Follow-up: {'Necessário' if analise.get('necessita_followup') else 'Não'}")
        
        return "\n".join(resumo)


class SalesforceIntegrationPrep:
    """Preparação para integração com Salesforce."""
    
    def __init__(self, github_processor: GitHubCopilotProcessor):
        self.processor = github_processor
    
    def processar_transcricao_completa(self, arquivo_transcricao: str) -> Dict:
        """
        Processa arquivo de transcrição completo para Salesforce.
        
        Args:
            arquivo_transcricao: Caminho para arquivo de transcrição
            
        Returns:
            Dict com dados prontos para Salesforce
        """
        
        if not os.path.exists(arquivo_transcricao):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_transcricao}")
        
        # Ler transcrição
        with open(arquivo_transcricao, 'r', encoding='utf-8') as f:
            texto = f.read()
        
        # Processar com GitHub Copilot
        dados_sf = self.processor.processar_para_salesforce(texto)
        
        # Adicionar informações do arquivo
        dados_sf['_metadata']['arquivo_origem'] = arquivo_transcricao
        dados_sf['_metadata']['tamanho_texto'] = len(texto)
        
        return dados_sf
    
    def salvar_dados_salesforce(self, dados_sf: Dict, nome_arquivo: str = None) -> str:
        """Salva dados preparados em arquivo JSON."""
        
        if nome_arquivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"salesforce_data_{timestamp}.json"
        
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_sf, f, ensure_ascii=False, indent=2)
        
        return nome_arquivo