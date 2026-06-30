"""Celery workers package: app + scheduled collection tasks.

Queues: ``price``, ``news``, ``cognify`` (independently scalable). ``cognify`` is
decoupled so a slow graph build never blocks fetching.
"""
