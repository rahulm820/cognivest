# Cognivest — Frontend

Next.js 14 (App Router) + TypeScript UI for the per-company financial intelligence platform.
This is the **presentation shell** described in [ARCHITECTURE.md](../ARCHITECTURE.md) §3 and
[CLAUDE.md](../CLAUDE.md) §5. All intelligence lives in the backend + Cognee; the frontend only
renders price charts, runs natural-language queries, and surfaces ingestion health.

> **Status: Phase 0 scaffold.** Components render minimal placeholder UI; hooks/services are typed
> stubs marked `// TODO(phase-N)`. No business logic yet.

## Tech stack

- **Next.js 14** (App Router) + **TypeScript** (`strict`)
- **Tailwind CSS** + **shadcn/ui** conventions (owned primitives in `src/components/ui`)
- **TanStack Query** for server state, **Zustand** for global UI state
- **Recharts** for price charts, **Axios** for the typed API client
- **Vitest** + **React Testing Library** for tests; **ESLint** + **Prettier** for lint/format
- Package manager: **pnpm**

## Screens

| Route | Purpose | Key components |
|---|---|---|
| `/dashboard` | Watchlist of companies + add ticker | `WatchlistTable`, `AddTickerModal`, `IngestionHealthBadge` |
| `/company/[ticker]` | Price chart + NL query box with citations | `PriceChart`, `NewsMarkerOverlay`, `QueryBox`, `AnswerPanel`, `DateRangePicker` |
| `/admin` | Ingestion-health table (polls) | `JobRunTable`, `ErrorLogPanel` |
| `/login` | JWT login stub | — |

`/` redirects to `/dashboard`.

## Folder structure

```text
src/
  app/                 # App Router pages + layout + providers + globals.css
    (auth)/login/
    dashboard/
    company/[ticker]/
    admin/
  components/
    ui/                # shadcn-style primitives (button, input, badge, spinner, card)
    charts/            # PriceChart, NewsMarkerOverlay
    layout/            # AppShell, Sidebar, TopNav
    common/            # DateRangePicker, CitationChip, TickerSearch
  features/            # WatchlistTable, QueryBox, JobRunTable, ...
  hooks/               # TanStack Query hooks (useWatchlist, useCompanyPrice, ...)
  services/api/        # axios client + endpoint modules (the ONLY HTTP seam)
  store/               # Zustand uiStore
  types/               # API contract types (OpenAPI-generated later)
  constants/           # API routes, query keys, ranges
  utils/               # cn(), formatters
```

## Conventions (from CLAUDE.md §5)

- **API access only through `src/services/api/*`** — never inline `fetch`/`axios` in components.
- **Server state** → TanStack Query hooks. **Global UI state** → Zustand. **Local** → `useState`.
- `PascalCase` components/types, `camelCase` functions, `useX` hooks.
- Import via the `@/` path alias.
- API base URL comes from `NEXT_PUBLIC_API_BASE_URL`.

## Getting started

```bash
pnpm install
cp .env.local.example .env.local   # set NEXT_PUBLIC_API_BASE_URL
pnpm dev                           # http://localhost:3000
```

## Scripts

```bash
pnpm dev            # start dev server
pnpm build          # production build
pnpm start          # serve production build
pnpm lint           # eslint
pnpm test           # vitest (run once)
pnpm format         # prettier --write
```
