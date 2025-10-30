export const queryKeys = {
  tree: ["tree"] as const,
  file: (path: string) => ["file", path] as const,
  search: (term: string) => ["search", term] as const,
  settings: ["settings"] as const,
  status: ["status"] as const,
  preview: (path: string) => ["preview", path] as const,
  stageStatus: ["stage-status"] as const,
  classGraph: (includeExternal: boolean, edgeTypes: string[]) =>
    ["class-graph", includeExternal, [...edgeTypes].sort().join(",")] as const,
};
