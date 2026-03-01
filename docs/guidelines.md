# Guidelines e Padrões

Este documento estabelece as diretrizes e padrões de código adotados no projeto CAR API. Seguir estas convenções garante consistência, legibilidade e manutenibilidade do código.

---

## 📐 Padrões de Código

### Ferramentas de Linting e Formatação

O projeto utiliza **Ruff** como ferramenta principal para linting e formatação.

#### Configuração (pyproject.toml):

```toml
[tool.ruff]
line-length = 79
exclude = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "migrations",
    "alembic",
]

[tool.ruff.lint]
preview = true
select = ['I', 'F', 'E', 'W', 'PL', 'PT']
ignore = ['PLR2004', 'PLR0917', 'PLR0913']

[tool.ruff.format]
preview = true
quote-style = 'single'
```

#### Regras Ativas:

| Código | Descrição |
|--------|-----------|
| `I` | Ordenação de imports (isort) |
| `F` | Erros do Pyflakes |
| `E` | Erros de estilo PEP 8 |
| `W` | Warnings PEP 8 |
| `PL` | Pylint (lógica e boas práticas) |
| `PT` | Padrões de teste (pytest) |

#### Executando:

```bash
# Verificar erros
task lint

# Formatar código
task format
```

---

## 📝 Convenções de Nomenclatura

### Arquivos e Diretórios

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Módulos Python | `snake_case.py` | `user_service.py` |
| Pacotes | `snake_case` | `car_api` |
| Scripts | `snake_case.py` | `run_migrations.py` |

### Classes e Objetos

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Classes | `PascalCase` | `UserService`, `CarSchema` |
| Exceções | `PascalCase` com sufixo Error/Exception | `ValidationError` |

### Funções e Variáveis

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Funções/Métodos | `snake_case` | `get_user_by_id`, `create_car` |
| Variáveis | `snake_case` | `user_id`, `car_data` |
| Constantes | `UPPER_SNAKE_CASE` | `JWT_SECRET_KEY`, `MAX_LIMIT` |
| Privadas | `snake_case` com prefixo `_` | `_internal_method` |

### Banco de Dados

| Tipo | Convenção | Exemplo |
|------|-----------|---------|
| Tabelas | `snake_case` plural | `users`, `cars`, `brands` |
| Colunas | `snake_case` | `created_at`, `user_id` |
| Chaves Estrangeiras | `tabela_id` | `user_id`, `brand_id` |

---

## 🏗️ Estrutura de Código

### Imports

Os imports devem seguir esta ordem:

1. **Standard Library** (biblioteca padrão)
2. **Third-party** (dependências externas)
3. **Local imports** (módulos do projeto)

```python
# Standard Library
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from car_api.core.database import get_session
from car_api.models import User
from car_api.schemas.users import UserSchema
```

### Type Hints

Sempre utilize type hints em funções e métodos:

```python
# ✅ Correto
def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    ...

async def create_user(db: AsyncSession, user: UserSchema) -> UserPublicSchema:
    ...

# ❌ Evite
def get_user_by_id(db, user_id):
    ...
```

### Docstrings

Use docstrings para documentar funções públicas:

```python
def authenticate_user(email: str, password: str, db: AsyncSession) -> User | None:
    """
    Autentica um usuário verificando email e senha.

    Args:
        email: Email do usuário
        password: Senha em texto plano
        db: Sessão do banco de dados

    Returns:
        Objeto User se autenticado, None caso contrário

    Raises:
        HTTPException: Se houver erro na autenticação
    """
    ...
```

---

## 🎯 Padrões de Implementação

### Routers (Endpoints)

```python
from fastapi import APIRouter, Depends, status

user_routers = APIRouter(prefix='/api/users', tags=['Users'])


@user_routers.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Criar um usuário',
)
async def create_user(
    user: UserSchema, db: AsyncSession = Depends(get_session)
) -> UserPublicSchema:
    ...
```

### Services (Regras de Negócio)

```python
class UserService:
    @staticmethod
    async def create_user(
        db: AsyncSession, user: UserSchema
    ) -> UserPublicSchema:
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

        # Criar e salvar
        new_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
        )

        return await UserRepository.save(db, new_user)
```

### Repositories (Acesso a Dados)

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

### Schemas (Pydantic)

```python
from pydantic import BaseModel, EmailStr, field_validator


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def username_min_length(cls, v):
        if len(v) < 3:
            raise ValueError('Username deve ter pelo menos 3 caracteres')
        return v

    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password deve ter pelo menos 6 caracteres')
        return v
```

---

## 🔒 Tratamento de Erros

### HTTP Exceptions

Sempre retorne erros HTTP apropriados:

```python
from fastapi import HTTPException, status

# Recurso não encontrado
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Usuário não encontrado',
)

# Não autorizado
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Email ou senha incorretos',
    headers={'WWW-Authenticate': 'Bearer'},
)

# Erro interno
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Erro interno no servidor',
)
```

### Try/Except em Endpoints

```python
@user_routers.post('/')
async def create_user(user: UserSchema, db: AsyncSession):
    try:
        return await UserService.create_user(db, user)

    except HTTPException as http_ex:
        raise http_ex

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro interno no servidor',
        )
```

---

## 💾 Padrões de Banco de Dados

### Models (SQLAlchemy)

```python
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_api.models import Base

if TYPE_CHECKING:
    from car_api.models import Car


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), server_default=func.now()
    )

    cars: Mapped[List['Car']] = relationship('Car', back_populates='owner')
```

### Relacionamentos

```python
# ForeignKey padrão: tabela_id
owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

# Relationship com back_populates
owner: Mapped['User'] = relationship('User', back_populates='cars')
```

---

## 🧪 Padrões de Teste

### Estrutura de Testes

```python
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from car_api.app import app
    return TestClient(app)


def test_create_user(client):
    response = client.post('/api/users', json={
        'username': 'test',
        'email': 'test@example.com',
        'password': '123456',
    })
    assert response.status_code == 201
```

### Nomenclatura de Testes

```python
def test_create_user_with_valid_data(): ...
def test_create_user_with_invalid_email(): ...
def test_get_user_not_found_returns_404(): ...
def test_delete_user_without_permission_returns_403(): ...
```

---

## 📏 Limites e Thresholds

### Tamanho de Código

| Métrica | Limite | Ação |
|---------|--------|------|
| Linha de código | 79 caracteres | Quebrar linha |
| Funções | Máx. 50 linhas | Refatorar |
| Parâmetros | Máx. 5 | Usar objeto/dict |
| Complexidade ciclomática | Máx. 10 | Simplificar |

### Imports

- Máximo de 3 níveis de import aninhado
- Evitar imports circulares (usar `TYPE_CHECKING`)

---

## 🔄 Controle de Versão (Git)

### Mensagens de Commit

Siga o padrão **Conventional Commits**:

```
<tipo>(<escopo>): <descrição curta>

<descrição detalhada (opcional)>
```

#### Tipos:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação/código (sem lógica)
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Configuração/manutenção

#### Exemplos:
```bash
feat(users): adicionar endpoint de listagem de usuários

fix(cars): corrigir validação de placa no cadastro

docs: atualizar documentação de autenticação

refactor(auth): simplificar lógica de verificação de token
```

### Branches

```
main              # Produção
develop           # Desenvolvimento
feature/xxx       # Novas funcionalidades
fix/xxx           # Correções
hotfix/xxx        # Correções urgentes em produção
```

---

## 📋 Checklist de Code Review

Antes de submeter código:

- [ ] Código formatado com `task format`
- [ ] Linter sem erros `task lint`
- [ ] Type hints em todas as funções
- [ ] Docstrings em funções públicas
- [ ] Tratamento de erros adequado
- [ ] Testes para novas funcionalidades
- [ ] Mensagem de commit no padrão

---

## 📚 Referências

- [PEP 8 - Style Guide for Python](https://peps.python.org/pep-0008/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🎯 Resumo Rápido

```python
# ✅ Padrão CAR API

# Imports ordenados
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import User


# Type hints e docstrings
async def get_user(
    db: AsyncSession, user_id: int
) -> User | None:
    """Obtém usuário por ID."""
    ...


# Strings com aspas simples
message = 'Usuário criado com sucesso'


# Snake case para funções/variáveis
user_id = 1
created_at = datetime.now()


# Pascal case para classes
class UserService:
    ...


# Constants em uppercase
JWT_ALGORITHM = 'HS256'
MAX_LIMIT = 100
```

---

**Dica:** Configure seu editor para formatar automaticamente ao salvar e executar o linter em tempo real.
