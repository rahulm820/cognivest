"""Celery tasks: per-ticker collection + cognify.

Every task is idempotent (dedup before ``cognee.add()``), retried with exponential
backoff, and routed to a dead-letter queue after exhausting retries (DLQ wiring is a
later-phase concern — noted below). Task bodies are stubs in this scaffold.

DLQ note: on final failure (``max_retries`` exhausted) the task should publish the
payload to a dedicated dead-letter queue for inspection/replay rather than silently
dropping it. Wire this via a custom ``on_failure`` handler in phase 6.
"""

from __future__ import annotations

from src.workers.celery_app import celery_app

# Retry policy shared by collection tasks.
_RETRY_KWARGS = {"max_retries": 5, "countdown": 10}  # exponential backoff applied per-retry


@celery_app.task(
    name="src.workers.tasks.collect_price_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs=_RETRY_KWARGS,
    acks_late=True,
)
def collect_price_task(self: object, ticker: str) -> int:
    """Collect price bars for a ticker and ingest new items.

    Idempotent: dedup runs before ingestion. Returns the count of NEW items.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-2): run CollectorService.run_for_ticker(ticker, PriceCollector())
    #               inside an event loop; enqueue cognify_task on success.
    raise NotImplementedError("TODO(phase-2): implement collect_price_task")


@celery_app.task(
    name="src.workers.tasks.collect_news_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs=_RETRY_KWARGS,
    acks_late=True,
)
def collect_news_task(self: object, ticker: str) -> int:
    """Collect news/web content for a ticker and ingest new items.

    Idempotent: dedup runs before ingestion. Returns the count of NEW items.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-2): run CollectorService.run_for_ticker(ticker, NewsCollector());
    #               enqueue cognify_task on success.
    raise NotImplementedError("TODO(phase-2): implement collect_news_task")


@celery_app.task(
    name="src.workers.tasks.cognify_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs=_RETRY_KWARGS,
    acks_late=True,
)
def cognify_task(self: object, ticker: str) -> None:
    """Run the decoupled ``cognee.cognify`` graph build for a ticker.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-3): run MemoryService.reflect(ticker) / cognify for the dataset.
    raise NotImplementedError("TODO(phase-3): implement cognify_task")
