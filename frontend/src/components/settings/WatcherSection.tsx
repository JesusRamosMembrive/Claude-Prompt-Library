interface WatcherSectionProps {
  watcherActive?: boolean;
}

export function WatcherSection({ watcherActive }: WatcherSectionProps): JSX.Element {
  return (
    <section className="settings-card">
      <h2>Watcher y sincronización</h2>
      <p>Controla cómo se aplican los cambios del sistema de archivos.</p>
      <div className="toggle-row">
        <div>
          <strong>Watcher activo</strong>
          <span>
            {watcherActive
              ? "Reescanea en cuanto se detectan eventos."
              : "Watcher deshabilitado."}
          </span>
        </div>
        <input type="checkbox" checked={Boolean(watcherActive)} readOnly />
      </div>
      <div className="toggle-row">
        <div>
          <strong>Auto-rescan</strong>
          <span>Fuerza escaneos completos al detectar cambios mayores.</span>
        </div>
        <input type="checkbox" disabled />
      </div>
      <div className="toggle-row">
        <div>
          <strong>Persistir snapshots</strong>
          <span>Guarda los resultados en `.code-map` para iniciar más rápido.</span>
        </div>
        <input type="checkbox" checked readOnly />
      </div>
    </section>
  );
}
