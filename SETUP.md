# Citizen Journalism Platform - Setup Guide

## 🔧 Required Configuration

Before running the platform, you MUST configure the following API keys and credentials.

### 1. Generate Secret Keys

Generate secure random keys for your application:

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Stripe Payment Integration

**REQUIRED for Payment Features (Phase 2)**

1. Create a Stripe account at https://dashboard.stripe.com/register
2. Get your API keys from https://dashboard.stripe.com/apikeys
3. For testing, use TEST mode keys (they start with `sk_test_` and `pk_test_`)

```bash
# In your .env file:
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
```

4. Set up webhooks:
   - Go to https://dashboard.stripe.com/webhooks
   - Add endpoint: `https://your-domain.com/api/v1/payments/webhook`
   - Copy the signing secret

```bash
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
```

### 3. AI Services (Optional but Recommended)

**REQUIRED for AI Article Generation (Phase 2)**

Choose ONE of the following:

#### Option A: OpenAI (GPT-4)

1. Create account at https://platform.openai.com/
2. Generate API key at https://platform.openai.com/api-keys
3. Add credit to your account

```bash
OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE
```

#### Option B: Anthropic (Claude)

1. Create account at https://console.anthropic.com/
2. Generate API key
3. Add credit to your account

```bash
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_API_KEY_HERE
```

### 4. Email Service Configuration

**REQUIRED for Email Notifications (Phase 2)**

#### Using Gmail (Recommended for Development)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
EMAIL_FROM=noreply@yourdomain.com
EMAIL_USE_TLS=True
```

#### Using SendGrid (Recommended for Production)

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USERNAME=apikey
EMAIL_PASSWORD=your-sendgrid-api-key
EMAIL_FROM=noreply@yourdomain.com
```

### 5. AWS S3 for File Storage (Optional)

**REQUIRED for Production File Uploads**

1. Create AWS account at https://aws.amazon.com/
2. Create S3 bucket
3. Create IAM user with S3 access
4. Generate access keys

```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

### 6. Sentry for Error Monitoring (Optional)

**RECOMMENDED for Production**

1. Create account at https://sentry.io/
2. Create new project
3. Copy DSN

```bash
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
```

## 📝 Complete .env File Example

Create a `.env` file in the root directory:

```bash
# REQUIRED - Generate these
SECRET_KEY=your-generated-secret-key-here
JWT_SECRET_KEY=your-generated-jwt-secret-key-here

# Database (using Docker Compose defaults)
POSTGRES_USER=citizen_user
POSTGRES_PASSWORD=citizen_pass
POSTGRES_DB=citizen_journalism
DATABASE_URL=postgresql://citizen_user:citizen_pass@localhost:5432/citizen_journalism

# Redis
REDIS_URL=redis://localhost:6379/0

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Stripe (REQUIRED for payments) - UPDATE THESE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# AI Services (choose one) - UPDATE THESE
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
# OR
ANTHROPIC_API_KEY=sk-ant-YOUR_ANTHROPIC_KEY_HERE

# Email (REQUIRED for notifications) - UPDATE THESE
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com
EMAIL_USE_TLS=True

# AWS S3 (optional for development) - UPDATE IF USING
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# Sentry (optional) - UPDATE IF USING
SENTRY_DSN=https://your-dsn@sentry.io/project

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Application Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

###2. Start Services with Docker

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose logs -f
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed database with dummy data
docker-compose exec backend python -m app.scripts.seed_data
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs

### 5. Login with Demo Credentials

```
Admin:
Email: admin@example.com
Password: admin123!@#

Writer 1:
Email: writer1@example.com
Password: Writer123!@#

Writer 2:
Email: writer2@example.com
Password: Writer123!@#

Reader:
Email: reader@example.com
Password: Reader123!@#
```

## 🔍 Troubleshooting

### Cannot Connect to Database

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart service
docker-compose restart postgres
```

### Email Not Sending

1. Verify Gmail App Password is correct (16 characters, no spaces)
2. Check 2FA is enabled on Gmail
3. Look for error messages in backend logs:
   ```bash
   docker-compose logs backend
   ```

### Stripe Errors

1. Ensure you're using TEST mode keys for development
2. Keys should start with `sk_test_` and `pk_test_`
3. Webhook secret starts with `whsec_`

### AI Service Not Working

1. Check API key is correctly set in .env
2. Verify you have credits in your AI provider account
3. Check backend logs for specific error messages

## 📦 Installing Dependencies Locally (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed database
python -m app.scripts.seed_data

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create frontend .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend
npm test -- --coverage

# View coverage
open coverage/lcov-report/index.html
```

## 🔒 Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY and JWT_SECRET_KEY
- [ ] Use production Stripe keys (sk_live_)
- [ ] Set DEBUG=False
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Enable Sentry error monitoring
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Review all environment variables

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs [service-name]`
2. Verify all API keys are correctly configured
3. Ensure all services are running: `docker-compose ps`
4. Review the troubleshooting section above

## 🎉 You're Ready!

Once you've completed the setup, you can:

1. Browse articles at http://localhost:3000/articles
2. Vote on topics at http://localhost:3000/topics
3. Login and write articles
4. Test AI article generation
5. Explore the writer dashboard

Enjoy building the future of citizen journalism! 🚀
