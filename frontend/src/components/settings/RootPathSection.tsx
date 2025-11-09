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
      <h2>Project path</h2>
      <p>Define the root directory that the backend will analyze.</p>
      <div className="setting-row">
        <div className="setting-info">
          <strong>Current path</strong>
          <span>{absoluteRoot ?? rootValue}</span>
        </div>
        <div className="setting-controls">
          <input
            type="text"
            value={rootValue}
            onChange={(event) => onRootChange(event.target.value)}
            disabled={disabled}
            placeholder="/path/to/project"
          />
          <button type="button" onClick={onBrowse} disabled={browseDisabled || disabled}>
            Browse…
          </button>
        </div>
      </div>
    </section>
  );
}
