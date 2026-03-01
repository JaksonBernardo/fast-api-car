# Desenvolvimento

Este guia fornece informações essenciais para desenvolvedores que desejam contribuir com a CAR API ou estender suas funcionalidades.

---

## 🚀 Configurando Ambiente de Desenvolvimento

### 1. Clone o Repositório

```bash
git clone https://github.com/JaksonBernardo/fast-api-car.git
cd car_api
```

### 2. Crie Ambiente Virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```ini
DB_HOST=localhost
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_NAME=car_api_dev
DATABASE_URL=mysql+aiomysql://dev_user:dev_password@localhost:3306/car_api_dev
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

### 5. Crie Banco de Dados de Desenvolvimento

```sql
CREATE DATABASE car_api_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Execute Migrações

```bash
alembic upgrade head
```

---

## 🛠️ Ferramentas de Desenvolvimento

### Taskipy - Automação de Tarefas

O projeto utiliza Taskipy para automatizar tarefas comuns.

**Comandos disponíveis:**

```bash
# Executar linter
task lint

# Formatar código
task format

# Iniciar servidor de desenvolvimento
task run

# Iniciar documentação
task docs
```

### Ruff - Linter e Formatter

```bash
# Verificar erros
ruff check .

# Formatar código
ruff format .

# Corrigir automaticamente
ruff check --fix .
```

### Uvicorn - Servidor ASGI

```bash
# Modo desenvolvimento (auto-reload)
uvicorn car_api.app:app --reload

# Com host e porta específicos
uvicorn car_api.app:app --reload --host 0.0.0.0 --port 8000

# Modo produção
uvicorn car_api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📁 Estrutura de Desenvolvimento

### Adicionando Nova Funcionalidade

Siga a estrutura existente ao adicionar novos recursos:

```
1. Crie o Model (models/)
2. Crie o Schema (schemas/)
3. Crie o Repository (repositories/)
4. Crie o Service (services/)
5. Crie o Router (routers/)
6. Registre o Router (app.py)
7. Crie Migração (alembic)
8. Escreva Testes (tests/)
```

### Exemplo: Adicionando Entidade "Categoria"

**1. Model (car_api/models/categories.py):**
```python
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from car_api.models import Base

if TYPE_CHECKING:
    from car_api.models import Car


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), server_default=func.now()
    )

    cars: Mapped[List['Car']] = relationship('Car', back_populates='category')
```

**2. Schema (car_api/schemas/categories.py):**
```python
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CategorySchema(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

**3. Repository (car_api/repositories/categories.py):**
```python
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Category


class CategoryRepository:
    @staticmethod
    async def save(db: AsyncSession, category: Category) -> Category:
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Category | None:
        return await db.scalar(select(Category).where(Category.id == category_id))
```

**4. Service (car_api/services/categories.py):**
```python
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.models import Category
from car_api.repositories.categories import CategoryRepository


class CategoryService:
    @staticmethod
    async def create_category(
        db: AsyncSession, category: CategorySchema
    ) -> Category:
        exists = await CategoryRepository.get_by_name(db, category.name)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Categoria já existe',
            )

        new_category = Category(
            name=category.name, description=category.description
        )
        return await CategoryRepository.save(db, new_category)
```

**5. Router (car_api/routers/categories.py):**
```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from car_api.core.database import get_session
from car_api.schemas.categories import CategorySchema, CategoryPublicSchema
from car_api.services.categories import CategoryService

categories_router = APIRouter(prefix='/api/categories', tags=['Categories'])


@categories_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryPublicSchema,
)
async def create_category(
    category: CategorySchema,
    db: AsyncSession = Depends(get_session),
) -> CategoryPublicSchema:
    return await CategoryService.create_category(db, category)
```

**6. Registrar Router (car_api/app.py):**
```python
from fastapi import FastAPI
from car_api.routers import (
    auth_routers,
    brands_routers,
    car_routers,
    user_routers,
    categories_router,  # Novo
)

app = FastAPI()

app.include_router(auth_routers)
app.include_router(user_routers)
app.include_router(brands_routers)
app.include_router(car_routers)
app.include_router(categories_router)  # Novo
```

**7. Criar Migração:**
```bash
alembic revision --autogenerate -m "Add categories table"
alembic upgrade head
```

---

## 🐛 Debugging

### Logs da Aplicação

Adicione logging para debug:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.get('/example')
async def example():
    logger.debug('Debug message')
    logger.info('Info message')
    logger.warning('Warning message')
    logger.error('Error message')
```

### Debug com Print (Desenvolvimento)

```python
# Adicione prints estratégicos para debug rápido
async def create_car(db: AsyncSession, car_data: CarSchema):
    print(f'Dados recebidos: {car_data}')  # Debug
    
    brand_exists = await BrandRepository.verify_if_exists_brand_id(
        db, car_data.brand_id
    )
    print(f'Brand existe: {brand_exists}')  # Debug
```

### Usando Python Debugger

```python
import pdb


async def debug_function():
    pdb.set_trace()  # Breakpoint
    # ... código
```

Execute e interaja no terminal.

---

## 🧪 Executando Testes

### Instale Dependências de Teste

```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

### Execute Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=car_api --cov-report=html

# Teste específico
pytest tests/test_users.py -v

# Teste com filtro
pytest -k "test_create_user"
```

### Configuração pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
```

---

## 📝 Trabalhando com Banco de Dados

### Criar Nova Migração

```bash
# Gerar migração automática baseada nos models
alembic revision --autogenerate -m "Descrição da mudança"

# Gerar migração vazia
alembic revision -m "Descrição"
```

### Aplicar Migrações

```bash
# Aplicar todas
alembic upgrade head

# Aplicar até versão específica
alembic upgrade <revision_id>

# Reverter última
alembic downgrade -1

# Reverter para versão específica
alembic downgrade <revision_id>
```

### Verificar Status

```bash
# Ver migrações pendentes
alembic current

# Histórico de migrações
alembic history
```

---

## 🔍 Boas Práticas de Desenvolvimento

### 1. Siga os Padrões do Projeto

```python
# ✅ Use type hints
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    ...

# ✅ Use docstrings
def create_token(data: Dict) -> str:
    """Cria token JWT com expiração."""
    ...

# ✅ Trate erros adequadamente
try:
    result = await operation()
except HTTPException:
    raise
except Exception:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Erro interno',
    )
```

### 2. Valide Dados de Entrada

```python
# ✅ Use Pydantic schemas
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Password deve ter pelo menos 6 caracteres')
        return v
```

### 3. Use Transações Adequadamente

```python
# ✅ Commit apenas após todas as operações
async def create_user_with_profile(db: AsyncSession, user_data: UserSchema):
    try:
        user = await UserRepository.save(db, user)
        profile = await ProfileRepository.save(db, profile)
        await db.commit()  # Commit único
    except Exception:
        await db.rollback()  # Rollback em caso de erro
        raise
```

### 4. Evite N+1 Queries

```python
# ❌ Evite queries N+1
users = await db.execute(select(User))
for user in users:
    cars = await db.execute(select(Car).where(Car.owner_id == user.id))

# ✅ Use eager loading
users = await db.execute(
    select(User).options(selectinload(User.cars))
)
```

### 5. Documente Endpoints

```python
@user_routers.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Criar um usuário',
    description='Registra um novo usuário no sistema',
    tags=['Users'],
)
async def create_user(...):
    ...
```

---

## 🔧 Resolução de Problemas Comuns

### Erro: "No module named 'car_api'"

```bash
# Certifique-se de estar na raiz do projeto
cd /path/to/car_api

# Verifique se o ambiente virtual está ativado
# (venv) deve aparecer no terminal
```

### Erro: "Can't connect to MySQL server"

```bash
# Verifique se o MySQL está rodando
# Windows:
net start MySQL

# Linux:
sudo systemctl status mysql
```

### Erro: "Table doesn't exist"

```bash
# Execute as migrações
alembic upgrade head
```

### Erro: "Token expired" durante desenvolvimento

```ini
# Aumente o tempo de expiração no .env
JWT_EXPIRATION_MINUTES=120
```

---

## 📚 Recursos Adicionais

### Documentação Oficial

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [PyJWT](https://pyjwt.readthedocs.io/)

### Ferramentas Úteis

| Ferramenta | Finalidade |
|------------|------------|
| **Postman** | Testar endpoints |
| **DBeaver** | Gerenciar banco de dados |
| **Insomnia** | Cliente API alternativo |
| **Swagger UI** | Documentação interativa (`/docs`) |

---

## 📋 Checklist de Desenvolvimento

Antes de commitar:

- [ ] Código formatado (`task format`)
- [ ] Linter sem erros (`task lint`)
- [ ] Testes passando
- [ ] Type hints adicionados
- [ ] Docstrings em funções públicas
- [ ] Migrações criadas (se aplicável)
- [ ] Documentação atualizada (se aplicável)

---

## 📚 Próximos Passos

Com o ambiente configurado:

1. [Testes](testing.md) - Aprenda a escrever e executar testes
2. [Deploy](deployment.md) - Prepare para produção
3. [Contribuição](contributing.md) - Como contribuir com o projeto

---

**Dica:** Mantenha o servidor em modo `--reload` durante o desenvolvimento para reinício automático nas mudanças de código.
