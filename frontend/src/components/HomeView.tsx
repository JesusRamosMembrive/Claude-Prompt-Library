import { Link } from "react-router-dom";
import type { UseQueryResult } from "@tanstack/react-query";

import type { StageDetectionStatus, StatusPayload } from "../api/types";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";

function renderStageHeadline(detection: StageDetectionStatus | undefined): string {
  if (!detection) {
    return "Comprueba instalación y detecta etapa automáticamente.";
  }
  if (!detection.available) {
    return detection.error ?? "Detección no disponible.";
  }
  return `Stage ${detection.recommended_stage} (${detection.confidence ?? "sin confianza"})`;
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

  return (
    <div className="home-view">
      <section className="home-hero">
        <h2>Stage-Aware Workspace</h2>
        <p>
          Gestiona la instalación de instrucciones para agentes y explora el mapa de código del
          proyecto actual.
        </p>
        <dl className="home-summary">
          <div>
            <dt>Root configurado</dt>
            <dd>{rootPath}</dd>
          </div>
          <div>
            <dt>Archivos indexados</dt>
            <dd>{filesIndexed}</dd>
          </div>
          <div>
            <dt>Detección actual</dt>
            <dd>
              {stageStatusQuery.isLoading
                ? "Calculando…"
                : renderStageHeadline(detection)}
            </dd>
          </div>
        </dl>
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
      </section>
    </div>
  );
}
