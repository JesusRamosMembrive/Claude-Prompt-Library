interface WatcherSectionProps {
  watcherActive?: boolean;
}

export function WatcherSection({ watcherActive }: WatcherSectionProps): JSX.Element {
  return (
    <section className="settings-card">
      <h2>Watcher and sync</h2>
      <p>Control how filesystem changes are applied.</p>
      <div className="toggle-row">
        <div>
          <strong>Watcher active</strong>
          <span>
            {watcherActive
              ? "Re-scans as soon as events are detected."
              : "Watcher disabled."}
          </span>
        </div>
        <input type="checkbox" checked={Boolean(watcherActive)} readOnly />
      </div>
      <div className="toggle-row">
        <div>
          <strong>Auto-rescan</strong>
          <span>Forces full scans when major changes are detected.</span>
        </div>
        <input type="checkbox" disabled />
      </div>
      <div className="toggle-row">
        <div>
          <strong>Persist snapshots</strong>
          <span>Store results in `.code-map` for faster startup.</span>
        </div>
        <input type="checkbox" checked readOnly />
      </div>
    </section>
  );
}
