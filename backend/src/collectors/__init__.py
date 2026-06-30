"""Collection layer: pluggable vendor fetch → normalize → dedup.

Collectors implement the :class:`~src.collectors.base.Collector` protocol so price,
news, and search vendors are interchangeable. Output flows through the normalizer to
a common schema and the dedup gate before reaching the memory layer.
"""
