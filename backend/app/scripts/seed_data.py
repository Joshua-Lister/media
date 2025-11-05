"""
Seed database with dummy data for testing.

Run with: python -m app.scripts.seed_data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User
from app.models.article import Article
from app.models.topic import Topic
from datetime import datetime, timedelta
from uuid import uuid4


# Dummy article data
DUMMY_ARTICLES = [
    {
        "title": "The Rise of Citizen Journalism in the Digital Age",
        "summary": "Exploring how everyday people are becoming powerful voices in media through digital platforms and social networks.",
        "content": """# The Rise of Citizen Journalism in the Digital Age

In an era where information travels at the speed of light, citizen journalism has emerged as a powerful force in shaping public discourse. No longer confined to traditional media gatekeepers, everyday individuals are now equipped with the tools to report, analyze, and share news that matters to their communities.

## The Democratization of News

The smartphone revolution has put a newsroom in everyone's pocket. With high-quality cameras, instant internet connectivity, and social media platforms, citizens can document events as they unfold, often beating traditional media to breaking news.

### Key Advantages of Citizen Journalism

1. **Hyperlocal Coverage**: Citizens can cover stories that mainstream media might overlook
2. **Diverse Perspectives**: Multiple viewpoints create a richer understanding of events
3. **Real-time Reporting**: Eyewitness accounts provide immediate context
4. **Community Engagement**: Direct connection between reporters and audiences

## Challenges and Responsibilities

While citizen journalism offers tremendous benefits, it also comes with challenges. The need for fact-checking, ethical reporting standards, and avoiding misinformation is paramount.

### Best Practices

- Verify sources before sharing information
- Maintain objectivity and fairness
- Respect privacy and obtain consent when possible
- Clearly label opinion versus fact

## The Future of News

As we move forward, the line between professional and citizen journalism continues to blur. The future likely holds a collaborative model where both work together to inform and engage communities effectively.

The power of citizen journalism lies not just in its ability to report news, but in its capacity to give voice to the voiceless and hold power accountable. As technology continues to evolve, so too will the ways in which we gather, share, and consume information.""",
        "category": "Media",
        "tags": ["journalism", "media", "technology", "social-media"],
    },
    {
        "title": "Climate Change: Local Actions for Global Impact",
        "summary": "How individual communities are making a difference in the fight against climate change through innovative local initiatives.",
        "content": """# Climate Change: Local Actions for Global Impact

While world leaders debate climate policy, communities around the globe are taking matters into their own hands. From urban gardens to renewable energy cooperatives, local action is proving that change doesn't have to wait for top-down mandates.

## Community-Led Initiatives

### Urban Farming Revolution

Cities across the world are transforming vacant lots into thriving urban farms. These green spaces not only provide fresh, local food but also:
- Reduce carbon footprints from food transportation
- Create community gathering spaces
- Improve air quality and reduce urban heat islands
- Provide educational opportunities for youth

### Renewable Energy Cooperatives

Neighborhoods are banding together to invest in solar panels and wind turbines, creating:
- Lower energy costs for participants
- Reduced dependence on fossil fuels
- Local jobs in the green economy
- Models for sustainable community development

## Success Stories

**Portland, Oregon**: The city's network of community gardens has reduced food transportation emissions by an estimated 30% in participating neighborhoods.

**Copenhagen, Denmark**: Citizen-led cycling initiatives have made it the world's most bike-friendly city, with 62% of residents commuting by bicycle.

**Freiburg, Germany**: A grassroots movement transformed the city into a solar energy leader, with more solar panels per capita than any other German city.

## How You Can Get Involved

1. Start or join a community garden
2. Organize a neighborhood cleanup
3. Advocate for bike lanes and public transit
4. Support local renewable energy projects
5. Educate others about sustainable practices

## The Ripple Effect

When communities take action, the impact extends far beyond local boundaries. These initiatives inspire others, influence policy, and demonstrate that sustainable living is not only possible but beneficial for everyone.

Remember: Global change starts with local action. Your community has the power to make a difference.""",
        "category": "Environment",
        "tags": ["climate-change", "sustainability", "community", "environment"],
    },
    {
        "title": "Tech Giants and Data Privacy: What You Need to Know",
        "summary": "An in-depth look at how major technology companies collect, use, and monetize your personal data, and what you can do about it.",
        "content": """# Tech Giants and Data Privacy: What You Need to Know

Every click, like, and share contributes to a vast digital profile that tech companies use to target ads, predict behavior, and generate billions in revenue. Understanding how your data is collected and used is the first step toward protecting your privacy.

## The Data Collection Ecosystem

### What's Being Collected?

- **Browsing History**: Every website you visit
- **Location Data**: Where you go, when, and for how long
- **Social Connections**: Your network of friends, family, and colleagues
- **Purchase History**: What you buy and how much you spend
- **Communication Content**: Messages, emails, and calls
- **Behavioral Patterns**: Sleep schedules, app usage, exercise routines

### How It's Used

1. **Targeted Advertising**: Creating detailed profiles for ad targeting
2. **Product Development**: Improving services based on user behavior
3. **Predictive Analytics**: Anticipating future actions and preferences
4. **Third-Party Sales**: Sharing data with partners and advertisers

## Major Players and Their Practices

### Google
Collects data across search, email, maps, and Android devices to create comprehensive user profiles.

### Facebook/Meta
Tracks activity not just on their platforms but across the web through embedded Like buttons and pixels.

### Amazon
Monitors shopping behavior, voice commands (Alexa), and reading habits (Kindle) to refine recommendations.

### Apple
Takes a more privacy-focused approach but still collects significant data through iOS and services.

## Protecting Your Privacy

### Immediate Actions

1. **Review Privacy Settings**: Adjust settings on all your accounts
2. **Use Privacy-Focused Browsers**: Switch to Firefox, Brave, or DuckDuckGo
3. **Install Ad Blockers**: Reduce tracking across websites
4. **Use VPNs**: Encrypt your internet traffic
5. **Enable Two-Factor Authentication**: Secure your accounts

### Long-Term Strategies

- Read privacy policies (yes, really)
- Regularly audit app permissions
- Use encrypted messaging apps
- Consider de-Googling your digital life
- Support privacy-focused alternatives

## The Future of Data Privacy

New regulations like GDPR (Europe) and CCPA (California) are giving users more control over their data. However, true privacy protection requires both legal frameworks and individual vigilance.

## Conclusion

Your data is valuable—treat it accordingly. While complete privacy in the digital age may be impossible, informed choices can significantly reduce your exposure and protect your personal information.""",
        "category": "Technology",
        "tags": ["privacy", "technology", "data-security", "big-tech"],
    },
    {
        "title": "The Mental Health Crisis: Breaking the Stigma",
        "summary": "Examining the growing mental health challenges in modern society and the movement to normalize conversations about mental wellness.",
        "content": """# The Mental Health Crisis: Breaking the Stigma

Mental health has emerged from the shadows as one of the most pressing public health issues of our time. As rates of anxiety, depression, and other mental health conditions rise, society is finally beginning to acknowledge that mental wellness is just as important as physical health.

## Understanding the Crisis

### Alarming Statistics

- 1 in 5 adults experience mental illness each year
- Suicide rates have increased by 35% since 1999
- Depression is the leading cause of disability worldwide
- Only 43% of those with mental illness receive treatment

### Contributing Factors

1. **Social Media**: Constant comparison and FOMO (fear of missing out)
2. **Work Culture**: Burnout and lack of work-life balance
3. **Economic Stress**: Financial insecurity and job instability
4. **Isolation**: Decreased social connections despite digital connectivity
5. **Global Uncertainty**: Climate change, pandemics, political polarization

## Breaking Down Barriers

### The Stigma Challenge

For decades, mental health issues were hidden, whispered about, or dismissed. Those struggling often faced:
- Discrimination in employment and education
- Social isolation and judgment
- Self-blame and shame
- Barriers to accessing care

### Changing the Narrative

Today's mental health movement is characterized by:
- **Open Dialogue**: Public figures sharing their struggles
- **Workplace Initiatives**: Employee assistance programs and mental health days
- **Educational Programs**: Teaching emotional intelligence and coping skills
- **Accessible Services**: Teletherapy and mental health apps
- **Peer Support**: Online communities and support groups

## Practical Steps for Mental Wellness

### Daily Practices

1. **Mindfulness and Meditation**: Even 5 minutes daily can help
2. **Physical Exercise**: Movement improves mood and reduces anxiety
3. **Quality Sleep**: Aim for 7-9 hours consistently
4. **Social Connection**: Nurture relationships with friends and family
5. **Limit Screen Time**: Especially social media

### When to Seek Help

Don't wait for a crisis. Consider professional help if you experience:
- Persistent sadness or anxiety
- Changes in sleep or appetite
- Difficulty concentrating
- Loss of interest in activities
- Thoughts of self-harm

### Resources

- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **NAMI**: National Alliance on Mental Illness
- **BetterHelp** and **Talkspace**: Online therapy platforms

## Creating Supportive Communities

### What You Can Do

1. **Listen Without Judgment**: Sometimes people just need to be heard
2. **Share Your Story**: Your vulnerability helps others feel less alone
3. **Check In Regularly**: A simple "how are you really doing?" can matter
4. **Educate Yourself**: Learn about mental health to better support others
5. **Advocate for Change**: Support mental health funding and policies

## The Path Forward

Breaking the mental health stigma requires collective effort. By normalizing conversations about mental wellness, supporting those who struggle, and prioritizing our own mental health, we create a society where everyone can thrive.

Remember: Seeking help is not a sign of weakness—it's a courageous step toward healing. Mental health is health, and everyone deserves support on their journey to wellness.""",
        "category": "Health",
        "tags": ["mental-health", "wellness", "society", "healthcare"],
    },
    {
        "title": "The Future of Work: Remote, Hybrid, or Back to Office?",
        "summary": "Analyzing how the pandemic transformed workplace culture and what the future holds for how and where we work.",
        "content": """# The Future of Work: Remote, Hybrid, or Back to Office?

The COVID-19 pandemic forced the world's largest work-from-home experiment, fundamentally changing how millions of people think about work. As we move forward, organizations and employees are grappling with what the "new normal" should look like.

## The Great Workplace Transformation

### Before the Pandemic

Traditional office work was characterized by:
- 9-to-5 schedules in physical offices
- Long commutes as part of daily routine
- In-person meetings and collaboration
- Limited flexibility in work location
- Face time equated with productivity

### The Remote Revolution

The shift to remote work revealed:
- Technology enables collaboration from anywhere
- Many jobs don't require physical presence
- Employees value flexibility and autonomy
- Productivity often increases with remote work
- Work-life balance can be improved (or worsened)

## The Three Models

### Fully Remote

**Advantages:**
- Access to global talent pool
- Reduced office costs
- Improved work-life balance
- Increased productivity for many
- Environmental benefits (less commuting)

**Challenges:**
- Isolation and mental health concerns
- Difficulty separating work and home life
- Challenges in building company culture
- Communication gaps
- Career development and mentorship

### Hybrid Work

**Advantages:**
- Flexibility for employees
- Maintains some in-person collaboration
- Reduced but not eliminated office space
- Better work-life balance
- Accommodates different work styles

**Challenges:**
- Coordination complexity
- Potential for two-tier culture
- Technology requirements
- Scheduling difficulties
- Unclear expectations

### Back to Office

**Advantages:**
- Direct collaboration and innovation
- Stronger company culture
- Clear work boundaries
- Easier onboarding and mentorship
- Spontaneous interactions

**Challenges:**
- Commute time and costs
- Less flexibility
- Higher overhead costs
- May lose talent to remote opportunities
- Environmental impact

## What Employees Want

Recent surveys show:
- 83% of employees want hybrid or remote options
- 55% would look for a new job if forced back full-time
- 67% say flexibility is more important than salary
- 76% report higher productivity working remotely
- 89% want autonomy in choosing work location

## What's Actually Working

### Successful Hybrid Models

Companies finding success typically:
1. **Set Clear Expectations**: Define in-office days and purposes
2. **Invest in Technology**: Ensure seamless remote collaboration
3. **Focus on Outcomes**: Measure results, not hours
4. **Maintain Culture**: Intentional team building and connection
5. **Provide Flexibility**: Allow individual and team preferences

### Best Practices

- **Asynchronous Communication**: Don't require real-time responses
- **Digital-First Meetings**: Include remote participants equally
- **Office Redesign**: Transform to collaboration spaces, not cubicles
- **Regular Check-ins**: Maintain connection and support
- **Flexible Schedules**: Trust employees to manage their time

## The Future is Flexible

The future of work won't be one-size-fits-all. Successful organizations will:
- Embrace flexibility as a core value
- Design work around outcomes, not location
- Invest in technology and training
- Prioritize employee well-being
- Adapt based on feedback and results

## Industry Variations

Different sectors will evolve differently:
- **Tech**: Leading remote and hybrid adoption
- **Finance**: Mixed, with some traditional firms mandating office return
- **Healthcare**: Limited remote options for patient care
- **Education**: Hybrid learning becoming more common
- **Manufacturing**: On-site requirements with flexible scheduling

## Preparing for Tomorrow

### For Employees

1. Develop strong communication skills
2. Build self-discipline and time management
3. Invest in home office setup
4. Maintain work-life boundaries
5. Network intentionally in remote settings

### For Employers

1. Trust your employees
2. Measure what matters (outcomes over presence)
3. Provide tools and resources for success
4. Communicate clearly and often
5. Be willing to experiment and adjust

## Conclusion

The future of work is not about returning to how things were or fully embracing remote work—it's about finding what works best for each organization and individual. Flexibility, trust, and adaptability will be the hallmarks of successful workplaces in the years to come.

The pandemic didn't just change where we work; it changed how we think about work itself. Organizations that embrace this transformation will thrive, while those clinging to the past may struggle to attract and retain top talent.""",
        "category": "Business",
        "tags": ["future-of-work", "remote-work", "business", "workplace-culture"],
    },
]

# Dummy topics
DUMMY_TOPICS = [
    {
        "title": "Investigating Local Government Transparency",
        "description": "A deep dive into how accessible local government records and meetings are to citizens, and what can be improved.",
        "category": "Politics",
    },
    {
        "title": "The Impact of AI on Creative Industries",
        "description": "Exploring how artificial intelligence is changing music, art, writing, and other creative fields.",
        "category": "Technology",
    },
    {
        "title": "Community Solutions to Food Deserts",
        "description": "Documenting innovative approaches communities are taking to address lack of access to fresh, healthy food.",
        "category": "Community",
    },
]


async def seed_database():
    """Seed the database with dummy data."""
    print("🌱 Starting database seeding...")

    # Create async engine
    DATABASE_URL = str(settings.DATABASE_URL).replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        # Create demo users
        print("Creating demo users...")

        demo_users = [
            User(
                id=uuid4(),
                email="admin@example.com",
                username="admin",
                full_name="Admin User",
                password_hash=get_password_hash("admin123!@#"),
                is_verified=True,
                is_superuser=True,
                is_writer=True,
                bio="Platform administrator and journalist",
            ),
            User(
                id=uuid4(),
                email="writer1@example.com",
                username="sarah_journalist",
                full_name="Sarah Johnson",
                password_hash=get_password_hash("Writer123!@#"),
                is_verified=True,
                is_writer=True,
                writer_verified=True,
                bio="Investigative journalist focusing on social issues and community stories.",
                expertise_tags='["journalism", "social-issues", "community"]',
                writer_rating=450,  # 4.5 * 100
            ),
            User(
                id=uuid4(),
                email="writer2@example.com",
                username="mike_tech",
                full_name="Mike Chen",
                password_hash=get_password_hash("Writer123!@#"),
                is_verified=True,
                is_writer=True,
                writer_verified=True,
                bio="Technology writer and analyst covering AI, privacy, and digital trends.",
                expertise_tags='["technology", "AI", "privacy", "cybersecurity"]',
                writer_rating=480,  # 4.8 * 100
            ),
            User(
                id=uuid4(),
                email="reader@example.com",
                username="john_reader",
                full_name="John Doe",
                password_hash=get_password_hash("Reader123!@#"),
                is_verified=True,
                is_writer=False,
                bio="Passionate reader interested in current events and technology.",
            ),
        ]

        for user in demo_users:
            db.add(user)

        await db.commit()
        print(f"✅ Created {len(demo_users)} users")

        # Refresh users to get IDs
        for user in demo_users:
            await db.refresh(user)

        writer1 = demo_users[1]
        writer2 = demo_users[2]

        # Create topics
        print("Creating topics...")
        demo_topics = []
        for topic_data in DUMMY_TOPICS:
            topic = Topic(
                id=uuid4(),
                proposed_by_id=demo_users[3].id,  # reader
                title=topic_data["title"],
                description=topic_data["description"],
                category=topic_data["category"],
                upvotes=int(15 + (hash(topic_data["title"]) % 30)),
                downvotes=int(2 + (hash(topic_data["title"]) % 5)),
                created_at=datetime.utcnow() - timedelta(days=5),
            )
            topic.vote_score = topic.upvotes - topic.downvotes
            demo_topics.append(topic)
            db.add(topic)

        await db.commit()
        print(f"✅ Created {len(demo_topics)} topics")

        # Create articles
        print("Creating articles...")
        for i, article_data in enumerate(DUMMY_ARTICLES):
            # Alternate between writers
            author = writer1 if i % 2 == 0 else writer2

            from slugify import slugify
            slug = slugify(article_data["title"])

            article = Article(
                id=uuid4(),
                author_id=author.id,
                title=article_data["title"],
                slug=slug,
                summary=article_data["summary"],
                content=article_data["content"],
                category=article_data["category"],
                tags=str(article_data["tags"]),
                status="published",
                reading_time_minutes=len(article_data["content"].split()) // 200 + 1,
                view_count=100 + (i * 50),
                unique_view_count=80 + (i * 30),
                average_rating=4.2 + (i * 0.1),
                rating_count=15 + (i * 5),
                published_at=datetime.utcnow() - timedelta(days=7 - i),
                created_at=datetime.utcnow() - timedelta(days=10 - i),
            )
            db.add(article)

        await db.commit()
        print(f"✅ Created {len(DUMMY_ARTICLES)} articles")

    print("\n🎉 Database seeding completed successfully!")
    print("\n📝 Demo Credentials:")
    print("=" * 50)
    print("Admin User:")
    print("  Email: admin@example.com")
    print("  Password: admin123!@#")
    print("\nWriter 1:")
    print("  Email: writer1@example.com")
    print("  Password: Writer123!@#")
    print("\nWriter 2:")
    print("  Email: writer2@example.com")
    print("  Password: Writer123!@#")
    print("\nReader:")
    print("  Email: reader@example.com")
    print("  Password: Reader123!@#")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_database())
