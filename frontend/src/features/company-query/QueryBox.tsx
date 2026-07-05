"use client";

import * as React from "react";
import { Send } from "lucide-react";
import { cn } from "@/utils/cn";

const MEMORY_PREFIX = "remember:";

/** True when the draft is a "remember:" memory directive (case-insensitive). */
export function isMemoryDirective(text: string): boolean {
  return text.trimStart().toLowerCase().startsWith(MEMORY_PREFIX);
}

/** Strip the "remember:" prefix to get the bare preference text. */
export function extractPreference(text: string): string {
  const trimmed = text.trim();
  return trimmed.slice(MEMORY_PREFIX.length).trim() || trimmed;
}

export interface QueryBoxProps {
  ticker: string;
  disabled?: boolean;
  onAsk: (question: string) => void;
  /** Seed the draft (from a dashboard "What can I ask?" chip). Not auto-sent. */
  initialValue?: string;
}

/**
 * Natural-language query input. Typing a "remember:" directive glows the border
 * emerald and surfaces a "🧠 memory directive" label — making the mode-switch to
 * memory visible before the request is even sent.
 */
export function QueryBox({ ticker, disabled = false, onAsk, initialValue = "" }: QueryBoxProps) {
  const [question, setQuestion] = React.useState(initialValue);
  const directive = isMemoryDirective(question);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || disabled) return;
    onAsk(q);
    setQuestion("");
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-1.5">
      <div className="flex h-5 items-center">
        {directive ? (
          <span className="animate-fade-in-up inline-flex items-center gap-1 text-[12px] font-medium text-primary">
            🧠 memory directive
          </span>
        ) : null}
      </div>
      <div
        className={cn(
          "flex items-center gap-2 rounded-xl border bg-surface p-1.5 pl-3 transition-all duration-200",
          directive
            ? "animate-focus-glow border-primary/70"
            : "border-border focus-within:border-primary/50",
        )}
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={`Ask about ${ticker}…  (or "remember: …")`}
          aria-label="Question"
          disabled={disabled}
          className="h-9 flex-1 bg-transparent text-[15px] text-foreground placeholder:text-text-muted focus-visible:outline-none disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={disabled || !question.trim()}
          className="inline-flex h-9 items-center gap-1.5 rounded-lg bg-primary px-4 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          {disabled ? "Asking…" : "Ask"}
        </button>
      </div>
    </form>
  );
}
