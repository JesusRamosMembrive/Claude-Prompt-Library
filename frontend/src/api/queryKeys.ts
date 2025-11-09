export const queryKeys = {
  tree: ["tree"] as const,
  file: (path: string) => ["file", path] as const,
  search: (term: string) => ["search", term] as const,
  settings: ["settings"] as const,
  status: ["status"] as const,
  preview: (path: string) => ["preview", path] as const,
  stageStatus: ["stage-status"] as const,
  ollamaInsights: (limit: number) => ["ollama", "insights", limit] as const,
  classUml: (
    includeExternal: boolean,
    prefixes?: string[],
    edgeTypes?: string[],
    graphvizSignature?: string,
  ) =>
    [
      "class-uml",
      includeExternal,
      prefixes ? [...prefixes].sort().join(",") : "",
      edgeTypes ? [...edgeTypes].sort().join(",") : "",
      graphvizSignature ?? "",
    ] as const,
  lintersLatest: ["linters", "latest"] as const,
  lintersReports: (limit: number, offset: number) =>
    ["linters", "reports", limit, offset] as const,
  lintersNotifications: (unreadOnly: boolean) =>
    ["linters", "notifications", unreadOnly] as const,
};
