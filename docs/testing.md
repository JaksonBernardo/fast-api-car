# Testes

Este documento descreve a estratégia de testes da CAR API, incluindo tipos de testes, ferramentas, exemplos e boas práticas.

---

## 🧪 Visão Geral

A CAR API utiliza **pytest** como framework de testes, combinado com **pytest-asyncio** para testes assíncronos e **httpx** para testes de API.

### Tipos de Testes

| Tipo | Descrição | Cobertura |
|------|-----------|-----------|
| **Unitários** | Testam unidades isoladas (funções, métodos) | Services, Repositories |
| **Integração** | Testam integração entre componentes | Routers + Services |
| **End-to-End (E2E)** | Testam fluxos completos | API completa |

---

## 📦 Configuração

### Instalação de Dependências

```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

### Estrutura de Diretórios de Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── test_auth.py             # Testes de autenticação
├── test_users.py            # Testes de usuários
├── test_cars.py             # Testes de carros
├── test_brands.py           # Testes de marcas
└── ...
```

### Configuração pytest.ini

Crie um arquivo `pytest.ini` na raiz:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short
```

### Fixtures (conftest.py)

```python
# tests/conftest.py

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from car_api.app import app
from car_api.core.database import get_session
from car_api.models.base import Base


# URL do banco de dados de teste
TEST_DATABASE_URL = 'mysql+aiomysql://test_user:test_pass@localhost:3306/car_api_test'


@pytest.fixture
async def db_session():
    """Cria sessão de banco de dados para testes."""
    engine = create_async_engine(TEST_DATABASE_URL)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    """Cria cliente de teste para a API."""
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client(client, db_session):
    """Cria cliente autenticado para testes."""
    # Criar usuário de teste
    from car_api.models import User
    from car_api.core.security import get_password_hash
    
    user = User(
        username='testuser',
        email='test@example.com',
        password=get_password_hash('password123'),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Login para obter token
    login_response = await client.post(
        '/api/auth/api/token',
        json={'email': 'test@example.com', 'password': 'password123'},
    )
    token = login_response.json()['access_token']
    
    # Adicionar token ao cliente
    client.headers['Authorization'] = f'Bearer {token}'
    
    yield client
```

---

## 📝 Escrevendo Testes

### Testes de Autenticação

```python
# tests/test_auth.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Testa login com credenciais válidas."""
    # Criar usuário primeiro
    await client.post('/api/users/', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
    })
    
    # Tentar login
    response = await client.post('/api/auth/api/token', json={
        'email': 'test@example.com',
        'password': 'password123',
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Testa login com credenciais inválidas."""
    response = await client.post('/api/auth/api/token', json={
        'email': 'invalid@example.com',
        'password': 'wrongpassword',
    })
    
    assert response.status_code == 401
    assert response.json()['detail'] == 'Email ou senha incorretos'


@pytest.mark.asyncio
async def test_login_invalid_email_format(client: AsyncClient):
    """Testa login com formato de email inválido."""
    response = await client.post('/api/auth/api/token', json={
        'email': 'invalid-email',
        'password': 'password123',
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refresh_token(auth_client: AsyncClient):
    """Testa refresh de token."""
    response = await auth_client.post('/api/auth/refresh_token')
    
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
```

---

### Testes de Usuários

```python
# tests/test_users.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """Testa criação de usuário com sucesso."""
    user_data = {
        'username': 'joaosilva',
        'email': 'joao@example.com',
        'password': 'senha123',
    }
    
    response = await client.post('/api/users/', json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'joaosilva'
    assert data['email'] == 'joao@example.com'
    assert 'id' in data
    assert 'created_at' in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    """Testa criação de usuário com email duplicado."""
    user_data = {
        'username': 'joaosilva',
        'email': 'joao@example.com',
        'password': 'senha123',
    }
    
    # Criar primeiro usuário
    await client.post('/api/users/', json=user_data)
    
    # Tentar criar com mesmo email
    response = await client.post('/api/users/', json={
        'username': 'outro_usuario',
        'email': 'joao@example.com',
        'password': 'senha456',
    })
    
    assert response.status_code == 400
    assert 'já está em uso' in response.json()['detail']


@pytest.mark.asyncio
async def test_create_user_short_password(client: AsyncClient):
    """Testa validação de senha curta."""
    response = await client.post('/api/users/', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': '123',  # Muito curta
    })
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    """Testa obtenção de usuário por ID."""
    # Criar usuário
    create_response = await client.post('/api/users/', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'senha123',
    })
    user_id = create_response.json()['id']
    
    # Buscar usuário
    response = await client.get(f'/api/users/{user_id}')
    
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == user_id
    assert data['username'] == 'testuser'


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Testa busca de usuário inexistente."""
    response = await client.get('/api/users/99999')
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Testa listagem de usuários."""
    # Criar vários usuários
    for i in range(5):
        await client.post('/api/users/', json={
            'username': f'user{i}',
            'email': f'user{i}@example.com',
            'password': 'senha123',
        })
    
    response = await client.get('/api/users/?offset=0&limit=10')
    
    assert response.status_code == 200
    data = response.json()
    assert 'users' in data
    assert 'offset' in data
    assert 'limit' in data
    assert len(data['users']) >= 5


@pytest.mark.asyncio
async def test_update_user(auth_client: AsyncClient):
    """Testa atualização de usuário."""
    # Obter dados do usuário atual
    response = await auth_client.get('/api/users/1')
    user_id = response.json()['id']
    
    # Atualizar
    update_response = await auth_client.put(f'/api/users/{user_id}', json={
        'username': 'novo_username',
    })
    
    assert update_response.status_code == 200
    assert update_response.json()['username'] == 'novo_username'


@pytest.mark.asyncio
async def test_update_user_without_permission(client: AsyncClient, db_session):
    """Testa atualização sem permissão."""
    # Criar outro usuário
    from car_api.models import User
    from car_api.core.security import get_password_hash
    
    other_user = User(
        username='other',
        email='other@example.com',
        password=get_password_hash('senha123'),
    )
    db_session.add(other_user)
    await db_session.commit()
    
    # Tentar atualizar usuário de outro
    response = await client.put('/api/users/2', json={
        'username': 'hacked',
    })
    
    assert response.status_code == 401  # Não autenticado


@pytest.mark.asyncio
async def test_delete_user(auth_client: AsyncClient):
    """Testa exclusão de usuário."""
    # Obter ID do usuário
    response = await auth_client.get('/api/users/1')
    user_id = response.json()['id']
    
    # Deletar
    delete_response = await auth_client.delete(f'/api/users/{user_id}')
    
    assert delete_response.status_code == 204
    
    # Verificar que foi deletado
    get_response = await auth_client.get(f'/api/users/{user_id}')
    assert get_response.status_code == 404
```

---

### Testes de Carros

```python
# tests/test_cars.py

import pytest
from httpx import AsyncClient
from decimal import Decimal


@pytest.mark.asyncio
async def test_create_car_success(auth_client: AsyncClient, db_session):
    """Testa criação de carro com sucesso."""
    # Criar marca primeiro
    brand_response = await auth_client.post('/api/brands/', json={
        'name': 'Honda',
        'description': 'Marca japonesa',
    })
    brand_id = brand_response.json()['id']
    
    # Criar carro
    car_data = {
        'model': 'Civic EXL',
        'factory_year': 2020,
        'model_year': 2021,
        'color': 'Prata',
        'plate': 'ABC1D23',
        'fuel_type': 'gasoline',
        'transmission': 'automatic',
        'price': '125000.00',
        'description': 'Carro em excelente estado',
        'is_available': True,
        'brand_id': brand_id,
        'owner_id': 1,  # Usuário criado no fixture
    }
    
    response = await auth_client.post('/api/cars/', json=car_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data['model'] == 'Civic EXL'
    assert data['plate'] == 'ABC1D23'


@pytest.mark.asyncio
async def test_create_car_duplicate_plate(auth_client: AsyncClient):
    """Testa criação de carro com placa duplicada."""
    # Criar marca
    brand_response = await auth_client.post('/api/brands/', json={
        'name': 'Toyota',
    })
    brand_id = brand_response.json()['id']
    
    # Criar primeiro carro
    await auth_client.post('/api/cars/', json={
        'model': 'Corolla',
        'factory_year': 2020,
        'model_year': 2021,
        'color': 'Preto',
        'plate': 'XYZ9A87',
        'fuel_type': 'flex',
        'transmission': 'automatic',
        'price': '150000.00',
        'brand_id': brand_id,
        'owner_id': 1,
    })
    
    # Tentar criar com mesma placa
    response = await auth_client.post('/api/cars/', json={
        'model': 'Outro Carro',
        'factory_year': 2019,
        'model_year': 2020,
        'color': 'Branco',
        'plate': 'XYZ9A87',  # Mesma placa
        'fuel_type': 'gasoline',
        'transmission': 'manual',
        'price': '100000.00',
        'brand_id': brand_id,
        'owner_id': 1,
    })
    
    assert response.status_code == 409
    assert 'placa já está inserida' in response.json()['detail']


@pytest.mark.asyncio
async def test_list_cars_with_filters(auth_client: AsyncClient):
    """Testa listagem de carros com filtros."""
    response = await auth_client.get(
        '/api/cars/?fuel_type=gasoline&transmission=automatic'
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'cars' in data
    assert 'offset' in data
    assert 'limit' in data


@pytest.mark.asyncio
async def test_get_car_not_owner(auth_client: AsyncClient, db_session):
    """Testa acesso a carro de outro proprietário."""
    from car_api.models import Car, Brand, User, FuelType, TransmissionType
    from car_api.core.security import get_password_hash
    
    # Criar outro usuário
    other_user = User(
        username='other',
        email='other@example.com',
        password=get_password_hash('senha123'),
    )
    db_session.add(other_user)
    await db_session.commit()
    
    # Criar marca
    brand = Brand(name='Ford')
    db_session.add(brand)
    await db_session.commit()
    
    # Criar carro de outro usuário
    car = Car(
        model='Fiesta',
        factory_year=2018,
        model_year=2019,
        color='Azul',
        plate='DEF2G34',
        fuel_type=FuelType.FLEX,
        transmission=TransmissionType.MANUAL,
        price=Decimal('50000.00'),
        brand_id=brand.id,
        owner_id=other_user.id,
    )
    db_session.add(car)
    await db_session.commit()
    
    # Tentar acessar carro de outro
    response = await auth_client.get(f'/api/cars/{car.id}')
    
    assert response.status_code == 403
    assert 'permissão' in response.json()['detail']
```

---

### Testes de Marcas

```python
# tests/test_brands.py

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_brand_success(auth_client: AsyncClient):
    """Testa criação de marca com sucesso."""
    response = await auth_client.post('/api/brands/', json={
        'name': 'BMW',
        'description': 'Marca alemã de luxo',
        'is_active': True,
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'BMW'
    assert data['is_active'] == True


@pytest.mark.asyncio
async def test_create_brand_duplicate(auth_client: AsyncClient):
    """Testa criação de marca duplicada."""
    # Criar primeira marca
    await auth_client.post('/api/brands/', json={
        'name': 'Mercedes',
    })
    
    # Tentar criar duplicada
    response = await auth_client.post('/api/brands/', json={
        'name': 'Mercedes',
    })
    
    assert response.status_code == 400
    assert 'já existe' in response.json()['detail']


@pytest.mark.asyncio
async def test_delete_brand_with_cars(auth_client: AsyncClient, db_session):
    """Testa exclusão de marca com carros associados."""
    from car_api.models import Brand, Car, FuelType, TransmissionType
    from decimal import Decimal
    
    # Criar marca
    brand = Brand(name='Volkswagen')
    db_session.add(brand)
    await db_session.commit()
    
    # Criar carro com essa marca
    car = Car(
        model='Golf',
        factory_year=2020,
        model_year=2021,
        color='Cinza',
        plate='VW1A234',
        fuel_type=FuelType.FLEX,
        transmission=TransmissionType.AUTOMATIC,
        price=Decimal('120000.00'),
        brand_id=brand.id,
        owner_id=1,
    )
    db_session.add(car)
    await db_session.commit()
    
    # Tentar deletar marca
    response = await auth_client.delete(f'/api/brands/{brand.id}')
    
    assert response.status_code == 403
    assert 'carros associados' in response.json()['detail']
```

---

## 📊 Executando Testes

### Comandos Básicos

```bash
# Executar todos os testes
pytest

# Executar com verbose
pytest -v

# Executar arquivo específico
pytest tests/test_users.py -v

# Executar teste específico
pytest tests/test_users.py::test_create_user_success -v

# Executar por palavra-chave
pytest -k "test_create" -v

# Executar com coverage
pytest --cov=car_api --cov-report=html

# Executar com coverage e falhar se abaixo de threshold
pytest --cov=car_api --cov-fail-under=80
```

### Opções Úteis

| Opção | Descrição |
|-------|-----------|
| `-v` | Verbose - mostra nome dos testes |
| `-s` | Mostra output dos prints |
| `-x` | Para no primeiro erro |
| `--tb=short` | Traceback resumido |
| `--cov=car_api` | Gera relatório de coverage |
| `--cov-report=html` | Gera relatório HTML |
| `-k "pattern"` | Filtra testes por nome |
| `--maxfail=3` | Para após N falhas |

---

## 📈 Coverage Report

### Gerar Relatório

```bash
# Relatório no terminal
pytest --cov=car_api

# Relatório HTML (abrir htmlcov/index.html)
pytest --cov=car_api --cov-report=html

# Relatório XML (para CI/CD)
pytest --cov=car_api --cov-report=xml

# Múltiplos formatos
pytest --cov=car_api --cov-report=term --cov-report=html --cov-report=xml
```

### Configurar Threshold

```ini
# pytest.ini
[pytest]
addopts = --cov=car_api --cov-fail-under=80
```

---

## 🔧 Mock e Fixtures

### Mock de Dependências

```python
from unittest.mock import AsyncMock, patch
import pytest


@pytest.mark.asyncio
async def test_service_with_mock():
    """Testa service usando mock."""
    mock_db = AsyncMock()
    mock_repo = AsyncMock()
    
    with patch('car_api.services.users.UserRepository', mock_repo):
        mock_repo.verify_if_exists_username.return_value = False
        mock_repo.save.return_value = User(id=1, username='test')
        
        result = await UserService.create_user(mock_db, user_schema)
        
        assert result.id == 1
        mock_repo.save.assert_called_once()
```

### Fixtures Personalizadas

```python
# conftest.py

@pytest.fixture
def sample_user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
    }


@pytest.fixture
async def created_user(client, sample_user_data):
    response = await client.post('/api/users/', json=sample_user_data)
    return response.json()


# Uso nos testes
@pytest.mark.asyncio
async def test_using_fixtures(client, created_user):
    response = await client.get(f"/api/users/{created_user['id']}")
    assert response.status_code == 200
```

---

## 📋 Boas Práticas

### ✅ Faça

```python
# Nomes descritivos
def test_create_user_with_valid_data(): ...
def test_create_user_with_duplicate_email(): ...
def test_delete_user_without_permission_returns_403(): ...

# Arrange-Act-Assert
@pytest.mark.asyncio
async def test_example(client):
    # Arrange
    user_data = {'username': 'test', 'email': 'test@example.com', 'password': '123'}
    
    # Act
    response = await client.post('/api/users/', json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()['username'] == 'test'

# Use fixtures para reutilização
@pytest.fixture
async def auth_client(client):
    # Setup de autenticação
    yield client

# Isole testes
@pytest.mark.asyncio
async def test_isolated(client, db_session):
    # Cada teste deve ser independente
    ...
```

### ❌ Evite

```python
# Nomes genéricos
def test_user(): ...  # Ruim

# Testes dependentes
def test_create(): ...
def test_update(): ...  # Depende do create

# Múltiplas asserções complexas
def test_complex():
    assert x == 1
    assert y == 2
    assert z == 3
    assert a == 4
    assert b == 5  # Difícil debug
```

---

## 🐛 Debug de Testes

### Print Output

```bash
# Mostrar prints
pytest -s

# Ou use logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug com pytest

```python
def test_debug():
    import pdb; pdb.set_trace()
    # ... código
```

---

## 📚 Próximos Passos

Com os testes configurados:

1. [Deploy](deployment.md) - Prepare para produção
2. [Contribuição](contributing.md) - Como contribuir
3. [Release Notes](release-notes.md) - Histórico de versões

---

**Dica:** Execute testes frequentemente durante o desenvolvimento para capturar erros cedo.
