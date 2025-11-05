"""
Demo mode in-memory database implementation.
Provides a simple in-memory storage for demo mode without requiring PostgreSQL.
"""
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class DemoUser:
    """In-memory user for demo mode."""
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    username: str = ""
    hashed_password: str = ""
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = True
    is_writer: bool = False
    is_superuser: bool = False
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    reputation_score: int = 0
    stripe_customer_id: Optional[str] = None
    stripe_account_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def dict(self):
        """Convert to dict for API responses."""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_writer": self.is_writer,
            "is_superuser": self.is_superuser,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "reputation_score": self.reputation_score,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class DemoArticle:
    """In-memory article for demo mode."""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    author_id: UUID = None
    topic_id: Optional[UUID] = None
    status: str = "draft"  # draft, published, archived
    view_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DemoTopic:
    """In-memory topic for demo mode."""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    vote_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DemoRating:
    """In-memory rating for demo mode."""
    id: UUID = field(default_factory=uuid4)
    article_id: UUID = None
    user_id: UUID = None
    score: int = 0  # 1-5 stars
    review: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class DemoDatabase:
    """In-memory database for demo mode."""

    def __init__(self):
        """Initialize empty in-memory storage."""
        self.users: Dict[UUID, DemoUser] = {}
        self.articles: Dict[UUID, DemoArticle] = {}
        self.topics: Dict[UUID, DemoTopic] = {}
        self.ratings: Dict[UUID, DemoRating] = {}
        self.user_by_email: Dict[str, UUID] = {}
        self.user_by_username: Dict[str, UUID] = {}

        # Seed with demo data
        self._seed_demo_data()

    def _seed_demo_data(self):
        """Seed database with demo data."""
        # Create demo users
        demo_reader = DemoUser(
            email="reader@demo.com",
            username="demo_reader",
            hashed_password="$2b$12$demo.hashed.password",  # "password"
            full_name="Demo Reader",
            is_writer=False,
            bio="I'm a demo reader exploring the platform",
        )

        demo_writer = DemoUser(
            email="writer@demo.com",
            username="demo_writer",
            hashed_password="$2b$12$demo.hashed.password",  # "password"
            full_name="Demo Writer",
            is_writer=True,
            bio="I'm a demo writer creating content",
        )

        # Add users
        self.users[demo_reader.id] = demo_reader
        self.users[demo_writer.id] = demo_writer
        self.user_by_email[demo_reader.email] = demo_reader.id
        self.user_by_email[demo_writer.email] = demo_writer.id
        self.user_by_username[demo_reader.username] = demo_reader.id
        self.user_by_username[demo_writer.username] = demo_writer.id

        # Create demo topics
        topics_data = [
            {"title": "Climate Change Solutions", "description": "Innovative approaches to combat climate change", "vote_count": 45},
            {"title": "Local Government Transparency", "description": "Exposing local government spending and decisions", "vote_count": 38},
            {"title": "Community Health", "description": "Health initiatives in our community", "vote_count": 32},
        ]

        for topic_data in topics_data:
            topic = DemoTopic(**topic_data)
            self.topics[topic.id] = topic

        # Create demo articles
        topic_ids = list(self.topics.keys())
        articles_data = [
            {
                "title": "Renewable Energy in Our City",
                "content": "A comprehensive look at renewable energy initiatives...",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[0] if topic_ids else None,
                "status": "published",
                "view_count": 234,
            },
            {
                "title": "City Budget 2024: Where Does Your Money Go?",
                "content": "An in-depth analysis of the city budget...",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[1] if len(topic_ids) > 1 else None,
                "status": "published",
                "view_count": 189,
            },
        ]

        for article_data in articles_data:
            article = DemoArticle(**article_data)
            self.articles[article.id] = article

    def get_user_by_id(self, user_id: UUID) -> Optional[DemoUser]:
        """Get user by ID."""
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[DemoUser]:
        """Get user by email."""
        user_id = self.user_by_email.get(email)
        return self.users.get(user_id) if user_id else None

    def get_user_by_username(self, username: str) -> Optional[DemoUser]:
        """Get user by username."""
        user_id = self.user_by_username.get(username)
        return self.users.get(user_id) if user_id else None

    def create_user(self, user_data: Dict[str, Any]) -> DemoUser:
        """Create a new user."""
        user = DemoUser(**user_data)
        self.users[user.id] = user
        self.user_by_email[user.email] = user.id
        self.user_by_username[user.username] = user.id
        return user

    def get_articles(self, skip: int = 0, limit: int = 20, status: str = "published") -> List[DemoArticle]:
        """Get list of articles."""
        filtered = [a for a in self.articles.values() if a.status == status]
        return filtered[skip:skip + limit]

    def get_article_by_id(self, article_id: UUID) -> Optional[DemoArticle]:
        """Get article by ID."""
        return self.articles.get(article_id)

    def get_topics(self, skip: int = 0, limit: int = 20) -> List[DemoTopic]:
        """Get list of topics sorted by vote count."""
        sorted_topics = sorted(self.topics.values(), key=lambda t: t.vote_count, reverse=True)
        return sorted_topics[skip:skip + limit]

    def get_topic_by_id(self, topic_id: UUID) -> Optional[DemoTopic]:
        """Get topic by ID."""
        return self.topics.get(topic_id)


# Global demo database instance
_demo_db: Optional[DemoDatabase] = None


def get_demo_db() -> DemoDatabase:
    """Get or create demo database instance."""
    global _demo_db
    if _demo_db is None:
        _demo_db = DemoDatabase()
    return _demo_db


def reset_demo_db() -> DemoDatabase:
    """Reset demo database to initial state."""
    global _demo_db
    _demo_db = DemoDatabase()
    return _demo_db
