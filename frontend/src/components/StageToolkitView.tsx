import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { FormEvent } from "react";

import type {
  AgentInstallStatus,
  DocsStatus,
  StageAgentSelection,
  StageDetectionStatus,
  OllamaStatus,
  OllamaModelInfo,
} from "../api/types";
import { updateSettings, triggerOllamaInsights, clearOllamaInsights } from "../api/client";
import { queryKeys } from "../api/queryKeys";
import { useStageInitMutation } from "../hooks/useStageInitMutation";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";
import { useOllamaStatusQuery } from "../hooks/useOllamaStatusQuery";
import { useOllamaTestMutation } from "../hooks/useOllamaTestMutation";
import { useOllamaStartMutation } from "../hooks/useOllamaStartMutation";
import { useSettingsQuery } from "../hooks/useSettingsQuery";
import { useOllamaInsightsQuery } from "../hooks/useOllamaInsightsQuery";

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

function formatLatency(latencyMs: number): string {
  if (latencyMs < 1000) {
    return `${latencyMs.toFixed(0)} ms`;
  }
  return `${(latencyMs / 1000).toFixed(2)} s`;
}

function formatModelDetails(model: OllamaModelInfo): string | null {
  const details: string[] = [];
  if (model.size_human) {
    details.push(model.size_human);
  }
  if (model.modified_at) {
    details.push(`actualizado ${new Date(model.modified_at).toLocaleDateString()}`);
  }
  return details.length > 0 ? details.join(" · ") : null;
}

function OllamaStatusCard({
  status,
  lastChecked,
  onStart,
  isStarting,
  startError,
}: {
  status: OllamaStatus | undefined;
  lastChecked: string | undefined;
  onStart: () => void;
  isStarting: boolean;
  startError: string | null;
}): JSX.Element {
  if (!status) {
    return (
      <article className="stage-card">
        <header>
          <h3>Ollama</h3>
        </header>
        <p>No se pudo obtener el estado de Ollama.</p>
      </article>
    );
  }

  const runningBadgeClass = status.running ? "stage-badge success" : "stage-badge warn";
  const runningLabel = status.running ? "Activo" : "Detenido";
  const canStart = status.installed && !status.running;

  return (
    <article className="stage-card">
      <header>
        <h3>Ollama</h3>
        <span className={runningBadgeClass}>{runningLabel}</span>
      </header>
      <section>
        <p className="stage-meta">
          Instalación: <strong>{status.installed ? "Detectada" : "No encontrada"}</strong>
        </p>
        {status.version ? <p className="stage-meta">Versión: {status.version}</p> : null}
        {status.binary_path ? (
          <p className="stage-meta">
            Binario: <code>{status.binary_path}</code>
          </p>
        ) : null}
        {status.endpoint ? (
          <p className="stage-meta">
            Endpoint: <code>{status.endpoint}</code>
          </p>
        ) : null}
        {lastChecked ? (
          <p className="stage-meta">Última comprobación: {new Date(lastChecked).toLocaleString()}</p>
        ) : null}
      </section>
      <section>
        <h4>Modelos detectados</h4>
        {status.models.length > 0 ? (
          <ul className="stage-list">
            {status.models.map((model) => {
              const details = formatModelDetails(model);
              return (
                <li key={model.name}>
                  <span>{model.name}</span>
                  {details ? <span> · {details}</span> : null}
                </li>
              );
            })}
          </ul>
        ) : status.running ? (
          <p className="stage-info">No se encontraron modelos registrados.</p>
        ) : (
          <p className="stage-info">Inicia Ollama para enumerar los modelos disponibles.</p>
        )}
      </section>
      {status.warning ? <p className="stage-info">Aviso: {status.warning}</p> : null}
      {status.error ? <p className="stage-error">Error: {status.error}</p> : null}
      {canStart ? (
        <div className="stage-form-actions">
          <button className="secondary-btn" type="button" onClick={onStart} disabled={isStarting}>
            {isStarting ? "Iniciando…" : "Iniciar Ollama"}
          </button>
        </div>
      ) : null}
      {startError ? <p className="stage-error">{startError}</p> : null}
    </article>
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
  const ollamaStatusQuery = useOllamaStatusQuery();
  const ollamaTestMutation = useOllamaTestMutation();
  const ollamaStartMutation = useOllamaStartMutation();
  const settingsQuery = useSettingsQuery();
  const queryClient = useQueryClient();
  const insightsQuery = useOllamaInsightsQuery(10);

  const [selection, setSelection] = useState<StageAgentSelection>("both");
  const [selectedOllamaModel, setSelectedOllamaModel] = useState<string>("");
  const [ollamaPrompt, setOllamaPrompt] = useState<string>(
    "Resume brevemente el propósito del repositorio actual."
  );
  const [ollamaSystemPrompt, setOllamaSystemPrompt] = useState<string>("");
  const [ollamaEndpoint, setOllamaEndpoint] = useState<string>("");
  const [ollamaTimeout, setOllamaTimeout] = useState<string>("180");
  const [ollamaEndpointTouched, setOllamaEndpointTouched] = useState<boolean>(false);
  const [insightsEnabled, setInsightsEnabled] = useState<boolean>(false);
  const [insightsModel, setInsightsModel] = useState<string>("");
  const [insightsFrequency, setInsightsFrequency] = useState<string>("60");
  const [insightsStatus, setInsightsStatus] = useState<string | null>(null);

  const stageStatus = statusQuery.data;
  const initResult = initMutation.data;

  const stdout = initResult?.stdout?.trim();
  const stderr = initResult?.stderr?.trim();

  const mutationError = initMutation.error ? String(initMutation.error) : null;

  const ollamaStatus = ollamaStatusQuery.data?.status;
  const ollamaLastChecked = ollamaStatusQuery.data?.checked_at;

  const availableOllamaModels = useMemo(
    () => (ollamaStatus?.models ?? []).map((model) => model.name),
    [ollamaStatus]
  );

  useEffect(() => {
    if (availableOllamaModels.length > 0) {
      setSelectedOllamaModel((current) =>
        current && availableOllamaModels.includes(current)
          ? current
          : availableOllamaModels[0]
      );
    }
  }, [availableOllamaModels]);

  const ollamaEndpointHint = ollamaStatus?.endpoint ?? "http://127.0.0.1:11434";
  const isOllamaRunning = ollamaStatus?.running ?? false;
  const isOllamaDetected = ollamaStatus?.installed ?? false;
  const parsedTimeout = useMemo(() => {
    const raw = ollamaTimeout.trim();
    if (!raw) {
      return undefined;
    }
    const value = Number.parseFloat(raw);
    return Number.isFinite(value) ? value : undefined;
  }, [ollamaTimeout]);
  const isTimeoutValid =
    !ollamaTimeout.trim() ||
    (parsedTimeout !== undefined && parsedTimeout > 0 && parsedTimeout <= 1200);
  const isTestingOllama = ollamaTestMutation.isPending;
  const ollamaTestResult = ollamaTestMutation.data;
  const ollamaTestError = ollamaTestMutation.error;
  const canSubmitOllamaTest =
    selectedOllamaModel.trim().length > 0 && ollamaPrompt.trim().length > 0 && isTimeoutValid;
  const hasOllamaFeedback = Boolean(ollamaTestResult || ollamaTestError);
  const ollamaErrorMessage =
    (ollamaTestError?.detail?.message ?? ollamaTestError?.message) ?? null;
  const ollamaErrorEndpoint = ollamaTestError?.detail?.endpoint;
  const ollamaErrorOriginal = ollamaTestError?.detail?.original_error;
  const ollamaErrorReason = ollamaTestError?.detail?.reason_code ?? null;
  const ollamaErrorRetryAfterSeconds = ollamaTestError?.detail?.retry_after_seconds;
  const isOllamaLoadingModel = Boolean(ollamaTestError?.detail?.loading);
  const ollamaLoadingSinceRaw = ollamaTestError?.detail?.loading_since ?? null;
  const ollamaLoadingSince = useMemo(() => {
    if (!ollamaLoadingSinceRaw) {
      return null;
    }
    const parsed = new Date(ollamaLoadingSinceRaw);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }, [ollamaLoadingSinceRaw]);
  const formattedRetrySeconds =
    typeof ollamaErrorRetryAfterSeconds === "number" && Number.isFinite(ollamaErrorRetryAfterSeconds)
      ? Math.max(1, Math.round(ollamaErrorRetryAfterSeconds))
      : null;
  const showOllamaRetryHint =
    ollamaErrorReason === "timeout" || ollamaErrorReason === "service_unavailable";
  const showTimeoutError = Boolean(ollamaTimeout.trim() && !isTimeoutValid);
  const isStartingOllama = ollamaStartMutation.isPending;
  const ollamaStartError = ollamaStartMutation.error ? String(ollamaStartMutation.error) : null;
  const ollamaStartResult = ollamaStartMutation.data;
  const showOllamaDetectionWarning = !ollamaStatusQuery.isLoading && !isOllamaDetected;
  const showOllamaOfflineWarning =
    !ollamaStatusQuery.isLoading && isOllamaDetected && !isOllamaRunning;
  const settings = settingsQuery.data;
  const settingsLoading = settingsQuery.isLoading;
  const insightsHistory = insightsQuery.data ?? [];
  const insightsHistoryError = insightsQuery.error;
  const insightsLastRunRaw = statusQuery.data?.ollama_insights_last_run ?? null;
  const insightsNextRunRaw = statusQuery.data?.ollama_insights_next_run ?? null;
  const insightsLastRun = insightsLastRunRaw ? new Date(insightsLastRunRaw) : null;
  const insightsNextRun = insightsNextRunRaw ? new Date(insightsNextRunRaw) : null;

  const currentAgentLabel = useMemo(
    () => AGENT_OPTIONS.find((option) => option.value === selection)?.label ?? "Claude + Codex",
    [selection],
  );

  const handleOllamaStart = () => {
    ollamaStartMutation.mutate(
      {},
      {
        onSuccess: (data) => {
          if (!ollamaEndpointTouched && data.status.endpoint) {
            setOllamaEndpoint(data.status.endpoint);
          }
          ollamaStatusQuery.refetch();
        },
      },
    );
  };

  useEffect(() => {
    if (!settings) {
      return;
    }
    setInsightsEnabled(settings.ollama_insights_enabled);
    setInsightsModel(settings.ollama_insights_model ?? "");
    setInsightsFrequency(
      settings.ollama_insights_frequency_minutes !== null
        ? String(settings.ollama_insights_frequency_minutes)
        : "60",
    );
  }, [settings]);

  const originalInsightsEnabled = settings?.ollama_insights_enabled ?? false;
  const originalInsightsModel = settings?.ollama_insights_model ?? "";
  const originalInsightsFrequency =
    settings?.ollama_insights_frequency_minutes !== null &&
    settings?.ollama_insights_frequency_minutes !== undefined
      ? String(settings?.ollama_insights_frequency_minutes)
      : null;

  const trimmedInsightsModel = insightsModel.trim();
  const parsedInsightsFrequency = useMemo(() => {
    const raw = insightsFrequency.trim();
    if (!raw) {
      return null;
    }
    const value = Number.parseInt(raw, 10);
    return Number.isFinite(value) ? value : null;
  }, [insightsFrequency]);

  const isFrequencyValid =
    !insightsEnabled ||
    insightsFrequency.trim().length === 0 ||
    (parsedInsightsFrequency !== null &&
      parsedInsightsFrequency >= 1 &&
      parsedInsightsFrequency <= 1440);

  const insightsChanges: Record<string, unknown> = {};
  if (insightsEnabled !== originalInsightsEnabled) {
    insightsChanges.ollama_insights_enabled = insightsEnabled;
  }
  if (trimmedInsightsModel !== originalInsightsModel) {
    insightsChanges.ollama_insights_model = trimmedInsightsModel || null;
  }
  if (
    (parsedInsightsFrequency === null && originalInsightsFrequency !== null) ||
    (parsedInsightsFrequency !== null && String(parsedInsightsFrequency) !== originalInsightsFrequency)
  ) {
    insightsChanges.ollama_insights_frequency_minutes =
      parsedInsightsFrequency !== null ? parsedInsightsFrequency : null;
  }

  const hasInsightsChanges = Object.keys(insightsChanges).length > 0;

  const insightsMutation = useMutation({
    mutationFn: updateSettings,
    onSuccess: (result) => {
      queryClient.setQueryData(queryKeys.settings, result.settings);
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
      queryClient.invalidateQueries({ queryKey: queryKeys.settings });
      queryClient.invalidateQueries({ queryKey: queryKeys.stageStatus });
      queryClient.invalidateQueries({ queryKey: queryKeys.ollamaInsights(10) });
      setInsightsStatus(
        result.updated.length > 0
          ? `Preferencias actualizadas (${result.updated.join(", ")})`
          : "No había cambios que guardar.",
      );
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "Error desconocido";
      setInsightsStatus(`Error al guardar: ${message}`);
    },
  });

  const manualInsightsMutation = useMutation({
    mutationFn: (input: { model?: string; timeout_seconds?: number } | undefined) =>
      triggerOllamaInsights(input),
    onSuccess: (result) => {
      const timestamp = new Date(result.generated_at).toLocaleString();
      setInsightsStatus(`Insight generado (${timestamp}).`);
      queryClient.invalidateQueries({ queryKey: queryKeys.ollamaInsights(10) });
      queryClient.invalidateQueries({ queryKey: queryKeys.status });
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "No se pudo generar el insight.";
      setInsightsStatus(`Error al generar insight: ${message}`);
    },
  });

  const clearInsightsMutation = useMutation({
    mutationFn: clearOllamaInsights,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ollamaInsights(10) });
      setInsightsStatus(
        result.deleted > 0
          ? `Se eliminaron ${result.deleted} insights almacenados.`
          : "No había insights que eliminar.",
      );
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : "No se pudo limpiar el historial.";
      setInsightsStatus(`Error al limpiar historial: ${message}`);
    },
  });

  const handleInsightsSave = () => {
    if (!isFrequencyValid || insightsMutation.isPending || !hasInsightsChanges) {
      return;
    }
    setInsightsStatus(null);
    insightsMutation.mutate(insightsChanges);
  };

  useEffect(() => {
    if (ollamaStatus?.endpoint) {
      if (!ollamaEndpointTouched) {
        setOllamaEndpoint(ollamaStatus.endpoint);
      }
    } else if (!ollamaEndpointTouched) {
      setOllamaEndpoint("");
    }
  }, [ollamaStatus, ollamaEndpointTouched]);

  useEffect(() => {
    const detected = ollamaStatus?.endpoint ?? "";
    if (ollamaEndpointTouched && ollamaEndpoint.trim() === detected.trim()) {
      setOllamaEndpointTouched(false);
    }
  }, [ollamaEndpoint, ollamaStatus, ollamaEndpointTouched]);

  const handleOllamaTestSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!canSubmitOllamaTest) {
      return;
    }
    const payload: {
      model: string;
      prompt: string;
      system_prompt?: string;
      endpoint?: string;
      timeout_seconds?: number;
    } = {
      model: selectedOllamaModel.trim(),
      prompt: ollamaPrompt.trim(),
    };
    if (ollamaSystemPrompt.trim()) {
      payload.system_prompt = ollamaSystemPrompt.trim();
    }
    const endpointValue = ollamaEndpoint.trim();
    if (endpointValue) {
      payload.endpoint = endpointValue;
    }
    if (parsedTimeout !== undefined && isTimeoutValid) {
      payload.timeout_seconds = parsedTimeout;
    }
    ollamaTestMutation.mutate(payload);
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
            <h2>Ollama local</h2>
            <p>
              Comprueba si el servidor Ollama está instalado y disponible, y qué modelos puedes usar
              desde esta máquina.
            </p>
          </div>
          <button
            className="secondary-btn"
            type="button"
            onClick={() => ollamaStatusQuery.refetch()}
            disabled={ollamaStatusQuery.isFetching}
          >
            {ollamaStatusQuery.isFetching ? "Analizando…" : "Comprobar de nuevo"}
          </button>
        </header>

        {ollamaStatusQuery.isLoading ? (
          <p className="stage-info">Analizando el estado de Ollama…</p>
        ) : ollamaStatusQuery.isError ? (
          <p className="stage-error">
            No se pudo consultar el estado de Ollama. {String(ollamaStatusQuery.error)}
          </p>
        ) : (
          <>
            <OllamaStatusCard
              status={ollamaStatus}
              lastChecked={ollamaLastChecked}
              onStart={handleOllamaStart}
              isStarting={isStartingOllama}
              startError={ollamaStartError}
            />
            {ollamaStartResult ? (
              <p className="stage-meta">
                {ollamaStartResult.already_running
                  ? "Ollama ya estaba en ejecución."
                  : `Ollama se inició correctamente (PID ${
                      ollamaStartResult.process_id ?? "?"
                    }).`}
              </p>
            ) : null}
          </>
        )}
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Insights automáticos con Ollama</h2>
            <p>
              Permite que Ollama genere recomendaciones periódicas sobre refactors, linters y estrategias.
            </p>
          </div>
        </header>

        <article className="stage-card">
          {settingsLoading ? (
            <p className="stage-info">Cargando preferencias…</p>
          ) : (
            <>
              <div className="stage-form-field stage-toggle-field">
                <span>Activar insights</span>
                <label className="stage-switch">
                  <input
                    type="checkbox"
                    checked={insightsEnabled}
                    onChange={(event) => setInsightsEnabled(event.target.checked)}
                    disabled={insightsMutation.isPending}
                  />
                  <span className="stage-switch-slider" aria-hidden="true" />
                </label>
              </div>

              <div className="stage-form-field">
                <span>Modelo preferido</span>
                <input
                  className="stage-input"
                  type="text"
                  list="ollama-insights-models"
                  value={insightsModel}
                  onChange={(event) => setInsightsModel(event.target.value)}
                  placeholder="Ej. gpt-oss:latest"
                  disabled={!insightsEnabled || insightsMutation.isPending}
                />
                <datalist id="ollama-insights-models">
                  {availableOllamaModels.map((model) => (
                    <option value={model} key={`insights-model-${model}`} />
                  ))}
                </datalist>
                <p className="stage-hint">
                  Puedes escribir cualquier modelo disponible en tu instalación de Ollama.
                </p>
              </div>

              <div className="stage-form-field">
                <span>Frecuencia (minutos)</span>
                <input
                  className="stage-input"
                  type="number"
                  min={1}
                  max={1440}
                  value={insightsFrequency}
                  onChange={(event) => setInsightsFrequency(event.target.value)}
                  disabled={!insightsEnabled || insightsMutation.isPending}
                />
                {!isFrequencyValid ? (
                  <p className="stage-error">
                    Introduce un número entre 1 y 1440 minutos o deja el campo vacío.
                  </p>
                ) : (
                  <p className="stage-hint">
                    Define cada cuánto se ejecutarán los análisis. Déjalo vacío para usar el valor por defecto (60 min).
                  </p>
                )}
              </div>

              <div className="stage-form-actions">
                <button
                  className="primary-btn"
                  type="button"
                  onClick={handleInsightsSave}
                  disabled={
                    insightsMutation.isPending ||
                    !hasInsightsChanges ||
                    !isFrequencyValid
                  }
                >
                  {insightsMutation.isPending ? "Guardando…" : "Guardar preferencias"}
                </button>
                <button
                  className="secondary-btn"
                  type="button"
                  onClick={() => {
                    if (!settings) {
                      return;
                    }
                    setInsightsEnabled(settings.ollama_insights_enabled);
                    setInsightsModel(settings.ollama_insights_model ?? "");
                    setInsightsFrequency(
                      settings.ollama_insights_frequency_minutes !== null
                        ? String(settings.ollama_insights_frequency_minutes)
                        : "60",
                    );
                    setInsightsStatus("Restablecido a los valores actuales.");
                  }}
                  disabled={insightsMutation.isPending}
                >
                  Deshacer cambios
                </button>
              </div>
              {insightsStatus ? (
                <p className="stage-info">{insightsStatus}</p>
              ) : null}
              <div className="stage-form-field">
                <span>Historial reciente</span>
                {insightsQuery.isLoading ? (
                  <p className="stage-info">Recuperando insights generados…</p>
                ) : insightsQuery.isError ? (
                  <p className="stage-error">
                    Error al cargar historial: {String(insightsHistoryError)}
                  </p>
                ) : insightsHistory.length === 0 ? (
                  <p className="stage-hint">
                    No se han registrado insights todavía. Genera uno manualmente o espera a la próxima ejecución automática.
                  </p>
                ) : (
                  <ul className="stage-list stage-insights-list">
                    {insightsHistory.map((entry) => (
                      <li key={entry.id}>
                        <strong>{entry.model}</strong>
                        <span> · {new Date(entry.generated_at).toLocaleString()}</span>
                        <p className="stage-insight-message">{entry.message}</p>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              <div className="stage-form-actions">
                <button
                  className="secondary-btn"
                  type="button"
                  onClick={() => {
                    const payload = trimmedInsightsModel
                      ? { model: trimmedInsightsModel || undefined }
                      : undefined;
                    manualInsightsMutation.mutate(payload);
                  }}
                  disabled={manualInsightsMutation.isPending}
                >
                  {manualInsightsMutation.isPending ? "Generando…" : "Generar ahora"}
                </button>
                <button
                  className="secondary-btn"
                  type="button"
                  onClick={() => clearInsightsMutation.mutate()}
                  disabled={clearInsightsMutation.isPending}
                >
                  {clearInsightsMutation.isPending ? "Limpiando…" : "Limpiar historial"}
                </button>
                {insightsLastRun ? (
                  <p className="stage-hint">
                    Última ejecución: {insightsLastRun.toLocaleString()}
                    {insightsNextRun ? ` · Próxima estimada: ${insightsNextRun.toLocaleString()}` : ""}
                  </p>
                ) : (
                  <p className="stage-hint">
                    Aún no se han ejecutado insights automáticamente.
                  </p>
                )}
              </div>
            </>
          )}
        </article>
      </section>

      <section className="stage-section">
        <header className="stage-section-header">
          <div>
            <h2>Ping a Ollama</h2>
            <p>
              Envía un prompt corto al modelo local para asegurarte de que el servicio responde y
              mide la latencia.
            </p>
          </div>
        </header>

        {showOllamaDetectionWarning ? (
          <p className="stage-info">
            Aún no detectamos Ollama instalado. Si lo tienes en otra ruta, ajusta el campo de
            endpoint y prueba igualmente.
          </p>
        ) : null}
        {showOllamaOfflineWarning ? (
          <p className="stage-error">
            Ollama está instalado pero el endpoint <code>{ollamaEndpointHint}</code> no respondió.
            Intenta iniciarlo con el botón anterior o hazlo manualmente.
          </p>
        ) : null}

        <form className="stage-form" onSubmit={handleOllamaTestSubmit}>
          <label className="stage-form-field">
            <span>Modelo</span>
            {availableOllamaModels.length > 0 ? (
              <select
                className="stage-select"
                value={selectedOllamaModel}
                onChange={(event) => setSelectedOllamaModel(event.target.value)}
                disabled={isTestingOllama}
              >
                {availableOllamaModels.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            ) : (
              <input
                className="stage-input"
                type="text"
                value={selectedOllamaModel}
                placeholder="Introduce el nombre del modelo (ej. llama3)"
                onChange={(event) => setSelectedOllamaModel(event.target.value)}
                disabled={isTestingOllama}
              />
            )}
          </label>

          <label className="stage-form-field">
            <span>Endpoint (opcional)</span>
            <input
              className="stage-input"
              type="text"
              value={ollamaEndpoint}
              placeholder={ollamaEndpointHint}
              onChange={(event) => {
                setOllamaEndpoint(event.target.value);
                setOllamaEndpointTouched(true);
              }}
              disabled={isTestingOllama}
              aria-label="Endpoint de Ollama"
            />
            <p className="stage-hint">
              Deja el campo vacío para usar el endpoint detectado automáticamente.
            </p>
          </label>

          <label className="stage-form-field">
            <span>Tiempo máximo de respuesta (segundos)</span>
            <input
              className="stage-input"
              type="number"
              min={1}
              max={1200}
              step={0.5}
              value={ollamaTimeout}
              onChange={(event) => setOllamaTimeout(event.target.value)}
              disabled={isTestingOllama}
              aria-label="Tiempo máximo de espera para la respuesta"
            />
            {showTimeoutError ? (
              <p className="stage-error">Introduce un valor entre 1 y 1200 segundos o deja el campo vacío.</p>
            ) : (
              <p className="stage-hint">
                Vacío usa el valor por defecto ({parsedTimeout ?? 180} s). Usa este límite para evitar esperas largas.
              </p>
            )}
          </label>

          <label className="stage-form-field">
            <span>System prompt (opcional)</span>
            <textarea
              className="stage-textarea"
              value={ollamaSystemPrompt}
              onChange={(event) => setOllamaSystemPrompt(event.target.value)}
              placeholder="Contexto adicional para orientar la respuesta."
              disabled={isTestingOllama}
            />
          </label>

          <label className="stage-form-field">
            <span>Prompt</span>
            <textarea
              className="stage-textarea"
              value={ollamaPrompt}
              onChange={(event) => setOllamaPrompt(event.target.value)}
              placeholder="Mensaje que quieres enviar al modelo."
              required
              disabled={isTestingOllama}
            />
          </label>

          <p className="stage-hint">
            Endpoint detectado: <code>{ollamaEndpointHint}</code>. Ajusta el campo de arriba o la
            variable <code>OLLAMA_HOST</code> si utilizas otra dirección.
          </p>

          <div className="stage-form-actions">
            <button
              className="primary-btn"
              type="submit"
              disabled={isTestingOllama || !canSubmitOllamaTest}
            >
              {isTestingOllama ? "Consultando…" : "Probar chat"}
            </button>
            {hasOllamaFeedback ? (
              <button
                className="secondary-btn"
                type="button"
                onClick={() => ollamaTestMutation.reset()}
                disabled={isTestingOllama}
              >
                Limpiar resultado
              </button>
            ) : null}
          </div>
        </form>

        {ollamaErrorMessage ? (
          <article className="stage-card">
            <header>
              <h3>Error al contactar con Ollama</h3>
              <span className="stage-badge warn">Falló</span>
            </header>
            <p className="stage-error">{ollamaErrorMessage}</p>
            {ollamaErrorEndpoint ? (
              <p className="stage-meta">
                Endpoint: <code>{ollamaErrorEndpoint}</code>
              </p>
            ) : null}
            {ollamaErrorOriginal ? (
              <p className="stage-meta">Detalle: {ollamaErrorOriginal}</p>
            ) : null}
            {isOllamaLoadingModel ? (
              <p className="stage-info">
                Detectamos que el modelo sigue cargándose
                {ollamaLoadingSince ? (
                  <> desde {ollamaLoadingSince.toLocaleTimeString()}</>
                ) : null}
                .{" "}
                Intenta nuevamente
                {formattedRetrySeconds ? <> en ~{formattedRetrySeconds} s</> : " en unos segundos"} o revisa los logs con{" "}
                <code>ollama serve</code>.
              </p>
            ) : null}
            {!isOllamaLoadingModel && showOllamaRetryHint ? (
              <p className="stage-info">
                Ollama sugirió reintentar pronto
                {formattedRetrySeconds ? <> (≈{formattedRetrySeconds} s)</> : ""}. Si el modelo tarda demasiado, abre una
                terminal y observa <code>ollama serve</code>.
              </p>
            ) : null}
          </article>
        ) : null}

        {ollamaTestResult ? (
          <article className="stage-card">
            <header>
              <h3>Respuesta de {ollamaTestResult.model}</h3>
              <span className="stage-badge success">
                {formatLatency(ollamaTestResult.latency_ms)}
              </span>
            </header>
            <p className="stage-meta">
              Endpoint: <code>{ollamaTestResult.endpoint}</code>
            </p>
            <section>
              <h4>Mensaje</h4>
              <pre className="stage-output">{ollamaTestResult.message}</pre>
            </section>
            <details className="stage-details">
              <summary>Ver JSON completo</summary>
              <pre className="stage-output">
                {JSON.stringify(ollamaTestResult.raw, null, 2)}
              </pre>
            </details>
          </article>
        ) : null}
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
            onClick={() => initMutation.mutate({ agents: selection })}
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
