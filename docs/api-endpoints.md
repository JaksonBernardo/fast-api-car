# API Endpoints

Este documento descreve todos os endpoints disponíveis na CAR API, incluindo métodos HTTP, parâmetros, schemas de entrada/saída e exemplos de uso.

## 📋 Informações Gerais

- **Base URL:** `http://localhost:8000`
- **Versão da API:** v1
- **Formato:** JSON
- **Autenticação:** JWT Bearer Token (onde aplicável)

---

## 🔐 Autenticação

### Gerar Token de Acesso

Obtém um token JWT realizando login com email e senha.

```
POST /api/auth/api/token
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Resposta de Erro (401 Unauthorized):**
```json
{
  "detail": "Email ou senha incorretos"
}
```

---

### Atualizar Token (Refresh Token)

Gera um novo token de acesso usando um token válido.

```
POST /api/auth/refresh_token
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Resposta de Sucesso (200 OK):**
```json
{
  "access_token": "novo_token_gerado...",
  "token_type": "bearer"
}
```

---

## 👥 Usuários

### Criar Usuário

Registra um novo usuário no sistema.

```
POST /api/users/
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "joaosilva",
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Validações:**
- `username`: Mínimo de 3 caracteres
- `email`: Deve ser um email válido
- `password`: Mínimo de 6 caracteres

**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "username": "joaosilva",
  "email": "joao@example.com",
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 400 | Nome ou email já está em uso |
| 422 | Dados inválidos (validação) |
| 500 | Erro interno no servidor |

---

### Listar Usuários

Lista todos os usuários com paginação e busca.

```
GET /api/users/?offset=0&limit=10&search=joao
```

**Parâmetros de Query:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `offset` | int | 0 | Número de registros a pular |
| `limit` | int | 100 | Limite de registros (1-100) |
| `search` | string | null | Buscar por username ou email |

**Resposta de Sucesso (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "joaosilva",
      "email": "joao@example.com",
      "created_at": "2026-03-01T10:00:00",
      "updated_at": "2026-03-01T10:00:00"
    }
  ],
  "offset": 0,
  "limit": 10
}
```

---

### Obter Usuário por ID

Obtém os detalhes de um usuário específico.

```
GET /api/users/{user_id}
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "username": "joaosilva",
  "email": "joao@example.com",
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 404 | Usuário não encontrado |
| 500 | Erro interno no servidor |

---

### Atualizar Usuário

Atualiza os dados de um usuário. Apenas o próprio usuário pode se atualizar.

```
PUT /api/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Body (todos os campos são opcionais):**
```json
{
  "username": "novo_username",
  "email": "novo@email.com",
  "password": "nova_senha"
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "username": "novo_username",
  "email": "novo@email.com",
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T11:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 403 | Você não tem permissão para alterar esse usuário |
| 404 | Usuário não encontrado |
| 409 | Email indisponível |

---

### Deletar Usuário

Remove um usuário do sistema. Apenas o próprio usuário pode se deletar.

```
DELETE /api/users/{user_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `user_id` | int | ID do usuário |

**Resposta de Sucesso (204 No Content):**
```
(sem conteúdo)
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 403 | Você não tem permissão para alterar esse usuário |
| 404 | Usuário não encontrado |

---

## 🚗 Carros

### Criar Carro

Cadastra um novo veículo no sistema.

```
POST /api/cars/
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
Content-Type: application/json
```

**Body:**
```json
{
  "model": "Civic EXL",
  "factory_year": 2020,
  "model_year": 2021,
  "color": "Prata",
  "plate": "ABC1D23",
  "fuel_type": "gasoline",
  "transmission": "automatic",
  "price": 125000.00,
  "description": "Carro em excelente estado",
  "is_available": true,
  "brand_id": 1,
  "owner_id": 1
}
```

**Tipos Válidos:**

| Campo | Valores |
|-------|---------|
| `fuel_type` | `gasoline`, `ethanol`, `flex`, `diesel`, `electric`, `hybrid` |
| `transmission` | `manual`, `automatic`, `semi_automatic`, `cvt` |

**Validações:**
- `model`: Mínimo de 2 caracteres
- `color`: Mínimo de 2 caracteres
- `plate`: 7 a 10 caracteres (formato Mercosul)
- `factory_year`, `model_year`: 1900-2030
- `price`: Maior que zero

**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "model": "Civic EXL",
  "factory_year": 2020,
  "model_year": 2021,
  "color": "Prata",
  "plate": "ABC1D23",
  "fuel_type": "gasoline",
  "transmission": "automatic",
  "price": "125000.00",
  "description": "Carro em excelente estado",
  "is_available": true,
  "brand_id": 1,
  "owner_id": 1,
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00",
  "brand": {
    "id": 1,
    "name": "Honda",
    "description": "Marca japonesa",
    "is_active": true,
    "created_at": "2026-03-01T09:00:00",
    "updated_at": "2026-03-01T09:00:00"
  },
  "owner": {
    "id": 1,
    "username": "joaosilva",
    "email": "joao@example.com",
    "created_at": "2026-03-01T08:00:00",
    "updated_at": "2026-03-01T08:00:00"
  }
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 404 | Marca de carro não encontrada / Proprietário não encontrado |
| 409 | Esta placa já está inserida no sistema |

---

### Listar Carros

Lista todos os veículos com filtros avançados.

```
GET /api/cars/?offset=0&limit=10&search=civic&brand_id=1&fuel_type=gasoline
```

**Parâmetros de Query:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `offset` | int | 0 | Número de registros a pular |
| `limit` | int | 100 | Limite de registros (1-100) |
| `search` | string | null | Buscar por modelo ou placa |
| `brand_id` | int | null | Filtrar por marca |
| `owner_id` | int | null | Filtrar por proprietário |
| `fuel_type` | string | null | Filtrar por tipo de combustível |
| `transmission` | string | null | Filtrar por tipo de transmissão |

**Resposta de Sucesso (200 OK):**
```json
{
  "cars": [
    {
      "id": 1,
      "model": "Civic EXL",
      "factory_year": 2020,
      "model_year": 2021,
      "color": "Prata",
      "plate": "ABC1D23",
      "fuel_type": "gasoline",
      "transmission": "automatic",
      "price": "125000.00",
      "description": "Carro em excelente estado",
      "is_available": true,
      "brand_id": 1,
      "owner_id": 1,
      "created_at": "2026-03-01T10:00:00",
      "updated_at": "2026-03-01T10:00:00",
      "brand": {...},
      "owner": {...}
    }
  ],
  "offset": 0,
  "limit": 10
}
```

---

### Obter Carro por ID

Obtém os detalhes de um veículo específico. Apenas o proprietário pode visualizar.

```
GET /api/cars/{car_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `car_id` | int | ID do carro |

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "model": "Civic EXL",
  "factory_year": 2020,
  ...
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 403 | Você não tem permissão para acessar esse carro |
| 404 | Carro não encontrado |

---

### Atualizar Carro

Atualiza os dados de um veículo. Apenas o proprietário pode atualizar.

```
PUT /api/cars/{car_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
Content-Type: application/json
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `car_id` | int | ID do carro |

**Body (todos os campos são opcionais):**
```json
{
  "model": "Novo Modelo",
  "color": "Preto",
  "price": 130000.00,
  "is_available": false
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "model": "Novo Modelo",
  ...
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 403 | Você não tem permissão para acessar esse carro |
| 404 | Carro não encontrado |
| 409 | Placa do veículo já existente / Preço inválido |

---

### Deletar Carro

Remove um veículo do sistema.

```
DELETE /api/cars/{car_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `car_id` | int | ID do carro |

**Resposta de Sucesso (204 No Content):**
```
(sem conteúdo)
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 403 | Você não tem permissão para acessar esse carro |
| 404 | Carro não encontrado |

---

## 🏷️ Marcas (Brands)

### Criar Marca

Cadastra uma nova marca de veículo.

```
POST /api/brands/
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
Content-Type: application/json
```

**Body:**
```json
{
  "name": "Toyota",
  "description": "Marca japonesa de automóveis",
  "is_active": true
}
```

**Validações:**
- `name`: Mínimo de 2 caracteres

**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "name": "Toyota",
  "description": "Marca japonesa de automóveis",
  "is_active": true,
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 400 | Brand já existe |
| 401 | Não autorizado |

---

### Listar Marcas

Lista todas as marcas cadastradas.

```
GET /api/brands/?offset=0&limit=10&search=toyota&is_active=true
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Query:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `offset` | int | 0 | Número de registros a pular |
| `limit` | int | 10 | Limite de registros (1-10) |
| `search` | string | null | Buscar por nome ou descrição |
| `is_active` | bool | null | Filtrar por status |

**Resposta de Sucesso (200 OK):**
```json
{
  "brands": [
    {
      "id": 1,
      "name": "Toyota",
      "description": "Marca japonesa de automóveis",
      "is_active": true,
      "created_at": "2026-03-01T10:00:00",
      "updated_at": "2026-03-01T10:00:00"
    }
  ],
  "offset": 0,
  "limit": 10
}
```

---

### Obter Marca por ID

Obtém os detalhes de uma marca específica.

```
GET /api/brands/{brand_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `brand_id` | int | ID da marca |

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "name": "Toyota",
  "description": "Marca japonesa de automóveis",
  "is_active": true,
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 404 | Essa brand não existe |

---

### Atualizar Marca

Atualiza os dados de uma marca.

```
PUT /api/brands/{brand_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
Content-Type: application/json
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `brand_id` | int | ID da marca |

**Body (todos os campos são opcionais):**
```json
{
  "name": "Novo Nome",
  "description": "Nova descrição",
  "is_active": false
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "id": 1,
  "name": "Novo Nome",
  "description": "Nova descrição",
  "is_active": false,
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T11:00:00"
}
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 401 | Não autorizado |
| 404 | Essa brand não existe |
| 409 | Nome da marca já existente |

---

### Deletar Marca

Remove uma marca do sistema.

```
DELETE /api/brands/{brand_id}
```

**Headers:**
```
Authorization: Bearer <seu_token_aqui>
```

**Parâmetros de Path:**

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `brand_id` | int | ID da marca |

**Resposta de Sucesso (204 No Content):**
```
(sem conteúdo)
```

**Respostas de Erro:**

| Código | Mensagem |
|--------|----------|
| 400 | Essa brand não existe |
| 401 | Não autorizado |
| 403 | Essa brand tem carros associados, não pode ser deletada |

---

## 📊 Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 201 | Created | Recurso criado com sucesso |
| 204 | No Content | Requisição bem-sucedida, sem conteúdo |
| 400 | Bad Request | Dados inválidos |
| 401 | Unauthorized | Não autenticado |
| 403 | Forbidden | Sem permissão |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Conflito (duplicidade) |
| 422 | Unprocessable Entity | Erro de validação |
| 500 | Internal Server Error | Erro no servidor |

---

## 🔗 Links Relacionados

- [Autenticação e Segurança](authentication.md)
- [Modelagem do Sistema](system-modeling.md)
- [Desenvolvimento](development.md)

---

**Dica:** Acesse `http://localhost:8000/docs` para visualizar a documentação interativa da API (Swagger UI).
