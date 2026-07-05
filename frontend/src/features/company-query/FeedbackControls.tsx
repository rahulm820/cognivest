"use client";

import * as React from "react";
import { ThumbsUp, ThumbsDown, Send } from "lucide-react";
import { useReflection, isNotImplemented } from "@/hooks";
import { cn } from "@/utils/cn";

export interface FeedbackControlsProps {
  ticker: string;
  question: string;
}

type Phase = "idle" | "correcting" | "done" | "unavailable";

/**
 * Answer feedback: 👍 / 👎 ghost buttons. 👎 expands a one-line correction input.
 * Submits to POST /memory/reflection with the demo identity header.
 *  - success → the control morphs to "✓ feedback stored — future answers adapt"
 *  - 501 → controls disable with a "coming online shortly" tooltip (never a toast)
 */
export function FeedbackControls({ ticker, question }: FeedbackControlsProps) {
  const [phase, setPhase] = React.useState<Phase>("idle");
  const [correction, setCorrection] = React.useState("");
  const reflection = useReflection();

  // Auto-reset the "done" morph after 3s, back to a quiet resting state.
  React.useEffect(() => {
    if (phase !== "done") return;
    const id = setTimeout(() => setPhase("idle"), 3000);
    return () => clearTimeout(id);
  }, [phase]);

  function submit(helpful: boolean, feedbackText: string) {
    reflection.mutate(
      { ticker, question, feedbackText, helpful },
      {
        onSuccess: () => {
          setCorrection("");
          setPhase("done");
        },
        onError: (err) => {
          if (isNotImplemented(err)) setPhase("unavailable");
          // Any other error: stay put silently (no error toast, per spec).
        },
      },
    );
  }

  if (phase === "done") {
    return (
      <p className="animate-fade-in-up mt-3 text-[12px] text-text-muted">
        ✓ feedback stored — future answers adapt
      </p>
    );
  }

  if (phase === "unavailable") {
    return (
      <div className="group relative mt-3 inline-flex">
        <span className="cursor-not-allowed text-[12px] text-text-muted/70">
          feedback · unavailable
        </span>
        <span
          role="tooltip"
          className="pointer-events-none absolute -top-8 left-0 whitespace-nowrap rounded-md border border-border bg-surface-raised px-2 py-1 text-[11px] text-foreground opacity-0 shadow-elevated transition-opacity duration-150 group-hover:opacity-100"
        >
          coming online shortly
        </span>
      </div>
    );
  }

  const busy = reflection.isPending;

  return (
    <div className="mt-3">
      <div className="flex items-center gap-1">
        <span className="mr-1 text-[12px] text-text-muted">Was this helpful?</span>
        <button
          type="button"
          onClick={() => submit(true, "")}
          disabled={busy}
          aria-label="Helpful"
          className="rounded-md p-1.5 text-text-muted transition-colors hover:bg-surface-raised hover:text-primary disabled:opacity-50"
        >
          <ThumbsUp className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={() => setPhase((p) => (p === "correcting" ? "idle" : "correcting"))}
          disabled={busy}
          aria-label="Not helpful"
          className={cn(
            "rounded-md p-1.5 transition-colors hover:bg-surface-raised hover:text-danger disabled:opacity-50",
            phase === "correcting" ? "text-danger" : "text-text-muted",
          )}
        >
          <ThumbsDown className="h-4 w-4" />
        </button>
      </div>

      {phase === "correcting" ? (
        <form
          className="animate-fade-in-up mt-2 flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (!correction.trim() || busy) return;
            submit(false, correction.trim());
          }}
        >
          <input
            value={correction}
            onChange={(e) => setCorrection(e.target.value)}
            placeholder="What was off? (helps future answers)"
            aria-label="Correction"
            autoFocus
            className="h-9 flex-1 rounded-lg border border-border bg-surface px-3 text-[13px] text-foreground placeholder:text-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
          <button
            type="submit"
            disabled={busy || !correction.trim()}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg bg-primary px-3 text-[13px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
          >
            <Send className="h-3.5 w-3.5" />
            Send
          </button>
        </form>
      ) : null}
    </div>
  );
}
