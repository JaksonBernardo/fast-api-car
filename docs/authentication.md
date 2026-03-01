# Autenticação e Segurança

Este documento descreve o sistema de autenticação e segurança implementado na CAR API, incluindo JWT, hash de senhas e controle de permissões.

---

## 🔐 Visão Geral

A CAR API utiliza um sistema de autenticação baseado em **JWT (JSON Web Tokens)** combinado com **Argon2** para hash de senhas, proporcionando segurança robusta para a aplicação.

### Componentes de Segurança

| Componente | Tecnologia | Finalidade |
|------------|------------|------------|
| **Autenticação** | JWT (JSON Web Tokens) | Tokens stateless para autenticação |
| **Hash de Senhas** | Argon2 | Algoritmo moderno e seguro |
| **Transporte** | HTTPS (recomendado) | Criptografia em trânsito |
| **Validação** | Pydantic | Validação de dados de entrada |

---

## 🔑 JWT (JSON Web Tokens)

### Estrutura do Token

O JWT é composto por três partes:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxIiwiZXhwIjoxNzQwODI4MDAwfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

| Parte | Descrição |
|-------|-----------|
| **Header** | Algoritmo e tipo de token |
| **Payload** | Dados (claims) do usuário |
| **Signature** | Assinatura para validação |

### Claims (Dados do Token)

```json
{
  "sub": "1",
  "exp": 1740828000
}
```

| Claim | Descrição |
|-------|-----------|
| `sub` | Subject - ID do usuário (string) |
| `exp` | Expiration - Timestamp de expiração |

### Configuração JWT

As configurações são definidas no arquivo `.env`:

```ini
# Chave secreta para assinar tokens
JWT_SECRET_KEY=sua_chave_secreta_muito_forte

# Algoritmo de assinatura
JWT_ALGORITHM=HS256

# Tempo de expiração em minutos
JWT_EXPIRATION_MINUTES=30
```

---

## 🔄 Fluxo de Autenticação

### 1. Login (Gerar Token)

```http
POST /api/auth/api/token
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Usar Token em Requisições

```http
GET /api/cars/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Refresh Token

```http
POST /api/auth/refresh_token
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Resposta:**
```json
{
  "access_token": "novo_token_atualizado...",
  "token_type": "bearer"
}
```

---

## 🔒 Hash de Senhas com Argon2

A CAR API utiliza **Argon2**, vencedor do Password Hashing Competition, considerado um dos algoritmos mais seguros atualmente.

### Características do Argon2

- ✅ Resistente a ataques de GPU/ASIC
- ✅ Usa memória intensiva para dificultar ataques
- ✅ Vencedor do Password Hashing Competition (2015)
- ✅ Recomendado por especialistas em segurança

### Implementação

```python
# car_api/core/security.py

from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Gera hash da senha usando Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Fluxo de Registro de Usuário

```mermaid
flowchart LR
    A[Senha em Texto Plano] --> B[get_password_hash]
    B --> C[Hash Argon2]
    C --> D[Salvar no Banco]
    
    E[Login: Senha + Hash] --> F[verify_password]
    F --> G{Senha Válida?}
    G -->|Sim| H[Autenticação OK]
    G -->|Não| I[Erro de Autenticação]
```

### Validações de Senha

```python
# car_api/schemas/users.py

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

**Recomendações para Senhas Fortes:**
- Mínimo de 8 caracteres (a API exige 6)
- Combine letras maiúsculas e minúsculas
- Inclua números e símbolos
- Evite senhas comuns

---

## 🛡️ Controle de Permissões

A API implementa controle de acesso baseado em propriedade (ownership).

### Tipos de Permissão

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| **Público** | Sem autenticação necessária | `POST /api/auth/api/token` |
| **Autenticado** | Requer token JWT válido | `GET /api/brands/` |
| **Owner (Dono)** | Requer ser o proprietário do recurso | `PUT /api/users/{id}` |

### Funções de Verificação

```python
# car_api/core/security.py


def verify_user_permission(current_user: User, user_id: int) -> None:
    """Verifica se usuário pode alterar outro usuário."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Você não tem permissão para alterar esse usuário',
        )


def verify_car_ownership(user: User, car_owner_id: int) -> None:
    """Verifica se usuário é dono do carro."""
    if user.id != car_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Você não tem permissão para acessar esse carro',
        )
```

### Uso em Endpoints

```python
# car_api/routers/users.py

@user_routers.delete('/{user_id}')
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await UserService.delete_user(
        db, user_id, current_user, verify_user_permission
    )
```

---

## 🔍 Implementação Técnica

### Dependência get_current_user

```python
# car_api/core/security.py

secutiry_http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(secutiry_http_bearer),
    db: AsyncSession = Depends(get_session),
) -> User:
    # 1. Extrair token do header
    payload = verify_token(credentials.credentials)
    
    # 2. Extrair user_id do payload
    user_id_str = payload.get('sub')
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Credenciais inválidas',
        )
    
    # 3. Converter para int
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Credenciais inválidas',
        )
    
    # 4. Buscar usuário no banco
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuário não encontrado',
        )
    
    return user
```

### Verificação de Token

```python
def verify_token(token: str) -> Dict:
    """Decodifica e valida token JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expirado',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token inválido',
            headers={'WWW-Authenticate': 'Bearer'},
        )
```

### Criação de Token

```python
def create_access_token(data: Dict) -> str:
    """Cria token JWT com expiração."""
    to_encode = data.copy()
    
    # Calcular expiração
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRATION_MINUTES
    )
    
    # Adicionar claim de expiração
    to_encode.update({'exp': expire})
    
    # Codificar token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )
    
    return encoded_jwt
```

---

## 🚨 Tratamento de Erros de Autenticação

### Códigos de Erro

| Código | Situação | Mensagem |
|--------|----------|----------|
| 401 | Token ausente | `Not authenticated` |
| 401 | Token expirado | `Token expirado` |
| 401 | Token inválido | `Token inválido` |
| 401 | Credenciais inválidas | `Email ou senha incorretos` |
| 403 | Sem permissão | `Você não tem permissão...` |
| 404 | Usuário não encontrado | `Usuário não encontrado` |

### Respostas de Erro

```json
// Token expirado
{
  "detail": "Token expirado"
}

// Token inválido
{
  "detail": "Token inválido"
}

// Credenciais inválidas
{
  "detail": "Email ou senha incorretos"
}

// Sem permissão
{
  "detail": "Você não tem permissão para acessar esse carro"
}
```

---

## 📋 Boas Práticas de Segurança

### ✅ Recomendações

1. **Use HTTPS em Produção**
   - Nunca transmita tokens JWT sobre HTTP não criptografado
   - Configure SSL/TLS no servidor

2. **Proteja a Chave Secreta**
   - Use chaves fortes (mínimo 32 caracteres)
   - Nunca commit chaves no repositório
   - Rotacione chaves periodicamente

3. **Tempo de Expiração Curto**
   - Tokens de acesso: 15-30 minutos
   - Implemente refresh token para renovação

4. **Valide Dados de Entrada**
   - Use schemas Pydantic
   - Valide tamanho e complexidade de senhas

5. **Rate Limiting**
   - Implemente limite de tentativas de login
   - Previne ataques de força bruta

6. **Logs de Segurança**
   - Registre tentativas de login falhas
   - Monitore atividades suspeitas

### ❌ O que Evitar

- Não armazene senhas em texto plano
- Não exponha JWT_SECRET_KEY em logs
- Não use tokens com expiração muito longa
- Não confie apenas no token para validações críticas
- Não ignore erros de validação de token

---

## 🔧 Exemplo de Uso no Cliente

### JavaScript/TypeScript (Fetch API)

```javascript
// Login
async function login(email, password) {
  const response = await fetch('/api/auth/api/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

// Requisição autenticada
async function getCars() {
  const token = localStorage.getItem('token');
  
  const response = await fetch('/api/cars/', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return response.json();
}

// Logout
function logout() {
  localStorage.removeItem('token');
}
```

### Python (Requests)

```python
import requests

BASE_URL = 'http://localhost:8000'

def login(email, password):
    response = requests.post(
        f'{BASE_URL}/api/auth/api/token',
        json={'email': email, 'password': password}
    )
    return response.json()['access_token']

def get_cars(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/cars/', headers=headers)
    return response.json()

# Uso
token = login('usuario@example.com', 'senha123')
cars = get_cars(token)
```

---

## 📊 Comparação de Algoritmos de Hash

| Algoritmo | Segurança | Performance | Recomendação |
|-----------|-----------|-------------|--------------|
| **Argon2** | ⭐⭐⭐⭐⭐ | Média | ✅ Recomendado |
| bcrypt | ⭐⭐⭐⭐ | Lenta | ✅ Aceitável |
| PBKDF2 | ⭐⭐⭐ | Média | ⚠️ Mínimo |
| SHA-256 | ⭐ | Rápida | ❌ Não usar |
| MD5 | ❌ | Rápida | ❌ Nunca usar |

---

## 🔗 Referências

- [RFC 7519 - JSON Web Tokens](https://tools.ietf.org/html/rfc7519)
- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [pwdlib Documentation](https://pwdlib.readthedocs.io/)

---

## 📚 Próximos Passos

Compreendida a autenticação:

1. [API Endpoints](api-endpoints.md) - Explore os endpoints
2. [Desenvolvimento](development.md) - Comece a desenvolver
3. [Deploy](deployment.md) - Prepare para produção

---

**Importante:** Sempre use HTTPS em produção para proteger tokens e dados sensíveis.
