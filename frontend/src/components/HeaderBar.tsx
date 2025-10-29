import { RescanButton } from "./RescanButton";

export function HeaderBar({
  onOpenSettings,
  watcherActive = true,
  rootPath,
  lastFullScan,
  filesIndexed,
}: {
  onOpenSettings: () => void;
  watcherActive?: boolean;
  rootPath?: string;
  lastFullScan?: string | null;
  filesIndexed?: number;
}): JSX.Element {
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
        <button
          className="secondary-btn"
          type="button"
          onClick={onOpenSettings}
        >
          Settings
        </button>
        <RescanButton />
      </div>
    </header>
  );
}
