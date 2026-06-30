"""AI answer-generation layer.

Turns Cognee's retrieved context into a cited natural-language answer via Anthropic
Claude. Prompt templates (the source of truth) live in ``prompt_templates.py``; the
single LLM call lives in ``answer_formatter.py``. This layer never imports Cognee.
"""
