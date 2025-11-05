"""
Celery configuration for async tasks.
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "citizen_journalism",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL),
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    # Update trending scores every 15 minutes
    "update-trending-topics": {
        "task": "app.tasks.topics.update_trending_scores",
        "schedule": crontab(minute="*/15"),
    },
    # Calculate writer ratings daily
    "calculate-writer-ratings": {
        "task": "app.tasks.users.calculate_writer_ratings",
        "schedule": crontab(hour=2, minute=0),  # 2 AM UTC
    },
    # Process pending payouts weekly
    "process-payouts": {
        "task": "app.tasks.payments.process_weekly_payouts",
        "schedule": crontab(day_of_week=1, hour=3, minute=0),  # Monday 3 AM UTC
    },
    # Clean up old drafts monthly
    "cleanup-old-drafts": {
        "task": "app.tasks.articles.cleanup_old_drafts",
        "schedule": crontab(day_of_month=1, hour=4, minute=0),  # 1st of month, 4 AM UTC
    },
}

# Task discovery
celery_app.autodiscover_tasks(
    [
        "app.tasks",
    ]
)
