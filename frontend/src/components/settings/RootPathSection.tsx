interface RootPathSectionProps {
  absoluteRoot?: string;
  rootValue: string;
  disabled: boolean;
  onRootChange: (value: string) => void;
  onBrowse: () => void;
  browseDisabled?: boolean;
}

export function RootPathSection({
  absoluteRoot,
  rootValue,
  disabled,
  onRootChange,
  onBrowse,
  browseDisabled = false,
}: RootPathSectionProps): JSX.Element {
  return (
    <section className="settings-card">
      <h2>Ruta del proyecto</h2>
      <p>Define el directorio raíz que será analizado por el backend.</p>
      <div className="setting-row">
        <div className="setting-info">
          <strong>Ruta actual</strong>
          <span>{absoluteRoot ?? rootValue}</span>
        </div>
        <div className="setting-controls">
          <input
            type="text"
            value={rootValue}
            onChange={(event) => onRootChange(event.target.value)}
            disabled={disabled}
            placeholder="/ruta/del/proyecto"
          />
          <button type="button" onClick={onBrowse} disabled={browseDisabled || disabled}>
            Seleccionar…
          </button>
        </div>
      </div>
    </section>
  );
}
