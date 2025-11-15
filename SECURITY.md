# Security Guide

Complete security checklist and best practices for the Citizen Journalism Platform.

## Table of Contents

1. [Critical Security Requirements](#critical-security-requirements)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Protection](#data-protection)
4. [API Security](#api-security)
5. [Infrastructure Security](#infrastructure-security)
6. [Code Security](#code-security)
7. [Compliance & Privacy](#compliance--privacy)
8. [Security Monitoring](#security-monitoring)
9. [Incident Response](#incident-response)

---

## Critical Security Requirements

### ⚠️ MUST FIX BEFORE PRODUCTION

These are **critical** security issues that MUST be addressed before going live:

#### 1. Change All Default Secrets

**Current State (INSECURE):**
```env
SECRET_KEY=demo-secret-key-for-testing-only-do-not-use-in-production
JWT_SECRET_KEY=demo-jwt-secret-key-for-testing-only-do-not-use-in-production
```

**Fix:**
```bash
# Generate strong random secrets
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For JWT_SECRET_KEY
```

**Production .env:**
```env
SECRET_KEY=8xK9mP2vQ7wE3nR6tY1uI4oP0aS5dF8gH2jK9lM3nB5vC8xZ1wE4rT7y
JWT_SECRET_KEY=3nR6tY1uI4oP0aS5dF8gH2jK9lM3nB5vC8xZ1wE4rT7y8K9mP2vQ7w
```

**Why Critical:** Default secrets allow attackers to forge JWT tokens and session cookies.

---

#### 2. Disable Debug Mode

**Current State (INSECURE):**
```env
DEBUG=True
```

**Fix:**
```env
DEBUG=False
ENVIRONMENT=production
```

**Why Critical:** Debug mode exposes:
- Full stack traces with file paths
- Environment variables
- Database queries
- Internal server structure

---

#### 3. Configure Proper CORS

**Current State (INSECURE):**
```python
# Allowing all origins
BACKEND_CORS_ORIGINS=*
```

**Fix:**
```env
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Why Critical:** Prevents cross-site request forgery (CSRF) attacks from malicious websites.

---

#### 4. Enable HTTPS Only

**Backend Configuration:**
```python
# backend/app/core/config.py
SECURE_COOKIES = True  # Only send cookies over HTTPS
SECURE_HSTS = True     # Force HTTPS
```

**Nginx Configuration:**
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # ... rest of config
}
```

**Why Critical:** Without HTTPS, all traffic (including passwords) is sent in plain text.

---

#### 5. Secure Database Credentials

**Current State (INSECURE):**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost/db
```

**Fix:**
```env
DATABASE_URL=postgresql://cj_user:xK8mP9vQ2wE7nR3tY6uI1oP@localhost/citizen_journalism
```

**Best Practices:**
- Use strong passwords (20+ characters)
- Create dedicated database user (not `postgres`)
- Limit database user permissions
- Use password manager to generate/store

```sql
-- Create restricted user
CREATE USER cj_user WITH PASSWORD 'strong_random_password_here';
GRANT CONNECT ON DATABASE citizen_journalism TO cj_user;
GRANT USAGE ON SCHEMA public TO cj_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cj_user;
```

**Why Critical:** Weak database credentials are the #1 cause of data breaches.

---

#### 6. Implement Rate Limiting

**Install dependency:**
```bash
cd backend
uv add slowapi
```

**Configure rate limiting:**
```python
# backend/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to routes
@router.post("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(request: Request, ...):
    ...

@router.post("/articles")
@limiter.limit("10/minute")  # Max 10 article submissions per minute
async def create_article(request: Request, ...):
    ...
```

**Why Critical:** Prevents brute force attacks, DDoS, and API abuse.

---

#### 7. Validate and Sanitize All Input

**Install dependency:**
```bash
uv add bleach
```

**Implement input sanitization:**
```python
# backend/app/core/security.py
import bleach
from typing import Optional

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt'],
}

def sanitize_html(content: str) -> str:
    """Remove potentially dangerous HTML/JavaScript."""
    return bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """Basic string sanitization."""
    # Remove null bytes
    text = text.replace('\x00', '')

    # Trim whitespace
    text = text.strip()

    # Enforce max length
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text
```

**Use in models:**
```python
# backend/app/models/article.py
from app.core.security import sanitize_html, sanitize_string

class ArticleCreate(BaseModel):
    title: str
    content: str

    @validator('title')
    def validate_title(cls, v):
        v = sanitize_string(v, max_length=200)
        if len(v) < 5:
            raise ValueError('Title too short')
        return v

    @validator('content')
    def validate_content(cls, v):
        v = sanitize_html(v)
        if len(v) < 100:
            raise ValueError('Content too short')
        return v
```

**Why Critical:** Prevents XSS (Cross-Site Scripting) attacks and SQL injection.

---

#### 8. Implement SQL Injection Protection

**Current Status:** SQLAlchemy ORM provides automatic protection, but verify:

**✅ Safe (using ORM):**
```python
# Good - parameterized query
article = await session.execute(
    select(Article).where(Article.id == article_id)
)
```

**❌ Dangerous (raw SQL):**
```python
# BAD - vulnerable to SQL injection
query = f"SELECT * FROM articles WHERE id = {article_id}"
result = await session.execute(text(query))
```

**If you must use raw SQL:**
```python
# Good - use parameters
query = text("SELECT * FROM articles WHERE id = :id")
result = await session.execute(query, {"id": article_id})
```

**Why Critical:** SQL injection can expose entire database or allow data deletion.

---

## Authentication & Authorization

### Password Security

#### 1. Password Hashing

**✅ Already implemented correctly:**
```python
# backend/app/core/security.py uses bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

#### 2. Password Requirements

**Add password validation:**
```python
# backend/app/models/user.py
import re
from pydantic import validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Password must be at least 12 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
```

#### 3. Multi-Factor Authentication (2FA)

**Add 2FA support:**
```bash
uv add pyotp qrcode
```

```python
# backend/app/core/mfa.py
import pyotp
import qrcode
from io import BytesIO
import base64

def generate_totp_secret() -> str:
    """Generate TOTP secret for user."""
    return pyotp.random_base64()

def generate_qr_code(email: str, secret: str) -> str:
    """Generate QR code for authenticator app."""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name="Citizen Journalism"
    )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"

def verify_totp(secret: str, token: str) -> bool:
    """Verify TOTP token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)
```

### JWT Token Security

**Current JWT configuration:**
```python
# backend/app/core/config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # ✅ Good - short lived
REFRESH_TOKEN_EXPIRE_DAYS = 7     # ✅ Good - reasonable

# Add these settings
JWT_ALGORITHM = "HS256"
JWT_AUDIENCE = "citizen-journalism-api"
JWT_ISSUER = "yourdomain.com"
```

**Improve JWT creation:**
```python
# backend/app/core/security.py
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),  # Issued at
        "aud": settings.JWT_AUDIENCE,  # Audience
        "iss": settings.JWT_ISSUER,    # Issuer
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt
```

### Session Management

**Implement secure sessions:**
```python
# backend/app/core/sessions.py
from redis.asyncio import Redis
import json
from uuid import uuid4

class SessionManager:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_session(self, user_id: str, data: dict) -> str:
        """Create new session."""
        session_id = str(uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **data
        }

        # Store in Redis with 7 day expiry
        await self.redis.setex(
            f"session:{session_id}",
            60 * 60 * 24 * 7,  # 7 days
            json.dumps(session_data)
        )

        return session_id

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session."""
        data = await self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None

    async def delete_session(self, session_id: str):
        """Delete session (logout)."""
        await self.redis.delete(f"session:{session_id}")

    async def delete_user_sessions(self, user_id: str):
        """Delete all sessions for user."""
        # Implement session tracking per user
        pass
```

---

## Data Protection

### 1. Encryption at Rest

**Database Encryption:**
```sql
-- Enable PostgreSQL encryption
ALTER DATABASE citizen_journalism SET encryption = 'on';

-- Encrypt specific columns (for sensitive data)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: encrypt SSN or payment info
UPDATE users SET
    ssn = pgp_sym_encrypt(ssn, 'encryption_key')
WHERE ssn IS NOT NULL;
```

**File Upload Encryption (S3):**
```python
# backend/app/core/storage.py
import boto3

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def upload_file(file, filename: str):
    """Upload file with server-side encryption."""
    s3_client.upload_fileobj(
        file,
        settings.AWS_S3_BUCKET,
        filename,
        ExtraArgs={
            'ServerSideEncryption': 'AES256',  # Enable encryption
            'ACL': 'private',  # Not public
            'ContentType': file.content_type,
        }
    )
```

### 2. Encryption in Transit

**Already covered:** HTTPS/TLS for all traffic.

**Database connections:**
```env
# Use SSL for database connection
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

### 3. Sensitive Data Handling

**PII (Personally Identifiable Information) guidelines:**

```python
# backend/app/models/user.py
from pydantic import BaseModel, EmailStr

class UserPublic(BaseModel):
    """Public user data - safe to expose."""
    id: UUID
    username: str
    full_name: str
    avatar_url: Optional[str]
    # DO NOT include: email, password_hash, ip_address, etc.

class UserPrivate(BaseModel):
    """Private user data - only for user themselves."""
    id: UUID
    username: str
    full_name: str
    email: EmailStr
    avatar_url: Optional[str]
    created_at: datetime
    # Still DO NOT include: password_hash, ip_address

class UserDB(BaseModel):
    """Database model - never expose directly."""
    id: UUID
    username: str
    email: EmailStr
    password_hash: str  # NEVER send to frontend
    ip_address: Optional[str]  # NEVER send to frontend
    # ... all fields
```

### 4. Data Retention & Deletion

**Implement GDPR-compliant deletion:**
```python
# backend/app/api/v1/users.py
@router.delete("/me")
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account and all associated data."""

    # Delete user data
    await db.execute(delete(Article).where(Article.author_id == current_user.id))
    await db.execute(delete(Comment).where(Comment.user_id == current_user.id))
    await db.execute(delete(Rating).where(Rating.user_id == current_user.id))

    # Anonymize instead of delete (for data integrity)
    current_user.email = f"deleted_{current_user.id}@deleted.com"
    current_user.username = f"deleted_{current_user.id}"
    current_user.full_name = "Deleted User"
    current_user.is_active = False

    await db.commit()

    return {"message": "Account deleted successfully"}
```

---

## API Security

### 1. Input Validation

**Pydantic models handle this, but add custom validators:**

```python
from pydantic import BaseModel, validator, constr

class ArticleCreate(BaseModel):
    title: constr(min_length=5, max_length=200)  # Constrained string
    content: constr(min_length=100)
    category: str

    @validator('category')
    def validate_category(cls, v):
        allowed = ['News', 'Politics', 'Environment', 'Health', 'Education']
        if v not in allowed:
            raise ValueError(f'Category must be one of: {allowed}')
        return v
```

### 2. API Authentication

**Current implementation uses JWT - good!**

**Add API key support for third-party access:**
```python
# backend/app/core/api_keys.py
import secrets

def generate_api_key() -> str:
    """Generate secure API key."""
    return f"cj_{secrets.token_urlsafe(32)}"

async def verify_api_key(api_key: str, db: AsyncSession) -> Optional[User]:
    """Verify API key and return associated user."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.key == api_key,
            APIKey.is_active == True,
            APIKey.expires_at > datetime.utcnow()
        )
    )
    key = result.scalar_one_or_none()

    if not key:
        return None

    # Update last used
    key.last_used_at = datetime.utcnow()
    await db.commit()

    return await db.get(User, key.user_id)
```

### 3. Request Size Limits

**Nginx configuration:**
```nginx
# Limit request body size
client_max_body_size 10M;  # Max 10MB uploads

# Limit request headers
large_client_header_buffers 4 16k;
```

**FastAPI configuration:**
```python
# backend/app/main.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large"}
            )
        return await call_next(request)

app.add_middleware(RequestSizeLimitMiddleware)
```

---

## Infrastructure Security

### 1. Firewall Configuration

**UFW (Uncomplicated Firewall) setup:**
```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow PostgreSQL only from localhost
sudo ufw deny 5432/tcp

# Allow Redis only from localhost
sudo ufw deny 6379/tcp

# Check status
sudo ufw status
```

### 2. Database Security

**PostgreSQL hardening:**
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

```
# Only allow local connections
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# DENY all other connections
host    all             all             0.0.0.0/0               reject
```

### 3. Redis Security

**Redis configuration:**
```bash
sudo nano /etc/redis/redis.conf
```

```conf
# Bind to localhost only
bind 127.0.0.1

# Require password
requirepass your_strong_redis_password_here

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
```

### 4. Server Hardening

```bash
# Keep system updated
sudo apt update && sudo apt upgrade -y

# Install fail2ban (blocks brute force attacks)
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Disable root SSH login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Use SSH keys instead of passwords
# Set: PasswordAuthentication no

sudo systemctl restart sshd
```

---

## Code Security

### 1. Dependency Scanning

**Scan Python dependencies:**
```bash
cd backend
uv add --dev safety
uv run safety check
```

**Scan Node dependencies:**
```bash
cd frontend
npm audit
npm audit fix
```

### 2. Static Code Analysis

**Python (bandit):**
```bash
cd backend
uv add --dev bandit
uv run bandit -r app/
```

**TypeScript (ESLint security plugin):**
```bash
cd frontend
npm install --save-dev eslint-plugin-security
```

Add to `.eslintrc.js`:
```javascript
module.exports = {
  plugins: ['security'],
  extends: ['plugin:security/recommended'],
};
```

### 3. Secret Scanning

**Use git-secrets to prevent committing secrets:**
```bash
# Install
brew install git-secrets  # macOS
# or
sudo apt install git-secrets  # Linux

# Setup
cd /home/joshua/personal/media
git secrets --install
git secrets --register-aws
```

Add custom patterns:
```bash
git secrets --add 'SECRET_KEY=.*'
git secrets --add 'JWT_SECRET_KEY=.*'
git secrets --add 'STRIPE_SECRET_KEY=.*'
```

---

## Compliance & Privacy

### 1. GDPR Compliance

**Requirements:**
- [ ] Privacy policy published
- [ ] Cookie consent banner
- [ ] Data export functionality
- [ ] Data deletion functionality
- [ ] User consent tracking
- [ ] Data breach notification plan

**Implement data export:**
```python
@router.get("/me/export")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export all user data (GDPR requirement)."""

    # Collect all user data
    articles = await db.execute(
        select(Article).where(Article.author_id == current_user.id)
    )

    data = {
        "user": {
            "email": current_user.email,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat(),
        },
        "articles": [a.dict() for a in articles.scalars()],
        # ... other data
    }

    return JSONResponse(content=data)
```

### 2. Cookie Policy

**Frontend cookie consent:**
```typescript
// frontend/src/components/CookieConsent.tsx
import React, { useState, useEffect } from 'react';

const CookieConsent: React.FC = () => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
      setShow(true);
    }
  }, []);

  const acceptCookies = () => {
    localStorage.setItem('cookieConsent', 'accepted');
    setShow(false);
  };

  if (!show) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <p className="text-sm">
          We use cookies to improve your experience. By using our site, you agree to our{' '}
          <a href="/privacy" className="underline">Privacy Policy</a>.
        </p>
        <button onClick={acceptCookies} className="btn btn-primary ml-4">
          Accept
        </button>
      </div>
    </div>
  );
};

export default CookieConsent;
```

### 3. Content Security Policy (CSP)

**Add CSP headers:**
```nginx
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.yourdomain.com;
    frame-src https://js.stripe.com;
" always;
```

---

## Security Monitoring

### 1. Logging

**Configure structured logging:**
```python
# backend/app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("citizen_journalism")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Log security events:**
```python
# Log failed login attempts
logger.warning(
    "Failed login attempt",
    extra={
        "email": email,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)

# Log successful authentications
logger.info(
    "User logged in",
    extra={"user_id": user.id, "ip_address": request.client.host}
)

# Log permission errors
logger.warning(
    "Unauthorized access attempt",
    extra={"user_id": user.id, "resource": resource_id}
)
```

### 2. Intrusion Detection

**Set up automated alerts:**
```python
# backend/app/core/alerts.py
import httpx

async def send_security_alert(message: str, severity: str = "warning"):
    """Send security alert to Slack/Discord/Email."""

    # Example: Slack webhook
    webhook_url = settings.SLACK_WEBHOOK_URL

    await httpx.post(webhook_url, json={
        "text": f"🚨 Security Alert [{severity.upper()}]",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            }
        ]
    })

# Use in code
if failed_login_attempts > 10:
    await send_security_alert(
        f"User {email} has {failed_login_attempts} failed login attempts",
        severity="critical"
    )
```

### 3. Audit Trail

**Track all important actions:**
```python
# backend/app/models/audit_log.py
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    action = Column(String)  # "login", "create_article", "delete_user", etc.
    resource_type = Column(String)  # "article", "user", "comment"
    resource_id = Column(UUID)
    ip_address = Column(String)
    user_agent = Column(String)
    details = Column(JSON)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow)

# Use in routes
async def create_audit_log(
    db: AsyncSession,
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: UUID,
    request: Request,
    details: dict = None
):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        details=details
    )
    db.add(log)
    await db.commit()
```

---

## Incident Response

### Incident Response Plan

**1. Detection:**
- Monitor error logs for unusual patterns
- Set up alerts for failed login attempts
- Track API error rates
- Monitor database performance

**2. Containment:**
```bash
# Block malicious IP immediately
sudo ufw deny from <IP_ADDRESS>

# Disable compromised user account
UPDATE users SET is_active = false WHERE id = '<user_id>';

# Rotate compromised secrets
# Update .env file with new SECRET_KEY and JWT_SECRET_KEY
sudo systemctl restart cj-backend
```

**3. Investigation:**
- Check audit logs for suspicious activity
- Review recent code changes
- Analyze database for unauthorized changes
- Check server access logs

**4. Recovery:**
- Restore from backup if needed
- Reset all user passwords (if credential breach)
- Update security measures
- Patch vulnerabilities

**5. Post-Incident:**
- Document incident
- Notify affected users (if required by GDPR)
- Update security procedures
- Conduct training

---

## Security Checklist

### Pre-Production

- [ ] All default secrets changed to strong random values
- [ ] DEBUG mode disabled
- [ ] HTTPS enabled with valid SSL certificate
- [ ] CORS configured to allow only production domains
- [ ] Database uses strong password
- [ ] Rate limiting enabled on all endpoints
- [ ] Input validation on all user inputs
- [ ] HTML sanitization on all content
- [ ] Password requirements enforced (12+ chars, complexity)
- [ ] JWT tokens properly signed and validated
- [ ] File upload size limits enforced
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] Firewall configured (UFW or similar)
- [ ] Database accessible only from localhost
- [ ] Redis password protected
- [ ] SSH key authentication (password auth disabled)
- [ ] Fail2ban installed and configured
- [ ] Dependencies scanned for vulnerabilities
- [ ] Privacy policy published
- [ ] Cookie consent implemented
- [ ] GDPR data export/deletion implemented
- [ ] Logging configured and monitored
- [ ] Backup strategy implemented
- [ ] Incident response plan documented

### Post-Production

- [ ] Monitor error logs daily
- [ ] Review security logs weekly
- [ ] Update dependencies monthly
- [ ] Test backups monthly
- [ ] Security audit quarterly
- [ ] Penetration testing annually
- [ ] Review access permissions quarterly
- [ ] Rotate secrets every 6 months

---

## Tools & Resources

### Security Scanning Tools

- **Backend:** Safety, Bandit, Snyk
- **Frontend:** npm audit, Snyk, ESLint security
- **Infrastructure:** Nmap, OpenVAS
- **Penetration Testing:** OWASP ZAP, Burp Suite

### Security Monitoring Services

- **Uptime:** UptimeRobot, Pingdom
- **Errors:** Sentry, Rollbar
- **Logs:** Papertrail, LogDNA, DataDog
- **Performance:** New Relic, AppDynamics

### Compliance Resources

- **GDPR:** https://gdpr.eu/
- **CCPA:** https://oag.ca.gov/privacy/ccpa
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE Top 25:** https://cwe.mitre.org/top25/

---

## Questions?

If you're unsure about any security aspect:

1. Consult OWASP guidelines
2. Run security audit tools
3. Consider hiring security consultant for penetration testing
4. Join security communities (r/netsec, /r/websecurity)

**Remember:** Security is not a one-time task, it's an ongoing process!
