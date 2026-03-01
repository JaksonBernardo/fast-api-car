# Instalação

Este guia fornece instruções passo a passo para instalar e configurar a CAR API em seu ambiente de desenvolvimento.

## 📥 Passo 1: Clonar o Repositório

Clone o repositório do projeto para sua máquina local:

```bash
git clone https://github.com/JaksonBernardo/fast-api-car.git
cd car_api
```

---

## 📦 Passo 2: Criar Ambiente Virtual

É altamente recomendado utilizar um ambiente virtual para isolar as dependências do projeto.

### Windows (PowerShell/CMD):
```bash
python -m venv venv
```

### Linux/macOS:
```bash
python3 -m venv venv
```

### Ativar o Ambiente Virtual

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

Após ativar, você verá `(venv)` no início da linha do terminal.

---

## 📋 Passo 3: Instalar Dependências

Com o ambiente virtual ativado, instale todas as dependências do projeto:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Dependências Principais Instaladas:

| Pacote | Versão | Finalidade |
|--------|--------|------------|
| fastapi | 0.128.0 | Framework web |
| sqlalchemy | 2.0.46 | ORM assíncrono |
| aiomysql | 0.3.2 | Driver MySQL async |
| pydantic | 2.12.5 | Validação de dados |
| pyjwt | 2.11.0 | Autenticação JWT |
| alembic | 1.18.3 | Migrações |
| argon2-cffi | 25.1.0 | Hash de senhas |
| uvicorn | 0.40.0 | Servidor ASGI |
| ruff | 0.15.4 | Linter/Formatter |
| mkdocs | 1.6.1 | Documentação |

---

## 🗄️ Passo 4: Configurar Banco de Dados

### Criar o Banco de Dados

Acesse o MySQL e crie o banco de dados:

```bash
mysql -u root -p
```

```sql
CREATE DATABASE car_api CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'car_api_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON car_api.* TO 'car_api_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Executar Migrações

Execute as migrações para criar as tabelas no banco de dados:

```bash
alembic upgrade head
```

Isso irá criar as tabelas:
- `users` - Usuários do sistema
- `brands` - Marcas de veículos
- `cars` - Veículos cadastrados

---

## ⚙️ Passo 5: Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

> **Nota:** Se não existir `.env.example`, crie o arquivo `.env` manualmente conforme descrito em [Configuração](configuration.md).

---

## 🧪 Passo 6: Verificar Instalação

### Testar Importação dos Módulos:
```bash
python -c "from car_api.app import app; print('Importação OK!')"
```

### Verificar se o servidor inicia:
```bash
uvicorn car_api.app:app --reload
```

Acesse `http://127.0.0.1:8000/docs` para visualizar a documentação interativa.

---

## 🚀 Comandos Úteis

O projeto utiliza **Taskipy** para gerenciar tarefas comuns. Os comandos disponíveis são:

### Iniciar o Servidor de Desenvolvimento:
```bash
task run
```

### Executar Linter:
```bash
task lint
```

### Formatar Código:
```bash
task format
```

### Iniciar Documentação:
```bash
task docs
```

### Executar sem Taskipy:
```bash
# Iniciar servidor
uvicorn car_api.app:app --reload --host 0.0.0.0 --port 8000

# Rodar linter
ruff check .

# Formatar código
ruff format .

# Documentação
mkdocs serve -a 127.0.0.1:8001
```

---

## 📁 Estrutura Após Instalação

Após completar a instalação, sua estrutura de diretórios deve estar assim:

```
car_api/
├── .env                    # Variáveis de ambiente (criado por você)
├── .git/
├── .ruff_cache/
├── car_api/
│   ├── __pycache__/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── app.py
├── docs/                   # Documentação
├── migrations/
│   ├── versions/
│   └── env.py
├── tests/
├── venv/                   # Ambiente virtual (criado por você)
├── requirements.txt
├── pyproject.toml
└── alembic.ini
```

---

## 🐛 Solução de Problemas

### Erro: "No module named 'car_api'"
Certifique-se de que o ambiente virtual está ativado e você está na raiz do projeto.

### Erro de Conexão com Banco de Dados
Verifique se:
- O MySQL está rodando
- As credenciais no `.env` estão corretas
- O banco de dados foi criado

### Erro: "Access denied for user"
Revise as permissões do usuário no MySQL:
```sql
GRANT ALL PRIVILEGES ON car_api.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

### Dependências não instalam
Atualize o pip e tente novamente:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

---

## ✅ Checklist de Instalação

- [ ] Repositório clonado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Banco de dados criado
- [ ] Migrações executadas
- [ ] Arquivo `.env` configurado
- [ ] Servidor inicia sem erros

---

## 📚 Próximos Passos

Com a instalação concluída:

1. [Configuração do Projeto](configuration.md) - Ajuste as variáveis de ambiente
2. [API Endpoints](api-endpoints.md) - Explore os endpoints disponíveis
3. [Desenvolvimento](development.md) - Comece a desenvolver

---

**Dica:** Mantenha o servidor em modo `--reload` durante o desenvolvimento para reinício automático nas mudanças de código.
