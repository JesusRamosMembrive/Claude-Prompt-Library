import { create } from "zustand";

type ActivityType = "updated" | "deleted";

export interface ActivityRecord {
  id: string;
  path: string;
  type: ActivityType;
  timestamp: number;
}

interface ActivityState {
  items: ActivityRecord[];
  push: (records: Omit<ActivityRecord, "id">[]) => void;
  clear: () => void;
}

const MAX_ITEMS = 20;

export const useActivityStore = create<ActivityState>((set) => ({
  items: [],
  push(records) {
    if (records.length === 0) {
      return;
    }
    set((state) => {
      const timestamp = Date.now();
      const next = [
        ...records.map((record, index) => ({
          ...record,
          id: `${record.type}-${record.path}-${timestamp}-${index}`,
        })),
        ...state.items,
      ].slice(0, MAX_ITEMS);
      return { items: next };
    });
  },
  clear() {
    set({ items: [] });
  },
}));
