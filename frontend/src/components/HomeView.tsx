import { Link } from "react-router-dom";
import type { UseQueryResult } from "@tanstack/react-query";

import type { StageDetectionStatus, StatusPayload } from "../api/types";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";

function detectionBadgeLabel(detection?: StageDetectionStatus): string {
  if (!detection) {
    return "Cargando detección…";
  }
  if (!detection.available) {
    return detection.error ?? "Detección no disponible";
  }
  const stage = detection.recommended_stage ?? "?";
  const confidence = detection.confidence ? detection.confidence.toUpperCase() : "SIN CONF.";
  return `Stage ${stage} · ${confidence}`;
}

export function HomeView({
  statusQuery,
}: {
  statusQuery: UseQueryResult<StatusPayload>;
}): JSX.Element {
  const stageStatusQuery = useStageStatusQuery();

  const rootPath = statusQuery.data?.absolute_root ?? statusQuery.data?.root_path ?? "—";
  const filesIndexed = statusQuery.data?.files_indexed ?? 0;
  const detection = stageStatusQuery.data?.detection;
  const reasons = detection?.reasons ?? [];
  const detectionAvailable = detection?.available ?? false;

  const detectionTone = detectionAvailable ? "success" : "warn";
  const detectionLabel = detectionBadgeLabel(detection);

  const lastScan = statusQuery.data?.last_full_scan
    ? new Date(statusQuery.data.last_full_scan).toLocaleString()
    : "Sin escaneos todavía";

  const formattedRoot =
    rootPath.length > 60 ? `…${rootPath.slice(rootPath.length - 57)}` : rootPath;

  return (
    <div className="home-view">
      <section className="home-hero">
        <div className="home-hero__glow" aria-hidden />
        <div className="home-hero__content">
          <span className={`home-stage-pill ${detectionTone}`}>
            {stageStatusQuery.isLoading ? "Calculando…" : detectionLabel}
          </span>
          <h2>Build con IA, sin perder el control.</h2>
          <p>
            Asegura que los agentes sigan las reglas del proyecto con el Stage Toolkit o explora el
            código con el Code Map enriquecido.
          </p>
          <dl className="home-summary">
            <div>
              <dt>Root configurado</dt>
              <dd title={rootPath}>{formattedRoot}</dd>
            </div>
            <div>
              <dt>Archivos indexados</dt>
              <dd>{filesIndexed.toLocaleString("es-ES")}</dd>
            </div>
            <div>
              <dt>Último escaneo</dt>
              <dd>{lastScan}</dd>
            </div>
          </dl>
        </div>

        <div className="home-hero__panel">
          <h3>Claves de la detección</h3>
          {stageStatusQuery.isLoading ? (
            <p className="home-hero__panel-loading">Analizando repositorio…</p>
          ) : detectionAvailable && reasons.length > 0 ? (
            <ul>
              {reasons.slice(0, 4).map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p className="home-hero__panel-empty">
              {detection?.error ?? "Aún no hay información suficiente para reportar."}
            </p>
          )}

          {detection?.metrics ? (
            <div className="home-hero__metrics">
              <div>
                <span className="metric-label">Archivos</span>
                <span className="metric-value">
                  {Number(detection.metrics.file_count ?? 0).toLocaleString("es-ES")}
                </span>
              </div>
              <div>
                <span className="metric-label">LOC aprox.</span>
                <span className="metric-value">
                  {Number(detection.metrics.lines_of_code ?? 0).toLocaleString("es-ES")}
                </span>
              </div>
              <div>
                <span className="metric-label">Patrones</span>
                <span className="metric-value">
                  {Array.isArray(detection.metrics.patterns_found) &&
                  detection.metrics.patterns_found.length > 0
                    ? detection.metrics.patterns_found.slice(0, 3).join(", ")
                    : "—"}
                </span>
              </div>
            </div>
          ) : null}
        </div>
      </section>

      <section className="home-card-grid">
        <Link to="/stage-toolkit" className="home-card">
          <div className="home-card-body">
            <h3>Project Stage Toolkit</h3>
            <p>
              Ejecuta <code>init_project.py</code>, valida archivos requeridos para Claude Code y
              Codex CLI, y consulta la etapa detectada del proyecto.
            </p>
          </div>
          <span className="home-card-cta">Abrir toolkit →</span>
        </Link>

        <Link to="/code-map" className="home-card">
          <div className="home-card-body">
            <h3>Code Map</h3>
            <p>
              Navega símbolos, búsqueda semántica y actividad reciente del repositorio. Ideal para
              explorar el código con contexto.
            </p>
          </div>
          <span className="home-card-cta">Abrir Code Map →</span>
        </Link>

        <article className="home-card home-card--neutral">
          <div className="home-card-body">
            <h3>Estado del workspace</h3>
            <p>
              {stageStatusQuery.isLoading
                ? "Evaluando estado del proyecto…"
                : detectionAvailable
                  ? `El proyecto se recomienda como Stage ${detection?.recommended_stage} con ${detection?.confidence ?? "confianza media"}.`
                  : "Aún no se ha podido determinar la etapa del proyecto."}
            </p>
            <ul className="home-card-list">
              <li>
                {statusQuery.data?.watcher_active
                  ? "Watcher activo para notificar cambios."
                  : "Watcher inactivo: ejecuta un escaneo manual cuando lo necesites."}
              </li>
              <li>Archivos indexados: {filesIndexed.toLocaleString("es-ES")}.</li>
              <li>Workspace actual: {rootPath}</li>
            </ul>
          </div>
        </article>

        <Link to="/class-uml" className="home-card">
          <div className="home-card-body">
            <h3>Class UML</h3>
            <p>
              Diagramas UML con atributos y métodos por clase. Perfecto para entender la estructura
              interna sin ruido externo.
            </p>
          </div>
          <span className="home-card-cta">Ver UML →</span>
        </Link>

        <Link to="/linters" className="home-card">
          <div className="home-card-body">
            <h3>Linters</h3>
            <p>
              Revisa el estado de los linters configurados, últimos resultados y logs para mantener
              la calidad del código.
            </p>
          </div>
          <span className="home-card-cta">Ver Linters →</span>
        </Link>
      </section>
    </div>
  );
}
