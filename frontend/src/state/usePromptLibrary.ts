import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface PromptEntry {
  id: string;
  title: string;
  body: string;
  tags: string[];
  category?: string | null;
  notes?: string | null;
  createdAt: string;
  updatedAt: string;
  lastUsedAt?: string | null;
}

export interface PromptInput {
  title: string;
  body: string;
  tags?: string[];
  category?: string | null;
  notes?: string | null;
}

interface PromptLibraryState {
  prompts: PromptEntry[];
  addPrompt: (input: PromptInput) => string;
  updatePrompt: (id: string, updates: PromptInput) => void;
  patchPrompt: (id: string, updates: Partial<Omit<PromptEntry, "id">>) => void;
  deletePrompt: (id: string) => void;
  recordUsage: (id: string) => void;
  clearAll: () => void;
}

function normalizeTags(tags?: string[]): string[] {
  if (!tags || tags.length === 0) {
    return [];
  }
  return Array.from(
    new Set(
      tags
        .map((tag) => tag.trim())
        .filter((tag) => tag.length > 0)
        .map((tag) => tag.toLowerCase())
    )
  );
}

function generateId(): string {
  return `prompt-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

const STORAGE_KEY = "prompt-library-v1";

export const usePromptLibrary = create<PromptLibraryState>()(
  persist(
    (set, get) => ({
      prompts: [],

      addPrompt(input) {
        const timestamp = new Date().toISOString();
        const next: PromptEntry = {
          id: generateId(),
          title: input.title.trim(),
          body: input.body,
          tags: normalizeTags(input.tags),
          category: input.category?.trim() || null,
          notes: input.notes?.trim() || null,
          createdAt: timestamp,
          updatedAt: timestamp,
          lastUsedAt: null,
        };
        set((state) => ({
          prompts: [next, ...state.prompts].sort(
            (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
          ),
        }));
        return next.id;
      },

      updatePrompt(id, updates) {
        get().patchPrompt(id, {
          title: updates.title.trim(),
          body: updates.body,
          tags: normalizeTags(updates.tags),
          category: updates.category?.trim() || null,
          notes: updates.notes?.trim() || null,
        });
      },

      patchPrompt(id, updates) {
        const now = new Date().toISOString();
        set((state) => {
          const prompts = state.prompts
            .map((prompt) =>
              prompt.id === id
                ? {
                    ...prompt,
                    ...updates,
                    ...(updates.tags !== undefined
                      ? { tags: normalizeTags(updates.tags) }
                      : null),
                    updatedAt: now,
                  }
                : prompt
            )
            .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
          return { prompts };
        });
      },

      deletePrompt(id) {
        set((state) => ({
          prompts: state.prompts.filter((prompt) => prompt.id !== id),
        }));
      },

      recordUsage(id) {
        const timestamp = new Date().toISOString();
        set((state) => {
          const prompts = state.prompts
            .map((prompt) =>
              prompt.id === id
                ? {
                    ...prompt,
                    lastUsedAt: timestamp,
                    updatedAt: timestamp,
                  }
                : prompt
            )
            .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
          return { prompts };
        });
      },

      clearAll() {
        set({ prompts: [] });
      },
    }),
    {
      name: STORAGE_KEY,
      version: 1,
      partialize: (state) => ({ prompts: state.prompts }),
    }
  )
);
