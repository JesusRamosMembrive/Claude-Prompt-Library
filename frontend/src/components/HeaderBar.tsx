import { Link } from "react-router-dom";
import { RescanButton } from "./RescanButton";

interface HeaderBarProps {
  watcherActive?: boolean;
  rootPath?: string;
  lastFullScan?: string | null;
  filesIndexed?: number;
}

export function HeaderBar({
  watcherActive = true,
  rootPath,
  lastFullScan,
  filesIndexed,
}: HeaderBarProps): JSX.Element {
  const rootLabel = rootPath ?? "CODE_MAP_ROOT";
  const description = lastFullScan
    ? `Último escaneo: ${new Date(lastFullScan).toLocaleString()} · ${filesIndexed ?? 0} archivos`
    : `${filesIndexed ?? 0} archivos indexados`;

  return (
    <header className="header-bar">
      <div className="header-left">
        <div className="brand-logo">&lt;/&gt;</div>
        <div className="brand-copy">
          <h1>Code Map</h1>
          <p>{description}</p>
        </div>
      </div>

      <div className="header-actions">
        <div className="status-indicator" title={`Root: ${rootLabel}`}>
          <span className="status-dot" style={{ opacity: watcherActive ? 1 : 0.4 }} />
          {watcherActive ? "Watcher activo" : "Watcher inactivo"}
        </div>
        <Link className="secondary-btn" to="/settings">
          Settings
        </Link>
        <RescanButton />
      </div>
    </header>
  );
}
