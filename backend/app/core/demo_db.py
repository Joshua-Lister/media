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
    rating: int = 0  # Overall 1-5 stars
    feedback: Optional[str] = None
    # Multi-criteria ratings
    accuracy_rating: Optional[int] = None
    sources_rating: Optional[int] = None
    writing_quality_rating: Optional[int] = None
    originality_rating: Optional[int] = None
    depth_rating: Optional[int] = None
    bias_rating: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DemoAnnotation:
    """In-memory annotation for demo mode."""
    id: UUID = field(default_factory=uuid4)
    article_id: UUID = None
    user_id: UUID = None
    selection_text: str = ""
    selection_start_offset: int = 0
    selection_end_offset: int = 0
    annotation_type: str = "comment"  # comment, fact_check, correction, question, support
    comment: str = ""
    evidence_url: Optional[str] = None
    evidence_title: Optional[str] = None
    evidence_excerpt: Optional[str] = None
    verification_status: str = "pending"
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)


class DemoDatabase:
    """In-memory database for demo mode."""

    def __init__(self):
        """Initialize empty in-memory storage."""
        self.users: Dict[UUID, DemoUser] = {}
        self.articles: Dict[UUID, DemoArticle] = {}
        self.topics: Dict[UUID, DemoTopic] = {}
        self.ratings: Dict[UUID, DemoRating] = {}
        self.annotations: Dict[UUID, DemoAnnotation] = {}
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
            {"title": "Climate Change Solutions", "description": "Innovative approaches to combat climate change and transition to renewable energy", "vote_count": 156},
            {"title": "Local Government Transparency", "description": "Exposing local government spending, decisions, and accountability", "vote_count": 142},
            {"title": "Community Health Initiatives", "description": "Public health programs, mental health services, and healthcare access in our community", "vote_count": 98},
            {"title": "Education System Reform", "description": "Teacher pay, curriculum changes, and school funding in our district", "vote_count": 87},
            {"title": "Housing Affordability Crisis", "description": "Rising rents, homelessness, and affordable housing solutions", "vote_count": 76},
            {"title": "Police Reform and Accountability", "description": "Community policing, transparency, and oversight of law enforcement", "vote_count": 65},
        ]

        for topic_data in topics_data:
            topic = DemoTopic(**topic_data)
            self.topics[topic.id] = topic

        # Create demo articles with rich content
        topic_ids = list(self.topics.keys())
        articles_data = [
            {
                "title": "Solar Panels Coming to City Hall: A $2M Investment",
                "content": """Our city is making a significant investment in renewable energy with a new solar panel installation at City Hall. The project, approved last month with a budget of $2 million, represents the largest clean energy initiative in our city's history.

According to Mayor Johnson, the solar array will cover the entire roof of City Hall and is expected to generate 400,000 kWh annually. This would reduce the building's electricity costs by an estimated 60% and save taxpayers approximately $50,000 per year.

However, critics point out that at current savings rates, it would take 40 years to recoup the initial investment. City Councilor Sarah Martinez questioned whether the funds could be better spent on other climate initiatives.

The installation is scheduled to begin next month and be completed by year's end. The project has received a $500,000 grant from the state's Clean Energy Fund.""",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[0] if topic_ids else None,
                "status": "published",
                "view_count": 1247,
            },
            {
                "title": "City Budget 2024: Where Your Tax Dollars Go",
                "content": """The city council approved the 2024 budget last night with a total spending of $450 million. Here's the breakdown:

- Education: $180M (40%)
- Public Safety: $135M (30%)
- Infrastructure: $67.5M (15%)
- Health Services: $45M (10%)
- Administration: $22.5M (5%)

The budget includes a 3% property tax increase, which will cost the average homeowner an additional $150 per year. This marks the fourth consecutive year of tax increases.

New investments include $10 million for road repairs and $5 million for a new community health center. However, the teachers' union expressed disappointment that educator salaries only increased by 2%, below the 3.5% inflation rate.""",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[1] if len(topic_ids) > 1 else None,
                "status": "published",
                "view_count": 892,
            },
        ]

        for article_data in articles_data:
            article = DemoArticle(**article_data)
            self.articles[article.id] = article

        # Create demo ratings with multi-criteria
        article_ids = list(self.articles.keys())
        if article_ids:
            # Rating 1: High quality review
            rating1 = DemoRating(
                article_id=article_ids[0],
                user_id=demo_reader.id,
                rating=5,
                feedback="Excellent investigative piece. Well-sourced and balanced coverage of the solar panel project.",
                accuracy_rating=5,
                sources_rating=5,
                writing_quality_rating=4,
                originality_rating=4,
                depth_rating=5,
                bias_rating=5,
            )
            self.ratings[rating1.id] = rating1

            # Rating 2: Critical review
            rating2 = DemoRating(
                article_id=article_ids[1],
                user_id=demo_reader.id,
                rating=4,
                feedback="Good breakdown of the budget, but would like to see more analysis on the tax increase impact.",
                accuracy_rating=5,
                sources_rating=4,
                writing_quality_rating=4,
                originality_rating=3,
                depth_rating=4,
                bias_rating=4,
            )
            self.ratings[rating2.id] = rating2

        # Create demo annotations
        if article_ids:
            # Annotation 1: Fact-check with evidence
            annotation1 = DemoAnnotation(
                article_id=article_ids[0],
                user_id=demo_reader.id,
                selection_text="400,000 kWh annually",
                selection_start_offset=250,
                selection_end_offset=270,
                annotation_type="fact_check",
                comment="I verified this number with the city's energy consultant report. The actual projection is 380,000-420,000 kWh depending on weather conditions.",
                evidence_url="https://example.com/energy-report.pdf",
                evidence_title="City Hall Solar Feasibility Study 2024",
                evidence_excerpt="Projected annual generation: 380,000-420,000 kWh (median: 400,000 kWh)",
                verification_status="verified_accurate",
                upvotes=12,
                downvotes=1,
            )
            self.annotations[annotation1.id] = annotation1

            # Annotation 2: Correction
            annotation2 = DemoAnnotation(
                article_id=article_ids[0],
                user_id=demo_reader.id,
                selection_text="$500,000 grant from the state's Clean Energy Fund",
                selection_start_offset=650,
                selection_end_offset=700,
                annotation_type="correction",
                comment="The grant is actually $750,000 according to the state website. The article may be using outdated information.",
                evidence_url="https://example.com/state-grants",
                evidence_title="State Clean Energy Grant Awards 2024",
                verification_status="pending",
                upvotes=5,
                downvotes=2,
            )
            self.annotations[annotation2.id] = annotation2

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
