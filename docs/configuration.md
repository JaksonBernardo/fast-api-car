# Configuração do Projeto

Este documento descreve como configurar corretamente o ambiente da CAR API através de variáveis de ambiente e arquivos de configuração.

## 📝 Arquivo .env

A configuração do projeto é feita através de um arquivo `.env` na raiz do projeto. Este arquivo contém todas as variáveis de ambiente necessárias para a aplicação funcionar corretamente.

### Estrutura do Arquivo .env

Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo:

```ini
# ===========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ===========================================
DB_HOST=localhost
DB_USER=car_api_user
DB_PASSWORD=sua_senha_segura
DB_PORT=3306
DB_NAME=car_api

# URL completa de conexão (DATABASE_URL)
# Formato: mysql+aiomysql://usuario:senha@host:porta/banco
DATABASE_URL=mysql+aiomysql://car_api_user:sua_senha_segura@localhost:3306/car_api

# ===========================================
# CONFIGURAÇÃO DO JWT (JSON WEB TOKEN)
# ===========================================
# Chave secreta para assinar os tokens JWT
# Gere uma chave forte e única para produção
JWT_SECRET_KEY=sua_chave_secreta_muito_forte_e_segura

# Algoritmo de criptografia utilizado
JWT_ALGORITHM=HS256

# Tempo de expiração do token em minutos
JWT_EXPIRATION_MINUTES=30
```

---

## 🔐 Configurações de Segurança

### JWT_SECRET_KEY

A chave secreta do JWT é crítica para a segurança da aplicação. **Nunca use valores padrão em produção**.

#### Gerando uma Chave Segura:

**Python:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**OpenSSL:**
```bash
openssl rand -hex 32
```

**Linux (urandom):**
```bash
head -c 32 /dev/urandom | base64
```

Exemplo de chave segura:
```
JWT_SECRET_KEY=x7K9mN2pQ5rT8wZ3yB6cD0fG4hJ7kL1nM5sV9xA2eI6uO
```

### JWT_ALGORITHM

O algoritmo padrão é `HS256` (HMAC-SHA256). Este valor é adequado para a maioria dos casos de uso.

Algoritmos suportados:
- `HS256` - HMAC-SHA256 (recomendado)
- `HS384` - HMAC-SHA384
- `HS512` - HMAC-SHA512

### JWT_EXPIRATION_MINUTES

Define o tempo de validade do token de acesso.

| Ambiente | Valor Recomendado |
|----------|-------------------|
| Desenvolvimento | 60-120 minutos |
| Produção | 15-30 minutos |
| APIs internas | 5-15 minutos |

---

## 🗄️ Configuração do Banco de Dados

### Variáveis de Conexão

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `DB_HOST` | Host do servidor MySQL | `localhost` |
| `DB_USER` | Usuário do banco de dados | `car_api_user` |
| `DB_PASSWORD` | Senha do usuário | `senha123` |
| `DB_PORT` | Porta do MySQL | `3306` |
| `DB_NAME` | Nome do banco de dados | `car_api` |

### DATABASE_URL

A URL de conexão segue o formato:

```
mysql+aiomysql://USUARIO:SENHA@HOST:PORTA/BANCO
```

#### Exemplos:

**Localhost:**
```ini
DATABASE_URL=mysql+aiomysql://root:senha@localhost:3306/car_api
```

**Servidor Remoto:**
```ini
DATABASE_URL=mysql+aiomysql://app:senha123@192.168.1.100:3306/car_api
```

**Docker:**
```ini
DATABASE_URL=mysql+aiomysql://car_api:senha@mysql:3306/car_api
```

---

## 🌍 Ambientes Múltiplos

### Desenvolvimento (.env.dev)

```ini
DB_HOST=localhost
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_NAME=car_api_dev
JWT_SECRET_KEY=dev_secret_key_change_in_production
JWT_EXPIRATION_MINUTES=120
```

### Produção (.env.prod)

```ini
DB_HOST=prod-db.example.com
DB_USER=prod_user
DB_PASSWORD=senha_forte_producao
DB_NAME=car_api_prod
JWT_SECRET_KEY=chave_secreta_forte_gerada_aleatoriamente
JWT_EXPIRATION_MINUTES=30
```

### Testes (.env.test)

```ini
DB_HOST=localhost
DB_USER=test_user
DB_PASSWORD=test_password
DB_NAME=car_api_test
JWT_SECRET_KEY=test_secret_key
JWT_EXPIRATION_MINUTES=5
```

---

## 🔧 Carregando Variáveis de Ambiente

A aplicação carrega automaticamente as variáveis do arquivo `.env` usando `pydantic-settings`.

### Verificando se as Variáveis foram Carregadas:

```python
from car_api.core.settings import Settings

settings = Settings()
print(f"DB_HOST: {settings.DB_HOST}")
print(f"JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
```

---

## 🐳 Configuração para Docker

Se estiver usando Docker, você pode passar as variáveis de ambiente via `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
      - DB_USER=car_api_user
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=car_api
      - DATABASE_URL=mysql+aiomysql://car_api_user:${DB_PASSWORD}@mysql:3306/car_api
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION_MINUTES=30
    depends_on:
      - mysql

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_PASSWORD}
      - MYSQL_DATABASE=car_api
      - MYSQL_USER=car_api_user
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

---

## 📋 Validação da Configuração

### Script de Validação

Crie um script para validar a configuração:

```python
# validate_config.py
from car_api.core.settings import Settings

try:
    settings = Settings()
    print("✅ Configuração válida!")
    print(f"   DB_HOST: {settings.DB_HOST}")
    print(f"   DB_NAME: {settings.DB_NAME}")
    print(f"   JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
    print(f"   JWT_EXPIRATION_MINUTES: {settings.JWT_EXPIRATION_MINUTES}")
except Exception as e:
    print(f"❌ Erro na configuração: {e}")
```

Execute:
```bash
python validate_config.py
```

---

## 🔒 Boas Práticas de Segurança

### ✅ Faça:
- Use variáveis de ambiente para dados sensíveis
- Gere chaves JWT únicas e fortes para cada ambiente
- Nunca commit o arquivo `.env` no Git
- Use valores diferentes para desenvolvimento e produção
- Rotacione as chaves JWT periodicamente

### ❌ Não Faça:
- Não hardcode credenciais no código
- Não use chaves JWT padrão em produção
- Não compartilhe o arquivo `.env`
- Não use senhas fracas no banco de dados

---

## 📁 Arquivos de Configuração do Projeto

| Arquivo | Finalidade |
|---------|------------|
| `.env` | Variáveis de ambiente (não versionado) |
| `pyproject.toml` | Configuração do Ruff e Taskipy |
| `alembic.ini` | Configuração de migrações |
| `mkdocs.yml` | Configuração da documentação |

---

## 🐛 Solução de Problemas

### Erro: "Settings not found"
Verifique se o arquivo `.env` está na raiz do projeto e se todas as variáveis obrigatórias estão presentes.

### Erro: "Could not connect to database"
- Verifique se o MySQL está rodando
- Confirme as credenciais no `.env`
- Teste a conexão manualmente:
  ```bash
  mysql -u car_api_user -p -h localhost car_api
  ```

### Erro: "Invalid JWT secret"
Certifique-se de que `JWT_SECRET_KEY` tem pelo menos 32 caracteres e use apenas caracteres ASCII.

---

## 📚 Próximos Passos

Com a configuração concluída:

1. [Guidelines e Padrões](guidelines.md) - Conheça as convenções do projeto
2. [API Endpoints](api-endpoints.md) - Explore a API
3. [Autenticação](authentication.md) - Entenda o sistema de segurança

---

**Importante:** O arquivo `.env` está listado no `.gitignore` e não deve ser versionado.
