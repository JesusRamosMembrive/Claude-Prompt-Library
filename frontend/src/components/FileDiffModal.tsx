import { useQuery } from "@tanstack/react-query";

import { getWorkingTreeDiff } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import "../styles/diff.css";

interface FileDiffModalProps {
  path: string;
  onClose: () => void;
}

export function FileDiffModal({ path, onClose }: FileDiffModalProps): JSX.Element {
  const { data, isPending, isError, error, refetch } = useQuery({
    queryKey: queryKeys.fileDiff(path),
    queryFn: () => getWorkingTreeDiff(path),
    enabled: Boolean(path),
  });

  const diffContent = data?.diff ?? "";
  const diffLines = diffContent ? diffContent.split(/\r?\n/) : [];
  const hasDiffContent = Boolean(diffContent.trim());
  const changeSummary = data?.change_summary;
  const changeStatus = data?.change_status;
  const changeLabel = formatStatus(changeStatus);

  const formatLineClass = (line: string) => {
    if (line.startsWith("+++")) {
      return "diff-line diff-line--meta";
    }
    if (line.startsWith("---")) {
      return "diff-line diff-line--meta";
    }
    if (line.startsWith("@@")) {
      return "diff-line diff-line--hunk";
    }
    if (line.startsWith("+")) {
      return "diff-line diff-line--added";
    }
    if (line.startsWith("-")) {
      return "diff-line diff-line--removed";
    }
    return "diff-line";
  };

  return (
    <div className="diff-overlay" onClick={onClose}>
      <div className="diff-modal" onClick={(event) => event.stopPropagation()}>
        <header className="diff-modal__header">
          <div>
            <p className="diff-modal__eyebrow">Working tree diff vs HEAD</p>
            <h2 className="diff-modal__title">{path}</h2>
            {changeLabel && (
              <span className="diff-modal__status" title={changeSummary ?? undefined}>
                {changeLabel}
              </span>
            )}
          </div>
          <div className="diff-modal__actions">
            <button
              type="button"
              className="diff-modal__refresh"
              onClick={() => refetch()}
            >
              Refresh
            </button>
            <button type="button" className="diff-modal__close" onClick={onClose}>
              ×
            </button>
          </div>
        </header>

        {isPending && <p className="diff-modal__hint">Loading diff...</p>}
        {isError && (
          <div className="error-banner" style={{ marginBottom: "16px" }}>
            Error loading diff: {(error as Error)?.message ?? "unknown error"}
          </div>
        )}

        {!isPending && !isError && !hasDiffContent && (
          <p className="diff-modal__hint">No changes detected for this file.</p>
        )}

        {hasDiffContent && (
          <div className="diff-modal__body">
            {diffLines.map((line, index) => (
              <div key={`${line}-${index}`} className={formatLineClass(line)}>
                {line.length === 0 ? "\u00A0" : line}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function formatStatus(status?: string | null): string {
  if (!status) {
    return "";
  }
  switch (status) {
    case "untracked":
      return "New file";
    case "added":
      return "Added";
    case "deleted":
      return "Deleted";
    case "renamed":
      return "Renamed";
    case "conflict":
      return "Conflict";
    default:
      return "Modified";
  }
}
