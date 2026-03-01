# Estrutura do Projeto

Este documento descreve a organização de diretórios e arquivos da CAR API, explicando a responsabilidade de cada componente.

---

## 🌳 Visão Geral da Estrutura

```
car_api/
├── .git/                          # Repositório Git
├── .ruff_cache/                   # Cache do linter Ruff
├── .venv/                         # Ambiente virtual Python
├── car_api/                       # Pacote principal da aplicação
│   ├── __init__.py                # Inicializador do pacote
│   ├── app.py                     # Aplicação FastAPI principal
│   ├── core/                      # Configurações centrais
│   │   ├── __init__.py
│   │   ├── database.py            # Configuração do banco de dados
│   │   ├── security.py            # Funções de segurança e autenticação
│   │   └── settings.py            # Configurações e variáveis de ambiente
│   ├── models/                    # Modelos SQLAlchemy (ORM)
│   │   ├── __init__.py
│   │   ├── base.py                # Classe base para modelos
│   │   ├── users.py               # Modelo User
│   │   └── cars.py                # Modelos Car e Brand
│   ├── repositories/              # Camada de acesso a dados
│   │   ├── __init__.py
│   │   ├── users.py               # Repository de usuários
│   │   ├── cars.py                # Repository de carros
│   │   └── brands.py              # Repository de marcas
│   ├── routers/                   # Endpoints da API
│   │   ├── __init__.py
│   │   ├── auth.py                # Rotas de autenticação
│   │   ├── users.py               # Rotas de usuários
│   │   ├── cars.py                # Rotas de carros
│   │   └── brands.py              # Rotas de marcas
│   ├── schemas/                   # Schemas Pydantic (validação)
│   │   ├── __init__.py
│   │   ├── auth.py                # Schemas de autenticação
│   │   ├── users.py               # Schemas de usuários
│   │   ├── cars.py                # Schemas de carros
│   │   └── brands.py              # Schemas de marcas
│   └── services/                  # Regras de negócio
│       ├── __init__.py
│       ├── users.py               # Service de usuários
│       ├── cars.py                # Service de carros
│       └── brands.py              # Service de marcas
├── docs/                          # Documentação do projeto
│   ├── index.md                   # Home da documentação
│   ├── overview.md
│   ├── prerequisites.md
│   ├── installation.md
│   ├── configuration.md
│   ├── guidelines.md
│   ├── structure.md
│   ├── api-endpoints.md
│   ├── system-modeling.md
│   ├── authentication.md
│   ├── development.md
│   ├── testing.md
│   ├── deployment.md
│   ├── contributing.md
│   └── release-notes.md
├── migrations/                    # Migrações do Alembic
│   ├── versions/                  # Scripts de migração
│   ├── env.py                     # Ambiente de migração
│   ├── README                     # Documentação do Alembic
│   └── script.py.mako             # Template para migrações
├── tests/                         # Testes automatizados
│   ├── __init__.py
│   └── ...                        # Arquivos de teste
├── .env                           # Variáveis de ambiente (não versionado)
├── .gitignore                     # Arquivos ignorados pelo Git
├── alembic.ini                    # Configuração do Alembic
├── mkdocs.yml                     # Configuração da documentação
├── pyproject.toml                 # Configuração do projeto (Ruff, Taskipy)
├── README.md                      # README principal
└── requirements.txt               # Dependências do projeto
```

---

## 📁 Descrição dos Diretórios

### `/car_api` - Pacote Principal

Contém todo o código fonte da aplicação.

| Arquivo/Diretório | Descrição |
|-------------------|-----------|
| `app.py` | Ponto de entrada da aplicação FastAPI |
| `core/` | Configurações essenciais e utilitários |
| `models/` | Definições dos modelos de banco de dados |
| `repositories/` | Camada de persistência de dados |
| `routers/` | Definição dos endpoints HTTP |
| `schemas/` | Validação e serialização de dados |
| `services/` | Regras de negócio da aplicação |

---

### `/car_api/core` - Núcleo da Aplicação

Configurações centrais e utilitários compartilhados.

| Arquivo | Descrição |
|---------|-----------|
| `settings.py` | Carrega e valida variáveis de ambiente usando Pydantic Settings |
| `database.py` | Configura engine assíncrona e sessão do SQLAlchemy |
| `security.py` | Funções de autenticação, JWT, hash de senha e permissões |

**Exemplo - settings.py:**
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_NAME: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int
```

---

### `/car_api/models` - Modelos de Dados

Define a estrutura das tabelas do banco de dados usando SQLAlchemy ORM.

| Arquivo | Classes | Descrição |
|---------|---------|-----------|
| `base.py` | `Base` | Classe base declarativa |
| `users.py` | `User` | Tabela de usuários |
| `cars.py` | `Car`, `Brand`, `FuelType`, `TransmissionType` | Tabela de carros e marcas |

**Exemplo - users.py:**
```python
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now())

    cars: Mapped[List['Car']] = relationship('Car', back_populates='owner')
```

---

### `/car_api/repositories` - Repositórios

Camada de acesso a dados (Data Access Object - DAO).

| Arquivo | Classe | Responsabilidade |
|---------|--------|------------------|
| `users.py` | `UserRepository` | Operações CRUD de usuários |
| `cars.py` | `CarRepository` | Operações CRUD de carros |
| `brands.py` | `BrandRepository` | Operações CRUD de marcas |

**Exemplo - UserRepository:**
```python
class UserRepository:
    @staticmethod
    async def save(db: AsyncSession, new_user: User) -> User:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        user = await db.scalar(select(User).where(User.id == user_id))
        return user
```

---

### `/car_api/routers` - Rotas da API

Define os endpoints HTTP e seus handlers.

| Arquivo | Prefixo | Tags | Descrição |
|---------|---------|------|-----------|
| `auth.py` | `/api/auth` | Auth | Login e refresh de token |
| `users.py` | `/api/users` | Users | CRUD de usuários |
| `cars.py` | `/api/cars` | Cars | CRUD de carros |
| `brands.py` | `/api/brands` | Brands | CRUD de marcas |

**Exemplo - Estrutura de Router:**
```python
user_routers = APIRouter(prefix='/api/users', tags=['Users'])


@user_routers.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Criar um usuário',
)
async def create_user(
    user: UserSchema, db: AsyncSession = Depends(get_session)
) -> UserPublicSchema:
    return await UserService.create_user(db, user)
```

---

### `/car_api/schemas` - Schemas Pydantic

Define a estrutura de validação e serialização de dados.

| Arquivo | Schemas | Descrição |
|---------|---------|-----------|
| `auth.py` | `Token`, `LoginRequest` | Autenticação |
| `users.py` | `UserSchema`, `UserUpdateSchema`, `UserPublicSchema`, `UserListPublicSchema` | Usuários |
| `cars.py` | `CarSchema`, `CarUpdateSchema`, `CarPublicSchema`, `CarListPublicSchema` | Carros |
| `brands.py` | `BrandSchema`, `BrandUpdateSchema`, `BrandPublicSchema`, `BrandListPublicSchema` | Marcas |

**Tipos de Schema:**
- `*Schema` - Dados de entrada (criação/atualização)
- `*UpdateSchema` - Dados de atualização (campos opcionais)
- `*PublicSchema` - Dados de saída (resposta da API)
- `*ListPublicSchema` - Listas paginadas

---

### `/car_api/services` - Serviços

Contém as regras de negócio da aplicação.

| Arquivo | Classe | Responsabilidade |
|---------|--------|------------------|
| `users.py` | `UserService` | Lógica de negócio de usuários |
| `cars.py` | `CarServices` | Lógica de negócio de carros |
| `brands.py` | `BrandService` | Lógica de negócio de marcas |

**Exemplo - UserService:**
```python
class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserSchema) -> UserPublicSchema:
        # Verificar duplicidade
        username_exists = await UserRepository.verify_if_exists_username(
            db, user.username
        )

        if username_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Nome ou email já está em uso',
            )

        # Hash da senha
        hashed_password = get_password_hash(user.password)

        # Criar usuário
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
        )

        return await UserRepository.save(db, new_user)
```

---

### `/migrations` - Migrações

Scripts de versionamento de banco de dados (Alembic).

| Arquivo/Diretório | Descrição |
|-------------------|-----------|
| `versions/` | Scripts de migração gerados |
| `env.py` | Configuração do ambiente de migração |
| `script.py.mako` | Template para novas migrações |

**Comandos úteis:**
```bash
# Criar nova migração
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

---

### `/docs` - Documentação

Documentação do projeto em Markdown para MkDocs.

| Arquivo | Descrição |
|---------|-----------|
| `index.md` | Página inicial da documentação |
| `overview.md` | Visão geral do projeto |
| `prerequisites.md` | Pré-requisitos |
| `installation.md` | Instalação |
| `configuration.md` | Configuração |
| `guidelines.md` | Guidelines e padrões |
| `structure.md` | Estrutura do projeto |
| `api-endpoints.md` | Documentação da API |
| `system-modeling.md` | Modelagem do sistema |
| `authentication.md` | Autenticação e segurança |
| `development.md` | Desenvolvimento |
| `testing.md` | Testes |
| `deployment.md` | Deploy |
| `contributing.md` | Contribuição |
| `release-notes.md` | Release notes |

---

### `/tests` - Testes

Testes automatizados da aplicação.

```
tests/
├── __init__.py
├── conftest.py              # Fixtures do pytest
├── test_auth.py             # Testes de autenticação
├── test_users.py            # Testes de usuários
├── test_cars.py             # Testes de carros
└── test_brands.py           # Testes de marcas
```

---

## 📄 Arquivos de Configuração

### `pyproject.toml`

Configurações do projeto, incluindo Ruff e Taskipy.

```toml
[tool.ruff]
line-length = 79

[tool.ruff.lint]
select = ['I', 'F', 'E', 'W', 'PL', 'PT']

[tool.taskipy.tasks]
lint = 'ruff check'
format = 'ruff format'
docs = 'mkdocs serve -a 127.0.0.1:8001'
run = 'uvicorn car_api.app:app --reload'
```

### `alembic.ini`

Configuração do Alembic para migrações.

```ini
[alembic]
script_location = migrations
sqlalchemy.url = mysql+aiomysql://user:pass@localhost/dbname
```

### `mkdocs.yml`

Configuração da documentação MkDocs.

```yaml
site_name: CAR API
theme:
  name: material
  language: pt-BR
nav:
  - Início: index.md
  - Guia: ...
```

### `.gitignore`

Arquivos e diretórios ignorados pelo Git.

```
# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Ambiente
.env

# IDE
.vscode/
.idea/

# Cache
.ruff_cache/
.pytest_cache/
```

---

## 🔄 Fluxo de Dados

```
┌──────────────────────────────────────────────────────────────────┐
│                           REQUEST                                │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Routers (car_api/routers/)                                      │
│  - Recebe requisição HTTP                                        │
│  - Valida schema de entrada (Pydantic)                           │
│  - Chama Service                                                 │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Services (car_api/services/)                                    │
│  - Aplica regras de negócio                                      │
│  - Validações adicionais                                         │
│  - Chama Repository                                              │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Repositories (car_api/repositories/)                            │
│  - Executa queries SQL                                           │
│  - Retorna modelos SQLAlchemy                                    │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  Database (MySQL)                                                │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                           RESPONSE                               │
│  - Service retorna para Router                                   │
│  - Router serializa com Schema                                   │
│  - Resposta JSON para cliente                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Dependências entre Módulos

```
routers/
    ├── depende de → services/
    ├── depende de → schemas/
    ├── depende de → core/database.py
    └── depende de → core/security.py

services/
    ├── depende de → repositories/
    ├── depende de → schemas/
    ├── depende de → models/
    └── depende de → core/security.py

repositories/
    ├── depende de → models/
    └── depende de → schemas/

models/
    └── depende de → core/database.py
```

---

## 🎯 Resumo das Responsabilidades

| Camada | Responsabilidade | Exemplo |
|--------|------------------|---------|
| **Routers** | Receber HTTP, validar schemas, retornar respostas | `@user_routers.post('/')` |
| **Services** | Regras de negócio, validações complexas | `UserService.create_user()` |
| **Repositories** | Acesso a dados, queries SQL | `UserRepository.save()` |
| **Models** | Estrutura das tabelas | `class User(Base)` |
| **Schemas** | Validação e serialização | `class UserSchema(BaseModel)` |
| **Core** | Configurações globais | `Settings`, `get_session`, `JWT` |

---

## 📚 Próximos Passos

Compreendida a estrutura:

1. [API Endpoints](api-endpoints.md) - Explore os endpoints disponíveis
2. [Modelagem do Sistema](system-modeling.md) - Entenda os modelos de dados
3. [Desenvolvimento](development.md) - Comece a contribuir

---

**Dica:** Use a estrutura como guia ao adicionar novas funcionalidades. Siga o padrão existente para manter a consistência.
