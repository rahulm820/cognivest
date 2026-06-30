#!/usr/bin/env python3
"""Offline evaluation harness for Cognivest answer generation.

Loads a fixture set of questions, calls the query API for each, and scores the
returned answers for citation accuracy, groundedness, and latency.

Scaffold phase: the scoring/orchestration body is intentionally a stub marked
``# TODO(phase-4)``. See ai/eval/README.md and docs/prompting.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EvalCase:
    """A single evaluation fixture."""

    ticker: str
    question: str
    date_range: dict[str, str] | None = None
    # Gold expectations (e.g. expected supporting URLs, or "insufficient_context").
    expected: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalResult:
    """Scored outcome for one case."""

    case: EvalCase
    citation_accuracy: float = 0.0
    groundedness: float = 0.0
    latency_ms: float = 0.0
    passed: bool = False


def load_cases(dataset_path: Path) -> list[EvalCase]:
    """Load evaluation cases from a JSONL fixture file (one JSON object per line)."""
    cases: list[EvalCase] = []
    with dataset_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            cases.append(
                EvalCase(
                    ticker=obj["ticker"],
                    question=obj["question"],
                    date_range=obj.get("date_range"),
                    expected=obj.get("expected", {}),
                )
            )
    return cases


def run_case(case: EvalCase, api_base: str) -> EvalResult:
    """Call the query API for a single case and score the response.

    TODO(phase-4): POST {question, date_range} to
    f"{api_base}/companies/{case.ticker}/query", measure latency, then score
    citation accuracy (cited [index] -> supporting passage) and groundedness
    (claims supported by retrieved context). See ai/eval/README.md.
    """
    raise NotImplementedError("TODO(phase-4): implement query call + scoring")


def summarize(results: list[EvalResult]) -> dict[str, float]:
    """Aggregate per-case results into summary metrics.

    TODO(phase-4): compute mean citation_accuracy / groundedness / p95 latency
    and a pass rate; compare against the stored baseline.
    """
    raise NotImplementedError("TODO(phase-4): implement aggregation")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cognivest offline answer-quality evaluation.")
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Path to a JSONL fixture file of evaluation cases.",
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000/api/v1",
        help="Base URL of the backend API (default: %(default)s).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path to write the JSON results report.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cases = load_cases(args.dataset)
    print(f"Loaded {len(cases)} evaluation case(s) from {args.dataset}")

    # TODO(phase-4): run each case, summarize, write report, and exit non-zero
    # if scores regress below the baseline thresholds.
    raise NotImplementedError("TODO(phase-4): wire run_case -> summarize -> report")


if __name__ == "__main__":
    sys.exit(main())
