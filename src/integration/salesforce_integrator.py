"""
Salesforce API Integration - Conexão real com Salesforce CRM
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from dotenv import load_dotenv

try:
    from simple_salesforce import Salesforce
    from simple_salesforce.exceptions import SalesforceError
except ImportError:
    print("⚠️ simple-salesforce não encontrado. Instale com: pip install simple-salesforce")
    Salesforce = None
    SalesforceError = Exception


@dataclass 
class SalesforceConnection:
    """Configuração de conexão Salesforce."""
    username: str
    password: str
    security_token: str
    domain: str = 'login'  # 'login' para produção, 'test' para sandbox


class SalesforceIntegrator:
    """Integrador oficial Salesforce API."""
    
    def __init__(self, config: Optional[SalesforceConnection] = None):
        """Inicializar integrador Salesforce."""
        load_dotenv()
        
        self.config = config or self._load_config_from_env()
        self.sf = None
        self.connected = False
        
        # Conectar automaticamente ao Salesforce
        self.connect()
        
    def _load_config_from_env(self) -> SalesforceConnection:
        """Carregar configuração do arquivo .env."""
        return SalesforceConnection(
            username=os.getenv('SALESFORCE_USERNAME', ''),
            password=os.getenv('SALESFORCE_PASSWORD', ''),
            security_token=os.getenv('SALESFORCE_SECURITY_TOKEN', ''),
            domain=os.getenv('SALESFORCE_DOMAIN', 'login')
        )
    
    def connect(self) -> bool:
        """Conectar ao Salesforce."""
        if not Salesforce:
            print("❌ simple-salesforce não está instalado!")
            return False
            
        try:
            print("🔗 Conectando ao Salesforce...")
            
            # Validar credenciais
            if not all([self.config.username, self.config.password, self.config.security_token]):
                print("❌ Credenciais Salesforce incompletas no .env!")
                print("📝 Configure: SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_SECURITY_TOKEN")
                return False
            
            # Conectar
            self.sf = Salesforce(
                username=self.config.username,
                password=self.config.password,
                security_token=self.config.security_token,
                domain=self.config.domain
            )
            
            # Testar conexão
            user_info = self.sf.query("SELECT Id, Name FROM User WHERE Username = '{}'".format(self.config.username))
            
            if user_info['totalSize'] > 0:
                user_name = user_info['records'][0]['Name']
                print(f"✅ Conectado como: {user_name}")
                self.connected = True
                return True
            else:
                print("❌ Usuário não encontrado!")
                return False
                
        except SalesforceError as e:
            print(f"❌ Erro Salesforce: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Erro de conexão: {str(e)}")
            return False
    
    def lookup_account_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Buscar Account pelo telefone via Contact.
        
        Se encontrar um Contact com o telefone, retorna a Account vinculada.
        """
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
        
        try:
            # Normalizar telefone para a busca
            phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            # Primeiro procurar Contact com esse telefone
            query = f"""
                SELECT Id, FirstName, LastName, Phone, AccountId, Account.Name, Account.Apelido__c
                FROM Contact 
                WHERE Phone LIKE '%{phone_clean}%' 
                LIMIT 1
            """
            
            result = self.sf.query(query)
            
            if result['totalSize'] > 0:
                contact = result['records'][0]
                account = contact.get('Account')
                
                if account:
                    account_id = contact.get('AccountId')
                    account_name = account.get('Name')
                    apelido = account.get('Apelido__c')
                    
                    print(f"✅ Contact encontrado: {contact.get('FirstName')} {contact.get('LastName')}")
                    print(f"   Account: {account_name} (ID: {account_id})")
                    print(f"   Apelido__c: {apelido}")
                    
                    return {
                        'Id': account_id,
                        'Name': account_name,
                        'Apelido__c': apelido,
                        'Contact': {
                            'Id': contact.get('Id'),
                            'FirstName': contact.get('FirstName'),
                            'LastName': contact.get('LastName')
                        }
                    }
            
            # Se não encontrou Contact, procurar Account direto
            print(f"⚠️ Nenhum Contact encontrado com telefone: {phone} - tentando Account direto")
            
            query_account = f"""
                SELECT Id, Name, Phone, Apelido__c 
                FROM Account 
                WHERE Phone LIKE '%{phone_clean}%' 
                LIMIT 1
            """
            
            result_account = self.sf.query(query_account)
            if result_account['totalSize'] > 0:
                account = result_account['records'][0]
                print(f"✅ Account encontrado: {account.get('Name')}")
                print(f"   Apelido__c: {account.get('Apelido__c')}")
                return account
            
            print(f"⚠️ Nenhuma Account ou Contact encontrada com telefone: {phone}")
            return None
                
        except Exception as e:
            print(f"⚠️ Erro ao procurar Account/Contact: {e}")
            return None
    
    def create_lead(self, data: Dict[str, Any], source_phone: Optional[str] = None) -> Optional[str]:
        """Criar Lead no Salesforce.
        
        Se source_phone for fornecido, procura Account/Contact e vincula o Lead.
        Remove campos que o usuário não tem permissão de escrever.
        """
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
        
        # Se temos source_phone, procurar Account e extrair dados
        if source_phone:
            account_info = self.lookup_account_by_phone(source_phone)
            if account_info:
                # Adicionar AccountId ao Lead para vinculação
                data['AccountId'] = account_info.get('Id')
                print(f"✅ Lead será vinculado à Account: {account_info.get('Name')}")
                
                # Se tem Apelido__c, adicionar também
                if account_info.get('Apelido__c'):
                    data['Apelido__c'] = account_info.get('Apelido__c')
                    print(f"✅ Adicionado Apelido__c ao Lead: {account_info.get('Apelido__c')}")
        
        # Remover campos que o usuário não tem permissão de escrever
        # Estes campos serão preenchidos pelos triggers do Salesforce
        readonly_fields = [
            'Company',  # Será preenchido por trigger
            'EmFila__c',  # Será preenchido por trigger
            'Qualificado_para_negociacao__c',
            'VendedorF__c',
            'Supervisor_F__c',
            'GestaoF__c',
            'ReatribuirFila__c',
            'MostrarChatBeetalk__c',
            'CelularDivergente__c',
            'EmailDivergente__c',
            'VisitaConfirmada__c',
            'ReagendamentoConfirmado__c',
            'SDR_F__c',
            'Celular_Pendente__c'
        ]
        
        data_clean = {k: v for k, v in data.items() if k not in readonly_fields}
        
        try:
            result = self.sf.Lead.create(data_clean)
            lead_id = result['id']
            print(f"✅ Lead criado: {lead_id}")
            return lead_id
        except Exception as e:
            error_str = str(e)
            
            # Verificar se o erro foi no trigger AfterUpdate (Lead foi criado, mas trigger falhou)
            if "AfterUpdate" in error_str and "00Q89" in error_str:
                # Extrair o ID do Lead do erro
                import re
                match = re.search(r"id (00Q\w+)", error_str)
                if match:
                    lead_id = match.group(1)
                    print(f"⚠️  Lead criado apesar do erro de trigger: {lead_id}")
                    print(f"   Erro do trigger: Campos customizados não encontrados")
                    print(f"   Lead foi salvo no Salesforce")
                    return lead_id
            
            print(f"❌ Erro ao criar Lead: {error_str}")
            return None
    
    def search_lead_by_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Buscar Leads pelo nome (FirstName e/ou LastName)."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
        
        try:
            if not first_name and not last_name:
                print("❌ Precisa fornecer FirstName e/ou LastName!")
                return None
            
            # Construir query dinamicamente
            where_clauses = []
            if first_name:
                where_clauses.append(f"FirstName LIKE '%{first_name}%'")
            if last_name:
                where_clauses.append(f"LastName LIKE '%{last_name}%'")
            
            where_clause = " OR ".join(where_clauses) if where_clauses else ""
            
            query = f"""
                SELECT Id, FirstName, LastName, Phone, Email, Status, Company, IsConverted
                FROM Lead
                WHERE {where_clause}
                ORDER BY CreatedDate DESC
                LIMIT 10
            """
            
            result = self.sf.query(query)
            
            if result['totalSize'] > 0:
                print(f"✅ {result['totalSize']} Lead(s) encontrado(s):")
                for lead in result['records']:
                    status = " [CONVERTIDO]" if lead.get('IsConverted') else ""
                    print(f"   • {lead.get('FirstName', '')} {lead.get('LastName', '')} (ID: {lead['Id']}){status}")
                return result['records']
            else:
                print(f"⚠️ Nenhum Lead encontrado com esse nome")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar Lead: {e}")
            return None
    
    def search_lead_by_phone(self, phone: str) -> Optional[List[Dict[str, Any]]]:
        """Buscar Leads pelo telefone."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
        
        try:
            # Normalizar telefone para busca
            phone_clean = phone.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
            
            query = f"""
                SELECT Id, FirstName, LastName, Phone, Email, Status, Company, IsConverted
                FROM Lead
                WHERE Phone LIKE '%{phone_clean}%'
                ORDER BY CreatedDate DESC
                LIMIT 10
            """
            
            result = self.sf.query(query)
            
            if result['totalSize'] > 0:
                print(f"✅ {result['totalSize']} Lead(s) encontrado(s):")
                for lead in result['records']:
                    status = " [CONVERTIDO]" if lead.get('IsConverted') else ""
                    print(f"   • {lead.get('FirstName', '')} {lead.get('LastName', '')} - {lead.get('Phone')} (ID: {lead['Id']}){status}")
                return result['records']
            else:
                print(f"⚠️ Nenhum Lead encontrado com esse telefone")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar Lead: {e}")
            return None
    
    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Atualizar Lead existente no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return False
        
        try:
            # Remover campos que não podem ser atualizados
            readonly_fields = [
                'Company',
                'EmFila__c',
                'Qualificado_para_negociacao__c',
                'VendedorF__c',
                'Supervisor_F__c',
                'GestaoF__c',
                'ReatribuirFila__c',
                'MostrarChatBeetalk__c',
                'CelularDivergente__c',
                'EmailDivergente__c',
                'VisitaConfirmada__c',
                'ReagendamentoConfirmado__c',
                'SDR_F__c',
                'Celular_Pendente__c'
            ]
            
            data_clean = {k: v for k, v in data.items() if k not in readonly_fields}
            
            if not data_clean:
                print("⚠️ Nenhum campo válido para atualizar!")
                return False
            
            # Atualizar Lead
            self.sf.Lead.update(lead_id, data_clean)
            print(f"✅ Lead atualizado: {lead_id}")
            print(f"   Campos atualizados: {list(data_clean.keys())}")
            return True
            
        except Exception as e:
            error_str = str(e)
            
            # Se o erro foi no trigger, pode ter sido atualizado parcialmente
            if "AfterUpdate" in error_str:
                print(f"⚠️ Lead foi atualizado, mas o trigger falhou")
                print(f"   Erro do trigger: {error_str[:100]}...")
                return True  # Consideramos sucesso parcial
            
            print(f"❌ Erro ao atualizar Lead: {error_str}")
            return False
    
    def create_contact(self, data: Dict[str, Any]) -> Optional[str]:
        """Criar Contact no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
            
        try:
            result = self.sf.Contact.create(data)
            contact_id = result['id']
            print(f"✅ Contact criado: {contact_id}")
            return contact_id
        except Exception as e:
            print(f"❌ Erro ao criar Contact: {str(e)}")
            return None
    
    def create_opportunity(self, data: Dict[str, Any]) -> Optional[str]:
        """Criar Opportunity no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
            
        try:
            result = self.sf.Opportunity.create(data)
            opp_id = result['id']
            print(f"✅ Opportunity criada: {opp_id}")
            return opp_id
        except Exception as e:
            print(f"❌ Erro ao criar Opportunity: {str(e)}")
            return None
    
    def create_task(self, data: Dict[str, Any]) -> Optional[str]:
        """Criar Task no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
            
        try:
            result = self.sf.Task.create(data)
            task_id = result['id']
            print(f"✅ Task criada: {task_id}")
            return task_id
        except Exception as e:
            print(f"❌ Erro ao criar Task: {str(e)}")
            return None
    
    def create_event(self, data: Dict[str, Any]) -> Optional[str]:
        """Criar Event no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
            
        try:
            result = self.sf.Event.create(data)
            event_id = result['id']
            print(f"✅ Event criado: {event_id}")
            return event_id
        except Exception as e:
            print(f"❌ Erro ao criar Event: {str(e)}")
            return None
    
    def create_note(self, data: Dict[str, Any]) -> Optional[str]:
        """Criar Note no Salesforce."""
        if not self.connected:
            print("❌ Não conectado ao Salesforce!")
            return None
            
        try:
            # Notes em Salesforce usam ContentNote (Lightning) ou Note (Classic)
            # Vamos usar ContentNote que é mais moderno
            
            content_data = {
                'Title': data.get('Title', 'Nota de Transcrição'),
                'Content': data.get('Body', '').encode('utf-8')  # ContentNote precisa de base64
            }
            
            result = self.sf.ContentNote.create(content_data)
            note_id = result['id']
            print(f"✅ Note criada: {note_id}")
            return note_id
        except Exception as e:
            print(f"❌ Erro ao criar Note: {str(e)}")
            # Tentar com Note clássica
            try:
                classic_data = {
                    'Title': data.get('Title', 'Nota de Transcrição'),
                    'Body': data.get('Body', ''),
                    'IsPrivate': data.get('IsPrivate', False)
                }
                result = self.sf.Note.create(classic_data)
                note_id = result['id']
                print(f"✅ Note (classic) criada: {note_id}")
                return note_id
            except Exception as e2:
                print(f"❌ Erro ao criar Note clássica: {str(e2)}")
                return None
    
    def process_salesforce_data(self, data: Dict[str, Any]) -> Dict[str, Optional[str]]:
        """Processar dados completos do Salesforce."""
        if not self.connected:
            if not self.connect():
                return {}
        
        results = {}
        
        # Processar cada tipo de objeto
        for obj_type in ['Lead', 'Contact', 'Opportunity', 'Task', 'Event', 'Note']:
            obj_data = data.get(obj_type)
            if obj_data:
                print(f"\n📤 Criando {obj_type}...")
                
                if obj_type == 'Lead':
                    results['lead_id'] = self.create_lead(obj_data)
                elif obj_type == 'Contact':
                    results['contact_id'] = self.create_contact(obj_data)
                elif obj_type == 'Opportunity':
                    results['opportunity_id'] = self.create_opportunity(obj_data)
                elif obj_type == 'Task':
                    results['task_id'] = self.create_task(obj_data)
                elif obj_type == 'Event':
                    results['event_id'] = self.create_event(obj_data)
                elif obj_type == 'Note':
                    results['note_id'] = self.create_note(obj_data)
        
        return results
    
    def test_connection(self) -> bool:
        """Testar conexão Salesforce."""
        if self.connect():
            try:
                # Fazer uma query simples para testar
                result = self.sf.query("SELECT Id, Name FROM Organization LIMIT 1")
                org_name = result['records'][0]['Name'] if result['totalSize'] > 0 else 'Unknown'
                print(f"🏢 Organização: {org_name}")
                return True
            except Exception as e:
                print(f"❌ Erro no teste: {str(e)}")
                return False
        return False


class AudioToSalesforceWorkflow:
    """Workflow completo: Áudio → Transcrição → Salesforce."""
    
    def __init__(self):
        """Inicializar workflow."""
        self.sf_integrator = SalesforceIntegrator()
    
    def process_audio_file(self, audio_path: str, send_to_salesforce: bool = True) -> Dict[str, Any]:
        """Processar arquivo de áudio completo."""
        print("🎵 AUDIO → SALESFORCE WORKFLOW")
        print("="*50)
        
        results = {
            'transcricao': None,
            'dados_preparados': None,
            'salesforce_ids': {},
            'sucesso': False
        }
        
        try:
            # 1. Transcrever áudio (assumindo que já temos)
            print("🎯 Procurando transcrições existentes...")
            
            # Procurar arquivo de dados Salesforce já processado
            # Remover extensão e adicionar sufixo correto
            if audio_path.endswith('_transcricao_real'):
                base_name = audio_path  # já está sem extensão
            else:
                base_name = os.path.splitext(os.path.basename(audio_path))[0]

            outputs_dir = 'outputs'
            dados_file = os.path.join(outputs_dir, f"{base_name}_salesforce_data.json")

            if not os.path.exists(dados_file):
                print(f"❌ Arquivo não encontrado: {dados_file}")
                print("📝 Execute primeiro: python teste_github_salesforce.py")
                return results

            # 2. Carregar dados preparados
            print(f"📂 Carregando: {dados_file}")
            with open(dados_file, 'r', encoding='utf-8') as f:
                dados_salesforce = json.load(f)
            
            results['dados_preparados'] = dados_salesforce
            
            # 3. Enviar para Salesforce
            if send_to_salesforce:
                print("\n🚀 Enviando para Salesforce...")
                sf_results = self.sf_integrator.process_salesforce_data(dados_salesforce)
                results['salesforce_ids'] = sf_results
                
                if any(sf_results.values()):
                    results['sucesso'] = True
                    print("\n✅ SUCESSO! Dados enviados para Salesforce!")
                else:
                    print("\n⚠️ Nenhum objeto foi criado no Salesforce.")
            else:
                print("\n🔄 Modo simulação - não enviando para Salesforce")
                results['sucesso'] = True
            
            return results
            
        except Exception as e:
            print(f"\n❌ Erro no workflow: {str(e)}")
            return results
    
    def get_status_report(self, results: Dict[str, Any]) -> str:
        """Gerar relatório de status."""
        if not results['sucesso']:
            return "❌ Workflow falhou!"
        
        report = "📊 RELATÓRIO DO WORKFLOW\n"
        report += "="*40 + "\n"
        
        if results['dados_preparados']:
            metadata = results['dados_preparados'].get('_metadata', {})
            analise = metadata.get('analise', {})
            
            report += f"🎯 Tipo detectado: {analise.get('tipo_conversa', 'indefinido')}\n"
            report += f"😊 Sentimento: {analise.get('sentimento', 'neutro')}\n"
            report += f"⚡ Urgência: {analise.get('urgencia', 'baixa')}\n"
            
            # Contar objetos criados
            objetos_criados = []
            for key, value in results['dados_preparados'].items():
                if key != '_metadata' and value is not None:
                    objetos_criados.append(key)
            
            report += f"📋 Objetos preparados: {', '.join(objetos_criados)}\n"
        
        if results['salesforce_ids']:
            report += "\n🏢 OBJETOS CRIADOS NO SALESFORCE:\n"
            for obj_type, obj_id in results['salesforce_ids'].items():
                if obj_id:
                    report += f"   • {obj_type}: {obj_id}\n"
        
        return report


def main():
    """Teste do integrador Salesforce."""
    print("🏢 TESTE SALESFORCE INTEGRATOR")
    print("="*50)
    
    integrator = SalesforceIntegrator()
    
    # Testar conexão
    if integrator.test_connection():
        print("\n✅ Conexão Salesforce OK!")
        
        # Exemplo de uso
        workflow = AudioToSalesforceWorkflow()
        
        # Procurar arquivos de áudio para processar
        audio_files = []
        for file in os.listdir('.'):
            if any(file.endswith(ext) for ext in ['.mp3', '.wav', '.ogg', '.m4a']):
                audio_files.append(file)
        
        if audio_files:
            print(f"\n🎵 Arquivos de áudio encontrados: {len(audio_files)}")
            for i, audio_file in enumerate(audio_files, 1):
                print(f"   {i}. {audio_file}")
                
                # Processar primeiro arquivo como exemplo
                if i == 1:
                    print(f"\n🎯 Processando: {audio_file}")
                    results = workflow.process_audio_file(audio_file, send_to_salesforce=False)  # Modo teste
                    print(f"\n{workflow.get_status_report(results)}")
                    break
        else:
            print("\n📁 Nenhum arquivo de áudio encontrado.")
    else:
        print("\n❌ Falha na conexão Salesforce!")
        print("\n📝 Verifique suas credenciais no arquivo .env:")
        print("   SALESFORCE_USERNAME=seu_email")
        print("   SALESFORCE_PASSWORD=sua_senha")  
        print("   SALESFORCE_SECURITY_TOKEN=seu_token")
        print("   SALESFORCE_DOMAIN=login  # ou 'test' para sandbox")


if __name__ == "__main__":
    main()