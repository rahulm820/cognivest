/**
 * Stylized product mock for the landing hero — pure SVG/CSS, zero data fetches.
 * Replays the app's signature choreography on a 9s loop (keyframes in
 * globals.css): price line draws → two emerald markers drop in and pulse → a
 * citation chip slides under the chart → soft fade → restart.
 */
export function HeroMock() {
  return (
    <div className="relative w-full max-w-[540px]">
      {/* ambient emerald glow behind the card */}
      <div className="absolute -inset-8 -z-10 rounded-full bg-primary/15 blur-3xl" aria-hidden />

      <div className="rounded-2xl border border-border bg-surface p-5 shadow-elevated">
        {/* fake workspace header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <span className="rounded-md border border-primary/40 bg-primary/10 px-2 py-0.5 text-[12px] font-semibold tracking-wide text-primary">
              AAPL
            </span>
            <span className="text-[13px] text-text-muted">Apple Inc.</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-[15px] font-semibold tabular-nums text-foreground">$189.42</span>
            <span className="text-[12px] font-medium tabular-nums text-primary">▲ 2.31%</span>
          </div>
        </div>

        {/* fake range pills */}
        <div className="mt-3 flex items-center gap-1">
          {["1D", "1M", "3M", "1Y"].map((r) => (
            <span
              key={r}
              className={
                r === "1M"
                  ? "rounded-md bg-primary/15 px-2 py-0.5 text-[11px] font-medium text-primary"
                  : "rounded-md px-2 py-0.5 text-[11px] text-text-muted"
              }
            >
              {r}
            </span>
          ))}
        </div>

        {/* animated chart */}
        <svg
          viewBox="0 0 480 200"
          className="mt-2 w-full"
          role="img"
          aria-label="Animated preview: a price chart gains citation markers as an answer arrives"
        >
          <defs>
            <linearGradient id="mock-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.18" />
              <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* grid */}
          {[50, 100, 150].map((y) => (
            <line
              key={y}
              x1="0"
              y1={y}
              x2="480"
              y2={y}
              stroke="hsl(var(--border))"
              strokeOpacity="0.4"
            />
          ))}

          {/* area fill (fades in once the line has drawn) */}
          <path
            className="mock-fill mock-el"
            d="M0 162 L30 154 L55 160 L85 142 L110 148 L140 122 L165 130 L195 112 L240 84 L265 94 L300 82 L340 58 L370 68 L405 56 L440 62 L480 38 L480 200 L0 200 Z"
            fill="url(#mock-grad)"
          />

          {/* price line (self-drawing) */}
          <path
            className="mock-line mock-el"
            d="M0 162 L30 154 L55 160 L85 142 L110 148 L140 122 L165 130 L195 112 L240 84 L265 94 L300 82 L340 58 L370 68 L405 56 L440 62 L480 38"
            pathLength={100}
            fill="none"
            stroke="hsl(var(--primary))"
            strokeWidth={2.5}
            strokeLinejoin="round"
            strokeLinecap="round"
          />

          {/* citation markers dropping onto the line */}
          <circle
            className="mock-pulse-a mock-el"
            cx={240}
            cy={84}
            r={6}
            fill="hsl(var(--primary))"
          />
          <circle
            className="mock-marker-a mock-el"
            cx={240}
            cy={84}
            r={5}
            fill="hsl(var(--primary))"
            stroke="hsl(var(--background))"
            strokeWidth={2}
          />
          <circle
            className="mock-pulse-b mock-el"
            cx={340}
            cy={58}
            r={6}
            fill="hsl(var(--primary))"
          />
          <circle
            className="mock-marker-b mock-el"
            cx={340}
            cy={58}
            r={5}
            fill="hsl(var(--primary))"
            stroke="hsl(var(--background))"
            strokeWidth={2}
          />
        </svg>

        {/* citation chip sliding in under the chart */}
        <div className="mock-chip mock-el mt-3 flex items-center gap-2">
          <span className="inline-flex max-w-full items-center gap-2 rounded-full border border-primary/40 bg-surface-raised px-3 py-1.5 text-[12px] text-foreground shadow-marker-glow">
            <span className="h-2 w-2 shrink-0 rounded-full bg-primary" aria-hidden />
            <span className="truncate">Apple flags supply-chain constraints — reuters.com</span>
            <span className="shrink-0 tabular-nums text-text-muted">· Mar 3</span>
          </span>
        </div>
      </div>
    </div>
  );
}
