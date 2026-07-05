"use client";

export interface MemoryCardProps {
  /** The preference text the agent acknowledged remembering. */
  text: string;
}

/**
 * Ack treatment for a "remember:" directive — NOT an answer panel. A compact
 * card slides in confirming the stored preference; the workspace also docks a
 * matching chip into the Agent Memory rail.
 */
export function MemoryCard({ text }: MemoryCardProps) {
  return (
    <div className="animate-memory-slide rounded-xl border border-primary/40 bg-primary/10 p-4 shadow-elevated">
      <div className="flex items-start gap-3">
        <span className="text-xl leading-none" aria-hidden>
          🧠
        </span>
        <div className="min-w-0">
          <div className="text-[12px] font-medium uppercase tracking-wide text-primary">
            Remembered
          </div>
          <p className="mt-1 text-[15px] leading-relaxed text-foreground">{text}</p>
          <p className="mt-1 text-[12px] text-text-muted">
            Docked into Agent Memory → it&apos;ll shape future answers this session.
          </p>
        </div>
      </div>
    </div>
  );
}
