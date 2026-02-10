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
    slug: str = ""
    summary: str = ""
    content: str = ""
    category: str = "News"
    cover_image_url: Optional[str] = None
    author_id: UUID = None
    topic_id: Optional[UUID] = None
    status: str = "draft"  # draft, published, archived
    view_count: int = 0
    reading_time_minutes: int = 5
    published_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DemoTopic:
    """In-memory topic for demo mode."""
    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: str = ""
    category: str = "General"  # Politics, Environment, Health, Education, Housing, etc.
    tags: List[str] = field(default_factory=list)  # ["climate", "renewable-energy", etc.]
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


@dataclass
class DemoUserInterest:
    """Track user interests for personalization."""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    # Categories and tags the user has interacted with
    category_scores: Dict[str, int] = field(default_factory=dict)  # {category: interaction_count}
    tag_scores: Dict[str, int] = field(default_factory=dict)  # {tag: interaction_count}
    # Topics the user has voted on
    voted_topic_ids: List[UUID] = field(default_factory=list)
    # Articles the user has read
    read_article_ids: List[UUID] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class DemoDatabase:
    """In-memory database for demo mode."""

    def __init__(self):
        """Initialize empty in-memory storage."""
        self.users: Dict[UUID, DemoUser] = {}
        self.articles: Dict[UUID, DemoArticle] = {}
        self.topics: Dict[UUID, DemoTopic] = {}
        self.ratings: Dict[UUID, DemoRating] = {}
        self.annotations: Dict[UUID, DemoAnnotation] = {}
        self.user_interests: Dict[UUID, DemoUserInterest] = {}  # user_id -> interests
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
            {
                "title": "Climate Change Solutions",
                "description": "Innovative approaches to combat climate change and transition to renewable energy",
                "category": "Environment",
                "tags": ["climate", "renewable-energy", "sustainability", "green-energy"],
                "vote_count": 156
            },
            {
                "title": "Local Government Transparency",
                "description": "Exposing local government spending, decisions, and accountability",
                "category": "Politics",
                "tags": ["government", "transparency", "accountability", "local-politics", "budget"],
                "vote_count": 142
            },
            {
                "title": "Community Health Initiatives",
                "description": "Public health programs, mental health services, and healthcare access in our community",
                "category": "Health",
                "tags": ["healthcare", "mental-health", "public-health", "wellness", "community"],
                "vote_count": 98
            },
            {
                "title": "Education System Reform",
                "description": "Teacher pay, curriculum changes, and school funding in our district",
                "category": "Education",
                "tags": ["education", "schools", "teachers", "curriculum", "funding"],
                "vote_count": 87
            },
            {
                "title": "Housing Affordability Crisis",
                "description": "Rising rents, homelessness, and affordable housing solutions",
                "category": "Housing",
                "tags": ["housing", "affordability", "homelessness", "rent", "real-estate"],
                "vote_count": 76
            },
            {
                "title": "Police Reform and Accountability",
                "description": "Community policing, transparency, and oversight of law enforcement",
                "category": "Public Safety",
                "tags": ["police", "reform", "accountability", "law-enforcement", "community-policing"],
                "vote_count": 65
            },
        ]

        for topic_data in topics_data:
            topic = DemoTopic(**topic_data)
            self.topics[topic.id] = topic

        # Create demo articles with rich content
        topic_ids = list(self.topics.keys())
        from datetime import timedelta

        articles_data = [
            {
                "title": "Solar Panels Coming to City Hall: A $2M Investment",
                "slug": "solar-panels-city-hall-2m-investment",
                "summary": "Our city is making a significant investment in renewable energy with a new solar panel installation at City Hall.",
                "content": """Our city is making a significant investment in renewable energy with a new solar panel installation at City Hall. The project, approved last month with a budget of $2 million, represents the largest clean energy initiative in our city's history.

According to Mayor Johnson, the solar array will cover the entire roof of City Hall and is expected to generate 400,000 kWh annually. This would reduce the building's electricity costs by an estimated 60% and save taxpayers approximately $50,000 per year.

However, critics point out that at current savings rates, it would take 40 years to recoup the initial investment. City Councilor Sarah Martinez questioned whether the funds could be better spent on other climate initiatives.

The installation is scheduled to begin next month and be completed by year's end. The project has received a $500,000 grant from the state's Clean Energy Fund.""",
                "category": "Environment",
                "cover_image_url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[0] if topic_ids else None,
                "status": "published",
                "view_count": 1247,
                "reading_time_minutes": 8,
                "published_at": datetime.utcnow() - timedelta(days=2),
            },
            {
                "title": "City Budget 2024: Where Your Tax Dollars Go",
                "slug": "city-budget-2024-tax-dollars",
                "summary": "A detailed breakdown of the city's $450 million budget and what it means for taxpayers.",
                "content": """The city council approved the 2024 budget last night with a total spending of $450 million. Here's the breakdown:

- Education: $180M (40%)
- Public Safety: $135M (30%)
- Infrastructure: $67.5M (15%)
- Health Services: $45M (10%)
- Administration: $22.5M (5%)

The budget includes a 3% property tax increase, which will cost the average homeowner an additional $150 per year. This marks the fourth consecutive year of tax increases.

New investments include $10 million for road repairs and $5 million for a new community health center. However, the teachers' union expressed disappointment that educator salaries only increased by 2%, below the 3.5% inflation rate.""",
                "category": "Politics",
                "cover_image_url": "https://images.unsplash.com/photo-1541872705-1f73c6400ec9?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[1] if len(topic_ids) > 1 else None,
                "status": "published",
                "view_count": 2134,
                "reading_time_minutes": 6,
                "published_at": datetime.utcnow() - timedelta(days=5),
            },
            {
                "title": "Mental Health Crisis: Breaking the Stigma in Our Community",
                "slug": "mental-health-crisis-breaking-stigma",
                "summary": "Local mental health advocates are working to normalize conversations about mental wellness and expand access to services.",
                "content": """Mental health has emerged from the shadows as one of the most pressing public health issues of our time. Local advocates are launching a new initiative to break the stigma and expand access to mental health services in our community.

The 'Minds Matter' campaign brings together healthcare providers, schools, and community organizations to provide free mental health screenings and connect residents with resources. According to Dr. Lisa Chen, the initiative's director, 1 in 5 adults in our county experience mental illness each year, yet only 40% receive treatment.

The program includes partnerships with local employers to offer mental health days and training for managers to recognize signs of distress in their teams. Three new counseling centers will open in underserved neighborhoods by year's end.

However, funding remains a challenge. The initiative relies heavily on donations and a small grant from the state health department. Organizers are calling on the city council to allocate dedicated funding in next year's budget.""",
                "category": "Health",
                "cover_image_url": "https://images.unsplash.com/photo-1573497491208-6b1acb260507?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[2] if len(topic_ids) > 2 else None,
                "status": "published",
                "view_count": 1856,
                "reading_time_minutes": 10,
                "published_at": datetime.utcnow() - timedelta(days=7),
            },
            {
                "title": "Public Schools Face Teacher Shortage Crisis",
                "slug": "public-schools-teacher-shortage-crisis",
                "summary": "District officials warn that unfilled teaching positions could force larger class sizes and reduced course offerings.",
                "content": """Our school district is facing its worst teacher shortage in decades, with 47 unfilled positions just weeks before the new school year begins. District Superintendent Maria Rodriguez warns that the crisis could lead to larger class sizes and reduced course offerings.

The shortage is hitting STEM subjects and special education hardest. At Lincoln High School, the physics and chemistry positions remain vacant, forcing the school to consider online instruction for advanced courses.

Teachers cite low pay, challenging working conditions, and lack of respect as reasons for leaving the profession. Starting salary for teachers in our district is $42,000, compared to the state average of $51,000. The teachers' union is demanding a 15% raise to make positions competitive with neighboring districts.

The district has launched an emergency recruitment campaign, including hiring bonuses of up to $5,000 for teachers in high-need subjects. They're also fast-tracking certification for career changers and working with local universities to expand student teacher programs.""",
                "category": "Education",
                "cover_image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[3] if len(topic_ids) > 3 else None,
                "status": "published",
                "view_count": 987,
                "reading_time_minutes": 9,
                "published_at": datetime.utcnow() - timedelta(days=10),
            },
            {
                "title": "Affordable Housing Project Approved Despite Neighborhood Opposition",
                "slug": "affordable-housing-project-approved",
                "summary": "City council votes 6-3 to approve 200-unit affordable housing development, overriding concerns from local residents.",
                "content": """The city council voted 6-3 Tuesday night to approve a controversial 200-unit affordable housing development on the former industrial site at Oak and Main Street, despite fierce opposition from neighborhood groups.

The Riverside Commons project, developed by Community Housing Partners, will provide housing for families earning 60% or less of the area median income. Units will range from studios to three-bedroom apartments, with rents capped at $850-$1,400 per month.

Supporters argue the project addresses the city's critical shortage of affordable housing. Over 2,000 families are currently on the waiting list for housing assistance, and median rents have increased 45% over the past five years.

Opponents, including the Riverside Neighborhood Association, raised concerns about traffic, parking, and strain on local schools. Some residents questioned whether the development would change the character of their neighborhood.

Construction is expected to begin in spring 2025, with the first units available by late 2026. The project includes a community center, playground, and green space.""",
                "category": "Housing",
                "cover_image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[4] if len(topic_ids) > 4 else None,
                "status": "published",
                "view_count": 1432,
                "reading_time_minutes": 7,
                "published_at": datetime.utcnow() - timedelta(days=14),
            },
            {
                "title": "Police Department Launches Body Camera Program",
                "slug": "police-body-camera-program-launch",
                "summary": "All patrol officers will be equipped with body cameras by end of year in effort to increase transparency and accountability.",
                "content": """The police department officially launched its body camera program Monday, equipping the first 50 officers with recording devices as part of a phased rollout that will cover all 200 patrol officers by year's end.

Police Chief Thomas Bradley called the $1.2 million program 'a significant step toward transparency and accountability.' The cameras will automatically activate when officers turn on their sirens or draw their weapons, and officers can also manually activate them during citizen encounters.

The program follows years of advocacy from civil rights groups and comes after several controversial incidents involving police use of force. Footage will be retained for 90 days, with longer retention for incidents involving arrests or use of force.

Privacy advocates have raised concerns about when cameras should be turned off, particularly in private homes or when interviewing victims of domestic violence. The department's policy allows officers to deactivate cameras in these sensitive situations, but they must document the reason.

The city has also hired two full-time staff members to manage the footage and respond to public records requests.""",
                "category": "Public Safety",
                "cover_image_url": "https://images.unsplash.com/photo-1587731556938-38755b4803a6?w=800",
                "author_id": demo_writer.id,
                "topic_id": topic_ids[5] if len(topic_ids) > 5 else None,
                "status": "published",
                "view_count": 2891,
                "reading_time_minutes": 8,
                "published_at": datetime.utcnow() - timedelta(days=1),
            },
        ]

        for article_data in articles_data:
            article = DemoArticle(**article_data)
            self.articles[article.id] = article

        # Create demo ratings with multi-criteria
        article_ids = list(self.articles.keys())
        if article_ids:
            # Ratings for article 0 (Solar Panels)
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

            # Ratings for article 1 (City Budget)
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

            # Ratings for article 2 (Mental Health)
            if len(article_ids) > 2:
                rating3 = DemoRating(
                    article_id=article_ids[2],
                    user_id=demo_reader.id,
                    rating=5,
                    feedback="Important topic covered with empathy and depth. Great resource list.",
                    accuracy_rating=5,
                    sources_rating=5,
                    writing_quality_rating=5,
                    originality_rating=4,
                    depth_rating=5,
                    bias_rating=5,
                )
                self.ratings[rating3.id] = rating3

            # Ratings for article 3 (Teacher Shortage)
            if len(article_ids) > 3:
                rating4 = DemoRating(
                    article_id=article_ids[3],
                    user_id=demo_reader.id,
                    rating=4,
                    feedback="Well-researched article highlighting a critical issue.",
                    accuracy_rating=5,
                    sources_rating=4,
                    writing_quality_rating=4,
                    originality_rating=4,
                    depth_rating=4,
                    bias_rating=4,
                )
                self.ratings[rating4.id] = rating4

            # Ratings for article 4 (Affordable Housing)
            if len(article_ids) > 4:
                rating5 = DemoRating(
                    article_id=article_ids[4],
                    user_id=demo_reader.id,
                    rating=4,
                    feedback="Balanced coverage of both sides of this controversial issue.",
                    accuracy_rating=5,
                    sources_rating=4,
                    writing_quality_rating=4,
                    originality_rating=3,
                    depth_rating=4,
                    bias_rating=5,
                )
                self.ratings[rating5.id] = rating5

            # Ratings for article 5 (Police Body Cameras)
            if len(article_ids) > 5:
                rating6 = DemoRating(
                    article_id=article_ids[5],
                    user_id=demo_reader.id,
                    rating=5,
                    feedback="Thorough examination of the body camera program with good privacy discussion.",
                    accuracy_rating=5,
                    sources_rating=5,
                    writing_quality_rating=5,
                    originality_rating=4,
                    depth_rating=5,
                    bias_rating=5,
                )
                self.ratings[rating6.id] = rating6

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

    def get_topics(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> List[DemoTopic]:
        """Get list of topics with filtering support."""
        topics = list(self.topics.values())

        # Filter by category
        if category:
            topics = [t for t in topics if t.category == category]

        # Filter by tags (topic must have at least one matching tag)
        if tags:
            topics = [
                t for t in topics
                if any(tag in t.tags for tag in tags)
            ]

        # Search in title and description
        if search:
            search_lower = search.lower()
            topics = [
                t for t in topics
                if search_lower in t.title.lower() or search_lower in t.description.lower()
            ]

        # Sort by vote count
        sorted_topics = sorted(topics, key=lambda t: t.vote_count, reverse=True)

        return sorted_topics[skip:skip + limit]

    def get_topic_by_id(self, topic_id: UUID) -> Optional[DemoTopic]:
        """Get topic by ID."""
        return self.topics.get(topic_id)

    def track_user_interest(
        self,
        user_id: UUID,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        topic_id: Optional[UUID] = None,
        article_id: Optional[UUID] = None
    ):
        """Track user interests for personalization."""
        # Get or create user interest record
        if user_id not in self.user_interests:
            self.user_interests[user_id] = DemoUserInterest(user_id=user_id)

        interest = self.user_interests[user_id]

        # Update category scores
        if category:
            interest.category_scores[category] = interest.category_scores.get(category, 0) + 1

        # Update tag scores
        if tags:
            for tag in tags:
                interest.tag_scores[tag] = interest.tag_scores.get(tag, 0) + 1

        # Track voted topics
        if topic_id and topic_id not in interest.voted_topic_ids:
            interest.voted_topic_ids.append(topic_id)

        # Track read articles
        if article_id and article_id not in interest.read_article_ids:
            interest.read_article_ids.append(article_id)

        interest.updated_at = datetime.utcnow()

    def get_recommended_topics(self, user_id: UUID, limit: int = 10) -> List[DemoTopic]:
        """Get personalized topic recommendations based on user interests."""
        # Get user interests
        interest = self.user_interests.get(user_id)

        # If no interests yet, return trending topics
        if not interest or (not interest.category_scores and not interest.tag_scores):
            return self.get_topics(limit=limit)

        # Score topics based on user interests
        scored_topics = []
        for topic in self.topics.values():
            score = 0

            # Skip topics the user has already voted on
            if topic.id in (interest.voted_topic_ids if interest else []):
                continue

            # Score based on category match
            if topic.category in interest.category_scores:
                score += interest.category_scores[topic.category] * 10

            # Score based on tag matches
            for tag in topic.tags:
                if tag in interest.tag_scores:
                    score += interest.tag_scores[tag] * 5

            # Add base popularity score (trending topics get a boost)
            score += topic.vote_count * 0.1

            scored_topics.append((score, topic))

        # Sort by score and return top results
        scored_topics.sort(key=lambda x: x[0], reverse=True)
        return [topic for score, topic in scored_topics[:limit]]


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
