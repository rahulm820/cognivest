"""Answer formatter: Cognee results → Claude → cited answer.

A single, stateless Claude call per user query, grounded in the context retrieved by
Cognee. No multi-agent orchestration in v1 (ARCHITECTURE.md §6). The Anthropic client
is constructed here (this layer owns the LLM call); the model defaults to
``settings.llm_model`` (``claude-opus-4-8``).
"""

from __future__ import annotations

from typing import Any

from src.ai.prompt_templates import SYSTEM_PROMPT, render_answer_prompt
from src.config.settings import get_settings
from src.schemas.query import Citation, QueryResponse


def _build_context_block(results: list[dict[str, Any]]) -> tuple[str, list[Citation]]:
    """Assemble a numbered context block + parallel citation list from hits.

    Args:
        results: Ranked retrieval hits from the memory layer.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    # TODO(phase-4): number passages [1..n], extract source_url/published_at -> Citation
    raise NotImplementedError("TODO(phase-4): implement context-block assembly")


async def format_answer(
    *,
    ticker: str,
    question: str,
    results: list[dict[str, Any]],
) -> QueryResponse:
    """Build the grounded prompt, call Claude, and return a cited answer.

    Args:
        ticker: The company ticker scoping the query.
        question: The user's natural-language question.
        results: Ranked retrieval hits from ``memory_service.search``.

    Returns:
        A :class:`QueryResponse` with the answer, citations, and graph snippet.

    Raises:
        NotImplementedError: Always, in the scaffold phase.
    """
    settings = get_settings()
    _ = SYSTEM_PROMPT  # system prompt sent verbatim to the LLM
    _ = render_answer_prompt  # user prompt rendered from template
    _ = settings.llm_model  # default model: claude-opus-4-8
    # TODO(phase-4):
    #   1. context_block, citations = _build_context_block(results)
    #   2. call anthropic client (model=settings.llm_model, max_tokens=settings.llm_max_tokens)
    #      with SYSTEM_PROMPT + render_answer_prompt(...)
    #   3. parse answer text, attach citations + graph snippet -> QueryResponse
    raise NotImplementedError("TODO(phase-4): implement Claude answer formatting")
