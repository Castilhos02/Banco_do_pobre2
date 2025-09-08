# 💸 Banco do Pobre

Sistema bancário simples e funcional desenvolvido em Python, utilizando os princípios da Programação Orientada a Objetos (POO). O projeto simula operações bancárias básicas como cadastro de clientes, criação de contas, depósitos, saques e geração de extratos, com persistência de dados em JSON.

---

## 🧠 Funcionalidades

- Cadastro de clientes com CPF, nome, data de nascimento e endereço
- Autenticação de cliente por CPF
- Criação de contas correntes vinculadas a clientes
- Depósitos com validação de valor positivo
- Saques com:
  - Limite de R$ 500 por operação
  - Máximo de 3 saques por dia
  - Verificação de saldo disponível
- Geração de extrato com histórico de transações
- Persistência de dados em arquivo `banco_data.json`
- Interface de menu interativo via terminal

---

## 🧱 Estrutura de Classes

- `Pessoa` / `PessoaFisica`: representa dados pessoais do cliente
- `Cliente`: associa uma pessoa às suas contas bancárias
- `Conta`: gerencia saldo, número da conta e histórico
- `Historico`: armazena transações realizadas
- `Transacao` (abstrata): base para `Deposito` e `Saque`
- `Banco`: orquestra clientes, contas e operações

---

## 🚀 Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/banco-pobre.git
   cd banco-pobre
