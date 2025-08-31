# 📁 Scripts de Gerenciamento

Este diretório contém scripts de automação para gerenciar o projeto Deriv Bot.

## 🚀 Scripts Disponíveis

### `install.sh` - Instalação Completa
**Descrição**: Instala todas as dependências e configura o projeto do zero.

**Funcionalidades**:
- ✅ Verifica pré-requisitos (Python 3.8+, Node.js 16+)
- ✅ Cria ambiente virtual Python
- ✅ Instala dependências Python (backend)
- ✅ Instala dependências Node.js (frontend)
- ✅ Instala dependências root (concurrently)
- ✅ Cria arquivo .env a partir do template

**Uso**:
```bash
./scripts/install.sh
```

### `start.sh` - Iniciar Serviços
**Descrição**: Inicia backend e frontend simultaneamente.

**Funcionalidades**:
- ✅ Verifica e instala dependências automaticamente
- ✅ Ativa o ambiente virtual Python
- ✅ Para processos existentes nas portas 5001, 5173, 5174
- ✅ Inicia backend e frontend simultaneamente
- ✅ Exibe URLs de acesso

**Uso**:
```bash
./scripts/start.sh
```

### `stop.sh` - Parar Serviços
**Descrição**: Para todos os serviços do projeto.

**Funcionalidades**:
- ✅ Para processos nas portas 5001, 5173, 5174
- ✅ Mata processos Python, Vite e Node.js relacionados
- ✅ Limpa processos em background

**Uso**:
```bash
./scripts/stop.sh
```

### `status.sh` - Verificar Status
**Descrição**: Verifica o status dos serviços e dependências.

**Funcionalidades**:
- ✅ Verifica se as dependências estão instaladas
- ✅ Verifica se os serviços estão rodando
- ✅ Testa a conectividade dos serviços
- ✅ Exibe URLs de acesso
- ✅ Mostra resumo do status

**Uso**:
```bash
./scripts/status.sh
```

## 🔧 Como Usar

### Primeira Instalação
```bash
# 1. Clone o repositório
git clone https://github.com/leonardolimanas/deriv-bot.git
cd deriv-bot

# 2. Instale tudo
./scripts/install.sh

# 3. Configure o .env (se necessário)
# 4. Inicie os serviços
./scripts/start.sh
```

### Uso Diário
```bash
# Iniciar
./scripts/start.sh

# Verificar status
./scripts/status.sh

# Parar
./scripts/stop.sh
```

## 📋 Requisitos

- **Sistema**: macOS, Linux ou WSL
- **Shell**: Bash
- **Permissões**: Scripts devem ser executáveis (`chmod +x scripts/*.sh`)

## 🛠️ Troubleshooting

### Scripts não executáveis
```bash
chmod +x scripts/*.sh
```

### Portas em uso
```bash
# Verificar processos nas portas
lsof -i :5001
lsof -i :5173
lsof -i :5174

# Matar processos manualmente
kill -9 <PID>
```

### Dependências faltando
```bash
# Reinstalar tudo
./scripts/install.sh
```

## 📊 Logs

Os scripts geram logs coloridos para facilitar o diagnóstico:

- 🟢 **SUCCESS**: Operação realizada com sucesso
- 🔴 **ERROR**: Erro que impede a operação
- 🟡 **WARNING**: Aviso que não impede a operação
- 🔵 **INFO**: Informação geral

## 🔄 Integração com npm

Os scripts são integrados com os comandos npm do projeto:

```bash
# Equivalente a ./scripts/install.sh
npm run install:all

# Equivalente a ./scripts/start.sh
npm run dev
```
