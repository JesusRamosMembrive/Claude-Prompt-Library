export const queryKeys = {
  tree: ["tree"] as const,
  file: (path: string) => ["file", path] as const,
  search: (term: string) => ["search", term] as const,
  settings: ["settings"] as const,
  status: ["status"] as const,
  preview: (path: string) => ["preview", path] as const,
  stageStatus: ["stage-status"] as const,
  classGraph: (includeExternal: boolean, edgeTypes: string[], prefixes?: string[]) =>
    [
      "class-graph",
      includeExternal,
      [...edgeTypes].sort().join(","),
      prefixes ? [...prefixes].sort().join(",") : "",
    ] as const,
  classUml: (includeExternal: boolean, prefixes?: string[]) =>
    [
      "class-uml",
      includeExternal,
      prefixes ? [...prefixes].sort().join(",") : "",
    ] as const,
  lintersLatest: ["linters", "latest"] as const,
  lintersReports: (limit: number, offset: number) =>
    ["linters", "reports", limit, offset] as const,
  lintersNotifications: (unreadOnly: boolean) =>
    ["linters", "notifications", unreadOnly] as const,
};
