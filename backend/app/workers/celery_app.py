"""
Celery worker for background tasks
"""
from celery import Celery

from .core.config import settings

celery_app = Celery(
    "versemusic",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.render_tasks",
        "app.workers.social_tasks",
        "app.workers.analytics_tasks",
        "app.workers.media_tasks",
        "app.workers.runtime_tasks",
        "app.workers.ai_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Task routes
celery_app.conf.task_routes = {
    "app.workers.render_tasks.*": {"queue": "render"},
    "app.workers.social_tasks.*": {"queue": "social"},
    "app.workers.analytics_tasks.*": {"queue": "analytics"},
    "app.workers.media_tasks.*": {"queue": "media"},
    "app.workers.runtime_tasks.*": {"queue": "runtime"},
    "app.workers.ai_tasks.*": {"queue": "ai"},
}


@celery_app.task(bind=True, name="health_check")
def health_check(self):
    """Health check task"""
    return {"status": "healthy"}


if __name__ == "__main__":
    celery_app.start()