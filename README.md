# Citizen Journalism Platform

A secure, scalable citizen journalism platform where readers vote on important topics and writers create content based on community interest. The platform supports dual user modes (reader/writer), comprehensive rating systems, and monetization options.

## 🚀 Quick Start with Demo Mode (No Setup Required!)

**Want to try it instantly without databases or API keys?**

```bash
# 1. Copy demo environment
cp .env.demo .env

# 2. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Start backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# 4. Start frontend (in another terminal)
cd frontend
npm install
npm start

# 5. Login at http://localhost:3000
# Use: reader@demo.com / password
```

**👉 See [DEMO_MODE.md](./DEMO_MODE.md) for complete demo mode guide.**

Demo mode works **without**:
- PostgreSQL, Redis, or Elasticsearch
- Stripe account or payment setup
- Email server configuration
- AWS S3 or cloud storage

---

## ⚠️ Production Setup: Configuration Required

**For production or full-featured development, you need to configure:**

👉 **See [SETUP.md](./SETUP.md) for detailed configuration instructions.**

Required for production:
- **Stripe API Keys** (for payment processing)
- **PostgreSQL Database** (for data persistence)
- **Email SMTP Settings** (for notifications)
- **Secret Keys** (for security)

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+) with async/await patterns
- PostgreSQL 15+ for primary database
- Redis for caching and session management
- Elasticsearch for article search
- Celery for background tasks
- Stripe for payment processing

**Frontend:**
- React 18+ with TypeScript
- Tailwind CSS for styling
- React Query for data fetching
- React Router for navigation
- Zustand for state management

**Infrastructure:**
- Docker & Docker Compose for containerization
- Nginx for reverse proxy (production)
- AWS S3 for file storage
- Sentry for error tracking

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (if running locally)
- Redis (if running locally)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd media
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update the following critical values:
- `SECRET_KEY` - Generate a secure random key
- `JWT_SECRET_KEY` - Generate another secure random key
- `STRIPE_SECRET_KEY` - Your Stripe secret key
- `OPENAI_API_KEY` - Your OpenAI API key (optional)
- Email configuration (SMTP settings)

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

The following services will be available:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Elasticsearch: localhost:9200

### 4. Run Database Migrations

```bash
# Access the backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head
```

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage
```

## 📁 Project Structure

```
citizen-journalism/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── migrations/         # Alembic migrations
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API services
│   │   └── store/          # State management
│   └── package.json        # Node dependencies
└── docker-compose.yml      # Docker orchestration
```

## 🔑 Key Features

### Phase 1: MVP (Current)
- ✅ User authentication with JWT
- ✅ Basic user profiles
- ✅ Topic voting system (in progress)
- ✅ Article CRUD operations (in progress)
- ✅ Rating and review system (in progress)

### Phase 2: Enhanced Features
- ⏳ AI article generation
- ⏳ Payment integration with Stripe
- ⏳ Advanced analytics
- ⏳ Email notifications
- ⏳ Mobile-responsive UI

### Phase 3: Production Ready
- ⏳ Performance optimization
- ⏳ Security hardening
- ⏳ Monitoring and logging
- ⏳ CI/CD pipeline
- ⏳ Production deployment

## 🔐 Security Features

- **Authentication:**
  - JWT tokens with refresh mechanism
  - 2FA support with TOTP
  - OAuth2 integration (planned)

- **Password Security:**
  - Argon2id hashing
  - Password complexity requirements
  - Account lockout after failed attempts
  - Password history tracking

- **API Security:**
  - Rate limiting
  - CORS protection
  - Request validation with Pydantic
  - SQL injection prevention

## 📊 Database Schema

Key tables:
- `users` - User accounts with security features
- `articles` - Article content and metadata
- `topics` - Community voting topics
- `ratings` - Article ratings and reviews
- `subscriptions` - Payment subscriptions
- `payments` - Transaction records

See `/backend/app/models/` for complete schema definitions.

## 🎯 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/profile` - Get current user profile
- `PUT /api/v1/users/profile` - Update profile
- `POST /api/v1/users/toggle-mode` - Toggle reader/writer mode

### Articles
- `GET /api/v1/articles` - List articles
- `POST /api/v1/articles` - Create article
- `GET /api/v1/articles/{id}` - Get article
- `PUT /api/v1/articles/{id}` - Update article
- `DELETE /api/v1/articles/{id}` - Delete article

### Topics
- `GET /api/v1/topics` - List topics
- `GET /api/v1/topics/trending` - Get trending topics
- `POST /api/v1/topics` - Create topic
- `POST /api/v1/topics/{id}/vote` - Vote on topic

### Payments
- `POST /api/v1/payments/subscribe` - Create subscription
- `POST /api/v1/payments/donate` - Make donation
- `GET /api/v1/payments/earnings` - Get earnings

### AI
- `POST /api/v1/ai/generate-article` - Generate article with AI
- `POST /api/v1/ai/improve-draft` - Improve draft
- `POST /api/v1/ai/summarize` - Summarize article
- `POST /api/v1/ai/fact-check` - Fact-check content

Full API documentation available at: http://localhost:8000/api/docs

## 🧪 Testing

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Testing
```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## 📈 Performance Optimization

- Database query optimization with indexes
- Redis caching for frequently accessed data
- CDN for static assets
- Image optimization and lazy loading
- Code splitting in frontend
- Database connection pooling

## 🚀 Deployment

### 📚 Complete Documentation

| Document | Description |
|----------|-------------|
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Complete production deployment guide (VPS, Docker, PaaS, scaling) |
| **[APP_STORE.md](./APP_STORE.md)** | Mobile app deployment (iOS App Store, Google Play Store, PWA) |
| **[SECURITY.md](./SECURITY.md)** | Security requirements, best practices, and compliance checklist |
| **[PERFORMANCE.md](./PERFORMANCE.md)** | Performance optimization, monitoring, and load testing |

### Production Checklist

**Critical Security (see [SECURITY.md](./SECURITY.md)):**
- [ ] Update `SECRET_KEY` and `JWT_SECRET_KEY` to random values
- [ ] Set `DEBUG=False` and `ENVIRONMENT=production`
- [ ] Configure production database with strong password
- [ ] Set up SSL/TLS certificates (Let's Encrypt)
- [ ] Configure CORS to allow only production domains
- [ ] Enable rate limiting on all endpoints
- [ ] Configure security headers (CSP, HSTS, etc.)

**Infrastructure (see [DEPLOYMENT.md](./DEPLOYMENT.md)):**
- [ ] Set up monitoring (Sentry for errors)
- [ ] Configure email service (SendGrid, SES)
- [ ] Set up backup strategy (daily PostgreSQL dumps)
- [ ] Configure CDN for static files (CloudFlare)
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure firewall (UFW) and fail2ban

**Performance (see [PERFORMANCE.md](./PERFORMANCE.md)):**
- [ ] Add database indexes on all foreign keys
- [ ] Configure Redis caching
- [ ] Enable Gzip compression
- [ ] Set up connection pooling
- [ ] Implement pagination on all lists

### Deployment Options

| Platform | Cost | Ease | Best For |
|----------|------|------|----------|
| **Render** | $7-25/mo | ⭐ Easy | Quick production deploy |
| **Railway** | $5-20/mo | ⭐ Easy | Small projects |
| **DigitalOcean** | $12-50/mo | ⭐⭐ Medium | Full control |
| **AWS** | $30-100/mo | ⭐⭐⭐ Hard | Enterprise scale |

### Mobile Apps

Deploy to iOS and Android app stores using **Capacitor**:

```bash
cd frontend
npm install @capacitor/core @capacitor/cli @capacitor/ios @capacitor/android
npx cap init
npx cap add ios
npx cap add android
npm run build
npx cap sync
```

**Costs:**
- Apple Developer: $99/year
- Google Play: $25 one-time

See [APP_STORE.md](./APP_STORE.md) for complete mobile deployment guide

## 📄 License

This project is licensed under the MIT License.

## 🗺️ Roadmap

- **Q1 2024:** MVP launch with core features
- **Q2 2024:** AI integration and payments
- **Q3 2024:** Mobile app development
- **Q4 2024:** Advanced analytics and reporting

---

**Built with ❤️ for the citizen journalism community**