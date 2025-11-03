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
  ollama_insights_enabled: boolean;
  watcher_active: boolean;
}

export interface SettingsUpdatePayload {
  root_path?: string;
  include_docstrings?: boolean;
  exclude_dirs?: string[];
  ollama_insights_enabled?: boolean;
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
  ollama_insights_enabled: boolean;
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

export interface OllamaModelInfo {
  name: string;
  size_bytes?: number | null;
  size_human?: string | null;
  digest?: string | null;
  modified_at?: string | null;
  format?: string | null;
}

export interface OllamaStatus {
  installed: boolean;
  running: boolean;
  models: OllamaModelInfo[];
  version?: string | null;
  binary_path?: string | null;
  endpoint?: string | null;
  warning?: string | null;
  error?: string | null;
}

export interface OllamaStatusPayload {
  status: OllamaStatus;
  checked_at: string;
}

export interface OllamaTestPayload {
  model: string;
  prompt: string;
  system_prompt?: string;
  endpoint?: string;
  timeout_seconds?: number;
}

export interface OllamaTestResponse {
  success: boolean;
  model: string;
  endpoint: string;
  latency_ms: number;
  message: string;
  raw: Record<string, unknown>;
}

export interface OllamaTestErrorDetail {
  message?: string;
  endpoint?: string;
  original_error?: string;
  status_code?: number | null;
  reason_code?: string;
  retry_after_seconds?: number;
  loading?: boolean;
  loading_since?: string;
}

export interface OllamaStartPayload {
  timeout_seconds?: number;
}

export interface OllamaStartResponse {
  started: boolean;
  already_running: boolean;
  endpoint: string;
  process_id?: number | null;
  status: OllamaStatus;
  checked_at: string;
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

export interface BrowseDirectoryResponse {
  path: string;
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
  type: "inherits" | "instantiates" | "references";
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

export interface UMLAttribute {
  name: string;
  type?: string | null;
  optional: boolean;
}

export interface UMLMethod {
  name: string;
  parameters: string[];
  returns?: string | null;
}

export interface UMLClass {
  id: string;
  name: string;
  module: string;
  file: string;
  bases: string[];
  attributes: UMLAttribute[];
  methods: UMLMethod[];
  associations: string[];
}

export interface UMLDiagramResponse {
  classes: UMLClass[];
  stats: Record<string, number>;
}

export type LinterCheckStatus = "pass" | "warn" | "fail" | "skipped" | "error";
export type LinterSeverity = "info" | "low" | "medium" | "high" | "critical";

export interface LinterIssueDetail {
  message: string;
  file?: string | null;
  line?: number | null;
  column?: number | null;
  code?: string | null;
  severity: LinterSeverity;
  suggestion?: string | null;
}

export interface LinterToolRun {
  key: string;
  name: string;
  status: LinterCheckStatus;
  command?: string | null;
  duration_ms?: number | null;
  exit_code?: number | null;
  version?: string | null;
  issues_found: number;
  issues_sample: LinterIssueDetail[];
  stdout_excerpt?: string | null;
  stderr_excerpt?: string | null;
}

export interface LinterCustomRuleRun {
  key: string;
  name: string;
  description: string;
  status: LinterCheckStatus;
  threshold?: number | null;
  violations: LinterIssueDetail[];
}

export interface LinterCoverageSnapshot {
  statement_coverage?: number | null;
  branch_coverage?: number | null;
  missing_lines?: number | null;
}

export interface LinterReportSummary {
  overall_status: LinterCheckStatus;
  total_checks: number;
  checks_passed: number;
  checks_warned: number;
  checks_failed: number;
  duration_ms?: number | null;
  files_scanned?: number | null;
  lines_scanned?: number | null;
  issues_total: number;
  critical_issues: number;
}

export interface LinterChartData {
  issues_by_tool: Record<string, number>;
  issues_by_severity: Record<LinterSeverity | string, number>;
  top_offenders: string[];
}

export interface LintersReportPayload {
  root_path: string;
  generated_at: string;
  summary: LinterReportSummary;
  tools: LinterToolRun[];
  custom_rules: LinterCustomRuleRun[];
  coverage?: LinterCoverageSnapshot | null;
  metrics: Record<string, number>;
  chart_data: LinterChartData;
  notes: string[];
}

export interface LintersReportListItem {
  id: number;
  generated_at: string;
  root_path: string;
  overall_status: LinterCheckStatus;
  issues_total: number;
  critical_issues: number;
}

export interface LintersReportRecord extends LintersReportListItem {
  report: LintersReportPayload;
}

export interface LintersNotificationEntry {
  id: number;
  created_at: string;
  channel: string;
  severity: LinterSeverity;
  title: string;
  message: string;
  payload?: Record<string, unknown> | null;
  root_path?: string | null;
  read: boolean;
}
