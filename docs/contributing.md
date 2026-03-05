# Contribuição

Este guia explica como contribuir com o projeto CAR API. Seja bem-vindo(a) para ajudar no desenvolvimento, documentação, testes ou reportando problemas.

---

## 🤝 Como Contribuir

Existem várias formas de contribuir com o projeto:

| Tipo | Descrição |
|------|-----------|
| 🐛 **Bug Reports** | Reportar bugs e problemas |
| ✨ **Feature Requests** | Sugerir novas funcionalidades |
| 📝 **Documentação** | Melhorar ou criar documentação |
| 💻 **Código** | Implementar features ou corrigir bugs |
| 🧪 **Testes** | Escrever ou melhorar testes |
| 🔍 **Code Review** | Revisar pull requests de outros |

---

## 📋 Fluxo de Contribuição

### 1. Fork do Repositório

```bash
# Clique em "Fork" no GitHub ou use a CLI
gh repo fork JaksonBernardo/fast-api-car
```

### 2. Clone Seu Fork

```bash
git clone https://github.com/JaksonBernardo/fast-api-car.git
cd fast-api-car
```

### 3. Configure Upstream

```bash
# Adicione o repositório original como remote
git remote add upstream https://github.com/JaksonBernardo/fast-api-car.git

# Verifique os remotes
git remote -v
```

### 4. Crie uma Branch

```bash
# Sempre crie branches a partir da main atualizada
git checkout main
git pull upstream main

# Crie sua branch
git checkout -b feature/minha-feature
# ou
git checkout -b fix/correcao-do-bug
```

### 5. Faça Suas Mudanças

```bash
# Edite os arquivos necessários
# ...

# Verifique o status
git status

# Adicione as mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: adicionar nova funcionalidade de busca"
```

### 6. Mantenha Sua Branch Atualizada

```bash
# Rebase com a main mais recente
git fetch upstream
git rebase upstream/main
```

### 7. Push para Seu Fork

```bash
git push origin feature/minha-feature
```

### 8. Crie um Pull Request

```bash
# Via GitHub
# 1. Acesse https://github.com/JaksonBernardo/fast-api-car
# 2. Clique em "Pull requests"
# 3. Clique em "New pull request"
# 4. Selecione sua branch
# 5. Preencha o template
# 6. Envie

# Via GitHub CLI
gh pr create --title "feat: adicionar nova funcionalidade" --body "Descrição das mudanças"
```

---

## 📝 Padrões de Commit

O projeto utiliza **Conventional Commits** para padronizar mensagens de commit.

### Estrutura

```
<tipo>(<escopo>): <descrição curta>

<descrição detalhada (opcional)>
```

### Tipos de Commit

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(cars): adicionar filtro por ano` |
| `fix` | Correção de bug | `fix(auth): corrigir validação de token` |
| `docs` | Documentação | `docs: atualizar README` |
| `style` | Formatação/código | `style: formatar código com ruff` |
| `refactor` | Refatoração | `refactor(users): simplificar service` |
| `test` | Testes | `test: adicionar testes de usuário` |
| `chore` | Configuração/manutenção | `chore: atualizar dependências` |
| `perf` | Performance | `perf: otimizar query de listagem` |
| `ci` | CI/CD | `ci: configurar GitHub Actions` |

### Exemplos de Mensagens

```bash
# Feature
git commit -m "feat(cars): adicionar endpoint de busca por placa"

# Fix
git commit -m "fix(auth): corrigir expiração do token JWT"

# Docs
git commit -m "docs: adicionar documentação de autenticação"

# Refactor
git commit -m "refactor(repositories): extrair método de validação"

# Múltiplas linhas
git commit -m "feat(users): adicionar paginação na listagem

- Implementar parâmetros offset e limit
- Adicionar validação de valores máximos
- Atualizar documentação da API"
```

---

## 🏷️ Padrões de Branch

| Prefixo | Descrição | Exemplo |
|---------|-----------|---------|
| `feature/` | Nova funcionalidade | `feature/user-registration` |
| `fix/` | Correção de bug | `fix/login-validation` |
| `docs/` | Documentação | `docs/api-endpoints` |
| `refactor/` | Refatoração | `refactor/database-queries` |
| `test/` | Testes | `test/user-service` |
| `chore/` | Tarefas gerais | `chore/update-deps` |
| `hotfix/` | Correção urgente | `hotfix/security-patch` |

---

## ✅ Checklist Antes de Enviar PR

Antes de criar um Pull Request, verifique:

- [ ] Código formatado (`task format`)
- [ ] Linter sem erros (`task lint`)
- [ ] Testes passando (`pytest`)
- [ ] Type hints adicionados
- [ ] Docstrings em funções públicas
- [ ] Migrações criadas (se aplicável)
- [ ] Documentação atualizada (se aplicável)
- [ ] Mensagem de commit no padrão
- [ ] Branch atualizada com a main

---

## 📐 Guidelines de Código

### Python

```python
# ✅ Use type hints
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Obtém usuário por ID."""
    ...

# ✅ Use aspas simples
message = 'Usuário criado com sucesso'

# ✅ Siga PEP 8
def function_name(param: str) -> str:
    ...
```

### SQL/Database

```python
# ✅ Use eager loading para evitar N+1
users = await db.execute(
    select(User).options(selectinload(User.cars))
)

# ✅ Use transações adequadamente
async with db.begin():
    await create_user(...)
    await create_profile(...)
```

### API Endpoints

```python
# ✅ Documente endpoints
@user_routers.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Criar um usuário',
    description='Registra um novo usuário no sistema',
)
async def create_user(...):
    ...
```

---

## 🐛 Reportando Bugs

### Template de Bug Report

```markdown
## Descrição
Descrição clara do bug.

## Passos para Reproduzir
1. Ir para '...'
2. Clicar em '...'
3. Ver erro '...'

## Comportamento Esperado
O que deveria acontecer.

## Comportamento Atual
O que está acontecendo.

## Screenshots
Se aplicável, adicione screenshots.

## Ambiente
- OS: [Windows, Linux, macOS]
- Python: [3.10, 3.11]
- Versão da API: [1.0.0]

## Logs
```
Cole logs relevantes aqui
```

## Informações Adicionais
Qualquer outra informação relevante.
```

### Onde Reportar

- **GitHub Issues:** https://github.com/JaksonBernardo/fast-api-car/issues

---

## ✨ Sugestão de Features

### Template de Feature Request

```markdown
## Problema Relacionado
Existe um problema que esta feature resolve?

## Solução Proposta
Descreva a solução desejada.

## Alternativas Consideradas
Quais alternativas você considerou?

## Exemplo de Uso
```python
# Como a feature seria usada
```

## Informações Adicionais
Contexto adicional sobre a feature.
```

---

## 📝 Contribuindo com Documentação

### Estrutura de Documentos

```markdown
# Título do Documento

Breve introdução.

## Seção 1
Conteúdo da seção.

### Subseção
Mais detalhes.

## Seção 2
Outro conteúdo.

## Referências
Links e referências.
```

### Dicas

- Use português brasileiro (pt-BR)
- Seja claro e conciso
- Inclua exemplos de código quando aplicável
- Use formatação Markdown adequada
- Revise ortografia e gramática

---

## 🧪 Contribuindo com Testes

### Escrevendo Testes

```python
import pytest


@pytest.mark.asyncio
async def test_feature_success(client):
    """Testa funcionalidade com sucesso."""
    # Arrange
    data = {'key': 'value'}
    
    # Act
    response = await client.post('/api/endpoint', json=data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()['key'] == 'value'


@pytest.mark.asyncio
async def test_feature_failure(client):
    """Testa falha da funcionalidade."""
    # Arrange
    data = {'key': ''}  # Inválido
    
    # Act
    response = await client.post('/api/endpoint', json=data)
    
    # Assert
    assert response.status_code == 422
```

### Cobertura de Testes

- Novas features devem ter testes
- Bug fixes devem incluir testes regressivos
- Mantenha cobertura acima de 80%

---

## 🔍 Code Review

### O que os Mantenedores Avaliam

| Critério | Descrição |
|----------|-----------|
| **Funcionalidade** | O código funciona como esperado? |
| **Qualidade** | O código segue os padrões do projeto? |
| **Testes** | Existem testes adequados? |
| **Documentação** | A documentação foi atualizada? |
| **Performance** | O código é eficiente? |
| **Segurança** | Não há vulnerabilidades introduzidas? |

### Respondendo a Feedback

```bash
# Faça as correções solicitadas
# ...

# Commit as correções
git add .
git commit -m "fix: corrigir comentários do review"

# Push (o PR será atualizado automaticamente)
git push origin feature/minha-feature
```

---

## 🏆 Reconhecimento

Contribuidores serão reconhecidos:

- Menção no CHANGELOG
- Lista de contribuidores no README
- Badge de contribuidor (se aplicável)

---

## 📞 Comunicação

### Canais

| Canal | Finalidade |
|-------|------------|
| **GitHub Issues** | Bugs e features |
| **GitHub Discussions** | Discussões gerais |
| **Email** | Questões privadas |

### Etiqueta

- Seja respeitoso e profissional
- Use português ou inglês
- Seja claro e objetivo
- Agradeça pelo tempo dos mantenedores

---

## 📜 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

## 🙏 Obrigado!

Agradecemos por contribuir com a CAR API! Sua ajuda torna o projeto melhor para todos.

---

**Dúvidas?** Abra uma issue ou entre em contato com os mantenedores.
