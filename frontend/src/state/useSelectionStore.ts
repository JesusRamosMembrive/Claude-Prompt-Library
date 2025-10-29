import { create } from "zustand";

interface SelectionState {
  selectedPath?: string;
  select: (path?: string) => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  selectedPath: undefined,
  select: (path?: string) => set({ selectedPath: path }),
}));
