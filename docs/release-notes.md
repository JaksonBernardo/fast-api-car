# Release Notes

Histórico de versões e mudanças da CAR API.

---

## [1.0.0] - 2026-03-01

### 🎉 Lançamento Inicial

Primeira versão estável da CAR API com funcionalidades completas para gerenciamento de carros, usuários e marcas.

### ✨ Funcionalidades Adicionadas

#### Autenticação
- ✅ Login com email e senha
- ✅ Geração de token JWT
- ✅ Refresh de token
- ✅ Hash de senhas com Argon2
- ✅ Validação de permissões por ownership

#### Usuários
- ✅ Criar usuário
- ✅ Listar usuários com paginação
- ✅ Buscar usuário por ID
- ✅ Atualizar usuário
- ✅ Deletar usuário
- ✅ Busca por username ou email

#### Carros
- ✅ Criar carro
- ✅ Listar carros com filtros avançados
- ✅ Buscar carro por ID
- ✅ Atualizar carro
- ✅ Deletar carro
- ✅ Filtros: marca, proprietário, combustível, transmissão
- ✅ Validação de placa única
- ✅ Verificação de ownership

#### Marcas (Brands)
- ✅ Criar marca
- ✅ Listar marcas com paginação
- ✅ Buscar marca por ID
- ✅ Atualizar marca
- ✅ Deletar marca
- ✅ Validação de marcas com carros associados

### 🏗️ Arquitetura

- **Framework:** FastAPI 0.128.0
- **ORM:** SQLAlchemy 2.0.46 (assíncrono)
- **Banco de Dados:** MySQL/MariaDB com aiomysql
- **Validação:** Pydantic 2.12.5
- **Autenticação:** PyJWT 2.11.0
- **Migrações:** Alembic 1.18.3
- **Linter:** Ruff 0.15.4

### 📁 Estrutura do Projeto

```
car_api/
├── core/           # Configurações centrais
├── models/         # Modelos SQLAlchemy
├── repositories/   # Camada de dados
├── routers/        # Endpoints da API
├── schemas/        # Schemas Pydantic
└── services/       # Regras de negócio
```

### 📊 Modelos de Dados

#### User
- id, username, email, password
- created_at, updated_at
- Relacionamento: 1:N com Car

#### Car
- id, model, factory_year, model_year
- color, plate, fuel_type, transmission
- price, description, is_available
- brand_id (FK), owner_id (FK)
- created_at, updated_at

#### Brand
- id, name, description, is_active
- created_at, updated_at
- Relacionamento: 1:N com Car

### 🔐 Segurança

- JWT com HS256
- Argon2 para hash de senhas
- Validação de ownership para operações sensíveis
- Headers de autenticação HTTP Bearer

### 📝 Validações

| Campo | Validação |
|-------|-----------|
| username | Mínimo 3 caracteres |
| email | Formato válido, único |
| password | Mínimo 6 caracteres |
| model | Mínimo 2 caracteres |
| color | Mínimo 2 caracteres |
| plate | 7-10 caracteres, único |
| year | 1900-2030 |
| price | Maior que zero |

### 🧪 Testes

- Framework: pytest
- Testes assíncronos com pytest-asyncio
- Fixtures para banco de dados e cliente HTTP
- Coverage report disponível

### 📚 Documentação

- Documentação completa em português (pt-BR)
- Swagger UI em `/docs`
- Redoc em `/redoc`
- Guias de instalação, configuração e desenvolvimento

### 🛠️ Ferramentas de Desenvolvimento

```bash
# Taskipy tasks
task lint      # Executar linter
task format    # Formatar código
task run       # Iniciar servidor
task docs      # Iniciar documentação
```

### 📦 Dependências Principais

| Pacote | Versão |
|--------|--------|
| fastapi | 0.128.0 |
| sqlalchemy | 2.0.46 |
| pydantic | 2.12.5 |
| pyjwt | 2.11.0 |
| alembic | 1.18.3 |
| argon2-cffi | 25.1.0 |
| uvicorn | 0.40.0 |
| ruff | 0.15.4 |

### 🐛 Correções Conhecidas

- Nenhuma correção pendente nesta versão

### ⚠️ Breaking Changes

- Nenhuma (versão inicial)

### 📋 Pendências para Próximas Versões

- [ ] Refresh token com token dedicado
- [ ] Upload de imagens para carros
- [ ] Sistema de favoritos
- [ ] Histórico de visualizações
- [ ] Exportação de dados (CSV, JSON)
- [ ] Rate limiting
- [ ] Webhooks
- [ ] GraphQL API

---

## 📅 Linha do Tempo

| Versão | Data | Status |
|--------|------|--------|
| 1.0.0 | 2026-03-01 | ✅ Lançada |

---

## 🔗 Links Relacionados

- [Repositório](https://github.com/JaksonBernardo/fast-api-car)
- [Issues](https://github.com/JaksonBernardo/fast-api-car/issues)
- [Documentação](./index.md)

---

## 📞 Contato

**Autor:** Jakson  
**GitHub:** [@JaksonBernardo](https://github.com/JaksonBernardo)  
**LinkedIn:** [jakson-bernardo](https://linkedin.com/in/jakson-bernardo)

---

## 🙏 Agradecimentos

Agradecemos a todos os contribuidores que tornaram este projeto possível!

---

**Nota:** Este é o lançamento inicial da CAR API. Versões futuras trarão novas funcionalidades e melhorias.
