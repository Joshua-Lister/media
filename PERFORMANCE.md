# Performance Optimization Guide

Complete guide for optimizing performance of the Citizen Journalism Platform.

## Table of Contents

1. [Performance Goals](#performance-goals)
2. [Backend Optimization](#backend-optimization)
3. [Frontend Optimization](#frontend-optimization)
4. [Database Optimization](#database-optimization)
5. [Caching Strategies](#caching-strategies)
6. [CDN & Asset Optimization](#cdn--asset-optimization)
7. [Monitoring & Metrics](#monitoring--metrics)
8. [Load Testing](#load-testing)
9. [Scaling Strategies](#scaling-strategies)

---

## Performance Goals

### Target Metrics

| Metric | Target | Current (Unoptimized) | Priority |
|--------|--------|----------------------|----------|
| **Page Load Time** | < 2s | ~5s | 🔴 High |
| **API Response Time** | < 200ms | ~500ms | 🔴 High |
| **Time to Interactive** | < 3s | ~7s | 🔴 High |
| **First Contentful Paint** | < 1.5s | ~3s | 🟡 Medium |
| **Database Queries** | < 50ms | ~200ms | 🔴 High |
| **Concurrent Users** | 1000+ | ~50 | 🟡 Medium |

### Google Lighthouse Score Targets

- **Performance:** 90+
- **Accessibility:** 95+
- **Best Practices:** 95+
- **SEO:** 100

---

## Backend Optimization

### 1. Database Query Optimization

#### Problem: N+1 Query Problem

**❌ Inefficient (makes 101 queries):**
```python
# Get articles
articles = await db.execute(select(Article).limit(100))

# This causes N+1 queries (1 for articles + 100 for authors)
for article in articles.scalars():
    author = await db.get(User, article.author_id)  # 100 extra queries!
```

**✅ Optimized (makes 1 query):**
```python
from sqlalchemy.orm import selectinload

# Load articles with authors in single query
result = await db.execute(
    select(Article)
    .options(selectinload(Article.author))  # Eager load author
    .limit(100)
)
articles = result.scalars().all()

# Now article.author is already loaded!
for article in articles:
    print(article.author.full_name)  # No extra query
```

#### Add Database Indexes

```python
# backend/app/models/article.py
class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID, primary_key=True, default=uuid4)
    author_id = Column(UUID, ForeignKey("users.id"), index=True)  # ✅ Add index
    topic_id = Column(UUID, ForeignKey("topics.id"), index=True)  # ✅ Add index
    status = Column(String, index=True)  # ✅ Add index for filtering
    published_at = Column(DateTime, index=True)  # ✅ Add index for sorting
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

# Add composite indexes for common queries
__table_args__ = (
    Index('idx_article_status_published', 'status', 'published_at'),
    Index('idx_article_author_status', 'author_id', 'status'),
)
```

**Create indexes via migration:**
```bash
cd backend
uv run alembic revision -m "add_performance_indexes"
```

Edit migration file:
```python
def upgrade():
    # Add indexes
    op.create_index('idx_article_status_published', 'articles', ['status', 'published_at'])
    op.create_index('idx_article_author_status', 'articles', ['author_id', 'status'])
    op.create_index('idx_rating_article', 'ratings', ['article_id'])
    op.create_index('idx_comment_article', 'comments', ['article_id'])

def downgrade():
    op.drop_index('idx_article_status_published')
    op.drop_index('idx_article_author_status')
    op.drop_index('idx_rating_article')
    op.drop_index('idx_comment_article')
```

Apply:
```bash
uv run alembic upgrade head
```

#### Use Database Connection Pooling

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,          # Number of connections to maintain
    max_overflow=10,       # Additional connections when pool is full
    pool_pre_ping=True,    # Verify connections before using
    pool_recycle=3600,     # Recycle connections every hour
)
```

### 2. Async Operations

**Use async for I/O operations:**

```python
# ❌ Slow - sequential
async def get_article_with_stats(article_id: UUID, db: AsyncSession):
    article = await db.get(Article, article_id)
    ratings = await get_article_ratings(article_id, db)  # Wait
    comments = await get_article_comments(article_id, db)  # Wait
    return article, ratings, comments

# ✅ Fast - parallel
import asyncio

async def get_article_with_stats(article_id: UUID, db: AsyncSession):
    article, ratings, comments = await asyncio.gather(
        db.get(Article, article_id),
        get_article_ratings(article_id, db),
        get_article_comments(article_id, db)
    )
    return article, ratings, comments
```

### 3. Response Compression

**Enable Gzip compression:**

```python
# backend/app/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Nginx compression:**
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml+rss;
```

### 4. Pagination

**Implement cursor-based pagination for large datasets:**

```python
from fastapi import Query

@router.get("/articles")
async def list_articles(
    cursor: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Efficient cursor-based pagination."""

    query = select(Article).where(Article.status == "published")

    if cursor:
        # Decode cursor to get last article ID
        cursor_id = UUID(cursor)
        query = query.where(Article.created_at < (
            select(Article.created_at).where(Article.id == cursor_id)
        ))

    query = query.order_by(Article.created_at.desc()).limit(limit + 1)

    result = await db.execute(query)
    articles = result.scalars().all()

    # Check if there are more results
    has_more = len(articles) > limit
    if has_more:
        articles = articles[:-1]

    # Next cursor is ID of last article
    next_cursor = str(articles[-1].id) if has_more and articles else None

    return {
        "articles": articles,
        "next_cursor": next_cursor,
        "has_more": has_more
    }
```

### 5. Background Tasks

**Move slow operations to background:**

```python
from fastapi import BackgroundTasks

async def send_notification_email(user_id: UUID):
    """Send email notification (slow operation)."""
    # Email sending logic here
    pass

async def update_article_stats(article_id: UUID):
    """Update article statistics."""
    # Calculate stats
    pass

@router.post("/articles")
async def create_article(
    article: ArticleCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create article and trigger background tasks."""

    # Create article (fast)
    new_article = Article(**article.dict(), author_id=current_user.id)
    db.add(new_article)
    await db.commit()

    # Schedule background tasks (don't wait)
    background_tasks.add_task(send_notification_email, current_user.id)
    background_tasks.add_task(update_article_stats, new_article.id)

    return new_article
```

---

## Frontend Optimization

### 1. Code Splitting

**Lazy load routes:**

```typescript
// frontend/src/App.tsx
import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Eager load critical components
import Layout from './components/Layout';
import HomePage from './pages/HomePage';

// Lazy load other pages
const ArticleDetailPage = lazy(() => import('./pages/ArticleDetailPage'));
const TopicsPage = lazy(() => import('./pages/TopicsPage'));
const WriterProfilePage = lazy(() => import('./pages/WriterProfilePage'));

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/articles/:slug" element={<ArticleDetailPage />} />
            <Route path="/topics" element={<TopicsPage />} />
            <Route path="/writers/:username" element={<WriterProfilePage />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}
```

### 2. Image Optimization

**Implement lazy loading and responsive images:**

```typescript
// frontend/src/components/OptimizedImage.tsx
import React, { useState } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({ src, alt, className }) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className={`relative ${className}`}>
      {/* Placeholder */}
      {!loaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}

      {/* Actual image */}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        decoding="async"
        onLoad={() => setLoaded(true)}
        className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
      />
    </div>
  );
};

export default OptimizedImage;
```

**Use responsive images:**
```typescript
<picture>
  <source
    srcSet={`${article.cover_image_url}?w=400 400w,
             ${article.cover_image_url}?w=800 800w,
             ${article.cover_image_url}?w=1200 1200w`}
    sizes="(max-width: 640px) 400px, (max-width: 1024px) 800px, 1200px"
  />
  <img src={article.cover_image_url} alt={article.title} loading="lazy" />
</picture>
```

### 3. React Query Optimization

**Configure caching:**

```typescript
// frontend/src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,  // Consider data fresh for 5 minutes
      cacheTime: 10 * 60 * 1000, // Keep unused data for 10 minutes
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Your app */}
    </QueryClientProvider>
  );
}
```

**Prefetch data on hover:**

```typescript
// frontend/src/components/ArticleCard.tsx
import { useQueryClient } from '@tanstack/react-query';

const ArticleCard: React.FC<{ article: Article }> = ({ article }) => {
  const queryClient = useQueryClient();

  const prefetchArticle = () => {
    queryClient.prefetchQuery(['article', article.slug], () =>
      articlesAPI.get(article.slug)
    );
  };

  return (
    <Link
      to={`/articles/${article.slug}`}
      onMouseEnter={prefetchArticle}  // Prefetch on hover
    >
      <h3>{article.title}</h3>
      <p>{article.summary}</p>
    </Link>
  );
};
```

### 4. Bundle Size Optimization

**Analyze bundle size:**
```bash
cd frontend
npm install --save-dev webpack-bundle-analyzer
npm run build
```

**Remove unused dependencies:**
```bash
# Check for unused dependencies
npm install -g depcheck
depcheck
```

**Tree shaking - import only what you need:**

```typescript
// ❌ Bad - imports entire library
import _ from 'lodash';
const result = _.debounce(fn, 300);

// ✅ Good - imports only what's needed
import debounce from 'lodash/debounce';
const result = debounce(fn, 300);
```

### 5. Memoization

**Prevent unnecessary re-renders:**

```typescript
import React, { memo, useMemo, useCallback } from 'react';

// Memoize expensive components
const ArticleCard = memo<ArticleCardProps>(({ article, onLike }) => {
  // This component only re-renders if article or onLike change
  return <div>...</div>;
});

// Memoize expensive calculations
const ArticleList: React.FC = ({ articles }) => {
  const sortedArticles = useMemo(() => {
    return articles.sort((a, b) => b.rating - a.rating);
  }, [articles]); // Only recalculate when articles change

  // Memoize callbacks
  const handleLike = useCallback((id: string) => {
    // Handle like
  }, []); // Function reference stays the same

  return (
    <div>
      {sortedArticles.map(article => (
        <ArticleCard key={article.id} article={article} onLike={handleLike} />
      ))}
    </div>
  );
};
```

### 6. Virtualization

**Use virtual scrolling for long lists:**

```bash
npm install react-window
```

```typescript
// frontend/src/components/VirtualizedArticleList.tsx
import { FixedSizeList } from 'react-window';

const VirtualizedArticleList: React.FC<{ articles: Article[] }> = ({ articles }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ArticleCard article={articles[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={800}           // Viewport height
      itemCount={articles.length}
      itemSize={200}         // Height of each item
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

---

## Database Optimization

### 1. Query Analysis

**Enable query logging:**
```python
# backend/app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Log all SQL queries
)
```

**Find slow queries:**
```sql
-- PostgreSQL slow query log
SELECT
  mean_exec_time,
  calls,
  query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 2. Database Indexing Strategy

**Check missing indexes:**
```sql
-- Find tables without indexes on foreign keys
SELECT
  c.relname AS table_name,
  a.attname AS column_name
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(con.conkey)
WHERE con.contype = 'f'
AND NOT EXISTS (
  SELECT 1 FROM pg_index i
  WHERE i.indrelid = c.oid
  AND a.attnum = ANY(i.indkey)
);
```

### 3. Database Partitioning

**For large tables (millions of rows), use partitioning:**

```sql
-- Partition articles by year
CREATE TABLE articles (
    id UUID,
    title TEXT,
    published_at TIMESTAMP,
    ...
) PARTITION BY RANGE (published_at);

-- Create partitions
CREATE TABLE articles_2024 PARTITION OF articles
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE articles_2025 PARTITION OF articles
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### 4. Read Replicas

**For read-heavy workloads:**

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

# Primary database (read + write)
primary_engine = create_async_engine(settings.DATABASE_URL)

# Read replica (read only)
replica_engine = create_async_engine(settings.DATABASE_REPLICA_URL)

def get_read_db():
    """Use read replica for read-only queries."""
    return AsyncSession(replica_engine)

def get_write_db():
    """Use primary for writes."""
    return AsyncSession(primary_engine)
```

---

## Caching Strategies

### 1. Redis Caching

**Install Redis client:**
```bash
cd backend
uv add redis[hiredis]
```

**Implement caching decorator:**

```python
# backend/app/core/cache.py
import redis.asyncio as redis
import json
from functools import wraps

redis_client = redis.from_url(settings.REDIS_URL)

def cache(ttl: int = 300):
    """Cache decorator with TTL in seconds."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, default=str)
            )

            return result
        return wrapper
    return decorator
```

**Use caching:**

```python
# backend/app/api/v1/articles.py
from app.core.cache import cache

@router.get("/articles")
@cache(ttl=300)  # Cache for 5 minutes
async def list_articles(db: AsyncSession = Depends(get_db)):
    """List articles with caching."""
    result = await db.execute(
        select(Article).where(Article.status == "published")
    )
    return result.scalars().all()
```

### 2. HTTP Caching Headers

```python
from fastapi import Response

@router.get("/articles/{slug}")
async def get_article(slug: str, response: Response):
    article = await get_article_by_slug(slug)

    # Cache for 1 hour
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["ETag"] = f'"{article.updated_at.timestamp()}"'

    return article
```

### 3. Browser Caching

**Nginx configuration:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## CDN & Asset Optimization

### 1. Use CDN

**CloudFlare (Free):**
1. Sign up at cloudflare.com
2. Add your domain
3. Update nameservers
4. Enable caching rules

**Automatic benefits:**
- Global edge caching
- DDoS protection
- Free SSL
- Image optimization

### 2. Image Optimization

**Use image CDN (imgix, Cloudinary):**

```typescript
// frontend/src/utils/imageOptimization.ts
const IMGIX_URL = 'https://your-domain.imgix.net';

export const optimizeImage = (src: string, options: {
  width?: number;
  quality?: number;
  format?: 'auto' | 'webp' | 'jpg';
} = {}) => {
  const params = new URLSearchParams({
    auto: options.format || 'format',
    q: (options.quality || 75).toString(),
    ...(options.width && { w: options.width.toString() }),
  });

  return `${IMGIX_URL}${src}?${params}`;
};
```

Usage:
```typescript
<img
  src={optimizeImage(article.cover_image_url, { width: 800, quality: 80 })}
  alt={article.title}
/>
```

### 3. Font Optimization

**Use system fonts when possible:**
```css
/* frontend/src/index.css */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", Arial, sans-serif;
}
```

**Or preload fonts:**
```html
<!-- frontend/public/index.html -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin>
```

---

## Monitoring & Metrics

### 1. Application Performance Monitoring (APM)

**Install Sentry:**
```bash
cd backend
uv add sentry-sdk[fastapi]

cd frontend
npm install @sentry/react
```

**Backend configuration:**
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1,  # Sample 10% of transactions
    profiles_sample_rate=0.1,
    integrations=[FastApiIntegration()],
)
```

**Frontend configuration:**
```typescript
// frontend/src/index.tsx
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],
});
```

### 2. Custom Metrics

**Track performance metrics:**

```python
# backend/app/core/metrics.py
import time
from functools import wraps

def track_performance(metric_name: str):
    """Decorator to track function execution time."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            result = await func(*args, **kwargs)

            duration = time.time() - start_time

            # Log to monitoring service
            logger.info(
                f"Performance metric: {metric_name}",
                extra={"duration_ms": duration * 1000}
            )

            return result
        return wrapper
    return decorator

# Use it
@track_performance("article_creation")
async def create_article(...):
    ...
```

### 3. Database Query Monitoring

```python
# backend/app/core/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - context._query_start_time

    if total_time > 0.1:  # Log slow queries (> 100ms)
        logger.warning(
            f"Slow query detected",
            extra={
                "duration_ms": total_time * 1000,
                "query": statement[:200]
            }
        )
```

### 4. Real User Monitoring (RUM)

**Add Web Vitals tracking:**

```bash
cd frontend
npm install web-vitals
```

```typescript
// frontend/src/reportWebVitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to analytics service
  fetch('/api/v1/analytics/vitals', {
    method: 'POST',
    body: JSON.stringify(metric),
    headers: { 'Content-Type': 'application/json' },
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

---

## Load Testing

### 1. Backend Load Testing

**Install Locust:**
```bash
pip install locust
```

**Create load test:**
```python
# loadtest.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_articles(self):
        """View article list (most common)."""
        self.client.get("/api/v1/articles/")

    @task(2)
    def view_article(self):
        """View specific article."""
        self.client.get("/api/v1/articles/some-article-slug")

    @task(1)
    def view_topics(self):
        """View topics."""
        self.client.get("/api/v1/topics/")

    def on_start(self):
        """Login once at start."""
        self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
```

**Run load test:**
```bash
locust -f loadtest.py --host=https://api.yourdomain.com
# Open http://localhost:8089
# Set users: 100, spawn rate: 10
```

### 2. Frontend Load Testing

**Use Lighthouse CI:**
```bash
npm install -g @lhci/cli

# Run lighthouse
lhci autorun --collect.url=http://localhost:3000
```

---

## Scaling Strategies

### 1. Horizontal Scaling

**Run multiple backend instances:**

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

**Load balancer (Nginx):**
```nginx
upstream backend {
    least_conn;  # Use least connections algorithm
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}

server {
    listen 80;

    location /api {
        proxy_pass http://backend;
    }
}
```

### 2. Auto-Scaling

**AWS Auto Scaling Group configuration:**
```yaml
# Scale up when CPU > 70%
# Scale down when CPU < 30%
min_instances: 2
max_instances: 10
target_cpu: 70%
```

### 3. Database Scaling

**Options:**
1. **Vertical:** Upgrade server (more CPU/RAM)
2. **Horizontal:** Add read replicas
3. **Sharding:** Split data across multiple databases

---

## Performance Checklist

### Backend

- [ ] Database indexes on all foreign keys
- [ ] Connection pooling configured
- [ ] Redis caching implemented
- [ ] Gzip compression enabled
- [ ] Async operations for I/O
- [ ] Background tasks for slow operations
- [ ] Pagination on all lists
- [ ] Query optimization (no N+1 queries)
- [ ] Response caching headers

### Frontend

- [ ] Code splitting implemented
- [ ] Images lazy loaded
- [ ] React Query caching configured
- [ ] Memoization on expensive components
- [ ] Bundle size analyzed and optimized
- [ ] Fonts optimized
- [ ] Service worker for offline
- [ ] Prefetching on hover

### Infrastructure

- [ ] CDN configured
- [ ] HTTP/2 enabled
- [ ] SSL/TLS configured
- [ ] Load balancer configured
- [ ] Auto-scaling enabled
- [ ] Database read replicas
- [ ] Monitoring configured
- [ ] Alert thresholds set

---

## Tools & Resources

### Performance Testing
- **Backend:** Locust, Apache JMeter, k6
- **Frontend:** Lighthouse, WebPageTest
- **Database:** pg_stat_statements, EXPLAIN ANALYZE

### Monitoring
- **APM:** Sentry, New Relic, DataDog
- **Uptime:** UptimeRobot, Pingdom
- **Logs:** Papertrail, LogDNA

### Optimization
- **Images:** imgix, Cloudinary, TinyPNG
- **CDN:** CloudFlare, AWS CloudFront
- **Caching:** Redis, Memcached

---

## Next Steps

1. Run Lighthouse audit on production
2. Implement critical optimizations (indexes, caching)
3. Set up monitoring (Sentry)
4. Run load tests
5. Monitor and iterate

**Remember:** Measure first, optimize second. Use monitoring data to guide optimization efforts!
