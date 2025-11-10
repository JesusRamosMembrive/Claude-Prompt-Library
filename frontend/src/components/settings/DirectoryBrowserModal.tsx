import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { listDirectories } from "../../api/client";

interface DirectoryBrowserModalProps {
  isOpen: boolean;
  currentPath: string;
  onClose: () => void;
  onSelect: (path: string) => void;
}

export function DirectoryBrowserModal({
  isOpen,
  currentPath,
  onClose,
  onSelect,
}: DirectoryBrowserModalProps): JSX.Element | null {
  // Always start from /work (Docker mount point) or current path if it starts with /work
  const initialPath = currentPath?.startsWith("/work") ? currentPath : "/work";
  const [browsePath, setBrowsePath] = useState(initialPath);

  // Reset to /work when modal opens
  useEffect(() => {
    if (isOpen) {
      const startPath = currentPath?.startsWith("/work") ? currentPath : "/work";
      setBrowsePath(startPath);
    }
  }, [isOpen, currentPath]);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["listDirectories", browsePath],
    queryFn: () => listDirectories(browsePath),
    enabled: isOpen,
  });

  const handleDirectoryClick = (path: string, isParent: boolean) => {
    if (isParent) {
      // Navigate to parent
      setBrowsePath(path);
      refetch();
    } else {
      // Navigate into subdirectory
      setBrowsePath(path);
      refetch();
    }
  };

  const handleSelectCurrent = () => {
    onSelect(browsePath);
    onClose();
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Select Project Directory</h2>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          <div className="directory-browser">
            <div className="directory-current-path">
              <strong>Current path:</strong>
              <code>{data?.current_path ?? browsePath}</code>
            </div>

            {isLoading && (
              <div className="directory-loading">
                <span className="loading-spinner" />
                <span>Loading directories...</span>
              </div>
            )}

            {error && (
              <div className="directory-error">
                <span className="error-icon">⚠️</span>
                <span>Error: {error instanceof Error ? error.message : "Failed to load directories"}</span>
              </div>
            )}

            {data && data.directories.length === 0 && (
              <div className="directory-empty">
                <span>📁</span>
                <span>No subdirectories found</span>
              </div>
            )}

            {data && data.directories.length > 0 && (
              <ul className="directory-list">
                {data.directories.map((dir) => (
                  <li
                    key={dir.path}
                    className={`directory-item ${dir.is_parent ? "directory-item--parent" : ""}`}
                    onClick={() => handleDirectoryClick(dir.path, dir.is_parent)}
                  >
                    <span className="directory-icon">
                      {dir.is_parent ? "⬆️" : "📁"}
                    </span>
                    <span className="directory-name">{dir.name}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="ghost-btn" onClick={onClose}>
            Cancel
          </button>
          <button className="primary-btn" onClick={handleSelectCurrent}>
            Select "{browsePath}"
          </button>
        </div>
      </div>
    </div>
  );
}
