import { RescanButton } from "./RescanButton";

export function HeaderBar({
  onOpenSettings,
  watcherActive = true,
  rootPath,
}: {
  onOpenSettings: () => void;
  watcherActive?: boolean;
  rootPath?: string;
}): JSX.Element {
  const rootLabel = rootPath ?? "CODE_MAP_ROOT";

  return (
    <header className="header-bar">
      <div className="header-left">
        <div className="brand-logo">&lt;/&gt;</div>
        <div className="brand-copy">
          <h1>Code Map</h1>
          <p>Explora las clases y funciones de tu proyecto en tiempo real.</p>
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
