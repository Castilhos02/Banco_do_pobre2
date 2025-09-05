import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

# Refatorar classes existentes (Passo 1 do plano)
class Pessoa:
    def __init__(self, cpf: str, nome: str, nascimento: str):
        self.cpf = cpf  # Stores CPF as object attribute
        self.nome = nome  # Stores nome as object attribute
        self.nascimento = nascimento  # Stores nascimento as object attribute

    def __str__(self):
        return f"Nome: {self.nome}, CPF: {self.cpf}"


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        # Ensure that the transacao object itself is stored or a representation that can be reconstructed
        # For now, storing a dictionary representation for simplicity and compatibility with existing JSON saving
        self._transacoes.append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor
        })

    def gerar_extrato(self):
        print("\n--- Extrato ---")
        if not self._transacoes:
            print("Não foram realizadas movimentações.")
        else:
            for transacao in self._transacoes:
                print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        print("---------------")


class Transacao(ABC):
    def __init__(self, valor: float):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @abstractmethod
    def registrar(self, conta):
        pass


class Deposito(Transacao):
    def registrar(self, conta):
        if self.valor <= 0:
            print("❌ Valor de depósito deve ser positivo.")
            return False

        conta.saldo += self.valor
        conta.historico.adicionar_transacao(self)
        print(f"✅ Depósito de R$ {self.valor:.2f} realizado com sucesso!")
        return True


class Saque(Transacao):
    def registrar(self, conta):
        if self.valor <= 0:
            print("❌ Valor de saque deve ser positivo.")
            return False

        if self.valor > conta.saldo:
            print("❌ Saldo insuficiente.")
            return False

        LIMITE_SAQUES = 3
        LIMITE_VALOR = 500

        # Get current date
        data_hoje = datetime.now().date()

        # Count saques performed today by comparing date parts
        saques_hoje = len([t for t in conta.historico.transacoes
                          if t['tipo'] == 'Saque'
                          and datetime.strptime(t['data'].split(' ')[0], "%d/%m/%Y").date() == data_hoje])

        if saques_hoje >= LIMITE_SAQUES:
            print("❌ Limite de saques diários excedido.")
            return False

        if self.valor > LIMITE_VALOR:
            print("❌ Valor máximo por saque é R$ 500,00.")
            return False

        conta.saldo -= self.valor
        conta.historico.adicionar_transacao(self)
        print(f"✅ Saque de R$ {self.valor:.2f} realizado com sucesso!")
        return True


# Step 2: Examine Conta class
class Conta:
    def __init__(self, numero: int, cliente):
        self._numero = numero  # Stores account number as object attribute
        self._cliente = cliente  # Stores client object as object attribute
        self._saldo = 0.0  # Stores balance as object attribute
        self._historico = Historico()  # Stores Historico object as object attribute

    @property
    def numero(self):
        return self._numero

    @property
    def cliente(self):
        return self._cliente

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor

    @property
    def historico(self):
        return self._historico

    def depositar(self, valor: float):
        deposito = Deposito(valor)
        return deposito.registrar(self)

    def sacar(self, valor: float):
        saque = Saque(valor)
        return saque.registrar(self)

    def __str__(self):
        return f"Conta {self.numero} - {self.cliente.pessoa.nome} - Saldo: R$ {self.saldo:.2f}"


class Cliente:
    def __init__(self, pessoa: Pessoa, endereco: str):
        self._pessoa = pessoa
        self._endereco = endereco
        self._contas = []

    @property
    def pessoa(self):
        return self._pessoa

    @property
    def endereco(self):
        return self._endereco

    @property
    def contas(self):
        return self._contas

    def adicionar_conta(self, conta: Conta):
        self._contas.append(conta)

    def __str__(self):
        return f"Cliente: {self.pessoa.nome} - CPF: {self.pessoa.cpf}"


# Step 3 & 4: Analyze and modify Banco class
class Banco:
    def __init__(self):
        self._clientes = []  # Stores clients as a list of objects
        self._contas = []  # Stores accounts as a list of objects
        self._proximo_numero_conta = 1

    def adicionar_cliente(self, cliente: Cliente):
        # Check if client already exists based on CPF
        if self.buscar_cliente_por_cpf(cliente.pessoa.cpf):
            print(f"❌ Cliente com CPF {cliente.pessoa.cpf} já cadastrado.")
            return False
        self._clientes.append(cliente)
        print(f"✅ Cliente {cliente.pessoa.nome} cadastrado com sucesso!")
        return True

    # Implementar autenticação e cadastro (Passo 2 do plano)
    def cadastrar_cliente(self, cpf: str, nome: str, nascimento: str, endereco: str) -> Cliente:
        """Cadastra um novo cliente no banco."""
        # Check if client already exists
        if self.buscar_cliente_por_cpf(cpf):
            print(f"❌ Cliente com CPF {cpf} já cadastrado.")
            return None

        # Create Pessoa and Cliente objects
        pessoa = Pessoa(cpf, nome, nascimento)
        cliente = Cliente(pessoa, endereco)

        # Add the new client using the existing method
        self.adicionar_cliente(cliente) # adicionar_cliente already prints success message
        return cliente

    def autenticar_cliente(self, cpf: str) -> Cliente:
        """Autentica um cliente buscando por CPF."""
        cliente = self.buscar_cliente_por_cpf(cpf)
        if cliente:
            print(f"✅ Cliente {cliente.pessoa.nome} autenticado com sucesso!")
            return cliente
        else:
            print(f"❌ Cliente com CPF {cpf} não encontrado.")
            return None


    def criar_conta(self, cliente: Cliente) -> Conta:
        # Check if client exists
        if not self.buscar_cliente_por_cpf(cliente.pessoa.cpf):
             print(f"❌ Cliente com CPF {cliente.pessoa.cpf} não encontrado.")
             return None

        conta = Conta(self._proximo_numero_conta, cliente)
        self._proximo_numero_conta += 1
        cliente.adicionar_conta(conta)
        self._contas.append(conta)
        print(f"✅ Conta {conta.numero} criada para o cliente {cliente.pessoa.nome}!")
        return conta

    def buscar_cliente_por_cpf(self, cpf: str) -> Cliente:
        for cliente in self._clientes:
            if cliente.pessoa.cpf == cpf:
                return cliente
        return None

    def buscar_conta_por_numero(self, numero: int) -> Conta:
        for conta in self._contas:
            if conta.numero == numero:
                return conta
        return None

    def listar_clientes(self):
        if not self._clientes:
            print("🚫 Nenhum cliente cadastrado.")
            return
        print("\n📋 Lista de Clientes e Contas:")
        for cliente in self._clientes:
            print(f"- {cliente}")
            if cliente.contas:
                for conta in cliente.contas:
                    print(f"  - {conta}")
            else:
                print("  (Nenhuma conta associada)")

    # Salvar e carregar dados de forma persistente (Passo 6 do plano)
    def salvar_dados(self, arquivo="banco_data.json"):
        """Salva os dados do banco em um arquivo JSON."""
        dados = {
            "proximo_numero_conta": self._proximo_numero_conta,
            "clientes": [
                {
                    "cpf": cliente.pessoa.cpf,
                    "nome": cliente.pessoa.nome,
                    "nascimento": cliente.pessoa.nascimento,
                    "endereco": cliente.endereco,
                    # Store account numbers for linking during loading
                    "contas_numeros": [conta.numero for conta in cliente.contas]
                } for cliente in self._clientes
            ],
            "contas": [
                {
                    "numero": conta.numero,
                    # Store CPF of the client to link during loading
                    "cpf_cliente": conta.cliente.pessoa.cpf,
                    "saldo": conta.saldo,
                    # Store transaction history as dictionaries
                    "historico": conta.historico.transacoes
                } for conta in self._contas
            ]
        }

        try:
            with open(arquivo, "w", encoding='utf-8') as f: # Added encoding
                json.dump(dados, f, indent=4, ensure_ascii=False)
            print("✅ Dados salvos com sucesso!")
        except IOError as e: # More specific error handling
            print(f"❌ Erro de I/O ao salvar dados: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao salvar dados: {e}")


    def carregar_dados(self, arquivo="banco_data.json"):
        """Carrega os dados do banco a partir de um arquivo JSON."""
        try:
            with open(arquivo, "r", encoding='utf-8') as f: # Added encoding
                dados = json.load(f)
                self._proximo_numero_conta = dados.get("proximo_numero_conta", 1)

                # Clear existing data before loading to prevent duplicates
                self._clientes = []
                self._contas = []

                # Recriar clientes
                clientes_data = dados.get("clientes", [])
                for cliente_data in clientes_data:
                    try:
                        pessoa = Pessoa(cliente_data["cpf"], cliente_data["nome"], cliente_data["nascimento"])
                        cliente = Cliente(pessoa, cliente_data["endereco"])
                        self._clientes.append(cliente)
                    except KeyError as e:
                        print(f"⚠️ Dados de cliente incompletos no arquivo JSON: faltando {e}. Cliente não carregado.")
                    except Exception as e:
                        print(f"⚠️ Erro ao recriar cliente {cliente_data.get('cpf', 'desconhecido')}: {e}. Cliente não carregado.")

                # Recriar contas and link to clients
                contas_data = dados.get("contas", [])
                for conta_data in contas_data:
                    try:
                        cliente = self.buscar_cliente_por_cpf(conta_data["cpf_cliente"])
                        if cliente:
                            conta = Conta(conta_data["numero"], cliente)
                            conta.saldo = conta_data.get("saldo", 0.0) # Use .get for robustness
                            conta.historico._transacoes = conta_data.get("historico", []) # Use .get for robustness
                            cliente.adicionar_conta(conta)
                            self._contas.append(conta)
                        else:
                            print(f"⚠️ Cliente com CPF {conta_data.get('cpf_cliente', 'desconhecido')} para conta {conta_data.get('numero', 'desconhecida')} não encontrado. Conta não carregada.")
                    except KeyError as e:
                         print(f"⚠️ Dados de conta incompletos no arquivo JSON: faltando {e}. Conta não carregada.")
                    except Exception as e:
                        print(f"⚠️ Erro ao recriar conta {conta_data.get('numero', 'desconhecida')}: {e}. Conta não carregada.")

                # Re-establish account relationships within clients based on loaded account numbers
                # This step is necessary because accounts were loaded into _contas list,
                # but the links within client.contas need to be re-established with the actual objects
                for cliente_data in clientes_data:
                    cliente = self.buscar_cliente_por_cpf(cliente_data["cpf"])
                    if cliente:
                        cliente._contas = [] # Clear existing account list (if any)
                        for conta_numero in cliente_data.get("contas_numeros", []):
                            conta = self.buscar_conta_por_numero(conta_numero)
                            if conta:
                                cliente.adicionar_conta(conta)
                            else:
                                print(f"⚠️ Conta com número {conta_numero} para cliente {cliente.pessoa.cpf} não encontrada durante o linking. Conta não associada ao cliente.")

                print("✅ Dados carregados com sucesso!")


        except FileNotFoundError:
            print("Arquivo de dados não encontrado. Iniciando com dados vazios.")
        except json.JSONDecodeError:
             print("❌ Erro ao decodificar o arquivo JSON. Verifique a formatação.")
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar dados: {e}")


# Criar menu de interação (Passo 3 do plano)
def exibir_menu_inicial():
    """Exibe o menu de opções iniciais para o usuário."""
    print("\n================ MENU INICIAL ================")
    print("[1] Cadastrar Cliente")
    print("[2] Autenticar Cliente")
    print("[3] Criar Conta Corrente")
    print("[0] Sair")
    print("==============================================")

def exibir_menu_operacoes():
    """Exibe o menu de opções de operações bancárias para o usuário autenticado."""
    print("\n============ MENU DE OPERAÇÕES ============")
    print("[4] Depositar")
    print("[5] Sacar")
    print("[6] Extrato")
    print("[7] Voltar ao Menu Inicial") # New option to return to initial menu
    print("[0] Sair")
    print("===========================================")


def main():
    banco = Banco()
    banco.carregar_dados()

    cliente_autenticado = None # Variable to store authenticated client

    while True:
        if cliente_autenticado and cliente_autenticado.contas: # Show operations menu if client is authenticated and has accounts
            exibir_menu_operacoes()
            opcao = input("=> Informe a opção desejada: ")

            if opcao == "4":
                print("Opção selecionada: Depositar")
                # Deposit logic (already implemented in previous steps)
                numero_conta = input("Informe o número da conta: ")
                conta_encontrada = None
                for conta in cliente_autenticado.contas: # Search within authenticated client's accounts
                    if str(conta.numero) == numero_conta:
                        conta_encontrada = conta
                        break

                if conta_encontrada:
                    try:
                        valor_deposito = float(input("Informe o valor do depósito: "))
                        conta_encontrada.depositar(valor_deposito)
                    except ValueError:
                        print("❌ Valor inválido. Por favor, insira um número.")
                else:
                    print("❌ Conta não encontrada para este cliente.")

            elif opcao == "5":
                print("Opção selecionada: Sacar")
                # Withdraw logic (already implemented in previous steps)
                numero_conta = input("Informe o número da conta: ")
                conta_encontrada = None
                for conta in cliente_autenticado.contas: # Search within authenticated client's accounts
                    if str(conta.numero) == numero_conta:
                        conta_encontrada = conta
                        break

                if conta_encontrada:
                    try:
                        valor_saque = float(input("Informe o valor do saque: "))
                        conta_encontrada.sacar(valor_saque)
                    except ValueError:
                        print("❌ Valor inválido. Por favor, insira um número.")
                else:
                    print("❌ Conta não encontrada para este cliente.")

            elif opcao == "6":
                print("Opção selecionada: Extrato")
                # Statement logic (already implemented in previous steps)
                numero_conta = input("Informe o número da conta: ")
                conta_encontrada = None
                for conta in cliente_autenticado.contas: # Search within authenticated client's accounts
                    if str(conta.numero) == numero_conta:
                        conta_encontrada = conta
                        break

                if conta_encontrada:
                    conta_encontrada.historico.gerar_extrato()
                else:
                    print("❌ Conta não encontrada para este cliente.")

            elif opcao == "7": # Option to return to initial menu
                cliente_autenticado = None # Clear authenticated client
                print("Voltando ao menu inicial.")

            elif opcao == "0":
                print("Saindo do sistema. Obrigado!")
                banco.salvar_dados()
                break
            else:
                print("❌ Opção inválida! Por favor, selecione uma opção válida.")

        else: # Show initial menu
            exibir_menu_inicial()
            opcao = input("=> Informe a opção desejada: ")

            if opcao == "1":
                print("Opção selecionada: Cadastrar Cliente")
                cpf = input("Informe o CPF (somente números): ")
                nome = input("Informe o nome completo: ")
                nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
                endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
                banco.cadastrar_cliente(cpf, nome, nascimento, endereco)

            elif opcao == "2":
                print("Opção selecionada: Autenticar Cliente")
                cpf = input("Informe o CPF para autenticar: ")
                cliente_autenticado = banco.autenticar_cliente(cpf)
                if cliente_autenticado and not cliente_autenticado.contas:
                    print("⚠️ Cliente autenticado, mas sem contas associadas. Crie uma conta para acessar as operações bancárias.")
                    cliente_autenticado = None # Clear authentication if no accounts

            elif opcao == "3":
                print("Opção selecionada: Criar Conta Corrente")
                cpf = input("Informe o CPF do cliente para criar a conta: ")
                cliente = banco.buscar_cliente_por_cpf(cpf)
                if cliente:
                    banco.criar_conta(cliente)
                else:
                    print("❌ Cliente não encontrado. Cadastre o cliente primeiro.")

            elif opcao == "0":
                print("Saindo do sistema. Obrigado!")
                banco.salvar_dados()
                break
            else:
                print("❌ Opção inválida! Por favor, selecione uma opção válida.")


if __name__ == "__main__":
    main()
