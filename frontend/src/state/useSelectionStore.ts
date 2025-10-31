import { create } from "zustand";

interface SelectionState {
  selectedPath?: string;
  selectPath: (path: string) => void;
  clearSelection: () => void;
}

export const useSelectionStore = create<SelectionState>((set) => ({
  selectedPath: undefined,
  selectPath: (path: string) => set({ selectedPath: path }),
  clearSelection: () => set({ selectedPath: undefined }),
}));
