import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { DateRange } from "@/types";

/** A preference the user asked the agent to remember during this session. */
export interface SessionMemory {
  id: string;
  text: string;
}

/**
 * Global UI state (ARCHITECTURE.md §3.5).
 *
 * Only `identity` is persisted (localStorage) — it is the demo `X-User-Id` and
 * should survive reloads. Everything else (hover-link, this-session remembers)
 * is intentionally ephemeral: the Agent Memory rail is honest that its list is
 * "remembered this session" (we have no list-memories endpoint).
 */
export interface UiState {
  selectedTicker: string | null;
  dateRange: DateRange | null;

  /** Demo identity asserted via the `X-User-Id` header (CLAUDE.md §8). */
  identity: string;

  /** Shared highlight between a CitationChip and its chart marker. */
  hoveredCitationId: string | null;

  /** Preferences remembered via "remember:" directives, this session only. */
  sessionMemories: SessionMemory[];

  setSelectedTicker: (ticker: string | null) => void;
  setDateRange: (range: DateRange | null) => void;
  setIdentity: (identity: string) => void;
  setHoveredCitationId: (id: string | null) => void;
  addSessionMemory: (memory: SessionMemory) => void;
}

export const DEFAULT_IDENTITY = "demo-user";

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      selectedTicker: null,
      dateRange: null,
      identity: DEFAULT_IDENTITY,
      hoveredCitationId: null,
      sessionMemories: [],

      setSelectedTicker: (ticker) => set({ selectedTicker: ticker }),
      setDateRange: (range) => set({ dateRange: range }),
      setIdentity: (identity) => set({ identity: identity.trim() || DEFAULT_IDENTITY }),
      setHoveredCitationId: (id) => set({ hoveredCitationId: id }),
      addSessionMemory: (memory) =>
        set((state) => ({ sessionMemories: [memory, ...state.sessionMemories] })),
    }),
    {
      name: "cognivest-ui",
      // Persist ONLY the demo identity; session memories + hover state stay ephemeral.
      partialize: (state) => ({ identity: state.identity }),
    },
  ),
);
