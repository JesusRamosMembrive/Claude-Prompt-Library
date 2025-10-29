import type { UseQueryResult } from "@tanstack/react-query";

import type { StatusPayload } from "../api/types";

function formatRelative(timestamp: string | null | undefined): string {
  if (!timestamp) {
    return "—";
  }
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }
  return date.toLocaleString();
}

export function StatusPanel({
  statusQuery,
}: {
  statusQuery: UseQueryResult<StatusPayload>;
}): JSX.Element {
  const status = statusQuery.data;

  if (statusQuery.isLoading) {
    return (
      <div>
        <h2>Estado</h2>
        <p style={{ color: "#7f869d", fontSize: "13px" }}>Cargando estado…</p>
      </div>
    );
  }

  if (statusQuery.isError || !status) {
    return (
      <div>
        <h2>Estado</h2>
        <div className="error-banner">
          No se pudo obtener el estado actual del backend.
        </div>
      </div>
    );
  }

  return (
    <div className="status-panel">
      <h2>Estado</h2>
      <dl className="status-grid">
        <div>
          <dt>Watcher</dt>
          <dd>{status.watcher_active ? "Activo" : "Inactivo"}</dd>
        </div>
        <div>
          <dt>Docstrings</dt>
          <dd>{status.include_docstrings ? "Incluidos" : "Ocultos"}</dd>
        </div>
        <div>
          <dt>Archivos</dt>
          <dd>{status.files_indexed}</dd>
        </div>
        <div>
          <dt>Símbolos</dt>
          <dd>{status.symbols_indexed}</dd>
        </div>
        <div>
          <dt>Último escaneo</dt>
          <dd>{formatRelative(status.last_full_scan)}</dd>
        </div>
        <div>
          <dt>Último evento</dt>
          <dd>{formatRelative(status.last_event_batch)}</dd>
        </div>
        <div>
          <dt>Pendientes</dt>
          <dd>{status.pending_events}</dd>
        </div>
      </dl>
    </div>
  );
}
