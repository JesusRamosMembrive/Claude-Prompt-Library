export type SymbolKind = "function" | "class" | "method";

export interface SymbolInfo {
  name: string;
  kind: SymbolKind;
  lineno: number;
  parent?: string | null;
  path?: string | null;
  docstring?: string | null;
}

export interface AnalysisError {
  message: string;
  lineno?: number | null;
  col_offset?: number | null;
}

export interface FileSummary {
  path: string;
  modified_at?: string | null;
  symbols: SymbolInfo[];
  errors: AnalysisError[];
}

export interface ProjectTreeNode {
  name: string;
  path: string;
  is_dir: boolean;
  children: ProjectTreeNode[];
  symbols: SymbolInfo[] | null;
  errors: AnalysisError[] | null;
  modified_at?: string | null;
}

export interface ChangeNotification {
  updated: string[];
  deleted: string[];
}

export interface SettingsPayload {
  root_path: string;
  absolute_root: string;
  exclude_dirs: string[];
  include_docstrings: boolean;
  watcher_active: boolean;
}

export interface SettingsUpdatePayload {
  root_path?: string;
  include_docstrings?: boolean;
  exclude_dirs?: string[];
}

export interface AnalyzerCapability {
  key: string;
  description: string;
  extensions: string[];
  available: boolean;
  dependency?: string | null;
  error?: string | null;
  degraded_extensions: string[];
}

export interface StatusPayload {
  root_path: string;
  absolute_root: string;
  watcher_active: boolean;
  include_docstrings: boolean;
  last_full_scan: string | null;
  last_event_batch: string | null;
  files_indexed: number;
  symbols_indexed: number;
  pending_events: number;
  capabilities: AnalyzerCapability[];
}

export type StageAgentSelection = "claude" | "codex" | "both";

export interface OptionalFilesStatus {
  expected: string[];
  present: string[];
  missing: string[];
}

export interface AgentInstallStatus {
  expected: string[];
  present: string[];
  missing: string[];
  installed: boolean;
  optional?: OptionalFilesStatus | null;
}

export interface DocsStatus {
  expected: string[];
  present: string[];
  missing: string[];
  complete: boolean;
}

export interface StageDetectionStatus {
  available: boolean;
  recommended_stage?: number | null;
  confidence?: string | null;
  reasons: string[];
  metrics?: Record<string, unknown> | null;
  error?: string | null;
  checked_at?: string | null;
}

export interface StageStatusPayload {
  root_path: string;
  claude: AgentInstallStatus;
  codex: AgentInstallStatus;
  docs: DocsStatus;
  detection: StageDetectionStatus;
}

export interface StageInitPayload {
  agents: StageAgentSelection;
}

export interface StageInitResponse {
  success: boolean;
  exit_code: number;
  command: string[];
  stdout: string;
  stderr: string;
  status: StageStatusPayload;
}

export interface ClassGraphNode {
  id: string;
  name: string;
  module: string;
  file: string;
}

export interface ClassGraphEdge {
  source: string;
  target: string;
  type: "inherits" | "instantiates";
  internal: boolean;
  raw_target: string;
}

export interface ClassGraphStats {
  nodes: number;
  edges: number;
  edges_by_type: Record<string, number>;
}

export interface ClassGraphResponse {
  nodes: ClassGraphNode[];
  edges: ClassGraphEdge[];
  stats: ClassGraphStats;
}
