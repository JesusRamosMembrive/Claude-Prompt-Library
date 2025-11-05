import { Link } from "react-router-dom";
import type { UseQueryResult } from "@tanstack/react-query";

import type { StatusPayload } from "../api/types";
import { useStageStatusQuery } from "../hooks/useStageStatusQuery";
import { useLintersLatestReport } from "../hooks/useLintersLatestReport";
import { useOllamaInsightsQuery } from "../hooks/useOllamaInsightsQuery";

const LINTER_STATUS_LABEL: Record<string, string> = {
  pass: "OK",
  warn: "Warnings",
  fail: "Failing",
  skipped: "Skipped",
  error: "Error",
  default: "No data",
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
    return new Date(value).toLocaleString("en-US");
  } catch {
    return value;
  }
}

function formatDuration(ms?: number | null): string {
  if (!ms || ms <= 0) {
    return "—";
  }
  if (ms < 1000) {
    return `${ms.toLocaleString("en-US")} ms`;
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
  return path;
}

interface OverviewDashboardProps {
  statusQuery: UseQueryResult<StatusPayload>;
}

export function OverviewDashboard({ statusQuery }: OverviewDashboardProps): JSX.Element {
  const stageStatusQuery = useStageStatusQuery();
  const lintersQuery = useLintersLatestReport();
  const ollamaInsightsQuery = useOllamaInsightsQuery(5);

  const statusData = statusQuery.data;
  const rootPath = statusData?.absolute_root ?? statusData?.root_path ?? "—";
  const formattedRoot = truncatePath(rootPath);
  const watcherActive = statusData?.watcher_active ?? false;
  const filesIndexed = statusData?.files_indexed ?? 0;
  const lastFullScanLabel = statusData?.last_full_scan
    ? formatDateTime(statusData.last_full_scan)
    : "No scans yet";

  const detection = stageStatusQuery.data?.detection;
  const detectionAvailable = detection?.available ?? false;
  const detectionReasons = detection?.reasons ?? [];
  const stageTone: "success" | "warn" | "neutral" =
    stageStatusQuery.isLoading ? "neutral" : detectionAvailable ? "success" : "warn";
  const stageHeadline = stageStatusQuery.isLoading
    ? "Calculating status…"
    : detectionAvailable
      ? `Stage ${detection?.recommended_stage ?? "?"}`
      : "Unavailable";
  const stageConfidence = detection?.confidence
    ? detection.confidence.toUpperCase()
    : detectionAvailable
      ? "NO CONF."
      : "—";
  const stageSummary = stageStatusQuery.isLoading
    ? "Fetching the current Stage Toolkit status."
    : detectionAvailable
      ? detection?.reasons?.[0] ?? "Toolkit operating without reported issues."
      : detection?.error ?? "Not enough information about the Stage yet.";

  const highlightCards = [
    {
      key: "root",
      title: "Configured root",
      value: formattedRoot,
      tooltip: rootPath,
    },
    {
      key: "files",
      title: "Indexed files",
      value: filesIndexed.toLocaleString("en-US"),
    },
    {
      key: "scan",
      title: "Last scan",
      value: lastFullScanLabel,
    },
  ];

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

  const ollamaInsights = ollamaInsightsQuery.data ?? [];
  const ollamaInsightsEnabled = statusData?.ollama_insights_enabled ?? false;
  const ollamaInsightsError =
    ollamaInsightsQuery.error instanceof Error ? ollamaInsightsQuery.error : null;
  const latestOllamaInsight = ollamaInsights[0] ?? null;

  let ollamaInsightsTone: "success" | "warn" | "danger" | "neutral" = "neutral";
  let ollamaInsightsLabel = "No data";
  if (ollamaInsightsQuery.isLoading) {
    ollamaInsightsLabel = "Loading…";
  } else if (ollamaInsightsError) {
    ollamaInsightsTone = "danger";
    ollamaInsightsLabel = "Error";
  } else if (ollamaInsightsEnabled && ollamaInsights.length > 0) {
    ollamaInsightsTone = "success";
    ollamaInsightsLabel = "Insights active";
  } else if (ollamaInsightsEnabled) {
    ollamaInsightsTone = "warn";
    ollamaInsightsLabel = "No messages";
  } else {
    ollamaInsightsTone = "neutral";
    ollamaInsightsLabel = "Disabled";
  }

  let ollamaInsightsSummary =
    "Ollama Insights is disabled. Enable recommendations from Settings.";
  if (ollamaInsightsQuery.isLoading) {
    ollamaInsightsSummary = "Retrieving the latest messages generated by Ollama…";
  } else if (ollamaInsightsError) {
    ollamaInsightsSummary = `Could not retrieve insights: ${ollamaInsightsError.message}`;
  } else if (ollamaInsightsEnabled && latestOllamaInsight) {
    ollamaInsightsSummary = `Latest insight generated on ${formatDateTime(latestOllamaInsight.generated_at)} by model ${latestOllamaInsight.model}.`;
  } else if (ollamaInsightsEnabled) {
    ollamaInsightsSummary =
      "No insights have been generated yet. Run an analysis from the Ollama tab.";
  }

  const ollamaInsightsLastRun = statusData?.ollama_insights_last_run ?? null;
  const ollamaInsightsNextRun = statusData?.ollama_insights_next_run ?? null;

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
      message: "Watcher inactive: remember to run a manual scan to keep the map current.",
      link: { label: "Go to Stage Toolkit", to: "/stage-toolkit" },
    });
  }

  if (!stageStatusQuery.isLoading && !detectionAvailable) {
    alerts.push({
      tone: "warn",
      message: detection?.error
        ? `Stage Toolkit: ${detection.error}`
        : "Stage Toolkit has no recent detection. Run an analysis to refresh it.",
      link: { label: "Open Stage Toolkit", to: "/stage-toolkit" },
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
          ? "Linters failed. Review the pipeline for details."
          : "Linters reported issues. Check the details to prioritize them.",
      link: { label: "Open Linters", to: "/linters" },
    });
  }

  if (pendingEvents > 25) {
    alerts.push({
      tone: "info",
      message: `There are ${pendingEvents.toLocaleString("en-US")} events pending processing.`,
      link: { label: "View Code Map", to: "/code-map" },
    });
  }

  if (capabilityIssues.length > 0) {
    alerts.push({
      tone: "warn",
      message: `Capabilities unavailable: ${capabilityIssues
        .map((cap) => cap.description || cap.key)
        .slice(0, 3)
        .join(", ")}`,
      link: { label: "Open Settings", to: "/settings" },
    });
  }

  return (
    <div className="overview-view">
      <section className="overview-intro">
        <div className="overview-intro__text">
          <h2>Workspace overview</h2>
          <p>Review Stage Toolkit, Code Map, and linters at a glance. Dive deeper from here.</p>
          <div className="overview-meta">
            <span className={`overview-meta-pill ${watcherActive ? "success" : "warn"}`}>
              {watcherActive ? "Watcher active" : "Watcher inactive"}
            </span>
          </div>
        </div>

        <div className="overview-detection-card">
          <span className="overview-highlight__title">Detection highlights</span>
          {stageStatusQuery.isLoading ? (
            <p className="overview-highlight__note">Analyzing repository…</p>
          ) : detectionAvailable && detectionReasons.length > 0 ? (
            <ul className="overview-highlight__list">
              {detectionReasons.slice(0, 4).map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          ) : (
            <p className="overview-highlight__note">
              {detection?.error ?? "Not enough information to report yet."}
            </p>
          )}

          {detection?.metrics ? (
            <div className="overview-highlight__metrics">
              <div>
                <span className="metric-label">Files</span>
                <span className="metric-value">
                  {Number(detection.metrics.file_count ?? 0).toLocaleString("en-US")}
                </span>
              </div>
              <div>
                <span className="metric-label">Approx. LOC</span>
                <span className="metric-value">
                  {Number(detection.metrics.lines_of_code ?? 0).toLocaleString("en-US")}
                </span>
              </div>
              <div>
                <span className="metric-label">Patterns</span>
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

        <section className="overview-highlight">
          {highlightCards.map((card) => (
            <div key={card.key} className="overview-highlight__card">
              <span className="overview-highlight__title">{card.title}</span>
              <span
                className="overview-highlight__value"
                title={card.tooltip ?? undefined}
              >
                {card.value}
              </span>
            </div>
          ))}
        </section>
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
              View details →
            </Link>
          </header>
          <p className="overview-card__summary">{stageSummary}</p>
          <dl className="overview-metrics">
            <div>
              <dt>Confidence</dt>
              <dd>{stageConfidence}</dd>
            </div>
            <div>
              <dt>Last detection</dt>
              <dd>{formatDateTime(detection?.checked_at)}</dd>
            </div>
            <div>
              <dt>Recorded reasons</dt>
              <dd>{detection?.reasons?.length ? detection.reasons.length : 0}</dd>
            </div>
          </dl>
        </article>

        <article className="overview-card overview-card--code">
          <header className="overview-card__header">
            <div>
              <span className="overview-pill neutral">
                {statusQuery.isLoading ? "Loading…" : "Indexing active"}
              </span>
              <h3>Code Map</h3>
            </div>
            <Link className="overview-card__cta" to="/code-map">
              Open Code Map →
            </Link>
          </header>
          <p className="overview-card__summary">
            {statusQuery.isLoading
              ? "Retrieving analyzer metrics…"
              : `The analyzer has ${statusData?.symbols_indexed?.toLocaleString("en-US") ?? "0"} indexed symbols.`}
          </p>
          <dl className="overview-metrics">
            <div>
              <dt>Indexed files</dt>
              <dd>{statusData?.files_indexed?.toLocaleString("en-US") ?? "—"}</dd>
            </div>
            <div>
              <dt>Last full scan</dt>
              <dd>{formatDateTime(statusData?.last_full_scan)}</dd>
            </div>
            <div>
              <dt>Pending events</dt>
              <dd>{pendingEvents.toLocaleString("en-US")}</dd>
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
              View linters →
            </Link>
          </header>
          <p className="overview-card__summary">
            {lintersQuery.isLoading
              ? "Fetching the latest linter pipeline…"
              : lintersReport
                ? `Latest pipeline generated on ${formatDateTime(lintersGeneratedAt)}.`
                : "No linter reports available yet."}
          </p>
          <dl className="overview-metrics">
            <div>
              <dt>Total checks</dt>
              <dd>{lintersSummary?.total_checks?.toLocaleString("en-US") ?? "—"}</dd>
            </div>
            <div>
              <dt>Issues</dt>
              <dd>{lintersIssues.toLocaleString("en-US")}</dd>
            </div>
            <div>
              <dt>Critical</dt>
              <dd>{lintersCritical.toLocaleString("en-US")}</dd>
            </div>
            <div>
              <dt>Duration</dt>
              <dd>{formatDuration(lintersDuration)}</dd>
            </div>
          </dl>
        </article>

        <article className="overview-card overview-card--ollama">
          <header className="overview-card__header">
            <div>
              <span className={`overview-pill ${ollamaInsightsTone}`}>{ollamaInsightsLabel}</span>
              <h3>Ollama Insights</h3>
            </div>
            <Link className="overview-card__cta" to="/ollama">
              Open Ollama →
            </Link>
          </header>
          <p className="overview-card__summary">{ollamaInsightsSummary}</p>
          {ollamaInsights.length > 0 ? (
            <ul className="ollama-insights-list">
              {ollamaInsights.slice(0, 4).map((insight) => (
                <li key={insight.id} className="ollama-insights-item">
                  <p className="ollama-insights-message">{insight.message}</p>
                  <span className="ollama-insights-meta">
                    {formatDateTime(insight.generated_at)} · {insight.model}
                  </span>
                </li>
              ))}
            </ul>
          ) : null}
          <dl className="overview-metrics">
            <div>
              <dt>Service</dt>
              <dd>{ollamaInsightsEnabled ? "Enabled" : "Disabled"}</dd>
            </div>
            <div>
              <dt>Last run</dt>
              <dd>{formatDateTime(ollamaInsightsLastRun)}</dd>
            </div>
            <div>
              <dt>Next run</dt>
              <dd>{formatDateTime(ollamaInsightsNextRun)}</dd>
            </div>
          </dl>
        </article>
      </section>
    </div>
  );
}
