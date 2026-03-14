# 🚗 Car API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.0-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-4A90E2?style=for-the-badge&logo=postgresql)](https://www.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-9.0.2-0A9EDC?style=for-the-badge&logo=pytest)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-✅-brightgreen?style=for-the-badge)](https://coverage.readthedocs.io/)

Uma **API RESTful moderna e escalável** para gerenciamento de veículos, construída com **FastAPI** e **arquitetura limpa**. Este projeto demonstra domínio de conceitos essenciais para desenvolvimento backend de alto nível, incluindo autenticação JWT, testes automatizados, migrations e boas práticas de código.

---

## ✨ Destaques do Projeto

- 🔐 **Autenticação JWT** com segurança de nível production (Argon2 hashing)
- 🏗️ **Arquitetura em Camadas** (Routers → Services → Repositories → Models)
- 🧪 **Testes Automatizados** com pytest e cobertura de código
- 📊 **Banco de Dados Assíncrono** com SQLAlchemy 2.0 e Alembic migrations
- 📝 **Validação de Dados** com Pydantic v2
- 🚀 **Pronto para Produção** com linting (Ruff), documentação e versionamento

---

## 🛠️ Stack Tecnológico

| Categoria | Tecnologias |
|-----------|-------------|
| **Framework** | FastAPI 0.128.0 |
| **Linguagem** | Python 3.12+ |
| **Banco de Dados** | SQLite (async) / MySQL compatível |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Autenticação** | JWT (PyJWT) + Argon2 |
| **Testes** | pytest + pytest-asyncio + pytest-cov |
| **Qualidade** | Ruff (linting + formatting) |
| **Documentação** | OpenAPI/Swagger automático |

---

## 📁 Estrutura do Projeto

```
car_api/
├── car_api/
│   ├── core/           # Configurações, database, segurança
│   ├── models/         # Modelos SQLAlchemy (User, Car, Brand)
│   ├── repositories/   # Camada de acesso a dados
│   ├── routers/        # Endpoints da API (auth, users, cars, brands)
│   ├── schemas/        # Schemas Pydantic para validação
│   ├── services/       # Regras de negócio
│   └── app.py          # Aplicação principal
├── tests/              # Testes automatizados
├── migrations/         # Migrations do Alembic
├── docs/               # Documentação MkDocs
└── pyproject.toml      # Configurações do projeto
```

---

## 🚀 Funcionalidades

### 🔐 Autenticação & Autorização
- Registro e login de usuários
- JWT tokens com expiração configurável
- Hash de senhas com **Argon2** (melhor prática de segurança)
- Proteção de rotas por autenticação
- Verificação de propriedade (usuário só gerencia seus próprios carros)

### 🚗 Gestão de Veículos
- CRUD completo de carros
- Filtros avançados (marca, combustível, transmissão, proprietário)
- Validação de dados com Pydantic
- Relacionamento com marcas e usuários

### 🏷️ Gestão de Marcas
- Cadastro e listagem de marcas de veículos

### 👥 Gestão de Usuários
- Perfil de usuário
- Permissões granulares

---

## 🔌 Endpoints da API

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/api/auth/token` | Gerar token de acesso | ❌ |
| `POST` | `/api/users/` | Criar novo usuário | ❌ |
| `GET` | `/api/users/{id}` | Obter usuário | ✅ |
| `PUT` | `/api/users/{id}` | Atualizar usuário | ✅ |
| `DELETE` | `/api/users/{id}` | Deletar usuário | ✅ |
| `POST` | `/api/cars/` | Criar carro | ✅ |
| `GET` | `/api/cars/` | Listar carros (com filtros) | ❌ |
| `GET` | `/api/cars/{id}` | Obter carro específico | ✅ |
| `PUT` | `/api/cars/{id}` | Atualizar carro | ✅ |
| `DELETE` | `/api/cars/{id}` | Deletar carro | ✅ |
| `POST` | `/api/brands/` | Criar marca | ✅ |
| `GET` | `/api/brands/` | Listar marcas | ❌ |

---

## 🏃‍♂️ Como Rodar o Projeto

### Pré-requisitos
```bash
Python 3.12+
```


### Configuração

Crie um arquivo `.env` na raiz do projeto (baseado em `.env.example`):

```env
SECRET_KEY=sua_chave_secreta_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite+aiosqlite:///./db.sqlite
```

> ⚠️ **Importante:** A `SECRET_KEY` deve ser uma string aleatória e segura em ambiente de produção.

### Instalação
```bash
# Clonar repositório
git clone https://github.com/JaksonBernardo/fast-api-car.git

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Rodar migrations
alembic upgrade head

# Iniciar servidor de desenvolvimento
task run
```

### Com Taskipy (recomendado)
```bash
# Ver todos os comandos disponíveis
task --list

# Rodar testes com coverage
task test_run

# Lint e formatação
task lint
task format

# Rodar documentação
task docs

# Iniciar servidor
task run
```

---

## 🧪 Testes

O projeto possui **suite de testes completa** cobrindo:
- Autenticação e autorização
- CRUD de usuários, carros e marcas
- Validações de negócio
- Verificação de permissões

```bash
# Rodar testes com coverage
pytest -s -x --cov=car_api -vv

# Gerar relatório HTML de coverage
coverage html
# Abra: htmlcov/index.html
```

---

## 📊 Qualidade de Código

Este projeto segue **boas práticas de desenvolvimento**:

- ✅ **Ruff** para linting e formatação (substituto moderno do Flake8 + Black)
- ✅ **Type hints** em todo o código
- ✅ **Docstrings** em funções críticas
- ✅ **Separação de responsabilidades** (SRP)
- ✅ **Injeção de dependências** do FastAPI
- ✅ **Migrations versionadas** com Alembic

---

## 🔐 Segurança

- Senhas hashadas com **Argon2** (vencedor do Password Hashing Competition)
- JWT tokens com expiração configurável
- Validação de propriedade em operações sensíveis
- HTTPS ready (configuração de produção)
- SQL injection prevenido (SQLAlchemy ORM)

---

## 📖 Documentação

A API possui **documentação OpenAPI automática**. Após rodar o servidor:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 🎯 Diferenciais

Este projeto demonstra:

1. **Domínio de FastAPI** - Framework moderno e performático
2. **Arquitetura escalável** - Separação clara de responsabilidades
3. **Cultura de testes** - Testes automatizados e coverage
4. **Segurança** - Autenticação JWT e hash de senhas adequado
5. **Qualidade de código** - Linting, type hints e padrões
6. **DevOps básico** - Migrations, ambiente reproduzível
7. **Documentação** - OpenAPI automático + MkDocs

---

## 📄 Licença

MIT License - Projeto desenvolvido para fins educacionais e portfólio.

---

## 👤 Autor

Desenvolvido como parte do portfólio técnico para demonstrar competências em **desenvolvimento backend Python** com foco em **APIs RESTful modernas**.

---

<div align="center">

**Interessado em ver mais?** Explore o código, rode os testes e veja a qualidade em ação! 🚀

</div>
