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
}
