# Deployment Guide

Complete guide for deploying the Citizen Journalism Platform to production.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Production Environment Setup](#production-environment-setup)
3. [Deployment Options](#deployment-options)
4. [Mobile App Deployment](#mobile-app-deployment)
5. [Post-Deployment](#post-deployment)

---

## Quick Start

### Prerequisites

- **Backend**: Python 3.11+, PostgreSQL 14+, Redis 7+
- **Frontend**: Node.js 18+, npm 9+
- **Infrastructure**: Docker (optional), SSL certificate
- **Services**: AWS S3 (for media), Stripe account, SMTP server

### Environment Variables Checklist

Before deployment, ensure you have:

- [ ] Database credentials (PostgreSQL)
- [ ] Redis connection URL
- [ ] Secret keys (generate strong random keys)
- [ ] Stripe API keys (production)
- [ ] Email/SMTP credentials
- [ ] AWS S3 credentials (for file uploads)
- [ ] Domain name and SSL certificate
- [ ] CORS origins configured

---

## Production Environment Setup

### 1. Backend Deployment

#### Option A: Traditional VPS (DigitalOcean, AWS EC2, Linode)

**Step 1: Server Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis
sudo apt install redis-server

# Install Nginx (reverse proxy)
sudo apt install nginx

# Install Certbot (SSL)
sudo apt install certbot python3-certbot-nginx
```

**Step 2: Database Setup**

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE citizen_journalism;
CREATE USER cj_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE citizen_journalism TO cj_user;
\q
```

**Step 3: Application Setup**

```bash
# Clone repository
cd /var/www
sudo git clone https://github.com/yourusername/media.git
cd media/backend

# Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create production .env file
sudo nano .env
```

**Production .env file:**

```env
# Production Environment
DEMO_MODE=False
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Security - CHANGE THESE!
SECRET_KEY=your-256-bit-secret-key-here-use-openssl-rand-base64-32
JWT_SECRET_KEY=your-jwt-secret-key-here-use-openssl-rand-base64-32

# Database
DATABASE_URL=postgresql+asyncpg://cj_user:your_secure_password@localhost:5432/citizen_journalism

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS - Your production domain
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Stripe (Production Keys)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# Email (SMTP)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USERNAME=apikey
EMAIL_PASSWORD=your_sendgrid_api_key
EMAIL_FROM=noreply@yourdomain.com

# AWS S3 (for media uploads)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=citizen-journalism-media
AWS_REGION=us-east-1

# API Configuration
API_V1_PREFIX=/api/v1

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Step 4: Run Database Migrations**

```bash
# Install dependencies and run migrations
uv sync
uv run alembic upgrade head
```

**Step 5: Create Systemd Service**

```bash
sudo nano /etc/systemd/system/cj-backend.service
```

```ini
[Unit]
Description=Citizen Journalism Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/media/backend
Environment="PATH=/var/www/media/backend/.venv/bin"
ExecStart=/root/.local/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Step 6: Start Backend Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable cj-backend
sudo systemctl start cj-backend
sudo systemctl status cj-backend
```

**Step 7: Configure Nginx**

```bash
sudo nano /etc/nginx/sites-available/citizen-journalism
```

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    client_max_body_size 50M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/citizen-journalism /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com
```

#### Option B: Docker Deployment

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: citizen_journalism
      POSTGRES_USER: cj_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cj_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

volumes:
  postgres_data:
  redis_data:
```

**Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application
COPY . .

# Run migrations on startup
CMD uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Deploy with Docker:**

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

#### Option C: Platform-as-a-Service (Heroku, Railway, Render)

**For Render.com (Recommended):**

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: cj-backend
    env: python
    buildCommand: "pip install uv && uv sync"
    startCommand: "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4"
    envVars:
      - key: DEMO_MODE
        value: false
      - key: DATABASE_URL
        fromDatabase:
          name: citizen-journalism-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: citizen-journalism-redis
          type: redis
          property: connectionString

databases:
  - name: citizen-journalism-db
    databaseName: citizen_journalism
    user: cj_user

  - name: citizen-journalism-redis
    type: redis
```

2. Connect GitHub repository
3. Add environment variables in Render dashboard
4. Deploy

---

### 2. Frontend Deployment

#### Option A: Static Hosting (Netlify, Vercel, AWS S3 + CloudFront)

**Build for Production:**

```bash
cd frontend

# Update .env.production
echo "REACT_APP_API_URL=https://api.yourdomain.com/api/v1" > .env.production
echo "REACT_APP_STRIPE_PUBLIC_KEY=pk_live_xxx" >> .env.production

# Build
npm run build

# Deploy to Netlify
npx netlify-cli deploy --prod --dir=build

# Or deploy to Vercel
npx vercel --prod
```

**Netlify Configuration (_redirects file):**

```
# Redirect all routes to index.html for client-side routing
/*    /index.html   200

# API proxy (optional)
/api/*  https://api.yourdomain.com/api/:splat  200
```

**Vercel Configuration (vercel.json):**

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://api.yourdomain.com/api/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

#### Option B: Nginx (Same Server as Backend)

```nginx
# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/media/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## Deployment Options Comparison

| Platform | Cost | Ease | Scalability | Best For |
|----------|------|------|-------------|----------|
| **VPS (DigitalOcean)** | $12-50/mo | Medium | High | Full control, custom needs |
| **Render** | $7-25/mo | Easy | High | Startups, quick deployment |
| **Railway** | $5-20/mo | Easy | Medium | Development, small apps |
| **AWS (EC2+RDS)** | $30-100/mo | Hard | Very High | Enterprise, heavy traffic |
| **Heroku** | $25-50/mo | Easy | High | Quick MVP, prototypes |
| **Docker + VPS** | $12-30/mo | Medium | High | Containerized, reproducible |

---

## Mobile App Deployment

See [APP_STORE.md](./APP_STORE.md) for detailed mobile deployment guides.

---

## Post-Deployment

### 1. Monitoring Setup

**Install Sentry (Error Tracking):**

```bash
# Backend
uv add sentry-sdk[fastapi]

# Frontend
npm install @sentry/react
```

**Configure Sentry:**

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1,
)
```

### 2. Performance Monitoring

- Set up uptime monitoring (UptimeRobot, Pingdom)
- Configure application performance monitoring (New Relic, DataDog)
- Enable database query logging
- Set up log aggregation (Papertrail, LogDNA)

### 3. Backup Strategy

```bash
# Automated PostgreSQL backups
0 2 * * * pg_dump citizen_journalism | gzip > /backups/db-$(date +\%Y\%m\%d).sql.gz

# Backup rotation (keep 30 days)
find /backups -name "db-*.sql.gz" -mtime +30 -delete
```

### 4. Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Environment variables secured (not in git)
- [ ] Database has strong passwords
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers configured
- [ ] Dependencies updated regularly
- [ ] API authentication working
- [ ] File upload size limits set
- [ ] Input validation enabled

### 5. Performance Checklist

- [ ] Database indexes created
- [ ] Redis caching configured
- [ ] CDN setup for static assets
- [ ] Image optimization enabled
- [ ] Gzip compression enabled
- [ ] HTTP/2 enabled
- [ ] Database connection pooling configured
- [ ] API response caching implemented

---

## Scaling Considerations

### When to Scale

- CPU usage consistently > 70%
- Memory usage > 80%
- Database connections maxed out
- Response times > 500ms
- Error rate > 1%

### Horizontal Scaling

```bash
# Run multiple backend workers
uvicorn app.main:app --workers 8

# Or use Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Database Scaling

- Enable read replicas for heavy read workloads
- Implement database connection pooling (PgBouncer)
- Consider managed database services (AWS RDS, DigitalOcean Managed DB)

### Caching Strategy

- Redis for session storage
- Cache API responses with short TTL
- Use CDN for static assets
- Implement browser caching headers

---

## CI/CD Pipeline

**GitHub Actions (.github/workflows/deploy.yml):**

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
      - name: Run tests
        run: |
          cd backend
          pip install uv
          uv run pytest

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
            cd /var/www/media
            git pull origin main
            systemctl restart cj-backend
```

---

## Emergency Procedures

### Database Restore

```bash
# Restore from backup
gunzip < /backups/db-20250115.sql.gz | psql citizen_journalism
```

### Rollback Deployment

```bash
# Rollback to previous commit
cd /var/www/media
git reset --hard HEAD~1
systemctl restart cj-backend
```

### High Traffic Emergency

```bash
# Increase workers temporarily
sudo systemctl stop cj-backend
# Edit service file to increase workers
sudo systemctl start cj-backend

# Enable aggressive caching
# Add Redis caching to all read endpoints
```

---

## Support

For issues or questions:
- Check logs: `sudo journalctl -u cj-backend -f`
- Database logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`
- Nginx logs: `sudo tail -f /var/log/nginx/error.log`

See also:
- [SECURITY.md](./SECURITY.md) - Security best practices
- [PERFORMANCE.md](./PERFORMANCE.md) - Performance optimization
- [APP_STORE.md](./APP_STORE.md) - Mobile app deployment
