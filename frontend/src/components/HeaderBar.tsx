import { Link, useLocation } from "react-router-dom";
import { RescanButton } from "./RescanButton";

export interface HeaderBarProps {
  watcherActive?: boolean;
  rootPath?: string;
  lastFullScan?: string | null;
  filesIndexed?: number;
  title?: string;
}

export function HeaderBar({
  watcherActive = true,
  rootPath,
  lastFullScan,
  filesIndexed,
  title,
}: HeaderBarProps): JSX.Element {
  const location = useLocation();
  const currentPath = location.pathname;

  const rootLabel = rootPath ?? "CODE_MAP_ROOT";
  const description = lastFullScan
    ? `Último escaneo: ${new Date(lastFullScan).toLocaleString()} · ${filesIndexed ?? 0} archivos`
    : `${filesIndexed ?? 0} archivos indexados`;

  const navLinks = [
    { to: "/overview", label: "Overview" },
    { to: "/", label: "Inicio" },
    { to: "/stage-toolkit", label: "Stage Toolkit" },
    { to: "/code-map", label: "Code Map" },
    { to: "/prompts", label: "Prompts" },
    { to: "/class-graph", label: "Class Graph" },
    { to: "/class-uml", label: "Class UML" },
    { to: "/linters", label: "Linters" },
  ];

  return (
    <header className="header-bar">
      <div className="header-left">
        <div className="brand-logo">&lt;/&gt;</div>
        <div className="brand-copy">
          <h1>{title ?? "Code Map"}</h1>
          <p>{description}</p>
        </div>
      </div>

      <div className="header-actions">
        <nav className="header-nav">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              className={`secondary-btn${currentPath === link.to ? " active" : ""}`}
              to={link.to}
            >
              {link.label}
            </Link>
          ))}
        </nav>
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
