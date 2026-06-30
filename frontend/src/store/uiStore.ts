import { create } from "zustand";
import type { DateRange } from "@/types";

export type Theme = "light" | "dark";

/** Global UI state (selected ticker, date range, theme). See ARCHITECTURE.md §3.5. */
export interface UiState {
  selectedTicker: string | null;
  dateRange: DateRange | null;
  theme: Theme;
  setSelectedTicker: (ticker: string | null) => void;
  setDateRange: (range: DateRange | null) => void;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  selectedTicker: null,
  dateRange: null,
  theme: "light",
  setSelectedTicker: (ticker) => set({ selectedTicker: ticker }),
  setDateRange: (range) => set({ dateRange: range }),
  setTheme: (theme) => set({ theme }),
  toggleTheme: () => set((state) => ({ theme: state.theme === "light" ? "dark" : "light" })),
}));
