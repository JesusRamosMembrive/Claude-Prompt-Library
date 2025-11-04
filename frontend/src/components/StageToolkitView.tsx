import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import type {
  AgentInstallStatus,
  DocsStatus,
  StageAgentSelection,
  StageDetectionStatus,
} from "../api/types";
import { useStageInitMutation } from "../hooks/useStageInitMutation";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";

const AGENT_OPTIONS: { value: StageAgentSelection; label: string }[] = [
  { value: "both", label: "Claude + Codex" },
  { value: "claude", label: "Solo Claude" },
  { value: "codex", label: "Solo Codex" },
];

function formatList(values: string[]): JSX.Element {
  if (values.length === 0) {
    return <em>—</em>;
  }

  return (
    <ul className="stage-list">
      {values.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function AgentStatusCard({
  title,
  status,
}: {
  title: string;
  status: AgentInstallStatus | undefined;
}): JSX.Element {
  if (!status) {
    return (
      <article className="stage-card">
        <header>
          <h3>{title}</h3>
        </header>
        <p>No se pudo obtener el estado.</p>
      </article>
    );
  }

  const badgeClass = status.installed ? "stage-badge success" : "stage-badge warn";
  const badgeLabel = status.installed ? "Instalado" : "Faltan elementos";

  return (
    <article className="stage-card">
      <header>
        <h3>{title}</h3>
        <span className={badgeClass}>{badgeLabel}</span>
      </header>
      <section>
        <h4>Archivos presentes</h4>
        {formatList(status.present)}
      </section>
      <section>
        <h4>Archivos faltantes</h4>
        {formatList(status.missing)}
      </section>
      {status.optional && status.optional.expected.length > 0 ? (
        <section>
          <h4>Opcionales</h4>
          {status.optional.missing.length === 0 ? (
            <p className="stage-optional">Todos los opcionales están presentes.</p>
          ) : (
            <>
              <p className="stage-optional">
                Opcionales recomendados pero no estrictamente necesarios:
              </p>
              {formatList(status.optional.missing)}
            </>
          )}
        </section>
      ) : null}
    </article>
  );
}

function DocsStatusCard({ status }: { status: DocsStatus | undefined }): JSX.Element {
  if (!status) {
    return (
      <article className="stage-card">
        <header>
          <h3>Documentación</h3>
        </header>
        <p>No se pudo comprobar la carpeta docs/.</p>
      </article>
    );
  }
  const badgeClass = status.complete ? "stage-badge success" : "stage-badge warn";
  const badgeLabel = status.complete ? "Completa" : "Faltan archivos";

  return (
    <article className="stage-card">
      <header>
        <h3>Documentación</h3>
        <span className={badgeClass}>{badgeLabel}</span>
      </header>
      <section>
        <h4>Presentes</h4>
        {formatList(status.present)}
      </section>
      <section>
        <h4>Faltantes</h4>
        {formatList(status.missing)}
      </section>
    </article>
  );
}

function StageDetectionCard({ detection }: { detection: StageDetectionStatus | undefined }) {
  if (!detection) {
    return null;
  }
  const { available, recommended_stage, confidence, reasons, metrics, error, checked_at } = detection;

  if (!available) {
    return (
      <article className="stage-card">
        <header>
          <h3>Detección de etapa</h3>
          <span className="stage-badge warn">No disponible</span>
        </header>
        <p>{error ?? "No se pudo evaluar la etapa del proyecto."}</p>
      </article>
    );
  }

  return (
    <article className="stage-card stage-detection">
      <header>
        <h3>Detección de etapa</h3>
        <span className="stage-badge success">
          Stage {recommended_stage} · {confidence?.toUpperCase() ?? "N/A"}
        </span>
      </header>
      {checked_at ? (
        <p className="stage-meta">Última evaluación: {new Date(checked_at).toLocaleString()}</p>
      ) : null}
      <section>
        <h4>Motivos destacados</h4>
        {formatList(reasons)}
      </section>
      {metrics ? (
        <section>
          <h4>Métricas</h4>
          <dl className="stage-metrics">
            {Object.entries(metrics).map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{Array.isArray(value) ? value.join(", ") : String(value)}</dd>
              </div>
            ))}
          </dl>
        </section>
      ) : null}
    </article>
  );
}

export function StageToolkitView(): JSX.Element {
  const statusQuery = useStageStatusQuery();
  const initMutation = useStageInitMutation();

  const [selection, setSelection] = useState<StageAgentSelection>("both");

  const stageStatus = statusQuery.data;
  const initResult = initMutation.data;

  const stdout = initResult?.stdout?.trim();
  const stderr = initResult?.stderr?.trim();

  const mutationError = initMutation.error ? String(initMutation.error) : null;

  const currentAgentLabel = useMemo(
    () => AGENT_OPTIONS.find((option) => option.value === selection)?.label ?? "Claude + Codex",
    [selection],
  );

  const handleStageInit = () => {
    initMutation.mutate({ agents: selection });
  };

  return (
    <div className="stage-toolkit">
      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Estado del proyecto Stage-Aware</h2>
            <p>
              Revisa si los archivos clave para Claude Code y Codex CLI están presentes en el
              workspace actual.
            </p>
          </div>
          <button
            className="secondary-btn"
            type="button"
            onClick={() => statusQuery.refetch()}
            disabled={statusQuery.isFetching}
          >
            {statusQuery.isFetching ? "Verificando…" : "Volver a verificar"}
          </button>
        </header>

        {statusQuery.isLoading ? (
          <p className="stage-info">Cargando estado…</p>
        ) : statusQuery.isError ? (
          <p className="stage-error">
            No se pudo obtener el estado. {String(statusQuery.error)}
          </p>
        ) : (
          <div className="stage-status-grid">
            <AgentStatusCard title="Claude Code" status={stageStatus?.claude} />
            <AgentStatusCard title="Codex CLI" status={stageStatus?.codex} />
            <DocsStatusCard status={stageStatus?.docs} />
          </div>
        )}
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Ollama y recomendaciones</h2>
            <p>
              La configuración del servicio Ollama y el historial de insights ahora viven en una
              página dedicada.
            </p>
          </div>
        </header>

        <article className="stage-card">
          <p>
            Visita la pestaña <Link to="/ollama">Ollama</Link> para iniciar el servidor, probar
            modelos y gestionar las recomendaciones automáticas generadas por Ollama.
          </p>
          <p className="stage-hint">
            Desde allí podrás ajustar el modelo, la frecuencia, lanzar análisis manuales y revisar
            el historial reciente de insights.
          </p>
        </article>
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Inicializar o reinstalar instrucciones</h2>
            <p>
              Ejecuta <code>init_project.py --existing</code> (puedes añadir <code>--dry-run</code>
              para ensayar) sobre el workspace actual con los agentes seleccionados.
            </p>
          </div>
        </header>

        <div className="stage-actions">
          <label className="stage-radio-group-title" htmlFor="agent-selection">
            Agentes
          </label>
          <div className="stage-radio-group" id="agent-selection">
            {AGENT_OPTIONS.map((option) => (
              <label key={option.value} className="stage-radio">
                <input
                  type="radio"
                  name="agent"
                  value={option.value}
                  checked={selection === option.value}
                  onChange={() => setSelection(option.value)}
                  disabled={initMutation.isPending}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
          <button
            className="primary-btn"
            type="button"
            onClick={handleStageInit}
            disabled={initMutation.isPending}
          >
            {initMutation.isPending ? "Ejecutando…" : `Inicializar (${currentAgentLabel})`}
          </button>
        </div>

        {mutationError ? <p className="stage-error">{mutationError}</p> : null}
      </section>

      <section className="stage-section">
        {statusQuery.isLoading ? (
          <p className="stage-info">Calculando detección de etapa…</p>
        ) : stageStatus ? (
          <StageDetectionCard detection={stageStatus.detection} />
        ) : (
          <p className="stage-info">No se pudo obtener el estado del proyecto.</p>
        )}
      </section>

      {initResult ? (
        <section className="stage-section">
          <header className="stage-section-header">
            <div>
              <h2>Salida de init_project.py</h2>
              <p>
                Comando ejecutado: <code>{initResult.command.join(" ")}</code>
              </p>
            </div>
          </header>
          {stdout ? (
            <pre className="stage-output">{stdout}</pre>
          ) : (
            <p className="stage-info">No hubo salida en stdout.</p>
          )}
          {stderr ? <pre className="stage-output error">{stderr}</pre> : null}
        </section>
      ) : null}
    </div>
  );
}
