interface DocstringsSectionProps {
  includeDocstrings: boolean;
  disabled: boolean;
  onToggleDocstrings: (value: boolean) => void;
}

export function DocstringsSection({
  includeDocstrings,
  disabled,
  onToggleDocstrings,
}: DocstringsSectionProps): JSX.Element {
  return (
    <section className="settings-card">
      <h2>Display</h2>
      <p>Adjust how symbols are shown in the interface.</p>
      <div className="setting-row">
        <div className="setting-info">
          <strong>Symbol mode</strong>
          <span>Primary grouping for the explorer.</span>
        </div>
        <div className="setting-controls setting-controls--centered">
          <span className="setting-display-value">Folder → file → symbol</span>
        </div>
      </div>
      <div className="toggle-row">
        <div>
          <strong>Show docstrings</strong>
          <span>Controls whether the analyzer extracts docstrings for the UI.</span>
        </div>
        <input
          type="checkbox"
          checked={includeDocstrings}
          onChange={(event) => onToggleDocstrings(event.target.checked)}
          disabled={disabled}
        />
      </div>
      <p className="settings-helper">
        Dark theme is always on for now; a light palette will ship later.
      </p>
    </section>
  );
}
