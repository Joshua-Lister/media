# Demo Mode Guide

## What is Demo Mode?

Demo Mode allows you to run the Citizen Journalism Platform **without requiring**:
- PostgreSQL database
- Redis cache
- Elasticsearch
- Stripe payment account
- SMTP email server
- AWS S3 storage

This is perfect for:
- Quick testing and exploration
- Development without infrastructure setup
- Demonstrations and presentations
- Learning how the platform works

## Quick Start (60 seconds)

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Copy the demo environment file

```bash
cp .env.demo .env
```

### 3. Start the backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm start
```

### 5. Access the application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Demo Accounts

Demo mode comes with pre-configured accounts:

### Reader Account
- **Email**: `reader@demo.com`
- **Password**: `password`
- **Role**: Reader (can browse articles, vote on topics)

### Writer Account
- **Email**: `writer@demo.com`
- **Password**: `password`
- **Role**: Writer (can create articles, publish content)

## Features in Demo Mode

### ✅ What Works

- **Authentication**: Login/logout with demo accounts
- **Articles**: Browse, read, and view pre-seeded articles
- **Topics**: View trending topics and vote counts
- **User Profiles**: View reader and writer profiles
- **Navigation**: Full UI navigation and layout
- **API Testing**: All API endpoints work with mock data

### ⚠️ What's Simulated

- **Database**: Uses in-memory storage (data resets on restart)
- **Payments**: Stripe calls return mock data
- **Emails**: Email notifications are logged but not sent
- **File Storage**: Files are handled in-memory

### ❌ What Doesn't Work

- **Persistence**: All data is lost when you restart the server
- **Real Payments**: No actual payment processing
- **Email Delivery**: Emails are simulated only
- **File Uploads**: Limited file storage capabilities

## Configuration

Demo mode is configured via environment variables in `.env`:

```bash
# Enable demo mode
DEMO_MODE=True

# Optional: Adjust demo settings
DEBUG=True
LOG_LEVEL=INFO
```

All other configuration (database URLs, API keys, etc.) can be omitted when `DEMO_MODE=True`.

## Pre-seeded Data

Demo mode automatically includes:

### Users
- 1 demo reader
- 1 demo writer

### Articles
- 2 published articles on various topics
- Realistic view counts and metadata

### Topics
- 3 trending topics with vote counts
- Topics cover climate, government, and health

### Ratings
- Sample article ratings and reviews

## API Usage in Demo Mode

### Login Example

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "reader@demo.com",
    "password": "password"
  }'
```

### Get Articles Example

```bash
curl -X GET "http://localhost:8000/api/v1/articles" \
  -H "Authorization: Bearer <your-access-token>"
```

## Switching from Demo to Production

When you're ready to use real services:

1. **Create `.env` from `.env.example`**:
   ```bash
   cp .env.example .env
   ```

2. **Set `DEMO_MODE=False`**

3. **Configure real services**:
   - PostgreSQL database URL
   - Redis URL
   - Stripe API keys
   - Email SMTP settings
   - AWS S3 credentials

4. **Run database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Restart services**:
   ```bash
   docker-compose up -d
   ```

## Troubleshooting

### "Database not initialized" error
- Ensure `DEMO_MODE=True` in your `.env` file
- Restart the backend server

### Login doesn't work
- Use exact credentials: `reader@demo.com` / `password`
- Check that demo mode is enabled in config

### Data disappears
- This is expected! Demo mode uses in-memory storage
- Data resets every time you restart the backend

### API returns errors
- Check the API documentation at http://localhost:8000/api/docs
- Ensure you're using valid demo account tokens

## Limitations

### Data Persistence
Demo mode stores all data in memory. When the server restarts, all data returns to the initial seeded state. This includes:
- User registrations (not supported in demo mode)
- New articles
- New topics
- Votes and ratings

### Concurrent Users
Demo mode is designed for single-user testing. Multiple concurrent users may experience data conflicts.

### Performance
In-memory storage is fast but limited by RAM. Large datasets are not recommended in demo mode.

## Architecture Details

Demo mode implements:

### In-Memory Database (`demo_db.py`)
- Simple Python dictionaries for storage
- Pre-seeded with demo data
- Mimics database operations

### Demo Dependencies (`demo_deps.py`)
- Authentication without database queries
- JWT token validation
- Role-based access control

### Service Bypasses
- Payment service returns mock Stripe data
- Email service logs instead of sending
- File service uses memory storage

## Development with Demo Mode

Demo mode is excellent for:
- Frontend development
- API integration testing
- UI/UX iterations
- Feature demonstrations

To add your own demo data, edit:
```python
backend/app/core/demo_db.py
```

Look for the `_seed_demo_data()` method and add your custom data.

## Support

For issues or questions about demo mode:
1. Check this documentation
2. Review the API docs at http://localhost:8000/api/docs
3. Open an issue on GitHub

---

**Happy exploring! 🚀**
