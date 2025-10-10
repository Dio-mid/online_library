from datetime import timedelta

from celery import Celery

from src.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    include=[
        "src.tasks.notifications",
        "src.tasks.maintenance",
    ],
)

celery_app.conf.beat_schedule = {
    "refresh-materialized-views": {
        "task": "src.tasks.maintenance.refresh_materialized_views",
        "schedule": timedelta(minutes=30),
    },
    "cleanup-redis-cache": {
        "task": "src.tasks.maintenance.cleanup_redis_cache",
        "schedule": timedelta(hours=1),
    },
}