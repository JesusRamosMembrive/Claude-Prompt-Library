import type {
  FileSummary,
  ProjectTreeNode,
  SettingsPayload,
  SettingsUpdatePayload,
  StatusPayload,
  SymbolInfo,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? String(import.meta.env.VITE_API_BASE_URL).replace(/\/$/, "")
  : null;
const API_PREFIX = API_BASE ? "" : "/api";

const buildUrl = (path: string): string =>
  `${API_BASE ?? ""}${API_PREFIX}${path}`;

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(
      `API request failed (${response.status}): ${detail || "Unknown error"}`
    );
  }

  return (await response.json()) as T;
}

export function getTree(): Promise<ProjectTreeNode> {
  return fetchJson<ProjectTreeNode>("/tree");
}

export function getFileSummary(path: string): Promise<FileSummary> {
  const encoded = encodeURIComponent(path);
  return fetchJson<FileSummary>(`/files/${encoded}`);
}

export function searchSymbols(term: string): Promise<{ results: SymbolInfo[] }> {
  const params = new URLSearchParams({ q: term });
  return fetchJson(`/search?${params.toString()}`);
}

export function triggerRescan(): Promise<{ files: number }> {
  return fetchJson<{ files: number }>("/rescan", {
    method: "POST",
  });
}

export function getEventsUrl(): string {
  return buildUrl("/events");
}

export type { ChangeNotification } from "./types";

export function getSettings(): Promise<SettingsPayload> {
  return fetchJson<SettingsPayload>("/settings");
}

export function updateSettings(payload: SettingsUpdatePayload): Promise<{
  updated: string[];
  settings: SettingsPayload;
}> {
  return fetchJson("/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function getStatus(): Promise<StatusPayload> {
  return fetchJson<StatusPayload>("/status");
}

export async function getPreview(path: string): Promise<{ content: string; contentType: string }> {
  const response = await fetch(buildUrl(`/preview?path=${encodeURIComponent(path)}`));
  if (!response.ok) {
    const detail = await response.text().catch(() => response.statusText);
    throw new Error(`Preview request failed (${response.status}): ${detail || "Unknown error"}`);
  }
  const content = await response.text();
  const contentType = response.headers.get("Content-Type") ?? "text/plain";
  return { content, contentType };
}
