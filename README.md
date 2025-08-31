# Deriv Bot - Modern Trading Bot

Um bot de trading moderno para a plataforma Deriv com interface web moderna construída em React + TypeScript + Vite.

![Deriv Bot](https://deriv.com/static/logo-deriv-512x512-5e5d5970.png)

## 🚀 Arquitetura Moderna

Este projeto foi refatorado para usar uma arquitetura moderna:

- **Backend**: Python + Flask (API REST)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Estrutura**: Monorepo com separação clara entre frontend e backend

## ✨ Funcionalidades

- **Integração com Deriv API**: Conecta à plataforma Deriv usando sua API oficial
- **Notificações Telegram**: Recebe notificações de status da conta e atividades de trading via Telegram
- **Dashboard Web Moderno**: Interface moderna para monitorar saldo e dados de mercado
- **Streaming de Ticks**: Inscreva-se em atualizações de preços em tempo real para vários mercados
- **Múltiplas Estratégias de Trading**: Suporte para diferentes estratégias (Básica, Martingale, Soros)
- **Tratamento de Erros Robusto**: Tratamento robusto de erros para disponibilidade de mercado e problemas de conexão

## 🏗️ Estrutura do Projeto

```
deriv-bot/
├── 📁 backend/                 # Backend Python/Flask
│   ├── 📁 app/                 # Aplicação modular
│   │   ├── 📁 api/            # Endpoints da API
│   │   ├── 📁 services/       # Serviços (Deriv, Telegram)
│   │   └── 📁 utils/          # Utilitários e decoradores
│   ├── 📁 scripts/            # Scripts de gerenciamento
│   ├── 📁 utils/              # Utilitários legados
│   ├── 📁 strategies/         # Estratégias de trading
│   ├── 📁 tests/              # Testes automatizados
│   ├── config.py              # Configuração por ambiente
│   ├── run.py                 # Ponto de entrada refatorado
│   └── requirements.txt       # Dependências Python
├── 📁 frontend/               # Frontend React/TypeScript
│   ├── 📁 src/               # Código fonte
│   │   ├── 📁 components/    # Componentes React
│   │   ├── 📁 types/         # Tipos TypeScript
│   │   └── 📁 utils/         # Utilitários frontend
│   ├── package.json          # Dependências Node.js
│   └── vite.config.ts        # Configuração Vite
├── 📁 scripts/               # Scripts de gerenciamento
│   ├── install.sh            # Instalação completa
│   ├── start.sh              # Iniciar serviços
│   ├── stop.sh               # Parar serviços
│   └── status.sh             # Verificar status
├── package.json              # Dependências root
└── README.md                 # Documentação
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.12+**: Linguagem principal
- **Flask**: Framework web para API REST
- **Flask-Limiter**: Rate limiting e proteção
- **Deriv API**: Cliente Python oficial para a plataforma Deriv
- **Aiogram**: Framework para integração com Telegram Bot
- **Asyncio**: Para operações assíncronas
- **WebSockets**: Para streaming de dados em tempo real
- **ReactiveX**: Para padrões de programação reativa

### Frontend
- **React 18**: Biblioteca JavaScript para interfaces de usuário
- **TypeScript**: Superset tipado do JavaScript
- **Vite**: Build tool e dev server moderno
- **Bootstrap 5**: Framework CSS para UI moderna
- **React-Bootstrap**: Componentes Bootstrap para React
- **Axios**: Cliente HTTP para requisições à API
- **Lucide React**: Biblioteca de ícones

## 📦 Instalação

### Pré-requisitos

- Python 3.12 ou superior
- Node.js 18+ e npm
- Git
- Conta Deriv com acesso à API
- Token do Telegram Bot

### Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/leonardolimanas/deriv-bot.git
   cd deriv-bot
   ```

2. Instale as dependências do projeto:
   ```bash
   ./scripts/install.sh
   ```
   
   Este script irá:
   - ✅ Verificar pré-requisitos (Python 3.8+, Node.js 16+)
   - ✅ Criar ambiente virtual Python
   - ✅ Instalar todas as dependências
   - ✅ Criar arquivo .env a partir do template

3. Configure as variáveis de ambiente (veja seção Configuração)

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto ou configure as seguintes variáveis de ambiente:

```env
DERIV_API_TOKEN=seu_token_api_deriv
DERIV_APP_ID=seu_app_id_deriv
DERIV_API_TOKEN_REAL=seu_token_conta_real_deriv
TELEGRAM_BOT_TOKEN=seu_token_bot_telegram
TELEGRAM_CHAT_ID=seu_chat_id_telegram
```

Alternativamente, você pode modificar os valores padrão em `backend/utils/config.py`.

## 🚀 Uso

### 🎯 Início Rápido (Recomendado)

Para iniciar o projeto com um comando simples:

```bash
./scripts/start.sh
```

Este script irá:
- ✅ Verificar e instalar dependências automaticamente
- ✅ Ativar o ambiente virtual Python
- ✅ Parar processos existentes nas portas 5001, 5173, 5174
- ✅ Iniciar backend e frontend simultaneamente
- ✅ Exibir URLs de acesso

### 🛑 Parando o Projeto

Para parar todos os serviços:

```bash
./scripts/stop.sh
```

### 📊 Verificando Status

Para verificar o status dos serviços:

```bash
./scripts/status.sh
```

Este script irá:
- ✅ Verificar se as dependências estão instaladas
- ✅ Verificar se os serviços estão rodando
- ✅ Testar a conectividade dos serviços
- ✅ Exibir URLs de acesso
- ✅ Mostrar resumo do status

### 📋 Scripts Disponíveis

| Script | Comando | Descrição |
|--------|---------|-----------|
| **Instalação** | `./scripts/install.sh` | Instala todas as dependências e configura o projeto |
| **Iniciar** | `./scripts/start.sh` | Inicia backend e frontend simultaneamente |
| **Parar** | `./scripts/stop.sh` | Para todos os serviços do projeto |
| **Status** | `./scripts/status.sh` | Verifica o status dos serviços |

### 📋 Comandos Manuais

#### Executando o Projeto Completo

Para executar tanto o backend quanto o frontend simultaneamente:

```bash
npm run dev
```

Isso irá:
1. Iniciar o servidor API Python na porta 5001
2. Iniciar o servidor de desenvolvimento Vite na porta 5173
3. Abrir automaticamente o dashboard no navegador

#### Executando Separadamente

**Backend apenas:**
```bash
npm run dev:backend
```

**Frontend apenas:**
```bash
npm run dev:frontend
```

### Dashboard Web

O dashboard moderno oferece:

- Exibição de saldo da conta em tempo real
- Seleção de mercado com dropdown organizado
- Controles de streaming de ticks
- Visualização de dados de preços em tempo real
- Interface responsiva e moderna

Para acessar o dashboard, abra um navegador e navegue para:
```
http://localhost:5173
```

### Streaming de Ticks de Mercado

1. Selecione um mercado do dropdown
2. Clique em "Inscrever em Ticks"
3. Visualize os dados de ticks em tempo real na tabela
4. Clique em "Cancelar Inscrição" para parar o stream

**Nota**: Alguns mercados podem estar indisponíveis durante certas horas ou dias. O dashboard exibirá mensagens de status apropriadas.

## 🔧 Melhorias do Backend

### 🏗️ Arquitetura Modular
- **Application Factory**: Padrão factory para criação da aplicação
- **Blueprints**: API organizada em blueprints modulares
- **Serviços Separados**: Deriv e Telegram como serviços independentes
- **Configuração Robusta**: Sistema de configuração por ambiente (Dev/Prod/Test)

### 🛡️ Segurança e Validação
- **Rate Limiting**: Proteção contra sobrecarga da API
- **Validação de Entrada**: Validadores para símbolos e dados
- **Sanitização**: Limpeza automática de entrada do usuário
- **Configuração Segura**: Tokens via variáveis de ambiente

### 📊 Logging e Monitoramento
- **Logging Estruturado**: Logs com rotação de arquivos
- **Tratamento de Erros**: Decoradores para tratamento centralizado
- **Health Checks**: Endpoints de monitoramento detalhados
- **Métricas**: Contadores e timestamps em todas as operações

### ⚡ Performance
- **Cache Simples**: Cache em memória para respostas frequentes
- **Timeout Management**: Timeouts para operações assíncronas
- **Connection Pooling**: Reutilização de conexões
- **Async Operations**: Operações assíncronas otimizadas

### 🎯 Funcionalidades Adicionais
- **Versionamento**: API versionada (v1)
- **Documentação**: Docstrings em todos os métodos
- **Testes Preparados**: Estrutura para testes automatizados
- **Configuração por Ambiente**: Dev, Prod, Test com validação

## 📁 Estrutura do Projeto

## 🎯 Estratégias de Trading

O projeto inclui suporte para múltiplas estratégias de trading:

- **Estratégia Básica**: Regras simples de entrada e saída
- **Estratégia Martingale**: Aumenta a aposta após cada perda
- **Estratégia Soros**: Baseada nos princípios de trading de George Soros

**Nota**: As implementações das estratégias estão atualmente em desenvolvimento.

## 🔧 Scripts Disponíveis

- `npm run dev`: Executa backend e frontend simultaneamente
- `npm run dev:backend`: Executa apenas o backend
- `npm run dev:frontend`: Executa apenas o frontend
- `npm run build`: Constrói o frontend para produção
- `npm run install:all`: Instala todas as dependências
- `npm start`: Executa apenas o backend (produção)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para enviar um Pull Request.

1. Faça um fork do repositório
2. Crie sua branch de feature (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'feat: add some amazing feature'`)
4. Push para a branch (`git push origin feature/amazing-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## ⚠️ Aviso Legal

Trading envolve risco. Este software é apenas para fins educacionais e de pesquisa. Use por sua conta e risco.

## 🆕 Novidades na Versão Modernizada

### Frontend
- **Interface Moderna**: Dashboard completamente redesenhado com React + TypeScript
- **Performance Melhorada**: Vite para desenvolvimento rápido e builds otimizados
- **Type Safety**: TypeScript para maior segurança de tipos
- **Design Responsivo**: Bootstrap 5 para interface moderna e responsiva
- **Arquitetura Limpa**: Separação clara entre frontend e backend
- **Developer Experience**: Hot reload, debugging melhorado, e ferramentas modernas

### Backend
- **Arquitetura Modular**: Application Factory, Blueprints e Serviços separados
- **Segurança Aprimorada**: Rate limiting, validação de entrada e sanitização
- **Logging Estruturado**: Sistema de logs com rotação e monitoramento
- **Performance Otimizada**: Cache, timeouts e operações assíncronas
- **Configuração Robusta**: Sistema de configuração por ambiente
- **Scripts de Gerenciamento**: Instalação, execução e monitoramento automatizados