"""
Script simples para testar e consultar Totvs RM.

Uso:
  python tools/consulta_totvs.py

Requer configuração em .env:
  TOTVS_API_URL=https://...
  TOTVS_CLIENT_ID=...
  TOTVS_CLIENT_SECRET=...
  (ou TOTVS_API_KEY=...)
"""

from src.integration.totvs_rm_client import TotvsRMClient


def main():
    # Inicializar cliente
    print("🏢 Conectando ao Totvs RM...")
    client = TotvsRMClient()
    
    # Testar conexão
    if not client.test_connection():
        print("\n❌ Não foi possível conectar. Verifique suas credenciais no .env")
        return
    
    # Menu simples
    while True:
        print("\n" + "=" * 60)
        print("📋 MENU TOTVS RM")
        print("=" * 60)
        print("1. Listar Clientes")
        print("2. Listar Contas a Receber")
        print("3. Listar Contas a Pagar")
        print("4. Listar Pedidos")
        print("5. Listar Produtos")
        print("6. Sair")
        print("-" * 60)
        
        opcao = input("Escolha uma opção (1-6): ").strip()
        
        if opcao == "1":
            print("\n📍 Buscando clientes...")
            clientes = client.get_clientes(limite=10)
            if clientes:
                print(f"\nTotal: {len(clientes)} clientes\n")
                for c in clientes:
                    print(f"  Código: {c.get('codigo')}")
                    print(f"  Nome: {c.get('nome')}")
                    print(f"  Telefone: {c.get('telefonePrincipal', 'N/A')}")
                    print()
            else:
                print("Nenhum cliente encontrado.")
        
        elif opcao == "2":
            print("\n💰 Buscando contas a receber...")
            contas = client.get_contas_receber(limite=10)
            if contas:
                print(f"\nTotal: {len(contas)} contas\n")
                for c in contas:
                    print(f"  Número: {c.get('numero')}")
                    print(f"  Cliente: {c.get('nomeCliente', 'N/A')}")
                    print(f"  Valor: R$ {c.get('valor', 0):.2f}")
                    print(f"  Vencimento: {c.get('dataVencimento', 'N/A')}")
                    print()
            else:
                print("Nenhuma conta a receber encontrada.")
        
        elif opcao == "3":
            print("\n💳 Buscando contas a pagar...")
            contas = client.get_contas_pagar(limite=10)
            if contas:
                print(f"\nTotal: {len(contas)} contas\n")
                for c in contas:
                    print(f"  Número: {c.get('numero')}")
                    print(f"  Fornecedor: {c.get('nomeFornecedor', 'N/A')}")
                    print(f"  Valor: R$ {c.get('valor', 0):.2f}")
                    print(f"  Vencimento: {c.get('dataVencimento', 'N/A')}")
                    print()
            else:
                print("Nenhuma conta a pagar encontrada.")
        
        elif opcao == "4":
            print("\n📦 Buscando pedidos...")
            pedidos = client.get_pedidos(limite=10)
            if pedidos:
                print(f"\nTotal: {len(pedidos)} pedidos\n")
                for p in pedidos:
                    print(f"  Número: {p.get('numero')}")
                    print(f"  Cliente: {p.get('nomeCliente', 'N/A')}")
                    print(f"  Data: {p.get('data', 'N/A')}")
                    print(f"  Total: R$ {p.get('total', 0):.2f}")
                    print()
            else:
                print("Nenhum pedido encontrado.")
        
        elif opcao == "5":
            print("\n🏭 Buscando produtos...")
            produtos = client.get_produtos(limite=10)
            if produtos:
                print(f"\nTotal: {len(produtos)} produtos\n")
                for p in produtos:
                    print(f"  Código: {p.get('codigo')}")
                    print(f"  Descrição: {p.get('descricao')}")
                    print(f"  Preço: R$ {p.get('precoVenda', 0):.2f}")
                    print()
            else:
                print("Nenhum produto encontrado.")
        
        elif opcao == "6":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida!")


if __name__ == '__main__':
    main()
