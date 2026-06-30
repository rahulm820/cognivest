"""Celery application.

Broker/result backend come from settings (Redis). Three queues — ``price``, ``news``,
``cognify`` — allow independent scaling/throttling. A Celery Beat schedule placeholder
is defined for per-ticker periodic collection (populated dynamically per watchlist in
a later phase).
"""

from __future__ import annotations

from celery import Celery

from src.config.logging import configure_logging
from src.config.settings import get_settings

settings = get_settings()
configure_logging(settings)

celery_app = Celery(
    "cognivest",
    broker=str(settings.celery_broker_url),
    backend=str(settings.celery_result_backend),
    include=["src.workers.tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue="news",
    task_track_started=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    # Route each task type to its dedicated queue.
    task_routes={
        "src.workers.tasks.collect_price_task": {"queue": "price"},
        "src.workers.tasks.collect_news_task": {"queue": "news"},
        "src.workers.tasks.cognify_task": {"queue": "cognify"},
    },
    # TODO(phase-6): populate the beat schedule per watchlisted ticker.
    # Placeholder: global cadences sourced from settings.
    beat_schedule={
        # "collect-news-every-2h": {
        #     "task": "src.workers.tasks.collect_news_task",
        #     "schedule": settings.news_collect_interval_hours * 3600,
        #     "args": (),
        # },
    },
)

__all__ = ["celery_app"]
