#!/usr/bin/env python3
"""
Evolution API Client - Cliente para integração com Evolution API
Substitui o Twilio pelo Evolution API para gerenciamento de WhatsApp
"""

import requests
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EvolutionClient:
    """Cliente para comunicar com Evolution API"""
    
    def __init__(
        self,
        api_url: str = "http://localhost:3001",
        api_key: str = "evolution_api_key_2025",
        instance_name: str = "salesforce-bot"
    ):
        """
        Inicializar cliente Evolution
        
        Args:
            api_url: URL base da Evolution API (padrão: http://localhost:3001)
            api_key: API Key para autenticação
            instance_name: Nome da instância WhatsApp
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.instance_name = instance_name
        self.headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(f"✅ EvolutionClient inicializado para {api_url}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Fazer requisição HTTP para Evolution API
        
        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Path do endpoint (ex: /instance/fetchInstances)
            data: Payload (para POST/PUT)
            timeout: Timeout em segundos
            
        Returns:
            Response em formato dict
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, json=data, headers=self.headers, timeout=timeout)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=self.headers, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP inválido: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Erro de conexão com Evolution API: {e}")
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Timeout na requisição: {e}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Erro HTTP: {response.status_code} - {response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Verificar status da Evolution API"""
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=5)
            return response.json()
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status: {e}")
            return {"status": "error", "message": str(e)}
    
    def list_instances(self) -> list:
        """Listar todas as instâncias criadas"""
        try:
            response = self._make_request("GET", "/instance/fetchInstances")
            return response.get("instances", [])
        except Exception as e:
            logger.error(f"❌ Erro ao listar instâncias: {e}")
            return []
    
    def create_instance(
        self,
        instance_name: str = None,
        integration: str = "whatsapp-web"
    ) -> Dict[str, Any]:
        """
        Criar nova instância WhatsApp
        
        Args:
            instance_name: Nome da instância (padrão: salesforce-bot)
            integration: Tipo de integração (padrão: whatsapp-web)
            
        Returns:
            Resposta da API com detalhes da instância criada
        """
        instance_name = instance_name or self.instance_name
        
        payload = {
            "instanceName": instance_name,
            "clientName": "evolution",
            "integration": integration,
            "installSystemPackages": True,
            "setupMachineRabbitmq": False,
            "setupMachineDaphne": False,
            "setupMachineRedis": False
        }
        
        try:
            logger.info(f"📋 Criando instância: {instance_name}")
            response = self._make_request("POST", "/instance/create", data=payload)
            logger.info(f"✅ Instância criada: {response}")
            return response
        except Exception as e:
            logger.error(f"❌ Erro ao criar instância: {e}")
            raise
    
    def get_qr_code(self, instance_name: str = None) -> Optional[str]:
        """
        Obter QR Code da instância para scannear com WhatsApp
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            String com dados do QR Code ou None se não disponível
        """
        instance_name = instance_name or self.instance_name
        
        try:
            response = self._make_request("GET", f"/instance/qrcode/{instance_name}")
            qr_code = response.get("qrcode")
            
            if qr_code:
                logger.info(f"✅ QR Code obtido para {instance_name}")
                return qr_code
            else:
                logger.warning(f"⚠️ Nenhum QR Code disponível para {instance_name}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter QR Code: {e}")
            return None
    
    def get_connection_status(self, instance_name: str = None) -> str:
        """
        Verificar status de conexão da instância
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            Status (ex: 'connected', 'disconnected', 'connecting')
        """
        instance_name = instance_name or self.instance_name
        
        try:
            response = self._make_request("GET", f"/instance/connectionState/{instance_name}")
            status = response.get("state", "unknown")
            logger.info(f"📊 Status de {instance_name}: {status}")
            return status
        except Exception as e:
            logger.warning(f"⚠️ Erro ao verificar status: {e}")
            return "unknown"
    
    def send_message(
        self,
        phone_number: str,
        message: str,
        instance_name: str = None
    ) -> Dict[str, Any]:
        """
        Enviar mensagem de texto via WhatsApp
        
        Args:
            phone_number: Número do WhatsApp (ex: 5511999999999)
            message: Conteúdo da mensagem
            instance_name: Nome da instância
            
        Returns:
            Resposta da API com dados da mensagem enviada
        """
        instance_name = instance_name or self.instance_name
        
        # Normalizar número se necessário
        if not phone_number.startswith("55"):
            phone_number = f"55{phone_number}"
        
        payload = {
            "number": phone_number,
            "options": {
                "delay": 1000,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": message
            }
        }
        
        try:
            logger.info(f"📤 Enviando mensagem para {phone_number}: {message[:50]}...")
            response = self._make_request(
                "POST",
                f"/message/sendText/{instance_name}",
                data=payload
            )
            
            logger.info(f"✅ Mensagem enviada: {response.get('key', {}).get('id', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            raise
    
    def send_message_to_group(
        self,
        group_jid: str,
        message: str,
        instance_name: str = None
    ) -> Dict[str, Any]:
        """
        Enviar mensagem para grupo
        
        Args:
            group_jid: JID do grupo (ex: 120363123456789-1234567890@g.us)
            message: Conteúdo da mensagem
            instance_name: Nome da instância
            
        Returns:
            Resposta da API
        """
        instance_name = instance_name or self.instance_name
        
        payload = {
            "number": group_jid,
            "options": {
                "delay": 1000,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": message
            }
        }
        
        try:
            logger.info(f"📤 Enviando mensagem para grupo: {message[:50]}...")
            response = self._make_request(
                "POST",
                f"/message/sendText/{instance_name}",
                data=payload
            )
            return response
        except Exception as e:
            logger.error(f"❌ Erro ao enviar para grupo: {e}")
            raise
    
    def send_media(
        self,
        phone_number: str,
        media_url: str,
        caption: str = "",
        media_type: str = "image",
        instance_name: str = None
    ) -> Dict[str, Any]:
        """
        Enviar mídia (imagem, áudio, vídeo)
        
        Args:
            phone_number: Número do WhatsApp
            media_url: URL da mídia
            caption: Legenda (opcional)
            media_type: Tipo de mídia (image, audio, video, document)
            instance_name: Nome da instância
            
        Returns:
            Resposta da API
        """
        instance_name = instance_name or self.instance_name
        
        if not phone_number.startswith("55"):
            phone_number = f"55{phone_number}"
        
        payload = {
            "number": phone_number,
            "options": {
                "delay": 1000,
                "presence": "composing"
            },
            "mediaMessage": {
                "mediatype": media_type,
                "media": media_url,
                "caption": caption
            }
        }
        
        try:
            logger.info(f"📸 Enviando {media_type} para {phone_number}: {media_url}")
            response = self._make_request(
                "POST",
                f"/message/sendMedia/{instance_name}",
                data=payload
            )
            return response
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mídia: {e}")
            raise
    
    def configure_webhook(
        self,
        webhook_url: str,
        events: list = None,
        instance_name: str = None
    ) -> Dict[str, Any]:
        """
        Configurar webhook para receber eventos
        
        Args:
            webhook_url: URL do webhook (ex: http://localhost:8000/evolution-webhook)
            events: Lista de eventos a receber
            instance_name: Nome da instância
            
        Returns:
            Resposta da API
        """
        instance_name = instance_name or self.instance_name
        
        # Eventos padrão
        if events is None:
            events = [
                "QRCODE_UPDATED",
                "MESSAGES_SET",
                "MESSAGES_UPSERT",
                "MESSAGES_EDITED",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
                "PRESENCE_UPDATE",
                "CHATS_SET",
                "CHATS_UPSERT",
                "CONTACTS_SET",
                "CONTACTS_UPSERT"
            ]
        
        payload = {
            "url": webhook_url,
            "events": events,
            "webhookByEvents": False,
            "deliveryConfirmation": True,
            "ignoreOwnMessages": False
        }
        
        try:
            logger.info(f"🔗 Configurando webhook: {webhook_url}")
            response = self._make_request(
                "POST",
                f"/webhook/set/{instance_name}",
                data=payload
            )
            logger.info(f"✅ Webhook configurado")
            return response
        except Exception as e:
            logger.error(f"❌ Erro ao configurar webhook: {e}")
            raise


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Testar cliente
    print("=" * 80)
    print("🧪 TESTE DO CLIENTE EVOLUTION")
    print("=" * 80)
    
    client = EvolutionClient()
    
    # 1. Verificar status
    print("\n[1️⃣] Verificando status da API...")
    status = client.get_status()
    print(f"✅ Status: {status.get('message', 'OK')}")
    
    # 2. Listar instâncias
    print("\n[2️⃣] Listando instâncias...")
    instances = client.list_instances()
    print(f"📊 Total: {len(instances)} instâncias")
    for instance in instances:
        print(f"  - {instance.get('name')}: {instance.get('status')}")
    
    print("\n" + "=" * 80)
    print("✅ CLIENTE PRONTO PARA USO!")
    print("=" * 80)
