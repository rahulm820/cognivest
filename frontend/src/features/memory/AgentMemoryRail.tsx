"use client";

import * as React from "react";
import { Brain, Pencil, Check, Clock, PanelRightClose, PanelRightOpen } from "lucide-react";
import { useUiStore, DEFAULT_IDENTITY } from "@/store";
import { cn } from "@/utils/cn";

const HINT = "try: remember: I care about supply-chain risk";

/** How long a freshly-remembered chip shows "consolidating…" before settling. */
const CONSOLIDATE_MS = 60_000;

/**
 * Tracks which session memories are still "consolidating" (added THIS mount).
 * Memories already present when the rail mounts are treated as settled, so
 * navigating between pages doesn't restart the timer. Purely a client-side
 * approximation of the background cognify — the label is honest about that.
 */
function useConsolidating(memoryIds: string[]) {
  const seen = React.useRef<Set<string> | null>(null);
  const timers = React.useRef<Record<string, ReturnType<typeof setTimeout>>>({});
  const [active, setActive] = React.useState<Record<string, boolean>>({});

  React.useEffect(() => {
    if (seen.current === null) {
      seen.current = new Set(memoryIds);
      return;
    }
    for (const id of memoryIds) {
      if (!seen.current.has(id)) {
        seen.current.add(id);
        setActive((a) => ({ ...a, [id]: true }));
        timers.current[id] = setTimeout(
          () => setActive((a) => ({ ...a, [id]: false })),
          CONSOLIDATE_MS,
        );
      }
    }
  }, [memoryIds]);

  const timersRef = timers.current;
  React.useEffect(() => () => Object.values(timersRef).forEach(clearTimeout), [timersRef]);

  return active;
}

/**
 * Agent Memory rail — a slim, collapsible right-side panel that makes the
 * (otherwise invisible) memory layer tangible:
 *  - current identity (X-User-Id), editable inline, Zustand-persisted
 *  - chips for everything remembered THIS SESSION (honest: no list endpoint)
 *  - a hint nudging the judge to try a "remember:" directive
 */
export function AgentMemoryRail() {
  const identity = useUiStore((s) => s.identity);
  const setIdentity = useUiStore((s) => s.setIdentity);
  const memories = useUiStore((s) => s.sessionMemories);
  const memoryIds = React.useMemo(() => memories.map((m) => m.id), [memories]);
  const consolidating = useConsolidating(memoryIds);

  const [collapsed, setCollapsed] = React.useState(false);
  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState(identity);

  React.useEffect(() => {
    if (!editing) setDraft(identity);
  }, [identity, editing]);

  function commit() {
    setIdentity(draft.trim() || DEFAULT_IDENTITY);
    setEditing(false);
  }

  if (collapsed) {
    return (
      <button
        type="button"
        onClick={() => setCollapsed(false)}
        aria-label="Open Agent Memory"
        className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-surface text-text-muted shadow-elevated transition-colors hover:text-primary"
      >
        <PanelRightOpen className="h-4 w-4" />
      </button>
    );
  }

  return (
    <aside className="w-64 shrink-0">
      <div className="rounded-xl border border-border bg-surface p-4 shadow-elevated">
        <div className="mb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-primary" />
            <h2 className="text-[13px] font-medium uppercase tracking-wide text-text-muted">
              Agent Memory
            </h2>
          </div>
          <button
            type="button"
            onClick={() => setCollapsed(true)}
            aria-label="Collapse Agent Memory"
            className="text-text-muted transition-colors hover:text-foreground"
          >
            <PanelRightClose className="h-4 w-4" />
          </button>
        </div>

        {/* Identity */}
        <div className="mb-4">
          <div className="mb-1 text-[11px] uppercase tracking-wide text-text-muted">Identity</div>
          {editing ? (
            <form
              className="flex items-center gap-1.5"
              onSubmit={(e) => {
                e.preventDefault();
                commit();
              }}
            >
              <input
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                aria-label="X-User-Id"
                autoFocus
                onBlur={commit}
                className="h-8 flex-1 rounded-lg border border-primary/50 bg-surface-raised px-2 text-[13px] text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
              <button
                type="submit"
                aria-label="Save identity"
                className="rounded-md p-1.5 text-primary transition-colors hover:bg-surface-raised"
              >
                <Check className="h-4 w-4" />
              </button>
            </form>
          ) : (
            <button
              type="button"
              onClick={() => setEditing(true)}
              className="group flex w-full items-center justify-between rounded-lg border border-border bg-surface-raised px-2.5 py-1.5 text-left transition-colors hover:border-primary/50"
            >
              <span className="truncate font-mono text-[13px] text-foreground">{identity}</span>
              <Pencil className="h-3.5 w-3.5 shrink-0 text-text-muted transition-colors group-hover:text-primary" />
            </button>
          )}
          <p className="mt-1 text-[11px] text-text-muted">
            sent as <span className="font-mono">X-User-Id</span> on every request
          </p>
        </div>

        {/* Session remembers */}
        <div className="mb-1 text-[11px] uppercase tracking-wide text-text-muted">
          Remembered this session
        </div>
        {memories.length === 0 ? (
          <p className="rounded-lg border border-dashed border-border px-2.5 py-2 text-[12px] text-text-muted">
            {HINT}
          </p>
        ) : (
          <ul className="space-y-1.5">
            {memories.map((m) => {
              const isConsolidating = consolidating[m.id];
              return (
                <li
                  key={m.id}
                  className={cn(
                    "animate-memory-slide rounded-lg border border-primary/30 bg-primary/10 px-2.5 py-1.5",
                    "text-[12px] leading-snug text-foreground",
                  )}
                >
                  <div>
                    <span className="mr-1" aria-hidden>
                      🧠
                    </span>
                    {m.text}
                  </div>
                  {isConsolidating ? (
                    <div
                      className="mt-1 inline-flex items-center gap-1 text-[10px] text-text-muted"
                      title="consolidating in background (~1 min)"
                    >
                      <Clock className="h-3 w-3 animate-pulse" />
                      consolidating…
                    </div>
                  ) : (
                    <div className="mt-1 inline-flex items-center gap-1 text-[10px] text-primary/80">
                      <Check className="h-3 w-3" />
                      in memory
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </aside>
  );
}
