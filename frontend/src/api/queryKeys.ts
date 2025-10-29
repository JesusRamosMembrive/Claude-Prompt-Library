export const queryKeys = {
  tree: ["tree"] as const,
  file: (path: string) => ["file", path] as const,
  search: (term: string) => ["search", term] as const,
  settings: ["settings"] as const,
};
