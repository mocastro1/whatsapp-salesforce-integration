"""
Cliente Totvs RM - Integração via API REST

Suporta autenticação OAuth 2.0 e API Key.
Consultas típicas: Contas a receber/pagar, Clientes, Pedidos, Estoque, etc.

Configuração via .env:
- TOTVS_API_URL=https://api.totvs.com.br/...
- TOTVS_CLIENT_ID=seu_client_id
- TOTVS_CLIENT_SECRET=seu_client_secret
- OU
- TOTVS_API_KEY=sua_chave_api
- TOTVS_EMPRESA=código_empresa
- TOTVS_FILIAL=código_filial
"""

import os
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()


class TotvsRMClient:
    """Cliente para integração com Totvs RM API."""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_key: Optional[str] = None,
        empresa: Optional[str] = None,
        filial: Optional[str] = None,
    ):
        """
        Inicializar cliente Totvs RM.
        
        Args:
            api_url: URL base da API Totvs RM
            client_id: Client ID para OAuth
            client_secret: Client Secret para OAuth
            api_key: API Key (alternativa ao OAuth)
            empresa: Código da empresa
            filial: Código da filial
        """
        self.api_url = api_url or os.getenv('TOTVS_API_URL', 'https://api.totvs.com.br')
        self.client_id = client_id or os.getenv('TOTVS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('TOTVS_CLIENT_SECRET')
        self.api_key = api_key or os.getenv('TOTVS_API_KEY')
        self.empresa = empresa or os.getenv('TOTVS_EMPRESA', '01')
        self.filial = filial or os.getenv('TOTVS_FILIAL', '01')
        
        self.access_token = None
        self.session = requests.Session()
        
        # Se temos credenciais OAuth, fazer login
        if self.client_id and self.client_secret:
            self._authenticate_oauth()
        elif self.api_key:
            self._setup_api_key_auth()
        else:
            print("⚠️ Nenhuma credencial configurada. Configure TOTVS_CLIENT_ID/SECRET ou TOTVS_API_KEY no .env")
    
    def _authenticate_oauth(self):
        """Autenticar usando OAuth 2.0."""
        try:
            print("🔐 Autenticando com OAuth 2.0...")
            
            # URL típica de token (pode variar)
            token_url = f"{self.api_url}/oauth/token" if "oauth" not in self.api_url else self.api_url
            
            payload = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
            
            response = requests.post(token_url, data=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data.get('access_token')
            
            if self.access_token:
                print("✅ Autenticação OAuth OK")
                self.session.headers.update({'Authorization': f'Bearer {self.access_token}'})
            else:
                print("❌ Não foi possível obter token")
                
        except Exception as e:
            print(f"❌ Erro na autenticação OAuth: {e}")
    
    def _setup_api_key_auth(self):
        """Configurar autenticação com API Key."""
        print("🔑 Usando autenticação por API Key")
        self.session.headers.update({'X-API-Key': self.api_key})
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fazer requisição à API Totvs RM.
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Path do endpoint (ex: /api/v1/fco/documentoreceber)
            params: Query parameters
            json_data: Payload JSON
            
        Returns:
            Response dict ou None
        """
        url = f"{self.api_url}{endpoint}"
        
        # Adicionar empresa/filial aos params se necessário
        if params is None:
            params = {}
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, params=params, json=json_data, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, params=params, json=json_data, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=30)
            else:
                print(f"❌ Método HTTP inválido: {method}")
                return None
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return {"status": "success"}
            
            return response.json() if response.text else {}
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return None
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
            return None
    
    # ========== CONSULTAS FINANCEIRAS ==========
    
    def get_contas_receber(
        self,
        filtro_status: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict]:
        """
        Obter contas a receber.
        
        Args:
            filtro_status: Status (Aberto, Pago, Vencido, etc)
            limite: Quantidade de registros
            
        Returns:
            Lista de contas a receber
        """
        params = {
            'empresa': self.empresa,
            'filial': self.filial,
            'top': limite,
        }
        
        if filtro_status:
            params['statusdoc'] = filtro_status
        
        result = self._request('GET', '/api/v1/fco/documentoreceber', params=params)
        
        if result and 'value' in result:
            print(f"✅ {len(result['value'])} contas a receber obtidas")
            return result['value']
        return []
    
    def get_contas_pagar(
        self,
        filtro_status: Optional[str] = None,
        limite: int = 100,
    ) -> List[Dict]:
        """
        Obter contas a pagar.
        
        Args:
            filtro_status: Status (Aberto, Pago, Vencido, etc)
            limite: Quantidade de registros
            
        Returns:
            Lista de contas a pagar
        """
        params = {
            'empresa': self.empresa,
            'filial': self.filial,
            'top': limite,
        }
        
        if filtro_status:
            params['statusdoc'] = filtro_status
        
        result = self._request('GET', '/api/v1/fco/documentopagar', params=params)
        
        if result and 'value' in result:
            print(f"✅ {len(result['value'])} contas a pagar obtidas")
            return result['value']
        return []
    
    # ========== CONSULTAS DE CLIENTES ==========
    
    def get_clientes(self, limite: int = 100) -> List[Dict]:
        """
        Obter lista de clientes.
        
        Args:
            limite: Quantidade de registros
            
        Returns:
            Lista de clientes
        """
        params = {
            'empresa': self.empresa,
            'top': limite,
        }
        
        result = self._request('GET', '/api/v1/mnt/cliente', params=params)
        
        if result and 'value' in result:
            print(f"✅ {len(result['value'])} clientes obtidos")
            return result['value']
        return []
    
    def get_cliente_por_codigo(self, codigo: str) -> Optional[Dict]:
        """
        Obter cliente específico por código.
        
        Args:
            codigo: Código do cliente
            
        Returns:
            Dados do cliente
        """
        result = self._request('GET', f'/api/v1/mnt/cliente/{codigo}')
        
        if result:
            print(f"✅ Cliente {codigo} obtido")
        return result
    
    # ========== CONSULTAS DE PEDIDOS ==========
    
    def get_pedidos(self, limite: int = 100) -> List[Dict]:
        """
        Obter lista de pedidos de venda.
        
        Args:
            limite: Quantidade de registros
            
        Returns:
            Lista de pedidos
        """
        params = {
            'empresa': self.empresa,
            'filial': self.filial,
            'top': limite,
        }
        
        result = self._request('GET', '/api/v1/vnd/pedidovenda', params=params)
        
        if result and 'value' in result:
            print(f"✅ {len(result['value'])} pedidos obtidos")
            return result['value']
        return []
    
    def get_pedido_por_numero(self, numero: str) -> Optional[Dict]:
        """
        Obter pedido específico.
        
        Args:
            numero: Número do pedido
            
        Returns:
            Dados do pedido
        """
        result = self._request('GET', f'/api/v1/vnd/pedidovenda/{numero}')
        
        if result:
            print(f"✅ Pedido {numero} obtido")
        return result
    
    # ========== CONSULTAS DE ESTOQUE ==========
    
    def get_produtos(self, limite: int = 100) -> List[Dict]:
        """
        Obter lista de produtos.
        
        Args:
            limite: Quantidade de registros
            
        Returns:
            Lista de produtos
        """
        params = {
            'empresa': self.empresa,
            'top': limite,
        }
        
        result = self._request('GET', '/api/v1/est/produto', params=params)
        
        if result and 'value' in result:
            print(f"✅ {len(result['value'])} produtos obtidos")
            return result['value']
        return []
    
    def get_estoque_produto(self, codigo_produto: str) -> Optional[Dict]:
        """
        Obter estoque de um produto.
        
        Args:
            codigo_produto: Código do produto
            
        Returns:
            Dados de estoque
        """
        params = {
            'empresa': self.empresa,
            'filial': self.filial,
        }
        
        result = self._request(
            'GET',
            f'/api/v1/est/saldoestoque/{codigo_produto}',
            params=params
        )
        
        if result:
            print(f"✅ Estoque do produto {codigo_produto} obtido")
        return result
    
    # ========== CONSULTAS GERAIS ==========
    
    def test_connection(self) -> bool:
        """Testar conexão com API Totvs RM."""
        try:
            print("🔗 Testando conexão com Totvs RM...")
            
            result = self._request('GET', '/api/v1/gpo/empresa', params={'top': 1})
            
            if result:
                print("✅ Conexão com Totvs RM OK")
                return True
            else:
                print("❌ Falha ao conectar com Totvs RM")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False


def main():
    """Demo do cliente Totvs RM."""
    print("🏢 TESTE CLIENTE TOTVS RM")
    print("=" * 60)
    
    # Inicializar cliente
    client = TotvsRMClient()
    
    # Testar conexão
    if not client.test_connection():
        print("\n⚠️ Configure as credenciais no .env primeiro:")
        print("   TOTVS_API_URL=https://...")
        print("   TOTVS_CLIENT_ID=...")
        print("   TOTVS_CLIENT_SECRET=...")
        print("   OU")
        print("   TOTVS_API_KEY=...")
        return
    
    # Exemplos de consultas
    print("\n📊 Exemplos de Consultas:")
    print("-" * 60)
    
    print("\n1️⃣ Clientes:")
    clientes = client.get_clientes(limite=5)
    if clientes:
        for c in clientes[:3]:
            print(f"   - {c.get('codigo')} - {c.get('nome')}")
    
    print("\n2️⃣ Contas a Receber:")
    contas_rec = client.get_contas_receber(limite=5)
    if contas_rec:
        for cr in contas_rec[:3]:
            print(f"   - Doc: {cr.get('numero')} - R$ {cr.get('valor')}")
    
    print("\n3️⃣ Contas a Pagar:")
    contas_pag = client.get_contas_pagar(limite=5)
    if contas_pag:
        for cp in contas_pag[:3]:
            print(f"   - Doc: {cp.get('numero')} - R$ {cp.get('valor')}")
    
    print("\n4️⃣ Produtos:")
    produtos = client.get_produtos(limite=5)
    if produtos:
        for p in produtos[:3]:
            print(f"   - {p.get('codigo')} - {p.get('descricao')}")
    
    print("\n" + "=" * 60)
    print("✅ Demo concluída!")


if __name__ == '__main__':
    main()
