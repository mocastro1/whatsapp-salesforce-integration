"""
Orchestrator: end-to-end flow that ties transcription extraction, phone matching and Salesforce actions.
"""
import os
import json
from typing import Optional, Dict, Any

from datetime import datetime

# Reuse existing processors
try:
    from transcription.copilot_client import CopilotTranscriptionProcessor
    from processing.github_processor import GitHubCopilotProcessor
except Exception as e:
    # Local import paths rely on script running from repo root; rethrow if missing
    raise

from src.matching.phone_matcher import normalize_phone, lookup_salesforce_by_phone, rank_candidates_by_name


class Orchestrator:
    def __init__(self, sf_integrator=None, github_token: Optional[str] = None):
        # sf_integrator can be an instance of SalesforceIntegrator or None
        self.sf_integrator = sf_integrator
        # GitHub processor (used for preparing Salesforce payloads)
        try:
            self.github_processor = GitHubCopilotProcessor(github_token or os.getenv('GITHUB_TOKEN') or 'fake_token_for_local')
        except ValueError:
            # In case token not present, create with fake token
            self.github_processor = GitHubCopilotProcessor('fake_token_for_local')
        # Copilot transcription processor for extracting contact info
        try:
            self.copilot_transcriber = CopilotTranscriptionProcessor()
        except Exception:
            # If Copilot client raises due to missing token, still allow local simulation via MockTranscriber
            self.copilot_transcriber = CopilotTranscriptionProcessor('fake_token_for_local')

    def process_by_basename(self, base_name: str, source_phone: Optional[str] = None, simulate_sf: bool = True) -> Dict[str, Any]:
        """Processa arquivos em outputs/<base_name>_transcricao_real.txt e gera decisões.

        Returns a dict with keys: action, matched_id, candidates, dados_salesforce, metadata
        """
        outputs_dir = os.path.join(os.getcwd(), 'outputs')
        arquivo_transcricao = os.path.join(outputs_dir, f"{base_name}_transcricao_real.txt")

        result = {
            'base_name': base_name,
            'action': None,
            'matched_id': None,
            'candidates': [],
            'dados_salesforce': None,
            'metadata': {}
        }

        if not os.path.exists(arquivo_transcricao):
            result['action'] = 'missing_transcription'
            return result

        with open(arquivo_transcricao, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        # Extrair texto puro (remover cabeçalho se presente)
        linhas = conteudo.split('\n')
        texto = ' '.join([l for l in linhas if l.strip() and not l.startswith('TRANSCRIÇÃO REAL') and not l.startswith('=') and not l.startswith('Modelo:') and not l.startswith('Idioma:')])

        # 1) Extract structured info with CopilotTranscriptionProcessor
        try:
            extracao = self.copilot_transcriber.extrair_informacoes_crm(texto)
        except Exception:
            extracao = {
                'contato': {'nome': None, 'empresa': None},
                'lead': {'identificador': None, 'status': None},
                'proxima_acao': {'acao': None, 'data': None},
                'sentimento': 'neutro',
                'observacoes': texto
            }

        result['metadata']['extraction'] = extracao

        # 2) Prepare dados para Salesforce using GitHub processor
        dados_salesforce = self.github_processor.processar_para_salesforce(texto)
        result['dados_salesforce'] = dados_salesforce

        # 3) Determine phone to use
        phone_to_use = None
        if source_phone:
            phone_to_use = source_phone
        else:
            # try to read source phone from existing outputs metadata if present
            poss_meta_file = os.path.join(outputs_dir, f"{base_name}_analise_real.json")
            if os.path.exists(poss_meta_file):
                try:
                    with open(poss_meta_file, 'r', encoding='utf-8') as mf:
                        meta = json.load(mf)
                        phone_to_use = meta.get('source_phone') or meta.get('transcricao_real', {}).get('source_phone')
                except Exception:
                    phone_to_use = None

        normalized = None
        if phone_to_use:
            normalized = normalize_phone(phone_to_use)
            result['metadata']['source_phone'] = phone_to_use
            result['metadata']['normalized_phone'] = normalized

        # 4) Try to find Lead by extracted name
        extracted_name = extracao.get('contato', {}).get('nome')
        matched_id = None
        decision = None
        all_candidates = []
        
        # First try: Search by extracted name
        if extracted_name and self.sf_integrator and not simulate_sf:
            # Split name into first and last
            name_parts = extracted_name.strip().split()
            first_name = name_parts[0] if len(name_parts) > 0 else None
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else None
            
            search_results = None
            if last_name:
                search_results = self.sf_integrator.search_lead_by_name(first_name=first_name, last_name=last_name)
            elif first_name:
                search_results = self.sf_integrator.search_lead_by_name(last_name=first_name)
            
            if search_results and len(search_results) > 0:
                # Se encontrou leads por nome - procurar o primeiro não-convertido
                for lead in search_results:
                    if not lead.get('IsConverted', False):  # Pular leads convertidos
                        matched_id = lead['Id']
                        decision = 'attach_to_existing_by_name'
                        all_candidates = search_results
                        print(f"[Orchestrator] Lead encontrado por nome: {matched_id}")
                        break
                
                # Se todos foram convertidos, usar o primeiro mesmo assim
                if not matched_id and len(search_results) > 0:
                    matched_id = search_results[0]['Id']
                    decision = 'attach_to_existing_by_name_converted'
                    all_candidates = search_results
                    print(f"[Orchestrator] Todos os Leads encontrados foram convertidos. Usando: {matched_id}")
        
        # Second try: Search by phone (apenas se não encontrou por nome)
        if not matched_id and normalized and self.sf_integrator and not simulate_sf:
            search_results = self.sf_integrator.search_lead_by_phone(normalized)
            if search_results and len(search_results) > 0:
                # Procurar o primeiro não-convertido
                for lead in search_results:
                    if not lead.get('IsConverted', False):
                        matched_id = lead['Id']
                        decision = 'attach_to_existing_by_phone'
                        all_candidates = search_results
                        print(f"[Orchestrator] Lead encontrado por telefone: {matched_id}")
                        break
                
                # Se todos foram convertidos, usar o primeiro
                if not matched_id and len(search_results) > 0:
                    matched_id = search_results[0]['Id']
                    decision = 'attach_to_existing_by_phone_converted'
                    all_candidates = search_results
                    print(f"[Orchestrator] Todos os Leads por telefone foram convertidos. Usando: {matched_id}")
        
        # If still no match, mark as no_candidates_found
        if not matched_id:
            decision = 'no_candidates_found'

        result['action'] = decision
        result['matched_id'] = matched_id
        result['candidates'] = all_candidates

        # 5) EXECUTE the decision if we have Salesforce integrator
        if self.sf_integrator and not simulate_sf:
            print(f"[Orchestrator] Executando ação: {decision}")
            
            if decision in ['attach_to_existing', 'attach_to_existing_by_name', 'attach_to_existing_by_phone', 
                           'attach_to_existing_by_name_converted', 'attach_to_existing_by_phone_converted']:
                # Update existing lead
                try:
                    lead_id = matched_id
                    update_data = dados_salesforce.get('Lead', {})
                    if update_data:
                        self.sf_integrator.update_lead(lead_id, update_data)
                        result['dados_salesforce']['Lead']['_execution_status'] = 'UPDATED'
                        print(f"✅ Lead atualizado: {lead_id}")
                except Exception as e:
                    error_str = str(e)
                    # Se o erro foi "cannot reference converted lead", procurar outro Lead
                    if "CANNOT_UPDATE_CONVERTED_LEAD" in error_str and all_candidates and len(all_candidates) > 1:
                        print(f"⚠️ Lead foi convertido. Procurando alternativa...")
                        # Procurar outro Lead não-convertido da lista
                        for alt_lead in all_candidates[1:]:
                            if not alt_lead.get('IsConverted', False):
                                print(f"   Tentando Lead alternativo: {alt_lead['Id']}")
                                try:
                                    self.sf_integrator.update_lead(alt_lead['Id'], update_data)
                                    result['dados_salesforce']['Lead']['_execution_status'] = 'UPDATED'
                                    result['matched_id'] = alt_lead['Id']
                                    print(f"✅ Lead alternativo atualizado: {alt_lead['Id']}")
                                    return result
                                except Exception as e2:
                                    print(f"   ❌ Erro neste Lead também: {str(e2)[:60]}")
                                    continue
                        # Se nenhum funcionou
                        print(f"❌ Nenhum Lead disponível para atualizar")
                        result['dados_salesforce']['Lead']['_execution_status'] = f'ERROR: {error_str}'
                    else:
                        print(f"❌ Erro ao atualizar lead: {e}")
                        result['dados_salesforce']['Lead']['_execution_status'] = f'ERROR: {str(e)}'
            
            elif decision == 'no_candidates_found' or decision == 'no_confident_match':
                # Create new lead
                try:
                    lead_data = dados_salesforce.get('Lead', {})
                    if lead_data:
                        # Ensure we have at least LastName
                        if not lead_data.get('LastName'):
                            lead_data['LastName'] = lead_data.get('FirstName', 'Sem Nome')
                        
                        # Pass source_phone to lookup Account and extract Apelido__c
                        new_lead_id = self.sf_integrator.create_lead(lead_data, source_phone=phone_to_use)
                        result['dados_salesforce']['Lead']['_execution_status'] = f'CREATED: {new_lead_id}'
                        result['matched_id'] = new_lead_id
                        print(f"✅ Lead criado: {new_lead_id}")
                        
                        # Also create Note with transcription
                        if dados_salesforce.get('Note'):
                            try:
                                note_data = dados_salesforce['Note']
                                note_data['ParentId'] = new_lead_id  # Link note to the new lead
                                self.sf_integrator.create_note(note_data)
                                result['dados_salesforce']['Note']['_execution_status'] = 'CREATED'
                                print(f"✅ Nota criada para o lead: {new_lead_id}")
                            except Exception as e:
                                print(f"⚠️  Erro ao criar nota: {e}")
                except Exception as e:
                    print(f"❌ Erro ao criar lead: {e}")
                    result['dados_salesforce']['Lead']['_execution_status'] = f'ERROR: {str(e)}'
        
        # 6) Persist decision into outputs
        timestamp = datetime.now().isoformat()
        result['metadata']['processed_at'] = timestamp

        out_file = os.path.join(outputs_dir, f"{base_name}_orchestrator_result.json")
        with open(out_file, 'w', encoding='utf-8') as of:
            json.dump(result, of, ensure_ascii=False, indent=2)

        return result
