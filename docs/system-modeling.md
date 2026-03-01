# Modelagem do Sistema

Este documento apresenta a modelagem de dados e arquitetura do sistema CAR API, incluindo diagramas visuais que ilustram a estrutura e os fluxos principais da aplicação.

---

## 📊 Modelos de Dados (ERD)

O sistema é composto por três entidades principais: **User**, **Car** e **Brand**.

```mermaid
erDiagram
    USER ||--o{ CAR : "possui"
    BRAND ||--o{ CAR : "classifica"

    USER {
        int id PK
        varchar username
        varchar email UK
        varchar password
        datetime created_at
        datetime updated_at
    }

    BRAND {
        int id PK
        varchar name
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    CAR {
        int id PK
        varchar model
        int factory_year
        int model_year
        varchar color
        varchar plate UK
        enum fuel_type
        enum transmission
        decimal price
        text description
        boolean is_available
        int brand_id FK
        int owner_id FK
        datetime created_at
        datetime updated_at
    }
```

### Relacionamentos

| Relacionamento | Tipo | Descrição |
|----------------|------|-----------|
| User → Car | 1:N | Um usuário pode possuir vários carros |
| Brand → Car | 1:N | Uma marca pode classificar vários carros |

---

## 🏗️ Arquitetura do Sistema

A CAR API segue uma arquitetura em camadas (Layered Architecture) com separação clara de responsabilidades.

```mermaid
graph TB
    subgraph "Camada de Apresentação"
        Client[Cliente HTTP]
        Router[Routers<br/>FastAPI Endpoints]
    end

    subgraph "Camada de Negócio"
        Service[Services<br/>Regras de Negócio]
    end

    subgraph "Camada de Dados"
        Repository[Repositories<br/>Acesso a Dados]
        Model[Models<br/>SQLAlchemy ORM]
    end

    subgraph "Infraestrutura"
        DB[(MySQL Database)]
        Security[Security Module<br/>JWT & Hash]
    end

    Client --> Router
    Router --> Service
    Service --> Repository
    Repository --> Model
    Model --> DB
    Router --> Security
    Service --> Security
```

### Descrição das Camadas

| Camada | Responsabilidade | Localização |
|--------|------------------|-------------|
| **Routers** | Receber requisições HTTP, validar schemas, retornar respostas | `car_api/routers/` |
| **Services** | Aplicar regras de negócio, validações complexas | `car_api/services/` |
| **Repositories** | Executar operações de banco de dados | `car_api/repositories/` |
| **Models** | Definir estrutura das tabelas | `car_api/models/` |
| **Schemas** | Validar e serializar dados | `car_api/schemas/` |
| **Security** | Autenticação JWT, hash de senhas | `car_api/core/security.py` |

---

## 🔐 Fluxo de Autenticação

Diagrama de sequência do processo de autenticação e geração de token JWT.

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router (Auth)
    participant S as Security Module
    participant DB as Banco de Dados

    C->>R: POST /api/auth/api/token<br/>{email, password}
    
    R->>DB: SELECT user WHERE email = ?
    DB-->>R: User (hashed_password)
    
    R->>S: verify_password(plain, hashed)
    S-->>R: true/false
    
    alt Senha Inválida
        R-->>C: 401 Unauthorized<br/>"Email ou senha incorretos"
    else Senha Válida
        R->>S: create_access_token({sub: user_id})
        S-->>R: JWT Token
        
        R-->>C: 200 OK<br/>{access_token, token_type}
    end

    Note over C,DB: Uso do Token em Requisições Futuras
    
    C->>R: GET /api/cars/<br/>Authorization: Bearer {token}
    R->>S: verify_token(token)
    S-->>R: payload {sub: user_id, exp: ...}
    R->>DB: SELECT user WHERE id = ?
    DB-->>R: User
    R-->>C: 200 OK + Dados
```

### Etapas do Fluxo

1. **Login:** Cliente envia email e senha
2. **Busca Usuário:** Sistema busca usuário no banco
3. **Verifica Senha:** Compara senha com hash armazenado (Argon2)
4. **Gera Token:** Cria JWT com `sub` = user_id e expiração
5. **Retorna Token:** Cliente recebe token para uso futuro
6. **Requisições Autenticadas:** Cliente envia token no header `Authorization: Bearer`
7. **Valida Token:** Sistema verifica validade e extrai user_id
8. **Busca Usuário:** Obtém dados completos do usuário

---

## 🚗 Fluxo CRUD de Carros

Diagrama de fluxo do processo de criação de um carro (Create).

```mermaid
flowchart TD
    Start([Início]) --> Auth[Autenticação<br/>Validar Token JWT]
    
    Auth --> Invalid{Token Válido?}
    Invalid -->|Não| Error401[Retorna 401<br/>Não Autorizado]
    Invalid -->|Sim| Validate[Validar Schema<br/>Pydantic]
    
    Validate --> InvalidSchema{Dados Válidos?}
    InvalidSchema -->|Não| Error422[Retorna 422<br/>Erro de Validação]
    InvalidSchema -->|Sim| CheckBrand[Verificar Brand<br/>Existe?]
    
    CheckBrand --> NoBrand{Brand Existe?}
    NoBrand -->|Não| Error404[Retorna 404<br/>Marca não encontrada]
    NoBrand -->|Sim| CheckOwner[Verificar Owner<br/>Existe?]
    
    CheckOwner --> NoOwner{Owner Existe?}
    NoOwner -->|Não| Error404Owner[Retorna 404<br/>Proprietário não encontrado]
    NoOwner -->|Sim| CheckPlate[Verificar Placa<br/>Já existe?]
    
    CheckPlate --> PlateExists{Placa Existe?}
    PlateExists -->|Sim| Error409[Retorna 409<br/>Placa já cadastrada]
    PlateExists -->|Não| Create[Salvar Carro no BD]
    
    Create --> GetRelations[Buscar Dados da<br/>Brand e Owner]
    GetRelations --> Return[Retorna 201<br/>Carro Criado]
    
    Error401 --> End([Fim])
    Error422 --> End
    Error404 --> End
    Error404Owner --> End
    Error409 --> End
    Return --> End
```

### Validações do Fluxo

| Validação | Descrição | Código de Erro |
|-----------|-----------|----------------|
| Token JWT | Verifica se usuário está autenticado | 401 |
| Schema | Valida dados de entrada com Pydantic | 422 |
| Brand | Verifica se marca existe | 404 |
| Owner | Verifica se proprietário existe | 404 |
| Plate | Verifica unicidade da placa | 409 |

---

## 🔒 Fluxo de Segurança

Diagrama do sistema de permissões e controle de acesso.

```mermaid
flowchart TD
    Request[Requisição HTTP] --> AuthCheck{Endpoint Requer<br/>Autenticação?}
    
    AuthCheck -->|Não| Public[Endpoint Público<br/>Ex: /api/auth/api/token]
    AuthCheck -->|Sim| TokenCheck{Token Presente<br/>no Header?}
    
    TokenCheck -->|Não| Error401[Retorna 401<br/>Não Autorizado]
    TokenCheck -->|Sim| ValidateToken[Validar Token JWT]
    
    ValidateToken --> Expired{Token Expirado?}
    Expired -->|Sim| Error401Exp[Retorna 401<br/>Token Expirado]
    Expired -->|Não| Invalid{Token Inválido?}
    
    Invalid -->|Sim| Error401Inv[Retorna 401<br/>Token Inválido]
    Invalid -->|Não| GetUser[Buscar Usuário<br/>pelo ID no Token]
    
    GetUser --> UserExists{Usuário Existe?}
    UserExists -->|Não| Error404User[Retorna 404<br/>Usuário não encontrado]
    UserExists -->|Sim| PermissionCheck{Verificar<br/>Permissão}
    
    PermissionCheck --> IsOwner{É o Proprietário?}
    IsOwner -->|Não| Error403[Retorna 403<br/>Acesso Negado]
    IsOwner -->|Sim| Execute[Executar Operação]
    
    Execute --> Success[Retorna Sucesso]
    
    Public --> End([Fim])
    Error401 --> End
    Error401Exp --> End
    Error401Inv --> End
    Error404User --> End
    Error403 --> End
    Success --> End
```

### Níveis de Permissão

| Tipo de Endpoint | Permissão Necessária | Exemplo |
|------------------|---------------------|---------|
| **Público** | Nenhuma | `POST /api/auth/api/token` |
| **Autenticado** | Token JWT válido | `GET /api/brands/` |
| **Owner (Usuário)** | Token + Mesmo user_id | `PUT /api/users/{id}` |
| **Owner (Carro)** | Token + Dono do carro | `DELETE /api/cars/{id}` |

### Funções de Segurança

```python
# car_api/core/security.py

# Hash de senha
get_password_hash(password: str) -> str
verify_password(plain_password, hashed_password) -> bool

# JWT
create_access_token(data: Dict) -> str
verify_token(token: str) -> Dict

# Autenticação
authenticate_user(email, password, db) -> User | None
get_current_user(credentials, db) -> User

# Permissões
verify_user_permission(current_user, user_id) -> None
verify_car_ownership(user, car_owner_id) -> None
```

---

## 📦 Diagrama de Classes

```mermaid
classDiagram
    class User {
        +int id
        +str username
        +str email
        +str password
        +datetime created_at
        +datetime updated_at
        +cars: List[Car]
    }

    class Car {
        +int id
        +str model
        +int factory_year
        +int model_year
        +str color
        +str plate
        +FuelType fuel_type
        +TransmissionType transmission
        +Decimal price
        +str description
        +bool is_available
        +int brand_id
        +int owner_id
        +datetime created_at
        +datetime updated_at
        +brand: Brand
        +owner: User
    }

    class Brand {
        +int id
        +str name
        +str description
        +bool is_active
        +datetime created_at
        +datetime updated_at
        +cars: List[Car]
    }

    class FuelType {
        <<enumeration>>
        GASOLINE
        ETHANOL
        FLEX
        DIESEL
        ELETRIC
        HYBRID
    }

    class TransmissionType {
        <<enumeration>>
        MANUAL
        AUTOMATIC
        SEMI_AUTOMATIC
        CVT
    }

    User "1" -- "0..*" Car : possui
    Brand "1" -- "0..*" Car : classifica
    Car --> FuelType : usa
    Car --> TransmissionType : usa
```

---

## 🔄 Diagrama de Sequência - Atualização de Carro

```mermaid
sequenceDiagram
    participant C as Cliente
    participant R as Router (Cars)
    participant S as CarServices
    participant Repo as CarRepository
    participant DB as Banco de Dados

    C->>R: PUT /api/cars/{id}<br/>Auth + Dados
    R->>R: get_current_user()
    R->>S: update_car(db, data, id, user)
    
    S->>Repo: verify_if_exists_by_id(id)
    Repo->>DB: SELECT EXISTS
    DB-->>Repo: true/false
    Repo-->>S: exists
    
    alt Carro Não Existe
        S-->>R: HTTPException 404
        R-->>C: 404 Not Found
    else Carro Existe
        S->>Repo: get_car_by_id(id)
        Repo->>DB: SELECT car
        DB-->>Repo: Car
        Repo-->>S: Car
        
        S->>S: verify_car_ownership(user, car.owner_id)
        
        alt Sem Permissão
            S-->>R: HTTPException 403
            R-->>C: 403 Forbidden
        else Com Permissão
            S->>Repo: verify_if_plate_exists(plate)
            Repo->>DB: SELECT EXISTS
            DB-->>Repo: exists
            Repo-->>S: false (não existe)
            
            S->>S: setattr(car, field, value)
            S->>Repo: update_car(car)
            Repo->>DB: UPDATE + COMMIT
            DB-->>Repo: success
            Repo-->>S: Car (atualizado)
            S-->>R: CarPublicSchema
            R-->>C: 200 OK + Carro
        end
    end
```

---

## 📊 Resumo dos Modelos

### User (Usuário)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Chave primária |
| `username` | varchar(100) | Nome de usuário |
| `email` | varchar(255) | Email único |
| `password` | varchar(255) | Senha com hash Argon2 |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

### Car (Carro)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Chave primária |
| `model` | varchar(100) | Modelo do veículo |
| `factory_year` | int | Ano de fabricação |
| `model_year` | int | Ano modelo |
| `color` | varchar(100) | Cor do veículo |
| `plate` | varchar(20) | Placa (única) |
| `fuel_type` | enum | Tipo de combustível |
| `transmission` | enum | Tipo de transmissão |
| `price` | decimal(15,2) | Preço |
| `description` | text | Descrição |
| `is_available` | boolean | Disponível para venda |
| `brand_id` | int | Chave estrangeira (Brand) |
| `owner_id` | int | Chave estrangeira (User) |

### Brand (Marca)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | int | Chave primária |
| `name` | varchar(100) | Nome da marca |
| `description` | text | Descrição |
| `is_active` | boolean | Status ativo/inativo |
| `created_at` | datetime | Data de criação |
| `updated_at` | datetime | Data de atualização |

---

## 📚 Próximos Passos

Compreendida a modelagem:

1. [Autenticação e Segurança](authentication.md) - Detalhes sobre segurança
2. [API Endpoints](api-endpoints.md) - Explore os endpoints
3. [Desenvolvimento](development.md) - Comece a desenvolver

---

**Referência:** Para mais detalhes sobre implementação, consulte os arquivos em `car_api/models/`.
