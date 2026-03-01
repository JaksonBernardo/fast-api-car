# Pré-requisitos

Antes de começar a trabalhar com a CAR API, certifique-se de ter os seguintes requisitos instalados e configurados em seu ambiente de desenvolvimento.

## 📋 Requisitos do Sistema

### Sistema Operacional
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ macOS (10.15 ou superior)

### Hardware Mínimo Recomendado
- **Processador:** Dual-core 2.0 GHz ou superior
- **Memória RAM:** 4 GB (8 GB recomendado)
- **Armazenamento:** 500 MB livres para o projeto e dependências

---

## 🔧 Software Obrigatório

### 1. Python 3.10 ou Superior

A CAR API foi desenvolvida com Python 3.10+. Versões inferiores podem não ser compatíveis.

#### Verificando a versão instalada:
```bash
python --version
# ou
python3 --version
```

#### Instalação:

**Windows:**
- Baixe o instalador em [python.org](https://www.python.org/downloads/)
- Marque a opção "Add Python to PATH" durante a instalação

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

---

### 2. Banco de Dados MySQL/MariaDB

A API utiliza MySQL ou MariaDB como banco de dados principal.

#### Versões Suportadas:
- MySQL 8.0+
- MariaDB 10.5+

#### Instalação:

**Windows:**
- Baixe o MySQL Installer em [dev.mysql.com](https://dev.mysql.com/downloads/installer/)

**Linux (Ubuntu/Debian):**
```bash
sudo apt install mysql-server
```

**macOS:**
```bash
brew install mysql
```

#### Verificando a instalação:
```bash
mysql --version
```

---

### 3. Git

Necessário para clonar o repositório e controle de versão.

#### Instalação:

**Windows:**
- Baixe em [git-scm.com](https://git-scm.com/download/win)

**Linux:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

#### Verificando a instalação:
```bash
git --version
```

---

## 📦 Conhecimentos Recomendados

Para aproveitar melhor este projeto, é recomendável ter familiaridade com:

| Conhecimento | Nível | Importância |
|--------------|-------|-------------|
| Python | Intermediário | Essencial |
| FastAPI | Básico | Importante |
| SQLAlchemy | Básico | Importante |
| REST APIs | Intermediário | Essencial |
| Git | Básico | Essencial |
| Banco de Dados SQL | Intermediário | Importante |
| Async/Await | Básico | Importante |

---

## 🛠️ Ferramentas Opcionais (Recomendadas)

### Editor de Código / IDE
- **VS Code** - Recomendado com extensões Python
- **PyCharm** - IDE completa para Python
- **Sublime Text** - Editor leve e rápido

### Extensões Úteis (VS Code)
- Python (Microsoft)
- Pylance
- Ruff (para linting)
- SQLite Viewer
- REST Client ou Thunder Client

### Cliente API
- **Postman** - Teste de endpoints
- **Insomnia** - Alternativa ao Postman
- **curl** - Linha de comando

### Gerenciamento de Ambiente
- **venv** - Já incluso no Python 3.3+
- **virtualenv** - Alternativa ao venv
- **poetry** - Gerenciamento moderno de dependências

---

## ✅ Checklist de Verificação

Antes de prosseguir para a instalação, execute os seguintes comandos para verificar seu ambiente:

```bash
# Verificar Python
python --version  # Deve ser 3.10 ou superior

# Verificar pip
pip --version

# Verificar Git
git --version

# Verificar MySQL
mysql --version
```

---

## 🐛 Solução de Problemas Comuns

### Python não é reconhecido
**Windows:** Adicione Python ao PATH manualmente ou reinstale marcando a opção correta.

**Linux/macOS:** Use `python3` em vez de `python`.

### Erro de permissão no pip
Use a flag `--user` ou crie um ambiente virtual:
```bash
pip install --user <pacote>
# ou
python -m venv venv
```

### MySQL não inicia
Verifique se o serviço está rodando:
```bash
# Linux
sudo systemctl status mysql

# Windows
net start MySQL
```

---

## 📚 Próximos Passos

Com todos os pré-requisitos instalados, você está pronto para:

1. [Instalar o projeto](installation.md) - Clone e configure as dependências
2. [Configurar o ambiente](configuration.md) - Ajuste as variáveis de ambiente

---

**Dica:** Mantenha todas as ferramentas atualizadas para garantir compatibilidade e segurança.
