# Visão Geral do Projeto

## 🎯 O que é a CAR API?

A **CAR API** é uma API RESTful assíncrona desenvolvida para fornecer um sistema completo de gerenciamento de veículos e usuários. Construída com tecnologias modernas e de alta performance, a API permite o cadastro, listagem, atualização e exclusão de carros, marcas e usuários de forma segura e eficiente.

## 🏗️ Arquitetura

O projeto segue uma arquitetura em camadas bem definida:

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente (Frontend)                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      Routers (API)                       │
│              (Endpoints HTTP - FastAPI)                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Services (Regras)                     │
│            (Lógica de Negócio e Validações)              │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Repositories (DAO)                     │
│         (Acesso e Persistência de Dados)                 │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Banco de Dados (MySQL)                  │
│              (Persistência com SQLAlchemy)               │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| **Python** | 3.10+ | Linguagem principal |
| **FastAPI** | 0.128.0 | Framework web assíncrono |
| **SQLAlchemy** | 2.0.46 | ORM assíncrono |
| **Pydantic** | 2.12.5 | Validação de dados |
| **PyJWT** | 2.11.0 | Autenticação JWT |
| **Alembic** | 1.18.3 | Migrações de banco |
| **MySQL** | - | Banco de dados |
| **aiomysql** | 0.3.2 | Driver MySQL assíncrono |
| **Argon2** | 25.1.0 | Hash de senhas |
| **Ruff** | 0.15.4 | Linter e formatador |
| **MkDocs** | 1.6.1 | Documentação |

## 📦 Módulos Principais

### 1. Autenticação e Usuários
- Registro e login de usuários
- Gerenciamento de perfil
- Autenticação baseada em JWT
- Controle de permissões

### 2. Carros
- Cadastro completo de veículos
- Listagem com filtros avançados
- Atualização e exclusão
- Vinculação com marcas e proprietários

### 3. Marcas (Brands)
- Gerenciamento de marcas de veículos
- Ativação/desativação de marcas
- Relacionamento com carros

## 🔐 Segurança

A API implementa diversas camadas de segurança:

- **JWT (JSON Web Tokens)** - Autenticação stateless
- **Argon2** - Hash de senhas com algoritmo moderno
- **Validação de Permissões** - Usuários só podem alterar seus próprios recursos
- **Propriedade de Carros** - Verificação de ownership para operações em veículos

## 🚀 Recursos e Funcionalidades

### Usuários
- [x] Criar usuário
- [x] Listar usuários (com paginação e busca)
- [x] Obter usuário por ID
- [x] Atualizar usuário
- [x] Deletar usuário

### Carros
- [x] Criar carro
- [x] Listar carros (com filtros avançados)
- [x] Obter carro por ID
- [x] Atualizar carro
- [x] Deletar carro

### Marcas
- [x] Criar marca
- [x] Listar marcas (com filtros)
- [x] Obter marca por ID
- [x] Atualizar marca
- [x] Deletar marca

### Autenticação
- [x] Login (gerar token)
- [x] Refresh token

## 📊 Modelos de Dados

O sistema é composto por três entidades principais:

1. **User (Usuário)** - Representa os usuários do sistema
2. **Car (Carro)** - Representa os veículos cadastrados
3. **Brand (Marca)** - Representa as marcas de automóveis

Para mais detalhes sobre a modelagem, consulte [Modelagem do Sistema](system-modeling.md).

## 🎯 Casos de Uso

A CAR API pode ser utilizada em diversos cenários:

- **Concessionárias** - Gerenciamento de estoque de veículos
- **Locadoras** - Controle de frota
- **Marketplace de Veículos** - Plataforma de compra e venda
- **Sistemas de Gestão** - Controle interno de frota empresarial

## 📝 Próximos Passos

Para começar a usar a CAR API:

1. Verifique os [Pré-requisitos](prerequisites.md)
2. Siga o guia de [Instalação](installation.md)
3. Configure o ambiente em [Configuração](configuration.md)

---

**Autor:** Jakson  
**Repositório:** [github.com/JaksonBernardo/fast-api-car](https://github.com/JaksonBernardo/fast-api-car.git)
