import { Link } from "react-router-dom";
import type { UseQueryResult } from "@tanstack/react-query";

import type { StatusPayload } from "../api/types";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";
import { useLintersLatestReport } from "../hooks/useLintersLatestReport";
import { RescanButton } from "./RescanButton";

const LINTER_STATUS_LABEL: Record<string, string> = {
  pass: "OK",
  warn: "Advertencias",
  fail: "Con fallos",
  skipped: "Omitido",
  error: "Error",
  default: "Sin datos",
};

const LINTER_STATUS_TONE: Record<string, "success" | "warn" | "danger" | "neutral"> = {
  pass: "success",
  warn: "warn",
  fail: "danger",
  error: "danger",
  skipped: "neutral",
  default: "neutral",
};

function formatDateTime(value?: string | null): string {
  if (!value) {
    return "—";
  }
  try {
    return new Date(value).toLocaleString("es-ES");
  } catch {
    return value;
  }
}

function formatDuration(ms?: number | null): string {
  if (!ms || ms <= 0) {
    return "—";
  }
  if (ms < 1000) {
    return `${ms.toLocaleString("es-ES")} ms`;
  }
  const seconds = ms / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(seconds >= 10 ? 0 : 1)} s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes} min ${remainingSeconds > 0 ? `${remainingSeconds} s` : ""}`.trim();
}

function truncatePath(path: string): string {
  if (path.length <= 60) {
    return path;
  }
  return `…${path.slice(path.length - 57)}`;
}

interface OverviewDashboardProps {
  statusQuery: UseQueryResult<StatusPayload>;
}

export function OverviewDashboard({ statusQuery }: OverviewDashboardProps): JSX.Element {
  const stageStatusQuery = useStageStatusQuery();
  const lintersQuery = useLintersLatestReport();

  const statusData = statusQuery.data;
  const rootPath = statusData?.absolute_root ?? statusData?.root_path ?? "—";
  const formattedRoot = truncatePath(rootPath);
  const watcherActive = statusData?.watcher_active ?? false;

  const detection = stageStatusQuery.data?.detection;
  const detectionAvailable = detection?.available ?? false;
  const stageTone: "success" | "warn" | "neutral" =
    stageStatusQuery.isLoading ? "neutral" : detectionAvailable ? "success" : "warn";
  const stageHeadline = stageStatusQuery.isLoading
    ? "Calculando estado…"
    : detectionAvailable
      ? `Stage ${detection?.recommended_stage ?? "?"}`
      : "No disponible";
  const stageConfidence = detection?.confidence
    ? detection.confidence.toUpperCase()
    : detectionAvailable
      ? "SIN CONF."
      : "—";
  const stageSummary = stageStatusQuery.isLoading
    ? "Obteniendo estado actual del Stage Toolkit."
    : detectionAvailable
      ? detection?.reasons?.[0] ?? "Toolkit en funcionamiento y sin incidencias."
      : detection?.error ?? "Aún no hay información suficiente sobre el Stage.";

  const lintersReport = lintersQuery.data ?? null;
  const lintersStatusKey = lintersReport?.report.summary.overall_status ?? "default";
  const lintersTone = LINTER_STATUS_TONE[lintersStatusKey] ?? "neutral";
  const lintersLabel = LINTER_STATUS_LABEL[lintersStatusKey] ?? LINTER_STATUS_LABEL.default;
  const lintersSummary = lintersReport
    ? lintersReport.report.summary
    : null;
  const lintersIssues = lintersSummary?.issues_total ?? 0;
  const lintersCritical = lintersSummary?.critical_issues ?? 0;
  const lintersDuration = lintersSummary?.duration_ms;
  const lintersGeneratedAt = lintersReport?.report.generated_at ?? lintersReport?.generated_at;

  const pendingEvents = statusData?.pending_events ?? 0;
  const capabilityIssues =
    statusData?.capabilities?.filter((capability) => !capability.available) ?? [];

  const alerts: Array<{
    tone: "info" | "warn" | "danger";
    message: string;
    link?: { label: string; to: string };
  }> = [];

  if (!watcherActive) {
    alerts.push({
      tone: "warn",
      message: "Watcher inactivo: recuerda lanzar un escaneo manual para mantener el mapa actualizado.",
      link: { label: "Ir a Stage Toolkit", to: "/stage-toolkit" },
    });
  }

  if (!stageStatusQuery.isLoading && !detectionAvailable) {
    alerts.push({
      tone: "warn",
      message: detection?.error
        ? `Stage Toolkit: ${detection.error}`
        : "Stage Toolkit sin detección reciente. Ejecuta un análisis para actualizarlo.",
      link: { label: "Ver Stage Toolkit", to: "/stage-toolkit" },
    });
  }

  if (
    lintersReport &&
    (lintersStatusKey === "fail" || lintersStatusKey === "error" || lintersCritical > 0)
  ) {
    alerts.push({
      tone: lintersStatusKey === "error" ? "danger" : "warn",
      message:
        lintersStatusKey === "error"
          ? "Los linters fallaron. Revisa el pipeline para ver los detalles."
          : "Los linters reportan incidencias. Consulta el detalle para priorizarlas.",
      link: { label: "Abrir Linters", to: "/linters" },
    });
  }

  if (pendingEvents > 25) {
    alerts.push({
      tone: "info",
      message: `Hay ${pendingEvents.toLocaleString("es-ES")} eventos pendientes por procesar.`,
      link: { label: "Ver Code Map", to: "/code-map" },
    });
  }

  if (capabilityIssues.length > 0) {
    alerts.push({
      tone: "warn",
      message: `Capacidades inhabilitadas: ${capabilityIssues
        .map((cap) => cap.description || cap.key)
        .slice(0, 3)
        .join(", ")}`,
      link: { label: "Configurar Settings", to: "/settings" },
    });
  }

  return (
    <div className="overview-view">
      <section className="overview-intro">
        <div className="overview-intro__text">
          <h2>Resumen general del workspace</h2>
          <p>
            Revisa el estado del Stage Toolkit, Code Map y los linters sin entrar en detalle. Si
            necesitas profundizar, abre la vista correspondiente desde aquí.
          </p>
          <div className="overview-meta">
            <span className={`overview-meta-pill ${watcherActive ? "success" : "warn"}`}>
              {watcherActive ? "Watcher activo" : "Watcher inactivo"}
            </span>
            <span className="overview-meta-path" title={rootPath}>
              Root: {formattedRoot}
            </span>
          </div>
        </div>
        <div className="overview-intro__actions">
          <RescanButton />
          <Link className="secondary-btn" to="/settings">
            Abrir settings
          </Link>
        </div>
      </section>

      {alerts.length > 0 ? (
        <section className="overview-alerts">
          {alerts.map((alert, index) => (
            <div key={`${alert.message}-${index}`} className={`overview-alert overview-alert--${alert.tone}`}>
              <span>{alert.message}</span>
              {alert.link ? (
                <Link className="overview-alert__cta" to={alert.link.to}>
                  {alert.link.label} →
                </Link>
              ) : null}
            </div>
          ))}
        </section>
      ) : null}

      <section className="overview-grid">
        <article className="overview-card overview-card--stage">
          <header className="overview-card__header">
            <div>
              <span className={`overview-pill ${stageTone}`}>{stageHeadline}</span>
              <h3>Stage Toolkit</h3>
            </div>
            <Link className="overview-card__cta" to="/stage-toolkit">
              Ver detalle →
            </Link>
          </header>
          <p className="overview-card__summary">{stageSummary}</p>
          <dl className="overview-metrics">
            <div>
              <dt>Confianza</dt>
              <dd>{stageConfidence}</dd>
            </div>
            <div>
              <dt>Última detección</dt>
              <dd>{formatDateTime(detection?.checked_at)}</dd>
            </div>
            <div>
              <dt>Motivos registrados</dt>
              <dd>{detection?.reasons?.length ? detection.reasons.length : 0}</dd>
            </div>
          </dl>
        </article>

        <article className="overview-card overview-card--code">
          <header className="overview-card__header">
            <div>
              <span className="overview-pill neutral">
                {statusQuery.isLoading ? "Cargando…" : "Indexación activa"}
              </span>
              <h3>Code Map</h3>
            </div>
            <Link className="overview-card__cta" to="/code-map">
              Abrir Code Map →
            </Link>
          </header>
          <p className="overview-card__summary">
            {statusQuery.isLoading
              ? "Recuperando métricas del analizador…"
              : `El analizador tiene ${statusData?.symbols_indexed?.toLocaleString("es-ES") ?? "0"} símbolos indexados.`}
          </p>
          <dl className="overview-metrics">
            <div>
              <dt>Archivos indexados</dt>
              <dd>{statusData?.files_indexed?.toLocaleString("es-ES") ?? "—"}</dd>
            </div>
            <div>
              <dt>Último escaneo</dt>
              <dd>{formatDateTime(statusData?.last_full_scan)}</dd>
            </div>
            <div>
              <dt>Eventos pendientes</dt>
              <dd>{pendingEvents.toLocaleString("es-ES")}</dd>
            </div>
          </dl>
        </article>

        <article className="overview-card overview-card--linters">
          <header className="overview-card__header">
            <div>
              <span className={`overview-pill ${lintersTone}`}>{lintersLabel}</span>
              <h3>Linters</h3>
            </div>
            <Link className="overview-card__cta" to="/linters">
              Ver linters →
            </Link>
          </header>
          <p className="overview-card__summary">
            {lintersQuery.isLoading
              ? "Buscando el último pipeline de linters…"
              : lintersReport
                ? `Último pipeline generado el ${formatDateTime(lintersGeneratedAt)}.`
                : "Todavía no hay reportes de linters disponibles."}
          </p>
          <dl className="overview-metrics">
            <div>
              <dt>Checks totales</dt>
              <dd>{lintersSummary?.total_checks?.toLocaleString("es-ES") ?? "—"}</dd>
            </div>
            <div>
              <dt>Incidencias</dt>
              <dd>{lintersIssues.toLocaleString("es-ES")}</dd>
            </div>
            <div>
              <dt>Críticas</dt>
              <dd>{lintersCritical.toLocaleString("es-ES")}</dd>
            </div>
            <div>
              <dt>Duración</dt>
              <dd>{formatDuration(lintersDuration)}</dd>
            </div>
          </dl>
        </article>
      </section>
    </div>
  );
}
