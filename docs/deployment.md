# Deploy

Este guia descreve como implantar a CAR API em diferentes ambientes, desde servidores tradicionais até plataformas em nuvem.

---

## 📋 Pré-requisitos para Deploy

Antes de implantar, certifique-se de:

- [ ] Todos os testes passando
- [ ] Variáveis de ambiente de produção configuradas
- [ ] Banco de dados configurado
- [ ] Chaves JWT fortes geradas
- [ ] HTTPS configurado (recomendado)

---

## 🐳 Deploy com Docker

### Dockerfile

Crie um `Dockerfile` na raiz do projeto:

```dockerfile
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "car_api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mysql
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}
      - DATABASE_URL=mysql+aiomysql://${DB_USER}:${DB_PASSWORD}@mysql:3306/${DB_NAME}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION_MINUTES=30
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - car_api_network

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
      - MYSQL_DATABASE=${DB_NAME}
      - MYSQL_USER=${DB_USER}
      - MYSQL_PASSWORD=${DB_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - car_api_network

volumes:
  mysql_data:

networks:
  car_api_network:
    driver: bridge
```

### .env para Produção

```ini
# Banco de dados
DB_USER=car_api_prod
DB_PASSWORD=senha_forte_aleatoria_aqui
DB_NAME=car_api_prod
DB_ROOT_PASSWORD=senha_root_ainda_mais_forte

# JWT - Gere uma chave forte
JWT_SECRET_KEY=chave_secreta_gerada_com_openssl_rand_hex_32

# Outras configurações
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

### Comandos Docker

```bash
# Build das imagens
docker-compose build

# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Parar serviços
docker-compose down

# Parar e remover volumes (cuidado!)
docker-compose down -v

# Executar migrações
docker-compose exec api alembic upgrade head

# Ver status
docker-compose ps
```

---

## ☁️ Deploy em Plataformas Cloud

### AWS (Elastic Beanstalk)

#### 1. Instale o EB CLI

```bash
pip install awsebcli
```

#### 2. Inicialize o EB

```bash
eb init -p python-3.11 car-api --region us-east-1
```

#### 3. Configure o Ambiente

```bash
eb create production
```

#### 4. Defina Variáveis de Ambiente

```bash
eb setenv DB_HOST=seu-rds.amazonaws.com \
    DB_USER=car_api \
    DB_PASSWORD=senha \
    DB_NAME=car_api_prod \
    DATABASE_URL="mysql+aiomysql://car_api:senha@rds.amazonaws.com:3306/car_api_prod" \
    JWT_SECRET_KEY=sua_chave_secreta
```

#### 5. Deploy

```bash
eb deploy
```

---

### Google Cloud Run

#### 1. Build e Push da Imagem

```bash
# Build
docker build -t gcr.io/SEU_PROJETO/car-api:latest .

# Push
docker push gcr.io/SEU_PROJETO/car-api:latest
```

#### 2. Deploy no Cloud Run

```bash
gcloud run deploy car-api \
    --image gcr.io/SEU_PROJETO/car-api:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DB_HOST=IP_DO_MYSQL,\
DB_USER=car_api,\
DB_PASSWORD=senha,\
DATABASE_URL="mysql+aiomysql://car_api:senha@IP_DO_MYSQL:3306/car_api_prod",\
JWT_SECRET_KEY=sua_chave_secreta
```

---

### Heroku

#### 1. Instale Heroku CLI

```bash
# Windows (Chocolatey)
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### 2. Login e Criação

```bash
heroku login
heroku create car-api-prod
```

#### 3. Configure Variáveis

```bash
heroku config:set DB_HOST=seu-host.amazonaws.com
heroku config:set DB_USER=car_api
heroku config:set DB_PASSWORD=senha
heroku config:set DB_NAME=car_api_prod
heroku config:set DATABASE_URL="mysql+aiomysql://car_api:senha@host:3306/car_api_prod"
heroku config:set JWT_SECRET_KEY=sua_chave_secreta
```

#### 4. Deploy

```bash
git push heroku main
```

#### 5. Execute Migrações

```bash
heroku run alembic upgrade head
```

---

## 🖥️ Deploy em Servidor Linux (Ubuntu)

### 1. Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3.11 python3.11-venv python3-pip nginx mysql-server git

# Instalar dependências do MySQL
sudo apt install -y default-libmysqlclient-dev pkg-config
```

### 2. Configurar Banco de Dados

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE car_api_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'car_api'@'localhost' IDENTIFIED BY 'senha_forte';
GRANT ALL PRIVILEGES ON car_api_prod.* TO 'car_api'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Clonar e Configurar Projeto

```bash
# Criar usuário para a aplicação
sudo useradd -m -s /bin/bash car_api

# Clonar repositório
sudo -u car_api git clone https://github.com/JaksonBernardo/fast-api-car.git /home/car_api/car_api
cd /home/car_api/car_api

# Criar ambiente virtual
sudo -u car_api python3 -m venv venv
sudo -u car_api ./venv/bin/pip install --upgrade pip
sudo -u car_api ./venv/bin/pip install -r requirements.txt

# Criar arquivo .env
sudo -u car_api nano .env
```

### 4. Configurar Systemd Service

```bash
sudo nano /etc/systemd/system/car-api.service
```

```ini
[Unit]
Description=CAR API Gunicorn instance
After=network.target

[Service]
User=car_api
Group=www-data
WorkingDirectory=/home/car_api/car_api
ExecStart=/home/car_api/car_api/venv/bin/uvicorn car_api.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/car-api
```

```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/car-api /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### 6. Iniciar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar serviço
sudo systemctl start car-api
sudo systemctl enable car-api

# Ver status
sudo systemctl status car-api
```

### 7. Configurar SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.seudominio.com
```

---

## 🚀 Deploy com Gunicorn (Produção)

### Instalar Gunicorn

```bash
pip install gunicorn
```

### Executar com Gunicorn

```bash
gunicorn car_api.app:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 5
```

---

## 📊 Monitoramento e Logs

### Logs da Aplicação

```bash
# Docker
docker-compose logs -f api

# Systemd
sudo journalctl -u car-api -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Health Check

Adicione um endpoint de health check:

```python
# car_api/app.py

@app.get('/health', tags=['Health'])
async def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now()}
```

### Monitoramento

| Ferramenta | Finalidade |
|------------|------------|
| **Prometheus + Grafana** | Métricas e dashboards |
| **Sentry** | Error tracking |
| **New Relic** | APM completo |
| **Datadog** | Monitoramento cloud |

---

## 🔒 Checklist de Segurança para Produção

- [ ] HTTPS configurado com SSL válido
- [ ] Variáveis de ambiente seguras
- [ ] Chaves JWT fortes e únicas
- [ ] Banco de dados não exposto publicamente
- [ ] Firewall configurado (UFW/iptables)
- [ ] Rate limiting implementado
- [ ] Logs de segurança habilitados
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo
- [ ] Plano de rollback definido

---

## 🔄 CI/CD com GitHub Actions

### .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /home/car_api/car_api
            git pull origin main
            source venv/bin/activate
            pip install -r requirements.txt
            alembic upgrade head
            sudo systemctl restart car-api
```

---

## 📈 Otimização de Performance

### Workers

```bash
# Fórmula: (2 x núcleos) + 1
# Exemplo: 4 núcleos = 9 workers
gunicorn car_api.app:app --workers 9 --worker-class uvicorn.workers.UvicornWorker
```

### Cache

```python
# Adicionar cache headers
from fastapi.responses import Response

@app.get('/api/brands/')
async def get_brands():
    response = Response(...)
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response
```

### Database Pool

```python
# car_api/core/database.py

engine = create_async_engine(
    Settings().DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)
```

---

## 📚 Próximos Passos

Com o deploy realizado:

1. [Contribuição](contributing.md) - Como contribuir com o projeto
2. [Release Notes](release-notes.md) - Histórico de versões

---

**Importante:** Sempre teste o deploy em um ambiente de staging antes de produzir.
