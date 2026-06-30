"""Service layer: business logic / orchestration.

Services coordinate repositories, collectors, the memory seam, and the AI layer.
They never import routers. ``memory_service`` is the ONLY caller of the Cognee client.
"""
