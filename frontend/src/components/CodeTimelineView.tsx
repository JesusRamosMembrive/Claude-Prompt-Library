/**
 * CodeTimelineView - DAW-style visualization of git commit history
 */

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import "../styles/timeline.css";

interface CommitInfo {
  hash: string;
  author: string;
  date: string;
  message: string;
  files_changed: string[];
}

interface TimelineMatrixResponse {
  commits: CommitInfo[];
  files: string[];
  matrix: boolean[][];
  total_files: number;
  total_commits: number;
}

export default function CodeTimelineView() {
  const [limit, setLimit] = useState(30);
  const [filePattern, setFilePattern] = useState("");

  const {
    data: matrixData,
    isLoading,
    error,
    refetch,
  } = useQuery<TimelineMatrixResponse>({
    queryKey: ["timeline-matrix", limit, filePattern],
    queryFn: async () => {
      const params = new URLSearchParams();
      params.append("limit", limit.toString());
      if (filePattern) {
        params.append("file_pattern", filePattern);
      }
      const response = await fetch(`/api/timeline/matrix?${params}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch timeline: ${response.statusText}`);
      }
      return response.json();
    },
  });

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  const formatShortHash = (hash: string) => hash.substring(0, 7);
  const getFileName = (path: string) => path.split("/").pop() || path;

  return (
    <div className="timeline-view">
      <div className="timeline-header">
        <h1>Code Timeline</h1>
        <p className="timeline-subtitle">
          DAW-style visualization of git commit history. Each cell represents a file change in a commit.
        </p>
      </div>

      {/* Controls */}
      <div className="timeline-controls">
        <div className="timeline-control-group">
          <label htmlFor="limit">Commits:</label>
          <input
            id="limit"
            type="number"
            min="5"
            max="1000"
            value={limit}
            onChange={(e) => setLimit(parseInt(e.target.value) || 30)}
            className="timeline-input"
          />
        </div>

        <div className="timeline-control-group">
          <label htmlFor="file-pattern">File Filter (regex):</label>
          <input
            id="file-pattern"
            type="text"
            placeholder="e.g., \.py$ for Python files"
            value={filePattern}
            onChange={(e) => setFilePattern(e.target.value)}
            className="timeline-input"
          />
        </div>

        <button onClick={() => refetch()} className="timeline-button">
          Refresh
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="timeline-loading">
          <p>Loading timeline data...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="timeline-error">
          <p>Error loading timeline: {(error as Error).message}</p>
          <p>Make sure the backend server is running and this is a git repository.</p>
        </div>
      )}

      {/* Timeline Matrix */}
      {matrixData && !isLoading && (
        <div className="timeline-content">
          {/* Summary Stats */}
          <div className="timeline-stats">
            <div className="timeline-stat">
              <span className="timeline-stat-label">Files:</span>
              <span className="timeline-stat-value">{matrixData.total_files}</span>
            </div>
            <div className="timeline-stat">
              <span className="timeline-stat-label">Commits:</span>
              <span className="timeline-stat-value">{matrixData.total_commits}</span>
            </div>
          </div>

          {matrixData.total_commits === 0 ? (
            <div className="timeline-help">
              <p>No commits found. Make sure you have git history in this repository.</p>
            </div>
          ) : (
            <>
              {/* Main Grid Container */}
              <div className="timeline-grid-container">
                {/* Header Row with Commits */}
                <div className="timeline-commits-header">
                  <div className="timeline-files-spacer">Files</div>
                  <div className="timeline-commits-row">
                    {matrixData.commits.map((commit) => (
                      <div
                        key={commit.hash}
                        className="timeline-commit-cell"
                        title={`${commit.hash}\n${commit.message}\nby ${commit.author}\n${commit.date}`}
                      >
                        <div className="timeline-commit-hash">
                          {formatShortHash(commit.hash)}
                        </div>
                        <div className="timeline-commit-date">
                          {formatDate(commit.date)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Grid Body: Files × Commits */}
                <div className="timeline-grid-body">
                  {matrixData.files.map((file, fileIdx) => (
                    <div key={file} className="timeline-grid-row">
                      {/* File name (left column) */}
                      <div className="timeline-file-label" title={file}>
                        {getFileName(file)}
                      </div>

                      {/* Cells for each commit */}
                      <div className="timeline-cells-row">
                        {matrixData.matrix[fileIdx].map((changed, commitIdx) => {
                          const commit = matrixData.commits[commitIdx];
                          return (
                            <div
                              key={`${file}-${commit.hash}`}
                              className={`timeline-cell ${
                                changed ? "timeline-cell--changed" : ""
                              }`}
                              title={
                                changed
                                  ? `${getFileName(file)} changed in ${formatShortHash(
                                      commit.hash
                                    )}`
                                  : ""
                              }
                            />
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Help Text */}
              <div className="timeline-help">
                <h3>How to use:</h3>
                <ul>
                  <li>Each row represents a file in your repository</li>
                  <li>Each column represents a commit (chronological order)</li>
                  <li>
                    Green cells indicate the file was changed in that commit
                  </li>
                  <li>
                    Use the file filter to narrow down to specific file types (e.g.,{" "}
                    <code>\.py$</code> for Python files)
                  </li>
                  <li>Hover over commits and cells to see more details</li>
                </ul>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
